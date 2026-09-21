# vaulttools

`vaulttools/` provides the `vault` command used by a private harness instance. It
reads layout and bounds from `vault.toml` at the vault root. Run `vault --help`
and `vault <command> --help` for the exact current arguments.

The commands have deliberately different mutation boundaries:

- `vault hook install` writes the checkout's Git pre-commit hook. `vault hook
  check` only inspects staged Markdown notes and refuses a newly grown note over
  its configured cap.
- `vault hygiene` is read-only. It checks the configured vault and workspace;
  `--report-only` always exits successfully after rendering findings.
- `vault sync` derives stream status from canonical Git repositories. Remote mode
  fetches each required repository once, queries GitLab merge requests with
  `glab`, and writes only changed `status` front-matter fields in the vault
  working tree. It does not pull, commit, or push the vault. `--local` performs
  no fetch or status write and returns hygiene results only.
- `vault move` rebases the vault from `origin`, edits the configured board,
  commits that board, and pushes `origin/main`.
- `vault sweep` verifies recorded merge ancestry after fetching participating
  repositories. `--to-promotion` moves and pushes the stream card;
  `--execute` deletes the authorised stream/task notes and card in one commit and
  pushes `origin/main`.

The CLI retains legacy task-folder defaults for `tasks` and `08 Tasks`. A new
instance should set `tasks = ["tasks"]` explicitly, as `vault.example.toml` does.
The optional `[scopes]` table is documentation only: the current loader ignores
it and no command enforces scope-link direction. The project installs no startup
refresh, all-repository pull, or host-side cutover automation.

Run the gates:

```sh
cd tools/vaulttools
uv sync --locked
uv run pytest
uv run ruff check .
uv run pyright
uv run vault --help
```
