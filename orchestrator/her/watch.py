import curses
import re
import textwrap
import time
from pathlib import Path

from .agents import pretty_lines

ORDER = ("running", "blocked", "failed", "done", "pending", "skipped")
PHASE_END = ("done", "finished-with-failures", "needs-answer")
LABELS = {"blocked": "needs answer"}
HINTS = "[up/down] step  [enter] full log  [q] close (run continues)"
VIEW_HINTS = "[up/down PgUp/PgDn g/G] scroll  [q/esc] back"


def short_model(agent, model):
    model = re.sub(r"-\d{8}$", "", (model or "").removeprefix("claude-"))
    return "/".join(part for part in (agent, model) if part) or "-"


def fmt_elapsed(seconds):
    seconds = int(seconds)
    if seconds < 60:
        return f"{seconds}s"
    if seconds < 3600:
        return f"{seconds // 60}m{seconds % 60:02d}s"
    return f"{seconds // 3600}h{seconds % 3600 // 60:02d}m"


def tilde(path):
    home = str(Path.home())
    path = str(path or "")
    return "~" + path[len(home):] if path == home or path.startswith(home + "/") else path


def fit(text, width):
    return text if len(text) <= width else text[: max(width - 1, 0)] + ("~" if width > 0 else "")


def wrap(lines, width):
    out = []
    for line in lines:
        for part in (line.expandtabs(4).splitlines() or [""]):
            part = "".join(c if c.isprintable() else "?" for c in part)
            out += textwrap.wrap(part, max(width, 1), replace_whitespace=False) or [""]
    return out


def step_status(state, sid):
    return state.get("steps", {}).get(sid, {}).get("status", "pending")


def default_selection(plan, state):
    steps = (plan or {}).get("steps", [])
    statuses = [step_status(state, s["id"]) for s in steps]
    for wanted in ("running", "blocked", "failed"):
        if wanted in statuses:
            return statuses.index(wanted)
    return max(len(steps) - 1, 0)


def step_tail(step, info, status, now):
    if status == "running":
        started = info.get("started_at")
        if started:
            return fmt_elapsed(max(now - started, 0))
    if status == "pending" and step.get("depends_on"):
        return "<- " + ", ".join(step["depends_on"])
    if status in ("done", "failed", "running", "blocked") and info.get("seconds") is not None:
        return fmt_elapsed(info["seconds"])
    return ""


def step_rows(plan, state, selected, now):
    steps = plan.get("steps", [])
    w_id = max([len(s["id"]) for s in steps] + [1])
    skills = [f"/her:{s['skill']}" if s.get("skill") else "-" for s in steps]
    models = [short_model(s.get("agent"), s.get("model")) for s in steps]
    w_skill, w_model = max(map(len, skills), default=1), max(map(len, models), default=1)
    rows = []
    w_status = max([8] + [len(LABELS.get(step_status(state, s["id"]), "")) for s in steps])
    for i, step in enumerate(steps):
        info = state.get("steps", {}).get(step["id"], {})
        status = step_status(state, step["id"])
        tail = step_tail(step, info, status, now)
        mark = ">" if i == selected else " "
        text = f"{mark} {LABELS.get(status, status):<{w_status}} {step['id']:<{w_id}} {skills[i]:<{w_skill}} {models[i]:<{w_model}} {tail}"
        rows.append((text.rstrip(), status if status in ORDER else "pending"))
    return rows


def blocked_foot(plan, state, width):
    asking = [
        (s["id"], state["steps"][s["id"]].get("question") or "")
        for s in plan.get("steps", [])
        if step_status(state, s["id"]) == "blocked"
    ]
    if not asking:
        return []
    foot = [(line, "blocked") for sid, question in asking for line in wrap([f"{sid} needs answer: {question}"], width)]
    foot.append((fit(f'answer with: her answer {asking[0][0]} "..."', width), "head"))
    return foot


def header_row(plan, state, width):
    steps = plan.get("steps", [])
    counts = {}
    for s in steps:
        status = step_status(state, s["id"])
        counts[status] = counts.get(status, 0) + 1
    right = " | ".join(f"{k} {counts[k]}" for k in ORDER if k in counts)
    phase = state.get("phase", "")
    right = f"{phase}  {right}".strip()
    title = plan.get("title") or plan.get("summary") or "(no plan yet)"
    title = " ".join(title.split())
    left = fit("HER  " + title, max(width - len(right) - 2, 5))
    return (f"{left:<{max(width - len(right), len(left))}}{right}", "head")


