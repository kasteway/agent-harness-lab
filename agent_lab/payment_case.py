"""A second, real-data case using exactly the same beginner agent loop.

The decision maker is scripted for learning. The counts come from a public
CFPB snapshot, and every calculation stays in ordinary Python.
"""

import csv
import json
from collections import defaultdict
from pathlib import Path

from .harness import run
from .model import Decision

ROOT = Path(__file__).resolve().parents[1]


def _rows():
    with (ROOT / "data" / "monthly_issues.csv").open(newline="", encoding="utf-8") as handle:
        return [dict(row, complaints=int(row["complaints"])) for row in csv.DictReader(handle)]


def payments_overview():
    totals = defaultdict(int)
    for row in _rows():
        totals[row["issue"]] += row["complaints"]
    leader = max(totals, key=totals.get)
    grand_total = sum(totals.values())
    return {"complaints": grand_total, "leading_issue": leader,
            "leading_count": totals[leader], "leading_share_pct": round(100 * totals[leader] / grand_total, 1)}


def fraud_months():
    return {row["month"]: row["complaints"] for row in _rows() if row["issue"] == "Fraud or scam"}


def source_context():
    provenance = json.loads((ROOT / "data" / "provenance.json").read_text(encoding="utf-8"))
    return {"source": provenance["source_url"], "period": provenance["period"],
            "caution": provenance["limitations"]}


def execute_payment(name, args):
    """The model may request only these three read-only operations."""
    if args != {}:
        raise ValueError("This case's tools take no arguments")
    allowed = {"payments_overview": payments_overview, "fraud_months": fraud_months,
               "source_context": source_context}
    if name not in allowed:
        raise ValueError("Unapproved payment-case tool")
    return allowed[name]()


class PaymentPracticeModel:
    """A transparent teaching stand-in, not an LLM or learned policy."""

    sequence = ("payments_overview", "fraud_months", "source_context")

    def decide(self, question, history):
        if len(history) < len(self.sequence):
            return Decision(tool=self.sequence[len(history)], arguments={})
        results = {item["name"]: item["result"] for item in history}
        overview = results["payments_overview"]
        months = results["fraud_months"]
        context = results["source_context"]
        return Decision(answer=(
            f"In the public money-transfer complaint slice, {overview['leading_issue']} is the largest issue: "
            f"{overview['leading_count']:,} of {overview['complaints']:,} complaints "
            f"({overview['leading_share_pct']:.1f}%). Its monthly counts run from {months['2024-01']} "
            f"in January to {months['2024-06']} in June. Source: {context['source']} "
            "These are published complaint counts, not a fraud rate or proof of an operational cause. "
            "An analyst should compare with internal transaction volume and investigate service changes."
        ))


def main():
    result = run("What should a payments operations lead investigate?", PaymentPracticeModel(),
                 execute_tool=execute_payment)
    print(result["answer"])
    print("\nTHREE BEGINNER STEPS")
    for index, item in enumerate(result["trace"], 1):
        print(f"{index}. {item['name']}: {json.dumps(item['result'])}")


if __name__ == "__main__":
    main()

