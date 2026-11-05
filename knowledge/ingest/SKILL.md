---
name: ingest
description: Ingest a note or source into its knowledge module, and turn its action items into an issue. Use when the user says "ingest" about a meeting note, daily note, paper or other file.
---

1. Read the module's `CLAUDE.md` and the `SCHEMA.md` it imports; follow Operations → Ingest and the update triggers.
2. **Action items** (open checkboxes): create one issue for the note in the owning team from INSTANCE, titled after the note, with the items as a checklist in its description and a link back to the note. An item that belongs to another team or person gets its own issue. Replace the checkboxes in the note with the issue link. Ask only when the team or owner is unclear.
3. **Pages:** update the pages the note affects. Permanent knowledge changes go through promotion with the operator.
4. Commit the note and pages, and report the issue and the changed pages.
