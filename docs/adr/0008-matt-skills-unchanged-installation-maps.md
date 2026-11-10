# Matt's skills stay unchanged; addenda add, the installation maps

Matt Pocock's skills stay untouched in `upstream/` as a git subtree. A fork would let us edit them directly, but every upstream update would then need a manual merge; with addenda in `engineering/addenda/<skill>.md`, appended at install, an update is one `git subtree pull` and our changes stay visible as a short list.

Matt's skills already ask for a mapping (tracker, labels, domain docs). Restating our infrastructure in addenda duplicated that mapping, left the mapping files thin and got them skipped. So addenda hold only true additions; tracker, branches, landing and where findings go live in the installation's `docs/agents/`; people, budget and delivery in its `INSTANCE.md`; test rules in `engineering`. All upstream skills are installed, `setup-matt-pocock-skills` included, so a new installation can generate its mapping.

Supersedes 0002 (addenda, not a fork), merged here.
