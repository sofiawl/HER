import os
import tomllib
from dataclasses import dataclass, field
from pathlib import Path

HER_ROOT = Path(__file__).resolve().parents[2]
HOME_DIR = Path(os.environ.get("HER_HOME", Path.home() / ".her"))
RUNS_DIR = HOME_DIR / "runs"
CONFIG_FILE = HOME_DIR / "config.toml"

TIERS = ("haiku", "sonnet", "opus", "fable")

DEFAULT_MODELS = {
    "claude": {
        "haiku": ["claude-haiku-4-5-20251001"],
        "sonnet": ["claude-sonnet-5-5"],
        "opus": ["claude-opus-5-5"],
        "fable": ["claude-fable-5-1"],
    },
    "cursor": {
        "haiku": [
            "composer-2.5-fast",
            "gemini-3.8-flash-high",
            "grok-4.7-high-fast",
            "cursor-grok-4.6-high-fast",
        ],
        "sonnet": ["claude-sonnet-5-5-high", "gpt-5.6-sol-medium"],
        "opus": ["claude-opus-5-thinking-high", "claude-opus-5-5-medium"],
        "fable": ["claude-fable-5-1-thinking-high"],
    },
}

DEFAULT_MODEL_NOTES = {
    "claude/claude-haiku-4-5-20251001": {"strengths": "mechanical edits, grep, inventory, known commands", "relative_cost": 1},
    "claude/claude-sonnet-5-5": {"strengths": "code exploration, routine implementation, test runs", "relative_cost": 2},
    "claude/claude-opus-5-5": {"strengths": "multi-file design, long careful writing, synthesis", "relative_cost": 4},
    "claude/claude-fable-5-1": {"strengths": "risky decisions, final review, verdicts", "relative_cost": 5},
    "cursor/composer-2.5-fast": {"strengths": "fast mechanical edits inside a repo", "relative_cost": 1},
    "cursor/gemini-3.8-flash-high": {"strengths": "cheap reading, summaries, large context scans", "relative_cost": 1},
    "cursor/grok-4.7-high-fast": {"strengths": "quick mechanical chores, shell-heavy work", "relative_cost": 1},
    "cursor/cursor-grok-4.6-high-fast": {"strengths": "quick mechanical chores, shell-heavy work", "relative_cost": 1},
    "cursor/claude-sonnet-5-5-high": {"strengths": "code exploration, routine implementation", "relative_cost": 2},
    "cursor/gpt-5.6-sol-medium": {"strengths": "routine implementation, debugging, test fixes", "relative_cost": 2},
    "cursor/claude-opus-5-thinking-high": {"strengths": "deep multi-file design with extended thinking", "relative_cost": 4},
    "cursor/claude-opus-5-5-medium": {"strengths": "multi-file design, long writing", "relative_cost": 4},
    "cursor/claude-fable-5-1-thinking-high": {"strengths": "risky decisions, final review, verdicts", "relative_cost": 5},
}

CLAUDE_READ_TOOLS = [
    "Read", "Grep", "Glob", "WebFetch", "WebSearch",
    "Bash(git *)", "Bash(gh pr view *)", "Bash(gh pr list *)",
    "Bash(ls *)", "Bash(cat *)", "Bash(head *)", "Bash(tail *)", "Bash(wc *)",
    "Bash(find *)", "Bash(grep *)", "Bash(rg *)",
    "Bash(python3 *)", "Bash(python *)", "Bash(node *)",
    "Bash(npm *)", "Bash(npx *)", "Bash(yarn *)", "Bash(pnpm *)",
    "Bash(pytest *)", "Bash(her *)",
]

CLAUDE_WRITE_TOOLS = CLAUDE_READ_TOOLS + [
    "Edit", "Write", "NotebookEdit",
    "Bash(gh pr create *)", "Bash(gh pr edit *)", "Bash(gh api *)",
    "Bash(mkdir *)", "Bash(mv *)", "Bash(cp *)",
]

INTERACTIVE_SKILLS = {
    "ask-her",
    "grilling",
    "grill-me",
    "debate",
    "teach",
    "understand",
    "adhd",
    "caveman",
    "handoff",
    "her",
}


@dataclass
class Config:
    models: dict = field(default_factory=lambda: DEFAULT_MODELS)
    model_notes: dict = field(default_factory=lambda: DEFAULT_MODEL_NOTES)
    prefer_agents: list = field(default_factory=list)
    max_parallel: int = 3
    claude_bin: str = "claude"
    cursor_bin: str = "cursor-agent"
    claude_write_args: list = field(default_factory=lambda: ["--permission-mode", "acceptEdits"])
    claude_read_args: list = field(
        default_factory=lambda: ["--disallowedTools", "Edit", "Write", "NotebookEdit"]
    )
    claude_read_tools: list = field(default_factory=lambda: list(CLAUDE_READ_TOOLS))
    claude_write_tools: list = field(default_factory=lambda: list(CLAUDE_WRITE_TOOLS))
    cursor_write_args: list = field(default_factory=lambda: ["--force", "--trust"])
    cursor_read_args: list = field(default_factory=lambda: ["--mode", "ask", "--trust"])

    def agents(self):
        return list(self.models)

    def binary(self, agent):
        return getattr(self, f"{agent}_bin", agent)

    def allowed(self, agent, tier):
        return self.models.get(agent, {}).get(tier, [])

    def default_model(self, agent, tier):
        options = self.allowed(agent, tier)
        return options[0] if options else None

    def fallbacks(self, agent, tier):
        lower = list(reversed(TIERS[: TIERS.index(tier)])) if tier in TIERS else []
        candidates = [(other, self.default_model(other, tier)) for other in self.agents() if other != agent]
        candidates += [(agent, self.default_model(agent, below)) for below in lower]
        return [(name, model) for name, model in candidates if model]


def load_config():
    config = Config()
    if not CONFIG_FILE.exists():
        return config
    data = tomllib.loads(CONFIG_FILE.read_text())
    for key, value in data.items():
        if key == "models":
            merged = {agent: dict(tiers) for agent, tiers in config.models.items()}
            for agent, tiers in value.items():
                merged.setdefault(agent, {}).update(tiers)
            config.models = merged
        elif key == "model_notes":
            config.model_notes = {**config.model_notes, **value}
        elif hasattr(config, key):
            setattr(config, key, value)
    return config
