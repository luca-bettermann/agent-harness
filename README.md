# agent-harness

`agent-harness` is a Git-backed method and command-line tool for coordinating agent work through task notes, stream notes, a board, and explicit review and promotion gates. The public repository owns the reusable method. A private instance supplies the work, deployment bindings, and knowledge stores for one team.

| Public framework | Private instance |
| --- | --- |
| `AGENTS.md`, doctrine, skills, templates, base views, examples, and `vaulttools` | `INSTANCE.md`, `vault.toml`, the live board, task and stream notes, mounted repositories, private knowledge, and local editor state |

The working vault and a team wiki may be independent sibling repositories. Record their concrete locations in the private `INSTANCE.md`; the framework does not own or mirror team knowledge.

## Layout

- `AGENTS.md` is the always-read entry point. It loads `INSTANCE.md` when an instance provides one.
- `doctrine/` holds the reusable operating method, craft skills, and note templates.
- `Board.base` and `Backlog.base` are optional Obsidian Bases views over task front matter.
- `tools/vaulttools/` provides the `vault` command.
- `vault.example.toml`, `INSTANCE.example.md`, and `Kanban.example.md` are copied into a private instance and edited there.

## Prerequisites

- Python 3.11 or newer
- [uv](https://docs.astral.sh/uv/)
- Git
- `glab` only when `vault sync` must derive stream state from GitLab merge requests

## Start a private instance

Clone this repository into a private remote, or merge its clean initial commit once into an existing private repository as described below. In the private checkout:

```sh
cp vault.example.toml vault.toml
cp INSTANCE.example.md INSTANCE.md
cp Kanban.example.md Kanban.md
cd tools/vaulttools
uv sync --locked
uv run vault --vault ../.. hook install
```

Edit the copied files before normal use. The example explicitly selects `tasks/`; without a config file, the CLI retains legacy task-folder defaults for both `tasks` and `08 Tasks`. Keep the public examples generic and commit concrete bindings only to the private repository.

For an existing private repository with unrelated history, add this public repository as `upstream`, fetch its public `main`, and make one normal merge with `--allow-unrelated-histories`. Resolve shared files to the reviewed public versions while preserving private-only files. Future framework updates are ordinary ancestry-preserving merges from `upstream/main`.

## Daily use

Run `uv run vault --help` and each subcommand's `--help` for the current interface. The command effects are summarised in [tools/README.md](tools/README.md): `hygiene` is read-only, `sync` may fetch canonical repositories and edit derived status fields, and `move` and `sweep` commit and push private vault state.

Pull private work from `origin` as usual. Review public framework updates separately: fetch `upstream`, inspect the public-only range, then merge an accepted public commit into the private branch. Do not combine an upstream framework review with an ordinary private `origin` pull.

## Contributing without private history

Develop public changes in a clean clone of `agent-harness`. Never push a private instance branch, merge commit, task note, board, config, binding file, mount, or private Git history to the public remote. Export only reviewed generic changes into the clean public checkout and inspect its tree and reachable commits before pushing.

## Tests

```sh
cd tools/vaulttools
uv sync --locked
uv run pytest
uv run ruff check .
uv run pyright
uv run vault --help
```

## Shipped limits

- `vault sync` is explicit; the harness does not install a startup refresh or pull every mounted repository automatically.
- Default remote status derivation uses GitLab merge-request state through `glab`. `--local` writes no status and runs hygiene only.
- `vault sync` does not pull, commit, or push the vault. In remote mode it fetches only the canonical repositories needed for status derivation and writes changed status fields to the working tree.
- A `[scopes]` table may document instance paths, but the current CLI neither loads it nor enforces cross-scope link direction.
- The repository ships no host installer. Hook installation is the explicit `vault hook install` action.
