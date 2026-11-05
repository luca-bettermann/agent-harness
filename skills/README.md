# Skills

- `upstream/` is [mattpocock/skills](https://github.com/mattpocock/skills) as a `git subtree` (MIT, see `upstream/LICENSE`). Never edit it; our additions live in the overlays and in each repository's `docs/agents/`.
- Update it after reviewing upstream's changes:
  `git subtree pull --prefix=skills/upstream https://github.com/mattpocock/skills.git main --squash`
- Skill names stay as upstream names them (`to-spec`, `to-tickets`, `implement-spec`, …). In Linear terms a spec is a project description and a ticket is an issue; `docs/agents/issue-tracker.md` tells the skills so.
- Installed from upstream: `engineering/` and `productivity/`. Left out: `in-progress/` (unfinished), `deprecated/`, and `misc/` (TypeScript-specific, or blocking `git push`, which our git rules require).
