Owns implementation and behavior tests inside a settled design. [[SKILLS - Architecture]] owns structural decisions; [[SKILLS - Interfaces]] owns published crossings and verification ownership. [[SKILLS - SSOT and Single Pipeline]] supplies the authority gate, and [[Agentic Documentation System]] owns context files and comments. Repository instructions own native tooling.

## Minimal implementation

The implementation satisfies every accepted requirement with the smallest clear design that serves it today.

**Covers:** Scope, reuse, deletion and the code-level application of [[AGENTS#2. Global principles|Minimal design and Adopt before build]].

**Applying:** The builder diagnoses the failing path before editing, identifies the whole defect class and its sibling sites, then fixes the shared cause and adds one regression test that catches every affected case.

**Violating:** A patch treats the first symptom before diagnosing its cause, leaves sibling cases broken, or silently drops a difficult accepted requirement to make the diff smaller.

**Detailed rules:**

- Inspect instructions, worktree status and the touched dependency surface first. Implement every accepted requirement; do not silently narrow it. Preserve unrelated edits and prefer a targeted edit when it achieves the same result.
- Reuse the existing implementation first. Within owned code, consider the standard library, an installed dependency and a mature framework before writing new code. This order never justifies rebuilding solved infrastructure from standard-library parts; Architecture owns that subsystem decision.
- Add no speculative abstraction, configuration, scaffold or future reader. Every addition names a current consumer. Never trade readability for fewer lines.
- Change production code, tests, fixtures, validators and workflow together within scope. Remove duplicate responsibilities while preserving behavioral protection; defer unrelated cleanup. Explain necessary growth by the requirement it serves.
- Apply SSOT's authority map, reuse audit and deletion ledger. Trace repeated defects or misplaced responsibilities through Architecture and Work instead of patching consumers independently.
- Preserve integrity, identity, lifecycle and physical-safety guarantees. INSTANCE sets the basic security scope; do not add speculative hardening or security-only gates. A disposable synthetic test token is not a release blocker. Real credentials remain subject to AGENTS.

## Tests prove behavior

A test establishes a named guarantee only when its oracle, inputs and bound environment can expose the claimed failure.

**Covers:** Laws, models, counterexamples, fixtures, inverse evidence and environment fidelity.

**Applying:** A test asserts the expected status for its intended nonempty input set; an inverse changes only the condition whose refusal it claims to prove. An injected clock or an explicit join proves timing or completion without making the verdict depend on host speed.

**Violating:** A check accepts any status except 403, including 500, or an unrelated input error makes an inverse fail before the condition it claims to test.

**Detailed rules:**

- Prefer laws such as roundtrip equality, rebuild equality and idempotence, then stateful models with a named oracle, then behavior counterexamples. Assert guarantees rather than private structure or call order. Use pytest functions, not unittest classes.
- Prove a denominator exists and covers the intended set before applying every-item predicates. Assert the exact expected outcome, including status and refusal meaning. Cover absence, mismatch, interruption, duplicate input and wrong authority within the guarantee that owns them.
- Show the inverse failing before the fix and passing after it. It must fail for the reason it claims; an earlier unrelated refusal is not proof. Use a temporary mutation to show a committed guard bites, then discard the probe.
- Use producer-owned, signature-bound support at crossings under Interfaces. Focused internal tests are allowed when a local guarantee earns maintenance. There is no fixed case quota or blanket public-import rule for repository-local tests.
- Keep one harness per actual boundary. Remove duplicate invariants, permissive mocks, copied generators and source-text or syntax-tree assertions that merely mirror implementation. Do not put a commit SHA in a fixture.
- A test proves only the environment it actually binds. Use the documented interpreter and configuration, selected daemon, reachable address, real file ownership and permissions, and every required binding. Never print credentials. Repair fixture assumptions at their owner; never weaken production policy to make a fixture pass.
- Installed-release witnesses consume shipped archives and committed locks, including the complete dependency and image closure. Mutable checkouts, ignored caches and ambient host tools do not represent an installed release.
- Do not use wall-clock bounds for test verdicts. Preserve timing and completion guarantees with injected clocks, controlled delays, readiness or joins; host speed must not decide correctness. A deadline bounds only the work it owns. Independently timed work keeps its own timeout instead of consuming the caller's budget; deadline semantics belong to the owning contract.
- Await typed refusal or status instead of a blind timeout. Assert public error meaning without obsolete narrower exception pins. Keep byte equality, custody and identity assertions strict when repairing environment faults.
- Exercise every default behavior path. Code defaults apply equally in CI and locally; do not add a CI-versus-local branch to application behavior.
- Local diagnostic runs collect all failures; acceptance candidates remain strict.
- Measure run frequency separately from suite size. Slow native tests remain unless a cheaper witness proves the same guarantee. Interfaces owns verification scheduling.
- Report each touched test and its invariant, with additions and deletions. Duplicate invariants, structural pins and unbound doubles are review refusals. Test count alone proves neither coverage nor debt.

## Readable implementation

Code makes domain meaning, state changes and failure behavior apparent to its next reader.

**Covers:** Functions, classes, constants, configuration, semantic tracing and repository hygiene.

**Applying:** A stateless transformation is a function, while a class keeps state and its lifecycle invariant together.

**Violating:** Dense expressions hide ownership or repeated external strings drift across modules.

**Detailed rules:**

- Favor composition and subclass only for a genuine is-a relationship. Put imports at the top, prefix private helpers with `_`, and avoid mechanical getters and setters. Split responsibilities when they diverge; roughly 500 lines prompts review rather than automatic abstraction.
- Enforce hard constraints through bounds or construction. Fail loudly at integrity, identity, lifecycle and safety boundaries, naming the cause and next action. Missing lifecycle state is never silently null. Warn only when proceeding is safe.
- Import shared vocabulary from a prominent schema or constants module. Namespace external fields so callers reveal their meaning. Algorithm constants used within one module stay at their use site.
- Use domain names and one configuration method per concern. Group related settings in named methods; keep internal defaults inspectable without turning them into user knobs or fallback wrappers.
- Use language-server references and definitions to establish symbol readers, including aliases and re-exports; inspect dynamic paths where needed. Text search locates strings and cross-checks findings but cannot alone prove zero readers.
- Use the repository's formatter, linter, interpreter and type checker. Python must be Pylance-clean; `# type: ignore` is allowed only when the checker is wrong. Repository-native environments override generic defaults.
- Ignore environments, caches, local state, generated output and editor files. Deliberately tracked publication artifacts are an exception. Extend incomplete ignore rules instead of dismissing leaked state. Resource cleanup follows AGENTS.
- Comments and context files follow Documentation System; plots follow Visual Identity. Console output is concise, informative and fixed-width, with debug detail in logs; INSTANCE may link a detailed console authority.
- Show the diff and validation evidence before committing. Git authorization follows AGENTS and the current task.
