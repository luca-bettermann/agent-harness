## Our additions

- **Linear:** the spec is the project description and each ticket is an issue (`docs/agents/issue-tracker.md`).
- **Branches:** the integration branch is `project/<slug>` in every repository the project touches. Each issue branch uses Linear's branch name, the same in every repository, with one worktree per repository under the INSTANCE work root.
- **Landing:** an issue merges directly into the project branch once its fast checks pass locally; then delete its branch and worktrees. The project lands through one MR per repository into `main`.
- **Sweep:** before step 1 and after step 9, check every branch, worktree and scratch entry whose name carries an issue ID against Linear. When the issue is Done or Canceled, remove it if it is clean and contained in `origin/main` or a `project/*` branch (`git worktree remove`, `git branch -d`, `git push origin --delete`), then run `git worktree prune`. Report anything you can't remove, and anything without an issue ID, to the operator with the reason.
- **Budget:** start a subagent only while the cost units of running subagents stay within the vendor's cap. Tier weights, caps and vendor order come from INSTANCE. A session that hits a limit leaves its issue In Progress for the next session to continue.
