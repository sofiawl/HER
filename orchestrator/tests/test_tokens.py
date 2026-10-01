import json
import tempfile
import unittest
from pathlib import Path

from her.agents import assistant_usage, result_info
from her.watch import fmt_cost, fmt_tokens, totals_row

FIXTURES = Path(__file__).parent / "fixtures"


class UsageTest(unittest.TestCase):
    def test_ml88_cosmos_result(self):
        info = result_info(FIXTURES / "cosmos-text.jsonl")
        self.assertEqual(
            info["tokens"],
            {"input": 22, "cache_write": 101430, "cache_read": 881062, "output": 3359},
        )
        self.assertEqual(info["tokens"]["output"], 3359)
        self.assertAlmostEqual(info["cost"], 0.6155664)

    def test_live_usage_sums_messages_once(self):
        events = [
            {"type": "assistant", "message": {"id": "a", "usage": {"input_tokens": 2, "output_tokens": 3}}},
            {"type": "assistant", "message": {"id": "a", "usage": {"input_tokens": 2, "output_tokens": 4}}},
            {"type": "assistant", "message": {"id": "b", "usage": {"inputTokens": 5, "outputTokens": 6}}},
        ]
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "log.jsonl"
            path.write_text("\n".join(json.dumps(event) for event in events))
            usage = assistant_usage(path)
        self.assertEqual(usage, {"input": 7, "cache_write": 0, "cache_read": 0, "output": 10})


class BoardMetricsTest(unittest.TestCase):
    def test_compact_formatting(self):
        self.assertEqual(fmt_tokens(1_100_000), "1.1M")
        self.assertEqual(fmt_tokens(985_000), "985k")
        self.assertEqual(fmt_tokens(3_359), "3.4k")
        self.assertEqual(fmt_tokens(None), "-")
        self.assertEqual(fmt_cost(0.6155664), "$0.62")
        self.assertEqual(fmt_cost(None), "-")

    def test_totals(self):
        plan = {"steps": [{"id": "one"}, {"id": "two"}, {"id": "missing"}]}
        state = {
            "steps": {
                "one": {
                    "tokens": {"input": 10, "cache_write": 20, "cache_read": 30, "output": 40},
                    "cost": 0.1,
                },
                "two": {
                    "tokens": {"input": 1, "cache_write": 2, "cache_read": 3, "output": 4},
                    "cost": 0.2,
                },
            }
        }
        row, _ = totals_row(plan, state, 100)
        self.assertIn("total", row)
        self.assertRegex(row, r"\b110\s+44\s+\$0\.30$")


if __name__ == "__main__":
    unittest.main()
