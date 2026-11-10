# Instance

Copy into the installation's repository as `INSTANCE.md` and pass its path to `install.sh` with the workspace root; the workspace's entry points load it, so don't import it anywhere else. Concrete people, paths and tools live here, never in agent-harness.

## People

- Operator (rulings, releases; approves promotions unless a module names another owner): `<name>`
- Accounts: `<account → who uses it>`. An account may be shared; the workspace root, not the account, selects this installation.
- Physical systems and their owners: `<system → owner>`

## Workspace

- Workspace root, work root and scratch root: `<paths>`
- Repository manifest (vcs2l): `<path to .repos>`
- Knowledge modules: `<module → path, owner, contribution rules>`
- Credential store: `<password-manager reference, never a value>`

## Tools

- Issue tracker: `<tracker>`; teams: `<team → scope>`; mapping: `<absolute path of this repository>/docs/agents/` (read it before any tracker skill)
- Hosting and CI: `<host>`; time budget per run: `<minutes>`

## Models

| Tier | Model | Cost weight |
| --- | --- | --- |
| T1 | `<model>` | 8 |
| T2 | `<model>` | 4 |
| T3 | `<model>` | 2 |
| T4 | `<model>` | 1 |

- Cost cap per vendor: `<units>`; vendor order: `<vendors>`
- Budget: start a subagent only while running subagents stay within the cap; builders run on the default build tier, a higher tier needs a reason on the issue.

## Delivery

- Where reports (architecture reports, project reports) are delivered so the operator can read them: `<channel>`. A local file and its path are not delivery.
