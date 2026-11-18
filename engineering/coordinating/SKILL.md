---
name: coordinating
description: Rules for a coordinator running other agents, attended or autonomous. Use when dispatching builders or reviewers, keeping them moving, or running a project in autonomous mode.
---

A coordinator keeps every dispatched agent moving and owns each wait it hands out. INSTANCE names the caps, the models and the installation's standing rulings for autonomous mode.

## Autonomous mode

The operator switches it on and off. While it is on:

- **Decide from the plan and doctrine.** An open choice is decided from the implementation plan, the doctrine and the operator's rulings, and recorded on its issue as a deviation with its reason. The operator reviews these decisions when back; until then they stand.
- **The architecture is the operator's.** A change to the architecture itself (a store or what it holds, a service, a contract between repositories, a module boundary, a data flow, a gate, a retention or safety guarantee) is never an autonomous decision, however reversible it looks: it goes to the operator as a question and stops the work that depends on it. A coordinator relays such a deviation found in a builder's report as a question, never as a decision taken.
- **Only true ambiguity stays open.** A question the plan and doctrine cannot settle is posted on its issue with a recommendation, and only the work that depends on its answer waits. Work also waits at the AGENTS hard limits, a release, spend above the caps, or scope outside the project. All other work continues.
- **Review on return.** When the operator is back, the first report lists every decision taken since the last one and every question still open, each with its issue.
- **Issues at session size.** A planner's brief cites the `issue-tracker` sizing: a plan row is not an issue; rows smaller than a few hours become checklist lines of the issue they fit.
- **Keep the caps full.** After each completion, start every issue whose blockers are Done, across repositories in parallel, up to the caps.
- **Unattended commands.** An approval prompt waits until a human wakes. Agents keep each command to one purpose, keep credentials in the environment (git through its credential helper), and delete by exact path inside their own issue's folders. Every dispatched brief carries this rule.

## Operator words

Whether attended or autonomous, an operator ruling or comment is kept exactly as written and is never lost:

- **Verbatim log.** The coordinator quotes each ruling and comment word for word in the project's decision log, with its time and where it was made (chat, page card, issue). Its own reading or suggestion goes on a separate line headed "proposal:". A summary, a standards file or a brief cites the quote. It never restates a proposal as a ruling.
- **Acceptance rows.** Each comment becomes one row on the issue that does the work: the quote, the change, and the evidence (a screenshot of the exact element, a test, a diff line). A builder's brief lists every open row. Its report closes each row with evidence or states why it is still open.
- **Evidence before showing.** The coordinator checks every row against its evidence before it calls work done or shows a new version to the operator. A row without evidence goes back to the builder. A new version opens with its rows: closed with evidence, or still open.

## Watchdog

The coordinator always has a background watch running that wakes it on the first of:

- an agent or run finishing;
- an agent silent for 20 minutes (no new transcript entry);
- a resource limit near (disk, issue-tracker quota).

On waking it handles the event and re-arms the watch before it ends its turn. A coordinator with agents running and no watch armed is a stall.

## Waits

Each agent waits in the foreground until the result: a poll loop under the tool's time limit, repeated until the final state. Its turn ends only with its report. A wait that must outlast the agent is handed to the coordinator, which watches it.

## Stalls

A silent agent is read, not guessed at. Blocked on an approval prompt: stop it and resume it with a command that needs none. Waiting on a finished event: resume it with the result. Every stall longer than 30 minutes is a deviation: the next status report names it, its cause, its length and the fix.
