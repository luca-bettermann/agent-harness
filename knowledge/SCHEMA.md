# Knowledge module schema

A knowledge module is a [Karpathy-style LLM wiki](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f): Markdown pages that humans read and agents maintain. Each module's `CLAUDE.md` imports this file and adds its own audience, owner, contribution and publication rules.

## Homes

Durable concepts, decisions and explanations live in a knowledge module. Current code behavior lives in its repository (code, `GLOSSARY.md`, `docs/adr/`), work in the issue tracker, and history in git. Put each fact in the one home whose purpose it serves, and link from everywhere else.

## Pages

- Frontmatter holds only `description`: one line saying what the page answers.
- Sources are linked inline, next to the claims they support.
- A topic is a concept page, never a tag: its backlinks list everything about it, and its summary is readable by agents.
- Each folder has an `index.md` listing its pages with their descriptions; the module index lists the folders. Lint keeps them in step. Queries read down this tree.

## Promotion

Permanent knowledge changes only through a promotion the module's owner (named in its `CLAUDE.md`; the operator by default) accepts while present. An agent proposes the exact change; it never lands it alone.

## Operations

- **Raw sources** (papers, transcripts, exports) stay unchanged in the module's `raw/` folder.
- **Ingest:** a new source or accepted decision updates the pages it affects. Revise an existing page before adding one, and merge or retire superseded content.
- **Query:** start at the index, follow links, and cite the pages and sources an answer uses. An answer worth keeping becomes a promotion proposal.
- **Lint:** find contradictions, stale claims, orphan pages, missing links, index entries out of step with page descriptions, and gaps; report them as proposals.

## Update triggers

| Event | Action |
| --- | --- |
| A project's last issue ("Update knowledge") starts, or a source or decision is accepted | Name the affected pages, or record why no change is needed. |
| A meeting or daily note with action items is ingested | One issue per note, the items as its checklist (an item for another team or person gets its own issue); the checkboxes become the issue link. |
| A durable change is identified | Propose the edit at the existing page, with sources and repaired links. |
| The proposal passes its checks (links, metadata, figures) | Present it to the module's owner for approval. |
| Approved | Land it per the module's contribution rules and publish; link the result back to the issue. |

A failed check returns the proposal to its author; a rejection ends it.
