Owns operating policy and the work model for the operator, orchestrator and agents, from authorization through packages, dispatch, review and landing to retirement. AGENTS owns global principles and hard limits. Interfaces owns verification guarantees; Review Templates owns assessment shapes and measurement rules. Task and Stream Note Templates own schemas. INSTANCE supplies concrete models and transport; `vault.toml` owns bounds, and tools implement them.

## Authorized outcomes

Authorized work advances to its accepted outcome, while decisions needing the operator hold only their dependent work.
**Covers:** Queue order, work representations, escalation and unattended work.
**Applying:** An authorized stream has one card and tasks with observable criteria; an open choice blocks only its dependent package.
**Violating:** A task gets another board card or an unresolved preference takes effect merely because time passes.
**Detailed rules:**
- Track work that must survive the sitting, including deferred, blocked, handed-off, reviewed or multi-session work. Otherwise its output and Git history are the record. State criteria as outcomes.
- The board contains stream cards only, written as `- [ ] [[Stream x]]`. `backlog` means prepared but unauthorized; `open` authorizes spend; `in progress` has active work and review; `promotion` has verified merge evidence and awaits the promotion conversation. Never mirror Git state onto the board. Move cards with `vault move`, so the board and the remote change in one transaction.
- Stream notes own rulings and integration evidence; task notes own scope, criteria, blockers and pickup. Task `stream:` front matter is the membership authority and must agree with the stream's `Tasks:` list in both directions. Clear lifted blockers and replace stale status instead of appending a diary.
- Create the stream note, backlog card and member tasks from templates. Authorization publishes `stream/x` from `main` and moves the card to `open`; dispatch waits for the required branches. Do not script creation unless the checklist fails twice.
- On start, resume and idle, pull the vault and reconcile assigned streams. Resume `in progress` first, then authorized `open` work in project card order. Only the operator preempts active work. Report old backlog notes rather than deleting them for age.
- Complete reversible work whose scope and approach are settled. Escalate from subagent to orchestrator to operator. The orchestrator rules principle-determined choices, including interfaces, storage and effort-L changes, records them in the stream note and reports the ground in chat. Question the requirement first.
- Wait for the operator on genuine ambiguity, changes to an operator ruling or scope, and irreversible, physical or outward-facing actions. Record Open for the operator with default, reversibility, blocked package and date. Time is not an answer; independent work continues.
- Unattended authorization keeps unblocked packages moving in queue order within caps. It never implies hardware, deployment, merges to `main`, host or root steps, or commitments beyond the project's repositories and vault. Land reviewed work with exact-head evidence and keep shared resources healthy. End with landed work, work in flight, recorded decisions, open defaults and pending operator steps.

## Context-led packages

A package retains the context and ownership needed to finish a coherent outcome with continuing builder and reviewer context.
**Covers:** Dispatch units, roles, tiers, caps, continuity and communication.
**Applying:** A builder and reviewer retain coupled context through increments while independent outcomes run in parallel.
**Violating:** Every checkbox spawns an agent, or the orchestrator reads code to perform the review it judges.
**Detailed rules:**
- A task is the tracked note; a package is the dispatch slice; increments are completeness checkboxes. The orchestrator defines packages before dispatch and the builder never re-slices them. Normally a task is one package; split only at independent owners or gates. Commits are coherent changes, not another work level.
- Delegate self-contained work when specification and checking cost less than doing it in the current context. Keep entangled, exploratory or high-risk work in one head. Parallelism follows independent scope and ownership, not repository count.
- The orchestrator specifies, judges, rules, dispatches and lands; it never reads code to review it. Artifact-producing work names an explicit model rather than inheriting one. The orchestrator writes an artifact only when its specification would be longer.
- Builder prompts include AGENTS' rule against killing processes by pattern verbatim. Preview startup records the process handles used for shutdown; a silent sibling session is not presumed dead.
- The builder completes the package and self-checks. The reviewer examines the cumulative result and never edits; the builder fixes findings in its warm context. After two rejected fixes, re-scope the package or raise the builder's tier. Replace a cut-off or full-context agent from the compact specification and current report.
- T1 handles design and plan review; plan-review prompts carry the needed evidence so the reviewer need not read code. T2 handles design, plans, challenging implementation and implementation review. T3 implements. T4 performs mechanical lookups, gate runs and exact-text edits; it never decides or reviews.
- Costs are T1 = 8, T2 = 4, T3 = 2 and T4 = 1. The operator sets a cap per vendor at session start; zero disables that vendor. Sum running agents within each cap, excluding the orchestrating session. INSTANCE maps tiers to models; flag a newer model. Reviews run one tier above the work or at the same tier with higher effort.
- Minimize context handovers and repeated long-context waits. Launch a long gate or background agent as the background command itself so completion notifies its caller. Use its job handle, one wait and bounded output tails, not process-list polling. Write reports incrementally; never paste a whole log into context.
- Record continuing sessions and exact heads in task pickup, not another registry. Build, review and landing reports name actual models and doctrine read. A session-model builder is a violation unless the orchestrator wrote the artifact under the specification-length exception above. Coding owns test evidence.
- Agents use their return channels. Cross-session messages use only operator-connected channels. Questions go to the owning orchestrator; substantial deliverables become tracked work. A recorded `handoff_from:` and cleared approved upstream handoff resume only authorized dependent scope.
- A dedicated implementation session receives its build, gate and landing dispatches; the orchestrator reads reports and records rulings. Client recovery follows INSTANCE.
- Fix or route every principle violation, new cut and plan gap into its owning task plan in the same turn; flag unowned items. Report numbers fixed and routed with owner links, completed work and next steps. Omit routine board narration.

## Proportionate review

