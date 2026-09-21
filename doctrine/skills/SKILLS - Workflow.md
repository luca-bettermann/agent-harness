## Boundary

This skill owns the **work model** — the hierarchy, its board and branch representation, the landing cadence, and the executor protocol — for every tracked task, whatever the craft. Load it alongside the applicable craft skill(s).

`AGENTS.md` owns the funnel, the column meanings, the hard git, worktree and safety rules, and the dispatch rules; [[tasks-and-collaboration]] owns the operator **policy** on top of this model (authorization, priority, delegation economics, review court, reporting) and `vault.toml` owns every **number**; [[Stream Note Template]] and [[Task Note Template]] own note shape; `tools/` owns the **mechanism** (`vault move`, `vault sweep`, `vault hygiene`, `vault hook`) and `vault --help` its invocation; [[SKILLS - Architecture]] owns what gets decided in design; [[SKILLS - SSOT and Single Pipeline]] is the mandatory design/build/review gate for structural work. This note links each of them and restates none.

## The work model

One hierarchy, three representations that never drift, because each fact has exactly one home: **git** holds the artifact, the **note** the why and the pickup, the **board** the state.

| Level | Git | Note | Board |
|---|---|---|---|
| **Work package** | one meaningful commit | a checkbox in its task note | — |
| **Task** | commits on a lane branch, merged into the stream | its own note in a configured task folder, `stream:` naming its stream | — |
| **Stream** | `stream/<x>` off `main`, one MR per repo at completion | the stream note — description, rulings, task list, MR link, merge evidence, promotion | one card, its column the stream's state |

- **The stream is the unit that lands.** Nothing reaches `main` except a stream; a lone task is a **stream of one** and lands exactly the same way.
- **A task is a note, never a card.** Its front-matter fields are defined by
  [[Task Note Template]]; `stream:` is the one membership authority and the
  stream note's `Tasks:` list must agree with it — the sweep refuses on a
  disagreement in either direction.
- **A work package is a checkbox inside its task note**, never a nested note. It earns a note only when it needs its own scope, criteria or pickup — that is, when it becomes a task.
- Design produces notes and rulings, not code: no git artifact, no board state of its own. It happens in chat and is recorded in the stream note ([[SKILLS - Architecture]]).

Design each task so one agent can complete its implementation and self-checks in one working session. Cluster subtasks because they share context, ownership and a coherent outcome, making that context useful throughout implementation. Split independently deliverable outcomes when a task exceeds that scope; keep coupled contract changes coordinated.

