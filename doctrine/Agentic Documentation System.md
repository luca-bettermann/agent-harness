Reference architecture for an agentic **documentation** system: where knowledge
and its representations live, with single sources and clean boundaries. This is
the evergreen model, separated from any one deployment. [[tasks-and-collaboration|Tasks
and collaboration]] owns the operating policy on top of it. To instantiate the
system, keep the method here and fill the concrete bindings in `INSTANCE.md`.
Per-craft detail lives in [[SKILLS - Coding]], [[SKILLS - Notes]], and
[[SKILLS - Visual Identity]].

> Status: **skeleton.** Settled components are filled; others are marked `STUB — fill case-by-case`.

## Principle — Single Source of Truth, drawn by boundaries

Every fact, decision, or convention has **exactly one authoritative home**; everything else points back to it. Duplication and drift are the failure mode, and they appear wherever a **boundary** is missing or fuzzy — so the real work is *drawing clean boundaries*. Boundaries are the engine; SSOT is the property that emerges when they're clean.

A thing points back to its source in one of two ways — the distinction that decides how it's protected:

- **Reference (hard link)** — the dependent pulls *from* the source (an import, a backlink). There is one copy; drift is structurally impossible.
- **Conformance (soft link)** — each site independently *embodies* the rule (naming, style, layering). The definition is single but the embodiments are many, so drift is possible and needs an **enforcer** (formatter, linter, review).

Test for whether a rule is *about* SSOT at all: **does it exist to stop the same thing living in two places?** ("Defined once" is trivially true of every rule and doesn't count — anti-drift *purpose* is the discriminator.) Physical safety and when-to-involve-a-human are *not* SSOT by this test; they have no second-home risk.

## The method — five fields per component

Define any component of the system by answering five things. The first four are evergreen and travel to any project; the fifth is the only project-specific slot.

1. **Role** — what knowledge/artifact it owns.
2. **Owns / boundary** — what it owns, and what it explicitly does *not* (and which neighbour does).
3. **Relationships** — how it links to the other components.
4. **Held by** — reference, or enforced conformance (name the enforcer).
5. **`[binding]`** — the concrete instance you fill in per project.

(This is the SSOT method applied per component; the rest of the note is just this template, repeated.)

## Components

### Evergreen knowledge store
- **Role:** the canonical *what & why* — concepts, rationale, design decisions, a thing's role across the system. One concept per unit; survives a from-scratch rewrite.
- **Owns / not:** the *why*. Not the as-built structure (→ Structure docs), not the *how* (→ Code), not work-state (→ Task board).
- **Relationships:** everything links *in*; it links *out* and never restates a neighbour.
- **Held by:** reference (links / backlinks).
- **`[binding]`:** knowledge application, repository, note granularity, and link format; supplied by `INSTANCE.md`.

### Code
- **Role:** the *how* — logic and implementation.
- **Owns / not:** behaviour. Not the *why* (→ knowledge store); not cross-module constants (→ a constants module).
- **Relationships:** imports the single source for shared logic/constants; named (not duplicated) by Structure docs.
- **Held by:** reference (define once, import/call) **and** enforced conformance for style/naming/layering (formatter, linter, import-contracts).
- **`[binding]`:** languages, shared-constant convention, formatters, linters, and import-contract tools; supplied by `INSTANCE.md` and repository instructions.

### Structure docs (as-built)
- **Role:** the *structure as it is now* — each folder's purpose, its modules and how they wire, current state & risks. Tracks the code.
- **Owns / not:** where things are and how they connect, *as-built*. Not the *why* (→ knowledge store), not the *how* (→ Code).
- **Relationships:** one per folder; names modules and links the knowledge store for the why; carries the diagram.
- **Held by:** conformance — updated whenever modules change.
- **`[binding]`:** structure-document names and locations; supplied by `INSTANCE.md` or repository instructions.

### Diagrams
- **Role:** *relationships / topology* at a given granularity. Repo-internal → in the Structure doc; cross-repo + deployment → in the knowledge store (one author).
- **Owns / not:** the wiring/flow. Not per-node identity (→ the structure table), not rationale (→ prose). One home per fact-type inside a file.
- **Relationships:** embedded in the doc whose scope it shows; edge nodes link out.
- **Held by:** conformance — updates with the structure it sits in.
- **`[binding]`:** diagram format and rendering constraints; supplied by `INSTANCE.md`.

### Change history
- **Role:** the *why-we-changed* — how the current state came to be.
- **Owns / not:** change rationale and history. *Nothing* about the present state (that lives in the present-tense artifacts; the source describes the present as if it had always been so).
- **Held by:** reference (the commits *are* the record).
- **`[binding]`:** version-control history; supplied by `INSTANCE.md`.

### Visual identity / branding
`STUB — fill case-by-case.` Expected shape: the single visual spec every output conforms to (a conformance-SSOT), enforced by a shared style module so figures/reports can't drift. Binding ≈ the palette / fonts / plot style.

## Evergreen vs binding — the reproducibility test

The line between "stays in this note" and "fill in per project" is **type vs instance**:

- *Evergreen (type):* "there is a store for evergreen knowledge, one concept per unit, linked not restated."
- *Binding (instance):* "it's this Obsidian vault, with these tags, at this URL."

To reproduce the system elsewhere: walk the components, keep fields 1–4, fill field 5. The faster that's possible, the cleaner the abstraction.
