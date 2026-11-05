#!/bin/sh
# SessionStart hook (compact, resume): re-inject AGENTS and ask for the skills in use.
cat "$(dirname "$0")/../AGENTS.md"
echo
echo "Before continuing, reload with the Skill tool every skill you were following before this compaction or resume."
