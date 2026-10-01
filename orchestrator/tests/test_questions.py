import json
import tempfile
import unittest
from pathlib import Path

from her.agents import build_command, question_text, result_info, session_id
from her.config import Config
from her.run import BLOCKED, DONE, Executor, resume_prompt, step_prompt, step_verdict

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


class ResumeTest(unittest.TestCase):
    def test_claude_command_resumes_session(self):
        command = build_command(Config(), "claude", "prompt", "m", "/tmp", ["/a"], True, "sess-9")
        self.assertEqual(command[command.index("--resume") + 1], "sess-9")
        self.assertEqual(command[command.index("--model") + 1], "m")
        self.assertEqual(command[command.index("--add-dir") + 1], "/a")
        self.assertNotIn("--resume", build_command(Config(), "claude", "prompt", "m", "/tmp", [], True))

    def test_cursor_never_resumes(self):
        command = build_command(Config(), "cursor", "prompt", "m", "/tmp", [], True, "sess-9")
        self.assertNotIn("--resume", command)

    def test_fallback_prompt_has_earlier_question(self):
        with tempfile.TemporaryDirectory() as directory:
            run = make_run(directory, [step("ask")])
            prompt = step_prompt(run, run.plan(), run.plan()["steps"][0], ("A or B?", "A"))
        self.assertIn("Earlier question: A or B?", prompt)
        self.assertIn("Sofia's answer: A", prompt)
        self.assertIn("do ask", prompt)

    def test_resume_prompt_has_answer_and_rules(self):
        prompt = resume_prompt(step("ask"), "go with A")
        self.assertIn("Sofia's answer: go with A", prompt)
        self.assertIn("QUESTION:", prompt)

    def run_answered(self, saved):
        with tempfile.TemporaryDirectory() as directory:
            run = make_run(directory, [step("ask")], {"ask": saved})
            run.step_log("ask").write_text(json.dumps({"type": "system", "session_id": "old"}) + "\n")
            config = Config(claude_bin=fake_claude(directory))
            phase = Executor(config, run, out=lambda *a, **k: None).execute()
            return phase, run.state()["steps"]["ask"], run.step_log("ask").read_text()

    def test_executor_resumes_and_clears_answer(self):
        saved = {"status": "pending", "question": "q", "answer": "A", "session_id": "sess-ask"}
        phase, info, log = self.run_answered(saved)
        self.assertEqual(phase, "done")
        self.assertEqual(info["status"], DONE)
        self.assertIsNone(info["answer"])
        self.assertIn('"--resume", "sess-ask"', log)
        self.assertTrue(log.startswith('{"type": "system", "session_id": "old"}'))

    def test_executor_falls_back_without_session(self):
        saved = {"status": "pending", "question": "q", "answer": "A", "session_id": None}
        phase, info, log = self.run_answered(saved)
        self.assertEqual(phase, "done")
        self.assertNotIn("--resume", log)
        self.assertNotIn('"old"', log)
        self.assertIsNone(info["answer"])


if __name__ == "__main__":
    unittest.main()
