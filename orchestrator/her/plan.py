import json
import os
import re
import shutil
from pathlib import Path

from .agents import git, git_root
from .config import TIERS
from .skills import catalog, catalog_text

BRANCH_PATTERN = re.compile(
    r"(feat|fix|proposal|chore|refactor|docs|test)/([A-Z][A-Z0-9]*-[0-9]+|[a-z0-9]+)(_[A-Za-z0-9]+)+"
)

PER_REPO_SKILLS = ("judge", "to-pr")

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
            lines.append(f"- agent `{agent}`, tier `{tier}`:")
            for model in config.allowed(agent, tier):
                note = config.model_notes.get(f"{agent}/{model}", {})
                detail = f" - {note.get('strengths', 'no notes')} (relative cost {note.get('relative_cost', '?')}/5)"
                lines.append(f"  - `{model}`{detail}")
    return "\n".join(lines)


def _preference_lines(config):
    if not config.prefer_agents:
        return []
    return [
        "- Sofia's agent preference order is " + ", ".join(f"`{a}`" for a in config.prefer_agents)
        + ". Use it to break ties between equally good fits before comparing cost.",
    ]


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
        "- Pick the cheapest tier that can do each step. Pick the model that fits the step type best,",
        "  break ties on relative cost, and do not default to one agent.",
        *_preference_lines(config),
        "- Steps run headless and cannot ask Sofia. Every decision a step needs must already be in",
        "  decisions.md and in the step's task text.",
        "- `judge` and `to-pr` run once per repo, with cwd set to that repo and no other repo in",
        "  add_dirs. When more than one repo has `to-pr` steps, add a final step that links the",
        "  companion PRs to each other.",
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
        if skill in PER_REPO_SKILLS:
            problems.extend(_other_repo_problems(step, plan.get("repos", [])))
    if _has_cycle(plan.get("steps", [])):
        problems.append("depends_on has a cycle")
    problems.extend(_preflight_problems(plan, config))
    return problems


def _resolved(path):
    return Path(os.path.expanduser(path)).resolve()


def _other_repo_problems(step, repos):
    own = _resolved(step.get("cwd", ""))
    problems = []
    for repo in repos:
        root = _resolved(repo.get("path", ""))
        if own == root or root in own.parents:
            continue
        for extra in step.get("add_dirs", []):
            path = _resolved(extra)
            if path == root or root in path.parents:
                problems.append(
                    f"step {step['id']}: {step['skill']} runs once per repo, remove {repo.get('name', root)} from add_dirs"
                )
                break
    return problems


def _dirty_files(path):
    found = git(path, "status", "--porcelain")
    return [line for line in found.stdout.splitlines() if line.strip()] if found.returncode == 0 else []


def _preflight_problems(plan, config):
    problems = []
    steps = plan.get("steps", [])
    for agent in sorted({step.get("agent") for step in steps if step.get("agent") in config.agents()}):
        if shutil.which(config.binary(agent)) is None:
            problems.append(f"agent {agent}: binary {config.binary(agent)} not found on PATH")
    writers = [step for step in steps if step.get("writes")]
    for repo in plan.get("repos", []):
        root = _resolved(repo.get("path", ""))
        if not root.is_dir() or git_root(root) is None:
            problems.append(f"repo {repo.get('name', root)}: {root} is not a git repo")
            continue
        touched = any(
            root in _resolved(p).parents or _resolved(p) == root
            for step in writers
            for p in [step.get("cwd", ""), *step.get("add_dirs", [])]
        )
        dirty = _dirty_files(root) if touched else []
        if dirty:
            problems.append(
                f"repo {repo.get('name', root)}: dirty tree, commit or stash first: "
                + ", ".join(line.strip() for line in dirty[:10])
                + (f" and {len(dirty) - 10} more" if len(dirty) > 10 else "")
            )
    return problems


def warnings(plan, config):
    used = {step.get("agent") for step in plan.get("steps", [])}
    if len(used) == 1 and len(config.agents()) > 1:
        return [
            f"every step uses agent {next(iter(used))} while {len(config.agents())} agents are configured, "
            "check that no step fits another agent better"
        ]
    return []


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
