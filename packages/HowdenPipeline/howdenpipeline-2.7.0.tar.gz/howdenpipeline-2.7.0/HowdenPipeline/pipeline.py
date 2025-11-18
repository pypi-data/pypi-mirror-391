import json
import hashlib
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Callable
import inspect
import asyncio

import concurrent.futures
import networkx as nx

from HowdenPipeline.manager.jsonMatcher import JsonMatcher
from HowdenPipeline.manager.tracker import Tracker


@dataclass
class Match:
    result: Path
    ground_truth: Path


class ParameterSerializer:
    def make_serializable(self, obj: Any) -> Any:
        if obj is None or isinstance(obj, (str, int, float, bool)):
            return obj
        if isinstance(obj, (list, tuple, set)):
            return [self.make_serializable(v) for v in obj]
        if isinstance(obj, dict):
            return {k: self.make_serializable(v) for k, v in sorted(obj.items())}
        if hasattr(obj, "__dict__"):
            return self.make_serializable(vars(obj))
        return f"{type(obj).__name__}:{repr(obj)}"


class StepHasher:
    def __init__(self, serializer: Optional[ParameterSerializer] = None) -> None:
        self._serializer = serializer or ParameterSerializer()

    def compute_hash(self, step: Any) -> str:
        attrs = {
            k: v
            for k, v in step.__dict__.items()
            if k != "hash"
               and not k.startswith("_")
               and k not in ("client", "provider")
        }
        serializable_attrs = self._serializer.make_serializable(attrs)
        attrs_str = json.dumps(serializable_attrs, sort_keys=True, ensure_ascii=True)
        return hashlib.sha256(attrs_str.encode()).hexdigest()[:8]


class StepNamer:
    def name_for(self, step: Any) -> str:
        name = getattr(step, "name", None)
        if name:
            return name
        return step.__class__.__name__


class PipelineGraphManager:
    def __init__(
            self,
            base_graph: Optional[nx.DiGraph] = None,
            hasher: Optional[StepHasher] = None,
            namer: Optional[StepNamer] = None,
    ) -> None:
        self.graph: nx.DiGraph = base_graph or nx.DiGraph()
        self._hasher = hasher or StepHasher()
        self._namer = namer or StepNamer()

    def add_step(
            self,
            step: Any,
            dependencies: Optional[Iterable[Any]] = None,
            track: bool = False,
            filetype: Optional[str] = None,
    ) -> None:
        node_id = self._node_id_for(step)
        name = self._namer.name_for(step)
        node_hash = self._hasher.compute_hash(step)
        node_label = f"{name}_{node_hash}" if node_hash else name

        if dependencies:
            for dep_step in dependencies:
                dep_id = self._node_id_for(dep_step)
                dep_path = self.graph.nodes[dep_id].get("full_path", [])
                full_path = dep_path + [node_label]

                self.graph.add_edge(dep_id, node_id)

                if node_id not in self.graph:
                    self.graph.add_node(node_id)

                self.graph.nodes[node_id].update(
                    cls=step,
                    name=name,
                    track=track,
                    filetype=filetype,
                    result=None,
                    hash=node_hash,
                    hash_path=[node_hash],
                    full_path=full_path,
                )
        else:
            self.graph.add_node(
                node_id,
                cls=step,
                name=name,
                track=track,
                filetype=filetype,
                result=None,
                hash=node_hash,
                hash_path=[node_hash],
                full_path=[node_label],
            )

    def traversal_order(self) -> List[str]:
        return list(nx.topological_sort(self.graph))

    def dependency_paths(self) -> List[str]:
        return [
            "/".join(self.graph.nodes[n]["full_path"])
            for n in self.graph.nodes
        ]

    @staticmethod
    def _node_id_for(step: Any) -> str:
        return hex(id(step))


