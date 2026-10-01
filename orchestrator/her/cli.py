import argparse
import json
import os
import shutil
import signal
import subprocess
import sys
import textwrap
import time
from dataclasses import asdict

from . import config as config_module
from . import plan as planner
from .agents import pretty_lines
from .config import RUNS_DIR, load_config
from .run import BLOCKED, DONE, FAILED, PENDING, SKIPPED, Executor, Run

RECENT_RUNS = 5
USAGE = """commands:
  her guide                  planning guide for the chat agent
  her new [-f file]          create a run from stdin, print id and path
  her check <run>            validate plan.json and show the plan
  her start <run>            run the pipeline detached, open the dashboard
  her watch [run]            live dashboard
  her answer <step> <text> [run]  answer a BLOCKED step and resume it
  her stop <run>             stop a running pipeline
  her runs                   list all runs
  her status [run]           plan steps with state
  her show <run> <step>      print a step output
  her logs <run> <step> [-f] print a step log, optionally follow it
  her config                 print the effective config"""


def terminal_width():
    return shutil.get_terminal_size((100, 24)).columns


def all_runs():
    if not RUNS_DIR.exists():
        return []
    return [Run(path) for path in sorted(RUNS_DIR.glob("*")) if path.is_dir()]


def run_phase(run):
    return run.state().get("phase", "?")


def print_table(header, rows):
    widths = [max(len(row[i]) for row in [header, *rows]) for i in range(len(header))]
    for row in [header, *rows]:
        cells = [cell.ljust(widths[i]) for i, cell in enumerate(row)]
        print("  " + "  ".join(cells).rstrip())


def short_path(path):
    home = os.path.expanduser("~")
    return "~" + path[len(home):] if path.startswith(home) else path


def wrapped(text, indent):
    width = max(terminal_width() - len(indent), 40)
    lines = []
    for paragraph in text.splitlines() or [""]:
        lines += textwrap.wrap(paragraph, width) or [""]
    return "\n".join(indent + line for line in lines)


def show_plan(plan):
    print()
    if plan.get("title"):
        print(f"Title: {plan['title']}")
    print(wrapped(f"Plan: {plan['summary']}", ""))
    print()
    print("Repos:")
    for repo in plan["repos"]:
        print(f"  {repo['name']}  {short_path(repo['path'])}")
    print()
    rows = []
    for step in plan["steps"]:
        rows.append([
            step["id"],
            step["skill"] or "-",
            f"{step['agent']}/{step['model']}",
            "writes" if step["writes"] else "reads",
            ",".join(step["depends_on"]) or "-",
            short_path(step["cwd"]),
        ])
    print_table(["id", "skill", "agent/model", "mode", "depends_on", "cwd"], rows)
    for step in plan["steps"]:
        print()
        print(f"  {step['id']}: {step['title']}")
        print(wrapped(step["task"], "      "))
    if plan["missing_skills"]:
        print()
        print("HER is missing these skills:")
        for skill in plan["missing_skills"]:
            print(f"  {skill['name']}")
            print(wrapped(f"{skill['would_do']} (why: {skill['why']})", "      "))
    if plan["decisions"]:
        print()
        print("Decisions listed:")
        for decision in plan["decisions"]:
            print(wrapped(f"{decision['id']}: {decision['question']}", "  "))
    print()


def load_checked_plan(config, run):
    if not (run.path / "plan.json").exists():
        return None, [f"no plan.json in {run.path}"]
    try:
        plan = run.plan()
    except json.JSONDecodeError as error:
        return None, [f"plan.json is not valid JSON: {error}"]
    if not isinstance(plan, dict):
        return None, ["plan.json must be a JSON object"]
    try:
        for repo in plan.get("repos", []):
            repo["path"] = os.path.expanduser(repo.get("path", ""))
        for step in plan.get("steps", []):
            step["cwd"] = os.path.expanduser(step.get("cwd", ""))
            step["add_dirs"] = [os.path.expanduser(d) for d in step.get("add_dirs", [])]
        run.save_plan(plan)
        problems = planner.validate(plan, config)
    except (KeyError, TypeError, AttributeError) as error:
        return None, [f"plan.json has the wrong shape: {error!r}"]
    return plan, problems


