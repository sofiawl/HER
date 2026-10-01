import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from her.config import Config
from her.plan import validate
from her.run import DONE, FAILED, Executor
from tests.fakes import make_run, step

MODELS = {"claude": {"haiku": [], "sonnet": ["c-sonnet"], "opus": [], "fable": []}}

FAKE_AGENT = """
import json, pathlib, sys
pathlib.Path(sys.argv[1]).write_text("changed")
print(json.dumps({"type": "assistant", "message": {"content": [{"type": "text", "text": "ok"}]}}))
print(json.dumps({"type": "result", "subtype": "success", "result": "ok"}))
"""


def git(repo, *args):
    return subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True, check=True).stdout.strip()


def make_repo(directory):
    repo = Path(directory) / "repo"
    repo.mkdir()
    git(repo, "init", "-q", "-b", "main")
    git(repo, "config", "user.email", "t@t")
    git(repo, "config", "user.name", "t")
    (repo / "a.txt").write_text("a")
    git(repo, "add", ".")
    git(repo, "commit", "-q", "-m", "init")
    return repo


def writer(sid, repo, branch, depends_on=()):
    return dict(step(sid, depends_on, cwd=str(repo)), writes=True, branch=branch, tier="sonnet", model="c-sonnet")


def execute(directory, repo, steps, base=None):
    run = make_run(directory, steps)
    plan = run.plan()
    plan["repos"] = [dict({"name": "repo", "path": str(repo)}, **({"base": base} if base else {}))]
    run.save_plan(plan)

    def fake_command(config, agent, prompt, model, cwd, add_dirs, writes, resume=None):
        return [sys.executable, "-c", FAKE_AGENT, str(Path(cwd) / f"{model}-{len(prompt)}.txt")]

    with mock.patch("her.run.build_command", fake_command):
        Executor(Config(models=MODELS), run, out=lambda *a, **k: None).execute()
    return run.state()["steps"]


class BranchExecutionTest(unittest.TestCase):
    def test_creates_missing_branch_from_repo_base(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = make_repo(directory)
            git(repo, "checkout", "-q", "-b", "develop")
            (repo / "b.txt").write_text("b")
            git(repo, "add", ".")
            git(repo, "commit", "-q", "-m", "develop")
            git(repo, "checkout", "-q", "main")
            state = execute(directory, repo, [writer("work", repo, "feat/ML-88_export_csv")], base="develop")
            self.assertEqual(state["work"]["status"], DONE)
            self.assertEqual(git(repo, "branch", "--show-current"), "feat/ML-88_export_csv")
            self.assertEqual(git(repo, "rev-parse", "HEAD"), git(repo, "rev-parse", "develop"))

    def test_checks_out_existing_branch(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = make_repo(directory)
            git(repo, "branch", "fix/login_redirect")
            state = execute(directory, repo, [writer("work", repo, "fix/login_redirect")])
            self.assertEqual(state["work"]["status"], DONE)
            self.assertEqual(git(repo, "branch", "--show-current"), "fix/login_redirect")

    def test_dirty_tree_fails_first_writer_without_running_it(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = make_repo(directory)
            (repo / "a.txt").write_text("local edit")
            state = execute(directory, repo, [writer("work", repo, "feat/new_thing")])
            self.assertEqual(state["work"]["status"], FAILED)
            self.assertEqual(state["work"]["reason"], "dirty tree")
            self.assertNotIn("attempts", state["work"])
            self.assertEqual(git(repo, "branch", "--show-current"), "main")

    def test_later_writer_in_same_repo_accepts_earlier_changes(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = make_repo(directory)
            steps = [writer("one", repo, "feat/new_thing"), writer("two", repo, "feat/new_thing", ["one"])]
            state = execute(directory, repo, steps)
            self.assertEqual([state["one"]["status"], state["two"]["status"]], [DONE, DONE])


class BranchValidationTest(unittest.TestCase):
    def problems(self, directory, **fields):
        plan = {
            "summary": "s", "repos": [], "decisions": [], "missing_skills": [],
            "steps": [dict(step("work", cwd=str(directory)), tier="sonnet", model="c-sonnet", **fields)],
        }
        return [p for p in validate(plan, Config(models=MODELS)) if "branch" in p or "fallback" in p]

    def test_writer_in_git_repo_needs_branch(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = make_repo(directory)
            self.assertEqual(self.problems(repo, writes=True), ["step work: writes in a git repo, declare branch"])
            self.assertEqual(self.problems(repo, writes=False), [])
            self.assertEqual(self.problems(directory, writes=True), [])

    def test_branch_name_shape(self):
        with tempfile.TemporaryDirectory() as directory:
            for good in ["feat/ML-88_export_csv", "fix/login_redirect", "chore/deps_bump", "proposal/x_y"]:
                self.assertEqual(self.problems(directory, branch=good), [], good)
            for bad in ["feature/foo_bar", "feat/foo-bar", "feat/foo", "feat/ML-88", "feat/Foo_bar", "main"]:
                self.assertEqual(len(self.problems(directory, branch=bad)), 1, bad)

    def test_fallback_models_shape(self):
        with tempfile.TemporaryDirectory() as directory:
            self.assertEqual(self.problems(directory, fallback_models=["claude/c-opus"]), [])
            self.assertEqual(len(self.problems(directory, fallback_models=["nope/x", "claude"])), 2)


if __name__ == "__main__":
    unittest.main()
