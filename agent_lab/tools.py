"""Approved tools. The model requests a tool; Python validates and executes it."""

import json
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
ALLOWED_WEEKS = {"prior", "current"}
ALLOWED_DIMENSIONS = {"region", "category"}


def _load(name):
    return json.loads((DATA / name).read_text(encoding="utf-8"))


def _tokens(text):
    return set(re.findall(r"[a-z0-9]+", text.lower()))


def compare_sla():
    """Deterministic math stays outside the LLM."""
    tickets = _load("tickets.json")
    out = {}
    for week in ("prior", "current"):
        rows = [t for t in tickets if t["week"] == week]
        on_time = sum(t["resolved_in_sla"] for t in rows)
        out[week] = {"on_time": on_time, "total": len(rows), "rate": round(on_time / len(rows), 4)}
    out["change_percentage_points"] = round(100 * (out["current"]["rate"] - out["prior"]["rate"]), 2)
    return out


def find_driver(dimension):
    """Rank segments by added late tickets; this is contribution, not causality."""
    if dimension not in ALLOWED_DIMENSIONS:
        raise ValueError("dimension must be region or category")
    tickets = _load("tickets.json")
    counts = {week: Counter(t[dimension] for t in tickets if t["week"] == week and not t["resolved_in_sla"])
              for week in ALLOWED_WEEKS}
    segments = set(counts["prior"]) | set(counts["current"])
    ranked = sorted(({"segment": s, "prior_late": counts["prior"][s],
                      "current_late": counts["current"][s],
                      "added_late": counts["current"][s] - counts["prior"][s]} for s in segments),
                    key=lambda x: (-x["added_late"], x["segment"]))
    return {"dimension": dimension, "segments": ranked}


def retrieve_notes(query, limit=2):
    """Tiny transparent RAG retriever: lexical overlap, with source IDs."""
    if not isinstance(query, str) or not query.strip() or len(query) > 300:
        raise ValueError("query must be 1-300 characters")
    if not isinstance(limit, int) or not 1 <= limit <= 3:
        raise ValueError("limit must be 1-3")
    terms = _tokens(query)
    scored = []
    for note in _load("knowledge.json"):
        score = len(terms & _tokens(note["title"] + " " + note["text"]))
        if score:
            scored.append((score, note))
    scored.sort(key=lambda pair: (-pair[0], pair[1]["id"]))
    return [{**note, "score": score} for score, note in scored[:limit]]


SCHEMAS = [
    {"type": "function", "name": "compare_sla", "description": "Calculate prior and current SLA from sample tickets.",
     "parameters": {"type": "object", "properties": {}, "required": [], "additionalProperties": False}, "strict": True},
    {"type": "function", "name": "find_driver", "description": "Rank added late tickets by region or category.",
     "parameters": {"type": "object", "properties": {"dimension": {"type": "string", "enum": ["region", "category"]}},
                    "required": ["dimension"], "additionalProperties": False}, "strict": True},
    {"type": "function", "name": "retrieve_notes", "description": "Find relevant cited local operating notes.",
     "parameters": {"type": "object", "properties": {"query": {"type": "string"}, "limit": {"type": "integer"}},
                    "required": ["query", "limit"], "additionalProperties": False}, "strict": True},
]


def execute(name, args):
    """Allowlist blocks arbitrary file, shell, network, or generated-code execution."""
    if name == "compare_sla" and args == {}:
        return compare_sla()
    if name == "find_driver" and set(args) == {"dimension"}:
        return find_driver(args["dimension"])
    if name == "retrieve_notes" and set(args) == {"query", "limit"}:
        return retrieve_notes(args["query"], args["limit"])
    raise ValueError("unapproved tool or arguments")
