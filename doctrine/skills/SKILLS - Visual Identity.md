## Boundaries & Sources

Visual identity's application of [[Agentic Documentation System]]: it's a **conformance-SSOT** — the identity is defined once here, and every output *conforms* to it via a shared style module, never by re-specifying colours per script. The single source is this spec + the style module; the enforcer is "import it, don't hardcode."

[[Writing Guide]] owns general diagram labels and relationship language; this
skill owns their visual treatment.

| Artifact | Single home | Held by |
| --- | --- | --- |
| Palette — colours + semantic roles | the Core Palette (below) | **enforced** conformance — import from the shared style module, never hardcode hex |
| Figure standards — fonts, spacing, gridlines | this skill | conformance — a shared matplotlib style / helpers |
| Per-figure choices | the figure's own script | local, within the standards |

## Scope

This skill applies to: figures, diagrams, plots, and any other visual output for papers, posters, presentations, and reports. The goal is a coherent, recognizable visual identity across all publications.

**Workflow:** After generating or modifying a plot, inspect the rendered image
with the available image viewer and make it reviewable before handoff.

**Design principles:**
- Clean and minimalistic — no chart junk, no decorative elements
- Color is used deliberately to carry meaning, never for decoration
- Grey/blue/green tones dominate; red and yellow are accent-only
- Large negative space, minimal gridlines, no unnecessary borders
- Inspired by 3blue1brown's clarity and restraint, adapted for white-background academic papers

---

## Core Palette

Three spectrums (Zinc, Steel, Emerald) plus two accent colors (Red, Yellow).

### Zinc — neutral / structural

The default for anything that doesn't carry semantic meaning: axes, text, gridlines, borders, diagram backgrounds.

| Stop | Hex       | Role                              |
| ---- | --------- | --------------------------------- |
| 50   | `#FAFAFA` | lightest background fill          |
| 100  | `#F4F4F5` | diagram box fill                  |
| 200  | `#E4E4E7` | gridlines, light borders          |
| 300  | `#D4D4D8` | dividers, secondary borders       |
| 400  | `#A1A1AA` | annotations, secondary text       |
| 500  | `#71717A` | axis tick labels                  |
| 600  | `#52525B` | axis labels, body text in figures |
| 700  | `#3F3F46` | titles, emphasis text             |
| 800  | `#27272A` | dark structural elements          |
| 900  | `#18181B` | near-black, highest contrast      |

### Steel — primary / data / information

The primary color for data representation: lines, fills, bars, flow arrows, the "data layer" in architecture diagrams.

| Stop | Hex | Role |
|---|---|---|
| 100 | `#D6E4F0` | light fill, background tint |
| 300 | `#8BB0CC` | medium fill, area charts |
| 500 | `#4A7FA5` | **primary data color** — lines, bars, scatter |
| 700 | `#2D5F85` | dark emphasis, text on light bg |
| 900 | `#1A3A5C` | darkest, diagram labels |

### Emerald — secondary / performance / positive

Secondary data color, performance encoding, "process layer" in diagrams.

| Stop | Hex | Role |
|---|---|---|
| 100 | `#D1FAE5` | light fill, background tint |
| 300 | `#6EE7B7` | medium fill, area charts |
| 500 | `#10B981` | **secondary data color** — lines, bars, scatter |
| 700 | `#047857` | dark emphasis, text on light bg |
| 900 | `#064E3B` | darkest, diagram labels |

### Accent: Red — warning / negative / alert

Single color, not a spectrum. Used sparingly for: error indicators, negative gaps, "look here" moments, the "prediction/agent layer" in architecture diagrams.

| Hex | Name |
|---|---|
| `#DC2626` | Red |

### Accent: Yellow — highlight / proposed / annotation

Single color, not a spectrum. Used for: proposed points (× markers), highlighted bars, call-out annotations.

| Hex | Name |
|---|---|
| `#EAB308` | Yellow |

---

## Semantic colour assignments

`INSTANCE.md` names the shared style module and any domain-specific semantic
mapping. That module is the executable source of truth: consumers request a
semantic role and never hard-code colormap names or hex values.

- Raw quantities use a neutral scale unless the domain defines a value judgment.
- Bounded quantities render on a fixed shared scale so equal values look equal
  across figures; fitting to data is an explicit per-figure choice.
- Ordered series use progression ramps distinct from surface colormaps.
- Direct labels are preferred when they reduce legend lookup without obscuring
  the data.
- Comparable panels share one scale and one colourbar.

### Data Series (line, scatter, bar)

When a figure has multiple data series, assign in this order:

