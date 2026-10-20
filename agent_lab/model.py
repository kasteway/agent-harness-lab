"""Two interchangeable decision-makers for the same agent loop.

The practice model is scripted, not an LLM. Live mode uses OpenAI Responses.
"""

import json
import os
from dataclasses import dataclass
from typing import Optional

from .tools import SCHEMAS


@dataclass
class Decision:
    tool: Optional[str] = None
    arguments: Optional[dict] = None
    answer: Optional[str] = None
    call_id: Optional[str] = None


class PracticeModel:
    """A transparent stand-in for model decisions; ideal for tracing the loop."""

    def decide(self, question, history):
        names = [entry["name"] for entry in history]
        if "compare_sla" not in names:
            return Decision(tool="compare_sla", arguments={})
        if "find_driver" not in names:
            return Decision(tool="find_driver", arguments={"dimension": "region"})
        if "retrieve_notes" not in names:
            return Decision(tool="retrieve_notes", arguments={"query": "West delivery SLA routing staffing incident", "limit": 2})
        results = {entry["name"]: entry["result"] for entry in history}
        comparison = results["compare_sla"]
        driver = results["find_driver"]["segments"][0]
        notes = results["retrieve_notes"]
        citations = ", ".join(note["id"] for note in notes) or "none"
        return Decision(answer=(
            f"SLA changed from {comparison['prior']['rate']:.1%} to {comparison['current']['rate']:.1%} "
            f"({comparison['change_percentage_points']:+.2f} percentage points). "
            f"{driver['segment']} added {driver['added_late']} late tickets, the largest regional increase. "
            f"Operating notes ({citations}) suggest checking routing and staffing, but the ticket data alone "
            "does not establish the cause. Verify with the queue owner before acting."
        ))


class OpenAIModel:
    """Real model-chosen tool calls using the official Responses API pattern."""

    def __init__(self, model):
        if not os.getenv("OPENAI_API_KEY"):
            raise RuntimeError("Set OPENAI_API_KEY for live mode; practice mode needs no key")
        try:
            from openai import OpenAI
        except ImportError as exc:
            raise RuntimeError("Install optional dependency: pip install -e '.[live]'") from exc
        self.client = OpenAI()
        self.model = model
        self.input_items = []

    def decide(self, question, history):
        if not self.input_items:
            self.input_items.append({"role": "user", "content": question})
        elif history:
            last = history[-1]
            self.input_items.append({"type": "function_call_output", "call_id": last["call_id"],
                                     "output": json.dumps(last["result"])})
        response = self.client.responses.create(
            model=self.model,
            instructions=("You are a read-only service analytics assistant. Use tools for every numerical claim. "
                          "Retrieve notes for context. Cite note IDs. Distinguish observed contribution from "
                          "unproven cause. Never claim to have changed records or sent messages."),
            tools=SCHEMAS,
            input=self.input_items,
        )
        self.input_items.extend(response.output)
        calls = [item for item in response.output if item.type == "function_call"]
        if calls:
            item = calls[0]
            # A response can contain multiple calls. The lesson keeps one call per turn.
            if len(calls) > 1:
                raise RuntimeError("This tutorial expects one tool call per model turn")
            return Decision(tool=item.name, arguments=json.loads(item.arguments), call_id=item.call_id)
        return Decision(answer=response.output_text)

