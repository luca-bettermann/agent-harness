Owns top-down audit and simplification of existing code. Architecture, Interfaces and SSOT own the principles applied; Coding owns test quality; Review Templates owns findings and complexity shapes. Instance supplies model routing.

## Requirements before mechanisms

The audit evaluates machinery against sourced requirements rather than treating existing machinery as a requirement.
**Covers:** Scope, authoritative requirements and goals.
**Applying:** The operator defines levels 0–5 and each kept requirement cites an operator ruling or measurement.
**Violating:** An agent-written plan invents a criterion, guard and handling chain, then audits it as a requirement.
**Detailed rules:**
- The operator chooses the start and end levels; the default is 0–5. Starting lower assumes the higher levels are settled.
- Name a source for every requirement: an operator ruling or a measurement. Agent notes or comments alone do not establish a requirement.
- Questions for the operator are an output: domain knowledge can remove the largest machinery. State criteria as goals, never a required evidence path or mechanism.

## Top-down once

Each audit level examines only the scope retained by the levels above it.
**Covers:** Audit level sequence and retained floor.
**Applying:** A redesigned concept is built at its new owner; only retained lower-level code is audited.
**Violating:** Several agents re-audit discarded code or count the same cross-repo deletion twice.
**Detailed rules:**
Finish each level across the whole scope before moving lower. Each level covers what the higher levels retain; its result becomes the next level's floor.

| Level | Ask | Hunt for | Result |
| --- | --- | --- | --- |
| **0 Goals** | What is the system for, and who asked for each requirement? | Requirements without a source; agent-invented chains (goal → criterion → enforcement → failure mode → handling) | Requirement list with sources |
| **1 Concepts** | How should each concept work at all? Enumerate every surface, type, operation, store, record and configuration. | The first rule under *Price the simpler alternative* | Concept census, target designs, operator questions |
| **2 Ownership and size** | Who owns each fact, and how small could each subsystem be for the same requirements? | Second owners, wrong dependency direction, duplicates across repositories | Owner map and a size budget per subsystem |
| **3 Mechanisms** | Does each guard, store, lock, retry or protocol earn its cost? | The remaining rules under *Price the simpler alternative* | Keep, simplify or delete, graded by consequence |
| **4 Code** | Is the kept code lean? | Dead code, wrappers, interfaces with one implementation, hand-rolled standard library | Delete list |
| **5 Tests** | Does each boundary prove its guarantee cheaply? | Example tests instead of laws, structure pins, duplicate builders, committed generated output | Test budget per boundary |

Levels 0–2 examine concepts and owners across repositories; levels 3–5 examine retained scope within each repository. The next target is the retained floor minus new cuts plus approved additions; code moved between repositories counts net. A design must reach its budget or cite the requirement that makes its current size necessary.

## Price the simpler alternative

Every retained mechanism earns its standing cost against the simplest viable alternative.
**Covers:** Concept and mechanism screening and standing debt.
**Applying:** A query replaces a stored mirror; a framework replaces custom infrastructure and its maintenance cost is priced.
**Violating:** A published fixture builder is cut because production does not call it, although consumers need it to test their supported interface.
**Detailed rules:**
- Apply [[AGENTS#2. Global principles|Minimal design and Adopt before build]]: for every subsystem, price an installed tool or mature framework against retaining custom code. Include deleting the requirement when its source allows it. Represent taxonomy as data, derive views through one computation, and expose declared operations through adapters. Producers publish source meaning. Prepare before the run, and skip all visual work when running headlessly.
- For each finding, state its location, consequence, cost, simpler alternative, what would be lost and who consumes it. Offer not building first where that is viable.
- Check that a new store, format or channel retires its predecessor. Keep validation at the owning contract; add crash handling only for an observed failure. Name the operating system, library or tool feature that already provides the guarantee.
- Delete a constant defined as equal to another authority; apply Interfaces when evaluating identities that cross a boundary. Test-only artifacts stay only if they are justified producer test surfaces or cannot be deterministically regenerated more cheaply.
- Bound the generator's volume and time where its guarantee requires it; bounding only the final artifact is insufficient. A later-scope feature is frozen, not extended; delete dead wrappers and abstractions with one implementation where no seam consumer exists.

## Demonstrate the failure

A reported defect is supported by evidence that exposes the claimed failure.
**Covers:** Verified findings and behavioral protection.
**Applying:** A reviewer reproduces the missing-denominator counterexample and keeps the law that protects it.
**Violating:** An unverified lead is labeled a defect or a permanent mutation harness duplicates the real law.
**Detailed rules:**
- Verify a found bug before promoting it to a defect, trace its owner and pattern, and apply owner fixes across confirmed instances. Keep assumptions and new versus known findings explicit.
- Level 5 keeps cheaply proven guarantees, removes structural pins and duplicate builders, and assigns each test its invariant. Coding owns the test-quality rules, not a numerical quota.
- Run the inverse review probe once and discard it; retain the committed behavioral laws. Use the strongest legitimate evidence. When runtime proof is unavailable, limit the claim without weakening the design rule.
- Run enumeration and per-area passes on the standard implementation tier, and synthesis and level 1–2 designs on the strongest tier. The highest-stakes audit design gets a cold review from the other vendor. INSTANCE maps these roles to models. Independent areas may run in parallel under Work; synthesize common concepts before defining packages. Use Review Templates to report decisions.
