## Boundary

This skill owns the workflow and craft for browser-facing surfaces — how they are designed, evidenced, reviewed,
and accepted. [[SKILLS - Coding]] owns general implementation craft including
*Projection & display SSOT*; [[SKILLS - Visual Identity]] owns visual
standards; [[Writing Guide]] owns interface prose; each repo's `*_CONTEXT.md`
owns its as-built structure.

## Architecture

- **The server owns every vocabulary and derivation** — apply
  [[SKILLS - Coding]] → *Projection & display SSOT* without exception:
  envelopes not bare ids, no client-held lists, unknown values render loud.
- **Pure view-model / thin DOM**: view logic is pure functions with Node
  tests; the DOM layer only renders. Interaction state folds from data, not
  from scattered flags.
- **[[SKILLS - Coding]] applies to JS unchanged** — the module-size prompt,
  Testing rules, and naming discipline are not Python-only.
- **Gate parity with Python**: JS changes pass lint clean plus view-model
  unit tests on the changed surface — syntax-clean is not a gate.
- **Layout containers own placement; components own content.** Chrome lives
  in docks/strips with shared tokens — no element positions itself with its
  own fixed coordinates.
- **Patterns portable, code not shared** across repos; palettes stay
  per-authority.
- **Fixtures are generated from the real projection or contract-validated,
  with realistic identities** — fake-shaped values (repeated hex, stub
  ports) hide broken links and layouts and are themselves a defect.

## Evidence and review — the gates

Rendered work passes four gates, in order; none substitutes for another:

1. **Design settles in chat**; the settled spec in the card note is the
   implementation source.
2. **The implementer runs a committed headless JOURNEY flow per increment**
   (using the instance- or repository-supplied browser driver): the canonical user journeys across BOTH
   navigation directions and all layouts — chrome mounts/unmounts, scrub
   and seek, window add/swap/close, link hrefs formed and pattern-valid,
   tooltips present on the enumerated element list, no column overlap or
   grid misalignment. **Spec-state PNGs alone are never sufficient
   evidence** — regressions live in the unspecified states and in
   interactions, which stills of specified states cannot show.
3. **The reviewing agent drives the live preview personally** — the full
   journey, interacting, before any human handoff. No preview link reaches
   the operator before this pass.
4. **The operator reviews the rendered result**; acceptance in chat.

Tooltip and affordance completeness is an enumerated checklist asserted by
the journey flow — never a vibe. A claim of "all findings closed" is
verified against the rendered surface, not the diff.

## Standing previews

`INSTANCE.md` names any standing preview surfaces and ports. Update the relevant
preview before a review round; the reviewer's journey runs against it with
realistic data.
