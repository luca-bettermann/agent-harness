# Knowledge module schema

A knowledge module is a [Karpathy-style LLM wiki](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f): Markdown pages that humans read and agents maintain. Each module's `CLAUDE.md` imports this file and adds its own audience, owner and publication rules.

## Homes

Durable concepts, decisions and explanations live in a knowledge module. Current code behavior lives in its repository (code, `GLOSSARY.md`, `docs/adr/`), work in the issue tracker, and history in git. Put each fact in the one home whose purpose it serves, and link from everywhere else.

## Pages

- Frontmatter holds only `description`: one line saying what the page answers. Indexes are generated from it.
- Sources are linked inline, next to the claims they support; a page's source count is derived from those links.
- A topic is a concept page, never a tag: its backlinks list everything about it, and its summary is readable by agents.
- Each folder has an `index.md` listing its pages; the module index lists the folders. Queries read down this tree.

## Promotion

Permanent knowledge changes only through a promotion the operator accepts while present. An agent proposes the exact change; it never merges it alone.

## Operations

- **Raw sources** (papers, transcripts, exports) stay unchanged in the module's `raw/` folder.
- **Ingest:** a new source or accepted decision updates the pages it affects. Revise an existing page before adding one, and merge or retire superseded content.
- **Query:** start at the index, follow links, and cite the pages and sources an answer uses. An answer worth keeping becomes a promotion proposal.
- **Lint:** find contradictions, stale claims, orphan pages, missing links and gaps; report them as proposals.

## Update triggers

| Event | Action |
| --- | --- |
| An issue completes, or a source or decision is accepted | Name the affected pages, or record why no change is needed. |
| A meeting or daily note with action items is ingested | Create one issue per item in the owning team, and replace the checkbox with the issue link. |
| A durable change is identified | Propose the edit at the existing page, with sources and repaired links. |
| The proposal passes its checks (links, metadata, figures) | Present it to the operator for approval. |
| Approved | Merge and publish; link the result back to the issue. |

A failed check returns the proposal to its author; a rejection ends it.
