# Upstream skills are extended by addenda, not forked

Superseded in part by [0008](0008-matt-skills-unchanged-installation-maps.md): addenda keep only true additions.

Matt Pocock's skills stay untouched in `upstream/` as a git subtree, and our additions live in `engineering/addenda/<skill>.md`, appended at install. A fork would have let us edit the skills directly, but every upstream update would then need a manual merge; with addenda an update is one `git subtree pull`, and our changes stay visible as a short list.