Every task leads with simplification: name what can be removed, consolidated or reused before adding mechanisms, applying [[SKILLS - Coding]] across production code, tests, fixtures, validation and workflow while preserving valuable behavioural protection. Review and correction ownership follows [[tasks-and-collaboration#Dispatch]].

## The board

The board file `vault.toml` names is the durable queue a cold agent reconciles from, and it carries **stream cards only**. A card is one line, and nothing else:

```markdown
- [ ] [[Stream x]]
```

- **Column = state**, and the columns are the ones `vault.toml` lists — never renamed, never added to. Position under a heading is exclusive by construction and moves with the same edit that makes the transition. Move a card with `vault move`, so the board and the remote change in one transaction.
- **The stream note is the record.** Description, rulings in force, the task
  list, review link, merge evidence, promotion candidates, and open-for-operator
  lines all live in that note, never on the card or in a second note.
- **Never mirror git state onto the board.** Whether a branch merged is git's fact, read by the sweep from the note's merge evidence; the board holds only state a human sets.
- A stream is created from [[Stream Note Template]]: note, then card in
  `backlog`, then its task notes get `stream: x`. The operator's authorisation
  publishes `stream/x` and moves the card to `open`; dispatch starts once that
  branch is live.

## Branches and lanes

- `main` is the only permanent branch and always deployable. **`stream/<x>`** is cut from `main` when the stream is authorised; it is multi-session but self-retiring — it dies at landing.
- **`stream/<x>` ↔ the stream note's `stream:` value, by name** — a naming contract, greppable both ways, needing no maintained mapping. `vault hygiene` refuses a live stream whose branch is missing from any repo its note lists.
- Every lane — the orchestrator's own included — works in **its own worktree on `lane/<x>/…`**, cut from the stream branch, never on `main` and never on the stream branch itself. Git refuses one branch in two worktrees, so lanes cannot collide.
- Base every branch on the current tip, re-resolved at pickup; report remote SHAs verified with `git ls-remote`.
- **Task work lands on the stream branch by plain merge** after cold review — no MR, no per-task ceremony.
- **One MR per repo, at completion**, from `stream/<x>` into `main`; that MR is the operator's code-review point. Review happens on the MR, announced in chat with its link the moment it opens and repeated whenever referred to; the card does not move for it — the stream note's `MR link:` line is the record.
- **Release before land** wherever the stream ships runnable software: the merge is authorized only after a green release cut from the stream tips.
- **Merge evidence** goes into the stream note, one line per repo — `- <repo>: <tip-sha> -> <target-ref>`, the target defaulting to `origin/main`. Merges are ancestry-preserving, never squash: the sweep verifies the recorded tip is an ancestor of the target, and an unknown ref or a failed fetch preserves the stream.

## Landing and promotion

Landing is **one action**, run to its end in one step.

1. **Merge** each repo's MR, ancestry-preserving, and record its `Merge evidence:` line.
2. **`vault sweep --to-promotion`** — it verifies the merge from those lines alone and moves the card into `promotion`. An unverifiable merge leaves the stream exactly where it was.
3. **The promotion conversation**, with the operator, in chat. The orchestrator writes the **Promotion** section: a checkbox per candidate plus a final `Execute`. A candidate is *text, not a file*, and only knowledge outliving the stream qualifies — kinds and the test are in [[Stream Note Template]].
4. **The operator ticks what stays, then `Execute`.** That tick is the go:
   ticked candidates are applied with the operator present, each destination
   commit or review link recorded; unticked ones drop; a candidate edited after
   ticking needs renewed acceptance.
5. **`vault sweep --execute`** — deletes the stream note, its card and every member task note in one commit, once every ticked candidate is complete and no surviving document references a deleted target. It refuses before deleting anything, so no half-swept state can exist.
6. **Delete the branch** in every repo, remote and local, remove the lane worktrees and their environments, then cut the next stream fresh off the new `main`.

`promotion` is a conversation, never an archive: its card bound and its age limit live in `vault.toml`, and `vault hygiene` reports a stream that overstays either. Git history is the archive; the board holds only live work.

**Hotfix.** A P0 fix is a stream of one — a `stream/<x>` off `main`, one MR, the same landing action, reviewed fast in chat. It is never a shortcut past review or the sweep.

## Branch hygiene and tags

- A branch is deleted the moment it lands one level up — ordinary landing hygiene, not a later chore. A reviewed prefix handed to another task is an interim checkpoint: the task-owned lane remains live while its remaining scope is active; final task integration retires it. Delete only on **provable death**: *merged* = ancestry-checked; *superseded* = content demonstrably shipped by another path, or the programme ruled dead, with the tip SHA recorded in the note first.
- **Ambiguous branches are presented, never guessed.** Never touch a branch that is not yours-and-done — another owner's branch, or one held by a live sibling worktree.
- **Commits are meaningful** — each a coherent, self-contained change with a short descriptive message; never one commit per edit, so history reads as changes rather than keystrokes.
- **Never force-push, never rewrite pushed history.** Pins, release records and provenance name exact SHAs, so a rewrite invalidates evidence. A rebase that conflicts fails loud rather than discarding work; integrate with a merge and say which you did.
- **Tags:** a contract tag lives while any consumer pins it and retires in one sweep when the last consumer moves off · a preservation tag carries a named death event and dies with it · no release tags, the release record owns release identity · no publication tags, a publication pins the contract tag instead.

## Enforcement

Load-bearing rules are mechanisms, not discipline. `vault hygiene` runs as a precondition before merge, sweep and landing, and again as a postflight.

**It blocks** — each finding refuses the action that called it:

- a canonical clone carrying a tracked edit (clones are fetch-only);
- a worktree whose branch belongs to no live stream and is no merge branch;
- any file under `temp/`;
- a live stream card whose `stream/<x>` branch is on no remote of a repo its note lists — or a stream note listing no repos at all.

**It reports**, for the operator, refusing nothing: the `promotion` card count and the days since each of those notes last changed, backlog task notes untouched past the backlog age, and every note over its folder's character cap, with its size (a ratcheted debt, not a landing blocker — [[tasks-and-collaboration]] → *Enforcement numbers*). `--report-only` never fails.

**The pre-commit hook** — `vault hook install`, once per clone — is a ratchet: it refuses a staged note that is over its folder's cap *and* grew relative to HEAD (or is new), naming the note, its cap, and its old and new size; an over-cap note that did not grow, or a deletion, commits cleanly. A guard bites growth, not existence. Every cap, bound and column name is `vault.toml`'s: never hard-code one here, in a note, or in the tools.

## Executor protocol

- **Reconcile on start, on resume and at idle:** pull the vault, read the board, resume `in progress` first, then take `open` work in card order. A new `open` card never pre-empts work in progress.
- Task ownership and review boundaries follow [[tasks-and-collaboration#Dispatch]]; record the continuing builder/reviewer session in the existing task pickup, not a separate registry.
- The task note is the increment record — SHA, exact gate counts, what changed. Replace stale status in place; never append a session diary.
- **Escalate in the note, never around the problem.** A blocked contract or an unmade decision stops the task, fills `blocked:`, and goes up the ladder; never invent a workaround, a fallback or a second path. Continue only genuinely independent work.
- Gates are the ones the task names, run every iteration and reported with exact numbers — "green" without counts is not a gate statement.
- No services, deployments, real runs or hardware unless the task explicitly authorizes them, and never a physical system (`AGENTS.md` → *Hard rules*).
- **Every landing report names the model that built and the model that reviewed.** A report whose builder is the session model is a rule violation, not a detail.

## Review and evidence

- Reviews happen **in chat**: the substance, the evidence and the resolvable links go into the conversation, and "see the card" is forbidden. The card does not move for review; the note carries the links for durability. Shapes: [[Review Templates]].
- Rendered or browser work follows [[SKILLS - Frontend]] → *Evidence and review*; that skill owns those gates.
- Structural review applies [[SKILLS - SSOT and Single Pipeline]] explicitly — authority map, identity-reuse audit, mode-as-data check, deletion ledger, production delta, inverse proof. An unjustified second path is RETURN.
- **Symbol evidence is semantic.** A live-reader or zero-reader claim about a symbol names the reference closure from the repo's language-server-backed reference tool; grep alone is refused for symbols, since it misses aliased imports and re-exports and matches prose. Grep stays the right instrument for wire keys, config strings and cross-language identifiers no language server tracks.
- A change touching a **canonical identity** — contract version, remote, member list, media types, record schema — ships, as review evidence, the enumeration of every reader of that identity (site → authority or witness → verdict), cross-repo readers included, and names which temporal directions it touches (new code × old records, old executor × new artifacts) and where each is guarded. Review refuses without it.
