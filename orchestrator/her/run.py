import json
import os
import re
import threading
from datetime import datetime
from pathlib import Path

from .config import HER_ROOT, RUNS_DIR
from .repo import checkout, dirty_files, git_root, resolved

PENDING, RUNNING, REVIEW, DONE, FAILED, BLOCKED, SKIPPED = (
    "pending", "running", "review", "done", "failed", "blocked", "skipped",
)
SETTLED = (DONE, FAILED, SKIPPED)
REPORT_STATUSES = ("DONE", "DONE_WITH_CONCERNS", "NEEDS_CONTEXT", "BLOCKED", "FAILED")
REVIEW_VERDICTS = ("approve", "changes")
VERDICTS = ("ship", "fix", "needs-discussion")
MAX_REVIEW_ROUNDS = 3


class Run:
    def __init__(self, path):
        self.path = Path(path)

    @classmethod
    def create(cls, request):
        slug = re.sub(r"[^a-z0-9]+", "-", request.lower())[:40].strip("-") or "run"
        path = RUNS_DIR / f"{datetime.now():%Y%m%d-%H%M%S}-{slug}"
        (path / "steps").mkdir(parents=True)
        run = cls(path)
        run.write("request.md", request)
        run.save_state({"phase": "created", "approved": False, "steps": {}})
        return run

    @classmethod
    def find(cls, ref=None):
        runs = sorted(p for p in RUNS_DIR.glob("*") if p.is_dir()) if RUNS_DIR.exists() else []
        if not runs:
            raise SystemExit("no runs yet")
        if ref is None:
            return cls(runs[-1])
        matches = [p for p in runs if p.name == ref or p.name.startswith(ref) or ref in p.name]
        if not matches:
            raise SystemExit(f"no run matches {ref}")
        return cls(matches[-1])

    @property
    def id(self):
        return self.path.name

    def read(self, name, default=""):
        file = self.path / name
        return file.read_text() if file.exists() else default

    def write(self, name, text):
        target = self.path / name
        temporary = target.with_name(f".{target.name}.{os.getpid()}.{threading.get_ident()}.tmp")
        temporary.write_text(text)
        os.replace(temporary, target)

    def request(self):
        return self.read("request.md")

    def decisions(self):
        return self.read("decisions.md")

    def plan(self):
        return json.loads(self.read("plan.json", "null"))

    def save_plan(self, plan):
        self.write("plan.json", json.dumps(plan, indent=2, ensure_ascii=False))

    def state(self):
        return json.loads(self.read("state.json", "{}"))

    def save_state(self, state):
        self.write("state.json", json.dumps(state, indent=2))

    def update_state(self, **changes):
        state = self.state()
        state.update(changes)
        self.save_state(state)

    def step_state(self, sid):
        return self.state().get("steps", {}).get(sid, {})

    def step_status(self, sid):
        return self.step_state(sid).get("status", PENDING)

    def record(self, sid, **fields):
        state = self.state()
        state.setdefault("steps", {}).setdefault(sid, {}).update(fields)
        self.save_state(state)

    def step_output(self, sid):
        return self.path / "steps" / f"{sid}.md"

    def review_path(self, sid):
        return self.path / "steps" / f"{sid}.review.md"

    def verdict_path(self, sid):
        return self.path / "steps" / f"{sid}.verdict.json"


def read_verdict(path):
    try:
        data = json.loads(Path(path).read_text())
    except FileNotFoundError:
        return "missing", f"no verdict file at {path}"
    except (OSError, json.JSONDecodeError):
        return "invalid", f"{path} is not valid JSON"
    if not isinstance(data, dict) or data.get("verdict") not in VERDICTS:
        return "invalid", f"{path} has no verdict among {', '.join(VERDICTS)}"
    return data["verdict"], str(data.get("why", "")).strip()


def report_status(report):
    for line in reversed(report.strip().splitlines()):
        word = line.strip().strip("*`").split(":", 1)[0].strip().upper()
        if word in REPORT_STATUSES:
            return word, line.strip().strip("*`").partition(":")[2].strip()
        if line.strip():
            break
    return None, ""


def _steps(plan):
    return {step["id"]: step for step in plan["steps"]}


