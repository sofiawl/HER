#!/usr/bin/env bash
set -u

threshold="${HER_HANDOFF_THRESHOLD:-75}"
window="${HER_CONTEXT_WINDOW:-1000000}"
stamp_dir="${TMPDIR:-/tmp}"

command -v jq >/dev/null 2>&1 || exit 0

input=$(cat)
session_id=$(printf '%s' "$input" | jq -r '.session_id // empty')
transcript=$(printf '%s' "$input" | jq -r '.transcript_path // empty')

[ -n "$session_id" ] || exit 0
[ -r "$transcript" ] || exit 0

stamp="$stamp_dir/her-handoff-nudge-$session_id"
[ -e "$stamp" ] && exit 0

used=$(tail -n 200 "$transcript" \
  | jq -R 'fromjson? | select(.type == "assistant" and (.isSidechain | not) and .message.usage != null) | .message.usage | (.input_tokens // 0) + (.cache_creation_input_tokens // 0) + (.cache_read_input_tokens // 0)' 2>/dev/null \
  | tail -n 1)

[ -n "$used" ] || exit 0

pct=$((used * 100 / window))
[ "$pct" -ge "$threshold" ] || exit 0

: > "$stamp"

jq -n --arg pct "$pct" '{
  systemMessage: ("Context is about " + $pct + "% full. Run /her:handoff before the native compact to save a resumable handoff doc."),
  hookSpecificOutput: {
    hookEventName: "UserPromptSubmit",
    additionalContext: ("Context is about " + $pct + "% full. Tell Sofia once, briefly, to run /her:handoff before the native compact. Do not run the handoff yourself unless she asks.")
  }
}'
