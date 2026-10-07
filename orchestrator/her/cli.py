import argparse
import json
import os
import shutil
import sys
import textwrap
from dataclasses import asdict

from . import config as config_module
from . import plan as planner
from . import run as ledger
from .config import RUNS_DIR, load_config
from .run import PENDING, REPORT_STATUSES, REVIEW, REVIEW_VERDICTS, RUNNING, Run

USAGE = """commands (run by the chat controller, see `her guide`):
  her guide                        planning guide and flow
  her new [-f file]                create a run from stdin, print id and path
  her check <run>                  validate plan.json and show the plan
  her approve <run>                record Sofia's approval
  her next <run>                   ready steps as JSON
  her begin <run> <step> [--note]  pre-flight the step and print its brief
  her finish <run> <step> <STATUS> store the implementer report from stdin
  her review-brief <run> <step>    print the reviewer brief
  her review <run> <step> <verdict> store the review from stdin
  her summary <run>                write summary.md
  her runs | status [run] | show <run> <step> | config"""


def fail(message):
    print(message, file=sys.stderr)
    raise SystemExit(1)


def wrapped(text, indent):
    width = max(shutil.get_terminal_size((100, 24)).columns - len(indent), 40)
    lines = []
    for paragraph in (text or "").splitlines() or [""]:
        lines += textwrap.wrap(paragraph, width) or [""]
    return "\n".join(indent + line for line in lines)


def short_path(path):
    home = os.path.expanduser("~")
    return "~" + path[len(home):] if path.startswith(home) else path


def show_plan(plan):
    if plan.get("title"):
        print(f"Title: {plan['title']}")
    print("Plan:")
    print(wrapped(plan["summary"], "  "))
    print(f"Host: {plan['host']}" + (f"  Card: {plan['card']}" if plan.get("card") else ""))
    print("Repos:")
    for repo in plan["repos"]:
        print(f"  {repo['name']}  {short_path(repo['path'])}  base {repo.get('base', 'main')}")
    print("Steps:")
    for step in plan["steps"]:
        flags = [step["tier"], step["model"], "writes" if step["writes"] else "reads"]
        if step.get("skill"):
            flags.insert(0, step["skill"])
        if step.get("branch"):
            flags.append(step["branch"])
        if step.get("depends_on"):
            flags.append("after " + ",".join(step["depends_on"]))
        print(f"  {step['id']}  {step['title']}  [{' | '.join(flags)}]")
        print(wrapped(step["task"], "      "))
    if plan.get("missing_skills"):
        print("HER is missing these skills:")
        for skill in plan["missing_skills"]:
            print(f"  {skill['name']}: {skill['would_do']} (why: {skill['why']})")
    if plan.get("decisions"):
        print("Decisions listed:")
        for decision in plan["decisions"]:
            print(f"  {decision['id']}: {decision['question']}")


def load_plan(config, run):
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
            repo["path"] = os.path.expanduser(repo["path"])
        for step in plan.get("steps", []):
            step["cwd"] = os.path.expanduser(step["cwd"])
            step["add_dirs"] = [os.path.expanduser(d) for d in step.get("add_dirs", [])]
    except (KeyError, TypeError, AttributeError) as error:
        return None, [f"plan.json has the wrong shape: {error!r}"]
    run.save_plan(plan)
    return plan, planner.validate(plan, config)


def checked(config, run):
    plan, problems = load_plan(config, run)
    if problems:
        fail("Problems in plan.json:\n" + "\n".join(f"  - {p}" for p in problems))
    return plan


def approved_plan(run):
    if not run.state().get("approved"):
        fail(f"run {run.id} is not approved, show Sofia the plan and run `her approve {run.id}`")
    return run.plan()


def find_step(plan, sid):
    for step in plan["steps"]:
        if step["id"] == sid:
            return step
    fail(f"no step {sid}")


def command_guide(args):
    print(planner.guide_text(load_config()))


def command_new(args):
    text = open(args.file).read() if args.file else sys.stdin.read()
    if not text.strip():
        fail("empty request")
    run = Run.create(text.strip())
    print(f"id {run.id}")
    print(f"path {run.path}")


def command_check(args):
    config = load_config()
    run = Run.find(args.run)
    plan = checked(config, run)
    show_plan(plan)
    for warning in planner.warnings(plan, config):
        print(f"WARNING: {warning}")


def command_approve(args):
    config = load_config()
    run = Run.find(args.run)
    checked(config, run)
    run.update_state(approved=True, phase="running")
    print(f"approved {run.id}")


def command_next(args):
    run = Run.find(args.run)
    plan = approved_plan(run)
    ready = ledger.ready_steps(run)
    open_steps = {
        step["id"]: run.step_status(step["id"]) for step in plan["steps"]
        if run.step_status(step["id"]) in (RUNNING, REVIEW, ledger.BLOCKED)
    }
    if not ready and not open_steps:
        run.update_state(phase="finished")
    print(json.dumps({
        "ready": [{"id": s["id"], "title": s["title"], "model": s["model"], "writes": s["writes"]} for s in ready],
        "open": open_steps,
        "finished": not ready and not open_steps,
    }, indent=2))


