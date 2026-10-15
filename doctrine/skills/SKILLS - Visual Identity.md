Owns legibility, semantic comparison, export and rendered inspection for figures, diagrams and presentations. Writing Guide owns diagram language; Academic Writing and the venue own publication constraints. INSTANCE names the one executable style authority and template owners; concrete palette, font and marker constants belong to that style authority, not here.

## One executable style

Every output consumes the same executable owner for shared visual meaning.

**Covers:** Consistent tokens and source ownership.

**Applying:** Figure scripts import the shared semantic style and save helper.

**Violating:** A figure copies hex codes from doctrine while the executable style uses another palette.

**Detailed rules:**

- Use the style module named by INSTANCE for semantic colors, typography, publication mode and provenance-saving. The executable module is authoritative; no spec-plus-code competing owners.
- Per-figure choices are local within accepted style and venue bounds. A needed new semantic role changes that owner rather than hard-coding a local color.
- Slide and poster templates and domain assignments remain instance bindings. A placeholder is an unresolved owner, not a reason to create another spec.

## Meaning is legible

Visual encodings make comparisons readable without obscuring or exaggerating the evidence.

**Covers:** Honest scales, layout, annotation and visual encoding.

**Applying:** Comparable panels share a fixed scale and colorbar and units; direct labels remove unnecessary legend lookup.

**Violating:** Autoscaling gives equal colors to unequal values or decoration obscures a conclusion.

**Detailed rules:**

- Color carries meaning rather than decoration; neutral structure and restrained accents keep hierarchy clear. Use whitespace, minimal grids and borders and no chart junk.
- Bounded comparable quantities use one shared fixed scale; fitting data is an explicit figure choice. Raw quantities are neutral unless the domain declares a judgment.
- Ordered series use progressions distinct from surface colormaps. Comparable panels share a colorbar; use direct labels when they clarify without covering data.
- Axis labels include units. Markers, line widths and typography come from the style owner; distinguish evidence and claims without inventing competing thresholds.
- Use legible diagram terms and relationship verbs under Writing Guide; preserve domain phase and layer semantics from the instance owner.

## Render before handoff

A visual is handed over only after its actual rendered form has been inspected.

**Covers:** Scientific artifact production and review.

**Applying:** A script exports vector publication output, then its author inspects clipping and reading-size labels.

**Violating:** A successful generator is called a publication-ready figure without viewing the image.

**Detailed rules:**

- Prefer reproducible standard plotting tools for scientific figures; adopt the existing plotting framework and style helper. Avoid a second save and provenance kernel.
- Vector PDF or SVG suits plots and diagrams; raster suits imagery with venue-required resolution. Development export may be PNG; concrete sizes and resolution are style and venue-owned.
- Inspect every generated or modified render with an image viewer at meaningful reading size; check clipping, labels, scales, contrast and export dimensions before handoff.
- Make the result reviewable with its source and evidence. A slide or poster follows the established instance template once its owner is known.
