# Resolver — historic address to today's parcel

**Mission:** decide, for each finding, whether it names a place that exists
today — and record the decision with its evidence. **Most of the mistakes this
project can make live in this stage**, so the bias is toward `unresolved`.

## Input

A findings file with entries at `resolution.status: "unresolved"`.

## Output

The same file, each entry's `resolution` filled in:

- `"resolved"` — with `apn`, `path`, `eas_address`, `method`, `checked_on`.
- `"unresolved"` — with `note` saying what is missing (no street number, OCR
  ambiguity, no EAS record, cross streets contradict the number).
- `"rejected"` — with `note` saying why it can never resolve (a demolished
  address, a street expunged, a duplicate of another finding).

Then a `research:publish` issue for the resolved ones, and a dossier note on
anything the batch taught you about the source's addressing.

## Doing the mechanical half with a tool

[`../tools/resolve_eas.py`](../tools/resolve_eas.py) does the joins below over a
whole findings file — EAS lookup, parcel confirmation against `sf-parcels` and
the roll, the lowest-number rule, the comparison between a record's two
addresses — and writes a `resolution` for every entry with the reason in
`method`:

```bash
python3 research/tools/resolve_eas.py fetch  research/findings/<id>/<batch>.json
python3 research/tools/resolve_eas.py report research/findings/<id>/<batch>.json
python3 research/tools/resolve_eas.py apply  research/findings/<id>/<batch>.json
```

It declines rather than guesses: no EAS record, a range now split across
parcels, a condominium's worth of parcels on one point, or two recorded
addresses that are both real all come back `unresolved`. **`report` before
`apply`, and read every conflict it prints** — the tool's job is the lookups,
not the judgement. A street the source spells its own way is mapped onto EAS's
spelling where squashing punctuation finds it, and otherwise needs an explicit
`--alias RECORDED=EAS`, which it states in the method.

## Procedure

1. **Check EAS first.** `sf-eas-addresses` in
   [../../DATA-SOURCES.md](../../DATA-SOURCES.md) is the canonical list of
   addresses that may have a page. No EAS record → not `resolved`, full stop.
   Record it as `unresolved` (or `rejected` if the address is known gone) and
   note where the fact could still live: the surviving building nearby, or the
   street hub.
2. **Use the source's own check material.** Cross streets, lot dimensions,
   block faces. "1311 Alabama, 40x100" against the assessor's `lot_area` of
   4,000 sq ft is an identification; a bare number is an assumption. Put what
   you checked in `resolution.method` — that sentence is the audit trail.
3. **Get the parcel, not just the address.** Join EAS → `parcel_number`, then
   confirm against `sf-parcels` / the assessor roll. Watch for a parcel that
   spans several street numbers (one page, at the lowest number, titled with
   the range) and for condominium APNs (units, not buildings). The rules are in
   the root [AGENTS.md](../../AGENTS.md) → "Directory contract".
4. **Set `path`** to where the fact belongs — an existing page, or the page
   that would exist. The publisher needs to know which.

## The renumbering traps

- **1909 renumbering.** Street numbers changed across much of the city and some
  streets were renamed. A pre-1909 number is not today's number until EAS and a
  cross-street check say so. Worked examples:
  [../../san-francisco/corbett-heights/AGENTS.md](../../san-francisco/corbett-heights/AGENTS.md).
- **Mission and Eureka Valley did *not* move in 1909.** Every cross-street
  check run in this corpus resolves to today's number. Check anyway; don't
  extend the finding to other neighborhoods.
- **South Van Ness is the dangerous one.** It was Howard Street until 1932 and
  was **renumbered** when renamed. The offset varies by block face — roughly
  −1,600 over 17th–24th but about −1,500 near 13th–16th — so **subtracting a
  constant misplaces buildings by a whole block.** Convert per block face using
  cross streets, or leave it unresolved. The table is in
  [../sources/loc-newspapers.md](../sources/loc-newspapers.md).
- **Pure renames carry their numbers over**: Lexington Avenue → Lexington
  Street, Army Street → Cesar Chavez, Clara → Ord, Dupont → Grant.
- **Streets that no longer exist** (Falcon Street, expunged by the Market
  Street extension) resolve to nothing. `rejected`, with the note saying where
  the story belongs instead.

## Conflicts

A finding that contradicts the assessor's `year_property_built`, or another
source, is **not** a resolution problem. Resolve the address, keep both claims,
and set `conflict` on the finding so the publisher records the disagreement in
the page's `.unknowns`. Never adjudicate, never average, never quietly prefer
the newer source.

## Done when

Every entry has a decision with a stated method, `check.py` passes, and the
resolved set is queued for publication. A batch that resolves 6 of 400 has done
its job.