def _repo_root(step):
    return git_root(step["cwd"]) or resolved(step["cwd"])


def ready_steps(run):
    plan = run.plan()
    steps = _steps(plan)
    changed = True
    while changed:
        changed = False
        for step in plan["steps"]:
            sid = step["id"]
            if run.step_status(sid) != PENDING:
                continue
            reason = _skip_reason(run, steps, step)
            if reason:
                run.record(sid, status=SKIPPED, reason=reason)
                changed = True
    busy = {
        _repo_root(step) for step in plan["steps"]
        if step["writes"] and run.step_status(step["id"]) in (RUNNING, REVIEW, BLOCKED)
    }
    ready = []
    for step in plan["steps"]:
        if run.step_status(step["id"]) != PENDING:
            continue
        if not all(run.step_status(dep) == DONE for dep in step.get("depends_on", [])):
            continue
        if step["writes"]:
            root = _repo_root(step)
            if root in busy:
                continue
            busy.add(root)
        ready.append(step)
    return ready


def _skip_reason(run, steps, step):
    for dep in step.get("depends_on", []):
        if run.step_status(dep) in (FAILED, SKIPPED):
            return f"dependency {dep} {run.step_status(dep)}"
    if step.get("skill") != "to-pr":
        return None
    for dep in step.get("depends_on", []):
        if steps[dep].get("skill") == "judge" and run.step_status(dep) == DONE:
            verdict, why = read_verdict(run.verdict_path(dep))
            if verdict != "ship":
                return f"judge verdict: {verdict}: {why}"
    return None


def preflight(run, step):
    if not step["writes"]:
        return None
    root = git_root(step["cwd"])
    if root is None:
        return None
    plan = run.plan()
    started = any(
        run.step_state(other["id"]).get("began") and git_root(other["cwd"]) == root
        for other in plan["steps"] if other["writes"]
    )
    if not started:
        dirty = dirty_files(root)
        if dirty:
            return f"dirty tree in {root}: " + ", ".join(line.strip() for line in dirty[:10])
    if not step.get("branch"):
        return None
    base = next(
        (repo.get("base") for repo in plan.get("repos", []) if resolved(repo["path"]) == root),
        None,
    )
    return checkout(step["cwd"], step["branch"], base or "main")


def skill_path(skill):
    return HER_ROOT / "skills" / skill / "SKILL.md"


def step_rules(step):
    return [
        "## Rules",
        "- Follow HER rules: no code comments, no em dash, no en dash, no emojis.",
        "- Do not commit, push, open PRs or install anything unless your task says so.",
        "- You may edit files inside the paths of your task." if step["writes"] else "- Read only: do not edit any file.",
        "- Nobody answers you during this step. Do not guess a decision that belongs to Sofia.",
        "- End with a short report: what you did, files changed, checks run and their results,",
        "  concerns. The last line is exactly one of:",
        "  `DONE`, `DONE_WITH_CONCERNS: <concern>`, `NEEDS_CONTEXT: <what is missing>`,",
        "  `BLOCKED: <why>`.",
    ]


def brief(run, step, note=None):
    plan = run.plan()
    lines = [
        f"You are step `{step['id']}` ({step['title']}) of HER run {run.id}.",
        f"Work in {step['cwd']}." + (f" Branch {step['branch']} is checked out." if step.get("branch") else ""),
    ]
    if step.get("add_dirs"):
        lines.append("Other dirs you may use: " + ", ".join(step["add_dirs"]))
    if step.get("skill"):
        lines.append(f"Read and follow the HER skill at {skill_path(step['skill'])} (headless mode if it has one).")
    lines += ["", "## Overall goal", plan["summary"], "", "## Your task", step["task"]]
    decisions = run.decisions().strip()
    if decisions:
        lines += ["", "## Settled decisions (final, do not reopen)", decisions]
    deps = step.get("depends_on", [])
    if deps:
        lines += ["", "## Reports of earlier steps (read them first)"]
        lines += [f"- {dep}: {run.step_output(dep)}" for dep in deps]
    if step.get("skill") == "judge":
        lines += [
            "", "## Verdict file",
            f"Write your verdict to {run.verdict_path(step['id'])} as JSON with the keys `verdict`",
            "(one of ship, fix, needs-discussion), `why` (one sentence) and `table` (the metrics table",
            "as a markdown string). This is the only file you may write.",
        ]
    review = run.review_path(step["id"])
    if review.exists() and run.step_state(step["id"]).get("review") == "changes":
        lines += ["", "## Review to address (fix every point, then report again)", review.read_text().strip()]
    if note:
        lines += ["", "## Note from the controller", note]
    return "\n".join(lines + [""] + step_rules(step))


