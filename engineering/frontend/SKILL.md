---
name: frontend
description: Browser interface rules. Use when building, changing, testing or reviewing a web UI.
---

- **Design before build:** before building a new view or a visible change, show a small mock-up or screenshot (the `prototype` skill builds throwaway ones) and iterate until the operator agrees. In an autonomous run, post it on the issue and build only the parts that don't depend on it.
- **Components:** use shadcn/ui. Build a component of your own only where shadcn has none.
- **Quiet UI:** few colors, little decoration, dense but calm layouts. References: the Claude and Codex apps, Linear, Vercel, Raycast.
- **Verify in the real browser:** walk every affected user journey on the rendered page before handing over. Type checks and screenshots don't show interaction.
