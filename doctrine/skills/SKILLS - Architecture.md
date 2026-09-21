> System and data architecture: the high-level, hard-to-reverse decisions about
> structure, data flow, storage, boundaries, layering, and schemas. It is
> distinct from [[SKILLS - Coding]], which owns implementation craft. Co-load
> both when a build writes code. [[Agentic Documentation System]] supplies the
> single-source model.

## When this applies
Designing or changing: a system's structure, an interface or cross-module/cross-repo **contract**, **data flow**, **storage/persistence**, a **data model / schema**, **dependency boundaries**, or **layering** — anything with several reasonable approaches + real trade-offs, or not cleanly reversible. Implementation *within* a settled design → just [[SKILLS - Coding]].

## Process
- **Sweep for a settled design before proposing one.** A proposal to design
  something is an addition, so reuse-before-addition governs designs exactly as
  it governs code: search the existing authority first. Designs are ruled in
  parallel lanes — one session's context is never the denominator of what has
  been decided, so never assert that something is undesigned on context alone.
  The sweep is cheap and mechanical: recent `tasks/` git history plus a grep
  for the concept's terms. Design-in-chat with the KB as single source of truth
  means every settled design is findable even when the authoring session kept no
  transcript.
- **Discuss before implementing** — present the viable options, trade-offs, and
  debt impact before a non-trivial change. Do not invent a second option merely
  to fill a table.
- **Architectural changes require approval** — interfaces, data flow, storage,
  authority, dependency direction, and cross-module contracts are design work.
- **Trace every bug to its source first.** A bug is a symptom — decide *why*: a localised defect (wrong logic, typo, off-by-one) or an architectural flaw (a missing abstraction, a contract two sites re-implement, a responsibility in the wrong layer). **Architectural root → stop and escalate; never a local patch** (a workaround leaves the flaw and the bug class returns). **Localised + sound architecture → fix directly.** The same bug in 2+ places, or a fix needing the same special-case in several spots, *is* the architectural signal. Mandatory on every bug.

## Structure & layering
- **Progressive decomposition** — independent phases, each solving one concern.
- **Layer independence** — separate representation, evaluation, optimization; each agnostic to the others. As-built layering lives in `*_CONTEXT.md`; *intended* layering (e.g. core must not import interfaces) is design intent → its KB concept note, backed by `import-linter` in CI where the layers are worth protecting.
- **Polymorphic dispatch, no type switches** — route by type through an
  enum-keyed registry or polymorphic handlers, never `if name ==` or
  `isinstance` chains. Adding a variant registers one handler instead of editing
  switches at multiple sites. Generic layers define the seam; applications
  supply domain behaviour at exactly one boundary point.
- **Dependency arrows point at the general core** — a shared capability is a **neutral/general** package others depend on (the dependency root); lab/domain specifics live in the **consumer** and are injected via the framework's seams (registry / port / interface), never baked into the general package. Importing a general capability is fine (consumer → core); the *bleed to avoid* is a general package depending on a specific one (core → consumer). Decide by the arrow direction + where the specifics live, not by which repo is "bigger".
- **One kernel, several interfaces** — CLI, API, UI, and automation adapt one
  application workflow. They never form parallel pipelines.
- **Facts, policy, and views are separate** — measure facts once, apply policy at
  the owning boundary, and derive presentation without feeding it back as truth.
- **Authority is explicit** — host, instance, release, device, and user-owned
  state are examples of scopes, not special cases. Each state and mutation has
  one owner; dependencies point toward that owner. The ownership test: a
  managing layer owns exactly the artifacts its own operations consume or
  produce; everything else belongs to the managed thing.
- **Lifecycle is a contract** — state-changing operations expose preflight,
  commit, postflight, interruption behavior, and cleanup. Read-only operations
  never acquire hidden mutation powers.
- **Identity is exact** — immutable artifacts and acceptance evidence bind every
  input that can change meaning. Never infer compatibility from one convenient
  field or offer a fallback that weakens the contract.
- **Cross-version boundaries get one gate** — independently shipped artifacts
  meeting across versions use the compatibility rule named by `INSTANCE.md` or
  their owning contract. Within one co-pinned artifact, an additional gate is
  ceremony.
- **Era-correctness** — an artifact is interpreted by its own era's code:
  builders/loaders ship *with* the thing they understand (its bundle or image);
  a manager never runs interpretation logic from its own checkout against a
  differently-pinned artifact. Rebuild-from-pins beats compatibility readers;
  git history is the archive for anything older.

