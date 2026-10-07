#!/usr/bin/env bash
# Nudge Sofia once to run /her:handoff when either the context window or a
# usage limit window is close to full. Usage limits come from a cache the
# status line writes, because hooks never receive rate_limits.
set -u

context_threshold="${HER_HANDOFF_THRESHOLD:-75}"
limit_threshold="${HER_LIMIT_THRESHOLD:-85}"
window="${HER_CONTEXT_WINDOW:-1000000}"
stamp_dir="${TMPDIR:-/tmp}"
limits_file="$stamp_dir/her-rate-limits.json"

command -v jq >/dev/null 2>&1 || exit 0

input=$(cat)
session_id=$(printf '%s' "$input" | jq -r '.session_id // empty')
transcript=$(printf '%s' "$input" | jq -r '.transcript_path // empty')

reason=""

# Usage limit: one nudge per limit window, across all sessions.
if [ -r "$limits_file" ]; then
  now=$(date +%s)
  hit=$(jq -r --argjson t "$limit_threshold" --argjson now "$now" '
    [ to_entries[]
      | select(.key == "five_hour" or .key == "seven_day")
      | select(.value.used_percentage != null and .value.resets_at != null)
      | select(.value.resets_at > $now and .value.used_percentage >= $t)
      | "\(.key) \(.value.used_percentage | floor) \(.value.resets_at)" ]
    | first // empty' "$limits_file" 2>/dev/null)
  if [ -n "$hit" ]; then
    read -r name pct resets <<<"$hit"
    stamp="$stamp_dir/her-handoff-limit-$name-$resets"
    if [ ! -e "$stamp" ]; then
      : > "$stamp"
      label="5-hour"
      [ "$name" = "seven_day" ] && label="7-day"
      reason="Your $label usage limit is about $pct% used (resets $(date -d "@$resets" +%H:%M 2>/dev/null || echo soon))."
    fi
  fi
fi

# Context window: one nudge per session.
if [ -z "$reason" ] && [ -n "$session_id" ] && [ -r "$transcript" ]; then
  stamp="$stamp_dir/her-handoff-nudge-$session_id"
  if [ ! -e "$stamp" ]; then
    used=$(tail -n 200 "$transcript" \
      | jq -R 'fromjson? | select(.type == "assistant" and (.isSidechain | not) and .message.usage != null) | .message.usage | (.input_tokens // 0) + (.cache_creation_input_tokens // 0) + (.cache_read_input_tokens // 0)' 2>/dev/null \
      | tail -n 1)
    if [ -n "$used" ]; then
      pct=$((used * 100 / window))
      if [ "$pct" -ge "$context_threshold" ]; then
        : > "$stamp"
        reason="Context is about $pct% full."
      fi
    fi
  fi
fi

[ -n "$reason" ] || exit 0

jq -n --arg r "$reason" '{
  systemMessage: ($r + " Run /her:handoff to save this thread (ai-memory gets session end if wired)."),
  hookSpecificOutput: {
    hookEventName: "UserPromptSubmit",
    additionalContext: ($r + " Tell Sofia once, briefly, to run /her:handoff now for HER-shaped state (next action + /her: skills). ai-memory hooks cover durable project memory on session end; do not run handoff yourself unless she asks.")
  }
}'
