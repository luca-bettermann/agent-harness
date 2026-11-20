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

Three hooks, the same for Claude Code and Codex: on every prompt, at every subagent start, and after compaction or resume, the agent is told AGENTS' skill-loading rule (`sh hooks/load-skills.sh --check`). Both clients also get a gate (`sh hooks/skill-gate.sh --check`): after compaction or resume, and in Claude Code at a subagent start too, every tool except a skill load is denied until the agent loads a skill (Claude Code: the `Skill` tool; Codex: a call whose input contains `SKILL.md`; [ADR 0009](docs/adr/0009-skill-gate.md)). A command guard (`sh hooks/command-guard.sh --check`) refuses `pkill`, `killall`, `kill` by pattern and a `git stash` without a pathspec, naming the allowed form ([ADR 0010](docs/adr/0010-command-guard.md)). For Codex the installer trusts the workspace in the account's config; the first Codex session then asks once to trust the hook.

## Requirements

An agent CLI ([Claude Code](https://claude.com/claude-code) or [Codex](https://github.com/openai/codex)), `git`, `jq`, a POSIX shell, and a folder of Markdown files; [uv](https://docs.astral.sh/uv/) for `emerge-map`. The installation chooses the rest: issue tracker, Git host with CI, Obsidian for reading knowledge modules, [vcs2l](https://github.com/ros-infrastructure/vcs2l) for many repositories.

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