## Data & storage (SSOT)
- **Single source of truth — write once, apply everywhere.** Every concept/constant/decision has exactly one home; everything else references it ([[Agentic Documentation System]]). Code/constants are covered by SSOT; beyond that, define formats/contracts once, apply uniformly. This reaches derived data: a transform, aggregate, join or projection over data the system already holds is a view computed on read by one function over the existing stores; storing it is a second home — unless recomputation at read time is too expensive or impossible, in which case the function stays the single definition and the store is declared as its materialisation with a rebuild-equals-stored guard. *Example of applying it:* a per-source record count, where the store already holds the records — a stored count is a second source that drifts the moment a record lands late or is redelivered, and it brings a lock, a cursor and an ownership rule with it; the count is a query, and only a query whose cost is prohibitive at read time earns a declared materialisation.
- **A cross-boundary fact is SSOT-governed too** — a fact that crosses a repo boundary is SSOT-governed like any other: it lives as a shipped artifact of exactly one repo (contracts package, schema file, generated constant) that the other side reads — never re-typed. Every cross-boundary design names each such fact and its carrying artifact; "both sides know it" fails review.
- **Author associations where the information is richest** — record an unambiguous authoring-time fact *there*; don't flatten it and re-derive it at runtime with tolerances. Runtime reconstruction of authoring-time knowledge precedes a bug class.
- **Normalize the source, denormalize the view** — the SSOT *store* is normalized: each fact once, **record changes not full state** (recompute stores inputs; defaults are a time-indexed changelog; per-dim params are change-logs), resolved to complete form via shared logic built once. *Complete/denormalized* representations exist **only as derived views** for visualization/query (Superset, a wide pivot, a search index) — regenerated from the source, never authoritative. A derived view / index / mirror / cache is **not** an SSOT violation: the source stays minimal *and* self-contained (normalized + a resolver still carries the logic, not the duplication) and keeps backups light; the view is disposable.
- **Precedence is per-data-class, not global** — which tier is authoritative (local-first vs remote-first; source vs derived mirror) is decided per data-class by its mutability + use: editable/operational data → its live store (remote-first); an immutable per-record snapshot → its frozen store; a derived view → never authoritative. One framework, opposite precedence per class is fine.
- **Propagate, don't shim** — don't soften a breaking change with a compatibility
  layer; make the clean change and bring dependants up to speed. The change is
  architectural, so settle it first, then file one handoff per affected
  repository owner. `INSTANCE.md` names the dependency-map authority.

## Interpretability & enforcement

- **A system is only as safe as it is understood.** Hidden complexity is a
  defect even when correct. Keep integrity and physical-safety guards
  structural; make policy guards explicit and visible instead of hiding them
  inside another action.
- **Simplicity is a design target, not a byproduct.** Simpler is easier to understand, and easier to understand is safer — the chain runs through simplicity, so pursue it directly: the simplest structure that does the job, and complexity only where it earns its place for a named reason.
- **Rules live where they can be seen.** A declaratively expressed constraint (a type, a schema CHECK, a grant, a structural bound) documents itself and has no moving parts. Enforcement that runs as process is judged by what its user must simulate at the moment of use: acceptable at an explicit, named action, or entirely off the human's plane (e.g. CI), failing loud with the next step to take; a defect when it runs implicitly inside another action or continuously in the background. Corollary: an action either changes state or reads it, and its name says which.

## Design review

Design happens in chat, not on a design-stage card. Use a compact decision table
(`# | decision | effect | simplicity | debt`) only for actual choices, followed
by an honest net assessment. The accepted implementation plan is written once;
executor cards reference it, and evergreen decisions are distilled to their
owning notes. Rejected alternatives get one sentence each. A worker escalates an
unmade design choice through the orchestrator in plain language.

Two classes of in-chat decision:

- **Principle-determined** — the core principles and skills already point one
  way. State the ruling and its one-line ground in chat and proceed without
  waiting for confirmation; it is still recorded in its owning note and stays
  veto-able. Escalate instead when principles conflict or real doubt remains.
- **Genuinely open** — principles and skills do not make the choice
  unambiguous. Present it with the decision shape in [[Review Templates]]
  (high-level context first, no abbreviations) and wait for the pick.
- **Mechanism-adding decisions carry the design assessment.** Any decision that
  adds a store, service, background job, lock, cursor, document format, or
  cross-repository seam is assessed with [[Review Templates#Design assessment — mandatory for any mechanism-adding decision]]
  before it is ruled. A re-open verdict belongs to the operator.

The classes also govern absence: a principle-determined
choice never blocks unattended work — make it, record it in the owning note,
and report it at the next sync for veto. Only a genuinely open fork holds for
the pick; work it doesn't block continues.

When unsure which class a decision is, present the template — misclassifying
toward silence is the expensive error.
