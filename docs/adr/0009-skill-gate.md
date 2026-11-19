# The skill gate refuses tools until a skill is loaded, in both clients

After a compaction an agent ignored the reminder from `load-skills.sh` and worked without its skills (DEV-624, Luca 2026-11-19: "we need a hook for this"). `skill-gate.sh` turns the rule into a refusal: SessionStart (compact or resume) and SubagentStart mark the session or agent "skills pending", PreToolUse denies every tool except the one that loads a skill while the mark exists, and that load clears the mark. The mark is a file under a per-user temp folder, keyed by `session_id` and, inside a subagent, `agent_id`. The reminder stays as it is.

## Claude Code

Primary source: [hooks reference](https://code.claude.com/docs/en/hooks), checked 2026-11-19 against Claude Code 2.1.326.

- A skill loads through the `Skill` tool; PostToolUse on `Skill` clears the mark.
- Hooks from settings run inside subagents: PreToolUse and PostToolUse fire there with the same configuration, and the input adds `agent_id` and `agent_type`. The input's `session_id` is the main session's, so a subagent's mark needs `agent_id` in its key.
- SubagentStart also fires when a subagent is resumed, so a resumed subagent loads its skills again.
- A skill typed as `/name` bypasses PreToolUse and PostToolUse, so it clears nothing; the agent still calls the `Skill` tool to proceed.

## Codex

Primary sources: [hooks page](https://developers.openai.com/codex/hooks) and `codex-cli 0.169.0`.

- Codex has no `Skill` tool and no skill-load event; the model loads a skill by reading its `SKILL.md`. PreToolUse and PostToolUse carry `tool_input` (`tool_input.command` for shell, the arguments for other function tools), so the gate treats a call whose input contains `SKILL.md` as the load: it allows that call and clears the mark. Run with `--codex`, which turns this rule on.
- Codex's PreToolUse and PostToolUse documentation lists no `agent_id`, and subagent hooks report the parent's `session_id`. A mark made at SubagentStart could not be matched to the subagent's tool calls and would block the parent instead. Codex therefore gates SessionStart (compact or resume) only; its subagents keep the reminder.
- The docs call tool hooks "a useful guardrail, not a complete enforcement boundary": a `SKILL.md` mention inside an unrelated command also clears the mark, and hosted tools do not reach the hooks.
