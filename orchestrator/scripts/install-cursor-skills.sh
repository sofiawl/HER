#!/bin/bash
set -euo pipefail

HER_SKILLS_DIR="/home/sofia/HER/skills"
CURSOR_SKILLS_DIR="${HOME}/.cursor/skills"
LINK_MARKER=".her-installed"

if [[ "${1:-}" == "--uninstall" ]]; then
  if [[ ! -d "$CURSOR_SKILLS_DIR" ]]; then
    exit 0
  fi

  while IFS= read -r link_path; do
    if [[ -L "$link_path" ]]; then
      rm "$link_path"
    fi
  done < <(find "$CURSOR_SKILLS_DIR" -maxdepth 1 -name "her-*" -type l 2>/dev/null || true)

  if [[ -f "$CURSOR_SKILLS_DIR/$LINK_MARKER" ]]; then
    rm "$CURSOR_SKILLS_DIR/$LINK_MARKER"
  fi

  exit 0
fi

mkdir -p "$CURSOR_SKILLS_DIR"

for skill_dir in "$HER_SKILLS_DIR"/*/; do
  if [[ ! -f "$skill_dir/SKILL.md" ]]; then
    continue
  fi

  skill_name=$(basename "$skill_dir")
  link_name="her-$skill_name"
  link_path="$CURSOR_SKILLS_DIR/$link_name"

  if [[ -L "$link_path" ]]; then
    target=$(readlink "$link_path")
    if [[ "$target" == "$skill_dir" ]]; then
      continue
    fi
    rm "$link_path"
  elif [[ -e "$link_path" ]]; then
    rm "$link_path"
  fi

  ln -s "$skill_dir" "$link_path"
done

touch "$CURSOR_SKILLS_DIR/$LINK_MARKER"
