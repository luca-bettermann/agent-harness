# Skills load through one hook, for both clients

An audit of 16 builder transcripts found that skill descriptions alone were not enough: builders loaded `engineering`, `tdd` and `frontend` inconsistently even when the brief asked for them. The rule now lives once in AGENTS ("Before acting, ... load every skill whose description matches the task"), and one hook repeats it on every prompt, at every subagent start, and after compaction or resume, registered the same way for Claude Code and Codex. A tool behaves the same for every model and coordinator; a sentence in a brief can be forgotten.
