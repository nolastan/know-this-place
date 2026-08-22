# loc-newspapers — Historic newspapers, Chronicling America (secondary)

> **Research dossier.** Rules: [../AGENTS.md](../AGENTS.md) · register:
> [../SOURCES.md](../SOURCES.md) · cited on pages by the source id `loc-newspapers`.
>
> - **Kind:** newspaper OCR corpus · **Tier:** secondary · **Status:** open
> - **Search-invisibility:** high — see the register for what that rates.
> - **Coverage:** 10 batches / 58,620 pages scanned of a much larger archive.
> - **Local corpus:** `research/corpora/loc-newspapers/` (`state.json` records batches pulled)
>
> Update this dossier at the end of every pass — the `Verified:` line, the
> coverage note, and anything the pass learned about getting at the source.

- **What:** Full-text OCR of digitized San Francisco dailies from the Library
  of Congress. A local mirror lives in `research/corpora/loc-newspapers/` (not
  committed — see `.gitignore`; older clones hold it at `sources/loc-newspapers/`,
  which still works if it's already there); `state.json` records which batches
  have been pulled.
  Two titles are held so far, and their runs abut exactly, because the first
  was renamed into the second:
  - `sn94052989` — *The Morning Call* (San Francisco). Local coverage: 1890–1894.
  - `sn85066387` — *The San Francisco Call*. Local coverage: 1895–1896,
    1900–1902, 1905–1910.
- **Citation URL:** `https://chroniclingamerica.loc.gov/lccn/<lccn>/<YYYY-MM-DD>/ed-<n>/seq-<n>/`
  — one page image; it redirects to the current `loc.gov` viewer. The OCR file
  path maps to it directly: `sn85066387/1895/04/08-ed-1-seq-004.txt` →
  `.../sn85066387/1895-04-08/ed-1/seq-4/` (drop the leading zeros on `seq`).
- **Citation label:** name the paper, the issue date and the page —
  "*The San Francisco Call*, 8 April 1895, p. 4".

### What is actually usable

Four recurring columns carry address-level facts. Only two of them resolve to
a street number, which is the whole constraint:

- **"Building Contracts" / "Builders' Contracts"** — owner, contractor,
  architect, scope of work and cost. This is a **pre-DBI permit record**, and
  the richest thing in the corpus. But it identifies *new* buildings by
  metes and bounds ("east line of Folsom street, 85 feet south of Twentieth"),
  and only gives a street number for **alterations to an existing building**.
  Those numbered entries are few but excellent.
- **"Real Estate Transactions"** — near-useless as it stands. Entries are
  metes-and-bounds, and the recorded consideration is almost always a nominal
  `$10` or `gift`, not a price. The occasional entry that names a street
  number *and* a real price ("known as 1311 Alabama street, 40x100 feet, sold
  … for $2400") is worth having.
- **"Fire Alarms"** — date, time, alarm box, address, building form
  ("two-story frame") and the damage. Numbered, dated, and directly usable.
- **Classified ads** (to let, for sale, business notices) — the bulk of the
  hits. An ad is dated proof a building **stood at that number**, and often
  states its room count, form (cottage / flat / house) and cross-streets.

### Cautions

- **Verify the number against the cross-streets — the ads hand you the check.**
  Most entries say "bet. 19th and 20th" or "near Guerrero." Confirm that
  against the parcel's own coordinates before trusting the match. Where an
  entry gives lot dimensions, check them against the assessor's `lot_area`:
  25x125 against 3,125 sq ft is a parcel identification, not a coincidence.
- **Mission and Eureka Valley street numbers did *not* move in 1909.** The
  general warning in `san-francisco/corbett-heights/AGENTS.md` still holds for
  renamed streets, but every cross-street check run here resolves to today's
  number
  (824 Valencia "bet. 19th and 20th"; 3460 16th "between Church and Sanchez";
  2995 Folsom "corner 26th"). Check, don't assume, and don't extend this to
  other neighborhoods.
- **Streets were renamed — and one was renumbered with it.** Lexington Street
  was Lexington *Avenue*, and Cesar Chavez was **Army Street**; both are pure
  renames, so the numbers carry over.
  **South Van Ness is not.** It was Howard Street until 1932, numbered as a
  continuation of Howard through SoMa, and it was **renumbered** when it was
  renamed. Measured against the modern block faces in `3psu-pn9h` (94 ads in
  this corpus that give a Howard number *and* a cross street):

  | at cross street | historical Howard | modern South Van Ness |
  |---|---|---|
  | 13th | ~1616–1759 | 193–249 |
  | 16th | ~1919–2004 | 467–499 |
  | 20th | ~2400–2424 | 801–899 |
  | 21st | ~2505–2544 | 901–999 |
  | 22nd | ~2600s | 1001–1099 |
  | 24th | ~2752–2867 | 1201–1299 |

  The offset is roughly −1,600 over 17th–24th but only about −1,500 nearer
  13th–16th, so **subtracting a constant misplaces buildings by up to a whole
  block.** Convert per block face using the cross streets, or skip the street.
  A Mission-numbered "Howard street" address is never today's Howard Street
  (which ends at 13th) — but it is not that number on South Van Ness either.
- **The OCR is dirty, and it gets worse after 1906.** Expect mangled digits and
  interleaved column text. Read the surrounding lines before trusting a
  reading, and never take a number from OCR alone if the page turns on it.
- **A mention that predates the assessor's `year_property_built` is not proof
  the assessor is wrong** — the building may have been replaced. Record the
  dated fact, name the disagreement in `.unknowns`, and don't adjudicate it
  (the same rule as the Corbett Heights photographs).
- **People.** These columns are full of names — householders in want-ads,
  the dead in funeral notices, tenants in fire reports. Per the root
  `AGENTS.md`, take **contractors, architects and named firms**; leave
  residents, occupants and owners out, however long dead.
- **Coverage is partial.** `state.json` lists 10 batches / 43,769 pages of a
  much larger archive; `batch-index.json` enumerates what has not been pulled.
- **Verified:** 2026-08-04 (58,620 OCR pages scanned; 8,437 numbered-address
  mentions on streets that have pages, across 2,025 distinct addresses)
