# agent-harness

A harness for coding and research agents (Claude Code, Codex): shared principles, workflow skills and a knowledge schema, installed into one workspace. Built on [Matt Pocock's skills](https://github.com/mattpocock/skills), kept unchanged in `upstream/`; our short additions to them live in [`engineering/addenda/`](engineering/addenda/). An installation maps the skills onto its infrastructure in its own `docs/agents/` and names its people, paths and tools in its `INSTANCE.md`.

The harness is split into independent axes, each with one owner: knowledge, task management, repository workspace, code structure, doctrine and agent execution. Any tool behind an axis can be replaced without touching the others ([Concept](docs/concept.md)).

- [Concept](docs/concept.md): axes and flow
- [Install details](docs/install.md): what the installer writes and why the launcher
- [Decisions](docs/adr/): why the harness works the way it does

## Flow

1. Explore in the conversation (`/wayfinder`, `/grill-me`, `/research`); nothing goes to the tracker yet.
2. `/to-spec`, then `/to-tickets`: the project and its issues.
3. `/implement-spec`: one subagent per unblocked issue, one review of the project branch.
4. "Update knowledge": the project's last issue, run with the operator.

## Hooks

One hook, the same for Claude Code and Codex: on every prompt, at every subagent start, and after compaction or resume, the agent is told AGENTS' skill-loading rule (`sh hooks/load-skills.sh --check`). For Codex the installer trusts the workspace in the account's config; the first Codex session then asks once to trust the hook.

## Requirements

An agent CLI ([Claude Code](https://claude.com/claude-code) or [Codex](https://github.com/openai/codex)), `git`, `jq`, a POSIX shell, and a folder of Markdown files. The installation chooses the rest: issue tracker, Git host with CI, Obsidian for reading knowledge modules, [vcs2l](https://github.com/ros-infrastructure/vcs2l) for many repositories.

## Install

```sh
./install.sh /path/to/workspace /path/to/INSTANCE.md
```

Then start agents below the workspace with `/path/to/workspace/.agent-harness/bin/claude` or `.../bin/codex`. Rerun the install after updating this checkout or installing another client.

## Update upstream

Review Matt's changes, then:

```sh
git subtree pull --prefix=upstream https://github.com/mattpocock/skills.git main --squash
```

## License

MIT, see [LICENSE](LICENSE). Matt Pocock's skills in `upstream/` keep their own MIT license.
