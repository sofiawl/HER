import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from her.agents import result_info
from her.config import Config
from her.run import DONE, FAILED, Executor, candidates, fast_failure
from tests.fakes import make_run, step

FIXTURES = Path(__file__).parent / "fixtures"

MODELS = {
    "claude": {"haiku": ["c-haiku"], "sonnet": ["c-sonnet"], "opus": ["c-opus"], "fable": []},
    "cursor": {"haiku": [], "sonnet": ["x-sonnet", "x-other"], "opus": [], "fable": []},
}

FAKE_AGENT = """
import json, sys
model = sys.argv[1]
behavior = json.loads(sys.argv[2]).get(model, "ok")
if behavior == "crash":
    print("model not available")
    sys.exit(1)
if behavior == "error":
    print(json.dumps({"type": "result", "subtype": "error_during_execution", "is_error": True, "result": "API error"}))
    sys.exit(0)
if behavior == "denied":
    print(json.dumps({"type": "assistant", "message": {"content": [{"type": "text", "text": "tried"}]}}))
    print(json.dumps({"type": "result", "subtype": "success", "result": "tried", "permission_denials": [{"tool_name": "Bash"}]}))
    sys.exit(0)
print(json.dumps({"type": "assistant", "message": {"content": [{"type": "text", "text": "done on " + model}]}}))
print(json.dumps({"type": "result", "subtype": "success", "result": "done on " + model}))
"""


def sonnet_step(**extra):
    return dict(step("work"), agent="claude", tier="sonnet", model="c-sonnet", **extra)


def run_with(directory, behaviors, **extra):
    run = make_run(directory, [sonnet_step(**extra)])
    said = []

    def fake_command(config, agent, prompt, model, cwd, add_dirs, writes, resume=None):
        return [sys.executable, "-c", FAKE_AGENT, model, json.dumps(behaviors)]

    with mock.patch("her.run.build_command", fake_command):
        Executor(Config(models=MODELS), run, out=lambda text, **k: said.append(text)).execute()
    return run, said


class CandidatesTest(unittest.TestCase):
    def test_same_tier_other_agent_then_one_tier_down(self):
        chain = candidates(Config(models=MODELS), sonnet_step())
        self.assertEqual(chain, [("claude", "c-sonnet"), ("cursor", "x-sonnet"), ("claude", "c-haiku")])

    def test_fallback_models_override_order(self):
        chain = candidates(Config(models=MODELS), sonnet_step(fallback_models=["claude/c-opus", "cursor/x-other"]))
        self.assertEqual(chain, [("claude", "c-sonnet"), ("claude", "c-opus"), ("cursor", "x-other")])

    def test_capped_at_three_attempts(self):
        entries = ["claude/a", "claude/b", "claude/c", "claude/d"]
        self.assertEqual(len(candidates(Config(models=MODELS), sonnet_step(fallback_models=entries))), 3)


class FastFailureTest(unittest.TestCase):
    def test_judge_fixture_with_text_is_not_fast(self):
        info = result_info(FIXTURES / "judge.jsonl")
        self.assertTrue(info["has_text"])
        self.assertFalse(fast_failure(FAILED, 5, info))

    def test_done_is_never_fast(self):
        self.assertFalse(fast_failure(DONE, 1, {"has_text": False, "is_error": False, "subtype": None, "tool_uses": 0}))

    def test_error_subtype_without_tool_use_is_fast_even_when_slow(self):
        info = {"has_text": True, "is_error": False, "subtype": "error_max_turns", "tool_uses": 0}
        self.assertTrue(fast_failure(FAILED, 120, info))
        self.assertFalse(fast_failure(FAILED, 120, dict(info, tool_uses=2)))


class FallbackExecutionTest(unittest.TestCase):
    def test_retries_down_the_chain_until_success(self):
        with tempfile.TemporaryDirectory() as directory:
            run, said = run_with(directory, {"c-sonnet": "crash", "x-sonnet": "error"})
            state = run.state()["steps"]["work"]
            self.assertEqual(state["status"], DONE)
            self.assertEqual([(a["agent"], a["model"]) for a in state["attempts"]],
                             [("claude", "c-sonnet"), ("cursor", "x-sonnet"), ("claude", "c-haiku")])
            self.assertEqual(state["attempts"][0]["reason"], "exit code 1")
            retries = [line for line in said if "retry  work on" in line]
            self.assertEqual(len(retries), 2)
            self.assertIn("retry  work on cursor/x-sonnet (exit code 1)", retries[0])
            self.assertEqual(run.step_output("work").read_text(), "done on c-haiku")
            self.assertTrue(run.step_log("work").with_name("work.attempt1.jsonl").exists())

    def test_gives_up_after_three_attempts(self):
        with tempfile.TemporaryDirectory() as directory:
            run, _ = run_with(directory, {"c-sonnet": "crash", "x-sonnet": "crash", "c-haiku": "crash"})
            state = run.state()["steps"]["work"]
            self.assertEqual(state["status"], FAILED)
            self.assertEqual(len(state["attempts"]), 3)

    def test_denied_step_with_text_is_not_retried(self):
        with tempfile.TemporaryDirectory() as directory:
            run, said = run_with(directory, {"c-sonnet": "denied"})
            state = run.state()["steps"]["work"]
            self.assertEqual(state["status"], FAILED)
            self.assertEqual(len(state["attempts"]), 1)
            self.assertFalse(any("retry" in line for line in said))


if __name__ == "__main__":
    unittest.main()
