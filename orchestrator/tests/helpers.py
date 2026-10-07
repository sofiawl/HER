import subprocess
from pathlib import Path

from her.config import DEFAULT_MODELS


def git_repo(directory, name="repo"):
    path = Path(directory) / name
    path.mkdir()
    for args in (["init", "-q", "-b", "main"], ["config", "user.email", "t@t"], ["config", "user.name", "t"]):
        subprocess.run(["git", "-C", str(path), *args], check=True)
    (path / "a.txt").write_text("a\n")
    subprocess.run(["git", "-C", str(path), "add", "."], check=True)
    subprocess.run(["git", "-C", str(path), "commit", "-qm", "init"], check=True)
    return path


def branch(path):
    return subprocess.run(
        ["git", "-C", str(path), "branch", "--show-current"], capture_output=True, text=True
    ).stdout.strip()


def make_step(sid, cwd, **fields):
    step = {
        "id": sid, "title": sid, "skill": None, "agent": "claude", "tier": "sonnet",
        "model": DEFAULT_MODELS["claude"]["sonnet"][0], "writes": False, "depends_on": [],
        "cwd": str(cwd), "add_dirs": [], "task": "do " + sid,
    }
    step.update(fields)
    return step


def make_plan(steps, repos=(), **fields):
    plan = {"summary": "goal", "host": "claude", "repos": list(repos), "decisions": [],
            "steps": steps, "missing_skills": []}
    plan.update(fields)
    return plan


def make_run(directory, plan, approved=True):
    from her.run import Run

    run = Run(Path(directory) / "run-1")
    (run.path / "steps").mkdir(parents=True)
    run.save_plan(plan)
    run.save_state({"phase": "running", "approved": approved, "steps": {}})
    return run
