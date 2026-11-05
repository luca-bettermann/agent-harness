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

## Install

Requires `jq`. Run once per account, and again after updating this checkout:

```sh
./install.sh
```

It builds `~/.agent-harness` (AGENTS, skills with addenda appended, the knowledge schema and the hook), links the skills into `~/.claude/skills` and `~/.codex/skills`, links `AGENTS.md` as `~/.claude/CLAUDE.md` and `~/.codex/AGENTS.md`, and adds a Claude Code `SessionStart` hook that re-injects AGENTS after compaction and resume. It never replaces a file it didn't create. The installation's workspace `CLAUDE.md` (and `AGENTS.md` for Codex) imports its `INSTANCE.md`.

## Update upstream

Review Matt's changes, then:

```sh
git subtree pull --prefix=upstream https://github.com/mattpocock/skills.git main --squash
```
