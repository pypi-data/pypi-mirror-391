from dataclasses import dataclass
from pathlib import Path
import json
from typing import List, Dict, Any


@dataclass
class Match:
    result: Path
    ground_truth: Path


class JsonMatcher:
    """Compare JSON files and compute match accuracy."""

    def __init__(self, matches: List[Match]):
        self.matches = matches

    @staticmethod
    def _load_json(path: Path) -> Dict[str, Any]:
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)

    @staticmethod
    def _flatten_json(data: Dict[str, Any], parent_key: str = "", sep: str = ".") -> Dict[str, Any]:
        items = []
        for k, v in data.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, dict):
                items.extend(JsonMatcher._flatten_json(v, new_key, sep=sep).items())
            else:
                items.append((new_key, v))
        return dict(items)

    def _compare_pair(self, file1: Path, file2: Path) -> Dict[str, Any]:
        print(file1)
        json1 = self._flatten_json(self._load_json(file1))
        print(file2)
        json2 = self._flatten_json(self._load_json(file2))

        all_keys = set(json1.keys()) | set(json2.keys())
        total = len(all_keys)
        correct = 0
        mismatches = []

        for key in all_keys:
            v1 = json1.get(key)
            v2 = json2.get(key)
            if v1 == v2 and v1 is not None:
                correct += 1
            else:
                mismatches.append((key, v1, v2))

        accuracy = correct / total if total else 1.0

        return {
            "file1": str(file1),
            "file2": str(file2),
            "accuracy": round(accuracy, 4),
            "total_keys": total,
            "matched_keys": correct,
            "mismatches": mismatches,
        }

    def run(self) -> List[Dict[str, Any]]:
        """Run comparisons for all match pairs."""
        return [self._compare_pair(m.result, m.ground_truth) for m in self.matches]

    def report(self) -> dict:
        """Pretty-print comparison results."""
        results = self.run()
        for res in results:
            print(f"\nComparing: {res['file1']} ↔ {res['file2']}")
            print(f"Accuracy: {res['accuracy'] * 100:.2f}% ({res['matched_keys']}/{res['total_keys']})")
            if res["mismatches"]:
                print("Mismatches:")
                for key, v1, v2 in res["mismatches"]:
                    print(f"  {key}: '{v1}' != '{v2}'")
        avg = sum(r["accuracy"] for r in results) / len(results)
        print(f"\nOverall average accuracy: {avg * 100:.2f}%")
        return {"accuracy": avg * 100}