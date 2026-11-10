#!/bin/sh
# SubagentStart hook: every subagent loads its matching skills before work.
printf '%s\n' '{"hookSpecificOutput":{"hookEventName":"SubagentStart","additionalContext":"Before any other step, invoke the Skill tool for every skill whose description matches your task (for example engineering for any change to code, tests, CI or configuration; frontend for any change to a web UI). A skill not loaded with the Skill tool is not followed."}}'
