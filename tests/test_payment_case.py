import unittest

from agent_lab.harness import run
from agent_lab.payment_case import PaymentPracticeModel, execute_payment, payments_overview


class PaymentCaseTests(unittest.TestCase):
    def test_real_data_case(self):
        result = run("What happened?", PaymentPracticeModel(), execute_tool=execute_payment)
        self.assertEqual([step["name"] for step in result["trace"]],
                         ["payments_overview", "fraud_months", "source_context"])
        self.assertIn("2,929", result["answer"])
        self.assertIn("not a fraud rate", result["answer"])
        self.assertEqual(payments_overview()["complaints"], 7953)

    def test_read_only_allowlist(self):
        with self.assertRaises(ValueError):
            execute_payment("delete_complaints", {})
        with self.assertRaises(ValueError):
            execute_payment("payments_overview", {"secret": "x"})


if __name__ == "__main__":
    unittest.main()
