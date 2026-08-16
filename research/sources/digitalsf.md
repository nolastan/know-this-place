# digitalsf — DigitalSF, San Francisco Public Library (primary)

> **Research dossier.** Rules: [../AGENTS.md](../AGENTS.md) · register:
> [../SOURCES.md](../SOURCES.md) · cited on pages by the source id `digitalsf`.
>
> - **Kind:** catalogued digital archive (photographs, city records, scanned documents) · **Tier:** primary · **Status:** mining
> - **Search-invisibility:** high — see the register for what that rates.
> - **Coverage:** harvested in full — 59,601 unique records. One of 44 collections extracted: **SFP 23, read whole — 1,165 records, 1,122 findings**.
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

| candidates | collection |
|---|---|
| 852 | San Francisco Subjects Photograph Collection (SFP 162) |
| 593 | **San Francisco Office of Assessor-Recorder Photographs (SFP 23) — done: 1,122 findings** |
| 210 | San Francisco Redevelopment Agency Records (SFH 371) |
| 151 | Tenderloin Times Photograph Archives (SFP 130) |
| 95 | Willard E. Worden Glass Plate Negatives (SFP 22) |
| 50 | James E. Gordon Color Slides of San Francisco Murals (SFP 173) |

**SFP 23 is done** — read whole on 2026-08-15, and it was the right one to
start with. The Office of Assessor-Recorder photographed properties *for
assessment*, so the collection is a per-building record by construction: 1,128
of its 1,165 records give a street number, a hit rate no other source here
comes near. Findings: [`../findings/digitalsf/sfp-23.json`](../findings/digitalsf/sfp-23.json).
The two largest remaining collections are too big for one session; split them
by decade.

### Cautions

- **Resolution runs about 69%, and the failures are the valuable part.** On a
  random sample of 140 candidates checked against `sf-eas-addresses`, 97
  resolved to an APN and 43 did not. The 31% that miss fall into three classes,
  and only one of them is an error:
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
- **This overlaps [`sfra-property-summaries`](../SOURCES.md) — check before
  extracting.** DigitalSF holds 866 San Francisco Redevelopment Agency Records
  (SFH 371) records in the sample alone, and the same SFH 371 collection is on
  the Internet Archive as `sanfranciscoredevelopmentagencyrecords`. They are two
  digitizations of one archive: DigitalSF has the catalogued photographs, the
  Internet Archive has the OCR'd paper forms. Neither supersedes the other, but
  a fact found in both is one fact, not two.

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

  **One collection of 44 has been extracted.** SFP 23 (San Francisco Office of
  Assessor-Recorder Photographs) was read whole — 1,165 records, 1,122 findings
  over 1,083 distinct addresses, in
  [`../findings/digitalsf/sfp-23.json`](../findings/digitalsf/sfp-23.json).
  None of them is resolved. The other 43 collections are untouched; by candidate
  count the next are SFP 162 (852), SFH 371 (210) and SFP 130 (151). Re-run the
  harvester to pick up records added since; it resumes from the stored token
  rather than re-downloading.

- **Verified:** 2026-08-15 (extracted SFP 23 in full: read all 1,165 catalogue
  records in the collection, wrote 1,122 findings, none resolved. Established
  three things the earlier pass had wrong — that `500$a` carries a second,
  structured address and an assessor block, so the title-only candidate count
  under-read this collection by nearly half; that `269$a` collapses a date range
  to its first year and `907$a` flags only 115 of 298 imprecise dates, so
  reading either alone promotes estimates to firm years; and that a collection's
  rights and personal-name profile can differ completely from the repository's —
  SFP 23 is 100% public domain and holds no personal names in `600`/`700` at
  all. Added [`../tools/digitalsf_extract.py`](../tools/digitalsf_extract.py) to
  make the next collection a shorter job.)

  Earlier, 2026-08-15: harvested the repository in full: 59,601 unique records,
  read 2,273 numbered-and-dated candidates out of them, resolved 97 of a random
  140 to an APN against `sf-eas-addresses`. Established that the advertised
  ~97,000-item figure double-counts overlapping sets, that sequential sampling
  misstates density by threefold, and that the 19th-century tail falls under the
  1909 renumbering rules.
