import json
import tempfile
import unittest
from pathlib import Path

from her.agents import question_text, result_info, session_id
from her.config import Config
from her.run import BLOCKED, DONE, Executor, step_verdict

from tests.fakes import fake_claude, make_run, step


def write_log(directory, result, sid="abc"):
    path = Path(directory) / "log.jsonl"
    events = [
        {"type": "system", "subtype": "init", "session_id": sid},
        {"type": "result", "subtype": "success", "is_error": False, "result": result, "permission_denials": []},
    ]
    path.write_text("\n".join(json.dumps(e) for e in events) + "\n")
    return path


class QuestionDetectionTest(unittest.TestCase):
    def test_question_line(self):
        self.assertEqual(question_text("notes\nQUESTION: A or B?"), "A or B?")

    def test_no_question_line(self):
        self.assertIsNone(question_text("notes\nno question remains"))

    def test_mention_of_word_question_is_done(self):
        with tempfile.TemporaryDirectory() as directory:
            path = write_log(directory, "I answered the question you asked earlier.")
            info = result_info(path)
            self.assertIsNone(info["question"])
            self.assertEqual(step_verdict(0, "x", info), (DONE, None))

    def test_question_makes_blocked_with_session(self):
        with tempfile.TemporaryDirectory() as directory:
            path = write_log(directory, "partial\nQUESTION: A or B?", sid="s-1")
            info = result_info(path)
            self.assertEqual(info["question"], "A or B?")
            self.assertEqual(info["session_id"], "s-1")
            self.assertEqual(step_verdict(0, "x", info), (BLOCKED, "needs answer"))

    def test_session_id_missing(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "cursor.jsonl"
            path.write_text(json.dumps({"type": "assistant", "message": {"content": "hi"}}) + "\n")
            self.assertIsNone(session_id(path))


class BlockedExecutionTest(unittest.TestCase):
    def test_dependents_pending_independent_runs_and_summary(self):
        with tempfile.TemporaryDirectory() as directory:
            run = make_run(directory, [step("ask"), step("after", ["ask"]), step("free")])
            config = Config(claude_bin=fake_claude(directory))
            phase = Executor(config, run, out=lambda *a, **k: None).execute()
            steps = run.state()["steps"]
            self.assertEqual(phase, "needs-answer")
            self.assertEqual(steps["ask"]["status"], BLOCKED)
            self.assertEqual(steps["ask"]["question"], "which option, A or B?")
            self.assertEqual(steps["ask"]["session_id"], "sess-ask")
            self.assertEqual(steps["ask"]["reason"], "needs answer")
            self.assertEqual(steps["free"]["status"], DONE)
            self.assertNotIn("after", steps)
            summary = run.read("summary.md")
            self.assertIn("which option, A or B?", summary)
            self.assertIn('her answer ask "..."', summary)


if __name__ == "__main__":
    unittest.main()
