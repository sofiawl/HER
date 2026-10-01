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
    max_parallel: int = 3
    claude_bin: str = "claude"
    cursor_bin: str = "cursor-agent"
    claude_write_args: list = field(default_factory=lambda: ["--permission-mode", "acceptEdits"])
    claude_read_args: list = field(
        default_factory=lambda: ["--disallowedTools", "Edit", "Write", "NotebookEdit"]
    )
    cursor_write_args: list = field(default_factory=lambda: ["--force", "--trust"])
    cursor_read_args: list = field(default_factory=lambda: ["--mode", "ask", "--trust"])

    def agents(self):
        return list(self.models)

    def allowed(self, agent, tier):
        return self.models.get(agent, {}).get(tier, [])

    def default_model(self, agent, tier):
        options = self.allowed(agent, tier)
        return options[0] if options else None


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
        elif hasattr(config, key):
            setattr(config, key, value)
    return config
