# Merchants

Putting the business that trades from a building today on that building's
page — from ordering apps and merchant directories — as the page's
`occupants`, rendered as the "Current occupant" panel at the top of the aside.

Read the root [AGENTS.md](../AGENTS.md) first; its privacy limits bind here
unchanged. The key and its block are specified in
[REFERENCE.md → occupants](../REFERENCE.md#occupants) and
[shared/BLOCKS.md → Current occupant](../shared/BLOCKS.md#current-occupant--panel-occupant).

## Sources

One row per directory. `id` is the id a page's `sources` entry and each
`occupants` entry cite. **Referral** says whether the renderer's `REFERRALS`
table carries an offer for it — that table, in `scripts/seed_pages.py`, is the
only place an offer lives.

| id | Directory | Read from | Referral | Files |
|---|---|---|---|---|
| `bites` | Bites, merchant directory | `https://withbites.com/merchants` — the page's schema.org `ItemList`, every Bites merchant in the country, one `Restaurant` each | $5 off a first order; the link opens the app, not the merchant (no per-merchant deep link exists) | `bites/<date>.json` |

Directories still to add are the GitHub issues labelled `monetization`.

## Rules

- **The business, never the people.** A merchant's trading name is a fact
  about the building; its owner, chef, staff and customers are not. A sole
  proprietor whose business is their own name does not go on a page.
- **Publish only what the directory states consistently.** Fetch the page more
  than once before trusting a field. Bites' `priceRange` changed on 111 of 786
  merchants between two fetches seconds apart — it is not a fact and never
  reaches a page. Ratings and menus describe the merchant rather than the
  building and are left out too.
- **The panel says when the listing was read.** Hours drift within days (9 of
  118 Bites merchants changed theirs in five days of September 2026), so the
  panel prints "Last updated" from the source's `retrieved`, and a refresh
  changes that one field.
- **A referral offer is the source's, not the merchant's.** Never put a link
  in an `occupants` entry. A directory gets an offer by a row in `REFERRALS`,
  added only when a human has supplied the link, and a merchant from any other
  directory never shows one.
- **Occupants describe today.** A refresh replaces a page's entries from that
  source wholesale: a merchant the directory no longer lists comes off the
  page. It is not a timeline fact.
- **List what the directory lists.** A shared kitchen trading as three brands
  at one door is three entries; don't adjudicate which is "real". The
  exception is the same listing twice — one point, identical hours, one name a
  prefix of the other — which becomes one entry, the fuller name, with the
  other marked `publish.status: "declined"` and the reason.
- **A parcel the resolver or the seeder refuses is not a page to force** —
  condominiums, addresses EAS can't join to a parcel, streets outside the
  city. The entry stays in the file with the reason, as in the news module.

## The file

`<source>/<date>.json` is a findings-shaped record of one read of the
directory, so `research/tools/resolve_eas.py` reads it unchanged: one entry per
San Francisco listing, `address_as_written` verbatim, `street_number` /
`street_name` / `street_type` parsed with the resolver's own
`parse_address` (a "1/2" or a trailing suite letter dropped first), and
`extra` holding what the page takes — `name`, `name_as_listed`, `cuisines`,
`opening_hours`, `geo`, and the listing's own locality and postal code.
`name` repairs the directory's title-casing (Bites writes "18Th St", "Kfc",
"Ihop"); `name_as_listed` keeps its spelling. `publish` records which page
each entry went on, or why it didn't.

## A run

1. Fetch the directory twice and compare, per the rule above. Keep the
   listings whose locality is San Francisco; check the postal code too —
   Bites files three South San Francisco (94080) restaurants under the city.
2. Write `<source>/<date>.json`, then resolve and seed:

   ```bash
   python3 research/tools/resolve_eas.py report   merchants/<source>/<date>.json
   python3 research/tools/resolve_eas.py apply    merchants/<source>/<date>.json
   python3 research/tools/resolve_eas.py manifest merchants/<source>/<date>.json \
       --out research/manifests/<source>-<date>.json
   python3 scripts/seed_pages.py seed-list --manifest research/manifests/<source>-<date>.json
   ```

3. For each resolved entry, set that page's `occupants` (every entry from the
   source, replacing the last read's) and its `sources` entry for the
   directory, with `supports: "Current occupant"` and `retrieved` set to the
   day of the read. `listed_address` is the listing's own number on the
   page's own spelling of the street, or the other street for a corner
   building. Preserve each `data.json`'s indent (1 or 2 spaces).
4. Render, rebuild the derived indexes, and validate:

   ```bash
   python3 scripts/seed_pages.py render <each page>
   python3 scripts/seed_pages.py districts
   python3 scripts/build_sitemap.py
   python3 scripts/build_map_index.py
   python3 scripts/build_link_index.py
   python3 research/tools/check.py --index
   python3 scripts/validate.py
   ```
