import json
import os
import re
from pathlib import Path

from .repo import dirty_files, git_root, resolved
from .config import TIERS
from .skills import catalog, catalog_text

BRANCH_PATTERN = re.compile(
    r"(feat|fix|proposal|chore|refactor|docs|test)/([A-Z][A-Z0-9]*-[0-9]+|[a-z0-9]+)(_[A-Za-z0-9]+)+"
)

PER_REPO_SKILLS = ("judge", "to-pr")
CARD_PATTERN = re.compile(r"[A-Z][A-Z0-9]*-[0-9]+")

PLAN_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "required": ["summary", "host", "repos", "decisions", "steps", "missing_skills"],
    "properties": {
        "title": {"type": "string"},
        "host": {"type": "string"},
        "card": {"type": "string"},
        "summary": {"type": "string"},
        "repos": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["name", "path"],
                "properties": {
                    "name": {"type": "string"},
                    "path": {"type": "string"},
                    "base": {"type": "string"},
                },
            },
        },
        "decisions": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["id", "question", "recommendation", "why"],
                "properties": {
                    "id": {"type": "string"},
                    "question": {"type": "string"},
                    "recommendation": {"type": "string"},
                    "why": {"type": "string"},
                },
            },
        },
        "steps": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": [
                    "id", "title", "skill", "tier", "agent", "model",
                    "cwd", "add_dirs", "writes", "depends_on", "task",
                ],
                "properties": {
                    "id": {"type": "string"},
                    "title": {"type": "string"},
                    "skill": {"type": ["string", "null"]},
                    "tier": {"type": "string", "enum": list(TIERS)},
                    "agent": {"type": "string"},
                    "model": {"type": "string"},
                    "cwd": {"type": "string"},
                    "add_dirs": {"type": "array", "items": {"type": "string"}},
                    "writes": {"type": "boolean"},
                    "depends_on": {"type": "array", "items": {"type": "string"}},
                    "task": {"type": "string"},
                    "branch": {"type": "string"},
                },
            },
        },
        "missing_skills": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["name", "why", "would_do"],
                "properties": {
                    "name": {"type": "string"},
                    "why": {"type": "string"},
                    "would_do": {"type": "string"},
                },
            },
        },
    },
}


def _models_text(config):
    lines = []
    for agent in config.agents():
        for tier in TIERS:
            lines.append(f"- agent `{agent}`, tier `{tier}`:")
            for model in config.allowed(agent, tier):
                note = config.model_notes.get(f"{agent}/{model}", {})
                detail = f" - {note.get('strengths', 'no notes')} (relative cost {note.get('relative_cost', '?')}/5)"
                lines.append(f"  - `{model}`{detail}")
    return "\n".join(lines)


