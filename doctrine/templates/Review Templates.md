[[SKILLS - Work]] owns when review occurs, who performs it and who accepts it. These shapes are ceilings, not obligatory empty tables. Writing Guide governs the prose; Architecture, Interfaces, SSOT and Coding supply the technical criteria.

## Decision / design review

Open with the high-level problem, only the technical detail needed to understand the choice, and a concrete example. Spell out abbreviations and explain unfamiliar names. Include not building when viable; never invent an alternative to fill a table.

Decision: <the choice> · Constraint: <why it matters now>

| Option | Approach | Benefit | Cost and debt |
| --- | --- | --- | --- |
| <name> | <how it works> | <consumed outcome> | <standing burden> |

Recommendation: <choice and reason> · Ask: <pick, adjust or request more evidence>

### Design assessment — mandatory for any mechanism-adding decision

Work owns this gate and its reassessment rule. Use fields as rows and decisions as columns, including an alternative that reuses an existing owner, computes from an existing store or adopts a mature tool.

| Field | Proposed option | Simpler alternative |
| --- | --- | --- |
| Decision | <one sentence> | <one sentence> |
| Impact | <new capability and its consumer> | <how the requirement is met> |
| Effort | <S: one sitting; M: one day; L: multiple days; repositories and increments> | <effort> |
| Mechanisms | <names and count> | <names and count> |
| Standing debt | <what remains and what retires> | <what remains and what retires> |
| Verdict | <proceed or reassess, with reason> | <reason> |

### Complexity ledger — mandatory for every package, before build and after

For Work's package ledger, add a row for each new module, class, command, route, persisted format, dependency, environment variable or harness engine, and for any change above 50 net production lines. Do not fill rows for ceremony.

| Addition | Benefit and consumer | Simplest alternative | Debt | Direction | Projection and measured delta | Verdict |
| --- | --- | --- | --- | --- | --- | --- |
| <name, files and mechanisms> | <landed caller or accepted plan line> | <not doing it, deleting it, or adopting an existing tool> | <standing maintenance> | <agreement with concept and scope> | <range before; per-repository measurement after> | <keep, simplify, delete or re-project> |

A benefit names what fails without the addition, who observes it and how often. An addition without a consumed benefit is speculative. A foundation may precede its callers only when an accepted plan names those consumers.

Use one classifier for production, tests, test harness, fixtures, contract data, locks and documentation throughout the programme. Link that classifier from the task. Measure moved code across both repositories and credit a deletion to exactly one package. Judge each package with its programme slice, and update the stream's running programme delta at every integration.

Lines measure structure, not density. Savings remove concepts, duplicates, unconsumed elements or custom infrastructure a library replaces. Packed lines and reduced readability are never a cut.

Return unexplained production drift beyond a projected range, a sign flip, an unconsumed addition or an unnamed new mechanism. Judge the reason in context rather than inventing a fixed line threshold. The orchestrator escalates to the operator when programme production materially exceeds summed projections, roughly a fifth or more, or a package that promised a negative delta becomes positive. The proportion is a judgment guide, not an automatic allowance.

Re-price only after attempting the planned cuts. Give the assumption, the requirement demonstrated at file and line, and why the simpler shape fails; the reviewer rules each re-price. Hunt new cuts before allowances. Hold a planned cut only for a concrete requirement or guard it would break, never effort or taste. Principle violations are repaired even when the repair adds code. Work owns routing new findings into the plan. Coding owns test budgets and inverse evidence; Interfaces owns compatibility policy.

## Implementation plan review

Implements: <accepted decision link> · Success criteria: <observable completion>

| Step | Scope, files and owner | Dependency | Risk | Debt and deletion |
| --- | --- | --- | --- | --- |
| <step> | <scope> | <authority> | <failure> | <delta> |

Out of scope: <non-goals> · Plan review: <evidence and verdict>

## One end findings table

Builder: <actual model> · Reviewer: <actual model> · Scope and heads: <exact identities>

| ID | File:line and sibling sites | Defect class, failure and counterexample | Consequence | Owner and fix | Disposition and evidence |
| --- | --- | --- | --- | --- | --- |
| <id> | <source> | <demonstrated failure> | <why it matters> | <owner> | <RETURN, closed or open, with scope> |

Delta verification: <the required fixes checked, consequences and verdict>

## Result review

What changed: <outcome and reason> · Links: <diff, commit and existing evidence>

| Criterion | Expected | Actual and limits | Evidence |
| --- | --- | --- | --- |
| <criterion> | <observable result> | <result> | <existing pointer> |

To verify: <remaining operator checks> · Decision: <accept or return>

### On evidence — cite, don't manufacture

Point to code, test output, logs or rendered evidence already produced in the work. Never manufacture an artifact to fill a table. Missing evidence means the criterion remains unverified; complete the work rather than decorate the report. Depth follows consequence. Review acceptance does not move the card or prove merge and promotion.

## Incident post-mortem (optional)

What happened: <failure> · Root cause: <observed cause or explicit hypothesis> · Fix: <owner and action> · Prevention: <existing owner and accepted limit>

Open research and strategy are conversations, not obligatory tables.
