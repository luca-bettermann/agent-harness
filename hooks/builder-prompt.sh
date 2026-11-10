#!/bin/sh
# PreToolUse hook on Agent: a `builder` subagent's prompt is exactly `Implement <ISSUE-ID>.`; other types pass.
# `sh builder-prompt.sh --check`.
if [ "${1:-}" = --check ]; then
  run() { printf '{"tool_name":"Agent","tool_input":{"subagent_type":"%s","prompt":"%s"}}' "$1" "$2" | sh "$0" 2>/dev/null; }
  run builder "Implement DEV-276. Also do X" && { echo FAIL: long prompt passed; exit 1; }
  run builder "Implement DEV-276." || { echo FAIL: exact prompt refused; exit 1; }
  run builder "Implement #42." || { echo FAIL: tracker-neutral ref refused; exit 1; }
  run general-purpose "anything" || { echo FAIL: other type refused; exit 1; }
  echo ok; exit 0
fi
in=$(cat)
[ "$(printf %s "$in" | jq -r '.tool_input.subagent_type // ""')" = builder ] || exit 0
printf %s "$in" | jq -e '.tool_input.prompt | test("^Implement [^ ]+\\.$")' >/dev/null && exit 0
echo "Put run-specific instructions on the issue. A builder's prompt is exactly: Implement <ISSUE-ID>." >&2
exit 2
