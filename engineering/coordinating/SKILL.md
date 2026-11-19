---
name: coordinating
description: Rules for a coordinator running other agents, attended or autonomous. Use when dispatching builders or reviewers, keeping them moving, or running a project in autonomous mode.
---

A coordinator keeps every dispatched agent moving and owns each wait it hands out. INSTANCE names the caps, the models and the installation's standing rulings for autonomous mode.

## Autonomous mode

The operator switches it on and off. While it is on, engineering's _Stop only for open design_ runs with nobody to ask:

- **Decide and record.** An open choice is decided from the plan, the doctrine and the operator's rulings and recorded on its issue as a deviation with its reason. It stands until the operator returns and reviews it: the first report then lists every decision taken since the previous report and every question still open, each with its issue.
- **The operator's decisions wait.** A question the plan and doctrine can't settle, and any change to the architecture (a store or what it holds, a service, a contract between repositories, a module boundary, a data flow, a gate, a retention or safety guarantee) however reversible it looks, go to the operator as a question with a recommendation, also when found in a builder's report. Work also waits at the AGENTS hard limits, a release, spend above the caps, or scope outside the project. Only the work that depends on them waits.
- **Caps full.** After each completion, start every issue whose blockers are Done, across repositories in parallel, up to the caps. A planner's brief cites the `issue-tracker` sizing.
- **Unattended commands.** An approval prompt is a wait nobody ends, so every brief tells its agent to keep commands approvable: one purpose each, credentials from the environment (git through its credential helper), deletes by exact path inside its own issue's folders.

## Operator words

Attended or autonomous, an operator ruling or comment is a source (AGENTS, Single source of truth):

- **Verbatim log.** The coordinator quotes it word for word in the project's decision log, with its time and where it was made (chat, page card, issue); summaries, standards and briefs cite the quote. Its own reading or suggestion is a separate line headed "proposal:", never a ruling.
- **Acceptance rows.** Each comment is an acceptance criterion on the issue that does the work: the quote, the change and its evidence (a screenshot of the exact element, a test, a diff line). A brief lists the open rows; a report closes each with evidence or says why it is still open. The coordinator checks every row against its evidence before it calls work done or shows a new version; a row without evidence goes back to the builder. A new version opens with its rows: closed with evidence, or open with the reason.

## Watch

While it coordinates, the coordinator keeps a background watch armed that wakes it on the first of: an agent or run finishing, an agent silent for 20 minutes (no new transcript entry), a resource limit near (disk, issue-tracker quota). It handles the event and re-arms the watch before it ends its turn; agents running with no watch armed is a stall. A silent agent is read, not guessed at: one blocked on an approval prompt is stopped and resumed with a command that needs none; one waiting on a finished event is resumed with the result. A stall longer than 30 minutes is a deviation; the next status report names its cause, length and fix.
