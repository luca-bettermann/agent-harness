# Knowledge module schema

A knowledge module is a [Karpathy-style LLM wiki](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f): Markdown pages that humans read and agents maintain. Each module's `CLAUDE.md` imports this file and adds its own audience, owner and publication rules.

## Homes

Durable concepts, decisions and explanations live in a knowledge module. Current code behavior lives in its repository (code, `GLOSSARY.md`, `docs/adr/`), work in the issue tracker, and history in git. Put each fact in the one home whose purpose it serves, and link from everywhere else.

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
| A durable change is identified | Propose the edit at the existing page, with sources and repaired links. |
| The proposal passes its checks (links, metadata, figures) | Present it to the operator for approval. |
| Approved | Merge and publish; link the result back to the issue. |

A failed check returns the proposal to its author; a rejection ends it.
