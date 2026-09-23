# loc-newspapers — Historic newspapers, Chronicling America (secondary)

> **Research dossier.** Rules: [../AGENTS.md](../AGENTS.md) · traps:
> [../LESSONS.md](../LESSONS.md) · register:
> [../SOURCES.md](../SOURCES.md) · cited on pages by the source id `loc-newspapers`.
>
> - **Kind:** newspaper OCR corpus · **Tier:** secondary · **Status:** open
> - **Search-invisibility:** high — see the register for what that rates.
> - **Coverage:** 10 batches / 58,620 pages scanned for address mentions in August 2026 (no findings file; see below), and the *Call*'s Real Estate and Financial Section read in full for 1911 and 1912, into `findings/loc-newspapers/sn85066387-1911-real-estate.json` and `sn85066387-1912-real-estate.json`.
> - **Local corpus:** `research/corpora/loc-newspapers/` — `tar/` for the batch OCR tarballs, `txt/<lccn>/<yyyy>/<mm>/<dd>/ed-1/seq-N/ocr.txt` for the extracted pages. A fresh container has none of it.
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

### Getting at it (September 2026)

- **The per-page routes are walled; the bulk dump is not.** Every
  `chroniclingamerica.loc.gov/lccn/…/ocr.txt` page, the `loc.gov` JSON search
  and each batch's `BATCH.xml` now answer with a Cloudflare challenge (403, 429,
  or a 308 into `tile.loc.gov` and a 404). The OCR tarballs at
  `https://chroniclingamerica.loc.gov/data/ocr/<batch>.tar.bz2` download whole
  — about 800 MB each, one request — and so do the directory listings under
  `data/batches/<batch>/data/<lccn>/<reel>/`, whose folder names
  (`1911040801`) are the issue dates. One tarball took a 429 and came through
  on a retry ninety seconds later. Extract only the text:
  `tar xjf <batch>.tar.bz2 -C txt --wildcards '*.txt'`.
- **The August 2026 pass left nothing on disk.** Its `state.json` and
  `batch-index.json` went with its container, and it wrote no findings file:
  the 21 pages citing `loc-sf-call-*` ids are what it published, by hand. Its
  "58,620 pages" are the 1890s and 1900s years below, and its mention counts
  cannot be re-derived without re-fetching.
- **The citation URL still works for a reader.** The page URL
  `…/lccn/sn85066387/<date>/ed-1/seq-N/` opens in a browser behind the same
  challenge a person passes without noticing; cite it, fetch the tarball.

### Which batch holds which year

Mapped 2026-09-22 from the batch listings (`BATCH.xml` where it answered).
Issue counts per year; a year split across batches needs all of them.

| title | year | batches (issues) |
|---|---|---|
| *San Francisco Call* `sn85066387` | 1895 | `curiv_dogtown_ver01` (302) |
| | 1896 | `dogtown` (121), `carlsbad_ver01` (215), `joshuaTree_ver01` (30) |
| | 1897 | `fredsplace_ver01` (152), `idyllwild_ver01` (212) |
| | 1898 | `ahwahnee_ver01` (365) |
| | 1899 | `carlsbad` (46), `exeter_ver01` (181), `joshuaTree` (137) |
| | 1900–1905 | `albion_ver01`, `brea_ver01`, `carmel_ver01`, `darwin_ver01`, `felix_ver01`, `plasse_ver01`, `elderwood_ver02` (listings only; years not mapped), `quincy_ver01` (1901: 61, 1904: 60), `oasis_ver01` (1905: 89) |
| | 1906–1907 | `hercules_ver01` (275 + 92), `indio_ver01` (1907: 245), `mecca_ver01` (1907: 28) |
| | 1908 | `indio` (90), `jenner_ver01` (31), `llano_ver01` (245) |
| | 1909 | `jenner` (92), `llano` (61), `mecca` (151), `needles_ver01` (61) |
| | 1910 | `jenner` (90), `klamath_ver01` (122), `mecca` (122), `needles` (31) |
| | **1911** | `curiv_betteravia_ver02` (Jan–Aug, 5,901 pages), `curiv_angwin_ver02` (Sep–Dec, 2,996 pages) — **both on disk** |
| | **1912** | `angwin` (106), `calipatria_ver03` (183), `dardanelle_ver01` (64) — 9,693 pages, **all three fetched 2026-09-23**; nothing after 15 December |
| | 1913 | `dardanelle` (15), `grimes_ver01` (132) |
| *Morning Call* `sn94052989` | 1890–1895 | `kaweah_ver01`, `hemet_ver01`, `garberville_ver01`, `exeter`, `idyllwild`, `oakland_ver01`, `pescadero_ver01` |

