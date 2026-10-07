import json
import tempfile
import unittest

from her import run as ledger
from her.run import BLOCKED, DONE, FAILED, REVIEW, RUNNING, SKIPPED
from tests.helpers import branch, git_repo, make_plan, make_run, make_step


def ids(steps):
    return [step["id"] for step in steps]


class ReadyStepsTest(unittest.TestCase):
    def test_dependencies_gate_and_failures_skip(self):
        with tempfile.TemporaryDirectory() as directory:
            steps = [make_step("a", directory), make_step("b", directory, depends_on=["a"]),
                     make_step("c", directory, depends_on=["b"])]
            run = make_run(directory, make_plan(steps))
            self.assertEqual(ids(ledger.ready_steps(run)), ["a"])
            run.record("a", status=FAILED)
            self.assertEqual(ledger.ready_steps(run), [])
            self.assertEqual(run.step_status("b"), SKIPPED)
            self.assertEqual(run.step_status("c"), SKIPPED)

    def test_one_writer_per_repo_at_a_time(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = git_repo(directory)
            steps = [make_step("a", repo, writes=True), make_step("b", repo, writes=True), make_step("r", repo)]
            run = make_run(directory, make_plan(steps))
            self.assertEqual(ids(ledger.ready_steps(run)), ["a", "r"])
            run.record("a", status=REVIEW)
            self.assertEqual(ids(ledger.ready_steps(run)), ["r"])
            run.record("a", status=DONE)
            self.assertEqual(ids(ledger.ready_steps(run)), ["b", "r"])


class JudgeGateTest(unittest.TestCase):
    def plan(self, directory):
        return make_plan([make_step("j", directory, skill="judge"),
                          make_step("pr", directory, skill="to-pr", depends_on=["j"])])

    def judge(self, run, verdict):
        if verdict:
            run.verdict_path("j").write_text(json.dumps({"verdict": verdict, "why": "because"}))
        step = run.plan()["steps"][0]
        run.record("j", status=RUNNING)
        return ledger.finish(run, step, "DONE", "report\nDONE")

    def test_ship_lets_to_pr_run(self):
        with tempfile.TemporaryDirectory() as directory:
            run = make_run(directory, self.plan(directory))
            self.assertEqual(self.judge(run, "ship"), DONE)
            self.assertEqual(ids(ledger.ready_steps(run)), ["pr"])

    def test_fix_skips_to_pr_with_why(self):
        with tempfile.TemporaryDirectory() as directory:
            run = make_run(directory, self.plan(directory))
            self.judge(run, "fix")
            self.assertEqual(ledger.ready_steps(run), [])
            self.assertEqual(run.step_state("pr")["reason"], "judge verdict: fix: because")

    def test_missing_verdict_fails_the_judge(self):
        with tempfile.TemporaryDirectory() as directory:
            run = make_run(directory, self.plan(directory))
            self.assertEqual(self.judge(run, None), FAILED)
            ledger.ready_steps(run)
            self.assertEqual(run.step_status("pr"), SKIPPED)

    def test_judge_brief_names_the_verdict_path(self):
        with tempfile.TemporaryDirectory() as directory:
            run = make_run(directory, self.plan(directory))
            text = ledger.brief(run, run.plan()["steps"][0])
            self.assertIn(str(run.verdict_path("j")), text)
            self.assertIn("skills/judge/SKILL.md", text)


class ReviewLoopTest(unittest.TestCase):
    def test_writer_goes_to_review_then_done(self):
        with tempfile.TemporaryDirectory() as directory:
            step = make_step("a", directory, writes=True)
            run = make_run(directory, make_plan([step]))
            run.record("a", status=RUNNING)
            self.assertEqual(ledger.finish(run, step, "DONE", "did it\nDONE"), REVIEW)
            self.assertEqual(ledger.review(run, step, "approve", "fine\nAPPROVE"), DONE)

    def test_changes_feed_the_next_brief_and_block_after_three_rounds(self):
        with tempfile.TemporaryDirectory() as directory:
            step = make_step("a", directory, writes=True)
            run = make_run(directory, make_plan([step]))
            for round_number in range(1, 4):
                run.record("a", status=RUNNING)
                ledger.finish(run, step, "DONE", "did it\nDONE")
                result = ledger.review(run, step, "changes", f"fix a.py:{round_number}\nCHANGES")
                if round_number < 3:
                    self.assertEqual(result, RUNNING)
                    self.assertIn(f"fix a.py:{round_number}", ledger.brief(run, step))
            self.assertEqual(result, BLOCKED)

    def test_needs_context_blocks_with_reason(self):
        with tempfile.TemporaryDirectory() as directory:
            step = make_step("a", directory)
            run = make_run(directory, make_plan([step]))
            ledger.finish(run, step, "NEEDS_CONTEXT", "stuck\nNEEDS_CONTEXT: which table?")
            self.assertEqual(run.step_status("a"), BLOCKED)
            self.assertEqual(run.step_state("a")["reason"], "which table?")

    def test_reader_is_done_without_review(self):
        with tempfile.TemporaryDirectory() as directory:
            step = make_step("a", directory)
            run = make_run(directory, make_plan([step]))
            self.assertEqual(ledger.finish(run, step, "DONE_WITH_CONCERNS", "x\nDONE_WITH_CONCERNS: slow"), DONE)
            self.assertTrue(run.step_state("a")["concerns"])


class PreflightTest(unittest.TestCase):
    def test_creates_branch_from_repo_base(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = git_repo(directory)
            step = make_step("a", repo, writes=True, branch="feat/ML-1_thing")
            run = make_run(directory, make_plan([step], repos=[{"name": "r", "path": str(repo), "base": "main"}]))
            self.assertIsNone(ledger.preflight(run, step))
            self.assertEqual(branch(repo), "feat/ML-1_thing")

    def test_dirty_tree_blocks_first_writer_only(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = git_repo(directory)
            (repo / "new.txt").write_text("x")
            steps = [make_step("a", repo, writes=True), make_step("b", repo, writes=True)]
            run = make_run(directory, make_plan(steps))
            self.assertIn("dirty tree", ledger.preflight(run, steps[0]))
            run.record("a", began=True, status=DONE)
            self.assertIsNone(ledger.preflight(run, steps[1]))


class BriefTest(unittest.TestCase):
    def test_brief_carries_decisions_reports_note_and_status_line(self):
        with tempfile.TemporaryDirectory() as directory:
            steps = [make_step("a", directory), make_step("b", directory, depends_on=["a"])]
            run = make_run(directory, make_plan(steps))
            run.write("decisions.md", "- Q: CSV or JSON? A: CSV.")
            text = ledger.brief(run, steps[1], note="use UTF-8")
            for phrase in ("CSV or JSON", str(run.step_output("a")), "use UTF-8", "NEEDS_CONTEXT", "Read only"):
                self.assertIn(phrase, text)

    def test_report_status_reads_the_last_line(self):
        self.assertEqual(ledger.report_status("work\n**BLOCKED: no access**\n"), ("BLOCKED", "no access"))
        self.assertEqual(ledger.report_status("work\nDONE"), ("DONE", ""))
        self.assertEqual(ledger.report_status("no status here"), (None, ""))


class SummaryTest(unittest.TestCase):
    def test_summary_lists_steps_and_open_questions(self):
        with tempfile.TemporaryDirectory() as directory:
            run = make_run(directory, make_plan([make_step("a", directory)]))
            run.record("a", status=BLOCKED, reason="which table?")
            text = ledger.write_summary(run).read_text()
            self.assertIn("## Open questions", text)
            self.assertIn("which table?", text)


if __name__ == "__main__":
    unittest.main()
