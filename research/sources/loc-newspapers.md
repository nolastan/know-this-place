# loc-newspapers — Historic newspapers, Chronicling America (secondary)

> **Research dossier.** Rules: [../AGENTS.md](../AGENTS.md) · traps:
> [../LESSONS.md](../LESSONS.md) · register:
> [../SOURCES.md](../SOURCES.md) · cited on pages by the source id `loc-newspapers`.
>
> - **Kind:** newspaper OCR corpus · **Tier:** secondary · **Status:** open
> - **Search-invisibility:** high — see the register for what that rates.
> - **Coverage:** 10 batches / 58,620 pages scanned for address mentions in August 2026 (no findings file; see below), and the *Call*'s Real Estate and Financial Section read in full for 1911 and 1912, as held for 1913, and for January–June 1910, into `findings/loc-newspapers/sn85066387-<year>-real-estate.json`.
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
| | **1910** | `jenner` (90), `klamath_ver01` (122), `mecca` (122), `needles` (31) — **all four fetched 2026-09-23**; January–June read |
| | **1911** | `curiv_betteravia_ver02` (Jan–Aug, 5,901 pages), `curiv_angwin_ver02` (Sep–Dec, 2,996 pages) — **both on disk** |
| | **1912** | `angwin` (106), `calipatria_ver03` (183), `dardanelle_ver01` (64) — 9,693 pages, **all three fetched 2026-09-23**; nothing after 15 December |
| | 1913 | `dardanelle` (15: 1–15 February), `grimes_ver01` (132: 16 July–8 December) — **both fetched 2026-09-23**; January, March to mid-July and the rest of December are in neither, and in no other batch: all 79 `curiv_` batch listings were checked for `sn85066387` on 2026-09-23 and every one that holds the *Call* is in this table |
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
  corner or "137:6 feet west of Mason" rather than by number. Placed by hand
  with `research/tools/corner.py` on lot area and roll year (see the 1912 and
  1913 notes below).
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

### The 1913 pages — what changed from 1912

The batches hold only **1–15 February and 16 July–8 December 1913**: 24
Saturdays, not 52. Three things differ from 1912:

- **The header goes after February.** "REAL ESTATE AND FINANCIAL SECTION"
  heads the page on 1, 8 and 15 February and then disappears. From July the
  realty news runs on one or two unheaded pages among the residence-park and
  country-land advertising (St. Francis Wood, Ingleside Terraces, Richmond
  tracts). Find it by its headlines — `SALES BY …`, `… LEASES MADE BY …`,
  `FEATURES OF SAN FRANCISCO'S BUILDING ACTIVITY` — not by the header, and
  skip the classified pages, which score high on addresses and carry nothing:
  a page with more than about 40 uses of "rooms" is want-ads. On 16 and 30
  August, when the paper ran ten to twelve pages, no realty page was found.
- **Far fewer numbers.** 186 numbered mentions on 32 pages, against 761 on
  131 in 1912; the brokers' columns give most sales as "the north line of
  Turk street, 180 feet east of Webster", so the corner-and-offset share
  rises to 37 of 59 findings. `research/tools/corner.py --to` lists the whole
  block face, and the sf-parcels shapes measure the offset (worked below).
- **Picture captions carry architects with no lot.** "A new apartment house
  at Hyde and O'Farrell streets. W. G. Hind, architect." Year and use alone
  do not place one; both 1913 captions stay `unresolved` with the likeliest
  parcel named.

### Cautions for the 1913 pages

- **The offset is the check where the lot is not.** The Ellsworth sale (1911)
  and the 24th Street and Mission Street sales (1913) were placed by
  measuring along the block face on the `acdm-wktn` shapes from the corner:
  the lot whose front begins at the stated distance is the parcel. Lots begin
  on round multiples of 25 feet from a 25- or 27:6-foot corner lot; an offset
  that falls on no lot line (80 feet east of Taylor, 1913) is a misprint or
  an OCR digit, and the entry stays unresolved.
- **Where the offset and the lot disagree, say so on the page.** The
  Ellsworth apartments are "147 feet east of Polk" and 45 by 128 feet; the
  only 45 by 128 lot on that block face begins 48 feet from Polk. The lot, the
  storeys and the unit count agree, so it was placed, and the disagreement is
  in the page's `unknowns`.
- **Pages confirm more often than not.** Of the 13 placements by hand, five
  landed on pages that already carried the same architect or owner from
  another source: Havens (the Flatiron Building), Smith and Stewart (the
  Metone), Blaisdell's Shreve factory, the Drexler–Colombo Building, and
  The Paul's 60 rooms.
- **A notable name on a vanished house goes on the lot as site history.**
  The Levi Strauss residence at Post and Leavenworth burned in 1906; the 1913
  sale notice is the published source that places it on the Matsonia's lot,
  so it is `building.site_before` plus a dated entry, not a
  `notable_residents` row.