def check_run(config, run):
    plan, problems = load_checked_plan(config, run)
    if problems:
        print("Problems in plan.json:")
        for problem in problems:
            print(f"  - {problem}")
        return False
    show_plan(plan)
    for warning in planner.warnings(plan, config):
        print(f"WARNING: {warning}")
    return True


def pid_alive(pid):
    if not pid:
        return False
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    return True


def command_guide(args):
    print(planner.guide_text(load_config()))
    return 0


def command_new(args):
    text = open(args.file).read() if args.file else sys.stdin.read()
    if not text.strip():
        print("empty request")
        return 1
    run = Run.create(text.strip())
    print(f"id {run.id}")
    print(f"path {run.path}")
    return 0


def command_check(args):
    return 0 if check_run(load_config(), Run.find(args.run)) else 1


def spawn_detached(command, log_path=None):
    log = open(log_path, "a") if log_path else subprocess.DEVNULL
    return subprocess.Popen(
        command,
        stdin=subprocess.DEVNULL,
        stdout=log,
        stderr=subprocess.STDOUT if log_path else subprocess.DEVNULL,
        start_new_session=True,
    )


def open_dashboard(run):
    watch = [sys.executable, "-m", "her", "watch", run.id]
    if shutil.which("ghostty"):
        spawn_detached(["ghostty", "-e", *watch])
        return True
    if shutil.which("gnome-terminal"):
        spawn_detached(["gnome-terminal", "--", *watch])
        return True
    return False


def launch_executor(run):
    process = spawn_detached([sys.executable, "-u", "-m", "her", "exec", run.id], run.path / "executor.log")
    run.update_state(approved=True, phase="approved", executor_pid=process.pid)
    return process


def command_start(args):
    config = load_config()
    run = Run.find(args.run)
    if pid_alive(run.state().get("executor_pid")):
        print(f"run {run.id} is already executing (pid {run.state()['executor_pid']})")
        return 1
    if not check_run(config, run):
        return 1
    process = launch_executor(run)
    print(f"run {run.id} started (pid {process.pid})")
    if not args.no_window and open_dashboard(run):
        print("dashboard opened in a new window")
    print(f"watch with: her watch {run.id}")
    return 0


def command_exec(args):
    run = Run.find(args.run)
    run.update_state(executor_pid=os.getpid())
    try:
        phase = Executor(load_config(), run).execute()
    finally:
        run.update_state(executor_pid=None)
    return 0 if phase == "done" else 1


def command_answer(args):
    run = Run.find(args.run)
    state = run.state()
    info = state.get("steps", {}).get(args.step, {})
    if info.get("status") != BLOCKED:
        print(f"step {args.step} is not blocked in {run.id} (state: {info.get('status', 'pending')})")
        return 1
    run.add_decision(info.get("question"), args.text)
    state["steps"][args.step].update(status=PENDING, answer=args.text, reason=None)
    run.save_state(state)
    if pid_alive(state.get("executor_pid")):
        print(f"step {args.step} answered, the running executor will resume it")
    else:
        launch_executor(run)
        print(f"step {args.step} answered, executor started")
    print(f"watch with: her watch {run.id}")
    return 0


def command_watch(args):
    from . import watch

    watch.dashboard(Run.find(args.run))
    return 0


def command_stop(args):
    run = Run.find(args.run)
    pid = run.state().get("executor_pid")
    if not pid_alive(pid):
        print(f"run {run.id} has no live executor")
        return 1
    os.killpg(pid, signal.SIGTERM)
    for _ in range(50):
        if not pid_alive(pid):
            break
        time.sleep(0.2)
    run.update_state(phase="stopped", executor_pid=None)
    print(f"stopped {run.id}")
    return 0


