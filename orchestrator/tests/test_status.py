import json
import tempfile
import unittest
from pathlib import Path

from her.agents import claude_command, final_result, result_info
from her.config import Config
from her.run import DONE, FAILED, step_verdict

FIXTURES = Path(__file__).parent / "fixtures"


def fixture_without_denials(name, directory):
    lines = []
    for line in (FIXTURES / name).read_text().splitlines():
        event = json.loads(line)
        if event.get("type") == "result":
            event["permission_denials"] = []
        lines.append(json.dumps(event))
    path = Path(directory) / name
    path.write_text("\n".join(lines) + "\n")
    return path


def verdict_for(path, code=0):
    return step_verdict(code, final_result(path), result_info(path))


class ResultInfoTest(unittest.TestCase):
    def test_judge_fixture_fields(self):
        info = result_info(FIXTURES / "judge.jsonl")
        self.assertEqual(info["subtype"], "success")
        self.assertFalse(info["is_error"])
        self.assertEqual(info["permission_denials"], ["Bash"] * 6)
        self.assertAlmostEqual(info["cost"], 0.9987478)
        self.assertEqual(info["models"], ["claude-opus-5-5"])
        self.assertEqual(info["usage"]["output_tokens"], 2535)
        self.assertFalse(info["blocked"])

    def test_missing_result_event_is_neutral(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "cursor.jsonl"
            path.write_text(json.dumps({"type": "assistant", "message": {"content": "hi"}}) + "\n")
            info = result_info(path)
        self.assertIsNone(info["subtype"])
        self.assertEqual(info["permission_denials"], [])
        self.assertIsNone(info["usage"])
        self.assertIsNone(info["cost"])
        self.assertEqual(info["models"], [])

    def test_blocked_line_detected(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "blocked.jsonl"
            event = {"type": "result", "subtype": "success", "result": "notes\nBLOCKED: need a human"}
            path.write_text(json.dumps(event) + "\n")
            self.assertTrue(result_info(path)["blocked"])


class StepVerdictTest(unittest.TestCase):
    def test_judge_with_denials_fails(self):
        status, reason = verdict_for(FIXTURES / "judge.jsonl")
        self.assertEqual(status, FAILED)
        self.assertEqual(reason, "denied: Bash x6")

    def test_cosmos_with_real_denials_fails(self):
        status, reason = verdict_for(FIXTURES / "cosmos-text.jsonl")
        self.assertEqual(status, FAILED)
        self.assertEqual(reason, "denied: Bash x3")

    def test_cosmos_without_denials_is_done(self):
        with tempfile.TemporaryDirectory() as directory:
            path = fixture_without_denials("cosmos-text.jsonl", directory)
            self.assertEqual(verdict_for(path), (DONE, None))

    def test_exit_code_and_empty_result_fail(self):
        info = result_info(FIXTURES / "cosmos-text.jsonl")
        self.assertEqual(step_verdict(1, "text", info)[0], FAILED)
        self.assertEqual(step_verdict(0, "  ", info)[0], FAILED)

    def test_error_subtype_and_flag_fail(self):
        base = {"subtype": None, "is_error": False, "permission_denials": [], "blocked": False}
        self.assertEqual(step_verdict(0, "x", {**base, "subtype": "error_max_turns"})[0], FAILED)
        self.assertEqual(step_verdict(0, "x", {**base, "is_error": True})[0], FAILED)
        self.assertEqual(step_verdict(0, "x", {**base, "blocked": True})[0], FAILED)
        self.assertEqual(step_verdict(0, "x", base), (DONE, None))


class AllowedToolsTest(unittest.TestCase):
    def flag_value(self, writes, config=None):
        command = claude_command(config or Config(), "p", "m", [], writes)
        return command[command.index("--allowedTools") + 1].split(",")

    def test_read_and_write_lists(self):
        reads = self.flag_value(False)
        writes = self.flag_value(True)
        self.assertIn("Bash(git *)", reads)
        self.assertNotIn("Edit", reads)
        self.assertTrue(set(reads) < set(writes))
        self.assertIn("Edit", writes)
        self.assertIn("Bash(gh pr create *)", writes)

    def test_existing_flags_kept(self):
        write = claude_command(Config(), "p", "m", [], True)
        read = claude_command(Config(), "p", "m", [], False)
        self.assertIn("acceptEdits", write)
        self.assertIn("--disallowedTools", read)

    def test_override(self):
        config = Config(claude_read_tools=["Read"])
        self.assertEqual(self.flag_value(False, config), ["Read"])


if __name__ == "__main__":
    unittest.main()
