import json
import tempfile
import unittest

from her.config import Config
from her.run import DONE, SKIPPED, Executor, read_verdict, step_prompt
from tests.fakes import fake_claude, make_run, step


def judge_pipeline(directory):
    judge = dict(step("judge"), skill="judge")
    ship = dict(step("ship", ["judge"]), skill="to-pr")
    return make_run(directory, [judge, ship])


def execute(directory, run):
    config = Config(claude_bin=fake_claude(directory))
    return Executor(config, run, out=lambda *a, **k: None).execute()


class VerdictGateTest(unittest.TestCase):
    def test_judge_prompt_names_absolute_verdict_path(self):
        with tempfile.TemporaryDirectory() as directory:
            run = judge_pipeline(directory)
            prompt = step_prompt(run, run.plan(), run.plan()["steps"][0])
            self.assertIn(str(run.verdict_path("judge")), prompt)
            self.assertTrue(run.verdict_path("judge").is_absolute())
            self.assertIn("ship, fix, needs-discussion", prompt)

    def test_every_prompt_starts_with_headless_decisions_line(self):
        with tempfile.TemporaryDirectory() as directory:
            run = judge_pipeline(directory)
            for planned in run.plan()["steps"]:
                prompt = step_prompt(run, run.plan(), planned)
                self.assertEqual(
                    prompt.splitlines()[0],
                    f"HER headless run. Decisions: {run.path}/decisions.md",
                )

    def test_missing_verdict_skips_to_pr_and_writes_summary(self):
        with tempfile.TemporaryDirectory() as directory:
            run = judge_pipeline(directory)
            execute(directory, run)
            ship = run.state()["steps"]["ship"]
            self.assertEqual(ship["status"], SKIPPED)
            self.assertTrue(ship["reason"].startswith("judge verdict: missing: "))
            self.assertIn("judge verdict: missing", run.read("summary.md"))

    def test_fix_verdict_skips_with_why(self):
        with tempfile.TemporaryDirectory() as directory:
            run = judge_pipeline(directory)
            verdict = {"verdict": "fix", "why": "p95 regressed 20%", "table": "| m | v |"}
            run.verdict_path("judge").write_text(json.dumps(verdict))
            execute(directory, run)
            self.assertEqual(run.state()["steps"]["ship"]["reason"], "judge verdict: fix: p95 regressed 20%")
            self.assertIn("judge verdict: fix: p95 regressed 20%", run.read("summary.md"))

    def test_ship_verdict_lets_to_pr_run(self):
        with tempfile.TemporaryDirectory() as directory:
            run = judge_pipeline(directory)
            verdict = {"verdict": "ship", "why": "all green", "table": ""}
            run.verdict_path("judge").write_text(json.dumps(verdict))
            execute(directory, run)
            self.assertEqual(run.state()["steps"]["ship"]["status"], DONE)

    def test_judge_step_gets_write_tools(self):
        with tempfile.TemporaryDirectory() as directory:
            run = judge_pipeline(directory)
            execute(directory, run)
            argv = json.loads(run.step_log("judge").read_text().splitlines()[-1])["argv"]
            self.assertIn("Write", argv[argv.index("--allowedTools") + 1].split(","))

    def test_invalid_verdict_file(self):
        with tempfile.TemporaryDirectory() as directory:
            run = judge_pipeline(directory)
            run.verdict_path("judge").write_text("{not json")
            self.assertEqual(read_verdict(run.verdict_path("judge"))[0], "invalid")
            run.verdict_path("judge").write_text(json.dumps({"verdict": "maybe"}))
            self.assertEqual(read_verdict(run.verdict_path("judge"))[0], "invalid")


if __name__ == "__main__":
    unittest.main()
