## Our additions

- **Map before exploring:** run `WORKSPACE/.agent-harness/bin/emerge-map SCOPE --scratch SCRATCH` before spawning the exploring subagent; INSTANCE names the workspace and scratch roots. Give it the short JSON summary: hubs with fan-in and fan-out, clusters crossing folders, import cycles and modularity.
- **Repo:** map the repository to choose a module to explore. Hubs with frequent changes rank first. The script combines the map with scoped `git log --numstat` from the last 90 days; Emerge's git metrics stay off.
- **Package:** run the same command on one subfolder to inspect its seams and locality. Import counts suggest where to read; judge depth from the module's interface and implementation.
- **Neighbourhood:** add `--neighbourhood PATH` for a candidate's files within two imports in either direction; `--imports N` changes the distance. Use this DOT graph as the report's before diagram. External or unresolved imports are counted separately.
- **Check:** run the script with `--self-check --scratch SCRATCH`. uv provides Emerge and its Python; exports go under SCRATCH, and source folders stay read-only.
- **Whole scope:** when the operator names several repositories or the whole system, design the target before any local candidate. Work one level at a time across the whole scope; each level works only on what the level above kept, starting from each repository's map.
  0. **Goals:** the requirements, each with its source (`engineering`, Requirements).
  1. **Modules:** which modules those requirements need at all, and the interface of each.
  2. **Ownership and size:** one owner per fact, the seams and dependency direction across repositories, and a size budget per module; a module meets its budget or names the requirement that sets its size.

  For levels 1 and 2, the strongest model of each vendor INSTANCE names designs independently (`codebase-design`'s design-it-twice); the orchestrator synthesizes and the operator grills the synthesis. The report shows the target module map, its gap to the current maps and the migration order, and names the local candidates the target absorbs; only the others continue in the local flow. At `/to-spec` the migration order becomes the project's tickets, and the audit and refactor issues the target absorbs become Duplicates of them.
