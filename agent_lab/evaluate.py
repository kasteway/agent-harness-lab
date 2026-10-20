"""Run small, reproducible checks; do not mistake them for production evaluation."""

import json

from .harness import run
from .model import PracticeModel
from .tools import compare_sla, find_driver, retrieve_notes


def evaluate():
    question = "Why did SLA fall this week?"
    outcome = run(question, PracticeModel())
    names = [item["name"] for item in outcome["trace"]]
    checks = {
        "arithmetic": compare_sla()["change_percentage_points"] == -33.33,
        "driver": find_driver("region")["segments"][0]["segment"] == "West",
        "retrieval": any(note["id"] == "K-02" for note in retrieve_notes("West delivery routing staffing")),
        "tool_sequence": names == ["compare_sla", "find_driver", "retrieve_notes"],
        "answer_has_citation": "K-02" in outcome["answer"],
        "answer_has_caution": "does not establish the cause" in outcome["answer"],
    }
    return {"passed": sum(checks.values()), "total": len(checks), "checks": checks}


if __name__ == "__main__":
    result = evaluate()
    print(json.dumps(result, indent=2))
    raise SystemExit(0 if result["passed"] == result["total"] else 1)