| Order | Color | Hex |
|---|---|---|
| 1st series | Steel-500 | `#4A7FA5` |
| 2nd series | Emerald-500 | `#10B981` |
| 3rd series | Zinc-400 | `#A1A1AA` |
| Highlight / proposed | Yellow | `#EAB308` |
| Alert / negative | Red | `#DC2626` |

Never use more than 3 regular data series in one plot. If a 4th is truly needed, use Zinc-600 (`#52525B`).

See **Symbols and Markers** below for shape rules (dots for data, crosses for notable points).

### Diagram Elements (architecture, flow, UML-style)

| Element | Fill | Border | Text |
|---|---|---|---|
| Container / background box | Zinc-100 | Zinc-300 | Zinc-600 |
| Data / information box | Steel-100 | Steel-500 | Steel-700 |
| Process / fabrication box | Emerald-100 | Emerald-500 | Emerald-700 |
| Agent / prediction box | — | Red | Red |
| Arrows / connections | Zinc-500 | — | — |
| Labels / annotations | — | — | Zinc-400 |

An instance may refine these roles for its domain in `INSTANCE.md`; it must not
redefine the palette in each figure.

### Symbols and Markers

Two primary marker shapes: **dots** (`o`) and **crosses** (`x`). No triangles, squares, diamonds, or other shapes. Stars (`*`) may be used as a fallback when crosses are visually indistinguishable from surrounding elements.

**Style:** markers should be minimalistic — small, thin, no shadows, no thick edges. They indicate position, not draw attention. Use thin lowercase `"x"` (not filled `"X"`), thin edge widths (0.4–1.2), small sizes.

| Symbol | Matplotlib marker | Meaning |
|---|---|---|
| Dot `o` | `"o"` | Observed / evaluated data |
| Cross `×` | `"x"` | Notable point (proposed, optimum, reference) |

Distinction between different notable points comes from **color**, not shape:

| Context | Shape | Color | Edge | Size |
|---|---|---|---|---|
| Baseline experiments | dot | White | Zinc-700, lw=0.5 | 4-5pt |
| Evaluated (same config) | dot | Zinc-900 | white, lw=0.5 | 4-5pt |
| Data on sigmoid / scatter | dot | Red `#DC2626` | dark red, lw=0.5 | 5-6pt |
| Proposed experiment | cross | Yellow `#EAB308` | lw=1.0 | 8-9pt |
| Known optimum | cross | White | lw=1.0 | 8-9pt |

### Presentation semantics

Use one colour family for one recurring concept and a progression within that
family for ordered phases. Record concrete domain mappings in `INSTANCE.md` and
the shared style module so diagrams, slides, and plots consume the same owner.

### Reference Lines and Grid

| Element | Style |
|---|---|
| Reference / threshold lines | Zinc-300, dashed, α=0.5 |
| Grid lines | Zinc-200, α=0.2 |
| Optimum crosshairs | Zinc-400, dashed, lw=0.8 |

---

## Typography (Figures)

Publication sizes below are defaults. The style module named by `INSTANCE.md`
owns any project override and the switch between development and publication
modes.

| Element | Font | Size | Color |
|---|---|---|---|
| Figure title | default sans-serif, bold | 12-13pt | Zinc-700 |
| Subplot titles | default sans-serif | 10pt | Zinc-700 |
| Axis labels | default sans-serif | 9-10pt | Zinc-600 |
| Tick labels | default sans-serif | 8-9pt | Zinc-500 |
| Annotations | default sans-serif | 7-8pt | Zinc-400 |
| Legend | default sans-serif | 7-8pt | Zinc-600 |

---

## Figure Production

| Context | Format | DPI |
|---|---|---|
| Dev diagnostics | PNG | 150 |
| Publication (preferred) | PDF or SVG | vector |
| Publication (fallback) | PNG | 300 |

The instance style module should switch typography, figure dimensions, and
output formats in one publication-mode call. Its save helper embeds the
provenance fields required by the project without placing them visibly in the
figure.

General rules:
- Preferred plotting library: matplotlib
- Always label axes with units
- Minimal gridlines (α=0.2)
- Remove top and right spines (keep left + bottom only)
- Line weight: 1.5-2pt for data, 0.8pt for reference/grid
- Marker size: 5-8pt for data, 12-16pt for optimum stars
- Use `fig.tight_layout()` to avoid label clipping

---

## Presentations

*Skeleton — add your slide template and layout conventions.*

- Slide template: *link or path to template file*
- Font sizes: title / body / caption
- Preferred diagram tool: *e.g. draw.io, Excalidraw, PowerPoint*

## Posters

*Skeleton — add your poster layout and sizing conventions.*

- Standard poster size: *e.g. A0, 90×120 cm*
- Layout: *e.g. column structure, logo placement*
