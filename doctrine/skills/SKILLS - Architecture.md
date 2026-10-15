Owns system decomposition, data flow and storage, ownership scopes, lifecycle and understandable enforcement. [[SKILLS - Interfaces]] owns published crossings, versions and verification; [[SKILLS - SSOT and Single Pipeline]] owns the one-authority gate; [[SKILLS - Coding]] owns implementation. Authorization and design review process live in [[SKILLS - Work]].

## Independent concerns

Components separate responsibilities that change for different reasons.
**Covers:** Structure, layers, dependency direction and domain membership.
**Applying:** Representation, evaluation and optimization have distinct change reasons; a small domain decision has one plain dispatch owner.
**Violating:** A generic core imports domain behavior, or a registry is added just to replace a two-case conditional.
**Detailed rules:**
- Decompose independent phases by responsibility. Separate facts, policy and views; presentation never feeds back as truth.
- Intended layering lives in its concept and as-built wiring in context. Published dependency and extension-point rules follow Interfaces.
- Define categories with objective, testable membership facts and exercise adversarial counterexamples from the real inventory. Do not invent exceptions to rescue ambiguous categories.
- Use one dispatch owner. A closed small set may use a clear conditional; extensible variants use the existing framework’s seam. Choose the smallest design, not a mandatory registry or polymorphism engine.
- Before proposing a design, search settled authority and current task rulings. One session’s context is not proof that a design is absent. A bug repeated across sites or needing duplicated special cases signals wrong ownership; settle the source design before building a workaround.

## Explicit state and lifecycle

Every mutation has an owner and an explicit lifecycle through interruption and cleanup.
**Covers:** Mutation ownership, interruption and cleanup.
**Applying:** An operation declares when ownership changes and how interruption resumes or cleans up, using the existing lifecycle owner.
**Violating:** A manager mutates a managed component’s unrelated state, or read-only status secretly cleans it.
**Detailed rules:**
- Every state and mutation has one owner. A managing layer owns artifacts its operations consume or produce; other artifacts remain with the managed thing.
- State-changing operations declare preflight, commit, postflight, interruption and cleanup. Read operations remain read-only and name the states they can observe.
- Use existing lifecycle actions before adding leases, retry workers or storage. Ownership changes only at a declared event; retained evidence carries the owner through delays.
- Admit a crash recovery mechanism for an observed failure, not a hypothetical one. Where the existing refusal exposes a rare accepted ceiling, record that limit without adding machinery.
- Physical-system triggering remains the root hard limit; domain safety invariants stay with their device or contract owner.

## Derive before storing

Derived facts retain one definition, and storage is added only when recomputation cannot serve the requirement.
**Covers:** Data models, associations, precedence and materialisations.
**Applying:** One query computes a record count; a costly measured query gets a declared materialisation with rebuild equality.
**Violating:** A stored count adds its own lock and cursor, or known author associations are flattened then guessed from runtime tolerances.
**Detailed rules:**
- Store each source fact once. A transform, join or projection over held facts is computed on read by one function. Measured prohibitive read cost or impossibility can justify a declared materialisation of that same function with rebuild-equals-stored protection.
- Record associations where information is richest. Do not discard an unambiguous authored relation and re-infer it later.
- Normalize authoritative stores; changes rather than repeated full snapshots suit mutable histories. Denormalized views, indexes and caches are disposable derivations, never independent authorities.
- Choose precedence per data class: operational editable data has its live owner, an immutable record snapshot its frozen owner, derived mirrors never win. No global local-first or remote-first switch overrides these distinctions.
- Do not invent storage formats, identities or compatibility paths where an existing owner can answer the question. Apply the SSOT map and deletion ledger.

## Understandable constraints

Operators can see what constrains an action and understand why it is allowed or refused.
**Covers:** Simplicity, adoption and visible enforcement.
**Applying:** A typed bound or existing declarative constraint prevents invalid construction and names refusal.
**Violating:** An implicit background guard repairs state during a read or a custom subsystem duplicates a mature tool.
**Detailed rules:**
- A system must be understandable to its operator. Simplicity is a design target; every mechanism names its consumed requirement and simplest alternative.
- Apply [[AGENTS#2. Global principles|Minimal design and Adopt before build]] at subsystem and infrastructure scale: price the mature framework before keeping custom infrastructure. Coding’s local stdlib reuse order never justifies replacing that framework with a hand-built subsystem.
- Prefer structural constraints: type, bound, schema or config. A process guard is visible at a named action or owned CI check, fails loud and states the next action.
- An action either reads or changes state and its name says which. Preferences do not justify bespoke enforcement. Mechanism-adding decisions use the design assessment through Work.
