"""
Eval Harness — validate a model swap before cutover.

Every module should have a golden eval set: labeled examples with a
known-correct output. Before swapping models in any module (especially
9 and 10), run this against both the incumbent and candidate model and
compare — don't cut over on a benchmark headline alone.

Usage:
    harness = EvalHarness(golden_set_path="./eval/cspm_golden.jsonl")
    results = harness.run(client, schema=TriageFinding)
    print(results.summary())
"""

import json
from dataclasses import dataclass, field
from typing import Callable, Type

from pydantic import BaseModel


@dataclass
class EvalResult:
    total: int = 0
    correct: int = 0
    false_positives: int = 0
    false_negatives: int = 0
    failures: list = field(default_factory=list)

    def summary(self) -> str:
        accuracy = self.correct / self.total if self.total else 0
        return (
            f"Accuracy: {accuracy:.1%} ({self.correct}/{self.total})\n"
            f"False positives: {self.false_positives}\n"
            f"False negatives: {self.false_negatives}\n"
            f"Failures logged: {len(self.failures)}"
        )


class EvalHarness:
    def __init__(self, golden_set_path: str):
        self.golden_set_path = golden_set_path

    def _load_golden_set(self) -> list[dict]:
        examples = []
        with open(self.golden_set_path) as f:
            for line in f:
                if line.strip():
                    examples.append(json.loads(line))
        return examples

    def run(
        self,
        call_fn: Callable[[str], BaseModel],
        compare_fn: Callable[[BaseModel, dict], bool] = None,
    ) -> EvalResult:
        """
        call_fn: takes the example's input, returns the model's
                 structured output.
        compare_fn: takes (model_output, expected_dict), returns True
                    if they match. Defaults to exact-match on a
                    'verdict' field if not provided — override this
                    per module, since "correct" means different things
                    for a triage verdict vs. a severity ranking.
        """
        examples = self._load_golden_set()
        result = EvalResult(total=len(examples))

        compare = compare_fn or self._default_compare

        for example in examples:
            try:
                output = call_fn(example["input"])
                if compare(output, example["expected"]):
                    result.correct += 1
                else:
                    if example["expected"].get("verdict") and not getattr(output, "verdict", None):
                        result.false_negatives += 1
                    else:
                        result.false_positives += 1
                    result.failures.append({
                        "input": example["input"],
                        "expected": example["expected"],
                        "got": output.model_dump() if hasattr(output, "model_dump") else str(output),
                    })
            except Exception as e:
                result.failures.append({"input": example["input"], "error": str(e)})

        return result

    @staticmethod
    def _default_compare(output: BaseModel, expected: dict) -> bool:
        return getattr(output, "verdict", None) == expected.get("verdict")
