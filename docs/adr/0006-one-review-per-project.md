---
status: accepted (trial)
---

# One review per project, a report check per issue

A full review per issue costs a review cycle per agent. Instead, one `code-review` covers the whole project branch before its merge request, and per issue the orchestrator only checks the builder's four-heading report (spec, rulings, principles, deviations) before merging. This is a trial: if defects slip through that a per-issue review would have caught, per-issue reviews return.
