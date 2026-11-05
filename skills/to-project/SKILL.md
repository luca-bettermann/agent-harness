---
name: to-project
description: "Turn the current conversation into a project spec, publish it as the Linear project description, then split it into issues with to-issue. Matt's to-spec, in Linear vocabulary."
disable-model-invocation: true
---

Follow [`to-spec`](../upstream/skills/engineering/to-spec/SKILL.md) exactly, with these changes. Where other skills say `to-spec`, they mean this skill.

- **Publish** the spec as the **description of the Linear project** (create the project if none exists), not as a separate issue. The project description is the single home of the spec.
- **Then** call `to-issue` on the same conversation, without clearing or compacting in between.
