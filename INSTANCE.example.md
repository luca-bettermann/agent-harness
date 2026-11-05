# Instance

Copy into the installation's repository as `INSTANCE.md` and import it from the workspace `CLAUDE.md`. Concrete people, paths and tools live here, never in agent-harness.

## People

- Operator (rulings, promotions, releases): `<name>`
- Physical systems and their owners: `<system → owner>`

## Workspace

- Workspace root and work root: `<paths>`
- Repository manifest (vcs2l): `<path to .repos>`
- Knowledge modules: `<module → path, owner>`
- Credential store: `<password-manager reference, never a value>`

## Tools

- Issue tracker and its mapping: `<tracker>`, `docs/agents/`
- Hosting and CI: `<host>`; time budget per run: `<minutes>`
- Add-ons: `<name → on or off>`

## Models

| Tier | Model | Cost weight |
| --- | --- | --- |
| T1 | `<model>` | 8 |
| T2 | `<model>` | 4 |
| T3 | `<model>` | 2 |
| T4 | `<model>` | 1 |

- Cost cap per vendor: `<units>`; vendor order: `<vendors>`