### The 1911 Real Estate and Financial Section

Every Saturday the *Call* ran a one- or two-page **Real Estate and Financial
Section**; its header survives the OCR as `REAL ESTATE AND F…CIAL SECTION`
often enough to find it, and misspelt on three Saturdays out of 51. What it
carries, and what of it is usable:

- **Leases** — the bulk. A broker's column of "For X to Y, the store at N …
  street, five years, $…". Most name only private lessors and lessees, which
  are left out at extraction; what survives is the building's form ("the
  five story and basement brick building"), its name ("the Sachs building"),
  its use (hotel, lodging house, apartment house) or the firm that took it.
- **Sales** — each with the side of the street, the distance from a corner and
  the lot in feet and inches, which is the whole check: "25x137:6" against the
  roll's 3,436 sq ft settled two OCR-damaged numbers.
- **Auction lists** — the building's rooms and form with the lot, a week before
  the sale, and the result the following Saturday.
- **Building news** — new construction with architect and cost, usually by
  corner or "137:6 feet west of Mason" rather than by number. Unresolvable
  unless Planning's `name` field names the parcel.
- **The improvement-club column** — dated meetings at named halls: the Eureka
  Valley Improvement hall at 406 Castro, St. Joseph's hall on Tenth Street,
  the Oakwood Hotel at 1805 Divisadero.
- **Noise** — about half the numbered mentions: advertisers' own office
  addresses, land companies selling British Columbia and the Sacramento Valley,
  and in January and February a savings bank's list of named depositors,
  which is people and never taken.

### Cautions for the 1911 section

- **After 1909 the numbers are today's numbers** — and still more than half
  did not resolve. Of 135 findings, 66 have no EAS record at their number,
  nearly all downtown and South of Market, where a later building took several
  lots and their numbers with them (Market between First and Fifth, Mission,
  Kearny, Sansome, Howard). That is the design, not a defect.
- **The same building is printed two ways.** "The Sachs building" is 110 Geary
  in January and 140 Geary in March; a sanatorium's lease is 1811 Van Ness in
  November and 1110 Van Ness in December; St. Joseph's is 260 Tenth in July
  and 250 in November. Planning's name settled the first; the other two stay
  unresolved.
- **The roll dates the sales.** Three buildings the section sold in 1911 are
  dated 1911 by the assessor (1637 Clay, 3731 17th, 3949 18th) — new
  buildings on the market. Seven were rebuilt after 1911; those sales and
  leases were declined or framed as the building before.
- **A notable owner appears in a sale notice.** "The marine view residence of
  Alfred Sbarboro, 3160 Jackson" — taken as a notable past resident, the
  buyers left out.

### The 1912 section — what changed from 1911

Same Saturday section, same header (misspelt on eight Saturdays: `ANF`, `AMD`,
`AN D`, one with no header surviving at all — find those by the page after the
Bay-cities news). Three things differ, and the second is the one that pays:

- **From April it runs three pages, not two:** the city page, a country-land
  page (Stockton, the San Joaquin, Richmond — no city addresses) and the
  improvement-club column. Read the first and third; the second is advertising.
