# Install details

Everything is written under the workspace root, nothing into a home directory; a root that contains `$HOME` is refused. Accounts may be shared: a session outside the root gets nothing from the harness.

| Written under the root | For |
| --- | --- |
| `.agent-harness/` | AGENTS, the skills with addenda appended, the knowledge schema, hooks, launcher and a link to INSTANCE |
| `CLAUDE.md` | AGENTS in full, read by Claude Code from the root and every directory below it, nested repositories and worktrees included |
| `CLAUDE.local.md` | link to INSTANCE, read the same way |
| `AGENTS.md` | AGENTS plus a pointer to INSTANCE, for Codex |
| `.claude/skills/`, `.agents/skills/` | links to the skills, for Claude Code and Codex |
| `.claude/settings.json` | Claude Code hooks: `SessionStart` asks to reload the skills in use after compaction and resume (AGENTS and INSTANCE come back by themselves as memory files); `SubagentStart` has every subagent load its matching skills first; the read-gate, builder-prompt and merge-checklist hooks (see README). Other settings stay. |
| `.claude/agents/builder.md` | link to the `builder` agent type, started with `Implement <ISSUE-ID>.` |

An entry file it didn't write, or one edited since, is moved aside as `*.pre-harness` (numbered when one exists); a skill or INSTANCE link it didn't make is left alone with a warning. `setup-matt-pocock-skills` is installed like the other upstream skills; run it to generate an installation's `docs/agents/`.

An entry file the installer didn't write, or one edited since, is moved aside as `*.pre-harness`; a link it didn't make is left alone with a warning.

## Why the launcher

Both clients stop at the nearest git repository: Claude Code reads `CLAUDE.md` upward but skills and hooks only from the repository root; Codex reads `AGENTS.md` and skills only from the repository root down. The launcher adds the workspace for that session only (`--add-dir` and `--settings` for Claude Code, `project_root_markers` for Codex) and runs the client unchanged anywhere else.

## Removing an account-wide install

Earlier versions installed into `~/.agent-harness` and wrote account-wide entry points, skill links and hooks. On each account that ran one, remove exactly what that installer wrote:

```sh
h=$HOME/.agent-harness
for p in claude:.claude/CLAUDE.md codex:.codex/AGENTS.md; do
  e=$HOME/${p#*:}; [ -e "$e" ] || continue
  if cmp -s "$e" "$h/written/${p%%:*}"; then rm "$e"; else echo "kept $e: not the installer's copy"; fi
done
for l in "$HOME"/.claude/skills/* "$HOME"/.codex/skills/*; do
  case $(readlink "$l") in "$h"/*) rm "$l";; esac
done
f=$HOME/.claude/settings.json
[ -f "$f" ] && jq --arg h "$h/" 'if .hooks then .hooks |= (map_values(map(select(all(.hooks[]?; .command | contains($h) | not)))) | with_entries(select(.value != []))) else . end' "$f" > "$f.tmp" && cat "$f.tmp" > "$f"; rm -f "$f.tmp"
rm -rf "$h"
```
