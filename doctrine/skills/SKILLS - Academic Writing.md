Method for papers, reports, and other evidence-bearing written deliverables.
Use with [[SKILLS - Literature Review]] for sources, [[SKILLS - Notes]] for
evergreen knowledge, and [[SKILLS - Visual Identity]] for figures.
[[Writing Guide]] owns the general language and structure used by every deliverable.

## Instance bindings

`INSTANCE.md` owns target venues, language variant, manuscript template,
bibliography style, collaboration host, storage paths, and any project-specific
terminology. Check the current venue's author instructions at submission time;
do not freeze them into generic doctrine.

## Claims and voice

- State what the work does, what the evidence supports, and what remains a
  limitation. Avoid novelty and significance claims that the evidence does not
  establish.
- Keep one spelling and terminology convention within a deliverable, using the
  instance binding or venue rule as authority.
- Remove citation piles that have no claim-level purpose.

## Structure

Choose the structure required by the deliverable and venue. A research article
normally establishes the challenge, positions related work, states the
contribution, explains the method, presents results, and separates discussion
from conclusion. The introduction must make the work understandable without
assuming the reader knows an earlier publication.

Keep the contribution statement explicit and early. Use related work to compare
external evidence; describe the system and prior project work where they are
methodologically relevant. State research questions in the form the venue and
discipline expect.

## Figures

- Every figure answers a specific question and is cited in the text.
- Follow [[SKILLS - Visual Identity]] and the instance-supplied style module.
- Prefer vector output for diagrams and plots; use raster output for images that
  require it and meet the venue's resolution rule.
- Make captions understandable without relying on the surrounding paragraph.
- Keep diagram source separate and reproducible where the document system
  supports it.

## Citations

- Cite at the exact claim supported by the source.
- Verify persistent identifiers, publication details, and cite keys before
  submission.
- Keep a clear reason for every citation.
- Follow the venue's rules for self-citation and anonymous review.

## Revision

Track each reviewer comment to a response and a manuscript change. Produce a
reviewable diff with the instance-supplied document tooling. Preserve the final
response record with the submitted version.

## Submission check

- [ ] Current author instructions checked for length, format, references, and figures
- [ ] Draft-only annotations removed
- [ ] Every citation key resolves
- [ ] Figures meet format and resolution requirements
- [ ] Captions are self-contained
- [ ] Language and terminology match the selected convention
- [ ] Funding, acknowledgements, conflicts, and contribution statements are complete
- [ ] Co-author or reviewer approval is recorded

## Reports

Treat each recurring report as its own deliverable with one current status.
Maintain narrative continuity by linking its predecessor rather than copying
technical detail. Repository documentation and evergreen concept notes retain
their own facts; the report references them. Once submitted, a report becomes a
historical record under the retention policy named by `INSTANCE.md`.
