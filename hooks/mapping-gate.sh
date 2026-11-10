#!/bin/sh
# PreToolUse hook: a call to a tool matching the installation's tracker pattern is refused until the session has read
# the mapping file (PostToolUse on Read records it). SessionEnd removes the state. `sh mapping-gate.sh --check`.
# Pattern and file: INSTANCE "Mapping read-gate: tracker tool pattern `P` ...; mapping file `F`".
d=$(cd "$(dirname "$0")" && pwd)
inst=${HARNESS_INSTANCE:-$d/../INSTANCE.md}
if [ "${1:-}" = --check ]; then
  t=$(mktemp -d); export TMPDIR=$t HARNESS_INSTANCE=$t/i.md
  echo '- Mapping read-gate: tracker tool pattern `mcp__trk__save_*` (x); mapping file `/m.md`.' > "$HARNESS_INSTANCE"
  run() { printf '{"session_id":"s1","hook_event_name":"%s","tool_name":"%s"}' "$1" "$2" | sh "$0" 2>/dev/null; }
  run PreToolUse mcp__trk__save_issue && { echo FAIL: first call passed; exit 1; }
  run PreToolUse mcp__trk__save_issue && { echo FAIL: retry without read passed; exit 1; }
  printf '{"session_id":"s1","hook_event_name":"PostToolUse","tool_name":"Read","tool_input":{"file_path":"/m.md"}}' | sh "$0"
  run PreToolUse mcp__trk__save_issue || { echo FAIL: call after read refused; exit 1; }
  run PreToolUse Bash || { echo FAIL: other tool refused; exit 1; }
  run SessionEnd ""; run PreToolUse mcp__trk__save_issue && { echo FAIL: state not removed; exit 1; }
  rm -rf "$t"; echo ok; exit 0
fi
in=$(cat)
sid=$(printf %s "$in" | jq -r '.session_id | gsub("[^A-Za-z0-9_-]"; "")')
state=${TMPDIR:-/tmp}/agent-harness-gate-$sid
[ "$(printf %s "$in" | jq -r .hook_event_name)" = SessionEnd ] && { rm -f "$state"; exit 0; }
pat=$(sed -n 's/^- Mapping read-gate: tracker tool pattern `\([^`]*\)`.*/\1/p' "$inst" 2>/dev/null)
map=$(sed -n 's/.*mapping file `\([^`]*\)`.*/\1/p' "$inst" 2>/dev/null)
[ -n "$pat" ] || exit 0
tool=$(printf %s "$in" | jq -r .tool_name)
if [ "$tool" = Read ]; then
  [ "$(printf %s "$in" | jq -r '.tool_input.file_path // ""')" = "$map" ] && : > "$state"
  exit 0
fi
case $tool in $pat) ;; *) exit 0;; esac
[ -e "$state" ] && exit 0
echo "Read $map first (with the Read tool), then repeat the call." >&2
exit 2
