## Boundaries & Sources

The KB's application of [[Agentic Documentation System]]: it holds the *evergreen what & why*; everything points back by **reference** (`[[backlinks]]`), never restated.

| Artifact | Single home | Held by |
| --- | --- | --- |
| Concept / the why | one KB note per concept | reference — `[[backlinks]]`, never summarise |
| Design decision + rationale | its owning note (concept / `*_CONTEXT.md` / methodology) | reference; supersede in place |
| A note's title | its filename | reference — no `# Title` H1 |
| Hierarchy / grouping | backlinks + name prefix | conformance — naming scheme, never folders |
| Agent lessons & working state | the owning KB home — skills (conduct/process), cards (program state), `*_CONTEXT.md` (repo facts) | conformance — **agent memory is not a knowledge home**: distil durable lessons into the owning skill/note compactly at the moment they're learned; a session's private memory holds at most volatile cross-session pointers into the KB, never individual lesson files |

## Principles

- Knowledge base purpose: **evergreen structural documentation and decision-making only**
- No in-depth process descriptions, no implementation walkthroughs, no content that duplicates what is already in code
- Agents will read these files — keep them concise and high-level
- Only mature concepts belong here — don't document brainstorms or draft ideas without checking with the user first

## Writing Notes

- Follow [[Writing Guide]] for general language, structure, links, and status.
- Write new notes in the knowledge store named by `INSTANCE.md`, using its format.
- **The filename is the title — no redundant H1.** Obsidian renders the filename as the page header, so never start a note with an `# <Title>` line repeating it (it shows as a double title). Begin with the first content paragraph or a `## ` section.
- Use Obsidian backlinks (`[[Note Name]]`) liberally — connectivity is critical
- **Never create new folders** — use backlinks for hierarchy instead
- Keep knowledge-base clean and up-to-date; update notes whenever concepts have materially changed
- **Capture decisions, not just designs.** A note that describes a design records the *why* and the *why-not* (rejected alternatives + reason), so future agents don't re-litigate. **Design decisions are evergreen and live in their owning note** (the concept / `*_CONTEXT.md` / methodology note they concern) — never parked in a task. **Supersede in place:** when a later decision changes things, update the note and remove the stale rationale; leave a one-line breadcrumb only where a reversal is non-obvious. Git history is the full trail (see CLAUDE.md → *Single Source of Truth*).
- **Skill files are evergreen** — state the standard timelessly: no dates,
  attributions, or supersession remnants in the text; git history carries when
  and who. (Task notes legitimately carry dates in status and fix logs.)
- Feel free to remove or restructure docs if appropriate — but ask the user first when in doubt

## Naming Conventions

Notes are organised by prefix, not by folder. Follow the existing scheme:

| Prefix | Domain |
| ----------- | ------- |
| `SKILLS - ` | Agent skill files |
| `Reference - ` | Detailed reference specifications that other notes and skills link to |

`INSTANCE.md` owns any domain-specific prefix table. Do not copy those prefixes
into generic doctrine.

- Check existing notes before creating a new one — extend or rename rather than duplicate
- **Note granularity: a new note is for a standalone concept with real backlink
  gravity.** A ruling, sub-concept, or ownership fact folds into the nearest
  existing concept note as a sentence or short paragraph — never a note per
  ruling; fragmentation explodes the KB exactly like per-lesson memory files.
- If a note spans multiple domains, use the most specific prefix and backlink to related notes

## Updating Notes

- Whenever you have changed or developed concepts that are represented in the knowledge-base, update the relevant notes
- Remove outdated content rather than leaving stale information alongside current content
- **Ask the operator before removing anything substantial** — outdated sections
  are flagged, not silently deleted. A note leaves only once its durable value
  is distilled or promoted to its canonical home; Git is the archive.
- If a note is no longer relevant, flag it for the user rather than deleting it unilaterally
- When consolidating multiple notes on the same topic, present the merge plan before executing

## Research Outputs

- When summarising papers or research, save output to the instance-supplied knowledge store in a relevant note.
- Follow the naming scheme used in existing literature notes (e.g. `Literature Review <Topic>.md`)
- See [[SKILLS - Literature Review]] for summarisation guidelines
