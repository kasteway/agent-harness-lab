"""Run the same case with a scripted model or a real OpenAI model."""

import argparse
import json

from .harness import run
from .memory import read_memory, remember
from .model import OpenAIModel, PracticeModel

DEFAULT_QUESTION = "Why did support SLA fall this week, and what should we investigate?"


def main():
    parser = argparse.ArgumentParser(description="Learn an agent harness from scratch")
    parser.add_argument("question", nargs="?", default=DEFAULT_QUESTION)
    parser.add_argument("--mode", choices=["practice", "live"], default="practice")
    parser.add_argument("--model", default="gpt-5-mini", help="Live mode model; choose one available to your account")
    parser.add_argument("--trace", action="store_true", help="Show every tool request and result")
    parser.add_argument("--remember", action="store_true", help="Save the Q&A locally (ignored by Git)")
    parser.add_argument("--show-memory", action="store_true")
    args = parser.parse_args()
    if args.show_memory:
        print(json.dumps(read_memory(), indent=2))
        return
    model = PracticeModel() if args.mode == "practice" else OpenAIModel(args.model)
    outcome = run(args.question, model)
    print(outcome["answer"])
    if args.trace:
        print("\nTOOL TRACE")
        for entry in outcome["trace"]:
            print(json.dumps({"tool": entry["name"], "arguments": entry["arguments"],
                              "result": entry["result"]}, indent=2))
    if args.remember:
        remember(args.question, outcome["answer"])


if __name__ == "__main__":
    main()

