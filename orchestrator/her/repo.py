import os
import subprocess
from pathlib import Path


def git(cwd, *args):
    return subprocess.run(["git", "-C", str(cwd), *args], capture_output=True, text=True)


def git_root(cwd):
    found = git(cwd, "rev-parse", "--show-toplevel")
    return Path(found.stdout.strip()).resolve() if found.returncode == 0 else None


def resolved(path):
    return Path(os.path.expanduser(path)).resolve()


def head_commit(cwd):
    found = git(cwd, "rev-parse", "--verify", "--quiet", "HEAD")
    return found.stdout.strip() if found.returncode == 0 else None


def dirty_files(path):
    found = git(path, "status", "--porcelain")
    return [line for line in found.stdout.splitlines() if line.strip()] if found.returncode == 0 else []


def current_branch(cwd):
    found = git(cwd, "branch", "--show-current")
    return found.stdout.strip() if found.returncode == 0 else None


def checkout(cwd, branch, base):
    if current_branch(cwd) == branch:
        return None
    exists = git(cwd, "rev-parse", "--verify", "--quiet", f"refs/heads/{branch}").returncode == 0
    done = git(cwd, "checkout", branch) if exists else git(cwd, "checkout", "-b", branch, base)
    if done.returncode == 0:
        return None
    lines = (done.stderr or done.stdout).strip().splitlines()
    return f"git checkout {branch} failed: {lines[-1] if lines else done.returncode}"
