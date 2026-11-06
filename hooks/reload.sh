#!/bin/sh
# SessionStart hook (compact, resume): re-inject AGENTS and INSTANCE, and ask for the skills in use.
h=$(dirname "$0")/..
cat "$h/AGENTS.md"
i=$(cat "$h/instance-path" 2>/dev/null) && [ -f "$i" ] && { echo; cat "$i"; }
echo
echo "Before continuing, reload with the Skill tool every skill you were following before this compaction or resume."
