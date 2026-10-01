import stat
from pathlib import Path

FAKE_CLAUDE = """#!/usr/bin/env python3
import json, sys
args = sys.argv[1:]
prompt = args[args.index("-p") + 1]
resumed = "--resume" in args
sid = "sess-" + prompt.split("`")[1] if "`" in prompt else "sess-x"
print(json.dumps({"type": "system", "subtype": "init", "session_id": sid}))
ask = "step `ask`" in prompt and not resumed and "Earlier question" not in prompt
text = "work\\nQUESTION: which option, A or B?" if ask else "all good, no question here"
print(json.dumps({"type": "result", "subtype": "success", "is_error": False, "result": text, "session_id": sid, "permission_denials": [], "argv": args}))
"""


def fake_claude(directory):
    path = Path(directory) / "fake-claude"
    path.write_text(FAKE_CLAUDE)
    path.chmod(path.stat().st_mode | stat.S_IEXEC)
    return str(path)


def step(sid, depends_on=(), cwd="/tmp"):
    return {
        "id": sid, "title": sid, "skill": None, "agent": "claude", "model": "m",
        "writes": False, "depends_on": list(depends_on), "cwd": cwd, "add_dirs": [], "task": "do " + sid,
    }


def make_run(directory, steps, state_steps=None):
    from her.run import Run

    run = Run(Path(directory) / "run-1")
    (run.path / "steps").mkdir(parents=True)
    run.save_plan({"summary": "goal", "steps": steps, "repos": []})
    run.save_state({"phase": "approved", "approved": True, "steps": state_steps or {}})
    return run
