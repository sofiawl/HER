import contextlib
import io
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from her import cli
from her.run import BLOCKED, DONE, PENDING, Run

from tests.fakes import step


class AnswerCommandTest(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.runs = Path(self.directory.name)
        patcher = mock.patch("her.run.RUNS_DIR", self.runs)
        patcher.start()
        self.addCleanup(patcher.stop)
        self.run = Run(self.runs / "20260101-000000-demo")
        (self.run.path / "steps").mkdir(parents=True)
        self.run.save_plan({"summary": "goal", "steps": [step("ask"), step("other")], "repos": []})
        self.run.save_state({
            "phase": "needs-answer",
            "steps": {
                "ask": {"status": BLOCKED, "question": "A or B?", "session_id": "s-1", "reason": "needs answer"},
                "other": {"status": DONE},
            },
        })

    def answer(self, *argv):
        args = cli.build_parser().parse_args(["answer", *argv])
        out = io.StringIO()
        with contextlib.redirect_stdout(out), mock.patch("her.cli.launch_executor") as launch:
            code = cli.command_answer(args)
        return code, out.getvalue(), launch

    def test_rejects_step_that_is_not_blocked(self):
        code, out, launch = self.answer("other", "A")
        self.assertEqual(code, 1)
        self.assertIn("not blocked", out)
        launch.assert_not_called()
        self.assertEqual(self.run.decisions(), "")

    def test_rejects_unknown_step(self):
        code, out, launch = self.answer("nope", "A")
        self.assertEqual(code, 1)
        launch.assert_not_called()

    def test_records_answer_and_starts_executor(self):
        code, out, launch = self.answer("ask", "go with A")
        self.assertEqual(code, 0)
        launch.assert_called_once()
        info = self.run.state()["steps"]["ask"]
        self.assertEqual(info["status"], PENDING)
        self.assertEqual(info["answer"], "go with A")
        self.assertEqual(info["question"], "A or B?")
        self.assertEqual(info["session_id"], "s-1")
        self.assertIsNone(info["reason"])
        self.assertIn("Q: A or B?\nA: go with A\n", self.run.decisions())
        self.assertIn("her watch", out)

    def test_decisions_are_appended(self):
        self.run.write("decisions.md", "- earlier decision\n")
        self.answer("ask", "go with A")
        self.assertTrue(self.run.decisions().startswith("- earlier decision\n\nQ: A or B?"))

    def test_explicit_run_argument(self):
        code, out, launch = self.answer("ask", "B", "demo")
        self.assertEqual(code, 0)
        self.assertIn("A: B", self.run.decisions())

    def test_live_executor_is_not_started_twice(self):
        self.run.update_state(executor_pid=4242)
        args = cli.build_parser().parse_args(["answer", "ask", "A"])
        with contextlib.redirect_stdout(io.StringIO()), mock.patch("her.cli.pid_alive", return_value=True), mock.patch("her.cli.launch_executor") as launch:
            self.assertEqual(cli.command_answer(args), 0)
        launch.assert_not_called()


if __name__ == "__main__":
    unittest.main()
