How a review is structured when it happens in chat. That reviews and their sign-off happen in the conversation, not on the board, is the rule in [[tasks-and-collaboration]] → *Review and completion*; this note is the shape each one takes, so a review lands as a scannable, self-contained digest instead of freeform prose.

Three review types recur across the work lifecycle, one template each. A template is a **ceiling on structure, not a floor**: reach for the full table only when the work warrants it, and drop to a sentence plus a link when it doesn't. Trivial work never enters review at all — it goes straight to `cleanup`.

## Decision / design review

An unmade architectural or methodological choice an agent escalated. The operator picks a direction.

Every decision presentation opens with three parts, in this order, before any
option table (the problem must be understandable before the options are):

1. **High-level context** — what part of the system this concerns and why it
   surfaces now, in plain language.
2. **Technical detail** — only as much as the decision actually needs; never
   more complicated than the choice itself.
3. **Practical example** — a concrete case, code snippet, or config fragment
   showing what the choice changes.

No abbreviations in a decision presentation: spell terms out and gloss every
codename or symbol on first use.

**Decision:** *what must be decided, one line* · **Constraint / why now:** *the forcing context*

| Option | Approach | Pros | Cons |
| --- | --- | --- | --- |
|  |  |  |  |

**Recommendation:** *which option, one-line why* · **Ask:** pick / adjust / need more.

### Design assessment — mandatory for any mechanism-adding decision

A decision that adds a **mechanism** — a store, service, background job, lock,
cursor, document format, or cross-repository seam — carries this table before
it is ruled. Write one matrix with fields as rows and decisions as columns; use
a few words per cell and close with the verdict.

| Field | What goes in |
|---|---|
| Decision | one sentence |
| Impact | what it enables that nothing existing provides, and who consumes it |
| Effort | S / M / L (one sitting / one day / multi-day), repos touched, increments |
| Mechanisms added | count them by name — the list *is* the debt |
| Standing debt | what must be maintained for ever (schema, cursors, migrations, fixtures); what dies |
| Resolve-instead alternative | at least one "compute it from an existing store" or "reuse X" option, with its effort and debt — see [[SKILLS - Architecture]] on single source of truth for derived data |
| Verdict | proceed, or **re-open** with the operator |

**Re-open rule:** effort L, or two or more new mechanisms, for an impact an existing store or function already provides → the decision goes to the operator in chat before anything is built; an agent never rules it alone ([[tasks-and-collaboration#Build or escalate]]).

**Worked case:** a stored summary duplicates records already held by the
authoritative database. It would add a format, lock, cursor, and custody rule.
A query over the existing records provides the same result with one derivation
and no stored duplicate. Verdict: re-open and prefer the query unless measured
read cost proves a materialisation necessary.

## Implementation plan review

The settled approach, before build. The operator signs off.

**Implements:** *the settled decision — link* · **Success criteria:** *what "done" means*

| # | Step | Scope / files | Risk | Tech debt |
| --- | --- | --- | --- | --- |
| 1 |  |  |  |  |

**Out of scope:** *what this deliberately doesn't touch* · **Ask:** approve / adjust.

## Result review

Finished, risky or consequential work, presented via its review link — the
card does not move for review. The operator ships or returns it.

**What shipped:** *one line* · **Why it's in review:** *the risk/consequence* · **Links:** *diff / commit / compare*

| Criterion | Expected | Actual | Evidence |
| --- | --- | --- | --- |
|  |  |  |  |

**To verify:** *what the operator should check* · **Decision:** accept → `cleanup` / return → `in progress`.

### On evidence — cite, don't manufacture

Evidence is a **pointer to something that already exists** — a commit, a test-output line, a log excerpt, a screenshot already produced in the course of the work — never a new artifact made to fill the table. If supplying it would take fresh work, that is the signal the criterion was never actually verified during the build; fix *that*, don't do the work just to populate a review. Evidence is **proportional to risk**: a link is enough for most rows, deeper proof only for the genuinely high-consequence ones. And because a result review happens only for consequential work in the first place, the cost is bounded to the few results that already earn it.

## Incident post-mortem (optional)

Not a lifecycle gate, but retrospectives recur with a stable shape. Use when something broke and the lesson is worth keeping.

**What happened:** *the failure, one line* · **Root cause:** *the actual cause, not the symptom* · **Fix:** *what was done* · **Prevention:** *the cause-fix, and where it is now encoded*

---

Deliberately not templatized: open research and strategy exploration. Those are discussions, and a table would strangle them.