class FilePipelineRunner:
    def __init__(
            self,
            graph: nx.DiGraph,
            serializer: Optional[ParameterSerializer] = None,
            tracker: Optional[Tracker] = None,
            match_holder: Optional[List[Match]] = None,
    ) -> None:
        self.graph = graph
        self.serializer = serializer or ParameterSerializer()
        self.tracker = tracker
        self.match_holder = match_holder if match_holder is not None else []

    # ------------------------------------------------------------------
    # This solves the event loop errors for async and sync async based APIs
    # ------------------------------------------------------------------
    def _run_step_safe(self, step, input_data):
        if inspect.iscoroutinefunction(step):
            loop = asyncio.new_event_loop()
            try:
                asyncio.set_event_loop(loop)
                return loop.run_until_complete(step(input_data))
            finally:
                loop.close()
                asyncio.set_event_loop(None)

        loop = asyncio.new_event_loop()
        try:
            asyncio.set_event_loop(loop)
            return step(input_data)
        finally:
            loop.close()
            asyncio.set_event_loop(None)

    # ------------------------------------------------------------------
    # Main execution
    # ------------------------------------------------------------------
    def run_for_file(self, file_path: Path) -> Path:
        print(f"Processing {file_path}")

        for node in self._traversal_order():
            step = self.graph.nodes[node]["cls"]
            dep_path = "/".join(self.graph.nodes[node]["full_path"])
            folder_path = Path(file_path.parent / dep_path)
            folder_path.mkdir(parents=True, exist_ok=True)

            filetype = self.graph.nodes[node]["filetype"]
            result_file_path = folder_path / Path("result").with_suffix(f".{filetype}")

            if not result_file_path.exists():
                self._write_parameters(step, folder_path)
                input_data = self._build_input_data(node, file_path)

                try:
                    result = self._run_step_safe(step, input_data)
                except Exception as exc:
                    msg = f"Step {step.name} failed for file {file_path} with error: {exc}"
                    raise RuntimeError(msg) from exc

                result_file_path.write_text(result, encoding="utf-8")

            if self.graph.nodes[node]["track"]:
                path = file_path.parent
                match = Match(
                    result=result_file_path,
                    ground_truth=Path(f"{path}/GT_{step.name}.json"),
                )
                self.match_holder.append(match)

            self._propagate_result_path(node, result_file_path)

        return file_path

    def _traversal_order(self) -> List[str]:
        return list(nx.topological_sort(self.graph))

    def _write_parameters(self, step: Any, folder_path: Path) -> None:
        json_parameter = folder_path / "parameter.json"
        attrs = {
            k: v
            for k, v in step.__dict__.items()
            if not k.startswith("_") and k not in ("client", "provider")
        }
        serializable_attrs = self.serializer.make_serializable(attrs)
        json_parameter.write_text(
            json.dumps(
                serializable_attrs,
                indent=2,
                sort_keys=True,
                ensure_ascii=True,
            ),
            encoding="utf-8",
        )

    def _build_input_data(self, node: str, file_path: Path) -> Any:
        dep_paths = [
            data["result_path_from_dep"]
            for _pred, _succ, data in self.graph.in_edges(node, data=True)
            if "result_path_from_dep" in data
        ]

        if dep_paths:
            dep_paths = [Path(p) for p in dep_paths]
            if len(dep_paths) == 1:
                return dep_paths[0]
            return dep_paths

        if isinstance(file_path, Path):
            return file_path
        return Path(file_path)

    def _propagate_result_path(self, node: str, result_file_path: Path) -> None:
        for _u, _v, data in self.graph.out_edges(node, data=True):
            data["result_path_from_dep"] = str(result_file_path)


class GraphPipeline:
    def __init__(
            self,
            root_folder: str,
            tracker: Optional[Tracker] = None,
            graph_manager: Optional[PipelineGraphManager] = None,
            serializer: Optional[ParameterSerializer] = None,
            hasher: Optional[StepHasher] = None,
            namer: Optional[StepNamer] = None,
            matcher_factory: Optional[Callable[[List[Match]], Any]] = None,
    ) -> None:
        self.root_folder = Path(root_folder)
        self.file_paths_pdf: List[Path] = list(self.root_folder.rglob("*.pdf"))

        self.serializer = serializer or ParameterSerializer()
        self.hasher = hasher or StepHasher(self.serializer)
        self.namer = namer or StepNamer()

        self.graph_manager = graph_manager or PipelineGraphManager(
            hasher=self.hasher,
            namer=self.namer,
        )

        self.tracker = tracker
        if self.tracker:
            print("run mlflow by writing <mlflow ui> in cli")

        self.matcher_factory = matcher_factory or JsonMatcher
        self.matches: List[Match] = []

    def add_step(
            self,
            step: Any,
            dependencies: Optional[Iterable[Any]] = None,
            track: bool = False,
            filetype: Optional[str] = None,
    ) -> None:
        self.graph_manager.add_step(
            step=step,
            dependencies=dependencies,
            track=track,
            filetype=filetype,
        )

    def execute(self, workers: int = 4) -> List[Path]:
        if not self.file_paths_pdf:
            return []

        results: List[Path] = []

        with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
            futures = []
            for file_path in self.file_paths_pdf:
                graph_copy = self.graph_manager.graph.copy()
                runner = FilePipelineRunner(
                    graph=graph_copy,
                    serializer=self.serializer,
                    tracker=self.tracker,
                    match_holder=self.matches,
                )
                futures.append(
                    executor.submit(runner.run_for_file, file_path=file_path)
                )

            for future in concurrent.futures.as_completed(futures):
                try:
                    result = future.result()
                    results.append(result)
                except Exception as exc:
                    print(f"Worker failed but pipeline continues: {exc}")
                    # You may log this instead:
                    # logger.error(f"Worker failed: {exc}")
                    continue

        if self.tracker and self.matcher_factory and self.matches:
            matcher = self.matcher_factory(self.matches)
            self.tracker.log_metrics(matcher.get_accuracy_per_filename())
            self.tracker.log_artifacts("././poetry.lock")

        return results
