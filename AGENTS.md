# AGENTS

The only always-loaded harness file. The installation's `INSTANCE.md`, loaded with this file, names the operator, people, paths, repositories and tools, including the issue-tracker mapping that tracker skills read. Before acting, and again after compaction or resume, load every skill whose description matches the task. A knowledge module's own `CLAUDE.md` brings its schema. The task's scope and authorization govern what may change.

## Principles

They hold in every domain we work in: code, documentation, tests, tasks and workflows. Each is a requirement; implement the simplest solution that satisfies all five.

**Single source of truth.** Everything has one authoritative home; everything else links to it or derives from it. Never maintain a copy by hand.

**Least debt.** The least total debt over the system's life, not the smallest change today. Build only for a real, current need; use an existing owner or a mature tool before building your own; retire what a change replaces.

**Root cause.** Fix a problem where it starts: in the principle, the skill or how they are loaded. Change the structure instead of adding a guard for the single case.

**Self-correcting.** Rules aren't always followed, so whoever finds a violation repairs it: within their task they fix it, otherwise they add it to the owner's open issue, or open one if none fits. The start and end of every project check the work against the doctrine.

**Predictable behavior.** Work moves on events and states its outcome: a wait ends on a result, a refusal or a stop, never on elapsed time alone; what is unknown is reported as unknown; a default lives with its owner, and a deviation reports itself.

## Hard limits

**Physical systems.** Never trigger movement, heating, actuation, hardware state changes or endpoints that reach them. Work in virtual or mock modes, and give real commands to the system's named human owner. Preserve stop and limit guarantees at their owner.

**Secrets.** Credential values never enter notes, issues, messages, logs, commits, prompts or command output, except a store INSTANCE names as allowed to hold them; never copy them out of it or print them. Link the password-manager entry instead.

**Git.** Pull before reading or writing. Stage explicit paths, never `-A` in a shared tree. Commit meaningful units and push after committing. Never force-push, rewrite published history or discard another writer's edits; a conflicting rebase fails visibly. Canonical clones are fetch-only. Each agent works in its own folder under the work root, with one worktree per repository it touches. In code repositories `main` only receives project merge requests. Only the personal knowledge base and the installation repository are edited directly on `main`; other knowledge modules follow their own contribution rules.

**Memory.** Private agent memory only links to authoritative sources; it never holds project knowledge, policy or lessons. A lesson worth keeping becomes a proposed change to its home.

**Created resources.** Everything an agent creates belongs to an issue, and its name says which (a branch is the issue's branch name, a folder carries the issue's identifier). It is removed as soon as its purpose is met (the issue closes, the content is promoted to its home, the handoff is read, the job ends), whether the work succeeded, failed or was cancelled. While its issue is open, only the agent working on that issue touches it. A cleanup of other agents' resources checks each owning issue in the tracker and removes only resources of closed issues; age or apparent disuse is not ownership. A resource that names no issue is a violation: report it, or remove it once nobody is working on it. Never `kill` or `pkill` by pattern; stop only PIDs you started. Without root, give the operator the command and continue once it has run.