- **The building-news column is richer and is almost all corners.** 1912 is
  the pre-exposition building boom, and the column names the architect for
  most new construction — Bugbee & Bugbee's Landseer, Meussdorffer's Hotel
  Justice and Hotel Henry, Willis Polk's Insurance Exchange, MacDonald &
  Applegarth's Clift. None has a number. `research/tools/corner.py` places them
  on lot area and roll year: 19 of 27 unnumbered entries went onto parcels,
  five of them on pages that already credited the same architect.
- **The lease columns are thinner on firms and thicker on private leases**
  between named people — about 90 bare leases left out. What survives is the
  firms (Ford at 53 Bluxome, the U.S. government at 615 Sansome, Sutro & Co.
  moving 412 → 410 Montgomery) and named buildings.

### Cautions for the 1912 section

- **The same lease printed with two numbers again:** the Standard Wall Paper
  company's ground floor is 710 Mission on 19 October and 719 Mission on
  2 November; the South of Civic Center club's hall is 1423 Folsom in June and
  1243 Folsom in September. Both left unresolved with the conflict recorded.
- **The same building on two corners:** the Voorman hotel is the northwest
  corner of Mission and Fourth in September and the northeast in November.
  Every corner there has been rebuilt, so it did not need deciding.
- **A demolished building's corner can carry a page that already dates the
  predecessor.** 121 Golden Gate's page is the 2014 parcel but its National
  Register entry is the 1912 building; the Moose hall went on it as the 1912
  building, with the two accounts of its first use in `unknowns`.
- **Thirteen resolved findings were declined** because the roll dates the
  building on the parcel after 1912 — Metreon, 1970s complexes on Golden Gate,
  the 1924 building on the Realty Building's lot.

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
  dated fact, name the disagreement in `unknowns`, and don't adjudicate it
  (the same rule as the Corbett Heights photographs).
- **People.** These columns are full of names — householders in want-ads,
  the dead in funeral notices, tenants in fire reports. Per the root
  `AGENTS.md`, take **contractors, architects and named firms**, and leave
  the private householder out however long dead: a name this paper prints in
  passing is not a published record of a notable occupant, and nothing
  survives redacting it but a household at a street number. The root rules'
  affirmative carve-out — always take the notable past occupant — needs a
  source that *covers* the person, which a want-ad does not.
- **Coverage is partial.** `state.json` lists 10 batches / 43,769 pages of a
  much larger archive; `batch-index.json` enumerates what has not been pulled.
- **Verified:** 2026-08-04 (58,620 OCR pages scanned; 8,437 numbered-address
  mentions on streets that have pages, across 2,025 distinct addresses)
- **Verified:** 2026-09-22 (the *Call*'s 1911 Real Estate and Financial
  Section, every Saturday: 96 OCR pages, 633 numbered-address mentions, 135
  findings — 59 resolved (8 by hand, 6 of them through a building name in
  Planning's `name` field), 76 unresolved; 50 published on 48 pages, 18 of
  them seeded, 9 declined. Batch file
  `findings/loc-newspapers/sn85066387-1911-real-estate.json`.)
- **Verified:** 2026-09-23 (the *Call*'s 1912 Real Estate and Financial
  Section, every Saturday with an issue: 131 OCR pages over 50 Saturdays, 761
  numbered-address mentions, 126 findings — 71 resolved (19 by hand, all of them
  corners or building names), 55 unresolved; 58 published on 56 pages, 26
  of them seeded, 13 declined. Batch file
  `findings/loc-newspapers/sn85066387-1912-real-estate.json`.)
- **Coverage:** 1890s and 1900s years scanned in August 2026 for mentions only
  (above); **1911 and 1912 Real Estate and Financial Sections read in full**
  (1912 lacks 21 and 28 December, which no batch holds). Next: 1913
  (`dardanelle` has 15 issues, `grimes_ver01` 132), then the unscanned
  1897–1899 and 1903–1904 years. The 1911 batch's unnumbered building entries
  can now be placed with `corner.py`. The rest of the 1911 paper — 8,800 pages of news, where the
  fires and the building-permit lists are — is on disk and unread.