def command_begin(args):
    run = Run.find(args.run)
    step = find_step(approved_plan(run), args.step)
    status = run.step_status(step["id"])
    if status not in (PENDING, RUNNING, ledger.BLOCKED):
        fail(f"step {step['id']} is {status}, it cannot begin")
    problem = ledger.preflight(run, step)
    if problem:
        run.record(step["id"], status=ledger.BLOCKED, reason=problem)
        fail(f"step {step['id']} blocked: {problem}")
    info = run.step_state(step["id"])
    run.record(step["id"], status=RUNNING, began=True, attempts=info.get("attempts", 0) + 1)
    print(f"model {step['model']}")
    print(f"readonly {str(not step['writes']).lower()}")
    print("---")
    print(ledger.brief(run, step, args.note))


def command_finish(args):
    run = Run.find(args.run)
    step = find_step(approved_plan(run), args.step)
    if run.step_status(step["id"]) != RUNNING:
        fail(f"step {step['id']} is not running")
    report = sys.stdin.read()
    status = args.status.upper()
    if status not in REPORT_STATUSES:
        fail(f"status must be one of {', '.join(REPORT_STATUSES)}")
    print(f"{step['id']} {ledger.finish(run, step, status, report)}")


def command_review_brief(args):
    run = Run.find(args.run)
    step = find_step(approved_plan(run), args.step)
    if run.step_status(step["id"]) != REVIEW:
        fail(f"step {step['id']} is not waiting for review")
    print(ledger.review_brief(run, step))


def command_review(args):
    run = Run.find(args.run)
    step = find_step(approved_plan(run), args.step)
    if run.step_status(step["id"]) != REVIEW:
        fail(f"step {step['id']} is not waiting for review")
    if args.verdict not in REVIEW_VERDICTS:
        fail(f"verdict must be one of {', '.join(REVIEW_VERDICTS)}")
    print(f"{step['id']} {ledger.review(run, step, args.verdict, sys.stdin.read())}")


def command_summary(args):
    run = Run.find(args.run)
    print(ledger.write_summary(run))


def command_runs(args):
    if not RUNS_DIR.exists():
        print("no runs yet")
        return
    for path in sorted(p for p in RUNS_DIR.glob("*") if p.is_dir()):
        run = Run(path)
        plan = run.plan() if (path / "plan.json").exists() else None
        first = run.request().splitlines()[:1]
        title = (plan or {}).get("title") or (first[0][:60] if first else "")
        print(f"  {run.id}  {run.state().get('phase', '?')}  {title}")


def command_status(args):
    run = Run.find(args.run)
    state = run.state()
    print(f"{run.id}  phase {state.get('phase', '?')}  approved {state.get('approved', False)}")
    plan = run.plan() if (run.path / "plan.json").exists() else None
    if not plan:
        print("  no plan yet")
        return
    for step in plan["steps"]:
        info = state.get("steps", {}).get(step["id"], {})
        reason = f"  {info['reason']}" if info.get("reason") else ""
        print(f"  {step['id']}  {info.get('status', PENDING)}  {step['title']}{reason}")


def command_show(args):
    run = Run.find(args.run)
    for path in (run.step_output(args.step), run.review_path(args.step), run.verdict_path(args.step)):
        if path.exists():
            print(f"== {path.name}")
            print(path.read_text())


def command_config(args):
    config = load_config()
    found = "found" if config_module.CONFIG_FILE.exists() else "not found, using defaults"
    print(f"config file: {config_module.CONFIG_FILE} ({found})")
    print(json.dumps(asdict(config), indent=2))


def build_parser():
    parser = argparse.ArgumentParser(
        prog="her", epilog=USAGE, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    sub = parser.add_subparsers(dest="command", required=True)

    def add(name, handler, *arguments):
        command = sub.add_parser(name)
        for flags, options in arguments:
            command.add_argument(*flags, **options)
        command.set_defaults(handler=handler)

    run_arg = (("run",), {})
    step_arg = (("step",), {})
    add("guide", command_guide)
    add("new", command_new, (("-f", "--file"), {}))
    add("check", command_check, run_arg)
    add("approve", command_approve, run_arg)
    add("next", command_next, run_arg)
    add("begin", command_begin, run_arg, step_arg, (("--note",), {}))
    add("finish", command_finish, run_arg, step_arg, (("status",), {}))
    add("review-brief", command_review_brief, run_arg, step_arg)
    add("review", command_review, run_arg, step_arg, (("verdict",), {}))
    add("summary", command_summary, run_arg)
    add("runs", command_runs)
    add("status", command_status, (("run",), {"nargs": "?"}))
    add("show", command_show, run_arg, step_arg)
    add("config", command_config)
    return parser


def main(argv=None):
    args = build_parser().parse_args(sys.argv[1:] if argv is None else argv)
    args.handler(args)
