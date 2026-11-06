# Cheat sheet

What you type. Skills marked † only run when you call them; the others also load by themselves when they fit.

## Plan a project

| Command | Does |
| --- | --- |
| `/wayfinder` † | Maps a large, unclear piece of work as decision issues |
| `/grill-me` † · `/grill-with-docs` † | Interviews you until a plan holds (the second also writes ADRs and glossary) |
| `/to-spec` † | Writes the conversation up as the project description |
| `/to-tickets` † | Splits it into issues with blocking links; the last is "Update knowledge" |
| `/triage` † | Sorts issues that arrive from outside this flow |
| `/to-questionnaire` † | Turns an open question into questions for someone else |

## Build

| Command | Does |
| --- | --- |
| `/implement-spec` † | Runs the project: one agent per unblocked issue, merges into `project/<slug>`, one review at the end |
| `/implement` † | Implements a single piece of work |
| `/prototype` | Throwaway mock-up or sketch to agree a design first |
| `/tdd` | Test-first build of a feature or fix |
| `/diagnosing-bugs` | Debug loop for hard bugs and slowdowns |
| `/code-review` | Reviews a branch against our rules and the spec |
| `/improve-codebase-architecture` † | Finds structural improvements, then grills through them |
| `/wizard` | Script that walks you through steps only a human may do (hardware, credentials) |

## Knowledge

| Command | Does |
| --- | --- |
| `/ingest <note>` | Files a note or source into the wiki; its action items become one issue |
| "query: …" | Answers from the wiki with sources; a good answer becomes a page proposal |
| "lint the wiki" | Lists contradictions, stale claims, orphans and gaps |
| `/research` | Researches a question from primary sources into a Markdown file |

## Sessions

| Command | Does |
| --- | --- |
| `/handoff` † | Writes a handoff so another session can continue |
| `/retro` † | Retrospective on a session |
| `/wait-what` † | Asks the agent to re-explain its last message |
| `/teach` † | Teaches you a concept in this workspace |
| `/ask-matt` † | Suggests which skill fits |
| `/compact`, `claude -c` | Shrink or resume a session; AGENTS comes back by itself |

## Maintain the harness

| Command | Does |
| --- | --- |
| `./install.sh [INSTANCE.md]` | Installs or updates this account (Claude Code and Codex) |
| `git subtree pull --prefix=upstream https://github.com/mattpocock/skills.git main --squash` | Updates Matt's skills after review |
