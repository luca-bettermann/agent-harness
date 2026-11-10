#!/bin/sh
# PostToolUse hook on Bash: after a command that merges into project/* or calls merge_requests/<iid>/merge,
# inject the mapping's "Tracker checklist" section. `sh merge-checklist.sh --check`.
# ponytail: textual match (`git merge` plus `project/` in the command); a merge from a script or after a bare cd is missed.
d=$(cd "$(dirname "$0")" && pwd)
inst=${HARNESS_INSTANCE:-$d/../INSTANCE.md}
if [ "${1:-}" = --check ]; then
  t=$(mktemp -d); export HARNESS_INSTANCE=$t/i.md
  printf '%s\n' '- Mapping read-gate: tracker tool pattern `x_*` (y); mapping file `'$t/m.md'`.' > "$HARNESS_INSTANCE"
  printf '%s\n' '# T' '## Tracker checklist at every merge' 'CHECKLIST-BODY' '## Other' 'no' > "$t/m.md"
  run() { jq -n --arg c "$1" '{tool_name:"Bash",tool_input:{command:$c}}' | sh "$0"; }
  run 'git merge dev-1 --no-ff # into project/x' | grep -q CHECKLIST-BODY || { echo FAIL: merge not injected; exit 1; }
  run 'curl -X PUT http://h/api/v4/projects/1/merge_requests/5/merge' | grep -q CHECKLIST-BODY || { echo FAIL: MR merge not injected; exit 1; }
  run 'git status' | grep -q . && { echo FAIL: injected on git status; exit 1; }
  run 'git merge dev-1 --no-ff # into project/x' | grep -q 'no$' && { echo FAIL: next section leaked; exit 1; }
  rm -rf "$t"; echo ok; exit 0
fi
cmd=$(jq -r '.tool_input.command // ""')
case $cmd in
  *merge_requests/[0-9]*/merge*) ;;
  *"git merge"*project/*|*project/*"git merge"*) ;;
  *) exit 0;;
esac
map=$(sed -n 's/.*mapping file `\([^`]*\)`.*/\1/p' "$inst" 2>/dev/null)
[ -r "$map" ] || exit 0
jq -n --arg c "$(awk '/^## Tracker checklist/{p=1} p&&/^## /&&!/^## Tracker checklist/{exit} p' "$map")" \
  '{hookSpecificOutput:{hookEventName:"PostToolUse",additionalContext:$c}}'
