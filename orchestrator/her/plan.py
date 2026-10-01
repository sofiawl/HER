import json
import os
import re
from pathlib import Path

from .agents import git_root
from .config import TIERS
from .skills import catalog, catalog_text

BRANCH_PATTERN = re.compile(
    r"(feat|fix|proposal|chore|refactor|docs|test)/([A-Z][A-Z0-9]*-[0-9]+|[a-z0-9]+)(_[a-z0-9]+)+"
)

PLAN_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "required": ["summary", "repos", "decisions", "steps", "missing_skills"],
    "properties": {
        "title": {"type": "string"},
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
                    "fallback_models": {"type": "array", "items": {"type": "string"}},
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
            lines.append(f"- agent `{agent}`, tier `{tier}`: {', '.join(config.allowed(agent, tier))}")
    return "\n".join(lines)


def guide_text(config):
    return "\n".join([
        "# HER planning guide",
        "",
        "You are the chat agent. Act as /her:ask-her: read the repos, settle every decision with",
        "Sofia by grilling in this conversation, then write the plan files and call `her`.",
        "",
        "## Skills available as steps",
        catalog_text(catalog()),
        "",
        "## Agents and models (step.model must be one of these for step.agent and step.tier)",
        _models_text(config),
        "",
        "## How to plan",
        "- Each step runs headless (no human in the loop) in its own agent process. Interactive",
        "  skills are never steps.",
        "- Anything that needs Sofia's judgment (a domain rule, a trade-off, naming, scope) is settled",
        "  by you through grilling BEFORE writing the plan. Facts you can look up are never questions:",
        "  read the repos yourself.",
        "- A step that still needs Sofia ends its reply with `QUESTION: ...`. It becomes BLOCKED,",
        "  its dependents wait, and `her answer <step_id> \"...\"` resumes it.",
        "- Write the settled decisions to <run>/decisions.md, one bullet per decision with the",
        "  question, the answer and why. Every step receives that file.",
        "- plan.json `decisions` must be empty, or only list decisions already settled in decisions.md.",
        "- Pick the cheapest tier that can do each step. Prefer agent `claude` unless another agent",
        "  is clearly cheaper for a mechanical step.",
        "- `skill` is a skill name from the list, or null when no skill fits. When a step needs a",
        "  capability no HER skill covers, still plan it with skill null and add an entry to",
        "  `missing_skills` describing the skill that should exist.",
        "- `task` is self-contained: goal, exact paths, what to produce and in what shape.",
        "- `cwd` is an absolute path. `add_dirs` lists other absolute dirs the step must read or edit.",
        "- `writes` is true only when the step edits files. Steps never commit, push or open PRs",
        "  unless the request explicitly asks for it.",
        "- `depends_on` lists step ids whose output this step needs. Independent steps run in",
        "  parallel. End code-changing pipelines with a `judge` step.",
        "- A `judge` step writes <run>/steps/<id>.verdict.json (verdict ship, fix or",
        "  needs-discussion). A `to-pr` step that depends on a judge step is skipped unless the",
        "  verdict is ship.",
        "- A writing step whose cwd is a git repo must set `branch`, shaped",
        "  `<type>/<CARD-or-word>_<words_with_underscores>` with type feat, fix, proposal, chore,",
        "  refactor, docs or test (hyphen only inside a card ID, e.g. feat/ML-88_export_csv).",
        "  The executor checks it out, creating it from the repo `base` when missing. The first",
        "  writing step in a repo fails with `dirty tree` if the repo has uncommitted changes.",
        "- A step that fails fast is retried on the same tier with the other agents, then one tier",
        "  down, at most 3 attempts. Optional `fallback_models` (list of `agent/model`) sets that",
        "  order instead.",
        "- `repos` lists every repo involved with absolute paths, and optional `base` (default",
        "  main) for new branches.",
        "- `title` is a short label shown in the dashboard.",
        "",
        "## Flow",
        "1. `her new` with the request on stdin prints `id` and `path`.",
        "2. Write <path>/decisions.md and <path>/plan.json.",
        "3. `her check <id>` until it prints the plan without problems.",
        "4. Show Sofia the plan, get approval, then `her start <id>`.",
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
        for entry in step.get("fallback_models", []):
            agent, _, model = entry.partition("/")
            if agent not in config.agents() or not model:
                problems.append(f"step {sid}: fallback model {entry} must be <agent>/<model> with a known agent")
        for dep in step.get("depends_on", []):
            if dep not in ids:
                problems.append(f"step {sid}: depends on unknown step {dep}")
    if _has_cycle(plan.get("steps", [])):
        problems.append("depends_on has a cycle")
    return problems


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
