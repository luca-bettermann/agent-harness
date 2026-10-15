Mandatory authority and semantic-path gate for changes to state, identity, derivation, persistence, orchestration or presentation. [[SKILLS - Architecture]] owns design choices; [[SKILLS - Interfaces]] owns published crossings; [[Review Templates]] owns evidence shapes; [[Writing Guide]] owns their prose.

## One authority

An authority map exposes competing definitions before implementation adds another.
**Covers:** Fact ownership and semantic implementation.
**Applying:** A catalog owner computes eligibility and serves typed meaning; consumers adapt it.
**Violating:** Two stores or projections independently define the same fact because they update at different rates.
**Detailed rules:**
- Before building, map the canonical fact, owner, producer, semantic derivation, persistence, served projection and consumers. Apply the root single-source principle to this whole path.
- Multiple producers, folds or projections for the same meaning require distinct authority or failure-domain proof; storage format or update rate alone does not supply it.
- Domain vocabulary, eligibility, identity, lifecycle state and refusal meaning are typed facts derived at their owner. Display and fixtures never reconstruct truth from labels, paths, timestamps or filenames.

## Reuse before adding

New concepts are justified only by a question that existing authorities cannot answer.
**Covers:** Existing identities and deletion-led design.
**Applying:** A missing consumer uses the existing identity rather than adding a second generation ledger.
**Violating:** A familiar new worker, version or digest is added before enumerating the concepts already answering the question.
**Detailed rules:**
- Before an identity, version, digest, state machine, catalog, endpoint, worker or projection, enumerate adjacent concepts; name the new unanswered question and propagation and validation sites; repair an existing incomplete consumer first.
- Record the paths removed, the concepts reused, any new concepts and why existing ones cannot serve, and the expected production delta. Unavoidable new responsibilities justify growth explicitly.
- A consolidation that grows logic without a consumed responsibility is a finding. Test and fixture growth may preserve a shrinking production kernel; classify it separately.

## One semantic fold

Equivalent modes share their meaning even when different adapters acquire their facts.
**Covers:** Modes, adapters and served projections.
**Applying:** Live and replay acquire differently but apply the same retained-event fold; a browser renders `id`, `label` and `tone` envelopes.
**Violating:** Two modes each infer lifecycle meaning, or a UI keeps its own vocabulary and eligibility ladder.
**Detailed rules:**
- Equivalent variants default to mode data in one contract and state machine. Separate semantics or failure domains may justify separation; acquisition or timing alone never creates another definition.
- Adapters for different external systems or crash boundaries may remain separate while sharing typed meaning and fold. A safety supervisor can outlive a run without re-owning its state.
- Serve display envelopes such as `id`, `label` and `tone` or `label` and `enabled`; clients render them. A one-way display mapping over stable IDs needs a loud unknown fallback and a key-set subset witness, never a domain policy map.
- Product policy and measurement semantics remain actual decisions; SSOT does not decide time versus distance or retention policy. Once settled, implement one meaning.

## Evidence that can refuse

Review can reject a second authority and states exactly which evidence supports its conclusions.
**Covers:** Review evidence, inverses and limits.
**Applying:** An authority map names a testable bypass; a source-only report leaves runtime acceptance open.
**Violating:** A missing live system is “fixed” by a fallback or a grep-only claim declares zero readers.
**Detailed rules:**
- Review names the canonical owner and fold, explains mode representation, checks consumer logic and identity reuse, and reports deleted paths, production delta and inverse evidence. Missing answers or an unjustified second path produce RETURN.
- Inventory the semantic denominator independently; use Coding’s reference evidence. Demonstrate a meaningful guard fails when authority is bypassed; design-only work names the precise falsifier.
- Design evidence names the map, alternatives, assumptions and falsifier. Source evidence inventories owners, readers and contracts. Test evidence establishes behavior and inverses. Live verification requires authorized checks of the environment needed for the claim.
- Never invent live proof or require unauthorized access; lower evidence can approve design while higher acceptance remains open. Verification environment and ownership follow Interfaces.
- Record task-specific authority map, deletion ledger, classified delta and inverse in the existing task build and review evidence; link this skill rather than copy its checklist.
