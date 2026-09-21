---
type: stream
stream:                    # the stream's own name — `stream/<name>` is its branch
repos: []                  # participating repos by root folder; the sweep verifies each one
blocked:                   # this stream's blocker, cleared when it lifts
---

<!-- HOW TO USE — delete this block in the real note.

Creating a stream (four steps, no script unless the checklist fails twice):
1. this note from this template, card `- [ ] [[Stream x]]` into `backlog`;
2. its task notes get `stream: x` — front matter is the one membership authority,
   and the `Tasks:` list below must agree with it or the sweep refuses;
3. the operator's authorisation publishes `stream/x` from `main` and moves the card to `open`;
4. dispatch starts once that branch is live.

Merge evidence: one line per repo, `- <repo>: <tip-sha> -> <target-ref>` (target
defaults to `origin/main`). `vault sweep --to-promotion` verifies the merge from
these lines alone — ancestry-preserving, never squash.

Promotion candidates: text, not files. Three kinds —
- **new concept** — title, why, linked notes, destination (personal or team);
- **amendment** — target note, sentences to add or replace, superseded text quoted;
- **supersession** — note to retire, reason, redirect.
Only knowledge that outlives the stream qualifies: a concept and its why, a decision
with its rejected alternatives, a rule of method — never state, counts, fix logs or
repository-owned facts. Fold before create: link the existing concept and add only the
genuinely new sentences. The operator ticks what stays, then `Execute`; that tick is the go.
-->

Owner: <project>

Stream description: one or two paragraphs; details live in the task notes.

Rulings in force:
- YYYY-MM-DD one sentence each

Tasks:
- [ ] [[Task note]]

MR link:

Merge evidence:
- <repo>: <tip-sha> -> <target-ref>

Promotion:
- [ ] candidate, one high-level line each
- [ ] Execute
