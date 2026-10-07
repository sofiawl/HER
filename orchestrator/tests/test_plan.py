import tempfile
import unittest
from pathlib import Path

from her.config import DEFAULT_MODEL_NOTES, DEFAULT_MODELS, TIERS, Config
from her.plan import BRANCH_PATTERN, guide_text, validate, warnings
from tests.helpers import git_repo, make_plan, make_step


def problems(plan):
    return validate(plan, Config())


class GuideTest(unittest.TestCase):
    def test_guide_describes_the_in_chat_flow(self):
        text = guide_text(Config())
        for phrase in ("her begin", "her finish", "her review", "her approve", "Kineloop", "`host`"):
            self.assertIn(phrase, text)
        for gone in ("her start", "her watch", "fable", "fallback_models"):
            self.assertNotIn(gone, text)

    def test_every_default_model_has_notes(self):
        for agent, tiers in DEFAULT_MODELS.items():
            self.assertEqual(set(tiers), set(TIERS))
            for models in tiers.values():
                for model in models:
                    self.assertIn(f"{agent}/{model}", DEFAULT_MODEL_NOTES)


class ValidationTest(unittest.TestCase):
    def test_clean_plan_passes(self):
        with tempfile.TemporaryDirectory() as directory:
            self.assertEqual(problems(make_plan([make_step("a", directory)])), [])

    def test_missing_host_is_reported(self):
        with tempfile.TemporaryDirectory() as directory:
            plan = make_plan([make_step("a", directory)])
            del plan["host"]
            self.assertIn("missing top-level key host", problems(plan))

    def test_step_agent_must_match_host(self):
        with tempfile.TemporaryDirectory() as directory:
            step = make_step("a", directory, agent="cursor", model=DEFAULT_MODELS["cursor"]["sonnet"][0])
            found = problems(make_plan([step]))
            self.assertTrue(any("differs from host claude" in p for p in found), found)

    def test_card_shape(self):
        with tempfile.TemporaryDirectory() as directory:
            self.assertEqual(problems(make_plan([make_step("a", directory)], card="ML-86")), [])
            found = problems(make_plan([make_step("a", directory)], card="ml86"))
            self.assertTrue(any("card ml86" in p for p in found), found)

    def test_unknown_tier_model_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            found = problems(make_plan([make_step("a", directory, tier="fable")]))
            self.assertTrue(any("not allowed" in p for p in found), found)

    def test_cycle_and_unknown_dependency(self):
        with tempfile.TemporaryDirectory() as directory:
            steps = [make_step("a", directory, depends_on=["b"]), make_step("b", directory, depends_on=["a", "z"])]
            found = problems(make_plan(steps))
            self.assertIn("depends_on has a cycle", found)
            self.assertIn("step b: depends on unknown step z", found)

    def test_writer_in_git_repo_needs_branch(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = git_repo(directory)
            plan = make_plan([make_step("a", repo, writes=True)], repos=[{"name": "r", "path": str(repo)}])
            self.assertIn("step a: writes in a git repo, declare branch", problems(plan))

    def test_judge_rejects_another_repo_in_add_dirs(self):
        with tempfile.TemporaryDirectory() as directory:
            one, two = git_repo(directory, "one"), git_repo(directory, "two")
            step = make_step("j", one, skill="judge", add_dirs=[str(two)])
            repos = [{"name": "one", "path": str(one)}, {"name": "two", "path": str(two)}]
            found = problems(make_plan([step], repos=repos))
            self.assertTrue(any("runs once per repo" in p for p in found), found)

    def test_dirty_repo_with_writer_is_a_problem(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = git_repo(directory)
            (repo / "new.txt").write_text("x")
            step = make_step("a", repo, writes=True, branch="feat/ML-1_thing")
            found = problems(make_plan([step], repos=[{"name": "r", "path": str(repo)}]))
            self.assertTrue(any("dirty tree" in p and "new.txt" in p for p in found), found)

    def test_repo_that_is_not_git_is_a_problem(self):
        with tempfile.TemporaryDirectory() as directory:
            plan = make_plan([make_step("a", directory)], repos=[{"name": "r", "path": directory}])
            self.assertTrue(any("is not a git repo" in p for p in problems(plan)))


class WarningTest(unittest.TestCase):
    def test_writing_plan_without_judge_warns(self):
        with tempfile.TemporaryDirectory() as directory:
            plan = make_plan([make_step("a", directory, writes=True)])
            self.assertEqual(len(warnings(plan, Config())), 1)
            plan["steps"].append(make_step("j", directory, skill="judge"))
            self.assertEqual(warnings(plan, Config()), [])


class BranchPatternTest(unittest.TestCase):
    def test_rule_examples(self):
        for good in ("feat/ML-88_export_csv", "fix/login_redirect", "refactor/01_her_orchestrator", "feat/DES2-213_nAIosh"):
            self.assertTrue(BRANCH_PATTERN.fullmatch(good), good)
        for bad in ("feat/ML-88_short-words", "feature/ML-88_x", "feat/ML-88"):
            self.assertFalse(BRANCH_PATTERN.fullmatch(bad), bad)


if __name__ == "__main__":
    unittest.main()
