import json
import re
import signal
import sys
import threading
import time
from datetime import datetime
from pathlib import Path

from .agents import build_command, final_result, result_info, run_logged
from .config import RUNS_DIR

DONE, FAILED, RUNNING, PENDING, SKIPPED = "done", "failed", "running", "pending", "skipped"


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
        (self.path / name).write_text(text)

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

    def step_log(self, sid):
        return self.path / "steps" / f"{sid}.jsonl"

    def step_output(self, sid):
        return self.path / "steps" / f"{sid}.md"


def step_prompt(run, plan, step):
    lines = [f"You are step `{step['id']}` ({step['title']}) of a HER orchestrator run."]
    if step.get("skill"):
        handle = f"her-{step['skill']}" if step["agent"] == "cursor" else f"her:{step['skill']}"
        lines.append(f"Use the HER skill `{handle}` for this step.")
    lines += ["", "## Overall goal", plan["summary"], "", "## Your task", step["task"]]
    decisions = run.decisions().strip()
    if decisions:
        lines += ["", "## Settled decisions (final, do not reopen)", decisions]
    deps = step.get("depends_on", [])
    if deps:
        lines += ["", "## Outputs of earlier steps (read them first)"]
        lines += [f"- {dep}: {run.step_output(dep)}" for dep in deps]
    lines += [
        "",
        "## Rules",
        "- Follow HER rules: no code comments, no em dash, no en dash, no emojis.",
        "- Do not commit, push, open PRs or install anything unless your task says so.",
        "- You may edit files." if step["writes"] else "- Read only: do not edit any file.",
        "- You run headless: nobody answers during this run.",
        "- If you cannot continue without a decision from Sofia, stop, change nothing more, and end",
        "  your final reply with one line `QUESTION: <one clear question with the options>`.",
        "- End with a short report: what you did, files changed, checks run and their results,",
        "  open questions.",
    ]
    return "\n".join(lines)


def step_verdict(code, result, info):
    if code != 0:
        return FAILED, f"exit code {code}"
    if not result.strip():
        return FAILED, "empty result"
    if info["subtype"] not in (None, "success"):
        return FAILED, f"subtype {info['subtype']}"
    if info["is_error"]:
        return FAILED, "is_error"
    denials = info["permission_denials"]
    if denials:
        counts = {}
        for name in denials:
            counts[name] = counts.get(name, 0) + 1
        return FAILED, "denied: " + ", ".join(f"{n} x{c}" for n, c in counts.items())
    if info["blocked"]:
        return FAILED, "blocked"
    return DONE, None


