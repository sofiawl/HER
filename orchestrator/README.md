# HER Orchestrator

Multi-agent pipelines driven from a chat. The `her` CLI is for the agent, not
for Sofia.

## Install

```bash
uv tool install -e ~/HER/orchestrator
```

For Cursor, install the skill as `her-her`:

```bash
~/HER/orchestrator/scripts/install-cursor-skills.sh
```

## How it is used

Sofia types `/her <what to do>` in Claude Code (skill `her:her`) or in
cursor-agent (skill `her-her`). The chat agent does the rest.

1. `her new` creates the run from the request (stdin heredoc).
2. `her guide` gives the agent the skill catalog and plan rules.
3. The agent reads the repos and grills Sofia in the chat, then writes
   `decisions.md`.
4. The agent writes `plan.json` and runs `her check` until it passes, then
   shows Sofia the plan and the missing skills.
5. After approval `her start` runs the steps detached and opens a live
   dashboard in a new Ghostty window.

## Dashboard keys

- `[up/down]` pick a step
- `[enter]` full log of the step
- `[q]` close the dashboard, the run continues

## Run folder layout

Runs live in `~/.her/runs/<id>/`:

```
request.md          # Original request
decisions.md        # Decisions settled with Sofia
plan.json           # Pipeline plan
state.json          # Run state
executor.log        # Executor output
steps/
  <step-id>.jsonl   # Log events from the step agent
  <step-id>.md      # Step result
summary.md          # Final summary
```

## Commands

| Command | What it does |
|---|---|
| `her` | Banner and recent runs |
| `her guide` | Skill catalog, allowed agents, tiers, models, plan rules and schema |
| `her new` | Create a run from stdin, print id and path |
| `her check <id>` | Validate `plan.json` and render it |
| `her start <id>` | Start the run detached and open the dashboard |
| `her exec <id>` | Internal: the detached executor |
| `her watch <id>` | Reopen the dashboard |
| `her stop <id>` | Stop a running run |
| `her runs` | List all runs |
| `her status [id]` | Status of a run |
| `her show <id> <step>` | Result of a step |
| `her logs <id> <step>` | Log of a step |
| `her config` | Show the configuration |

## Config

Override in `~/.her/config.toml`. Run `her config` to see the active values.
HER rule 6 maps tiers to models: bare model names on Claude Code, Cursor slugs
on Cursor.
