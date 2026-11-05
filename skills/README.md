# Skills

- `upstream/` is [mattpocock/skills](https://github.com/mattpocock/skills) as a `git subtree` (MIT, see `upstream/LICENSE`). Never edit it; changes go in a skill beside it.
- Update it after reviewing upstream's changes:
  `git subtree pull --prefix=skills/upstream https://github.com/mattpocock/skills.git main --squash`
- Installed from upstream: `engineering/` and `productivity/`, except the three skills renamed here. Left out: `in-progress/` (unfinished), `deprecated/`, and `misc/` (TypeScript-specific, or blocking `git push`, which our git rules require).
- Renamed to Linear vocabulary, each a thin delta on the upstream skill it names:

| Ours | Upstream |
| --- | --- |
| `to-project` | `to-spec` |
| `to-issue` | `to-tickets` |
| `implement-project` | `implement-spec` |