### The 1910 section — what changed from 1911

- **Three pages a Saturday, found by the head and what follows it.** Only the
  first page carries `REAL ESTATE AND FINANCIAL SECTION` near its top; the next
  two are the rest of the section, up to the page headed `EVENTS IN THE COUNTIES
  BORDERING ON THE BAY`. Special Richmond (5 March) and Turlock (30 April)
  editions push the city pages later, so also take any non-classified page
  dense in broker vocabulary (lease, sold, architect, lot). A page with more
  than about 40 uses of "rooms" is want-ads, as in 1913.
- **The building-news column is three times as dense as 1912's**, about 150
  architect or corner passages in six months, and it is the section's real
  value: MacDonald & Applegarth, Bliss & Faville, D. H. Burnham & Co., Reid
  Brothers, Righetti & Headman, the Rousseaus, N. W. Sexton, Cunningham &
  Politeo. Placing all of them is more than a run. The January–June batch took
  the entries naming an architect, a building, an institution or a firm, and
  left the permits that name only a private owner.
- **Fewer numbers, more ranges.** The sale columns give flats as "1325-27-29"
  and the resolver finds many such ranges split across parcels today; about
  half the numbered entries have no EAS record at all (Western Addition and
  downtown lots taken by later buildings).

### Cautions for the 1910 section

- **The realty columns put the private buyer between the address and the
  price**, so a raw quote of fixed length carries the name. Cut or splice the
  quote round it (see LESSONS). About 30 of 172 needed it.
- **The same building is placed two ways again.** The Rousseaus' apartment
  hotel is the northeast corner of Pine and Leavenworth in their February list
  and the northwest in April and May; the Wolf company's building is the
  northeast corner of Bush and Mason and "50 feet east of Mason" in one issue;
  the Schmiedell estate's is the southwest corner of Post and Jones and "78 feet
  west of Jones" (the lot's frontage, as the parcel's exact 78 by 137:6 shows).
  The conflicts are stated on the pages.
- **A corner the city lists under one street only.** The Mission Turnverein
  (the Women's Building, 3541 18th) never appeared at 18th and Lapidge in
  `corner.py`; its page was found by name.
- **Planned storeys are not built storeys.** O. D. Baldwin's hotel (321 Grant)
  was let as eight storeys and the roll counts ten; the Sutter Hotel corner was
  planned at eight and has nine. Descriptions say "planned".
- **The Keystone, the Herald Hotel and 245 Leavenworth** were already on their
  pages from other sources and were declined. Eight placements landed on pages
  already crediting the same architect (3106 16th, 317 and 245 Leavenworth,
  3541 18th, 100 New Montgomery, 414 Mason, 524 Post, 1369 Hyde), which is the
  best check a corner placement gets.

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
- **Verified:** 2026-09-23 (the *Call*'s 1913 real-estate pages, every
  Saturday the batches hold: 32 OCR pages over 22 Saturdays, 186
  numbered-address mentions and 296 corner or architect cues, 59 findings — 25
  resolved (13 by hand), 34 unresolved; 21 published on 21 pages, 5 of them
  seeded, 4 declined. Batch file
  `findings/loc-newspapers/sn85066387-1913-real-estate.json`. Same day, the
  1911 batch's seven corner-located entries (#401): 4 resolved onto 3 parcels
  — 500 Ellis, 1580 Jackson (seeded; the Ellsworth), 1218 Haight (seeded; two
  sales of "No. 1210") — and 3 left unresolved with the parcel checks written
  in.)
- **Verified:** 2026-09-23 (the *Call*'s 1910 Real Estate and Financial
  Section, January–June: 84 OCR pages over 26 Saturdays, 393 numbered-address
  mentions and about 150 architect or corner passages, 172 findings — 76
  resolved (45 by hand), 96 unresolved; 73 published on 68 pages, 28 of them
  seeded, 3 declined as duplicates. Batch file
  `findings/loc-newspapers/sn85066387-1910-real-estate.json`.)
- **Coverage:** 1890s and 1900s years scanned in August 2026 for mentions only
  (above); **1910 read January–June**; **1911 and 1912 Real Estate and Financial Sections read in full**
  (1912 lacks 21 and 28 December, which no batch holds); **1913 read as far
  as the batches hold it** (1–15 February, 16 July–8 December); 1913's other
  months are in no batch on the bulk route. Next: **1910, July–December** (#404)
  (on disk in klamath, mecca and needles for a session that fetched them), then
  the unscanned 1897–1899 and 1903–1904 years. The weekly Building
  Contracts lists in 1911–1913 are metes-and-bounds and were read only for
  named buildings; they are the next `corner.py` batch. The rest of the 1911,
  1912 and 1913 paper — the fires and the building-permit lists — is on disk
  in a session that fetched it, and unread.