def command_banner():
    print("HER orchestrator")
    print()
    print("Use /her inside Claude Code or cursor-agent to start a run.")
    print()
    print(USAGE)
    print()
    print(f"Last {RECENT_RUNS} runs:")
    runs = all_runs()[-RECENT_RUNS:]
    if not runs:
        print("  (none yet)")
    for run in reversed(runs):
        print(f"  {run.id}  {run_phase(run)}")
    return 0


def command_runs(args):
    runs = all_runs()
    if not runs:
        print("no runs yet")
    for run in reversed(runs):
        print(f"{run.id}  {run_phase(run)}")
    return 0


def command_status(args):
    run = Run.find(args.run)
    state = run.state()
    print(f"run {run.id}")
    print(f"phase {state.get('phase', '?')}  approved {state.get('approved', False)}")
    plan = run.plan()
    if not plan:
        print("no plan yet")
        return 0
    rows = []
    for step in plan["steps"]:
        info = state.get("steps", {}).get(step["id"], {})
        seconds = info.get("seconds")
        code = info.get("exit_code")
        rows.append([
            step["id"],
            info.get("status", "pending"),
            "-" if seconds is None else f"{seconds}s",
            "-" if code is None else str(code),
            step["title"],
        ])
    print_table(["id", "state", "seconds", "exit", "title"], rows)
    return 0


def command_show(args):
    run = Run.find(args.run)
    output = run.step_output(args.step)
    if not output.exists():
        print(f"no output for step {args.step} in {run.id}")
        return 1
    print(output.read_text())
    return 0


def step_status(run, step_id):
    return run.state().get("steps", {}).get(step_id, {}).get("status")


def command_logs(args):
    run = Run.find(args.run)
    log_path = run.step_log(args.step)
    printed = 0
    while True:
        finished = step_status(run, args.step) in (DONE, FAILED, SKIPPED, BLOCKED)
        lines = list(pretty_lines(log_path)) if log_path.exists() else []
        for line in lines[printed:]:
            print(line)
        printed = len(lines)
        if not args.follow or finished:
            break
        time.sleep(1)
    if not log_path.exists() and not args.follow:
        print(f"no log for step {args.step} in {run.id}")
        return 1
    return 0


def command_config(args):
    config = load_config()
    print(f"config file: {config_module.CONFIG_FILE} ({'found' if config_module.CONFIG_FILE.exists() else 'not found, using defaults'})")
    print(json.dumps(asdict(config), indent=2))
    return 0


def build_parser():
    parser = argparse.ArgumentParser(prog="her", epilog=USAGE, formatter_class=argparse.RawDescriptionHelpFormatter)
    subparsers = parser.add_subparsers(dest="command", required=True)

    def add(name, handler, *arguments):
        sub = subparsers.add_parser(name)
        for names, options in arguments:
            sub.add_argument(*names, **options)
        sub.set_defaults(handler=handler)

    optional = {"nargs": "?"}
    add("guide", command_guide)
    add("new", command_new, (("-f", "--file"), {}))
    add("check", command_check, (("run",), {}))
    add("start", command_start, (("run",), {}), (("--no-window",), {"action": "store_true"}))
    add("exec", command_exec, (("run",), {}))
    add("answer", command_answer, (("step",), {}), (("text",), {}), (("run",), optional))
    add("watch", command_watch, (("run",), optional))
    add("stop", command_stop, (("run",), {}))
    add("runs", command_runs)
    add("status", command_status, (("run",), optional))
    add("show", command_show, (("run",), {}), (("step",), {}))
    add("logs", command_logs, (("run",), {}), (("step",), {}), (("-f", "--follow"), {"action": "store_true"}))
    add("config", command_config)
    return parser


def main(argv=None):
    argv = sys.argv[1:] if argv is None else list(argv)
    if not argv:
        return command_banner()
    args = build_parser().parse_args(argv)
    return args.handler(args)
