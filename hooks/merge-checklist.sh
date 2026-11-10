#!/bin/sh
# PostToolUse hook on Bash: after a command that merges into project/* or calls merge_requests/<iid>/merge,
# inject the mapping's "Tracker checklist" section. `sh merge-checklist.sh --check`.
# A `git merge` counts when the session's working directory is on a `project/*` branch afterwards.
# ponytail: a merge run in another directory (`cd x && git merge`, `git -C x merge`) or from a script is missed.
d=$(cd "$(dirname "$0")" && pwd)
inst=${HARNESS_INSTANCE:-$d/../INSTANCE.md}
if [ "${1:-}" = --check ]; then
  t=$(mktemp -d); export HARNESS_INSTANCE=$t/i.md
  printf '%s\n' '- Mapping read-gate: tracker tool pattern `x_*` (y); mapping file `'$t/m.md'`.' > "$HARNESS_INSTANCE"
  printf '%s\n' '# T' '## Tracker checklist at every merge' 'CHECKLIST-BODY' '## Other' 'no' > "$t/m.md"
  run() { jq -n --arg c "$1" '{tool_name:"Bash",tool_input:{command:$c}}' | sh "$0"; }
  git init -q -b project/x "$t/r"; git -C "$t/r" -c user.name=t -c user.email=t@t commit -q --allow-empty -m i
  run() { jq -n --arg c "$1" --arg d "$2" '{tool_name:"Bash",cwd:$d,tool_input:{command:$c}}' | sh "$0"; }
  run 'git merge dev-1 --no-ff' "$t/r" | grep -q CHECKLIST-BODY || { echo FAIL: merge on project branch not injected; exit 1; }
  git -C "$t/r" checkout -q -b dev-1
  run 'git merge origin/project/x' "$t/r" | grep -q . && { echo FAIL: merge into an issue branch injected; exit 1; }
  run 'curl -X PUT http://h/api/v4/projects/1/merge_requests/5/merge' "$t" | grep -q CHECKLIST-BODY || { echo FAIL: MR merge not injected; exit 1; }
  run 'glab mr merge 12' "$t" | grep -q CHECKLIST-BODY || { echo FAIL: glab merge not injected; exit 1; }
  git -C "$t/r" checkout -q project/x
  run 'git status' "$t/r" | grep -q . && { echo FAIL: injected on git status; exit 1; }
  run 'git merge dev-1 --no-ff' "$t/r" | grep -q 'no$' && { echo FAIL: next section leaked; exit 1; }
  rm -rf "$t"; echo ok; exit 0
fi
in=$(cat)
cmd=$(printf %s "$in" | jq -r '.tool_input.command // ""')
cwd=$(printf %s "$in" | jq -r '.cwd // "."')
case $cmd in
  *merge_requests/[0-9]*/merge*|*"glab mr merge"*) ;;
  *"git merge"*) case $(git -C "$cwd" rev-parse --abbrev-ref HEAD 2>/dev/null) in project/*) ;; *) exit 0;; esac ;;
  *) exit 0;;
esac
map=$(sed -n 's/.*mapping file `\([^`]*\)`.*/\1/p' "$inst" 2>/dev/null)
[ -r "$map" ] || exit 0
jq -n --arg c "$(awk '/^## Tracker checklist/{p=1} p&&/^## /&&!/^## Tracker checklist/{exit} p' "$map")" \
  '{hookSpecificOutput:{hookEventName:"PostToolUse",additionalContext:$c}}'
