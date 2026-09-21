## Boundary

This skill is the mandatory design and review gate for changes that add or
alter state, identity, derivation, persistence, orchestration, or presentation.
[[SKILLS - Architecture]] owns domain decisions; this note checks that each
decision has one authority and one implementation pipeline. [[SKILLS - Coding]]
and [[SKILLS - Workflow]] apply it during build and review.

## Core rule

Every fact has one authoritative owner and one derivation path. Different
interfaces, execution modes, storage adapters, and display surfaces may consume
that fact, but they do not independently recreate its meaning.

Before proposing implementation options, inspect the existing system and try to
extend or delete into its current authority. A familiar new abstraction is not
justified until the existing identities, folds, and contracts have been shown
insufficient.

## Design preflight

Every implementation plan records this map:

```text
Canonical fact:
Owner:
Producer:
Fold / derivation:
Persistence:
Served projection:
Consumers:
```

More than one producer, fold, persistence model, or projection for the same
fact is a design refusal unless a distinct authority or failure domain is
proven. Storage format or update rate alone does not create a new authority.

## Decision rules

### Reuse before addition

Before adding an id, version, digest, generation, state machine, catalogue,
endpoint, worker, or projection:

1. enumerate the existing concepts that answer adjacent questions;
2. state the exact new question none of them answers;
3. list every propagation and validation site the new concept creates;
4. prefer repairing an incomplete consumer of an existing authority.

### Mode is data

Simulation/reality, live/replay, current/historical, interactive/non-interactive
and similar variants default to mode fields within one contract and one state
machine. Adapters may acquire facts differently; they feed the same fold.
Separate implementations require proof of separate semantics or failure
domains, not merely different timing or transport.

### Derive once, serve

Domain vocabulary, grouping, eligibility, identity binding, lifecycle state and
refusal meaning are derived at their owner and served as typed facts. Browsers,
CLIs, fixtures and downstream repos render or adapt them; they do not maintain
parallel maps or reconstruct them from labels, paths, timestamps, or filenames.

### Delete first

Every structural proposal carries a deletion ledger:

```text
Existing paths removed:
Existing concepts reused:
New concepts introduced:
Why existing concepts cannot serve:
Expected production-code delta:
```

A consolidation that grows production logic is a review finding until the plan
names the unavoidable new responsibility. Tests, fixtures and generated
contracts may grow while production code shrinks.

## Legitimate separation

SSOT does not mean one file or one process. Separate adapters are legitimate for
different external systems, update rates, or crash boundaries when they share
one typed contract and one semantic fold. A safety supervisor may outlive a run
process; a live adapter may read an open record while replay reads the persisted
record. Neither separation permits a second definition of identity, state, or
meaning.

Product policy and measurement semantics remain real decisions. The principles
cannot choose whether names are reusable, evidence is retained, or a defect is
defined by time or distance. Once decided, however, they constrain the result to
one authority and pipeline.

## Review gate

A structural review answers each question explicitly:

- What is the canonical fact and who owns it?
- Is there exactly one semantic derivation and state machine?
- Are modes represented as data rather than parallel implementations?
- Did a UI, CLI, fixture, or consumer gain domain logic?
- Was an existing identity or contract overlooked before adding another?
- Which obsolete path, fallback, map, or state was deleted?
- Is the production-code delta negative, or is growth justified by a named
  responsibility or failure domain?
- For implemented behavior, do inverse guards fail when the single authority is
  bypassed or duplicated? For design-only work, is the equivalent falsifier
  stated precisely enough for a later implementation to test?

Missing answers or an unjustified second path produce **RETURN**, not a cleanup
suggestion. A reviewer independently inventories the semantic denominator;
grep locates candidates but does not prove one-path ownership.

## Evidence

The gate applies at every evidence level. Lack of a live system does not weaken
the design rule and does not block a design review; it limits only what may be
claimed as verified. Use the strongest evidence the context legitimately
provides:

| Context | Required evidence |
| --- | --- |
| Concept or design only | Authority map, alternatives, deletion ledger, named assumptions and testable falsifiers. |
| Source available, execution unavailable | Semantic inventory of owners/readers, contract and dependency inspection, static comparison, explicit unverified runtime claims. |
| Tests available | Focused behavioral/structural guards and inverse mutations, then the applicable repository gates. |
| Live system authorized | The source/test evidence plus only the live checks needed to close environment, timing, integration, or hardware claims. |

Never invent runtime evidence, require unauthorized access, or turn unavailable
live proof into an implementation workaround. Mark each conclusion as designed,
source-grounded, test-proven, or live-verified. A lower evidence level may still
approve the architecture while leaving higher-level acceptance explicitly open.

Where implementation and a meaningful denominator exist, use targeted
structural and behavioral guards such as:

- exactly one catalogue, controller, manifest, ownership projection, or fold;
- all supported modes exercise the same implementation through a parameterized
  contract test;
- generated fixtures and docs compare against the real owner;
- retired endpoints, aliases, compatibility maps, and fallback paths are absent;
- a mutation that bypasses the authority or reintroduces a duplicate path fails
  a named guard.

Record the authority map, deletion ledger, production delta and inverse proofs
in the task note's build and review sections. Do not duplicate this checklist in
individual task cards; link this skill and record only task-specific evidence.
