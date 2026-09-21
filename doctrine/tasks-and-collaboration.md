The operator's policy for agents working this vault. `AGENTS.md` owns the
funnel, board, and gates; [[SKILLS - Workflow]] owns the work model. This note
owns authorization, priority, decomposition, dispatch, review, and completion.
The board named by `vault.toml` is the live queue, never a second policy source.

## Select and prioritize work

- `backlog` records identified work the operator has not authorized or prioritized.
- `open` is the spend gate: the operator moves a stream there, or an already-authorized dependency chain makes the next stream ready through a documented handoff.
- On session start, resume and idle, pull the vault and reconcile the streams routed to the agent: resume `in progress`, then take authorized `open` work in card order.
- A new `open` card never pre-empts work in progress; only the operator moves it ahead. Card order expresses priority only among cards of the same project.

## Create only useful queue entries

Track work only when it must survive the sitting: deferred, blocked, handed to another owner, awaiting the operator's review, or multi-session. Otherwise complete it directly; its output and Git history are the record. A question or coordination sentence is a direct message; an independently tracked deliverable is a task note, which holds work state and pickup, never durable knowledge.

- The board carries stream cards only; a task joins its stream through front matter ([[Task Note Template]]): scope, success criteria, current status, blockers, pickup, review links. Replace stale status; never append a diary.
- Fill `blocked:` only when work cannot progress, state the blocker, clear it when it lifts.
- Related fixes are checkboxes in one task note. Split into a separate task only when work changes owner, has an independent blocker, or is a reusable prerequisite.

## Build or escalate

Agents implement reversible, in-scope work whose approach is settled: routine implementation, mechanical changes, localized fixes, small features with an obvious method.

Escalate when a task forces an unmade architectural or methodological choice; changes an interface, data flow, storage, dependency or algorithm; is not cleanly reversible; triggers a physical system; creates an outward-facing commitment; or stays ambiguous after checking its sources. The orchestrator brings the decision to the operator in chat and the task waits with `blocked:` filled. Design is resolved in conversation under [[SKILLS - Architecture]]; the resulting plan is the source the task follows. The ladder is subagent → orchestrator → the operator; most questions stop with the orchestrator.

