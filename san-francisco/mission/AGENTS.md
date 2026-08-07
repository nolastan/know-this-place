# Mission — neighborhood guidance

Applies to everything under `san-francisco/mission/`, in addition to the root
`AGENTS.md`.

## Scope

The Mission: roughly from the Central Freeway and Duboce Avenue south to
Cesar Chavez Street, and from Dolores Street east across Potrero Avenue to the
Utah and Vermont Street blocks. The boundary is wider than the neighborhood's
everyday sense of itself — it takes in Western SoMa streets north of Duboce
and a strip of Potrero Hill. The authoritative test for whether an address
belongs here is the SF Planning "Analysis Neighborhoods" boundary — in the
datasets, `nhood` /
`analysis_neighborhood` **`Mission`**. That is the value the seeder is run
with, and it is what decides membership; the sentence above is orientation,
not the test.

Fourteen streets have a directory under both `mission/` and `castro/` — 14th
through 21st Streets, Cumberland, Dolores, Dorland, Duboce, Liberty and
Market. The parcels are different on each side of the boundary, so neither
directory is a duplicate of the other. There is no
`AREA_EXCLUDE_STREETS` entry for the Mission; independently of that list, the
seeder skips any parcel that already has a page anywhere on the site.

The assessor's `assessor_neighborhood` splits the same ground finer: most
parcels here are "Inner Mission", but the roll also files them under Mission
Dolores, Noe Valley, Eureka Valley/Dolores Heights, South of Market and
Potrero Hill. That field is recorded in `data.json` and is not the membership
test — the breadcrumb, the directory and the `.sub` line all say
Mission.

## Seeding this neighborhood

The neighborhood has been seeded from the 2025 roll: 5,003 new pages, joining
the one that already existed, across 100 streets. Those pages are now edited
by hand like any other — see "Page lifecycle" in the root `AGENTS.md`.

Re-run the seeder only to pick up parcels that have newly appeared:

```
python3 scripts/seed_pages.py seed --neighborhood "Mission" \
                                   --city san-francisco --area mission
```

It creates pages that don't exist and touches nothing that does. Of the 7,435
parcels EAS lists in the boundary, that run wrote pages for 5,003 and passed
over 712 with no 2025 assessor record, 530 condominium units (units, not
buildings — see the root `AGENTS.md`), the five parcels below, and 1,184
business parcels that were out of scope at the time. Business parcels are in
scope now, so a re-run writes those 1,184.

### Deferred for a human — parcels sharing a street number

Each of these shares its street number with another parcel that the assessor
numbers plainly, so the plain one has the page and these were left out rather
than overwrite it or invent an address EAS doesn't carry:

- 1268 South Van Ness Avenue — parcels 3642076 (assessor: 1268A) and 3642077
  (1268B)
- 1270 South Van Ness Avenue — parcels 3642078 (1270A) and 3642079 (1270B)
- 163 Liberty Street — parcel 3607035A (assessor: 163A)

Resolving one means establishing what the lettered parcel actually is — a
second building on the lot, a subdivided one, or a records artifact — and
writing the page by hand.

## Orientation (context, not citable facts)

Useful background so pages are written with the right instincts. **Verify
before asserting any of this about a specific building** — cite per-address
sources, not this file.

- The housing stock is largely Victorian and Edwardian, and the 1906 fire line
  ran through the neighborhood: pre-fire buildings survive on the western
  slopes while much of the district was rebuilt in 1906–1912. The historic
  district names record this directly — "Guerrero Street Fire Line", "16th and
  Valencia Streets Post-Fire", "Inner Mission Boulevards and Alleys
  Reconstruction". Where a building's date matters, the assessor's
  `year_property_built` and Planning's `yearbuilt` are the evidence, not the
  district it sits in.
- Historic districts are dense here: 34 of them touch parcels in this
  boundary, and 43 parcels sit in two at once. Follow the
  `sf-historic-districts` rules in DATA-SOURCES.md — lead with the district
  that confers Article 10 protection and name the other, and remember that
  California Register "Eligible" is not "Listed" and neither implies local
  landmark protection.
- Mission Street, Valencia Street and 24th Street are largely commercial, so
  expect storefronts and mixed-use buildings there rather than flats. The
  assessor's `use_definition` is what says which a parcel is, not its street.
- Good deep-context sources: OpenSFHistory (Western Neighborhoods Project),
  Shaping San Francisco / FoundSF, Mission Local, and the SF Planning
  historic-district survey documents.

## Hub pages

- `san-francisco/mission/index.*` — the neighborhood page: shared history
  lives HERE (not duplicated across address pages), plus links to street
  indexes.
- Each street directory's `index.*` lists its covered numbers with a one-line
  hook per building.
- A street hub's first paragraph is its hand-written lead, and rebuilding the
  hubs preserves it. Don't leave a bullet list as the first paragraph — the
  rebuild will read it as the lead.
