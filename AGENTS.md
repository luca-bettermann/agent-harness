# AGENTS

The only always-read framework file; everything else loads through section 8.
If `INSTANCE.md` exists at the vault root, read it immediately after this file.
It supplies concrete people, paths, remotes, repositories, knowledge stores and
domain rules. `vault.toml` is the CLI's machine-readable layout and bounds.
Neither file replaces the method here.

## 1. This vault and the funnel

This vault is agents' working memory and doctrine. Its root holds `AGENTS.md`,
the board and task folders named by `vault.toml`, `doctrine/`, `temp/`, and
`tools/`. A private instance may add `INSTANCE.md`, mounted repositories, local
editor state, and independent knowledge stores as recorded in that file.
Knowledge moves one way — from `temp` through task notes into `doctrine` or an
instance-supplied evergreen knowledge store, never back.
`temp/` — scratch, probe logs from any lane, dead on read or step end; uncapped, never a source.
Configured task folders — task/stream notes: scope, criteria, status, pickup,
links; swept when the stream's branch dies.
`doctrine/` — skills and templates (this file, at the root, belongs to the same layer): standing rules agents load; it never dies — superseded text is deleted in place.
No agent-private memory holds project knowledge; the vault or an
instance-supplied knowledge store does. Personal and team knowledge stores take
only what promotion accepts; agents write there only during the promotion
conversation, with the operator present. The team store may be an independent
sibling repository. `INSTANCE.md` names those stores without duplicating them.

## 2. Main principles

**Single source of truth.** Every concept, constant and decision has exactly one home; everything else links or imports it, never restates it. Logic is defined once, called; a cross-boundary fact is one repo's shipped artifact the other reads. Derived data is a view computed on read by one function; a store is a declared materialisation with a rebuild-equals-stored guard (Architecture → *Data & storage*).

**Single pipeline.** One kernel per workflow, one authoritative path: no parallel implementation, fallback, shim or second way to do it; interfaces adapt the one core rather than recreate its meaning. A blocking contract is escalated, changed at its source, never worked around locally.

**Least debt — fold before create.** Every addition — code, infrastructure, docs, process — is standing liability; the simplest structure that does the job wins. **Fold before create** in every medium: any addition first names the existing home that could absorb it; a new artifact needs a positive reason (a standalone concept, new owner, independent lifecycle), never merely the absence of one. A shipped deliverable becomes the source of truth: distil what still matters into its permanent home, delete the rest. Enforcement follows suit — an unenforced load-bearing rule is recurring debt, retired **structurally first** (type, bound, config, impossible-by-construction) before any bespoke tool; genuine preferences stay norms.

## 3. Where things live

| Thing | Single home |
| --- | --- |
| Concept — what and why, with rejected alternatives | instance-supplied evergreen knowledge note; supersede in place |
| Implementation — the how | repo code |
| Cross-module constants, codes, IDs | the repo's schema module |
| As-built structure — API, module purpose, wiring | repo `*_CONTEXT.md`, updated with the change |
| Figures and visual assets | code-generated: the generating repo; hand-made: the instance-supplied asset store — Visual Identity governs both |
| Why we changed | git history |

When in doubt: what changes with the code belongs to the repo, what survives a rewrite to a note.

## 4. Hard rules

**Physical systems.** Never autonomously call anything that can move, heat, actuate or change hardware state, or any endpoint reaching it. Write code only, test in a virtual or mock mode; hand the operator the command for real-hardware runs. The rule restricts *triggering* hardware, never *asking about* it: each device repository's `*_CONTEXT.md` names the physical system it drives and its human owner; ask that owner instead of opening a hardware session or parking the question as a blocker.

**Secrets.** A credential value never enters a note, card, message, log, commit or prompt — name and link it in the password manager. Rotations are the operator's to execute or approve.

**Git.** Pull before you read or write, using any additional large-file or
reference-store commands named by `INSTANCE.md`. Commits are meaningful units
of work, short messages, never per edit; push right after committing. Stage
explicit paths, never `-A`, in any tree a second writer may touch; a rebase that
conflicts fails loud, never discarding edits. Never force-push or rewrite
history — pins and release records name exact SHAs. `main` is production,
always deployable, the only long-lived branch.

