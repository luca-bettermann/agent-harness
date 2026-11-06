# agent-harness

A harness for coding and research agents (Claude Code, Codex): shared principles, workflow skills and a knowledge schema, installed into one workspace. Built on [Matt Pocock's skills](https://github.com/mattpocock/skills).

- [Concept](docs/concept.md): axes, layers, layout and flow
- [Cheat sheet](CHEATSHEET.md): the commands you use day to day
- [Install details](docs/install.md): what the installer writes, the launcher, removing an old install
- [Decisions](docs/adr/): why the harness works the way it does

## Requirements

| Need | For | Required |
| --- | --- | --- |
| [Claude Code](https://claude.com/claude-code) and/or [Codex CLI](https://github.com/openai/codex) | Running the agents | yes, at least one |
| `git`, `jq`, a POSIX shell | `install.sh` and the git workflow | yes |
| An issue tracker with an MCP server ([Linear](https://linear.app) by default) | Projects, issues and their states | yes |
| A git host with merge requests and CI (GitLab or GitHub) | Project MRs into `main`, affected-only CI | yes, for code work |
| [Obsidian](https://obsidian.md) | Reading and editing knowledge modules | recommended |
| [vcs2l](https://github.com/ros-infrastructure/vcs2l) | Cloning and updating many repositories from one manifest | for multi-repo workspaces |
| [Quartz](https://quartz.jzhao.xyz), [TikZJax](https://tikzjax.com) | Publishing a wiki, rendering TikZ figures | optional |

## Install

```sh
./install.sh /path/to/workspace /path/to/INSTANCE.md
```

Then start agents below the workspace with `/path/to/workspace/.agent-harness/bin/claude` or `.../bin/codex`. Rerun the install after updating this checkout.

## Start your own installation

1. Create a private repository for your installation.
2. Copy `INSTANCE.example.md` into it as `INSTANCE.md` and fill in your people, paths, tools and models.
3. Add `docs/agents/` with your issue-tracker mapping (how a spec, an issue, blocking links and states map onto your tracker). Matt's `setup-matt-pocock-skills` shows the format.
4. For each knowledge module, copy `knowledge/module/` and fill in its `CLAUDE.md`.
5. Run the install above.

## Update upstream

Review Matt's changes, then:

```sh
git subtree pull --prefix=upstream https://github.com/mattpocock/skills.git main --squash
```

## License

MIT, see [LICENSE](LICENSE). Matt Pocock's skills in `upstream/` keep their own MIT license.
