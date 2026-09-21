Workflow and conventions for literature discovery, assessment, synthesis, and
tracking. Use with [[SKILLS - Notes]] for note structure and
[[SKILLS - Academic Writing]] when evidence enters a manuscript.

## Instance bindings

`INSTANCE.md` names the context-document store, per-source note store,
synthesis-note store, reference manager, read-only PDF access, filename
convention, and note template. Treat those as locations and tools, not as a
second definition of this method.

## Sources of truth

- Published sources own their claims. Verify metadata and quote against the
  source itself.
- Per-source notes hold faithful metadata, extracts, highlights, and a short
  relevance statement. They do not hold cross-source synthesis.
- Synthesis notes own comparisons, themes, gaps, and contribution arguments for
  one research question or deliverable.
- Context documents may establish project baselines but can become stale; check
  their declared date or revision before relying on them.

## Access

Use the instance-supplied reference manager and read-only document stores for
the existing library. Use publisher APIs and open scholarly indexes for
discovery and lawful full-text access. Credential values stay outside notes and
prompts.

## Workflows

### Curated-library intake

1. Read and annotate in the configured reference manager.
2. Export or create one per-source note using the configured template.
3. Link the note to every synthesis context that consumes it.
4. Keep source summary in the per-source note; compare and argue only in the
   synthesis note.
5. Record open questions explicitly in the synthesis note.

### Discovery

1. Search authoritative indexes and publisher sources against the stated review
   question.
2. Read the source deeply enough to assess the claims that matter.
3. Check whether a per-source note already exists before creating one.
4. If relevant, add the note, evidence extracts, and links to its synthesis
   contexts. Ask the operator to add any required source file to the reference
   manager.
5. If full text is unavailable, report the title, persistent identifier, and
   reason it may matter. Do not infer findings from an abstract alone.
6. If irrelevant, create no note.

## Per-source notes

A per-source note contains:

- verified citation metadata and persistent identifier;
- the abstract when its reuse is permitted;
- concise evidence extracts or annotations with page locations;
- a one- or two-sentence relevance statement linked to its synthesis context.

Long paraphrases, cross-source arguments, implementation plans, and unlocated
personal critique belong elsewhere.

## Synthesis notes

Use one synthesis note per research question, venue, or reporting deliverable.
State its scope, group evidence into a small number of themes, identify gaps,
and state what the current work adds. Every material claim links back to the
source notes that support or challenge it. Mark submitted or published outputs
as historical records instead of silently deleting them.

## Manuscript integration

- Use the cite key from the verified source record.
- Place citations at the claims they support.
- State why each citation is present; remove citations with no specific role.
- Keep source evidence, synthesis, and manuscript prose as distinct layers.

When a filename, cite-key, or template convention changes, update its single
instance authority and this skill in the same reviewed change if the method also
changed.
