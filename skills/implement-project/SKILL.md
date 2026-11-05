---
name: implement-project
description: "Implement a Linear project's issues in code on the project branch, running subagents across the unblocked issues. Matt's implement-spec, in Linear vocabulary."
disable-model-invocation: true
---

Follow [`implement-spec`](../upstream/skills/engineering/implement-spec/SKILL.md) exactly, with these changes. Where other skills say `implement-spec`, spec or ticket, they mean this skill, the Linear project and its issues.

- **Integration branch:** `project/<slug>` in every repository the project touches.
- **Issue branch:** Linear's branch name for the issue, the same in every repository it touches, with one worktree per repository.
