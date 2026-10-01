import unittest

from her import watch


def plan_step(sid, depends_on=()):
    return {"id": sid, "skill": None, "agent": "claude", "model": "m", "cwd": "/tmp", "depends_on": list(depends_on)}


class BlockedBoardTest(unittest.TestCase):
    plan = {"summary": "goal", "steps": [plan_step("ask"), plan_step("after", ["ask"])]}
    question = "which of the two long options should the executor pick for the branch name, A or B?"
    state = {"phase": "needs-answer", "steps": {"ask": {"status": "blocked", "question": question, "seconds": 3}}}

    def test_shows_needs_answer_question_and_hint(self):
        rows = watch.render(self.plan, self.state, 0, 60, 30, [])
        text = "\n".join(row for row, _ in rows)
        self.assertIn("needs answer ask", text)
        flat = " ".join(text.split())
        self.assertIn("ask needs answer: which of the two long options", flat)
        self.assertIn("pick for the branch name, A or B?", flat)
        self.assertIn('her answer ask "..."', text)
        self.assertTrue(any(style == "blocked" for _, style in rows))

    def test_no_foot_without_blocked_steps(self):
        state = {"phase": "running", "steps": {"ask": {"status": "done"}}}
        text = "\n".join(row for row, _ in watch.render(self.plan, state, 0, 60, 30, []))
        self.assertNotIn("her answer", text)


if __name__ == "__main__":
    unittest.main()
