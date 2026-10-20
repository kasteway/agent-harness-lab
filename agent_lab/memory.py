"""Small local memory: previous questions and answers, never a hidden data source."""

import json
from pathlib import Path

DEFAULT_PATH = Path(__file__).resolve().parents[1] / "data" / "memory.json"


def read_memory(path=DEFAULT_PATH):
    path = Path(path)
    if not path.exists():
        return []
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError("memory file must contain a list")
    return data[-10:]


def remember(question, answer, path=DEFAULT_PATH):
    path = Path(path)
    entries = read_memory(path)
    entries.append({"question": question[:500], "answer": answer[:2000]})
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(entries[-10:], indent=2) + "\n", encoding="utf-8")

