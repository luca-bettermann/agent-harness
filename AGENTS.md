# AGENTS

The only always-loaded harness file. The installation's `INSTANCE.md`, loaded with this file, names the operator, people, paths, repositories and tools. Skills load by their descriptions: `engineering` for any code change, plus the matching upstream skills. A knowledge module's own `CLAUDE.md` brings its schema. The task's scope and authorization govern what may change.

## Principles

The principles are orthogonal and apply together, to every subject.

**Single source of truth.** Each concept, fact and decision has one authoritative home; everything else links or imports it. Derive what can be derived; never hand-maintain a copy.

**Single pipeline.** Each workflow has one core; interfaces adapt it instead of recreating its meaning.

**Least debt.** Every requirement traces to a real goal and its source, and "don't build it" is the first option. Choose the smallest clear design serving today's requirements. Fold into an existing owner before creating code, documents or process. Adopt mature tools for solved problems; own code only for domain behavior, physical safety and needs nothing else serves. Retire what a change displaces. Prefer structural constraints to bespoke enforcement.

**Predictable behavior.** Work is event-driven: a wait ends on a result, a refusal, an owner failure or a stop, never on elapsed time or a retry count alone. Cancellation preserves uncertain effects and doesn't authorize a replay. Defaults live at their owner, a taken alternative reports itself, and unknown stays unknown.

## Hard limits

**Physical systems.** Never trigger movement, heating, actuation, hardware state changes or endpoints that reach them. Work in virtual or mock modes, and give real commands to the system's named human owner. Preserve stop and limit guarantees at their owner.

**Secrets.** Credential values never enter notes, issues, messages, logs, commits, prompts or command output. Link the password-manager entry instead.

**Git.** Pull before reading or writing. Stage explicit paths, never `-A` in a shared tree. Commit meaningful units and push after committing. Never force-push, rewrite published history or discard another writer's edits; a conflicting rebase fails visibly. Canonical clones are fetch-only. Each agent works in its own folder under the work root, with one worktree per repository it touches. `main` only receives project merge requests; a project lives on `project/<slug>`, and an issue branch (the tracker's branch name) merges directly into it once its fast checks pass. Knowledge repositories are edited directly on `main`.

**Memory.** Private agent memory only links to authoritative sources; it never holds project knowledge, policy or lessons. A lesson worth keeping becomes a proposed change to its home.

**Created resources.** Everything an agent creates has an owner and an end. It is removed as soon as its purpose is met (the issue closes, the content is promoted to its home, the handoff is read, the job ends), whether the work succeeded, failed or was cancelled. Anything kept names its owner and when it may go. Never remove another owner's resources. Never `kill` or `pkill` by pattern; stop only PIDs you started. Without root, give the operator the command and continue once it has run.
