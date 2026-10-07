# HER Orchestrator

Multi-step work run from the chat, superpowers-style, with HER skills. Works in
**Claude Code** or **Cursor** (`host` in `plan.json`). The chat session is the
controller: it grills Sofia, writes a plan, and dispatches one fresh subagent
per step, plus a fresh reviewer after every writing step. The `her` CLI is the
controller's ledger and guard rails, not something Sofia types. See `DESIGN.md`
for the decisions behind it.

## Install

```bash
uv tool install -e ~/HER/orchestrator
```

For Cursor, link the skills (`her-her` and the rest) and the subagents
(`her-implementer`, `her-reader`, `her-reviewer`):

```bash
~/HER/orchestrator/scripts/install-cursor-skills.sh
```

## How it is used

Sofia types `/her <what to do>` in Claude Code (skill `her:her`) or in
cursor-agent (skill `her-her`). The chat does the rest:

1. `her new` creates the run, `her guide` gives the rules and the flow.
2. The controller reads the repos (and the Kineloop card, if any), grills
   Sofia, writes `decisions.md` and `plan.json`, and runs `her check`.
3. Sofia approves in the chat, the controller runs `her approve`.
4. Loop: `her next` lists ready steps, `her begin` checks the branch and tree
   and prints the brief, a fresh subagent does the step, `her finish` stores
   its report, a fresh reviewer checks writing steps and `her review` settles
   them. Blocked steps go back to Sofia in the chat.
5. `her summary` writes the summary. With a card, the controller comments it
   on Kineloop.

## Run folder layout

Runs live in `~/.her/runs/<id>/` (or `$HER_HOME/runs/<id>/`):

```
request.md                # Original request
decisions.md              # Decisions settled with Sofia
plan.json                 # Pipeline plan
state.json                # Run and step state
steps/
  <step-id>.md            # Implementer report
  <step-id>.review.md     # Last review
  <step-id>.verdict.json  # Judge verdict
summary.md                # Final summary
```

## Commands

| Command | What it does |
|---|---|
| `her guide` | Skills, models, plan rules, the flow and the schema |
| `her new` | Create a run from stdin, print id and path |
| `her check <id>` | Validate `plan.json` and render it |
| `her approve <id>` | Record Sofia's approval |
| `her next <id>` | Ready and open steps as JSON |
| `her begin <id> <step> [--note]` | Pre-flight the step and print its brief |
| `her finish <id> <step> <STATUS>` | Store the implementer report from stdin |
| `her review-brief <id> <step>` | Print the reviewer brief |
| `her review <id> <step> approve\|changes` | Store the review from stdin |
| `her summary <id>` | Write `summary.md` |
| `her runs` | List all runs |
| `her status [id]` | Status of a run |
| `her show <id> <step>` | Report, review and verdict of a step |
| `her config` | Show the configuration |

## Tests

```bash
cd ~/HER/orchestrator && PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -t .
```

## Config

Override in `~/.her/config.toml`. Run `her config` to see the active values.
HER rule 6 maps tiers to models: bare model names on Claude Code, Cursor slugs
on Cursor.