def guide_text(config):
    return "\n".join([
        "# HER planning guide",
        "",
        "You are the controller: the chat session Sofia talks to. You grill, plan, dispatch one",
        "fresh subagent per step, review its work with another fresh subagent, and report to Sofia.",
        "You never do step work yourself. The run ledger in ~/.her/runs/<id>/ is your memory.",
        "",
        "## Skills available as steps",
        catalog_text(catalog()),
        "",
        "## Models (step.model must be one of these for the host and step.tier)",
        _models_text(config),
        "",
        "## How to plan",
        "- Set `host` to the app you run in (`claude` for Claude Code, `cursor` for cursor-agent).",
        "  Every step uses `agent` equal to `host`: you can only dispatch subagents of your own app.",
        "- If the request names a Kineloop card (like ML-86), set `card`, read the card with the",
        "  Kineloop tools while grilling, and put the card ID in branch names.",
        "- Interactive skills are never steps. Anything that needs Sofia's judgment (a domain rule,",
        "  a trade-off, naming, scope) is settled by grilling BEFORE writing the plan. Facts you can",
        "  look up are never questions: read the repos or dispatch a lookup subagent.",
        "- Write the settled decisions to <run>/decisions.md, one bullet per decision with the",
        "  question, the answer and why. Every brief includes that file.",
        "- plan.json `decisions` must be empty, or only list decisions already settled in decisions.md.",
        "- Pick the cheapest tier that can do each step and the model that fits the step type best.",
        "  Use `opus` for risky decisions, final review and verdicts.",
        "- `judge` and `to-pr` run once per repo, with cwd set to that repo and no other repo in",
        "  add_dirs. When more than one repo has `to-pr` steps, add a final step that links the",
        "  companion PRs to each other.",
        "- `skill` is a skill name from the list, or null when no skill fits. When a step needs a",
        "  capability no HER skill covers, still plan it with skill null and add an entry to",
        "  `missing_skills` describing the skill that should exist.",
        "- `task` is self-contained: goal, exact paths, what to produce and in what shape. Size each",
        "  writing step so one subagent finishes it and a reviewer can check it in one pass.",
        "- `cwd` is an absolute path. `add_dirs` lists other absolute dirs the step must read or edit.",
        "- `writes` is true only when the step edits files. Steps never commit, push or open PRs",
        "  unless the request explicitly asks for it.",
        "- `depends_on` lists step ids whose report this step needs. End code-changing pipelines",
        "  with a `judge` step. A `to-pr` step after a judge step is skipped unless the verdict is ship.",
        "- A writing step whose cwd is a git repo must set `branch`, shaped",
        "  `<type>/<CARD-or-word>_<words_with_underscores>` with type feat, fix, proposal, chore,",
        "  refactor, docs or test (hyphen only inside a card ID, e.g. feat/ML-88_export_csv).",
        "  `her begin` checks it out, creating it from the repo `base` (default main) when missing.",
        "  The first writing step in a repo refuses a dirty tree.",
        "- `title` is a short label for the step.",
        "",
        "## Flow",
        "1. `her new` with the request on stdin prints `id` and `path`.",
        "2. Grill Sofia, write <path>/decisions.md and <path>/plan.json.",
        "3. `her check <id>` until it prints the plan without problems.",
        "4. Show Sofia the plan and the missing skills. On approval run `her approve <id>`.",
        "   With a card, move it to started in Kineloop.",
        "5. Loop until `her next <id>` returns no ready steps:",
        f"   a. For each ready step (at most {config.max_parallel} at once; `her next` already holds",
        "      back a second writing step in the same repo): `her begin <id> <sid>` prints the brief.",
        "      Dispatch a fresh subagent with the step model and the brief pasted verbatim.",
        "   b. Pipe the report to `her finish <id> <sid> <STATUS>` with the status from its last line.",
        "   c. A writing step goes to review: `her review-brief <id> <sid>` prints the review brief.",
        "      Dispatch a fresh read-only reviewer on the `opus` tier and pipe its reply to",
        "      `her review <id> <sid> approve|changes`. On changes, `her begin` again and dispatch a",
        "      fresh implementer: the brief carries the review. After 3 rounds the step is blocked.",
        "   d. A blocked step (NEEDS_CONTEXT, BLOCKED, too many review rounds) goes to Sofia. Ask her",
        "      in the chat, then `her begin <id> <sid> --note \"<answer>\"` and dispatch again. A step",
        "      that blocks on capability may move up a tier: change its model in plan.json and run",
        "      `her check` first.",
        "6. `her summary <id>`, show Sofia the summary and PR links. With a card, comment the",
        "   summary on it and move it to review when PRs are open.",
        "",
        "## plan.json schema",
        json.dumps(PLAN_SCHEMA, indent=2),
    ])