Review assesses the complete accepted outcome and verifies its corrections without repeating unchanged work.
**Covers:** Plan assessment, complexity, end findings and delta verification.
**Applying:** A cold reviewer checks a seam-changing plan. The first implementation review covers the complete change, with independent dimensions reviewed in parallel when useful. Findings name each defect class and its sibling sites; later rounds verify the corrections and their consequences.
**Violating:** A reviewer edits production, discovers one sibling defect per round, or repeats a broad review of unchanged work after the builder has fixed the named class.
**Detailed rules:**
- Before build, a seam-crossing or mechanism-adding package receives T1 cold plan review. The reviewer hunts contradictions, open forks, weak guards, authority violations, dependency and ordering errors, and plan drift, returning findings without editing. Record accepted changes before dispatch.
- Before a mechanism-adding decision, use the design assessment in Review Templates. Every package carries its complexity ledger, projected before build and measured after. Reassess effort L or at least two mechanisms for a capability an existing store or function supplies. The escalation rule above decides who rules the result.
- The first end review examines the cumulative implementation broadly. Independent reviewers may cover separate dimensions in parallel; consolidate their results into one findings table with defect class, sibling sites, location, failure, consequence, owner and disposition. The builder corrects each class; subsequent rounds verify required fixes and their consequences. A failed delta remains RETURN. Re-scope substantive change openly. Changed design may need renewed plan review; unchanged checklists do not.
- Apply Coding and SSOT to repository quality and Interfaces to crossings. Review Templates owns measurement, drift escalation and the running programme delta. Retain meaningful inverse evidence and task-specific authority and deletion records.
- Gate reports state exact pass, failure and skip counts, scope and head; green without counts is insufficient. Missing evidence stays explicit. Deliver self-contained review substance, evidence and links in chat; a note is not a substitute.
- Announce a review link when it opens and whenever discussed. Acceptance, verification, merge and promotion are distinct states. Browser work follows Frontend's full live-preview gate.

## Evidence-bound landing

Landing preserves reviewed artifact identity and completes the durable handoff before work state retires.
**Covers:** Branches, merge evidence, promotion and integration.
**Applying:** Related fixes converge before generated locks and fixtures are rebuilt once at integration. The verified head then lands through configured review transport, with ancestry proving its recorded tip before promotion.
**Violating:** Every fix round regenerates locks and fixtures, a direct stream push bypasses review, or only half of a new incompatible version lands.
**Detailed rules:**
- Code streams use `stream/x`, matching the note's `stream:` value. Code lanes use `lane/x/...`, cut from the current stream tip in their own worktrees; never work on `main` or the stream branch. Resolve refs at pickup and verify reported remote SHAs with `git ls-remote`. Root Git rules govern history and knowledge repositories.
- Merge the stream forward when it moves; do not rebase lane history. Keep one merge request per repository per package. If an unlanded lane blocks implementation, a stacked lane may start from its head for build and review only. Accepted stacked lanes merge per repository into one candidate lane for one stream landing.
- Rebuild generated locks and fixtures once at integration after the related fixes have converged, then verify the integrated result. Do not regenerate them in every fix round.
- INSTANCE owns lane transport and release bindings. Each completed code stream has one stream-to-main merge request per repository. Interfaces determines the verified unit; publication alone never proves hardware acceptance.
- Record per-repository merge evidence as `- <repo>: <tip-sha> -> <target-ref>`, defaulting to `origin/main`. Preserve ancestry, never squash. Failed lookups, unknown refs or failed fetches preserve the stream; Git owns merge truth.
- Complete landing as one action: hygiene, merge and evidence, `vault sweep --to-promotion`, promotion conversation, accepted destinations, `Execute`, and retirement. Report partial progress honestly if an external step prevents completion.
- The Stream Note Template owns promotion candidate kinds and the durability test. The operator ticks candidates and then `Execute`. Apply accepted text with the operator present and record destination commits or review links. Changed accepted text needs renewed acceptance; unticked candidates drop.
- `vault sweep --execute` atomically deletes the stream, card and all member tasks only after accepted destinations complete, references are repaired and stream-owned artifacts retire. It refuses membership disagreement before deletion. Promotion is a conversation; Git history is the archive.

## Retire at the owning event

Completion removes disposable resources and obsolete work state when their purpose ends.
**Covers:** Branch death, worktree retirement, hygiene and cap enforcement.
**Applying:** A landed lane loses its branch, worktree and environment; an ambiguous sibling branch stays with its owner.
**Violating:** A hygiene bypass leaves abandoned work or deletes a lane whose scope remains active.
**Detailed rules:**
- AGENTS owns resource and writer limits. Delete branches only on provable death: ancestry proves merge, content demonstrably shipped elsewhere, or the programme is ruled dead with its tip SHA recorded. A reviewed checkpoint does not kill an active lane. Present ambiguous branches to their owner.
- Contract tags remain while consumers pin them and retire when the last consumer moves. Preservation tags name a death event. Release records own release identity; do not create release or publication tags alongside them.
- Run `vault hygiene` before merge, sweep and landing, and afterward. It blocks edited canonical clones, ownerless worktrees, files under `temp/`, and missing required remote stream branches or repository membership. It reports promotion count and age, old backlog and cap debt. `--report-only` never fails.
- Install the existing cap hook once per clone. Its ratchet refuses new over-cap notes and staged growth of over-cap notes; unchanged debt and deletions pass. Legacy cap debt does not block landing. `vault.toml` owns caps, bounds and columns.
- Reuse an existing lane environment instead of creating another for the same lane.
- A P0 hotfix is a reviewed stream of one, not a shortcut past sweep. Remove landed lane environments and worktrees in the same step; subsequent work starts from the new authoritative tip.
