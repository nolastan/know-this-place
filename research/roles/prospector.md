# Prospector — find sources worth mining

**Mission:** find material that carries San Francisco street numbers and that a
reader could not have found by searching that address.

## Input

A theme, a neighborhood, a gap ("we have almost nothing on the Sunset before
1930"), or nothing at all — prospecting is legitimate open-ended work.

## Output

Prospecting has two gears, and picking the wrong one wastes a session.

**Triage** — when there are several unverified leads and you don't yet know
which deserve the effort. Per lead: the four judgements below, one sampled
example proving it carries numbered addresses with dates, and a `hold` /
`promote` / retire verdict written into the **Leads** table's `triaged` column
with its evidence in [../SOURCES.md](../SOURCES.md) → Triage notes. No dossier,
no issue. Thirteen dossiers written before knowing which three are worth mining
is thirteen sessions spent to learn what three would have told you.

**Promotion** — when one lead has already survived triage, or arrives obviously
strong. Then:

1. A dossier at `../sources/<id>.md`, from
   [../templates/source-dossier.md](../templates/source-dossier.md).
2. A row in [../SOURCES.md](../SOURCES.md) with status `lead` or `acquiring`,
   and the lead's triage note deleted.
3. A `research:acquire` issue, per [../templates/issues.md](../templates/issues.md).

For everything rejected in either gear: the row in the **Leads** table, struck
through with the reason. A rejected lead is worth recording so nobody spends a
session rediscovering it.

## How to judge a source

Score it on four things, in this order:

1. **Search-invisibility.** Would a reader searching "1311 Alabama Street" ever
   see this? If yes, it is a low-value target no matter how big it is. Rate
   high / medium / low and put the rating in the register.
2. **Address density.** Does it name street numbers, or only streets,
   neighborhoods and metes-and-bounds? "Between 19th and 20th on the east side
   of Folsom" is not an address. A source that never gives numbers is not
   worthless, but it is a context source, not a page source.
3. **Datedness.** Can a fact from it be pinned to a year? Undated claims are
   nearly unusable under the evidence bar.
4. **Access and licensing.** Can we get it lawfully and cite it stably? Facts
   are free to use; expression is not. Paywalls, login walls, and terms that
   forbid automated access make it a `needs-human` lead, not an obstacle to
   route around.

**Size is not on that list.** Ten thousand pages that yield four addresses is a
good source. See "Mining a corpus" in [../AGENTS.md](../AGENTS.md).

## Procedure

1. Check [../SOURCES.md](../SOURCES.md) — registered and leads both — and search
   open issues for the source id. Don't re-prospect what's already known.
2. Establish what the source actually is: publisher, dates covered, format,
   where it lives, whether a stable citation URL exists.
3. Sample it. Read enough to answer "does this give street numbers with dates?"
   with evidence — quote one real example in the dossier. A lead promoted on a
   guess wastes the acquirer's session.
4. Write the dossier: what it is, how to get at it, what it should yield, the
   citation label a page will use, and the cautions you already see.
5. Pick the `id`: lowercase, hyphenated, stable, and descriptive of the source
   rather than the project (`cdnc-sf-papers`, not `newspapers-2`).
6. Register it, file the acquire issue, stop. **Prospecting doesn't mine.**

## Done when

**Triage:** every lead in scope carries a dated verdict in the `triaged` column,
each `hold` has a triage note with a real sampled example, and each rejection is
struck through with its reason.

**Promotion:** the register has a row, the dossier exists with a real sampled
example, and an issue names the next concrete step.

Either way, run `python3 research/tools/check.py`.
