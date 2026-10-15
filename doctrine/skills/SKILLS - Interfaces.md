Owns published boundaries between independently maintained or shipped components, including library APIs, HTTP services, browser clients, protocols, commands and retained artifacts. [[SKILLS - Architecture]] owns system structure. [[SKILLS - Coding]] owns implementation quality, and [[SKILLS - Work]] owns review and landing process. Each contract owns its validation strictness.

## Published interfaces

The producer publishes the meaning and supported surface that its consumers use.
**Covers:** Public APIs, dependency direction, schemas, artifacts and test support.
**Applying:** An application imports a framework's documented API and uses the fixture builder that the framework ships. A changed response is traced through every consumer boundary, including HTTP and browser clients, so the census determines the affected scope.
**Violating:** A consumer imports an internal module or reconstructs the producer's artifact generator.
**Detailed rules:**
- Everything behind a published interface is private to its owner. A public in-process library import is a valid crossing; separate processes are not required.
- Dependencies point toward the more general capability. Domain behavior enters through its published extension point. Apply SOLID at seams, while keeping implementation inside them as simple as the accepted requirement permits.
- The producer ships schemas, semantic constants, artifacts and test doubles. Consumers use that support instead of copying generators or inventing semantic fixtures. Doubles bind to the real callable's signature and declared behavior.
- Name the producer, published surface and complete consumer census when a crossing changes. Trace every boundary, including HTTP routes, browser clients, commands and retained artifacts; repository imports alone are not the census. Reviewing it includes opening the other repository's side. Fix a blocked contract at its owner instead of adding a consumer shim or another reader.
- A producer's CI never clones its consumers. Consumers test against their locked producer and its shipped test doubles. This is an ownership rule; existing migrations must name their remaining consumer-owned witnesses rather than claim the direction is already implemented.
- Each contract declares its validation sites and record strictness. A closed control message may reject unknown fields while a descriptive format permits safely ignored additions. Neither choice is a universal rule.

## Explicit versions

A crossing declares compatible meaning and resolves the exact artifact that supplies it.
**Covers:** Contract versions, dependency locks, deliberate upgrades and artifact interpretation.
**Applying:** A consumer deliberately relocks to version 2, while a version-1 reader rejects version 2 before effects.
**Violating:** CI silently substitutes a sibling head for a committed lock, or a manager reads an old artifact with its own newer loader.
**Detailed rules:**
- Name an exact contract or API version and an exact resolved artifact identity. A digest identifies bytes; a version identifies compatible meaning. These are different questions.
- An addition is compatible only when existing consumers can safely ignore it without losing a guarantee. Such an addition alone requires neither coordinated landing nor joint verification.
- An incompatible change publishes a new version that older consumers refuse. Consumers adopt it deliberately and relock. Propagate that version through the affected set without compatibility shims.
- Cross-root dependencies use pinned Git references, with tags for releases and branches for development, resolved exactly in committed locks. Editable paths stay within one root. Never substitute a foreign worktree or silently relock in CI.
- Artifacts ship the builders and loaders of their own version. Managers invoke those tools instead of interpreting differently pinned artifacts from their checkout. Rebuild from pins instead of adding historical readers; Git retains history.
- For a changed canonical identity, enumerate every reader, including other repositories. Record each reader's authority or witness, verdict and temporal directions, including new code reading old records and old executors receiving new artifacts.

## Verify once where the change is

Each check has one owner and one deciding environment, so verification establishes a guarantee without multiplying its machinery.
**Covers:** Repository checks, changes spanning repositories, release verification and acceptance receipts.
**Applying:** A consumer checks its committed producer lock; a new contract version spanning repositories is verified as one selected set.
**Violating:** A second repository repeats a producer's suite or presents a green pipeline for an earlier head as acceptance of a changed head.
**Detailed rules:**
- Assign every check to the repository whose change and guarantee it protects and name the environment that decides it. Verification machinery must earn its maintenance through the failures it prevents.
- Builders use focused tests and inverse probes for feedback. The exact-head merge-request pipeline is the final receipt; do not run local full suites.
- Verify repositories together when the change spans them. A new version crossing repositories is verified and landed as one unit; use one lane name across that spanning set. Otherwise consumers retain their committed producer locks. Verify the selected shipped set once at release assembly.
- Path selection covers every changed path. A skipped or unavailable required check is not acceptance. State the limit instead of inventing a substitute environment or hidden fallback.
- The existing supply owner provides the selected artifact closure. Warm caches and a second image inventory do not establish reproducibility. Work owns who reviews and lands the evidence.
