# agent-harness

A harness for coding and research agents (Claude Code, Codex): shared principles, workflow skills and a knowledge schema, installed into one workspace. Built on [Matt Pocock's skills](https://github.com/mattpocock/skills).

Three layers, each with one job:

1. **Matt's skills, unchanged** in `upstream/`, all of them, including `setup-matt-pocock-skills`. Four short addenda add what he lacks: the builder report and its check, the knowledge issue, gates as a review check, and `emerge-map`.
2. **This harness adds** principles and hard limits (`AGENTS.md`), the knowledge module, the `engineering`, `frontend` and `writing` rules, and the install.
3. **An installation maps Matt's skills onto its infrastructure** in `docs/agents/` (tracker, labels, branches, merge requests, where findings go). Its `INSTANCE.md` holds facts about the installation: people, paths, tools, models.

- [Concept](docs/concept.md): axes, layers, layout and flow
- [Cheat sheet](CHEATSHEET.md): the commands you use day to day
- [Install details](docs/install.md): what the installer writes, the launcher, removing an old install
- [Decisions](docs/adr/): why the harness works the way it does

## Hooks

Claude Code hooks enforce three rules at the point of use: the first call per session to a tracker tool (pattern and mapping file from the installation's INSTANCE) is refused until the mapping is read; a `builder` subagent's prompt must be exactly `Implement <ISSUE-ID>.`; after a merge into `project/*` or a `merge_requests/<iid>/merge` call, the mapping's tracker checklist is injected. Each script runs a self-check with `--check`. Codex has no such hooks and gets the same rules as text only.

## Requirements

An agent CLI ([Claude Code](https://claude.com/claude-code) or [Codex](https://github.com/openai/codex)), `git`, `jq`, a POSIX shell, and a folder of Markdown files. The installation chooses the rest: issue tracker, Git host with CI, Obsidian for reading knowledge modules, [vcs2l](https://github.com/ros-infrastructure/vcs2l) for many repositories.

## Install

```sh
./install.sh /path/to/workspace /path/to/INSTANCE.md
```

Then start agents below the workspace with `/path/to/workspace/.agent-harness/bin/claude` or `.../bin/codex`. Rerun the install after updating this checkout.

## Start your own installation

1. Create a private repository for your installation.
2. Copy `INSTANCE.example.md` into it as `INSTANCE.md` and fill it in.
3. Run the install, then `/setup-matt-pocock-skills` to generate `docs/agents/`.
4. For each knowledge module, copy `knowledge/module/` and fill in its `CLAUDE.md`.

## Update upstream

Review Matt's changes, then:

```sh
git subtree pull --prefix=upstream https://github.com/mattpocock/skills.git main --squash
```

## License

MIT, see [LICENSE](LICENSE). Matt Pocock's skills in `upstream/` keep their own MIT license.
