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

## Flow

A project is a spec, its issues are thin slices with blocking links (`to-spec`, `to-tickets`). `implement-spec` starts one fresh subagent per unblocked issue on its own branch and worktree, merges each finished issue into `project/<slug>`, and ends with one `code-review` of the project branch. One merge request per repository brings the project into `main`. CI runs only the jobs a change affects.

