#!/bin/sh
# Hook for Claude Code and Codex on prompt submit, subagent start, and session start after compaction or resume:
# repeats the skill-loading rule from AGENTS, its one home. `sh load-skills.sh --check`.
a=$(dirname "$0")/../AGENTS.md
if [ "${1:-}" = --check ]; then
  for e in SubagentStart UserPromptSubmit SessionStart; do
    printf '{"hook_event_name":"%s"}' "$e" | sh "$0" | jq -e --arg e "$e" '.hookSpecificOutput | .hookEventName == $e and (.additionalContext | startswith("Before acting"))' >/dev/null || { echo "FAIL: $e"; exit 1; }
  done
  echo ok; exit 0
fi
jq -c --arg r "$(grep -o 'Before acting, [^.]*\.' "$a")" '{hookSpecificOutput: {hookEventName: (.hook_event_name // "UserPromptSubmit"), additionalContext: ($r + " A skill that is not loaded is not followed.")}}'