def validate(plan, config):
    problems = []
    for key in PLAN_SCHEMA["required"]:
        if key not in plan:
            problems.append(f"missing top-level key {key}")
    step_keys = PLAN_SCHEMA["properties"]["steps"]["items"]["required"]
    for number, step in enumerate(plan.get("steps", []), 1):
        for key in step_keys:
            if key not in step:
                problems.append(f"step {step.get('id', number)}: missing key {key}")
    if problems:
        return problems
    if plan["host"] not in config.agents():
        problems.append(f"unknown host {plan['host']}, use one of {', '.join(config.agents())}")
    if plan.get("card") and not CARD_PATTERN.fullmatch(plan["card"]):
        problems.append(f"card {plan['card']} must look like ML-86")
    skills = catalog()
    ids = [step["id"] for step in plan.get("steps", [])]
    if len(ids) != len(set(ids)):
        problems.append("step ids must be unique")
    for step in plan.get("steps", []):
        sid = step.get("id")
        skill = step.get("skill")
        if skill and skill not in skills:
            problems.append(f"step {sid}: unknown skill {skill}")
        if skill and skills.get(skill, {}).get("interactive"):
            problems.append(f"step {sid}: skill {skill} is interactive, move it to decisions")
        if step.get("agent") not in config.agents():
            problems.append(f"step {sid}: unknown agent {step.get('agent')}")
        elif step.get("model") not in config.allowed(step["agent"], step.get("tier")):
            problems.append(
                f"step {sid}: model {step.get('model')} not allowed for {step['agent']}/{step.get('tier')}"
            )
        cwd = Path(os.path.expanduser(step.get("cwd", "")))
        if not cwd.is_dir():
            problems.append(f"step {sid}: cwd {step.get('cwd')} does not exist")
        elif step.get("writes") and not step.get("branch") and git_root(cwd):
            problems.append(f"step {sid}: writes in a git repo, declare branch")
        if step.get("branch") and not BRANCH_PATTERN.fullmatch(step["branch"]):
            problems.append(
                f"step {sid}: branch {step['branch']} must look like feat/ML-88_short_words or fix/word_more_words"
            )
        if step.get("agent") != plan.get("host"):
            problems.append(f"step {sid}: agent {step.get('agent')} differs from host {plan.get('host')}")
        for dep in step.get("depends_on", []):
            if dep not in ids:
                problems.append(f"step {sid}: depends on unknown step {dep}")
        if skill in PER_REPO_SKILLS:
            problems.extend(_other_repo_problems(step, plan.get("repos", [])))
    if _has_cycle(plan.get("steps", [])):
        problems.append("depends_on has a cycle")
    problems.extend(_preflight_problems(plan, config))
    return problems


def _other_repo_problems(step, repos):
    own = resolved(step.get("cwd", ""))
    problems = []
    for repo in repos:
        root = resolved(repo.get("path", ""))
        if own == root or root in own.parents:
            continue
        for extra in step.get("add_dirs", []):
            path = resolved(extra)
            if path == root or root in path.parents:
                problems.append(
                    f"step {step['id']}: {step['skill']} runs once per repo, remove {repo.get('name', root)} from add_dirs"
                )
                break
    return problems


def _preflight_problems(plan, config):
    problems = []
    steps = plan.get("steps", [])
    writers = [step for step in steps if step.get("writes")]
    for repo in plan.get("repos", []):
        root = resolved(repo.get("path", ""))
        if not root.is_dir() or git_root(root) is None:
            problems.append(f"repo {repo.get('name', root)}: {root} is not a git repo")
            continue
        touched = any(
            root in resolved(p).parents or resolved(p) == root
            for step in writers
            for p in [step.get("cwd", ""), *step.get("add_dirs", [])]
        )
        dirty = dirty_files(root) if touched else []
        if dirty:
            problems.append(
                f"repo {repo.get('name', root)}: dirty tree, commit or stash first: "
                + ", ".join(line.strip() for line in dirty[:10])
                + (f" and {len(dirty) - 10} more" if len(dirty) > 10 else "")
            )
    return problems


def warnings(plan, config):
    found = []
    if not any(step.get("skill") == "judge" for step in plan.get("steps", [])) and any(
        step.get("writes") for step in plan.get("steps", [])
    ):
        found.append("the plan changes code but has no judge step")
    return found


def _has_cycle(steps):
    graph = {step["id"]: step.get("depends_on", []) for step in steps}
    state = {}

    def visit(node):
        if state.get(node) == 1:
            return True
        if state.get(node) == 2 or node not in graph:
            return False
        state[node] = 1
        if any(visit(dep) for dep in graph[node]):
            return True
        state[node] = 2
        return False

    return any(visit(node) for node in graph)