**Worktrees.** One workspace root holds every repository as a **fetch-only,
never edited** clone under the directory named by `vault.toml`. Every lane,
orchestrator included, works in its own worktree at
`<root>/work/<lane>/<repo>` on its own `lane/<stream>/…` branch cut from
`stream/<stream>` — never on `main` or the stream branch itself. Environments
are per worktree; landing removes both. One writer per worktree, **one
committing writer per vault clone at a time**, scheduled through dispatch;
every other lane returns a draft or a patch. A cross-root code dependency is a
pinned Git reference (`tag` release, `branch` development), never a foreign
working tree; editable path dependencies stay inside one root.

**Working space.** Nothing created outlives its step unless promoted. Disposable work — a throwaway clone, scratch file, test container, one-gate env — lives in its own directory per job under the scratch root (the harness's scratch dir, else `temp/<job>/`), never a shared parent, deleted by the step that created it; a leftover is that step's defect. Remove only your own — a sibling lane's worktree or scratch is not a leftover. Releases, gate environments, a `.venv` and host-managed state are kept on purpose. `sudo` is not a blocker: prefer no-root alternatives, else give the operator the command and continue once it runs.

## 5. How work is organised

**The board.** The board file holds **stream cards only**; each column has one meaning:

| Column | Meaning |
| --- | --- |
| `backlog` | Prepared, not authorised — no spend |
| `open` | Authorised; the spend gate — base branch publishes on entry |
| `in progress` | Dispatch runs against a live branch, through MR review |
| `promotion` | Merge verified; the branch is gone, the note holds the evidence. The configured bound applies. |

The card is the one `- [ ] [[Stream x]]` line on the board; everything else — description, rulings, MR link, merge evidence, promotion — lives in the stream note.

**Tasks are notes, never cards.** A task note lives in a configured task folder;
its front matter uses the fields in `doctrine/templates/Task Note Template.md`.
Front matter is the **one membership authority**: a task joins a stream by its
`stream:` value; the note's `Tasks:` list must agree with it, and the sweep
refuses on any member missing from either side. Increments are checkboxes in a
task note — one needing its own scope, criteria or pickup becomes a task. A
backlog note older than the configured reporting age is reported, never deleted.

Work that must outlive the sitting — deferred, blocked, multi-session, or awaiting the operator's review — is a task note in a stream; anything else is done directly, its commit the record. On start, resume and idle the orchestrator pulls the vault and reconciles its streams: `in progress` first, then `open` in card order; a new `open` card never pre-empts work in progress.

**Creating a stream:** stream note from `doctrine/templates/Stream Note Template.md`, card into `backlog`; its task notes get `stream: x`; the operator's authorisation publishes `stream/x` from `main` and moves the card to `open`; dispatch starts once that branch is live. No script unless the checklist fails twice.

**Landing** is one action — merge, sweep, promotion conversation, `Execute`, deletion — and the sweep is two-phase. Phase one moves the card to `promotion` only once the merge is verified **per repository** from the note's `Merge evidence:` lines (`- <repo>: <tip-sha> -> <target-ref>`, target defaults to `origin/main`), ancestry-preserving, never squash; an unknown ref or remote failure keeps the stream. The orchestrator then writes the **Promotion** section — a checkbox per candidate, plus a final `Execute`; a candidate is text, not a file, and only knowledge outliving the stream qualifies (kinds and test: `doctrine/templates/Stream Note Template.md`). The operator ticks what stays, then `Execute`; that tick is the agent's go: ticked candidates are applied with the operator present, each destination commit or MR link recorded; unticked ones drop; a candidate edited after ticking needs renewed acceptance. Phase two deletes the stream note, its card and every member task note in one commit, once every ticked candidate is complete, no surviving document references a deleted target, and every stream-owned artifact is gone.

**Note caps.** `vault.toml` owns the configured character caps. `temp/` is
uncapped; the pre-commit hook refuses only staged growth that breaks a cap.

Backlog tasks are browsed in `Backlog.base` (every task note without a stream); the board's `backlog` column holds streams only.

## 6. How agents work

The orchestrator designs and rules **in chat**, records rulings, dispatches and lands; it never reads code to review it. Everything that produces an artifact — code, tests, a note edit, a lookup, a gate run — is dispatched with an **explicit model for the job** (tiers: `doctrine/tasks-and-collaboration.md` → *Dispatch*), never the session's model by inheritance; the orchestrator writes an artifact itself only when the specification would be longer than it.

**Context is the cost.** Minimise large context handovers and maximise the value taken from context already accumulated. The unit of dispatch is the **package**, defined in the task note by the orchestrator: the slice of a task one builder carries end to end, then one reviewer who fixes what it finds, then a fresh cold-delta over the fixes; increments inside it are completeness checks, not agent boundaries. A task is normally one package and splits only where gates or owners are independent. **Every landing report names the model that built and the model that reviewed.** A subagent returns through its own return channel, never a session pane. Keep chat concise, prefer doing to explaining, never narrate the board.

## 7. Design and review gates

**The design assessment matrix** (`doctrine/templates/Review Templates.md` → *Design assessment*) **is mandatory before any mechanism-adding decision** — a store, service, background job, lock, cursor, document format or cross-repo seam — in design sessions and escalation rulings alike: one matrix, fields as rows, decisions as columns, written in chat and copied into the stream note with the ruling. **Re-open rule:** effort L, or 2+ new mechanisms, for an impact an existing store or function already provides — the operator rules before anything is built.

**Pre-build plan review.** Before an increment is dispatched its plan passes a cold reviewer on the strong tier (what it hunts: `doctrine/tasks-and-collaboration.md` → *Build or escalate*), who returns one findings table and never builds or edits; accepted changes go into the notes before the implementer starts.

**Escalation ladder: subagent → orchestrator → operator.** Settled, reversible,
in-scope work is implemented autonomously. A **principle-determined** choice
proceeds unattended, recorded in the stream note so the operator can veto it.
An in-scope, reversible fork the principles leave open is ruled by the
orchestrator in chat and recorded. **Operator-only** decisions — an unmade
architectural or methodological choice; an interface, data-flow, storage,
dependency or algorithm change; anything not cleanly reversible, physical or
outward-facing — are parked as an "Open for the operator" line in the stream
note. Reviews happen in chat; the review link is pasted when it opens and
repeated whenever referred to.

## 8. Routing table

Before starting, read every row that applies; a tracked task always adds Workflow.
An instance may extend this table through the marked `Work` → `Read` table in
`INSTANCE.md`. Its stable route IDs and ordered source links are the sole native
wrapper inventory. Later sources may override only explicit preferences in their
stated scope; prose cannot override an enforced schema or a rule outside it.

| Work | Read |
| --- | --- |
| General writing and editing | `doctrine/Writing Guide.md` |
| Coding, tests, refactors | `doctrine/skills/SKILLS - Coding.md` |
| Architecture, design, any interface change | `doctrine/skills/SKILLS - Architecture.md` |
| Single-source questions, a new module or constant | `doctrine/skills/SKILLS - SSOT and Single Pipeline.md` |
| SSOT in depth (boundaries, reference vs conformance, layer test) | `doctrine/Agentic Documentation System.md` |
| Any tracked task | `doctrine/skills/SKILLS - Workflow.md` |
| Authorization, priority, delegation, review and completion policy | `doctrine/tasks-and-collaboration.md` |
| Notes and vault documentation | `doctrine/skills/SKILLS - Notes.md` |
| Browser UI and frontend | `doctrine/skills/SKILLS - Frontend.md` |
| Literature review, summarisation | `doctrine/skills/SKILLS - Literature Review.md` |
| Academic writing, papers, LaTeX | `doctrine/skills/SKILLS - Academic Writing.md` |
| Figures, plots, presentations | `doctrine/skills/SKILLS - Visual Identity.md` |
| Presenting a review, design or decision | `doctrine/templates/Review Templates.md` |
| Writing a task note | `doctrine/templates/Task Note Template.md` |
| Writing a stream note | `doctrine/templates/Stream Note Template.md` |

## 9. Tools

`vault` is the CLI in `tools/` (`vault --help`); `vault hook install` runs once per clone; its commit gate is a ratchet — it refuses only a staged over-cap note that grew since HEAD.

- `vault move` — moves a card between columns in one git transaction.
- `vault sweep` — the two-phase sweep: to `promotion` on verified merge, deletion on `Execute`.
- `vault hygiene` — the working-space check: precondition before merge, sweep and landing, postflight after. **Blocks:** an edited canonical clone, a worktree on no live stream's branch, any file in `temp/`, a live stream card missing its `stream/x` branch on any listed repo. **Reports for the operator:** `promotion` count and age, backlog notes past the configured reporting age, over-cap notes; `--report-only` never fails.
