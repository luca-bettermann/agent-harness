#!/bin/sh
# Hook for Claude Code and Codex that enforces the skill-loading rule from AGENTS (load-skills.sh only reminds):
# SessionStart after compaction or resume and SubagentStart mark the session or agent "skills pending"; while marked,
# PreToolUse denies every tool except the one that loads a skill; that tool's call clears the mark.
# Claude Code loads through the Skill tool. With --codex, a tool whose input contains SKILL.md loads a skill (Codex has
# no Skill tool: the model reads the file), and only SessionStart marks, because Codex's tool hooks carry no agent_id.
# `sh skill-gate.sh --check`. A mark is a file under a per-user temp folder, keyed by session_id and agent_id.
d=${TMPDIR:-/tmp}/agent-harness-skill-gate-$(id -u)
reason='Load every skill whose description matches the task before acting (AGENTS). A skill that is not loaded is not followed.'
if [ "${1:-}" = --check ]; then
  me=$0
  export TMPDIR=$(mktemp -d) || exit 1
  trap 'rm -rf "$TMPDIR"' EXIT
  run() { printf '%s' "$1" | sh "$me"; }
  denied() { run "$1" | jq -e '.hookSpecificOutput | .hookEventName == "PreToolUse" and .permissionDecision == "deny" and .permissionDecisionReason == $r' --arg r "$reason" >/dev/null; }
  fail() { echo "FAIL: $1"; exit 1; }
  m='{"session_id":"s1","hook_event_name":"SessionStart","source":"compact"}'
  bash='{"session_id":"s1","hook_event_name":"PreToolUse","tool_name":"Bash"}'
  skill='{"session_id":"s1","hook_event_name":"PreToolUse","tool_name":"Skill"}'
  done_='{"session_id":"s1","hook_event_name":"PostToolUse","tool_name":"Skill"}'
  [ -z "$(run "$bash")" ] || fail "Bash allowed before any mark"
  run "$m" >/dev/null
  denied "$bash" || fail "Bash after SessionStart"
  [ -z "$(run "$skill")" ] || fail "Skill denied while pending"
  [ -z "$(run '{"session_id":"s2","hook_event_name":"PreToolUse","tool_name":"Bash"}')" ] || fail "mark leaked to another session"
  run '{"session_id":"s1","hook_event_name":"PostToolUse","tool_name":"Bash"}' >/dev/null
  denied "$bash" || fail "a tool other than Skill cleared the mark"
  run "$done_" >/dev/null
  [ -z "$(run "$bash")" ] || fail "Bash after Skill"
  run '{"session_id":"s1","hook_event_name":"SubagentStart","agent_id":"a1","agent_type":"Explore"}' >/dev/null
  denied '{"session_id":"s1","hook_event_name":"PreToolUse","tool_name":"Read","agent_id":"a1"}' || fail "subagent tool after SubagentStart"
  [ -z "$(run "$bash")" ] || fail "subagent mark blocked the main session"
  run '{"session_id":"s1","hook_event_name":"PostToolUse","tool_name":"Skill","agent_id":"a1"}' >/dev/null
  [ -z "$(run '{"session_id":"s1","hook_event_name":"PreToolUse","tool_name":"Read","agent_id":"a1"}')" ] || fail "subagent tool after Skill"
  cx() { printf '%s' "$1" | sh "$me" --codex; }
  cm='{"session_id":"c1","hook_event_name":"SessionStart","source":"resume"}'
  cb='{"session_id":"c1","hook_event_name":"PreToolUse","tool_name":"Bash","tool_input":{"command":"ls"}}'
  cs='{"session_id":"c1","hook_event_name":"PreToolUse","tool_name":"Bash","tool_input":{"command":"cat /w/skills/engineering/SKILL.md"}}'
  [ -z "$(cx "$cb")" ] || fail "codex: Bash allowed before any mark"
  cx "$cm" >/dev/null
  cx "$cb" | jq -e '.hookSpecificOutput.permissionDecision == "deny"' >/dev/null || fail "codex: Bash after SessionStart"
  [ -z "$(cx "$cs")" ] || fail "codex: SKILL.md read denied while pending"
  [ -z "$(cx "$cb")" ] || fail "codex: Bash after the SKILL.md read"
  cx "$cm" >/dev/null
  cx '{"session_id":"c1","hook_event_name":"PostToolUse","tool_name":"Read","tool_input":{"path":"/w/skills/tdd/SKILL.md"}}' >/dev/null
  [ -z "$(cx "$cb")" ] || fail "codex: PostToolUse on SKILL.md did not clear"
  cx "$cm" >/dev/null
  [ -z "$(run "$cs")" ] && fail "claude: a SKILL.md path cleared the mark"
  echo ok; exit 0
fi
codex=false; [ "${1:-}" = --codex ] && codex=true
in=$(cat)
set -- $(printf '%s' "$in" | jq -r --argjson c "$codex" '[.hook_event_name, .tool_name // "-", .session_id, .agent_id // "main", ($c and ((.tool_input // "" | tostring) | contains("SKILL.md")) | tostring), (.tool_name == "Skill" | tostring)] | map(gsub("[^A-Za-z0-9_-]"; "_")) | .[]')
[ $# -eq 6 ] || exit 0
mark=$d/$3.$4
load=false; { [ "$5" = true ] || [ "$6" = true ]; } && load=true
case $1 in
  SessionStart|SubagentStart) mkdir -p "$d" && chmod 700 "$d" && : > "$mark";;
  PreToolUse) if $load; then [ "$5" != true ] || rm -f "$mark"; elif [ -e "$mark" ]; then jq -nc --arg r "$reason" '{hookSpecificOutput: {hookEventName: "PreToolUse", permissionDecision: "deny", permissionDecisionReason: $r}}'; fi;;
  PostToolUse) ! $load || rm -f "$mark";;
esac
exit 0
