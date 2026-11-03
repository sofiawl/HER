import argparse
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

SKIP_PREFIXES = ("<", "Base directory", "Another Claude session", "[Request interrupted", "This session is being continued")


def text_of(content):
    if isinstance(content, list):
        content = " ".join(p.get("text", "") for p in content if isinstance(p, dict) and p.get("type") == "text")
    return content if isinstance(content, str) else ""


def claude_sessions(since, until, width):
    root = Path.home() / ".claude" / "projects"
    for path in sorted(root.glob("*/*.jsonl")):
        stamps, messages = [], []
        for line in path.open(errors="ignore"):
            try:
                row = json.loads(line)
            except ValueError:
                continue
            if row.get("type") != "user" or row.get("isMeta") or row.get("toolUseResult") is not None:
                continue
            stamp = row.get("timestamp", "")[:16]
            if not (since <= stamp[:10] <= until):
                continue
            text = text_of(row.get("message", {}).get("content")).strip()
            if not text or text.startswith(SKIP_PREFIXES):
                continue
            stamps.append(stamp)
            messages.append(f"  {stamp[5:]} {text[:width]}".replace("\n", " "))
        if messages:
            print(f"### {path.parent.name} / {path.stem[:8]}: {len(messages)} messages, {stamps[0]} to {stamps[-1]}")
            print("\n".join(messages))
            print()


def git_commits(since, until, author):
    candidates = sorted(Path.home().glob("kinebot-*")) + [Path.home() / "HER"]
    seen = set()
    for repo in candidates:
        if not (repo / ".git").exists():
            continue
        common = subprocess.run(
            ["git", "-C", str(repo), "rev-parse", "--path-format=absolute", "--git-common-dir"],
            capture_output=True, text=True,
        ).stdout.strip()
        if common in seen:
            continue
        seen.add(common)
        out = subprocess.run(
            ["git", "-C", str(repo), "log", "--branches", "--remotes", f"--since={since}",
             f"--author={author}", "--format=%as|%s"],
            capture_output=True, text=True,
        ).stdout.strip()
        if out:
            subjects = {}
            for line in out.splitlines():
                day, subject = line.split("|", 1)
                if since <= day <= until:
                    subjects.setdefault(subject, day[5:])
            if not subjects:
                continue
            print(f"### {repo.name}: {len(subjects)} distinct commit subjects")
            for subject, day in sorted(subjects.items(), key=lambda kv: kv[1]):
                print(f"  {day} {subject[:150]}")
            print()


def cursor_transcripts(since, until):
    root = Path.home() / ".cursor" / "projects"
    found = []
    for path in root.glob("*/agent-transcripts/**/*.jsonl"):
        if "subagents" in path.parts:
            continue
        day = datetime.fromtimestamp(path.stat().st_mtime).strftime("%Y-%m-%d")
        if since <= day <= until:
            found.append((day, path))
    for day, path in sorted(found):
        print(f"  {day} {path}")
    print(f"\n{len(found)} cursor transcripts")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--since", required=True)
    parser.add_argument("--until", default=datetime.now().strftime("%Y-%m-%d"))
    parser.add_argument("--author", default="Sofia")
    parser.add_argument("--width", type=int, default=160)
    args = parser.parse_args()
    print(f"# Window {args.since} to {args.until}\n")
    print("## Claude Code sessions (user messages)\n")
    claude_sessions(args.since, args.until, args.width)
    print("## Git commits\n")
    git_commits(args.since, args.until, args.author)
    print("## Cursor transcripts (summarize with a subagent)\n")
    cursor_transcripts(args.since, args.until)


if __name__ == "__main__":
    sys.exit(main())
