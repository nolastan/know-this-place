# digitalsf — DigitalSF, San Francisco Public Library (primary)

> **Research dossier.** Rules: [../AGENTS.md](../AGENTS.md) · register:
> [../SOURCES.md](../SOURCES.md) · cited on pages by the source id `digitalsf`.
>
> - **Kind:** catalogued digital archive (photographs, city records, scanned documents) · **Tier:** primary · **Status:** open
> - **Search-invisibility:** high — see the register for what that rates.
> - **Coverage:** harvested in full — 59,601 unique records. Two of 44 collections read whole: **SFP 23** (1,165 records, 1,122 findings, 923 resolved, 919 published) and **SFH 371** (2,421 records, 421 findings, 117 resolved, 116 published on 103 pages).
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
| 1,505 | San Francisco Subjects Photograph Collection (SFP 162) — 34,738 records; too big for one session, split it by decade |
| 1,128 | **Office of Assessor-Recorder Photographs (SFP 23) — done: 1,122 findings, 919 published** |
| 251 | **Redevelopment Agency Records (SFH 371) — done: 421 findings, 116 published** |
| 186 | Tenderloin Times Photograph Archives (SFP 130) |
| 151 | Judi Iranyi Photographs of the Tenderloin (SFP 179) |
| 103 | Willard E. Worden Glass Plate Negatives (SFP 22) |
| 70 | James A. Martin Color Slides of San Francisco (SFP 169) |
| 70 | Robert Durden Color Slide Collection (SFP 42) |
| 60 | Lee Sims Photographs of Tenants and Owners in Opposition to Redevelopment (SFP 125) |
| 54 | James E. Gordon Color Slide Collection of San Francisco Murals (SFP 90) |

An earlier version of this table listed the murals collection as **SFP 173**.
There is no SFP 173 in the harvest; the murals are **SFP 90**, and SFP 169 is
the Martin slides. Match on the `524$a` string, not on a remembered number.

**SFP 23 is done** — read whole on 2026-08-15, and it was the right one to
start with. The Office of Assessor-Recorder photographed properties *for
assessment*, so the collection is a per-building record by construction: 1,128
of its 1,165 records give a street number, a hit rate no other source here
comes near. Findings: [`../findings/digitalsf/sfp-23.json`](../findings/digitalsf/sfp-23.json).
The two largest remaining collections are too big for one session; split them
by decade.

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
- **Sets overlap.** Deduplicate on the OAI identifier or you will double-count
  the Hormel and Shades material, which sits in `Photographs` and `lgbtq` both.
- **A block is not an address.** "900 block of Valencia Street" is the
  most common near-miss shape. It stays unresolved.
- **`fuzzy date` means what it says.** A record flagged in `907` is an
  archivist's estimate. Carry the flag through to the finding rather than
  silently promoting it to a firm year.
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

  **One collection of 44 has been extracted, and it is now resolved.** SFP 23
  (San Francisco Office of Assessor-Recorder Photographs) was read whole — 1,165
  records, 1,122 findings over 1,083 distinct addresses, in
  [`../findings/digitalsf/sfp-23.json`](../findings/digitalsf/sfp-23.json).
  **923 of the 1,122 are resolved** to 886 parcels and 889 page paths, 165 of
  which are pages that already exist; the other 199 are unresolved with a stated
  reason, 74 of them because the address no longer exists in EAS. **919 of the
  923 are published** on 882 pages in #117, 720 of those pages seeded for it; 4
  are declined with a reason. The other 43 collections are untouched; by candidate
  count the next are SFP 162 (852), SFH 371 (210) and SFP 130 (151). Re-run the
  harvester to pick up records added since; it resumes from the stored token
  rather than re-downloading.

- **Verified:** 2026-09-02 (read, resolved and published **SFH 371, the San
  Francisco Redevelopment Agency Records**, whole: 2,421 records → 421 findings
  → 117 on a parcel → **116 published on 103 pages**, 51 of them seeded for it,
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