def render(plan, state, selected, width, height, log_lines, now=None, summary_path=None):
    if width < 1 or height < 1:
        return []
    plan, state = plan or {}, state or {}
    now = time.time() if now is None else now
    steps = plan.get("steps", [])
    rule = ("-" * width, "dim")
    foot = blocked_foot(plan, state, width)
    if state.get("phase") in PHASE_END:
        foot.append((f"{state['phase']}: {summary_path or 'summary.md'}", "head"))
        missing = [m.get("name", "?") for m in plan.get("missing_skills", [])]
        if missing:
            foot.append(("missing skills: " + ", ".join(missing), "dim"))
    fixed = 4 + len(foot) + 1
    shown = min(len(steps), max(1, height - fixed - 3))
    start = min(max(selected - shown // 2, 0), max(len(steps) - shown, 0))
    body = step_rows(plan, state, selected, now)[start : start + shown]
    if not steps:
        body = [("  waiting for a plan...", "dim")]
    sel = steps[selected] if 0 <= selected < len(steps) else None
    detail = f"{sel['id']} | {tilde(sel.get('cwd'))}" if sel else ""
    room = max(height - fixed - len(body), 0)
    tail = wrap(log_lines or [], width - 2)[-room:] if room else []
    rows = [header_row(plan, state, width), rule, *body, rule, (detail, "head")]
    rows += [("  " + line, "text") for line in tail]
    rows = rows[: height - len(foot) - 1]
    rows += [(t, s) for t, s in foot] if height > 1 else []
    rows = rows[: height - 1]
    rows.append((HINTS, "dim"))
    return [(fit(t, width), s) for t, s in rows][:height]


def view_rows(title, lines, offset, width, height):
    body = wrap(lines, width)
    room = max(height - 2, 0)
    offset = min(max(offset, 0), max(len(body) - room, 0))
    rows = [(fit(title, width), "head"), *[(t, "text") for t in body[offset : offset + room]]]
    rows = rows[: height - 1] if height > 1 else rows
    rows.append((fit(VIEW_HINTS, width), "dim"))
    return rows[:height], offset


def load(run):
    try:
        plan = run.plan()
    except (OSError, ValueError):
        plan = None
    try:
        state = run.state()
    except (OSError, ValueError):
        state = {}
    return plan or {}, state


def content_lines(run, sid, status):
    try:
        out = run.step_output(sid)
        if status == "done" and out.exists() and out.read_text().strip():
            return out.read_text().splitlines()
        if run.step_log(sid).exists():
            return list(pretty_lines(run.step_log(sid)))
    except OSError:
        pass
    return []


def attrs():
    if not curses.has_colors():
        return {"head": curses.A_BOLD, "dim": curses.A_DIM, "skipped": curses.A_DIM}
    curses.use_default_colors()
    for i, color in enumerate((curses.COLOR_GREEN, curses.COLOR_YELLOW, curses.COLOR_RED, curses.COLOR_CYAN), 1):
        curses.init_pair(i, color, -1)
    return {
        "head": curses.A_BOLD,
        "dim": curses.A_DIM,
        "skipped": curses.A_DIM,
        "done": curses.color_pair(1),
        "running": curses.color_pair(2),
        "failed": curses.color_pair(3),
        "blocked": curses.color_pair(4),
    }


def paint(stdscr, rows, style):
    stdscr.erase()
    for y, (text, key) in enumerate(rows):
        try:
            stdscr.addstr(y, 0, text, style.get(key, 0))
        except curses.error:
            pass
    stdscr.refresh()


def full_view(stdscr, run, sid, style):
    offset, follow = 0, False
    while True:
        plan, state = load(run)
        lines = content_lines(run, sid, step_status(state, sid))
        height, width = stdscr.getmaxyx()
        rows, offset = view_rows(f"{sid} | full", lines, 10**9 if follow else offset, width - 1, height)
        paint(stdscr, rows, style)
        key = stdscr.getch()
        page = max(height - 3, 1)
        if key in (ord("q"), 27):
            return
        if key != -1:
            follow = key == ord("G")
        if key in (curses.KEY_UP, ord("k")):
            offset -= 1
        elif key in (curses.KEY_DOWN, ord("j")):
            offset += 1
        elif key == curses.KEY_PPAGE:
            offset -= page
        elif key == curses.KEY_NPAGE:
            offset += page
        elif key == ord("g"):
            offset = 0


def loop(stdscr, run):
    try:
        curses.curs_set(0)
    except curses.error:
        pass
    style = attrs()
    stdscr.keypad(True)
    stdscr.timeout(1000)
    selected = None
    while True:
        plan, state = load(run)
        steps = plan.get("steps", [])
        if selected is None:
            selected = default_selection(plan, state)
        selected = min(max(selected, 0), max(len(steps) - 1, 0))
        sid = steps[selected]["id"] if steps else None
        lines = content_lines(run, sid, step_status(state, sid)) if sid else []
        height, width = stdscr.getmaxyx()
        rows = render(plan, state, selected, width - 1, height, lines, summary_path=run.path / "summary.md")
        paint(stdscr, rows, style)
        key = stdscr.getch()
        if key in (ord("q"), 27):
            return
        if key in (curses.KEY_UP, ord("k")):
            selected -= 1
        elif key in (curses.KEY_DOWN, ord("j")):
            selected += 1
        elif key in (10, 13, curses.KEY_ENTER) and sid:
            full_view(stdscr, run, sid, style)


def dashboard(run):
    curses.wrapper(loop, run)
