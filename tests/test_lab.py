import tempfile
import unittest
from pathlib import Path

from agent_lab.evaluate import evaluate
from agent_lab.harness import run
from agent_lab.memory import read_memory, remember
from agent_lab.model import Decision, PracticeModel
from agent_lab.tools import compare_sla, execute, find_driver, retrieve_notes


class LabTests(unittest.TestCase):
    def test_end_to_end_practice_mode(self):
        outcome = run("Why did SLA fall?", PracticeModel())
        self.assertEqual(len(outcome["trace"]), 3)
        self.assertIn("K-02", outcome["answer"])
        self.assertEqual(evaluate()["passed"], evaluate()["total"])

    def test_math_and_driver(self):
        self.assertEqual(compare_sla()["prior"]["on_time"], 5)
        self.assertEqual(compare_sla()["current"]["on_time"], 3)
        self.assertEqual(find_driver("region")["segments"][0]["added_late"], 2)

    def test_retrieval_carries_source_ids(self):
        notes = retrieve_notes("West delivery routing staffing")
        self.assertEqual(notes[0]["id"], "K-02")

    def test_unapproved_tools_and_inputs_are_rejected(self):
        for name, args in [("delete_tickets", {}), ("find_driver", {"dimension": "agent"}),
                           ("compare_sla", {"extra": True})]:
            with self.assertRaises(ValueError):
                execute(name, args)
        with self.assertRaises(ValueError):
            retrieve_notes("x" * 301)

    def test_loop_has_step_limit(self):
        class NeverDone:
            def decide(self, question, history):
                return Decision(tool="compare_sla", arguments={})
        with self.assertRaisesRegex(RuntimeError, "Stopped after"):
            run("test", NeverDone(), max_steps=2)

    def test_memory_is_explicit_and_local(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "memory.json"
            self.assertEqual(read_memory(path), [])
            remember("question", "answer", path)
            self.assertEqual(read_memory(path)[0]["answer"], "answer")


if __name__ == "__main__":
    unittest.main()
