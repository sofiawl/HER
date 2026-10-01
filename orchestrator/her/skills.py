import re

from .config import HER_ROOT, INTERACTIVE_SKILLS


def _frontmatter(text):
    match = re.match(r"^---\n(.*?)\n---", text, re.S)
    return match.group(1) if match else ""


def _description(front):
    match = re.search(r"^description:\s*(>-?|\|)?\s*(.*?)(?=^\S[\w-]*:|\Z)", front, re.S | re.M)
    if not match:
        return ""
    return " ".join(match.group(2).split())


def catalog():
    skills = {}
    for path in sorted((HER_ROOT / "skills").glob("*/SKILL.md")):
        front = _frontmatter(path.read_text())
        skills[path.parent.name] = {
            "description": _description(front),
            "interactive": path.parent.name in INTERACTIVE_SKILLS,
            "path": str(path),
        }
    return skills


def catalog_text(skills):
    lines = []
    for name, info in skills.items():
        tag = " [interactive: never a step]" if info["interactive"] else ""
        lines.append(f"- {name}{tag}: {info['description']}")
    return "\n".join(lines)
