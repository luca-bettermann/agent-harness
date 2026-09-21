---
type: task
stream:                    # empty in backlog; else the owning stream's name
repos: []                  # participating repos by root folder
blocked:                   # this task's own blocker, never the stream's
handoff_from:              # optional — the scope that requested this deliverable
---

<!-- These fields are the whole contract; front matter is the one membership
authority, so `stream:` must agree with the stream note's `Tasks:` list. Cap: 10,000
characters. Replace stale status in place — never append a session diary. -->

## Scope
<1–3 sentences: the problem, and what success looks like.>

## Success criteria
- [ ] <observable, testable condition>

## Out of scope (optional)
- <explicit non-goal>

## Packages
<!-- The orchestrator slices the task into packages before dispatch; a builder executes exactly
one and never re-slices. One package unless gates or owners are independent. -->
1. **<package name>** — <what one builder carries end to end; the gates it must turn green>
   - [ ] <increment: a completeness check, never an agent boundary>
   Built by: <model, date> · Reviewed by: <model, date> · Cold-delta: <model, date>

## Status and pickup
<current state, the blocker if any, and the files a fresh agent needs to resume;
plus canonical plan, MR and compare links.>
