# Knowledge

- `SCHEMA.md`: the rules every knowledge module imports.
- `module/`: the skeleton for a new module. Copy it once; its `CLAUDE.md` imports the installed `SCHEMA.md`, so the rules stay current. A shared wiki whose readers lack agent-harness vendors a copy of `SCHEMA.md` instead, updated deliberately.
- `ingest/`: the `ingest` skill (`/ingest <note>`).
- `index.py`: regenerates a module's `index.md` files from page descriptions; `--check` is the lint.
- `writing/`: the `writing` skill for prose people read.
- `drafts/`: writing skills not yet mature enough to load (Academic Writing, Literature Review, Visual Identity).
