import os
import stat
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from her.config import DEFAULT_MODELS, DEFAULT_MODEL_NOTES, Config
from her.plan import guide_text, validate, warnings
from tests.fakes import step
from tests.test_branches import git, make_repo

MODELS = {
    "claude": {"haiku": [], "sonnet": ["c-sonnet"], "opus": [], "fable": []},
    "cursor": {"haiku": [], "sonnet": ["x-sonnet"], "opus": [], "fable": []},
}


def make_bin(directory, name):
    path = Path(directory) / name
    path.write_text("#!/bin/sh\n")
    path.chmod(path.stat().st_mode | stat.S_IEXEC)
    return str(path)


def config_with_bins(directory, **fields):
    return Config(
        models=MODELS,
        claude_bin=make_bin(directory, "fake-claude"),
        cursor_bin=make_bin(directory, "fake-cursor"),
        **fields,
    )


def make_step(sid, cwd, **fields):
    return dict(step(sid, cwd=str(cwd)), tier="sonnet", model="c-sonnet", **fields)


def make_plan(steps, repos=()):
    return {"summary": "s", "repos": list(repos), "decisions": [], "missing_skills": [], "steps": steps}


class GuideTest(unittest.TestCase):
    def test_guide_is_neutral_and_lists_model_notes(self):
        text = guide_text(Config())
        self.assertNotIn("Prefer agent `claude`", text)
        self.assertIn("do not default to one agent", text)
        self.assertIn("relative cost", text)
        self.assertIn("cannot ask Sofia", text)
        self.assertIn("once per repo", text)
        self.assertNotIn("preference order", text)

    def test_prefer_agents_states_the_order(self):
        text = guide_text(Config(prefer_agents=["cursor", "claude"]))
        self.assertIn("preference order is `cursor`, `claude`", text)

    def test_every_default_model_has_notes(self):
        for agent, tiers in DEFAULT_MODELS.items():
            for models in tiers.values():
                for model in models:
                    note = DEFAULT_MODEL_NOTES[f"{agent}/{model}"]
                    self.assertTrue(note["strengths"])
                    self.assertIn(note["relative_cost"], range(1, 6))


class WarningTest(unittest.TestCase):
    def test_single_agent_plan_warns_when_several_configured(self):
        config = Config(models=MODELS)
        self.assertEqual(len(warnings(make_plan([make_step("a", "/tmp")]), config)), 1)

    def test_mixed_or_single_agent_config_does_not_warn(self):
        mixed = make_plan([make_step("a", "/tmp"), dict(make_step("b", "/tmp"), agent="cursor")])
        self.assertEqual(warnings(mixed, Config(models=MODELS)), [])
        single = Config(models={"claude": MODELS["claude"]})
        self.assertEqual(warnings(make_plan([make_step("a", "/tmp")]), single), [])


class FanOutTest(unittest.TestCase):
    def problems(self, directory, skill, extra_in_add_dirs):
        one = make_repo(directory)
        two = Path(directory) / "two"
        two.mkdir()
        git(two, "init", "-q", "-b", "main")
        repos = [{"name": "one", "path": str(one)}, {"name": "two", "path": str(two)}]
        add_dirs = [str(two / "sub")] if extra_in_add_dirs else [str(one)]
        plan = make_plan([make_step("ship", one, skill=skill, add_dirs=add_dirs)], repos)
        with mock.patch("her.plan.catalog", return_value={"judge": {}, "to-pr": {}}):
            return [p for p in validate(plan, config_with_bins(directory)) if "once per repo" in p]

    def test_judge_and_to_pr_reject_another_repo_in_add_dirs(self):
        for skill in ("judge", "to-pr"):
            with tempfile.TemporaryDirectory() as directory:
                self.assertEqual(len(self.problems(directory, skill, True)), 1, skill)

    def test_own_repo_in_add_dirs_is_fine(self):
        with tempfile.TemporaryDirectory() as directory:
            self.assertEqual(self.problems(directory, "judge", False), [])


class PreflightTest(unittest.TestCase):
    def problems(self, directory, steps, repos, config=None):
        found = validate(make_plan(steps, repos), config or config_with_bins(directory))
        return [p for p in found if p.startswith(("repo ", "agent "))]

    def test_dirty_repo_with_writing_step_lists_files(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = make_repo(directory)
            (repo / "a.txt").write_text("edit")
            (repo / "new.txt").write_text("new")
            writer = make_step("w", repo, writes=True, branch="feat/new_thing")
            found = self.problems(directory, [writer], [{"name": "repo", "path": str(repo)}])
            self.assertEqual(len(found), 1)
            self.assertIn("dirty tree", found[0])
            self.assertIn("a.txt", found[0])
            self.assertIn("new.txt", found[0])

    def test_dirty_repo_without_writing_step_is_fine(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = make_repo(directory)
            (repo / "a.txt").write_text("edit")
            reader = make_step("r", repo)
            self.assertEqual(self.problems(directory, [reader], [{"name": "repo", "path": str(repo)}]), [])

    def test_clean_repo_passes(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = make_repo(directory)
            writer = make_step("w", repo, writes=True, branch="feat/new_thing")
            self.assertEqual(self.problems(directory, [writer], [{"name": "repo", "path": str(repo)}]), [])

    def test_repo_path_that_is_not_git_is_a_problem(self):
        with tempfile.TemporaryDirectory() as directory:
            plain = Path(directory) / "plain"
            plain.mkdir()
            found = self.problems(directory, [make_step("r", plain)], [{"name": "plain", "path": str(plain)}])
            self.assertEqual(len(found), 1)
            self.assertIn("not a git repo", found[0])

    def test_missing_agent_binary_is_a_problem(self):
        with tempfile.TemporaryDirectory() as directory:
            config = Config(models=MODELS, claude_bin=str(Path(directory) / "absent"))
            found = self.problems(directory, [make_step("r", directory)], [], config)
            self.assertEqual(len(found), 1)
            self.assertIn("agent claude", found[0])

    def test_only_used_agents_are_checked(self):
        with tempfile.TemporaryDirectory() as directory:
            config = Config(
                models=MODELS,
                claude_bin=make_bin(directory, "fake-claude"),
                cursor_bin=str(Path(directory) / "absent"),
            )
            self.assertEqual(self.problems(directory, [make_step("r", directory)], [], config), [])


if __name__ == "__main__":
    unittest.main()
