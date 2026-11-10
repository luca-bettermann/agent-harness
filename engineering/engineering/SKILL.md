---
name: engineering
description: Engineering rules beyond AGENTS. Use for any change to code, tests, CI or configuration, and for reviewing or designing them.
---

- **Gates.** A gate is any condition that refuses a start, stops a run, drops data or marks a device not ready. Only an operator ruling, cited in the commit, or physical safety at the device owner may add one; without that it becomes a question to the operator. Missing, stale or unproven input is reported, as a warning or a record marked incomplete, and never stops work by itself.
- **Dependencies between repositories** go only through published versions: a declared compatible range plus an exact lock. A release pins one known set of exact versions.
- **Decisions.** In an interactive session, settle each open decision with the operator (`grilling`). In an autonomous session, decide local, reversible choices yourself and note them in the change; post a hard-to-reverse one as a comment on the issue with a recommendation, and keep working on everything that doesn't depend on it.
- **Self-correction.** A principle violation in files the change already touches is fixed in the same change. One elsewhere, or a fix that would materially grow the change, becomes a Backlog issue in the owning project, linked to where it was found.
- **Waits end on a result.** Play the CI jobs your change needs and wait for them; a turn never ends while jobs you need are unplayed or running. A project branch receives only work whose required checks are green.
- **Tests.** Each boundary has one shared test harness, built from the real code on both sides and reused by every test that crosses it; a side that can't run in a test is a minimal fake of its published contract. Use the smallest real input that still shows the failure; no test job runs a full-scale dataset. A test stays only when its benefit clearly exceeds its cost in code and run time; a job over the installation's time budget gets smaller inputs, never a longer timeout. Golden files change only through a ruled regeneration that names the fields allowed to differ; everything else must still match.
