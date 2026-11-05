# Engineering

- `engineering/` and `frontend/` are skills of our own. `engineering` loads for any code change.
- `addenda/<skill>.md` is appended to Matt's skill of the same name (in `../upstream/skills/engineering/`) at install. Matt's files stay untouched.
- Installed from upstream: `engineering/` and `productivity/`. Left out: `in-progress/`, `deprecated/` and `misc/` (TypeScript-specific, or blocking `git push`, which our git rules require).
- Update upstream after reviewing its changes:
  `git subtree pull --prefix=upstream https://github.com/mattpocock/skills.git main --squash`
