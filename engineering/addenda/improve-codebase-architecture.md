## Our additions

- **Map before exploring:** run `WORKSPACE/.agent-harness/bin/emerge-map SCOPE --scratch SCRATCH` before spawning the exploring subagent; INSTANCE names the workspace and scratch roots. Give it the short JSON summary: hubs with fan-in and fan-out, clusters crossing folders, import cycles and modularity.
- **Repo:** map the repository to choose a module to explore. Hubs with frequent changes rank first. The script combines the map with scoped `git log --numstat` from the last 90 days; Emerge's git metrics stay off.
- **Package:** run the same command on one subfolder to inspect its seams and locality. Import counts suggest where to read; judge depth from the module's interface and implementation.
- **Neighbourhood:** add `--neighbourhood PATH` for a candidate's files within two imports in either direction; `--imports N` changes the distance. Use this DOT graph as the report's before diagram. External or unresolved imports are counted separately.
- **Check:** run the script with `--self-check --scratch SCRATCH`. It installs Emerge in an isolated environment under SCRATCH and writes exports there. Source folders stay read-only.
