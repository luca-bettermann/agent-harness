# Subagents load their skills through a hook

An audit of 16 builder transcripts found that skill descriptions alone were not enough: builders loaded `engineering`, `tdd` and `frontend` inconsistently even when the brief asked for them. A `SubagentStart` hook now tells every subagent to load the skills matching its task before anything else. A tool behaves the same for every model and coordinator; a sentence in a brief can be forgotten.
