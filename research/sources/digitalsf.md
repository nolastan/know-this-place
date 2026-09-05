# digitalsf — DigitalSF, San Francisco Public Library (primary)

> **Research dossier.** Rules: [../AGENTS.md](../AGENTS.md) · traps:
> [../LESSONS.md](../LESSONS.md) · register:
> [../SOURCES.md](../SOURCES.md) · cited on pages by the source id `digitalsf`.
>
> - **Kind:** catalogued digital archive (photographs, city records, scanned documents) · **Tier:** primary · **Status:** open
> - **Search-invisibility:** high — see the register for what that rates.
> - **Coverage:** harvested in full — 59,601 unique records. Twelve of 44 collections read whole, plus the 1,678 records that carry no `524$a`: **SFP 23** (1,165 records, 1,122 findings, 923 resolved, 919 published), **SFH 371** (2,421 records, 421 findings, 117 resolved, 116 published on 103 pages), **SFP 162** (34,738 records, 1,186 findings, 662 resolved, 545 published on 481 pages), **SFP 22** (433 records, 77 findings, 72 resolved, 60 published on 59 pages), the four small buildings collections read together — **SFP 42** (288 records, 58 findings, 56 resolved), **SFP 90** (285 → 14 → 11), **SFP 125** (253 → 36 → 11) and **SFP 169** (918 → 39 → 21), 99 published on 88 pages — and the four institutional collections read together: **SFP 26** (984 records, 17 findings, 12 resolved, 7 published on 6 pages), **SFP 84** (483 → 13 → 1 → 1), **SFP 103** (51 → 7 → 3 → 0) and **SFH 3** (1,603 → 3 → 2 → 0). The **no-`524$a`** batch is 1,678 records and zero findings.
> - **Local corpus:** `research/corpora/digitalsf/` (453 MB; `state.json` records the OAI resumption token per set)
>
> Update this dossier at the end of every pass — the `Verified:` line, the
> coverage note, and anything the pass learned about getting at the source.

- **What:** San Francisco Public Library's own digitization platform. The whole
  repository has now been harvested: **59,601 unique records**.

  **The website's collection counts do not add up to that, and it matters.**
  digitalsf.org advertises nine collections totalling roughly 97,000 items, but
  those are **overlapping views of one repository**, not disjoint collections —
  6,818 records sit in `Photographs`, `city` and `sfhistory` at once, and only 44
  records are `city`-only. Summing the collection counts double-counts most of
  the repository. Anyone planning work off the advertised figures will plan for
  about 60% more material than exists.

  Every item carries a full **MARC catalogue record**, which is what makes this
  worth mining: the address-level fact sits in structured metadata rather than
  buried in OCR. Candidate facts spread across the 20th century, peaking in the
  1950s (535) and 1960s (502) with the 1940s (282) and 1970s (252) either side,
  and a real 19th-century tail (45 in the 1880s, 11 in the 1890s).

- **Where:** A page cites the record page — `https://digitalsf.org/record/<id>`
  — for example `https://digitalsf.org/record/62884`. That is the URL a reader
  should be given. It differs from the harvesting endpoint below.

### How to get at it

**Harvest OAI-PMH. Do not scrape the search interface.**
`https://digitalsf.org/robots.txt` sets `Crawl-Delay: 5` and **disallows
`/search`**, which rules out the obvious approach and rules it out for good —
under "Corpora on disk" in [../AGENTS.md](../AGENTS.md) that is a limit to
honour, not an obstacle to route around. The sanctioned path is the OAI-PMH
endpoint, which is open, undisallowed, and purpose-built for exactly this:

```
https://digitalsf.org/oai2d?verb=ListRecords&metadataPrefix=marcxml&set=<set>
```

- **Metadata formats:** `marcxml`, `oai_dc`, `oai_openaire`. **Use `marcxml`** —
  `oai_dc` flattens away the subject headings, the rights statement and the
  preferred citation, which are three of the four reasons to come here.
- **Sets:** `Photographs` (57,647), `sfhistory` (7,987), `city` (6,867),
  `lgbtq` (2,727), `basc` (10), and a `TEST` set to ignore. **They overlap
  heavily** — 59,601 unique records against 75,238 set memberships — so
  deduplicate on the OAI identifier. `Photographs` alone is 97% of the
  repository; harvesting it first gets you almost everything.
- **Paging:** 100 records per response with a `resumptionToken`; the first
  response carries `completeListSize`.
  `research/tools/digitalsf_harvest.py <set> <max_pages>` does this with the
  5-second delay, retries transient 503s with backoff, and writes `state.json`
  per set, so a later pass resumes on the stored token instead of
  re-downloading.
- A full `Photographs` harvest is 577 requests — about 50 minutes at the
  required delay, and 453 MB on disk for the whole repository. Budget for it;
  don't parallelize it. The endpoint 503s sporadically under load, which is
  why the harvester backs off rather than aborting.

### What is actually usable

The MARC fields that carry the payload:

| field | what it holds |
|---|---|
| `245$a` | title — where an exact street number appears, when one does |
| `500$a` | **the archivist's own address note** — see below, this is the field the first pass missed |
| `260$c` | **the date. Use this one.** `269$a` is a single year and loses what `260$c` says |
| `269$a` | a year, collapsed — "between 1946 and 1951" arrives here as `1946` |
| `907$a` | the string `fuzzy date`. It flags *some* of the approximate dates, not all |
| `650$a` | subject heading, including a controlled **`Streets--<name>`** index |
| `540$a`/`$f` | rights, machine-readable in `$f` |
| `524$a` | the preferred citation, ready to print |
| `600`, `700` | personal names — see **People** below |
| `852$c` | the physical box and bundle |
| `856$u` | the master image file |

**`500$a` carries a second address, and it is better than the title.** In SFP 23,
686 of 1,165 records carry `Address. Box 3; Mission, 3232-3234.` and a further
129 carry `Block. Box 1; Block 196.` — an **assessor block number**, which is
half of an APN and the strongest lead a resolver can be handed. The title-only
candidate count under-reads this collection by nearly half, because SFP 23 files
much of its material as "1377 Fulton" with no street type at all and
`digitalsf_profile.py`'s regex requires one. `digitalsf_profile.py --candidates`
is still the right way to *size* a batch; it is not the right way to *read* one.
Use [`digitalsf_extract.py`](../tools/digitalsf_extract.py), which reads both
fields, cross-checks them, and flags the disagreements.

**`269$a` is a trap.** It reports one year even when the archivist recorded a
range. Measured on SFP 23: 298 of 1,165 records have an imprecise `260$c`
("between 1947 and 1951", "after 1947", "probably 1940s") and only **115** of
them are flagged `fuzzy date` in `907$a`. Reading `269$a` and trusting `907$a` —
which is what the first pass and the extract issue both prescribed — promotes
183 archivist estimates to firm years. Read `260$c`.

**Measured across all 59,601 records** (`digitalsf_profile.py`):

- **4.1% carry an exact street number in the title**, and **3.8% carry both a
  number and a year** — **2,273 candidate records**. A further 0.3% give a
  block ("900 block of Valencia Street") and are not addresses.
- **88.8% carry a four-digit year**, only **5.0%** flagged `fuzzy date`. This is
  much better than the web interface suggests: the "undated"-looking display
  dates are a rendering artefact, not the record.
- **10.6% carry a `Streets--<name>` subject heading**, indexing **511 distinct
  streets**. These name a street without a number, so they are not page facts on
  their own, but they are the enumeration key — they let a pass sweep one street
  at a time instead of reading the whole corpus.

**Do not sample this corpus sequentially to estimate density.** OAI-PMH returns
records in accession order, so any prefix is one or two accessions rather than a
cross-section. The first 2,500 records measured 1.2%; later 2,500-record bands
ran 0.2%, 5.8%, 6.9%. The prospecting pass initially reported ~1.2% on that
basis and was wrong by more than threefold. Measure on the whole harvest.

**Sampled:** `This building is now the Gay Community Center at 1800 Market
Street`, 1978; `Construction at 1410 Innes Avenue`, 1970; `Japantown 1715
Buchanan Street`, 1976; `1066 Palou Avenue entrance with damaged and graffiti`,
1966; `Tommy's Tavern, 1196 Geneva Avenue`, 1944.

### Batch unit: the archival collection

The natural unit is the **collection named in `524$a`** — 44 of them, and each
is also the citation a page will print, so one batch is one citable unit. The
`490$a` series field looks like a candidate and is not: it is empty for 1,846 of
the 2,273 candidates.

The candidate counts below are the title-only figures from
`digitalsf_profile.py`. Treat them as a *lower bound* on a collection's size:
SFP 23 was listed at 593 and produced 1,122 findings once the `500$a` address
note was read too. Size a session on the profile; expect more.

Counted over the **complete** harvest on 2026-09-02, reading the `500$a`
address note as well as the title — which is what `digitalsf_extract.py` does,
and roughly double what the title-only profile reports:

| addressed records | collection |
|---|---|
| 1,435 | **San Francisco Subjects Photograph Collection (SFP 162) — done: 1,186 findings, 545 published.** One session, not the three the decade split assumed |
| 1,128 | **Office of Assessor-Recorder Photographs (SFP 23) — done: 1,122 findings, 919 published** |
| 251 | **Redevelopment Agency Records (SFH 371) — done: 421 findings, 116 published** |
| 186 | **Tenderloin Times Photograph Archives (SFP 130) — not a batch. Skipped, and it stays skipped (#217).** Its addressed half is a newspaper's reporting on named living tenants at their own street numbers; see People below |
| 151 | **Judi Iranyi Photographs of the Tenderloin (SFP 179) — a batch after all (#217).** The count is wrong: **100 of the 151 are the phrase "4 Corner Friday"** read as street number 4. The real 52 are storefronts, and their people are unnamed. Ordered here on the uncorrected count; the row moves when the guard lands |
| 103 | **Willard E. Worden Glass Plate Negatives (SFP 22) — done: 77 findings, 60 published on 59 pages** |
| 67 | **Robert Durden Color Slide Collection (SFP 42) — done: 58 findings, 56 resolved** |
| 60 | **Lee Sims Photographs of Tenants and Owners in Opposition to Redevelopment (SFP 125) — done: 36 findings, 11 resolved** |
| 51 | **James E. Gordon Color Slide Collection of San Francisco Murals (SFP 90) — done: 14 findings, 11 resolved** |
| 43 | **James A. Martin Color Slides of San Francisco (SFP 169) — done: 39 findings, 21 resolved** |
| 30 | San Francisco Portrait Photograph Collection (SFP 136) — **still unread, and the reason is an assumption nobody has checked**: that a *portrait* collection raises the SFP 130 question. SFP 179 was written off the same way and was wrong. Measure its 30 addressed captions before deciding |
| 28 | **San Francisco Police Department Records (SFH 61) — done in the `tail` batch: 14 findings, 4 published.** Its addressed half is the 1906 ruins and the Bureau of Special Services' 1960s surveillance of bars |
| 28 | **Marilyn Blaisdell Photograph Collection (SFP 84) — done: 13 findings, 1 published.** A collector's miscellany, 1880s–1914, so eleven of twelve misses are the pre-1910 renumbering rule |
| 22 | **Michael Brailove Photographic Negatives (SFP 103) — done: 7 findings, 3 resolved, 0 published.** The densest thing left, and every address is a Western Addition building the A-2 clearances took |
| 21 | **San Francisco Unified School District records (SFH 3) — done: 3 findings, 2 resolved, 0 published.** Select on `"(SFH 3)"`; the bare string also matches SFH 371 and SFH 391 |
| 16 | **Dept. of Public Works Bureau of Engineering Photograph Records (SFP 26) — done: 17 findings, 12 resolved, 7 published on 6 pages.** The best of the four |
| 37 | **records with no `524$a` at all — done: 1,678 records, 0 findings.** Not a collection but six digital series, five of which are not photograph catalogues; every one of the 37 candidates is a false positive. Reachable with `--key 982` |

Recounted on 2026-09-02 with the extractor as it now stands; the four rows
marked done moved by a few records each against the earlier count, because the
guards added while reading them (a quoted work title, a hyphenated model
designation, a background landmark) take some candidates back out. The same
happened again on 2026-09-03: the plate-number, serial-number and clock-time
guards learned from SFP 84 and SFH 3 take back thirteen more.

**Size a batch on what the addressed half is *about*, not only on how many
records it has.** This table was ordered by addressed-record count and told the
next run to take SFP 130. Its 184 addressed captions are a neighbourhood
newspaper's photographs of the people of the Tenderloin: **177 of the 184 carry
a personal-name shape and 82 name a person in a role** — "250 Taylor Street
tenant [name withheld] pointing out damage to shower the landlord refuses to
repair", "Lao family moving out of their apartment at 355 Eddy Street due to
rent increases", "Tenderloin resident [name withheld] standing outside building
at 237 Leavenworth Street". (Withheld here, not in the source. This paragraph
quoted both names in full until #217; a dossier is as committed as a findings
file.) The name filter keeps every one of those
off a page, but `raw.text` carries the caption verbatim into a committed
findings file, and these are living people in rent strikes and evictions. **SFP
130 is not a batch and will not become one** (#217): redaction leaves the
sentence minus the name, which is still a household's eviction at a street
number, so the collection is skipped rather than mechanised around. What that
gives up is real and worth naming — the Palace Theatre at 53 Turk, the Lyric
Hotel at 140 Jones, Powell West at 111 Mason, Newman's Gym at 124 Leavenworth,
the Hibernia Bank as the Tenderloin police station at 1 Jones, the former KGO
building at 277 Golden Gate, and three fires (57 Taylor, 376 Ellis, 820
O'Farrell) — and none of it is the only record of its building. SFP 22, 42,
90, 125 and 169 were the buildings collections to take meanwhile, and all five
are now done; the next such run is SFP 84, SFP 103, SFH 3 and SFP 26 together.

**SFP 179 was written off with it and should not have been.** The dossier
called it "the same collection shape" on subject matter alone, and the addressed
half says otherwise. **100 of its 151 addressed records are the phrase "4 Corner
Friday"**, whose `4` the extractor reads as a street number — the same class of
false address as the plate numbers and clock times already guarded, and a guard
the SFP 179 run has to add first. The **52** that remain are storefronts:
Daldas Grocery at 200 Eddy, Radman's Produce Market at 201 Turk, El Castillito
Taqueria at 250 Golden Gate, Kim Huang Cafe at 325 Leavenworth, Em's Barber
Shop at 342 Jones, Angkor Laundromat at 353 Eddy, Hamlin Hotel at 385 Eddy,
Amigo's Market at 500 Ellis, Hotel Essex at 684 Ellis, Kelly Cullen Community
at 220 Golden Gate. Where a person is in frame the caption does not name them —
"Tenderloin barber standing in doorway of Eddy Barber Shop at 330 Eddy Street",
"Barista behind the counter of Cafecito at 406 Ellis Street", "Five restaurant
staff members pose for photo outside Yemen Kitchen at 219 Jones Street" — and
the limit bars naming, not photographing. One of the 52 carries a name, and it
is a forename. **It reads under the three policies already in the extractor**,
with no `raw.text` policy and nothing new but the guard.

**The four institutional collections are done, and the next run has no
buildings batch left.** SFP 26, SFP 84, SFP 103 and SFH 3 were read together on
2026-09-03 and yielded 40 findings and 8 published pages between them, on 3,121
catalogue records.

**And then there was no batch left at all.** Everything below SFP 26 in this
table, plus the thirty-odd collections too small to have a row in it, was read
on 2026-09-04 as the single `tail` batch — 36 collections, 7,261 records, 45
published pages. The only rows here still untouched are SFP 130, SFP 179 and
SFP 136. #217 has since closed SFP 130 unread, cleared SFP 179 as the next
batch, and left SFP 136 undecided and unmeasured. **The densest thing the tail
turned up was not in this table**, because the table is ordered by
addressed-record count and it has only ten records: SFH 611, the Junior
League of San Francisco's *Here Today* building research files, where ten of
ten records are one building at one street number, photographed in 1964-65.

**SFP 125 was on that list and half belongs on the other one.** Its *addressed*
half is unambiguously buildings — 60 records naming South of Market residential
hotels by name and number in 1970-71, weeks before they came down — but its
unnumbered half is the people of those hotels, and the two are in the same
collection. Reading it needed `named-buildings-only` **and** the personal-name
redaction described under People below. A collection can be a buildings batch
and a privacy problem at the same time; judge the addressed half separately.

An earlier version of this table listed the murals collection as **SFP 173**.
There is no SFP 173 in the harvest; the murals are **SFP 90**, and SFP 169 is
the Martin slides. Match on the `524$a` string, not on a remembered number.

**SFP 23 is done, with one loose end.** 28 of its published findings name a
page path that has no `data.json` — the source id is on no page in the street
directory, so `published` is false for them. Six more of the same shape were
just a wrong path (the fact was on the sibling page at the parcel's lowest
number) and are corrected. The 28 are #221; the two known reasons a resolved
parcel gets no page — `in_asr_secured_roll: false` and a condominium APN — are
both `declined`, not `published`.

Read whole on 2026-08-15, and it was the right one to
start with. The Office of Assessor-Recorder photographed properties *for
assessment*, so the collection is a per-building record by construction: 1,128
of its 1,165 records give a street number, a hit rate no other source here
comes near. Findings: [`../findings/digitalsf/sfp-23.json`](../findings/digitalsf/sfp-23.json).
**Size a batch on the addressed records, not the record count.** SFP 162 is the
largest collection here — 34,738 records — and this dossier told the next run to
split it by decade on that basis. It was wrong: 1,435 of those records carry a
street number, the extractor reads the other 33,303 in five seconds, and the
whole collection went from harvest to published pages in one session. What costs
a session is the *addressed* half — the EAS join, the seeding, the page writes —
so a collection is one batch until that number passes about fifteen hundred.

### Cautions

- **Resolution runs 69–82%, and the failures are the valuable part.** A random
  sample of 140 candidates checked against `sf-eas-addresses` resolved 97 and
  missed 43. Resolving SFP 23 whole did better — **923 of 1,122, or 82%** — and
  the difference is method, not luck: mapping the source's street spellings onto
  EAS's, and going back to `sf-parcels` for the parcel that exists now where
  EAS's `parcel_number` is retired, together recovered about 60 findings that a
  plain EAS join reports as demolished. Read "Resolving an address from this
  source" below before quoting a miss rate. The misses that remain fall into
  three classes, and only one of them is an error:
  - **Demolished.** A cluster of 1964 records — 682 Guerrero, 1056 Geary, 329
    Divisadero, 1832 Fillmore, 1057 Powell, 1109 Golden Gate, 888 Eddy, and
    770 Turk twice — are Western Addition addresses that no longer exist in EAS
    *because the buildings were cleared*. Under "The evidence bar" in
    [../AGENTS.md](../AGENTS.md) no EAS record means no page, so these become
    street-hub facts. They are also the single most valuable thing in this
    corpus: a photograph of a building that no longer exists, dated, at a number.
  - **Pre-1909 numbering.** The 19th-century tail is real — 449 Pacific (1895),
    1123 California (1887), 819 Clay (1903), 320 Market (1907) — and for those
    the renumbering traps in [loc-newspapers.md](loc-newspapers.md) **do** apply.
    An earlier version of this dossier said the corpus was 20th-century and the
    traps did not apply anywhere; that was wrong. Anything dated before 1910
    resolves under the newspaper rules, not these.
  - **False positives.** `Drive` is both a street suffix and a fundraising
    campaign, so "1944 War Fund Drive" and "1950 Red Cross Fund Drive" parse as
    addresses. `digitalsf_profile.py --candidates` flags any record whose street
    number equals its year as `check-not-an-address` — six records, half of them
    genuine (1977 Bush Street is a real address). Eyeball those six; don't
    filter them automatically. **None of the six is in SFP 23** — they sit in
    SFP 162 and the Bancroft / St. Ignatius material, so the trap is still
    waiting for whoever reads those.
- **Rights are mixed and machine-readable — filter on `540$f`, per collection.**
  Across the full harvest, **60% are `In Copyright`** and **40% are `No
  Copyright – United States`**, with 33 undetermined — but that whole-repository
  split says nothing about any one collection. All 1,165 SFP 23 records are `No
  Copyright – United States`, which is what you would expect of city government
  work. Check the collection, not the corpus. The
  In-Copyright statement restricts *publishing the photograph*: permission must
  be sought in writing from the Photo Curator, with SFPL granting it as owner of
  the physical item. It does not restrict the facts in the catalogue record — a
  date, a street number and a building name are facts, and this module extracts
  facts. **Do not reproduce a DigitalSF image on a page** regardless of the flag
  without a decision from a human.
- **A donor's or a photographer's `500$a` note is not the archivist's address
  note, and reading it as one invents addresses.** Two shapes, both measured:

  - **SFP 169 appends a geocode.** 549 of its 918 records end their donor note
    with a modern street address — "SPCA - Animal Shelter, 16th & Alabama,
    front lobby. 2500 16th St, 94103" — and that address is **where the camera
    was or roughly what the frame shows**, not a statement about a building.
    "SF Opera House from Franklin. 406 Franklin St" geocodes the viewpoint;
    "Elevated View Opera House & War Memorial. 1390 Market St" geocodes Fox
    Plaza. Where the donor *also* names a number in the descriptive half the
    two disagree about as often as they agree — 2324 against 2330 Chestnut, 230
    against 250 Brannan, 581 against 553 Buckingham. So the extractor reads the
    number the donor states in the descriptive half, keeps the geocode in
    `extra.donor_geocode_as_recorded`, and writes a conflict when they differ;
    it never treats the geocode as the address. **Taking the geocode would have
    produced roughly 300 confidently wrong findings** in a collection whose
    honest yield is 21.
  - **SFP 125's photographer's notes are roll-level.** 385 of its 431 note
    instances are on a note shared by more than one record — one note listing
    every building on a 36-frame roll, attached to all 36 frames. Read
    per-record it puts Jim's General Merchandise, the Imperial Hotel and the
    Panama Hotel at each other's addresses. **Use the title only for this
    collection.**

  The test before using any `500$a` as an address: count the distinct note
  strings against the record count. Roughly one note per record means the
  archivist wrote it about that item; far fewer means it belongs to the roll,
  the folder or the accession.

- **A caption's numbers are not all addresses, and four shapes cost real
  findings before they were caught.** Each is now a guard in
  [`digitalsf_extract.py`](../tools/digitalsf_extract.py):
  - **A hyphenated model designation.** "Sikorsky HH-52A Seaguard", "Coast
    Guard HC-130B Hercules", "Grumman HU-16 Albatross" — the word boundary
    falls inside the designation and the model's name reads as a street.
  - **An unhyphenated one**, which no rule can catch: "Beechcraft 35 Bonanza",
    "John Deere 93 Series A". Those are on the curated `NOT_A_STREET_NAME` list,
    which is how this project has always handled the residue.
  - **A quoted work title.** `"200 Years of Resistance" on Uganda Liquors`
    yielded *200 Years Street*. Quoted spans come out before the address match,
    the way parentheses already did.
  - **A landmark named for scale.** The BART construction slides photograph the
    street and name a tower to place it — "a construction crane with auger in
    the middle of the street. 555 Market in background", "View north towards
    1141 Market Street". Six of SFP 169's candidates were of this shape, and
    every one would have put a 1967 street photograph on a skyscraper's page.
    The qualifier can follow the number as well as precede it.

- **`269$a` promotes a decade to a firm year, and the extractor was letting
  it.** The `260$c` caution above is about a *range*; this is its other half.
  Where `260$c` reads "1920s", `\b1920\b` does not match inside it — the
  trailing "s" is a word character and defeats the boundary — so the decade
  fell through to the `269$a` fallback and was recorded as
  `date_precision: year`. Worse, `260$c` "19--" is the catalogue saying
  "some time in the twentieth century" and `269$a` answers **1900**, which is
  also the assessor's bucket year for "nineteenth century" and therefore the
  one year this project is least able to tell from a real one. Measured over the
  whole harvest: **731 records read "19--"**, 163 "1920s", 160 "1960s", 154
  "1970s" and so on — over 2,100 records that the pass would have dated to a
  year nobody recorded. **24 of them had already reached published pages** and
  are corrected. `269$a` is now used only where `260$c` is empty; a decade is
  `circa` with the decade as the date, and an open century is `unknown`. The
  timeline already renders and sorts "1930s" — `date_key` names the shape in its
  own docstring — so nothing downstream needed teaching.

- **The people are not always in `600$a`, and a photographer credit does not
  settle it.** SFP 23's `600`/`700` hold one corporate body; SFP 84 leaves
  `600` empty and files the family whose house it is under `700$a`, joined by an
  ampersand — "Winchell, Ezra & Winchell, Led F." — with `$e Photographer`,
  because they photographed their own home in the weeks after the fire. The
  role is not the test: a name written into a caption is a person in the frame
  whatever the record credits them for elsewhere, and "…home at 747 Baker
  Street" is a sentence about who lived at a street number. **`redact()` now
  reads `600$a` and `700$a` both**, splits ampersand-joined pairs, and strips a
  corporate qualifier before testing for the comma that distinguishes a person
  ("San Francisco Redevelopment Agency (San Francisco, Calif.)" has a comma and
  is not a person). 14,535 of the corpus's 22,360 `700` fields carry no role at
  all. The guard that keeps this from eating the evidence: **a bare surname is
  left alone when the next word says it is a place** — "Canterbury Hotel, 750
  Sutter Street" against a `700$a` of "Canterbury, Alan J.", or a street named
  for someone. Run over every findings file in the repo the widening changes
  eight quoted spans and takes nothing but names.

- **Three more shapes of number that are not an address**, each measured over
  the whole harvest and each now guarded:
  - **A plate number at the head of the title**, in a collection that numbers
    its plates. All fourteen of SFP 84's title-initial numbers are stereograph
    serials — "877 A view of San Francisco Bay", "3022 Ferry-boat entering
    Oakland slip", "1704 Mission Church, Mission Dolores" — and every genuine
    address in that collection is mid-caption. It is a per-collection switch
    (`COLLECTION_PLATE_NUMBERS`) because **779 titles corpus-wide open with a
    real street number**; as a general rule it would be a disaster.
  - **A serial introduced by "No." or "#"**: "Ridgepoint No. 2 Elementary
    School", "Pumping Station No. 2", "Lantern Slide No. 55 A", "Chinese San
    Francisco No. 9". 140 titles corpus-wide, and it is general.
  - **A clock time**, whose minutes read as a number over a street: "at 1:00
    P. M." yields *00 P. M*. Four titles, and the colon before the number is
    the tell — the same one-character test as the hyphen guard.

- **A run of buildings is written with a word between the numbers, and a
  hyphen-only pattern files the photograph on the wrong one.** SFP 26 prints
  "610 to 624 Anza Street", "183 to 94 Cook Street", "648 thru 622 Jerrold
  Avenue". Matching only the hyphen took the *second* number and lost the
  first — and on the Cook Street rows that second number is an abbreviated high
  end read literally: 94 for 194, 73 for 173, neither of which EAS holds.
  Eleven titles corpus-wide. The extractor now reads the whole construct, fills
  the short high end in from the low, and emits **one finding per printed
  number** per "A row of buildings is not a range" in ../LESSONS.md, keeping the
  caption's own words in `extra.address_as_printed`.

- **A year-shaped number with no street type is a year about half the time.**
  "1958 Bell 47G-2 N977B Helicopter" is a year and a make; "House of Prime Rib,
  1906 Van Ness" is an address. The standing guard — a number equal to the
  record's own date — catches neither, because a caption is free to date
  something else. The refusal is applied only to a donor's or photographer's
  free prose, where the equipment captions live, and not to a catalogued
  "<name>, <address>" title.

  **The standing guard was reading the wrong field, and the tail is where it
  showed.** It compared the number against `year_of(date)`, which returns the
  archivist's whole phrase for an imprecise date — "not before 1906", "between
  1985 and 1987" — and a phrase equals no street number ever. So the guard
  fired on "1966 Bayview-Hunters Point riots" dated `1966-09` and missed
  "Damage at 1st Street and Harrison from 1906 Earthquake and Fire" dated "not
  before 1906". It now compares against **every** four-digit year the date
  carries, which takes out 28 more candidates across the tail and, measured
  over every findings file in the repository, changes nothing already
  committed.

- **Sets overlap.** Deduplicate on the OAI identifier or you will double-count
  the Hormel and Shades material, which sits in `Photographs` and `lgbtq` both.
- **A block is not an address.** "900 block of Valencia Street" is the
  most common near-miss shape. It stays unresolved.
- **`fuzzy date` means what it says.** A record flagged in `907` is an
  archivist's estimate. Carry the flag through to the finding rather than
  silently promoting it to a firm year.
- **A name change in the extractor is a correction pass over what already
  shipped, and it is bigger than the one record that showed it.** Adding
  `Ruins of` to `CAPTION_PREFIX` was filed (#247) as recovering five building
  names in SFP 162. Re-running the extractor over that collection and diffing
  on `citation.url` — **not** on the finding id, which is positional and moves
  the moment a record is added or dropped — showed **93**: every caption-prefix
  and name-filter fix landed since the collection was read, not just the one the
  issue noticed. 44 of them were on published pages. So: when a name rule
  changes, re-run the affected batches and diff, rather than patching the
  records the issue happens to list. Merge the diff into the committed file
  (`extra.named_in_record` and the `The record names …` sentence only) — never
  regenerate it, or 1,186 hand-checked resolutions and 545 publish decisions go
  with it.

- **The same re-run also drops findings, and that is usually right.** Fifteen
  SFP 162 entries the current extractor no longer produces: thirteen are the
  people filter working — "ARTISTIC HOMES OF CALIFORNIA — Residence of Mr. W.
  MAYO NEWHALL, No. 1206 Post Street" is a person's house, and "4 P.M. Aug",
  "886 Cliff House" and "214 Carl Saxsenmeir" were never addresses — and two
  are the same address now folded onto a sibling record. All fifteen were
  unresolved, so nothing published depended on them.

- **A capitalized word is not a proper noun, and `is_named_building` used to
  assume it was.** "Large house at 3905 Clay Street" and "Residencial building
  in 907 Pine street" passed the filter — a BUILDING_NOUN plus one capitalized
  word is all it asked for — and the first of them reached a published page as
  a building's name. `GENERIC_QUALIFIER` is the fix, and it is a **closed list**
  for a measured reason: 234 stored names are an adjective plus a building noun
  and 232 of them are real ("Grand Theater", "Ideal Bar", "Imperial Hotel",
  "Sunset Market", "White Cleaners"), so no part-of-speech test separates them.
  Measured over every name in every findings file in the repository, the rule
  flips **2 of 1,001** — exactly the two above.

- **Two known regressions in the current name/address parse**, both found by
  that diff, both on entries no page carries. `Park View Hotel, 102 South Park`
  now parses the street as `SOUTH` + type `PARK` where the hand-checked entry
  has `SOUTH PARK` and no type; and `View from 624 Ashbury Street of three
  children…` keeps `View from` inside `address_as_written`. Don't adopt a
  re-run's address fields wholesale for this collection — take the names.

- **This overlaps the *SF Redevelopment Agency property summaries* lead — check
  before extracting.** That lead is in the leads table of
  [../SOURCES.md](../SOURCES.md); it has no source id yet because it has not
  been promoted. DigitalSF holds 866 San Francisco Redevelopment Agency Records
  (SFH 371) records in the sample alone, and the same SFH 371 collection is on
  the Internet Archive as `sanfranciscoredevelopmentagencyrecords`. They are two
  digitizations of one archive: DigitalSF has the catalogued photographs, the
  Internet Archive has the OCR'd paper forms. Neither supersedes the other, but
  a fact found in both is one fact, not two.

### Resolving an address from this source

Measured on SFP 23, resolved whole on 2026-08-15 with
[`../tools/resolve_eas.py`](../tools/resolve_eas.py). Four things cost findings
if they are skipped, and each one is a query, not a judgement call:

- **Map the source's street spellings onto EAS's before concluding an address
  is gone.** The archivist writes Bayshore Boulevard, O'Farrell, Sea Cliff and
  Embarcadero; EAS holds `BAY SHORE`, `OFARRELL`, `SEACLIFF` and
  `THE EMBARCADERO`. Squashing punctuation and spaces catches those four and any
  like them; Douglas for `DOUGLASS` does not squash and needs an explicit alias
  (`--alias DOUGLAS=DOUGLASS`), stated in the resolution method so it stays
  auditable. Fifteen findings in SFP 23 turn on this, and unmapped every one of
  them reads as a demolished building.
- **EAS's `parcel_number` is stale or missing often enough to matter.** 49 SFP 23
  findings — 5% — resolved only after the address's own coordinates went through
  `sf-parcels` for the active parcel containing them. Query the point at full
  precision: EAS address points sit centimetres from their parcel boundary, and
  rounding the coordinates to six decimals moves enough of them across it to
  lose the parcel.
- **A point that returns several active parcels is a condominium**, one parcel
  per unit — 18 SFP 23 addresses. Unless exactly one of them carries the number
  in its own address range, none of them is the building, and the directory
  contract in the root [AGENTS.md](../../AGENTS.md) defers it. A further 25 are
  classed `Condominium` on the roll outright.
- **The archivist's `500$a` assessor block is a check, not just a lead.** Of the
  166 SFP 23 findings carrying one, 156 reached a parcel and 153 agreed with it
  — including a block written without the letter of the lettered sub-block the
  parcel is in (2526 for 2526B), which is agreement, not a conflict. The three
  that genuinely disagree are recorded as conflicts on the finding.

Two shapes of address in this collection resolve to nothing and should not be
made to: a **range whose numbers now sit on several parcels** (39 in SFP 23 —
one page cannot hold a photograph of what is now three buildings), and the
**title-versus-note conflicts where both addresses are real today** (11). Where
only one of the two survives in EAS the catalogue title wins, because it is the
archive's own identification and EAS corroborates it — but say so in
`resolution.method` and leave the `conflict` on the finding.

### People

**32.9% of records name a person** in `600` or `700` — 19,598 of them. But
**`600`/`700` is not where the people are in every collection**: in SFP 23 all
566 of those fields hold one corporate body, "San Francisco (Calif.) Office of
the Assessor-Recorder", and there is not a single `600` personal subject. The
profiler's `named-person` column therefore fires on a third of SFP 23 and means
nothing. The people in that collection are in the **titles** — a 1951 storefront
lists its tenants, and some of them are individuals renting an office rather
than firms ("F. Justin McCarthy, M.D."). Check where a collection actually keeps
its names before trusting a flag about them.

Photographers in `700$e=Photographer` are creators and may be credited. Everyone else — the
`600` subjects, the donors quoted at length in `500` notes, the residents named
in Shades of San Francisco oral-history captions — falls under "Privacy — hard
limits" in the root [AGENTS.md](../../AGENTS.md). Take the building, the
business, the architect and the photographer. Leave the residents.

This bites hardest in the Redevelopment Agency series, which document
displacement: the sibling Internet Archive collection includes items titled
"Identified people relocated". The subject being historically significant does
not make the people in it fair game, and the displacement makes the material
more sensitive rather than less.

**The name filter keeps people off a page; it does not keep them out of the
repository.** `raw.text` is the caption verbatim, and it is committed. "Lee
Washington's room in Daton Hotel, 175 3rd Street, personal items atop dresser
next to sink" is a finding about a building and a sentence about a named
resident's belongings, and the privacy limits bind when the finding is written,
not when a page is. Two mechanisms, both now in the extractor:

- **Redaction.** A record's own `600$a` personal-name subjects are replaced in
  `raw.text` with `[name withheld]`, in every form the heading and the caption
  might use — as filed, flipped, surname alone, forenames alone, with the
  heading's dates stripped off. What is left still justifies the address, the
  date and the building's name, which is all `raw.text` exists for. It cannot
  catch a name the heading spells differently from the caption, and one record
  in SFP 169 proves it: the heading reads "Cresi, Dominic" and the caption
  "Dominic Cresci".
- **Dropping the note.** `COLLECTION_NOTE_POLICY` refuses to carry the leftover
  `500$a` notes into `extra.record_notes` for SFP 125 and SFP 169, whose notes
  are a photographer's and a donor's free prose about who is in the frame
  ("214, Lee Wash room Daton Hot.", "Doris Martin & son", "Reverend Fumio
  Matsui (in white robes)"), **and for all 36 tail collections**, where the same
  turned out to be true in every register the note can be written in. A donor's
  memoir of their own family ("Donor's mother Suwa… donor's father"), a police
  case note with a robbery victim's name and home apartment number ("EVELYN
  POWERS… Victim. 1900 Vallejo St. apt. #204"), the party to a 1941 collision
  with his street address, and a newspaper's copy naming the children at a
  blackboard. Two of the biggest collections in the archive keep their notes,
  because there they are archival housekeeping — "Sheet: S.F. Streets - Hayes",
  "See SFP22-0125". **The default is wrong for a caption collection**: judge it
  by reading `--report`'s notes before writing the file, not after.
  The record page is one click from `citation.url` if an auditor wants the
  original.
- **Both mechanisms have a limit, and SFP 130 is where it is** (#217, decided
  2026-09-05). They work because the name is *incidental* to what the caption
  says: take "Lee Washington" out of "Lee Washington's room in Daton Hotel, 175
  3rd Street" and a hotel, a number and a date survive. Take the name out of
  "250 Taylor Street tenant [name withheld] pointing out damage to shower the
  landlord refuses to repair" and what survives is still one household's
  dispute at one street number. **Where the caption is the person, no
  `raw.text` policy makes the collection readable, and the answer is to skip
  it** rather than build the policy. That was the decision on SFP 130; there is
  deliberately no `COLLECTION_RAW_POLICY` in the extractor.
- **Decide it per collection, on the addressed half, measured.** The same issue
  had SFP 179 down as SFP 130's twin, and reading it showed two thirds of its
  addressed count was a false address and the rest were shopfronts with
  unnamed people in them. Subject matter is not the test; the captions are.
- **A courtesy title is the one name shape narrow enough to redact blind.**
  `redact` can only reach a name the catalogue filed in a `600`/`700` heading,
  and captions name people the cataloguer indexed nowhere (#248).
  `redact_honorifics` closes most of that: a courtesy title or a rank —
  `Mr.`/`Mrs.`/`Miss`/`Dr.`/`Capt.`/`Rev.`/`Judge` and their siblings — in
  front of a capitalised run, with `Mr. and Mrs. X` bridged as one name.

  **What it caught, measured over every `raw.text` in every digitalsf findings
  file: 53 spans, 49 of them people.** Not four edge cases — 30 in SFP 162
  alone, and most of them the sharpest shape the privacy limits exist for:
  "ARTISTIC HOMES OF CALIFORNIA, Residence of Mr. WILLIAM HAAS, 2007 Franklin
  Street", "Residence of Mrs. Henrietta Lehe, 15 Cerritos Avenue", "1736
  Fitzgerald street, scene of the shooting of Mrs. Angela Archie", and — in a
  **published** finding — "in the home of Mr. and Mrs. Ferdinand Smith at 825
  Francisco Street". A named resident at their own street number, committed.

  **Two exemptions, both measured, and between them they take the false
  positive rate to zero on this source.** What follows the title reads as a
  firm under `is_named_building` ("Dr. Pepper Bottling Company", "Mrs. Biggs
  Bakery"); or the record's own `610`/`650` headings already file it as one —
  `Businesses--Andrews Diamond Palace.` is the catalogue saying "Col. Andrews
  Diamond Palace" is a shop, not a colonel.

  **It is safe here because `redact` is only ever called on this source, and it
  would be wrong almost anywhere else.** Run the same rule over the whole
  repository and it fires on "Dr. Carlton B. Goodlett Place" (a street), "Miss
  Smith's Tea Room" and "Mr. S Leather" (businesses), "Dr. William L. Cobb
  Elementary School" (a building), and on Dr. Tom Waddell, Dr. Arthur H.
  Coleman and Reverend Frederick Douglas Haynes — the civic figures the
  African American and LGBTQ context statements exist to document. **Don't
  lift it into `sf-context-statements`.**

  What it still cannot reach is a bare name with no title: "Lloyd W.
  Dinkelspiel", "William Chester", "Revels Cayton" survive, and a general
  capitalised-name detector would eat "Eagle Market" and "Shadows Restaurant",
  so that half stays open deliberately.

- **A name can sit outside `raw.text`.** `2786 Diamond Street. Mrs. Evers` was
  the *street name* of a finding — the caption's second sentence parsed as part
  of the address, so the owner's name reached `address_as_written`,
  `description` and `citation.label`, none of which the redactor looks at.
  Sweep those three fields as well as `raw.text` when a name rule changes; it
  was the only one in the source, and taking it out also made the finding
  resolvable for the first time (Glen Park, 2784 Diamond Street, published).

**A mural artist is a creator credit, and the only one this archive states.**
`700 $e mural artist` names the person who made the work at that address — the
same class of fact as an architect, and allowed for the same reason. 78 SFP 90
records carry one; exactly one of those also carries a street number.

- **Citation label:** the record's own `524$a`, with the item identified.
  Worked examples, both real:

  > [Identification of item], San Francisco Redevelopment Agency Records
  > (SFH 371), San Francisco History Center, San Francisco Public Library.

  > [Identification of item], Shades of San Francisco: Shades of LGBTQIA
  > (SFP 78), James C. Hormel LGBTQIA Center, San Francisco Public Library.

  On a page, name the collection and the year and link the record URL —
  "San Francisco Redevelopment Agency Records (SFH 371), San Francisco Public
  Library, 1970".

- **Coverage:** **the repository is harvested in full** — all five real sets,
  59,601 unique records, 453 MB under `research/corpora/digitalsf/`.
  `Photographs` 57,647 · `sfhistory` 7,987 · `city` 6,867 · `lgbtq` 2,727 ·
  `basc` 10, before deduplication.

  **Every collection in the archive that holds an addressed record has now been
  read, except the three blocked on #217.** Twelve were read on their own —
  SFP 23, SFP 162, SFH 371, SFP 22, then SFP 42, SFP 90, SFP 125 and SFP 169
  together, then SFP 26, SFP 84, SFP 103 and SFH 3 together — and the
  remaining **36 were read as one batch, `tail`**: 7,261 records, 188 candidate
  addresses, 137 findings, 45 published on 45 pages. What is left in the
  archive is SFP 130 (184 addressed), **skipped for good under #217**; SFP 179
  (151 reported, 52 real), **cleared to read by the same issue**; SFP 136 (30),
  still undecided and needing its captions measured rather than assumed; and
  128 collections that carry no addressed record at all.
  The table under "Batch unit" says what each yielded. Re-run the
  harvester to pick up records added since; it resumes from the stored token
  rather than re-downloading.

  **What is left, after #217.** SFP 130 (184 addressed) is **closed unread**:
  its captions are named living tenants and no redaction survives that. SFP 179
  is **the next batch** — 151 reported, 52 real once "4 Corner Friday" stops
  parsing as an address, and those 52 are Tenderloin storefronts. SFP 136 (30)
  is a *portrait* collection assumed to raise the SFP 130 question and never
  measured; measure it. Nothing else in the archive carries an addressed
  record: a corpus-wide address pass over all 59,902 records finds no candidate
  in any other unread collection.

  **The tail was one batch, and that is the shape to reuse.** 36 collections
  holding one to nineteen addressed records each are not 36 batches; reading
  them separately would have been 36 findings files, 36 register lines and 36
  dossier entries for 188 candidates. `digitalsf_extract.py` now takes a
  comma-separated list and resolves the description template and all three
  policies per record, so a set of collections is a batch whenever they are
  too small to be batches on their own.

  **The 1,678 records with no `524$a` are read and closed** (issue #220).
  `digitalsf_extract.py --key 982` reaches them, and `982$a` groups all 1,678
  into six digital series with nothing left over — `092$a` and `490$a` are
  empty on every one, so `982$a` is the only second key. **Five of the six are
  not photograph catalogues at all:** 958 records are newspaper *issues* (San
  Francisco Bay Times 854 including its Coming Up! years, The Spokesman 54,
  Hunter's Point Beacon 50), one record per issue with the paper's name and a
  date for a title and per-page TIFFs in `856$u`; 384 are Sanborn atlas page
  images, one per plate; 5 are Book Arts items. The sixth is the **San
  Francisco Public Utilities Commission (PUC) Digital Collection**, 331 Water
  Department photographs — a real photograph collection whose subject is the
  Hetch Hetchy system and the peninsula reservoirs, and which locates its
  in-city records by intersection ("Howard & 20th Sts.", "Market Street,
  opposite Spear Street").

  Across all 1,678: **zero `650$a Streets--` headings, zero `500$a` address
  notes, zero block notes.** The catalogue states no address for any of them in
  any field, and **all 37 title-parse candidates are false positives** — 23
  Sanborn front-matter pages printing the publisher's imprint (*"Sanborn-Perris
  Map Co. Limited, 115 Broadway, New York"*, the advertiser trap arriving
  through a title rather than a frequency count; EAS has no 115 Broadway, so
  they would have stayed unresolved) and 14 PUC captions where the number is a
  measurement or a sequence ("1/4 Mile Below Big Oak", "500 Ft. In", "Lantern
  Slide No. 55 A", "2 Miners in Tunnel"). Findings:
  [`no-citation-field`](../findings/digitalsf/no-citation-field.json), zero
  findings and a coverage note.

  **What the batch left behind is a lead, not a batch.** The three newspaper
  runs — the Bay Times from 1978, The Spokesman 1965–66, the Hunter's Point
  Beacon 1943–45 — are three search-invisible San Francisco papers digitized
  page by page with no OCR in the MARC. Reading them is an acquisition
  question, not a re-read of these records.

  **Where a record has no `524$a`, the citation is built to the same shape**:
  `982$a` (or `791$t`) names the digital series and `692$a` the holding centre,
  which gives "San Francisco Public Utilities Commission (PUC) Digital
  Collection, San Francisco History Center, San Francisco Public Library."
  `citation_of()` does this, and refuses a record that names neither rather
  than citing "the archive".

- **Verified:** 2026-09-04 (correction pass over SFP 162 and a redaction pass
  over the whole source; no new material read. Closed #247 and #248, both of
  which turned out to be several times the size they were filed at.

  **#247 said five recovered building names; re-running the extractor over SFP
  162 and diffing on `citation.url` showed 93**, 44 of them on published pages,
  because every caption-prefix and name-filter fix landed since the collection
  was read had gone unapplied to it. 42 timeline rows on 38 pages went from
  "Photographed." to naming the building. Two of the 93 were not names at all —
  "Large house", "Residencial building" — and `GENERIC_QUALIFIER` now catches
  them; measured over every name in every findings file, that rule flips 2 of
  1,001. The re-run also **drops** 15 SFP 162 entries, and 13 of those are the
  people filter working on "ARTISTIC HOMES OF CALIFORNIA — Residence of Mr. W.
  MAYO NEWHALL, No. 1206 Post Street".

  **#248 said four leaked names in the tail; the honorific rule finds 53 spans
  across the source and 49 are people** — 30 in SFP 162, including a named
  resident at their own street number in a published finding. One name was
  outside `raw.text` altogether, in `address_as_written` and `citation.label`,
  and taking it out made that finding resolvable for the first time: the Glen
  Park Nickelodeon, 1926, is now on 2784 Diamond Street.

  What both have in common is the lesson: **when a name rule changes, re-run
  the affected batches and diff, rather than patching the records the issue
  happens to list** — and diff on `citation.url`, because the finding id is
  positional and moves.)

- **Verified:** 2026-09-04 (read, resolved and published **the tail — 36
  collections in one batch**, everything in the archive that holds an addressed
  record except the three blocked on #217. 7,261 catalogue records → 188
  candidate addresses → 137 findings over 116 distinct addresses → 73 resolved,
  33 unresolved, 31 rejected → **45 published on 45 pages, 18 of them seeded by
  this run**; 28 declined. Three things this batch taught the tool. **The
  archivist's note is a privacy problem in a caption collection**, not
  housekeeping — a robbery victim's home apartment number, a donor's parents,
  the children at a blackboard — so all 36 take `drop`. **The year guard was
  reading the printed date phrase rather than the years in it** and missed
  every caption that names the year in words; widened, it removes 28 candidates
  and changes nothing already committed. And **`Ruins of` belongs in
  `CAPTION_PREFIX`** with `Exterior of` and `View of`: it recovers five real
  building names in SFP 162 that were being thrown away with the caption. Two
  things it taught about the city. **Dupont Street is today's Grant Avenue and
  the numbers carry over, but the buildings do not** — EAS holds no 1011, 1013,
  1017 or 714 Grant Avenue, and the Board of Health album photographs Chinatown
  facades in 1903, the year its own campaign demolished 160 buildings there.
  And **EAS files Buena Vista Avenue East and West under one `street_name`**
  with the direction in `address`, so `--alias "BUENA VISTA AVENUE W=BUENA
  VISTA"` resolves 737 correctly only because 737 is unique across both sides —
  check that before reusing it)
- **Verified:** 2026-09-03 (audit run, no new material read. Corrected **28 SFP
  23 findings that said `published` with no page at their path** (issue #221)
  and **two SFP 23 placements the block's number line refuses** (issue #222).

  **A corner parcel's page is not at the number the resolver formed the path
  from.** The site keeps one page per parcel, at the number the assessor files
  it under, and every one of the 28 had in fact been published — on the
  parcel's page one street over, at an address the finding never names. 700
  Montgomery is on the Washington Street page, 568 Sacramento on the Commercial
  Street one, 2034 Filbert on Pixley. Only `resolution.path` was wrong.
  `resolve_eas.py` already prefers an existing page when one exists, so this is
  residue from resolutions written before those pages were seeded; `check.py`
  now fails on it rather than leaving it to an audit.

  **Two placements were the neighbour**: 1435 17th Street sat on 1401–1423, a
  parcel short of the block face's end, and its photograph had been folded into
  the combined entry on that page (digitalsf-54653 is out of it); 1762 Great
  Highway sat on 1758 with 1760 in between. Both are now `unresolved`.)

- **Verified:** 2026-09-03 (read, resolved and published **the four
  institutional collections in one run** — SFP 26, SFP 84, SFP 103 and SFH 3 —
  and closed the **no-`524$a`** batch that issue #220 raised. 4,799 catalogue
  records → 40 findings → 18 on a parcel → **8 published on 7 pages**, 6 of them
  seeded for it, 10 declined. Findings:
  [`sfp-26`](../findings/digitalsf/sfp-26.json),
  [`sfp-84`](../findings/digitalsf/sfp-84.json),
  [`sfp-103`](../findings/digitalsf/sfp-103.json),
  [`sfh-3`](../findings/digitalsf/sfh-3.json),
  [`no-citation-field`](../findings/digitalsf/no-citation-field.json).

  **The batch that yielded nothing was the most useful one.** Issue #220 asked
  what the 1,678 records with no citation field are; the answer is that "no
  `524$a`" is a symptom rather than a collection, and the six series behind it
  are three newspaper runs, the Sanborn atlas plates, the PUC water-system
  photographs and five Book Arts items — of which only the PUC collection is a
  photograph catalogue, and none of the 1,678 states an address in any field.
  Every one of the 37 candidates the issue counted is a false positive. That
  closes a haystack the collection table cannot see.

  **The run's real find was a date defect, and it was on published pages.** The
  extractor read `260$c` to avoid `269$a`'s collapsed ranges, exactly as this
  dossier prescribes — but `\b1920\b` does not match inside "1920s", so every
  decade fell through to the `269$a` fallback and became a firm year, and
  `260$c` "19--" became **1900**. Over 2,100 records corpus-wide, **24 of them
  on published pages**, all corrected here along with their descriptions,
  citation labels and page source entries. This is the third distinct way
  `269$a` has cost this project a date; the field is now read only where
  `260$c` is empty.

  Four extraction guards and one privacy widening, all measured over the whole
  harvest before landing:

  - **A plate number at the head of a title**, per collection — all 14 of SFP
    84's are stereograph serials, but 779 titles corpus-wide open with a real
    address, so it cannot be general.
  - **A serial after "No." or "#"** — 140 titles, general.
  - **A clock time** — 4 titles, and the colon before the number is the test.
  - **A run written "N to M Street"** — 11 titles, now one finding per printed
    number with the abbreviated high end filled in from the low.
  - **`redact()` reads `700$a` as well as `600$a`.** SFP 84 files the household
    that photographed its own house under `700 $e Photographer` and leaves
    `600` empty, so the redactor could not see the names in seven captions of
    747 Baker Street. A photographer credit does not make a name in a caption
    something other than a person in the frame. A bare surname is left alone
    where the next word says it is a place, which is what keeps "Canterbury
    Hotel" and "747 Baker Street" intact.

  **One resolution was wrong in a way nothing checked.** 1458 Kirkwood Avenue is
  in EAS with coordinates and no parcel number, and the single active parcel its
  point falls in states its own range as 1470–1498 Kirkwood — the neighbour.
  `resolve_eas.py report` now raises this shape. It raises rather than decides
  because the blanket rule was measured first: it fires on **61 of 582**
  point-placed resolutions across the repo and most of those are right, since
  sf-parcels' address range is routinely narrower than the EAS numbers a parcel
  holds. The 61 are #222.

  **SFP 103 is the collection this archive is for and the one that publishes
  nothing.** Fifty-one negatives of the Western Addition in 1964, the year
  before the A-2 clearances: four of its seven addresses are gone from EAS, and
  the three that resolve sit on buildings the roll dates 1973, 1974 and 1975 —
  the replacements, carrying the reissued numbers. All three declined. Freedom
  House at 1832 Fillmore Street, the Temple Theater at 1745 Fillmore, the
  Paradise Inn at 949 Fillmore and Eddie's and Bizon's used-furniture stores on
  McAllister are now indexed by number and date only in the findings file.)

- **Verified:** 2026-09-02 (read, resolved and published **the four small
  buildings collections in one run** — SFP 42, SFP 90, SFP 125 and SFP 169:
  1,744 catalogue records → 147 findings → 99 on a parcel → **99 published on
  88 pages**, 34 of those pages seeded for it. Findings:
  [`sfp-42`](../findings/digitalsf/sfp-42.json),
  [`sfp-90`](../findings/digitalsf/sfp-90.json),
  [`sfp-125`](../findings/digitalsf/sfp-125.json),
  [`sfp-169`](../findings/digitalsf/sfp-169.json).

  **Four small collections is the right size of run here, and the reason is the
  extractor.** Each one needed a `COLLECTION_VOICE` sentence and a name policy
  before it would run at all, and each one taught a guard the next three then
  got for free — the quoted work title from SFP 90, the roll-level note from
  SFP 125, the geocode and the model designations from SFP 169. Read singly
  that is four runs paying the same setup cost four times.

  Five things learned, all now cautions above:

  - **The donor geocode in SFP 169 is a viewpoint, not an address** — 549
    records carry one and it disagrees with the donor's own stated number about
    as often as it agrees. Taking it would have manufactured about 300 findings
    in a collection whose honest yield is 21.
  - **SFP 125's photographer's notes are roll-level** — 385 of 431 instances
    are shared across records, so per-record reading cross-files every hotel on
    a roll.
  - **Machinery, quoted work titles and background landmarks all parse as
    addresses.** Six BART construction slides would have put a street
    photograph on a skyscraper's page.
  - **`raw.text` carries people into the repository even when the page never
    sees them.** SFP 125 is a buildings collection *and* a privacy problem;
    both are handled at extraction. #217 settled the harder case the same way
    it was asked: SFP 130 is skipped because redaction leaves the household,
    and SFP 179 turned out not to be that case at all.
  - **The extractor's street-type map had drifted from the site's.** It was
    missing `PARK`, which `scripts/seed_pages.py` has carried all along, so
    "2 Clinton Park" came back as a street the city does not have. EAS files it
    as street_name CLINTON, street_type PARK.

  The unresolved half is the interesting one and it is concentrated: **25 of
  SFP 125's 36 findings did not resolve, and 10 of those are South of Market
  residential hotels EAS no longer holds** — the Milner, the Panama, the Mars,
  the St. Regis, the Imperial at 140 4th Street, 789 Howard, 286 Second Street,
  175 3rd Street, 115 Market, 252 6th Street. They were photographed in October
  1970 and cleared for Yerba Buena within a few years. Under "The evidence bar"
  no EAS record means no page, so the best record of those buildings in this
  archive stays in the findings file.)

- **Verified:** 2026-09-02 (read, resolved and published **SFP 22, the Willard
  E. Worden Glass Plate Negatives**, whole: 433 records → 77 findings → 72 on a
  parcel → **60 published on 59 pages** in #218, 50 of them seeded for it, 12
  declined. Findings:
  [`../findings/digitalsf/sfp-22.json`](../findings/digitalsf/sfp-22.json).

  It is the first collection here that is a **developer's record of a tract
  going up**: Worden photographed Ingleside Terraces and Jordan Park house by
  house between 1911 and 1915, and four plates catch a house still under
  construction. Four things this collection taught:

  - **Every one of its 433 records is `No Copyright – United States`** — the
    only untouched collection in the table that is, and worth taking first for
    that alone.
  - **The caption tail is the owner about as often as it is anything.**
    "Residence of Mrs. Henrietta Lehe, 15 Cerritos Avenue", "Residence of Dr.
    Authur G White, 760 Victoria Street" — 21 of them, all dropped by
    `named-buildings-only`, which keeps **no** name at all in this collection.
    That is the correct outcome, not a failure of the filter: Worden was
    photographing houses, and the only names in the captions are the people who
    owned them.
  - **A caption's district heading reads as a building name.** Every plate ends
    "in Ingleside Terraces", `terrace` is a `BUILDING_NOUN`, and the filter kept
    "Ingleside Terraces" as the building on sixty pages until `business_names`
    was given the record's own `650$a Districts--` headings the way it was
    already given its `Streets--` ones.
  - **The archivist's `500$a` note carries the readdressing.** The plate headed
    "299 Moncada Way" adds "Now the address is 101 Paloma Avenue", and 299
    Moncada Way has no EAS record at all — the Russian Hill "site of today's #N"
    rule, arriving from a photo archive rather than a survey. Resolved on the
    number the record gives for today.

  **Twenty of the sixty published findings are dated the year the assessor says
  the house went up**, which `--overlap`'s roll-year scan flags and which is
  here the fact rather than the defect: the photographs *are* of the tract being
  finished. Each says so in its publish note.

  Two tool defects surfaced and are fixed: `resolve_eas.py manifest` built a
  seeded page's street identity from the finding's recorded street rather than
  the resolution's `eas_address`, so the readdressed corner house produced a
  manifest entry reading `street_slug: paloma-avenue` with `street_name:
  MONCADA`, no coordinates and a `KeyError` in the seeder; and
  `check.py --overlap` reported all 60 of this batch's own entries as duplicates
  of themselves, because it recognised the batch's writes by description text
  and the publisher trims the address out of a description before it goes on a
  page. It now matches on the source-id prefix.)

- **Verified:** 2026-09-02 (re-read **SFP 162** with the caption name filter
  fixed, per issue #216. The extractor learned three things — a lower-case
  street type in the title, a part-of-building phrase in front of a name, and
  the participle "located" left behind an address — and recovered **42 distinct building
  names on 53 findings** with nothing lost. 33 of them were on findings
  already published, and their pages now say what the photograph shows: the
  Bank of Canton at 743 Washington Street, Hamm's Brewery on Bryant, the Hotel
  Turpin and Moars Cafeteria at 17 Powell, the Ladies' Protection & Relief
  Society on Laguna, the Marines' Memorial Club on Sutter. The lower-case
  street type corrected **92 addresses, 92 citation labels and 67 resolution
  methods** across SFP 162, plus two findings in SFP 23 and one in SFH 371;
  47 page source labels were rewritten with it. No status changed:
  662 resolved, 545 published, as before.)

- **Verified:** 2026-09-02 (read, resolved and published **SFP 162, the San
  Francisco Subjects Photograph Collection**, whole: 34,738 records → 1,186
  findings → 662 on a parcel → **545 published on 481 pages** in #215, 235 of
  them seeded for it, 117 declined. Findings:
  [`../findings/digitalsf/sfp-162.json`](../findings/digitalsf/sfp-162.json).
  183 of the published entries name the building or business the caption names —
  the Castro and Grand and Granada theatres, the Hobart and Russ and Underwood
  buildings, forty-odd churches, the branch libraries.

  This is the first collection here that is **not** a survey of buildings. It is
  the library's general subject file, and four things follow from that:

  - **A subject file's unnumbered records are not about buildings at all**, so
    keeping them as unresolved findings buys nothing. 31,988 of 34,738 records
    give no street number, and the earlier default — keep every one as a stub so
    the haystack is not re-read — would have written a 9,000-entry findings file
    saying "the record names no street number" about a photograph of Stow Lake.
    `COLLECTION_UNNUMBERED_POLICY` in
    [`../tools/digitalsf_extract.py`](../tools/digitalsf_extract.py) now takes
    that per collection; the coverage block records the whole read either way.
  - **There is no one body that made these photographs**, so the description
    cannot name one. SFP 23 says "The San Francisco Office of the
    Assessor-Recorder photographed the property"; SFP 162 can only say
    "Photographed", plus the building where the caption names one. The
    `COLLECTION_VOICE` guard that refuses to run without a template for the
    collection is what made this a decision rather than an accident.
  - **Caption prose parses as addresses.** "23 April", "2 Engine", "1 Fire
    House", "32 Streetcar", "365 Club" — a month, a fire company, a numbered
    vehicle, a venue named for its street number. 37 of them, on top of the 70
    the year-as-street-number rule already caught. `NOT_A_STREET_NAME` in the
    extractor holds the list; extend it from `--report` on the next narrative
    collection rather than rediscovering it.
  - **Caption framing sticks to the building's name.** "Exterior of Ernie's
    Restaurant", "Former North Beach Branch Library", "Warehouse of Allegheny
    Ludlum Steel Corporation" — stripped now by `CAPTION_PREFIX`, and a fragment
    that is nothing but a building noun ("Building", "House") is dropped. The
    first pass over this collection left three shapes of framing behind, which
    #218 fixed and which are worth knowing before reading the next caption
    collection:

    - **A part of the building in front of the name** — "Main entrance to the
      Marines' Memorial Club", "Courtyard at the San Francisco Art Institute",
      "Lobby of the Hotel Turpin". `CAPTION_PREFIX` now strips an optional
      qualifier, a part-of-building noun and its preposition. None of those
      nouns is in `BUILDING_NOUN`, so the strip can never take a name's own
      head noun.
    - **The participle behind it** — "Bank of Canton located at 743 Washington
      street" leaves "Bank of Canton located" once the address is removed, and
      the lower-case word fails the all-capitalized test and takes the name with
      it. `TRAILING_LOCATIVE` strips it.
    - **A lower-case street type inside the address**, which is the one that did
      the most damage: see the next bullet.

    Together they recovered **42 distinct names on 53 findings** with nothing
    lost, and
    eight `BUILDING_NOUN` additions — institute, society, brewery, saloon, bar,
    mortuary, cafeteria, bookstore — each completing a family already in the
    list. **What was deliberately not added is `home`.** Fourteen dropped
    fragments end in it and most are firms ("Butler Funeral Home",
    "Currivan's Funeral Home") — but so are "Home of Charles Berta" and "Home of
    Katherine Modesti", which the same rule would have put on a page. A head
    noun that reads as a building in a firm name and as a dwelling in a
    resident's is not safe as a bare noun, whatever the ratio.

  - **The catalogue writes the street type in lower case about a third of the
    time, and the extractor could not see it.** `TITLE_ADDR`'s name token is
    keyed on a capital letter, so "743 Washington street" parsed as *743
    Washington*, with `street_type_not_stated` recorded about a record that
    stated it. **101 of SFP 162's 1,378 addressed records** were affected, and
    it cost three separate things: the type was missing from the finding, the
    orphaned "street" left in the caption blocked the name filter, and the
    resolution method said "the record states no street type" — which sent
    212 12th Street to the Avenue-or-Street tie-break for want of a word the
    record had printed. The parser now matches the type in its own right, in
    lower case, as an optional last token, and drops a sentence-ending full stop
    from a spelled-out one ("429 Montgomery street." is not the address). *A
    pattern keyed on capitalization is a claim about the source's house style;
    check it against the source.*

  **The expensive lesson was the 1909 renumbering, and it was caught in the
  audit rather than the resolver.** 42 findings dated before 1910 resolved on a
  clean EAS join: the number exists today, on a parcel, and nothing in the join
  can see that the numbering changed underneath it. Checked against the roll,
  **36 of the 42 sat on a parcel whose building the assessor dates *after* the
  photograph** — 760 Mission Street, photographed in 1867, on a parcel built in
  1989; 315 Montgomery, 1865, on one built in 1921; 120 Kearny, 1880, on one
  built in 1980. All 42 were pulled back to `unresolved`, taken off their pages
  and their 15 pages deleted. [`../tools/resolve_eas.py`](../tools/resolve_eas.py)
  now refuses any pre-1910 address outright and says what would unblock it, so
  the refusal is the tool's rather than the auditor's. SFP 23 and SFH 371 were
  checked for the same trap and have none.

  Two smaller ones. **A street alias must not collapse a post-direction.**
  `--alias 'BUENA VISTA WEST=BUENA VISTA'` looked like the Douglas/Douglass case
  and is not: EAS keeps the WEST in `address`, not in `street_name`, so the
  alias filed 737 Buena Vista Avenue West on Buena Vista Avenue — where the site
  already had a second page for the same building under another parcel, which is
  the duplicate in #201. The finding is declined and left for a person. And **a page in
  `scripts/render-backlog.txt` may have no timeline at all** — 420 Montgomery
  Street carries a permit history, 737 Buena Vista Avenue West carries none —
  in which case a photograph row has nowhere to sit and the finding is a
  decline, not a hand-edit. 1 Montgomery Street did have one, and its row and
  source were added to the HTML by hand.

  **The roll dates the building later than the photograph on 57 pages**, the
  same finding SFP 23 reported on 45. Each carries the SFP 23 wording in
  `.unknowns` — "The assessor dates the building to 1988, after this photograph
  was taken" — so a Built tag does not sit unexplained beside an older
  photograph.

  **The Photographs set alone holds every SFP 162 record**, so the `city`,
  `sfhistory` and `lgbtq` sets — harvested in this run to complete the
  repository — added nothing to this batch. A fresh worktree gitignores the
  corpus, but another worktree on the same machine usually has it: `cp -Rc` off
  it is a copy-on-write clone and saves the 70-minute `Photographs` harvest.)

- **Verified:** 2026-09-02 (read, resolved and published **SFH 371, the San
  Francisco Redevelopment Agency Records**, whole: 2,421 records → 421 findings
  → 117 on a parcel → **116 published on 103 pages** in #214, 51 of them seeded for it,
  1 declined. 49 name the building then standing — mostly Tenderloin residential
  hotels, plus the Japantown YWCA, the Miyako Hotel, Woolf House Apartments and
  the Western Addition Solar House. Findings:
  [`../findings/digitalsf/sfh-371.json`](../findings/digitalsf/sfh-371.json).

  **The corpus is gitignored, so a fresh worktree starts with no `state.json`
  and the whole `Photographs` set has to come down again** — 578 pages, 70
  minutes at the required 5-second delay, and it cannot be parallelized. Budget
  it as the first hour of any digitalsf run, or work in a checkout that already
  has the corpus.

  Three things this collection taught that SFP 23 could not, all of them now
  enforced in [`../tools/digitalsf_extract.py`](../tools/digitalsf_extract.py):

  - **A caption collection is not a signage collection, and the name filter has
    to know which it is.** SFP 23 titles are "address, shop sign", so the
    extractor's default — keep the leftover fragment unless something says it is
    a person — is right for them. SFH 371 titles are narrative: "1249 Scott
    Street home on dolly being pulled by bulldozer". Run the default over those
    and it returns 140 "firm names", most of them caption prose ("home on
    dolly", "under construction", "Adjacent") and four of them **individuals at
    public ceremonies**, which the privacy limits bar outright. Hence
    `COLLECTION_NAME_POLICY`: this collection keeps a fragment only if every
    word is capitalized, it carries no digits and one capitalized word is a
    building noun. That drops the people and the prose and keeps 56 real
    building names. It also loses names buried in lowercase caption ("Japantown
    bakery Benkyodo Company"), which is the right trade — a false keep here is a
    privacy failure, a false drop is one missing name.
  - **Records that photograph people, not places, should not become findings at
    all.** 234 of 2,421 have a MARC `600` personal-name subject or a personal
    title in the caption *and* no street number. With no number they can never
    become a page, so keeping them as unresolved findings buys nothing and
    carries named individuals into the repository. Skipped outright.
  - **The year-as-street-number trap is live here.** "Miss Chinatown 1967
    Marilyn Lew" parses as number 1967 on a street called Marilyn Lew. The
    cautions above already record the rule — a street number equal to the
    record's own year is not an address — but only `digitalsf_profile.py`
    enforced it; the extractor now does too.

  A fourth thing, not specific to this source: **the description the extractor
  writes is not the sentence that goes on the page.** The publisher trims it —
  the timeline already carries the date and the page is the address — so
  "The San Francisco Redevelopment Agency photographed the property at 1830
  Sutter Street in 1975-08" becomes "The Redevelopment Agency photographed the
  property, then the Japantown YWCA." That convention is why `check.py
  --landed` reported 116 of 116 here and 885 of 885 for SFP 23 as no-ops when
  every one was on its page; the check now also accepts the page citing the
  finding's own record URL, which is stronger evidence than matching text.

  What did not resolve, and why it is the interesting half: 257 records give no
  street number, **33 name an address EAS no longer holds because the building
  was cleared**, 6 name something the register does not treat as a street
  (Embarcadero Center, One Maritime Plaza, One Jackson Place, Ridgeview Terrace,
  Verona, and a "W 24th Street" that looks like a cataloguing error), 5 are
  ranges now split across parcels, 3 are condominiums. Those 33 are the most
  valuable records in the collection and the one class the evidence bar will not
  let onto a page.)

- **Verified:** 2026-08-16 (published SFP 23: 919 of the 923 resolved findings
  onto 882 pages in #117, 720 of them seeded from
  [`../manifests/digitalsf-sfp-23.json`](../manifests/digitalsf-sfp-23.json),
  and seven new neighborhood directories with them. Each fact is one
  `historical_record` entry on the page's single timeline, cited to the record's
  own `524$a`; the circa dates publish the archivist's phrase and the 14
  conflicts went into `.unknowns` unadjudicated. Learned two things worth
  carrying to the next collection. **EAS's stale `parcel_number` bites the
  publisher as well as the resolver** — 15 of the 723 parcels are filed in EAS
  under a retired APN, so a manifest built by looking EAS up on the active
  blklot silently loses them; go via the retired number EAS actually carries,
  and take the street from EAS rather than sf-parcels, which addresses 0067041
  as 841 Chestnut while every EAS address on it is on Lombard. **The roll dates
  the building later than the photograph on 45 pages** — the parcel was rebuilt
  between the assessor's camera and today, so a page needs to say so or a "Built
  1988" tag sits unexplained beside a 1951 photograph. Declined 4: one parcel
  disagreement a page already contradicts, and three parcels with no row on the
  secured roll, which the seeder will not give a page.)

  Earlier, 2026-08-15: resolved SFP 23 in full against `sf-eas-addresses`,
  `sf-parcels` and the 2025 secured roll: 923 of 1,122 findings placed on a
  parcel, 199 left unresolved with a reason. Established the four addressing
  facts under "Resolving an address from this source" above — the source's own
  street spellings, EAS's stale `parcel_number`, the condominium signal in the
  parcel map, and the archivist's assessor block agreeing with the parcel on 153
  of 156 checks. Wrote three conflicts the resolver found rather than inherited,
  where the recorded block and the resolved parcel disagree. Added
  [`../tools/resolve_eas.py`](../tools/resolve_eas.py), which does the join,
  the parcel confirmation and the conflict comparison for any findings file.)

  Earlier, 2026-08-15: extracted SFP 23 in full: read all 1,165 catalogue
  records in the collection, wrote 1,122 findings, none resolved. Established
  three things the earlier pass had wrong — that `500$a` carries a second,
  structured address and an assessor block, so the title-only candidate count
  under-read this collection by nearly half; that `269$a` collapses a date range
  to its first year and `907$a` flags only 115 of 298 imprecise dates, so
  reading either alone promotes estimates to firm years; and that a collection's
  rights and personal-name profile can differ completely from the repository's —
  SFP 23 is 100% public domain and holds no personal names in `600`/`700` at
  all. Added [`../tools/digitalsf_extract.py`](../tools/digitalsf_extract.py) to
  make the next collection a shorter job.

  Earlier, 2026-08-15: harvested the repository in full: 59,601 unique records,
  read 2,273 numbered-and-dated candidates out of them, resolved 97 of a random
  140 to an APN against `sf-eas-addresses`. Established that the advertised
  ~97,000-item figure double-counts overlapping sets, that sequential sampling
  misstates density by threefold, and that the 19th-century tail falls under the
  1909 renumbering rules.