A ruling that adds a mechanism — store, service, background job, lock, cursor, document format, cross-repo seam — carries the design assessment matrix ([[Review Templates#Design assessment — mandatory for any mechanism-adding decision]]). A re-open verdict (effort L, or two or more new mechanisms, for an impact an existing store or function already provides) goes to the operator before anything is built; an agent never rules it alone.

**Pre-build plan review.** Before a package is dispatched, its plan — increments, note sections, rulings — passes a cold reviewer on the strong tier: a fresh agent that never builds or edits. It hunts internal contradictions, unruled forks, guards that do not bite, single-source violations, ordering and dependency errors, plan-versus-code drift and mechanism-heavy designs measured with the matrix, and proposes superior alternatives with their own matrix column. It returns one findings table; the orchestrator rules the principle-determined findings, brings open forks and re-open verdicts to the operator, and writes accepted changes into the notes before the builder starts.

## Dispatch

**Context is the cost.** Minimise large context handovers and maximise the value taken from context already accumulated. Every tool round re-reads an agent's whole context and a subagent's cache lives five minutes, so a long-context agent that waits, polls or is resumed pays for its history again. Everything below follows from it.

**Units.** A *task* is the tracked note. A *package* is the dispatch unit: the slice of a task one builder carries end to end, then one reviewer, then a cold-delta. The orchestrator defines a task's packages in its note ([[Task Note Template]] → *Packages*) before dispatch; a builder executes one and never re-slices. A task is normally one package; it splits only where gates or owners are independent. *Increments* are checkboxes inside a package — completeness checks, never agent boundaries. Delegate only work that is separable, self-contained and cheaper to specify and check than to do in the current context; keep entangled, exploratory or high-risk work in one head.

**Roles.** The session model judges: it reads the plan, grounds decisions, specifies, rules and gives verdicts — it never reads code to review it. Everything that produces an artifact — code, tests, a note edit, a lookup, a gate run — is dispatched with an explicit model, never the dispatching agent's by inheritance, with a specification precise enough to check the result; the session model writes an artifact itself only when the specification would be longer than the artifact. The builder completes the package and its self-checks. One reviewer examines the whole cumulative result and fixes what it finds in the same context; having edited, it relinquishes independent approval. A fresh cold reviewer checks those corrections and the affected callers, contracts and behavioural invariants against the reviewed baseline, wider when design or impact changed; unrelated accepted review is not repeated, and no third agent is needed when the reviewer changed nothing. Builder and reviewer keep their contexts through the package's increments and fixups; a changed plan or new design choice is re-reviewed, an unchanged checklist is not. A new agent starts from a compact specification plus the previous report, never from a resumed transcript; a cut-off agent is restarted from its preserved state and partial report.

**Tiers.** Mechanical work (LSP lookups, gate runs, single-file edits with exact text) → the cheapest tier; ordinary building, surveys, harnesses, note rewrites → the middle tier; judgment-heavy building → the strong building tier at high effort; cold review of code, design, plans and rulings → the strong tier, never cheap. Vendor model names are deployment bindings, not doctrine. Structure questions go through the LSP, never grep; grep serves non-code text and cross-checks, never as acceptance proof.

**Inside a dispatch.** Long gates run as one background command with one wait, output to files, only tails read back, no polling. The report is written incrementally so a cutoff loses nothing; a log is never pasted whole into a context. Every build and review report names its model and carries the invariant table for the test files it touched ([[SKILLS - Coding]] → *Testing*); a report whose builder is the session model is a rule violation. Incremental commits, exact acceptance evidence and one writer per worktree are preserved. Parallelism follows independent scope and ownership, not repository count.

**Channels.** A subagent returns through its own return channel when it finishes, never into a session pane. `agent-msg` runs only between the sessions the operator connects in chat; a question for another project goes to its orchestrator as a direct message, a substantial deliverable as a stream card. A cleared upstream handoff — the stream a task depends on reaching `promotion` — authorizes the requesting agent to resume the approved dependent work: `handoff_from:` records who asked, the requesting agent discovers it on reconcile or the completing agent flags it, and work continues without the operator unless it reaches the escalation boundary. When a dedicated implementation session runs, every build, gate and landing dispatch goes through it and it cold-reviews its own commits with its own subagents; the orchestrator reads reports, rules, sequences and records.

## Review and completion

Agents self-check before declaring work finished. The MR is the operator's court: a stream lands into `main` via one MR at completion ([[SKILLS - Workflow]]); its resolvable link goes into the stream note's `MR link:` line, is announced in chat the moment it opens and repeated whenever the MR is referred to. The card does not move for review; the operator requests changes in chat and work continues `in progress`; once the merge verifies, `vault sweep --to-promotion` moves the card.

**Reviews happen in chat.** The agent presents the review substance in the conversation — a self-contained digest, the evidence, the resolvable links — in the shapes of [[Review Templates]] (decision, implementation plan, result; each a ceiling, not a floor). "See the card" is as forbidden for a review as for design; the note carries links for durability, the chat is the delivery.

`promotion` is a conversation, never an archive: durable results are offered as candidates — canonical code, repository context, a permanent personal note, the team wiki — the operator ticks what stays, then `Execute`; `vault sweep --execute` deletes the stream note, its card and every member task note in one commit, refusing while references remain. Git history is the archive.

## Enforcement numbers

The bounds the tools refuse against are the operator's, tuned in `vault.toml` and never in the mechanism: the per-folder note caps, the `promotion` count and age bound, the backlog reporting age. `vault hygiene` blocks or reports each; `AGENTS.md` states the caps. One owning project per stream card. Sweep is event-bound to landing — merge → `vault sweep --to-promotion` → promotion conversation → `Execute` → next stream, in one step; the `promotion` bound is only the backstop. Cap enforcement is a ratchet: the hook refuses growth of an over-cap note, hygiene reports the over-cap backlog, and legacy over-cap notes never block a landing.

## Report without narrating the board

No routine column moves, card counts or board state in chat. After tracked work:

```text
Task Note Title done
Next: Next Task Title
```
