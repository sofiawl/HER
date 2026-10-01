import json
import re
import signal
import sys
import threading
import time
from datetime import datetime
from pathlib import Path

from .agents import TOKEN_KEYS, build_command, final_result, git, git_root, result_info, run_logged
from .config import RUNS_DIR

DONE, FAILED, RUNNING, PENDING, SKIPPED, BLOCKED = "done", "failed", "running", "pending", "skipped", "blocked"


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

    def add_decision(self, question, answer):
        text = self.decisions().rstrip("\n")
        self.write("decisions.md", (text + "\n\n" if text else "") + f"Q: {question}\nA: {answer}\n")

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

    def verdict_path(self, sid):
        return self.path / "steps" / f"{sid}.verdict.json"


VERDICTS = ("ship", "fix", "needs-discussion")


def read_verdict(path):
    try:
        data = json.loads(path.read_text())
    except FileNotFoundError:
        return "missing", f"no verdict file at {path}"
    except (OSError, json.JSONDecodeError):
        return "invalid", f"{path} is not valid JSON"
    if not isinstance(data, dict) or data.get("verdict") not in VERDICTS:
        return "invalid", f"{path} has no verdict among {', '.join(VERDICTS)}"
    return data["verdict"], str(data.get("why", "")).strip()


def step_rules(step):
    return [
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


def step_prompt(run, plan, step, earlier=None):
    lines = [
        f"HER headless run. Decisions: {run.path / 'decisions.md'}",
        "",
        f"You are step `{step['id']}` ({step['title']}) of a HER orchestrator run.",
    ]
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
    if step.get("skill") == "judge":
        lines += [
            "", "## Verdict file",
            f"Write your verdict to {run.verdict_path(step['id'])} as JSON with the keys `verdict`",
            "(one of ship, fix, needs-discussion), `why` (one sentence) and `table` (the metrics table",
            "as a markdown string). This is the only file you may write when the step is read only.",
            "A to-pr step that depends on you runs only when the verdict is ship.",
        ]
    if earlier:
        lines += ["", f"Earlier question: {earlier[0]}", f"Sofia's answer: {earlier[1]}"]
    return "\n".join(lines + [""] + step_rules(step))


def resume_prompt(step, answer):
    return "\n".join([f"Sofia's answer: {answer}", "", "Continue your task with this answer."] + [""] + step_rules(step))


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
    if info.get("question"):
        return BLOCKED, "needs answer"
    if info["blocked"]:
        return FAILED, "blocked"
    return DONE, None


MAX_ATTEMPTS = 3
FAST_FAIL_SECONDS = 30


def candidates(config, step):
    if step.get("fallback_models"):
        fallbacks = [tuple(entry.split("/", 1)) for entry in step["fallback_models"]]
    else:
        fallbacks = config.fallbacks(step["agent"], step.get("tier"))
    chain = [(step["agent"], step["model"])]
    for option in fallbacks:
        if option not in chain:
            chain.append(option)
    return chain[:MAX_ATTEMPTS]


def fast_failure(status, seconds, info):
    if status != FAILED:
        return False
    if seconds < FAST_FAIL_SECONDS and not info["has_text"]:
        return True
    errored = info["is_error"] or str(info["subtype"] or "").startswith("error")
    return errored and not info["tool_uses"]


def checkout(cwd, branch, base):
    exists = git(cwd, "rev-parse", "--verify", "--quiet", f"refs/heads/{branch}").returncode == 0
    done = git(cwd, "checkout", branch) if exists else git(cwd, "checkout", "-b", branch, base)
    if done.returncode == 0:
        return None
    lines = (done.stderr or done.stdout).strip().splitlines()
    return f"git checkout {branch} failed: {lines[-1] if lines else done.returncode}"


class Executor:
    def __init__(self, config, run, out=print):
        self.config = config
        self.run = run
        self.plan = run.plan()
        self.out = out
        self.lock = threading.RLock()
        self.wake = threading.Event()
        self.cwd_locks = {}
        state = run.state().get("steps", {})
        self.status = {
            s["id"]: state.get(s["id"], {}).get("status") if state.get(s["id"], {}).get("status") in (DONE, BLOCKED) else PENDING
            for s in self.plan["steps"]
        }
        self.steps = {s["id"]: s for s in self.plan["steps"]}
        self.started = {}
        self.processes = {}
        self.prepared = set()

    def _prepare_repo(self, step):
        root = git_root(step["cwd"])
        if root is None:
            return None
        with self.lock:
            saved = self.run.state().get("steps", {})
            ran = any(
                saved.get(s["id"], {}).get("attempts") and git_root(s["cwd"]) == root
                for s in self.plan["steps"] if s["writes"]
            )
            first = root not in self.prepared and not ran
            self.prepared.add(root)
        if first and git(root, "status", "--porcelain").stdout.strip():
            return "dirty tree"
        if not step.get("branch"):
            return None
        base = next(
            (r.get("base") for r in self.plan.get("repos", [])
             if Path(r["path"]).expanduser().resolve() == root),
            None,
        )
        return checkout(step["cwd"], step["branch"], base or "main")

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
        if step.get("skill") == "to-pr":
            for dep in deps:
                if self.steps[dep].get("skill") != "judge":
                    continue
                verdict, why = read_verdict(self.run.verdict_path(dep))
                if verdict != "ship":
                    reason = f"judge verdict: {verdict}: {why}"
                    self.status[step["id"]] = SKIPPED
                    self._record(step["id"], status=SKIPPED, reason=reason)
                    self._say(f"skip   {step['id']}: {reason}")
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
        try:
            self._execute_step(step)
        finally:
            self.wake.set()

    def _execute_step(self, step):
        sid = step["id"]
        problem = self._prepare_repo(step) if step["writes"] else None
        if problem:
            with self.lock:
                self.status[sid] = FAILED
            self._record(sid, status=FAILED, reason=problem)
            self._say(f"{FAILED:<6} {sid}: {problem}")
            return
        saved = self.run.state().get("steps", {}).get(sid, {})
        answer = saved.get("answer")
        add_dirs = [str(self.run.path)] + [d for d in step.get("add_dirs", []) if d != step["cwd"]]
        writes = step["writes"] or step.get("skill") == "judge"
        log_path = self.run.step_log(sid)
        attempts = []
        tokens = {name: 0 for name in TOKEN_KEYS}
        has_tokens = False
        cost = 0.0
        has_cost = False
        for agent, model in candidates(self.config, step):
            current = dict(step, agent=agent, model=model)
            resume = None
            if attempts:
                self._say(f"retry  {sid} on {agent}/{model} ({attempts[-1]['reason']})")
                log_path.rename(log_path.with_name(f"{sid}.attempt{len(attempts)}.jsonl"))
            if answer and not attempts and agent == "claude" and saved.get("session_id"):
                prompt, resume = resume_prompt(current, answer), saved["session_id"]
            else:
                earlier = (saved.get("question"), answer) if answer else None
                prompt = step_prompt(self.run, self.plan, current, earlier)
            command = build_command(self.config, agent, prompt, model, step["cwd"], add_dirs, writes, resume)
            began = time.time()
            process = run_logged(command, step["cwd"], log_path, append=resume is not None)
            self.processes[sid] = process
            code = process.wait()
            result = final_result(log_path)
            info = result_info(log_path)
            status, reason = step_verdict(code, result, info)
            seconds = int(time.time() - began)
            if info["tokens"] is not None:
                has_tokens = True
                for name in tokens:
                    tokens[name] += info["tokens"][name]
            if info["cost"] is not None:
                has_cost = True
                cost += info["cost"]
            attempts.append({"agent": agent, "model": model, "status": status, "reason": reason, "seconds": seconds})
            self._record(
                sid,
                attempts=attempts,
                tokens=tokens if has_tokens else None,
                cost=cost if has_cost else None,
            )
            if code < 0 or not fast_failure(status, seconds, info):
                break
        self.run.step_output(sid).write_text(result)
        elapsed = int(time.time() - self.started[sid])
        with self.lock:
            self.status[sid] = status
        blocked = status == BLOCKED
        self._record(
            sid, status=status, exit_code=code, seconds=elapsed, reason=reason,
            question=info["question"] if blocked else None,
            session_id=info["session_id"] if blocked else None,
            answer=None,
            tokens=tokens if has_tokens else None,
            cost=cost if has_cost else None,
        )
        why = f" ({reason})" if reason else ""
        self._say(f"{status:<6} {sid} in {elapsed}s{why} -> {self.run.step_output(sid)}")

    def _pick_up_answers(self):
        if BLOCKED not in self.status.values():
            return
        steps = self.run.state().get("steps", {})
        for sid, value in self.status.items():
            if value == BLOCKED and steps.get(sid, {}).get("status") == PENDING:
                self.status[sid] = PENDING

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
            self._pick_up_answers()
            before = dict(self.status)
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
            with self.lock:
                busy = RUNNING in self.status.values()
                idle = not busy and before == self.status
            if idle:
                break
            if sys.stdout.isatty():
                with self.lock:
                    sys.stdout.write("\r\033[K" + self._status_line())
                    sys.stdout.flush()
            # Poll once a second for answers while steps run, waking at once when one ends.
            # With nothing running, the loop itself changed a status (a skip), so recheck now.
            if busy:
                self.wake.wait(1)
                self.wake.clear()
        for thread in threads:
            thread.join()
        if sys.stdout.isatty():
            sys.stdout.write("\r\033[K")
        values = self.status.values()
        if all(v == DONE for v in values):
            phase = "done"
        elif BLOCKED in values:
            phase = "needs-answer"
        else:
            phase = "finished-with-failures"
        self.run.update_state(phase=phase)
        self._write_summary()
        return phase

    def _write_summary(self):
        lines = [f"# HER run {self.run.id}", "", self.plan["summary"], "", "## Steps", ""]
        steps = self.run.state().get("steps", {})
        for step in self.plan["steps"]:
            info = steps.get(step["id"], {})
            reason = info.get("reason")
            why = f" ({reason})" if reason else ""
            tokens = info.get("tokens")
            token_text = ", ".join(f"{name} {tokens[name]}" for name in TOKEN_KEYS) if tokens else "-"
            cost = f"${info['cost']:.6f}" if info.get("cost") is not None else "-"
            lines.append(
                f"- `{step['id']}` {self.status[step['id']]}{why}: "
                f"tokens {token_text}; cost {cost}; {self.run.step_output(step['id'])}"
            )
        blocked = [sid for sid, value in self.status.items() if value == BLOCKED]
        if blocked:
            lines += ["", "## Open questions", ""]
            for sid in blocked:
                lines.append(f"- `{sid}`: {steps.get(sid, {}).get('question')}")
                lines.append(f'  answer with: her answer {sid} "..."')
        missing = self.plan.get("missing_skills", [])
        if missing:
            lines += ["", "## Skills HER is missing", ""]
            lines += [f"- `{m['name']}`: {m['would_do']} ({m['why']})" for m in missing]
        self.run.write("summary.md", "\n".join(lines) + "\n")
