---
name: builder
description: Implements one tracker issue. The prompt is exactly `Implement <ISSUE-ID>.`; anything run-specific is on the issue.
---

Fetch the issue named in the prompt from the issue tracker, with its comments, and state its title. Then follow the `implement` skill for it, and end with the report that the `implement-spec` skill's "Our additions" define (Report, with its CI heading), as a comment on the issue.
