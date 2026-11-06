# agent-harness

A harness for coding and research agents, assembled from established, replaceable tools that each own one responsibility. Tools connect through their existing CLI, API or MCP interfaces, plus a few skills that explain how to use them. Custom code stays minimal.

Two rules shape every choice:

- **Adopt before building.** Use an established tool wherever one exists; write our own only for what nothing else covers.
- **Model-agnostic and minimal.** Write down only what a capable model can't know (our facts, hard limits and deliberate departures from common practice), and enforce what matters with tools rather than prose.

## Axes

Each axis has one owner. Replacing a tool may need data migration and new instructions, but the other axes keep their owners. The tools are this harness's defaults; an installation can choose others.

| Axis | Owns | Default |
| --- | --- | --- |
| Knowledge | Durable concepts, decisions, sources and explanations | Karpathy-style Markdown wiki in modules (`knowledge/`) |
| Task management | Work items, owners, progress, blockers and handoffs | Linear |
| Repository workspace | Repositories, branches, merge requests and CI | Git, vcs2l, GitLab |
| Code structure | Where code concepts live and how they depend on each other, as derived diagrams | Emerge, Mermaid, AsyncAPI and OpenAPI |
| Doctrine | Principles, workflows as skills, and enforcement | `AGENTS.md`, `engineering/`, Matt Pocock's skills |
| Agent execution | Sessions, dispatch, models and budgets | Claude Code, Codex; `implement-spec` |

## Layers

Three repositories, each pinned by the next:

1. [mattpocock/skills](https://github.com/mattpocock/skills), kept untouched in `upstream/` as a git subtree.
2. **agent-harness** (this repository): the general harness.
3. **An installation** (private): `INSTANCE.md` with its people, paths, repositories and models, the issue-tracker mapping in `docs/agents/`, and client settings. Start from `INSTANCE.example.md`.

## Layout

| Scope | Where | Loaded |
| --- | --- | --- |
| Everything | `AGENTS.md`: principles and hard limits | always |
| Code | `engineering/`: the `engineering` and `frontend` skills | by description |
| One skill | `engineering/addenda/<skill>.md`, appended to the upstream skill of that name at install | with that skill |
| Knowledge | `knowledge/SCHEMA.md`, imported by each module's `CLAUDE.md`; `knowledge/module/` is the skeleton | in that module |
| Baseline | `upstream/skills/engineering/` and `productivity/` | by description |

## Flow

A project is a spec, its issues are thin slices with blocking links (`to-spec`, `to-tickets`). `implement-spec` starts one fresh subagent per unblocked issue on its own branch and worktree, merges each finished issue into `project/<slug>`, and ends with one `code-review` of the project branch. One merge request per repository brings the project into `main`. CI runs only the jobs a change affects.

See [CHEATSHEET.md](CHEATSHEET.md) for the commands you use day to day.

## Requirements

| Need | For | Required |
| --- | --- | --- |
| [Claude Code](https://claude.com/claude-code) and/or [Codex CLI](https://github.com/openai/codex) | Running the agents | yes, at least one |
| `git`, `jq`, a POSIX shell | `install.sh` and the git workflow | yes |
| An issue tracker with an MCP server ([Linear](https://linear.app) by default) | Projects, issues and their states | yes |
| A git host with merge requests and CI (GitLab or GitHub) | Project MRs into `main`, affected-only CI | yes, for code work |
| [Obsidian](https://obsidian.md) | Reading and editing knowledge modules | recommended |
| [vcs2l](https://github.com/ros-infrastructure/vcs2l) | Cloning and updating many repositories from one manifest | for multi-repo workspaces |
| [Quartz](https://quartz.jzhao.xyz), [TikZJax](https://tikzjax.com) | Publishing a wiki, rendering TikZ figures | optional |

## Install

Requires `jq`. Install into the workspace root the agents work under, and again after updating this checkout:

```sh
./install.sh /path/to/workspace /path/to/your/INSTANCE.md   # INSTANCE is remembered for later runs
```

The workspace root, not the account, selects the installation: everything is written under that root, nothing into a home directory, and a root that contains `$HOME` is refused. Accounts may be shared, and a session outside the root gets nothing from the harness.

| Written under the root | For |
| --- | --- |
| `.agent-harness/` | AGENTS, the skills with addenda appended, the knowledge schema, hooks, launcher and a link to INSTANCE |
| `CLAUDE.md` | AGENTS in full, read by Claude Code from the root and every directory below it, nested repositories and worktrees included |
| `CLAUDE.local.md` | link to INSTANCE, read the same way |
| `AGENTS.md` | AGENTS plus a pointer to INSTANCE, for Codex |
| `.claude/skills/`, `.agents/skills/` | links to the skills, for Claude Code and Codex |
| `.claude/settings.json` | Claude Code hooks: `SessionStart` asks to reload the skills in use after compaction and resume (AGENTS and INSTANCE come back by themselves as memory files); `SubagentStart` has every subagent load its matching skills first. Other settings stay. |

An entry file it didn't write, or one edited since, is moved aside as `*.pre-harness` (numbered when one exists); a skill or INSTANCE link it didn't make is left alone with a warning. `setup-matt-pocock-skills` isn't installed: the issue-tracker mapping lives once, in the installation.

Below the root, both clients stop at the nearest git repository: Claude Code still reads `CLAUDE.md` and `CLAUDE.local.md` upward, but skills and hooks only from the repository root; Codex reads `AGENTS.md` and skills only from the repository root down. So below the root, start agents with the launcher, which adds the workspace for that session only and runs the client unchanged anywhere else:

```sh
/path/to/workspace/.agent-harness/bin/claude   # adds --add-dir <root> --settings <root>/.claude/settings.json
/path/to/workspace/.agent-harness/bin/codex    # adds -c project_root_markers=[".agent-harness"], so the root is Codex's project root
```

Put `.agent-harness/bin` first on your `PATH` or alias the two, if you like; the installer doesn't change any account.

### Removing an account-wide install

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

## Start your own installation

1. Create a private repository for your installation.
2. Copy `INSTANCE.example.md` into it as `INSTANCE.md` and fill in your people, paths, tools and models.
3. Add `docs/agents/` with your issue-tracker mapping (how a spec, an issue, blocking links and states map onto your tracker). Matt's `setup-matt-pocock-skills` shows the format.
4. For each knowledge module, copy `knowledge/module/` and fill in its `CLAUDE.md`.
5. Run `./install.sh /path/to/workspace /path/to/your/INSTANCE.md` once per workspace root.

## Update upstream

Review Matt's changes, then:

```sh
git subtree pull --prefix=upstream https://github.com/mattpocock/skills.git main --squash
```

## License

MIT, see [LICENSE](LICENSE). Matt Pocock's skills in `upstream/` keep their own MIT license.
