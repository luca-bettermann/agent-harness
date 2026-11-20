# A command guard refuses kill by pattern and a bare git stash

A builder used `pkill -f` and a bare `git stash`, both against AGENTS ("Never `kill` or `pkill` by pattern"; never discard another writer's edits) (DEV-660; DEV-677, Luca 2026-11-20: "hm, ok"). Per the Root cause principle the rule is enforced by a hook, not by more text.

`command-guard.sh` is a PreToolUse hook on shell commands. It splits the command into its simple commands and refuses:

- `pkill`, `killall`, and `xargs … kill`;
- `kill` with any argument that is not a literal number (a name, `$PID`, `$(pgrep …)`, a backtick substitution); signal options such as `-9` or `-s TERM` pass;
- `git stash`, `git stash push` and `git stash save` without a word after `--`. Other stash commands (`pop`, `list`, `drop` …) pass.

The refusal names the allowed form: `kill <PID you started>`, `git stash push -- <paths>`.

It reads words, not quoting, so a quoted string containing `; pkill` is refused too. It is a guardrail, not a boundary: a command built at run time passes.

## Clients

Claude Code runs it on PreToolUse for `Bash`; Codex on every PreToolUse, taking `tool_input.command` as a string or an array. Neither needs a session or agent key, so Codex subagents are covered too. `sh hooks/command-guard.sh --check` holds the tests.
