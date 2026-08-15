# Roles

Six playbooks, one per stage of the pipeline in [../AGENTS.md](../AGENTS.md).
They exist so a session can be handed **one job** — "extract batch X",
"resolve the unresolved findings for Y" — and do it well without holding the
whole project in its head.

| Role | One line |
|---|---|
| [prospector](prospector.md) | Find a source worth mining and register it. |
| [acquirer](acquirer.md) | Get the material where an agent can actually read it. |
| [extractor](extractor.md) | Messy source in, structured findings JSON out. |
| [resolver](resolver.md) | Historic address in, today's parcel out — or unresolved. |
| [publisher](publisher.md) | Resolved findings onto pages, and a PR. |
| [auditor](auditor.md) | Check what shipped against what was found. |

**Wearing a role doesn't narrow the rules.** [../AGENTS.md](../AGENTS.md), the
root [AGENTS.md](../../AGENTS.md) privacy limits, and the evidence bar apply in
every role.

**A role is a job, not an identity.** One session may run several stages for a
small source; that is normal. What matters is that each stage's output exists
as a file before the next one starts, so the work survives the session.

Adding or reshaping a role is expected as the project learns — see "Amending
this module" in [../AGENTS.md](../AGENTS.md).