def review_brief(run, step):
    lines = [
        f"You review step `{step['id']}` ({step['title']}) of HER run {run.id}. Read only: do not edit any file.",
        f"Repo: {step['cwd']}" + (f", branch {step['branch']}." if step.get("branch") else "."),
        "",
        "## The task the step was given",
        step["task"],
        "",
    ]
    decisions = run.decisions().strip()
    if decisions:
        lines += ["## Settled decisions", decisions, ""]
    lines += [
        f"## The implementer report\n{run.step_output(step['id'])}",
        "",
        "## How to review",
        "1. Spec: read the diff (`git diff` and untracked files). Does it do exactly the task, nothing",
        "   missing and nothing extra? Do not trust the report, check the code.",
        "2. Quality: correctness, tests run and passing, HER rules (no code comments, no em dash,",
        "   no en dash, no emojis), names, dead code.",
        "3. List each problem with file:line and the fix. Ignore style nits that no rule covers.",
        "",
        "The last line of your reply is exactly `APPROVE` or `CHANGES`.",
    ]
    return "\n".join(lines)


def finish(run, step, status, report):
    sid = step["id"]
    run.write(f"steps/{sid}.md", report)
    if status in ("NEEDS_CONTEXT", "BLOCKED"):
        run.record(sid, status=BLOCKED, reason=report_status(report)[1] or status.lower())
        return BLOCKED
    if status == "FAILED":
        run.record(sid, status=FAILED, reason=report_status(report)[1] or "implementer failed")
        return FAILED
    if step.get("skill") == "judge":
        verdict, why = read_verdict(run.verdict_path(sid))
        if verdict not in VERDICTS:
            run.record(sid, status=FAILED, reason=why)
            return FAILED
        run.record(sid, status=DONE, reason=f"verdict {verdict}: {why}")
        return DONE
    if step["writes"]:
        run.record(sid, status=REVIEW, concerns=status == "DONE_WITH_CONCERNS")
        return REVIEW
    run.record(sid, status=DONE, concerns=status == "DONE_WITH_CONCERNS")
    return DONE


def review(run, step, verdict, text):
    sid = step["id"]
    run.write(f"steps/{sid}.review.md", text)
    rounds = run.step_state(sid).get("review_rounds", 0) + 1
    if verdict == "approve":
        run.record(sid, status=DONE, review="approve", review_rounds=rounds)
        return DONE
    if rounds >= MAX_REVIEW_ROUNDS:
        run.record(sid, status=BLOCKED, review="changes", review_rounds=rounds,
                   reason=f"review asked for changes {rounds} times")
        return BLOCKED
    run.record(sid, status=RUNNING, review="changes", review_rounds=rounds)
    return RUNNING


def write_summary(run):
    plan = run.plan()
    lines = [f"# {plan.get('title') or run.id}", "", plan["summary"], "", "## Steps"]
    for step in plan["steps"]:
        info = run.step_state(step["id"])
        why = f": {info['reason']}" if info.get("reason") else ""
        lines.append(f"- {step['id']} ({step['title']}): {info.get('status', PENDING)}{why}")
    blocked = [step["id"] for step in plan["steps"] if run.step_status(step["id"]) == BLOCKED]
    if blocked:
        lines += ["", "## Open questions"] + [f"- {sid}: {run.step_state(sid).get('reason', '')}" for sid in blocked]
    if plan.get("missing_skills"):
        lines += ["", "## Skills HER is missing"]
        lines += [f"- {s['name']}: {s['would_do']} ({s['why']})" for s in plan["missing_skills"]]
    run.write("summary.md", "\n".join(lines) + "\n")
    return run.path / "summary.md"