class Executor:
    def __init__(self, config, run, out=print):
        self.config = config
        self.run = run
        self.plan = run.plan()
        self.out = out
        self.lock = threading.RLock()
        self.cwd_locks = {}
        state = run.state().get("steps", {})
        self.status = {
            s["id"]: (DONE if state.get(s["id"], {}).get("status") == DONE else PENDING)
            for s in self.plan["steps"]
        }
        self.started = {}
        self.processes = {}

    def _record(self, sid, **fields):
        with self.lock:
            state = self.run.state()
            state.setdefault("steps", {}).setdefault(sid, {}).update(fields)
            self.run.save_state(state)

    def _say(self, text):
        with self.lock:
            if sys.stdout.isatty():
                sys.stdout.write("\r\033[K")
            self.out(f"[{datetime.now():%H:%M:%S}] {text}", flush=True)

    def _ready(self, step):
        if self.status[step["id"]] != PENDING:
            return False
        deps = step.get("depends_on", [])
        if any(self.status[d] in (FAILED, SKIPPED) for d in deps):
            self.status[step["id"]] = SKIPPED
            self._record(step["id"], status=SKIPPED)
            self._say(f"skip   {step['id']}: a dependency failed")
            return False
        if not all(self.status[d] == DONE for d in deps):
            return False
        if step["writes"]:
            busy = [
                s for s in self.plan["steps"]
                if self.status[s["id"]] == RUNNING and s["writes"] and s["cwd"] == step["cwd"]
            ]
            if busy:
                return False
        return True

    def _execute(self, step):
        sid = step["id"]
        prompt = step_prompt(self.run, self.plan, step)
        add_dirs = [str(self.run.path)] + [d for d in step.get("add_dirs", []) if d != step["cwd"]]
        command = build_command(
            self.config, step["agent"], prompt, step["model"], step["cwd"], add_dirs, step["writes"]
        )
        log_path = self.run.step_log(sid)
        process = run_logged(command, step["cwd"], log_path)
        self.processes[sid] = process
        code = process.wait()
        result = final_result(log_path)
        self.run.step_output(sid).write_text(result)
        status, reason = step_verdict(code, result, result_info(log_path))
        elapsed = int(time.time() - self.started[sid])
        with self.lock:
            self.status[sid] = status
        self._record(sid, status=status, exit_code=code, seconds=elapsed, reason=reason)
        why = f" ({reason})" if reason else ""
        self._say(f"{status:<6} {sid} in {elapsed}s{why} -> {self.run.step_output(sid)}")

    def _status_line(self):
        counts = {}
        for value in self.status.values():
            counts[value] = counts.get(value, 0) + 1
        running = [sid for sid, value in self.status.items() if value == RUNNING]
        parts = [f"{k} {v}" for k, v in counts.items()]
        return f"  {' | '.join(parts)}   running: {', '.join(running) or '-'}"

    def _stop(self, signum, frame):
        for sid, process in list(self.processes.items()):
            if process.poll() is None:
                process.terminate()
        for sid, value in self.status.items():
            if value == RUNNING:
                self._record(sid, status=FAILED, exit_code=-15)
        self.run.update_state(phase="stopped")
        raise SystemExit(143)

    def execute(self):
        signal.signal(signal.SIGTERM, self._stop)
        self.run.update_state(phase="executing")
        threads = []
        while True:
            with self.lock:
                running = sum(1 for v in self.status.values() if v == RUNNING)
            for step in self.plan["steps"]:
                if running >= self.config.max_parallel:
                    break
                if self._ready(step):
                    sid = step["id"]
                    with self.lock:
                        self.status[sid] = RUNNING
                    self.started[sid] = time.time()
                    self._record(sid, status=RUNNING, started_at=self.started[sid], seconds=None, exit_code=None, reason=None)
                    skill = f" /her:{step['skill']}" if step.get("skill") else ""
                    mode = "writes" if step["writes"] else "reads"
                    self._say(f"start  {sid}{skill} on {step['agent']}/{step['model']} ({mode}) in {step['cwd']}")
                    thread = threading.Thread(target=self._execute, args=(step,), daemon=True)
                    thread.start()
                    threads.append(thread)
                    running += 1
            if all(v in (DONE, FAILED, SKIPPED) for v in self.status.values()):
                break
            if sys.stdout.isatty():
                with self.lock:
                    sys.stdout.write("\r\033[K" + self._status_line())
                    sys.stdout.flush()
            time.sleep(1)
        for thread in threads:
            thread.join()
        if sys.stdout.isatty():
            sys.stdout.write("\r\033[K")
        phase = "done" if all(v == DONE for v in self.status.values()) else "finished-with-failures"
        self.run.update_state(phase=phase)
        self._write_summary()
        return phase

    def _write_summary(self):
        lines = [f"# HER run {self.run.id}", "", self.plan["summary"], "", "## Steps", ""]
        for step in self.plan["steps"]:
            lines.append(f"- `{step['id']}` {self.status[step['id']]}: {self.run.step_output(step['id'])}")
        missing = self.plan.get("missing_skills", [])
        if missing:
            lines += ["", "## Skills HER is missing", ""]
            lines += [f"- `{m['name']}`: {m['would_do']} ({m['why']})" for m in missing]
        self.run.write("summary.md", "\n".join(lines) + "\n")
