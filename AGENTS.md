# AGENTS

This is the only always-read framework file. If INSTANCE.md exists, read it immediately afterward. Then read every applicable section 8 route before work. Without an instance file, use the task and repository configuration for concrete bindings; do not require a private extension. Explicit task scope and authorization govern what may be changed. `vault.toml` supplies the machine-readable layout and bounds.

## 1. Vault and knowledge

This vault holds agent working memory and doctrine. Knowledge moves from disposable scratch through task notes into doctrine or an instance-supplied evergreen store, never back. No agent-private memory holds project knowledge. Agents write permanent personal or team knowledge only during accepted promotion with the operator present. [[Agentic Documentation System]] defines knowledge homes and granularity; INSTANCE names concrete stores.

## 2. Global principles

**Single source of truth.** Each concept, fact and decision has one authoritative home; other sites import or link it. [[SKILLS - SSOT and Single Pipeline]] supplies the authority map and refusal gate.

**Single pipeline.** Each workflow has one semantic kernel. Interfaces adapt that core instead of recreating its meaning.

**Least debt — fold before create.** Before adding code, infrastructure, documents or process, name the existing home that could absorb it. A new artifact needs a positive reason, such as distinct ownership or lifecycle. Retire superseded artifacts and use structural constraints before bespoke enforcement; genuine preferences stay norms.

**Minimal design.** Choose the smallest design that meets today's requirements. Every mechanism, field and check serves a current consumer. Cut unused generality rather than readability.

**Adopt before build.** Adopt mature tools for solved capabilities. Owned code is for domain behavior, physical safety and needs no existing tool serves. Standard-library preference governs lines inside owned code, never the decision to rebuild a subsystem.

## 3. Permanent homes

Use [[Agentic Documentation System]] for the home of a fact and INSTANCE for its concrete binding. A shipped deliverable replaces its provisional authority; permanent documents describe current state and Git retains change history.

## 4. Hard limits

**Physical systems.** Never autonomously trigger movement, heating, actuation, hardware state changes or endpoints reaching them. Write code and test in virtual or mock modes; give the real command to the human owner. Ask that owner about the system instead of opening a hardware session or parking an answerable question. Each device context names its system and human owner.

**Secrets.** Credential values never enter notes, cards, messages, logs, commits or prompts. Name and link their password-manager entries. The operator executes or explicitly approves rotations.

**Git.** Pull before reading or writing, subject to explicit task restrictions. INSTANCE names additional synchronization commands. Stage explicit intended paths, never `-A` in a shared tree. Commit meaningful units with short messages; push right after committing. Never force-push, rewrite published history or discard another writer's edits; a conflicting rebase fails loudly. `main` is the only long-lived branch and remains deployable. INSTANCE names the release authority; deployability alone is not accepted deployment.

**Knowledge repositories.** Edit, commit and push agent and personal knowledge-base notes directly on `main`, without knowledge-base branches or worktrees. Serialize vault commits; other writers return drafts or patches. Independent team stores keep their contribution rules.

**Code writers.** Canonical clones are fetch-only. Each lane has one writer and its own worktree under the configured work root. [[SKILLS - Work]] owns lane branches and retirement; [[SKILLS - Interfaces]] owns dependency pins.

**Created resources.** Disposable work lives in a separate owned directory per job under harness scratch, otherwise `temp/<job>/`, never a shared parent. Each step removes what it creates, including daemon-held resources, on completion, failure or cancellation. Label resources with their owner and use existing finalization hooks. Preserved releases, environments and host-managed state have declared lifetimes. Remove only your own resources. Never `pkill` or `kill` by pattern; stop only PIDs you started and recorded. Prefer no-root alternatives; otherwise give the operator the command and continue when that step runs.

## 5. Tracked work

[[SKILLS - Work]] owns authorization, queues, task membership, landing and promotion. Task and Stream Note Templates define note fields; tools enforce their schema.

## 6. Dispatch

[[SKILLS - Work]] owns roles, explicit model selection, context continuity, reporting and communication. INSTANCE maps those roles to current models.

## 7. Design and review

[[SKILLS - Work]] owns the design and review gates and escalation policy. [[Review Templates]] supplies their shapes and measurement rules. [[SKILLS - SSOT and Single Pipeline]] supplies the structural review gate.

## 8. Routing

Read every applicable row. Tracked work adds Work. An optional INSTANCE.md marked route table extends this inventory. Later sources may override only explicit preferences within their stated scope, never an enforced schema or an unrelated rule.

| Work | Read |
| --- | --- |
| Writing, notes, documentation | doctrine/Writing Guide.md; doctrine/Agentic Documentation System.md |
| Coding, tests, refactors | doctrine/skills/SKILLS - Coding.md |
| Architecture and system design | doctrine/skills/SKILLS - Architecture.md |
| Published interfaces, versions and verification | doctrine/skills/SKILLS - Interfaces.md |
| State, identity, derivation, persistence, orchestration, presentation | doctrine/skills/SKILLS - SSOT and Single Pipeline.md |
| Audits and redesign of existing code | doctrine/skills/SKILLS - Audit.md |
| Work from authorization through packages, dispatch, review, landing and retirement | doctrine/skills/SKILLS - Work.md |
| Browser interfaces | doctrine/skills/SKILLS - Frontend.md |
| Literature review and synthesis | doctrine/skills/SKILLS - Literature Review.md |
| Academic writing, papers and LaTeX | doctrine/skills/SKILLS - Academic Writing.md |
| Figures, plots and presentations | doctrine/skills/SKILLS - Visual Identity.md |
| Presenting reviews, designs and decisions | doctrine/templates/Review Templates.md |
| Task note | doctrine/templates/Task Note Template.md |
| Stream note | doctrine/templates/Stream Note Template.md |


## 9. Tools

`vault` is the existing CLI under `tools/`; `vault --help` describes invocation. Work owns the events that use its move, sweep, hygiene and cap mechanisms.
