# Concept

Assembled from established, replaceable tools, each owning one responsibility, connected through their CLI, API or MCP interfaces. Two rules: adopt before building, and write down only what a capable model can't know.

## Axes

Each axis has one owner. Replacing a tool may need data migration and new instructions, but the other axes keep their owners. The tools are this harness's defaults; an installation can choose others.

| Axis | Owns | Default |
| --- | --- | --- |
| Knowledge | Durable concepts, decisions, sources and explanations | Karpathy-style Markdown wiki in modules (`knowledge/`) |
| Task management | Work items, owners, progress, blockers and handoffs | Linear |
| Repository workspace | Repositories, branches, merge requests and CI | Git, vcs2l, GitLab |
| Code structure | Where code concepts live and how they depend on each other, as derived diagrams | Emerge, TikZ, AsyncAPI and OpenAPI |
| Doctrine | Principles, workflows as skills, and enforcement | `AGENTS.md`, `engineering/`, Matt Pocock's skills |
| Agent execution | Sessions, dispatch, models and budgets | Claude Code, Codex; `implement-spec` |

## Layers

Three repositories, each pinned by the next:

1. [mattpocock/skills](https://github.com/mattpocock/skills), kept untouched in `upstream/` as a git subtree.
2. **agent-harness** (this repository): what Matt lacks, namely principles, knowledge, `engineering`, `frontend` and `writing` rules, four short addenda, the install.
3. **An installation** (private): the mapping of Matt's skills onto its infrastructure in `docs/agents/` (tracker, labels, branches, merge requests), and `INSTANCE.md` with its people, paths, repositories and models. Start from `INSTANCE.example.md`.

## Layout

| Scope | Where | Loaded |
| --- | --- | --- |
| Everything | `AGENTS.md`: principles and hard limits | always |
| Code | `engineering/`: the `engineering` and `frontend` skills | by description |
| One skill | `engineering/addenda/<skill>.md`, appended to the upstream skill of that name at install; only true additions (ADR 0008) | with that skill |
| Knowledge | `knowledge/SCHEMA.md`, imported by each module's `CLAUDE.md`; `knowledge/module/` is the skeleton | in that module |
| Baseline | `upstream/skills/engineering/` and `productivity/`, all installed | by description |

## Flow

A project is a spec, its issues are thin slices with blocking links (`to-spec`, `to-tickets`). `implement-spec` starts one fresh subagent per unblocked issue on its own branch and worktree, merges each finished issue into `project/<slug>`, and ends with one `code-review` of the project branch. One merge request per repository brings the project into `main`. CI runs only the jobs a change affects.

