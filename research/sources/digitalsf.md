# digitalsf — DigitalSF, San Francisco Public Library (primary)

> **Research dossier.** Rules: [../AGENTS.md](../AGENTS.md) · register:
> [../SOURCES.md](../SOURCES.md) · cited on pages by the source id `digitalsf`.
>
> - **Kind:** catalogued digital archive (photographs, city records, scanned documents) · **Tier:** primary · **Status:** acquiring
> - **Search-invisibility:** high — see the register for what that rates.
> - **Coverage:** 4,500 of ~97,000 records harvested (Photographs 2,500 of 57,647; City Archives 2,000 of 6,867)
> - **Local corpus:** `research/corpora/digitalsf/` (`state.json` records the OAI resumption token per set)
>
> Update this dossier at the end of every pass — the `Verified:` line, the
> coverage note, and anything the pass learned about getting at the source.

- **What:** San Francisco Public Library's own digitization platform, holding
  roughly **97,000 catalogued items** across nine collections: San Francisco
  Historical Photographs (57,407), Government Documents (9,151), San Francisco
  History Center (7,987), Archives of the City and County of San Francisco
  (6,867), SFPL Neighborhood Branch Libraries (6,351), Digitized Books and
  Serials (4,557), Hormel LGBTQIA Center (2,727), Shades of San Francisco
  (2,041), Book Arts & Special Collections (10).

  Every item carries a full **MARC catalogue record**, which is what makes this
  worth mining: the address-level fact is in structured metadata rather than
  buried in OCR. The corpus is concentrated on the **redevelopment era** — a
  decade profile of 4,100 harvested records peaks hard at the 1960s (1,091) and
  1970s (1,031), with the 1950s and 1980s either side, and a thin 19th-century
  tail. The largest archival series are Redevelopment Agency project areas:
  Hunters Point Area A, Yerba Buena D-1, Diamond Heights B-1, Western Addition
  A-1 and A-2, Embarcadero-Lower Market (Golden Gateway), plus the neighborhood
  series of Shades of San Francisco (Western Addition, Mission, OMI, Filipino
  American, LGBTQIA).

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
- **Sets:** `Photographs` (57,647), `city` (6,867), `sfhistory`, `lgbtq`,
  `basc`, and a `TEST` set to ignore. Sets overlap: a record can be in both
  `lgbtq` and `Photographs`, so deduplicate on the OAI identifier.
- **Paging:** 100 records per response with a `resumptionToken`; the first
  response carries `completeListSize`. `research/corpora/digitalsf/harvest.py`
  does this with the 5-second delay and writes `state.json` per set, so a later
  pass resumes on the stored token instead of re-downloading.
- A full Photographs harvest is ~577 requests, so a little under an hour at the
  required delay. Budget for it; don't parallelize it.

### What is actually usable

The MARC fields that carry the payload:

| field | what it holds |
|---|---|
| `245$a` | title — **where an exact street number appears, when one does** |
| `269$a`, `260$c` | the year |
| `907$a` | the string `fuzzy date` when that year is approximate |
| `650$a` | subject heading, including a controlled **`Streets--<name>`** index |
| `540$a`/`$f` | rights, machine-readable in `$f` |
| `524$a` | the preferred citation, ready to print |
| `600`, `700` | personal names — see **People** below |
| `856$u` | the master image file |

**Measured density, on 4,100 records harvested from two sets:**

- **~1.2% carry an exact street number in the title** (32 of 2,500 in
  Photographs, 6 of 600 in City Archives — two independent stretches of the
  corpus agreeing). Across ~97,000 items that projects to roughly **1,100
  numbered, dated, citable records**. That is a good source by this module's
  arithmetic, not a thin one.
- **100% carry a four-digit year**, and **17.3%** are flagged `fuzzy date`, so
  better than four in five have a firm year. This is much better than the web
  interface suggests — the "undated"-looking display dates are a rendering
  artefact, not the record.
- **16.8% carry a `Streets--<name>` subject heading** — 147 distinct streets in
  4,100 records. These name a street without a number, so they are not page
  facts on their own, but they are the enumeration key: they let a pass sweep
  one street at a time instead of reading the whole corpus.

**Sampled:** `Woman on traffic light on 900 block of Valencia Street`, 1981
(block-level, not usable as an address); `This building is now the Gay Community
Center at 1800 Market Street`, 1978; `Construction at 1410 Innes Avenue`, 1970;
`Japantown 1715 Buchanan Street`, 1976; `1066 Palou Avenue entrance with damaged
and graffiti`, 1966.

### Cautions

- **Resolution is nearly free here, and that is unusual.** Eleven title
  addresses were checked against `sf-eas-addresses`: **ten resolved straight to
  an APN**, and the eleventh was correctly no-match because the title says it is
  in Norwalk. The corpus is 20th-century, post-dating the 1909 renumbering, so
  none of the traps in [loc-newspapers.md](loc-newspapers.md) — renumbering,
  Howard→South Van Ness, mangled OCR digits — apply. Still check the
  neighborhood field against the parcel; a street name can repeat across cities
  and this corpus contains non-SF material.
- **Rights are mixed and machine-readable — filter on `540$f`.** In the sample,
  **61% are `In Copyright`** and **39% are `No Copyright – United States`**. The
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

**41.8% of sampled records name a person** in `600` or `700`. Photographers in
`700$e=Photographer` are creators and may be credited. Everyone else — the
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

- **Coverage:** 4,500 records of ~97,000 harvested — `Photographs` 2,500 of
  57,647 (resumption token stored), `city` 2,000 of 6,867 (token stored),
  `sfhistory`/`lgbtq`/`basc` untouched. No findings extracted yet. The harvest
  is resumable: `python3 harvest.py <set> <max_pages>` picks up where it stopped.

- **Verified:** 2026-08-15 (prospecting pass: confirmed OAI-PMH access and
  robots.txt limits, harvested 4,500 records across two sets, measured ~1.2%
  exact-street-number density and 100% year coverage, resolved 10 of 11 sampled
  addresses to an APN against `sf-eas-addresses`. No findings file yet.)
