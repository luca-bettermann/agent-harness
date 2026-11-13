---
name: frontend
description: Browser interface rules. Use for any change to a web UI, and for testing or reviewing one.
---

- **Design before build:** before building a new view or a visible change, show a small mock-up or screenshot (the `prototype` skill builds throwaway ones) and iterate until the operator agrees. In an autonomous run, post screenshots on the issue as soon as the first version renders, before polishing, and again at the end; the operator can't see local files.
- **Components:** use shadcn/ui. Build a component of your own only where shadcn has none.
- **Quiet UI:** few colors, little decoration, dense but calm layouts. References: the Claude and Codex apps, Linear, Vercel, Raycast.
- **Information on demand:** by default a row or control shows its name and value; descriptions and help appear beside or below it on hover or focus, and status messages sit behind a small info or warning icon instead of lines of text. What the user needs to act safely stays visible: errors, blocking warnings, and units where a value would otherwise be ambiguous.
- **Responsive:** every view shows content quickly and answers input without a noticeable wait. Each new or changed view states time budgets in its acceptance criteria (first content, ready, response to input), measured cold and warm in the real browser on the development platform. Heavy work streams in behind visible progress, never behind a blank screen. Layouts adapt to the window, from a laptop to a large monitor; phones are out of scope.
- **Verify in the real browser:** walk every affected user journey on the rendered page before handing over. Type checks and screenshots don't show interaction.
