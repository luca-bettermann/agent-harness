# Install details

Everything is written under the workspace root; a root that contains `$HOME` is refused. The one exception: Codex accepts project trust only from the account's own config, so the installer adds `[projects."<root>"] trust_level = "trusted"` to `${CODEX_HOME:-~/.codex}/config.toml` when Codex is installed and the root has no entry yet. Accounts may be shared: a session outside the root gets nothing from the harness.

| Written under the root | For |
| --- | --- |
| `.agent-harness/` | AGENTS, the skills with addenda appended, the knowledge schema, hooks, launcher and a link to INSTANCE; each `docs/agents/*.md` next to INSTANCE that has skill frontmatter is linked in as a skill |
| `CLAUDE.md` | AGENTS in full, read by Claude Code from the root and every directory below it, nested repositories and worktrees included |
| `CLAUDE.local.md` | link to INSTANCE, read the same way |
| `AGENTS.md` | AGENTS plus a pointer to INSTANCE, for Codex |
| `.claude/skills/`, `.agents/skills/` | links to the skills, for Claude Code and Codex |
| `.claude/settings.json`, `.codex/hooks.json` | the `load-skills.sh` hook for Claude Code and Codex on `UserPromptSubmit`, `SubagentStart` and `SessionStart` after compaction or resume (AGENTS and INSTANCE come back by themselves). Earlier entries pointing into `.agent-harness/hooks/` are replaced; other settings stay. Codex runs them once the account has reviewed them: the first Codex session below the root asks once ("Trust all and continue"). |

An entry file it didn't write, or one edited since, is moved aside as `*.pre-harness` (numbered when one exists); a skill or INSTANCE link it didn't make is left alone with a warning. `setup-matt-pocock-skills` is installed like the other upstream skills; run it to generate an installation's `docs/agents/`.

## Why the launcher

Both clients stop at the nearest git repository: Claude Code reads `CLAUDE.md` upward but skills and hooks only from the repository root; Codex reads `AGENTS.md` and skills only from the repository root down. The launcher adds the workspace for that session only (`--add-dir` and `--settings` for Claude Code, `project_root_markers` for Codex) and runs the client unchanged anywhere else.
