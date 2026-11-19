---
name: coordinating
description: Rules for a coordinator running other agents, attended or autonomous. Use when dispatching builders or reviewers, keeping them moving, or running a project in autonomous mode.
---

A coordinator keeps every dispatched agent moving and is the live waiter for every wait it hands out (AGENTS, Predictable behavior). INSTANCE names the caps, the models and the installation's standing rulings for autonomous mode.

## Autonomous mode

The operator switches it on and off. While it is on, engineering's _Stop only for open design_ runs with nobody to ask:

- **Decide and record.** An open choice is decided from the plan, the doctrine and the operator's rulings and recorded on its issue as a deviation with its reason. It stands until the operator returns; the first report then lists every decision taken and every question still open, each with its issue.
- **The operator's decisions wait.** What INSTANCE assigns the operator, the AGENTS hard limits, and any change to the architecture (a store or what it holds, a service, a contract between repositories, a module boundary, a data flow, a gate, a retention or safety guarantee), however reversible it looks, go to the operator as a question with a recommendation, also when found in a builder's report. Only the work that depends on the answer waits.
- **Caps full.** After each completion, start every issue whose blockers are Done, across repositories in parallel, up to the caps.
- **Unattended commands.** An approval prompt is a wait nobody ends, so every brief tells its agent to keep commands approvable: one purpose each, credentials from the environment (git through its credential helper), deletes by exact path inside its own issue's folders.

## Operator words

Attended or autonomous, an operator ruling or comment is a source (AGENTS, Single source of truth):

- **Verbatim log.** The coordinator quotes it word for word in the project's decision log, with its time and where it was made (chat, page card, issue); summaries, standards and briefs cite the quote. Its own reading is a separate line headed "proposal:", never a ruling.
- **Acceptance rows.** Each comment is an acceptance criterion on the issue that does the work: the quote, the change and its evidence (a screenshot of the exact element, a test, a diff line), proven like every criterion (engineering, _Iterate to acceptance_) before the operator sees the next version. Briefs list the open rows, reports close them, and each new version opens with every row's state.

## Watch

While any agent or run it started is going, the coordinator keeps a background watch armed that wakes it on the first of: one finishing, one silent for 20 minutes (no new transcript entry), a resource limit near (disk, issue-tracker quota). It handles the event and re-arms the watch before it ends its turn. A silent agent is read, not guessed at: one blocked on an approval prompt is stopped and resumed with a command that needs none; one waiting on a finished event is resumed with the result. A stall longer than 30 minutes is a deviation; the next status report names its cause, length and fix.
