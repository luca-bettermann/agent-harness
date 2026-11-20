#!/bin/sh
# PreToolUse hook for Claude Code and Codex that enforces two AGENTS rules on shell commands (docs/adr/0010):
# no `kill` by pattern (pkill, killall, kill of a name or a substitution such as $(pgrep ...)), and no `git stash`
# without a pathspec (a bare stash takes other writers' edits). It reads the command's words, not its quoting: a
# quoted string that itself contains `; pkill` is refused too, which no real command needs.
# `sh command-guard.sh --check` runs the tests.
reason_kill='Never kill by pattern (AGENTS, Created resources): use `kill <PID you started>`, a literal number, never pkill, killall, a name or a $(pgrep ...) substitution.'
reason_stash='Never stash without a pathspec: a bare stash takes other writers'"'"' edits (AGENTS, Git). Use `git stash push -- <paths>`.'

# verdict <command>: prints kill, stash or nothing.
verdict() {
  printf '%s\n' "$1" | sed -e 's/\$(/ $SUBST\n/g; s/`/ $SUBST\n/g' -e 's/[0-9&]*>>*&[0-9-]*//g' -e 's/[0-9&]*>>*[^ ;|&]*//g' -e 's/&&/\n/g; s/||/\n/g; s/[;|&(){}`]/\n/g' | {
    set -f
    while IFS= read -r seg; do
      # shellcheck disable=SC2086
      set -- $(printf '%s' "$seg" | tr -d "\"'")
      # Skip variable assignments, `$`/`)` leftovers and wrappers before the command word.
      while [ $# -gt 0 ]; do
        case $1 in
          *=*|\$|\)|\}|sudo|env|command|nohup|time|exec|builtin|nice|setsid|timeout) shift;;
          *) break;;
        esac
      done
      [ $# -gt 0 ] || continue
      w=${1##*/}; shift
      case $w in
        pkill|killall) echo kill; exit;;
        xargs) for a in "$@"; do case ${a##*/} in kill|pkill|killall) echo kill; exit;; esac; done;;
        kill)
          while [ $# -gt 0 ]; do
            case $1 in
              -l|-L|-h|--help|--list|--table) break;;
              -s|-n|--signal) shift;;
              -[0-9]*|-[A-Z]*|--signal=*) :;;
              *[!0-9]*) echo kill; exit;;
            esac
            shift
          done;;
        git)
          while [ $# -gt 0 ]; do
            case $1 in
              -C|-c|--git-dir|--work-tree|--namespace) shift 2 || break;;
              -*) shift;;
              *) break;;
            esac
          done
          [ "${1:-}" = stash ] || continue
          shift
          case ${1:-} in
            ""|-*|push|save)
              [ "${1:-}" = push ] || [ "${1:-}" = save ] && shift
              # a pathspec is any word after `--`
              ps=false; seen=false
              for a in "$@"; do
                if $seen; then ps=true; break; fi
                [ "$a" = -- ] && seen=true
              done
              $ps || { echo stash; exit; };;
          esac;;
      esac
    done
  }
}

if [ "${1:-}" = --check ]; then
  me=$0
  fail() { echo "FAIL: $1"; exit 1; }
  run() { jq -nc --arg c "$1" '{hook_event_name: "PreToolUse", tool_name: "Bash", tool_input: {command: $c}}' | sh "$me"; }
  refused() { run "$1" | jq -e '.hookSpecificOutput | .permissionDecision == "deny" and (.permissionDecisionReason | contains($w))' --arg w "$2" >/dev/null; }
  for c in 'pkill -f foo' 'pkill node' 'killall node' 'kill $(pgrep -f foo)' 'kill `pgrep foo`' 'kill $PID' 'kill -9 $(pidof x)' \
    'kill 12 node' 'pgrep foo | xargs kill' 'pgrep foo | xargs -r kill -9' 'sudo pkill foo' 'cd /x && pkill foo' 'true; killall x' 'FOO=1 pkill x' '/usr/bin/pkill x'; do
    refused "$c" 'kill <PID you started>' || fail "kill allowed: $c"
  done
  for c in 'git stash' 'git stash push' 'git stash -u' 'git stash save wip' 'git stash push -m wip' 'git stash push -u' 'git stash push --' \
    'git -C /x stash' 'cd x && git stash' 'git stash --include-untracked' 'git stash push -m wip --'; do
    refused "$c" 'git stash push -- <paths>' || fail "stash allowed: $c"
  done
  for c in 'kill 1234' 'kill -9 1234' 'kill -TERM 12 34' 'kill -s TERM 1234' 'kill -l' 'kill 12 2>/dev/null' 'kill 12 2>&1' 'git stash push -- a b' \
    'git stash push -m wip -- a' 'git stash push -u -- a' 'git stash push --include-untracked -- a' 'git -C /x stash push -- a' 'git stash pop' 'git stash list' \
    'git stash show -p' 'git stash drop' 'git stash apply stash@{0}' 'git status' 'git commit -m "pkill is refused"' 'ls | grep kill' 'echo killall' 'pgrep -f foo' \
    'make kill' 'git log && kill 7'; do
    [ -z "$(run "$c")" ] || fail "refused: $c"
  done
  [ -z "$(printf '%s' '{"hook_event_name":"PostToolUse","tool_name":"Bash","tool_input":{"command":"pkill x"}}' | sh "$me")" ] || fail "acts outside PreToolUse"
  [ -z "$(printf '%s' '{"hook_event_name":"PreToolUse","tool_name":"Read","tool_input":{"file_path":"/x"}}' | sh "$me")" ] || fail "acts on a tool without a command"
  [ -z "$(printf '%s' 'not json' | sh "$me")" ] || fail "fails on bad input"
  echo ok; exit 0
fi

in=$(cat)
cmd=$(printf '%s' "$in" | jq -r 'select(.hook_event_name == "PreToolUse") | .tool_input.command // empty | if type == "array" then join(" ") else . end' 2>/dev/null) || exit 0
[ -n "$cmd" ] || exit 0
case $(verdict "$cmd") in
  kill) r=$reason_kill;;
  stash) r=$reason_stash;;
  *) exit 0;;
esac
jq -nc --arg r "$r" '{hookSpecificOutput: {hookEventName: "PreToolUse", permissionDecision: "deny", permissionDecisionReason: $r}}'
exit 0
