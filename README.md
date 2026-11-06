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

Requires `jq`. Run once per account, and again after updating this checkout:

```sh
./install.sh
```

It builds `~/.agent-harness` (AGENTS, skills with addenda appended, the knowledge schema and the hook) and links the skills into `~/.claude/skills` and `~/.codex/skills`; a skill link it didn't make is left alone with a warning. It writes `~/.claude/CLAUDE.md` and `~/.codex/AGENTS.md` to load AGENTS and the given `INSTANCE.md` (`./install.sh <path>`, remembered). An entry file it didn't write, or one edited since, is moved aside as `*.pre-harness` (numbered when one exists). It adds a Claude Code `SessionStart` hook that re-injects AGENTS and INSTANCE after compaction and resume. `setup-matt-pocock-skills` isn't installed: the issue-tracker mapping lives once, in the installation.

## Start your own installation

1. Create a private repository for your installation.
2. Copy `INSTANCE.example.md` into it as `INSTANCE.md` and fill in your people, paths, tools and models.
3. Add `docs/agents/` with your issue-tracker mapping (how a spec, an issue, blocking links and states map onto your tracker). Matt's `setup-matt-pocock-skills` shows the format.
4. For each knowledge module, copy `knowledge/module/` and fill in its `CLAUDE.md`.
5. Run `./install.sh /path/to/your/INSTANCE.md` on every account that runs agents.

## Update upstream

Review Matt's changes, then:

```sh
git subtree pull --prefix=upstream https://github.com/mattpocock/skills.git main --squash
```

## License

MIT, see [LICENSE](LICENSE). Matt Pocock's skills in `upstream/` keep their own MIT license.
