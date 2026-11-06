# Knowledge pages carry only a description; topics are pages, not tags

Following the Karpathy LLM-wiki pattern, queries start from an index that lists every page with a one-line summary, so each page's frontmatter holds only `description`, and indexes are generated from it. Tags were mostly duplicating folders or drifting keyword lists; a topic becomes a concept page instead, whose backlinks list everything about it and whose summary agents can read. Sources are linked inline, so their count is derived rather than maintained.
