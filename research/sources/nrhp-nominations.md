# nrhp-nominations — National Register of Historic Places nomination forms (primary)

> **Research dossier.** Rules: [../AGENTS.md](../AGENTS.md) · traps:
> [../LESSONS.md](../LESSONS.md) · register:
> [../SOURCES.md](../SOURCES.md) · cited on pages by the source id `nrhp-nominations`.
>
> - **Kind:** PDF reports (federal nomination forms) · **Tier:** primary · **Status:** open
> - **Search-invisibility:** high — the listings are indexed everywhere; the forms are not. A search for a street number returns the Wikipedia list entry and the NPS map pin, never the paragraph inside the PDF that dates the building and names its architect.
> - **Coverage:** 54 of 165 San Francisco listings read — every one certified before 1980. 56 findings, 30 resolved, 25 published on 21 pages, 6 of them seeded.
> - **Local corpus:** `research/corpora/nrhp-nominations/` (one PDF and one `.txt` per reference number, plus `index-san-francisco.json` and `state.json`)
>
> Update this dossier at the end of every pass — the `Verified:` line, the
> coverage note, and anything the pass learned about getting at the source.

- **What:** The nomination form a property is listed on. One document per
  listing, written by whoever proposed it — a preservation group, a city
  agency, a state historic preservation office — and reviewed by the National
  Park Service. It is a **federal work product in the public domain**.

  What makes it a page source rather than a status index is section 8, the
  Statement of Significance, and section 7, the Description. Between them a
  nomination normally gives a **construction date**, the **architect or
  builder**, the **dated alterations**, and — where the building moved, burned
  or was rebuilt — the dates of that. The 1969 Form 10-300 even has a field
  called `SPECIFIC DATE(S)` that a nominator fills in with a year.

  San Francisco has **165 listings** in the NPS index, of which **134 carry a
  numbered street address**. The rest are ships in the Maritime collection,
  objects, districts and military reservations.

- **Where:** A page cites the nomination by its **reference number** — the
  six-digit (older) or nine-digit (post-2016) NRIS number. The stable public URL
  for the document is:

  ```
  https://npgallery.nps.gov/NRHP/GetAsset/NRHP/<refnum>_text
  ```

  which is both the URL that serves the PDF and the URL a reader can use.
  `npgallery.nps.gov` has **no robots.txt** (it 404s), and nothing about the
  service forbids automated retrieval.

### How to get at it

**The index is an ArcGIS query, and it is a point layer, so query it by
county.**

```
https://mapservices.nps.gov/arcgis/rest/services/cultural_resources/nrhp_locations/MapServer/0/query
  ?where=County%3D%27San+Francisco%27+AND+State%3D%27CALIFORNIA%27
  &outFields=*&f=json&returnGeometry=false&resultRecordCount=2000
```

One call, no paging at this size. It returns `NRIS_Refnum`, `RESNAME`,
`Address`, `City`, `CertDate` and `ResType` per listing — enough to plan every
batch without fetching a document.

- **`County='San Francisco'` beats `City='San Francisco'`.** The city query
  returns 165 and the county query 170; the five it adds are the Treasure
  Island and Yerba Buena Island listings, whose `City` is the island.
- **The index is not complete, and the gap is districts.** The San Francisco
  Civic Center (78000757) is a real, listed historic district with a
  99,000-character nomination, and it is **in neither query** — not by city,
  not by county, and not by a geometry envelope over the whole city. Three
  recent listings (100004869 Gran Oriente Filipino Hotel, 100009644 St. Luke's
  Episcopal Church, 100009717 Western Manufacturing Company Building) appear
  only in the envelope query, with every attribute blank. *Treat the index as
  the batch planner, not as the enumeration; a listing you know of and cannot
  find in it is still fetchable by reference number.*
- Fetch the PDFs at 2–3 seconds apart and extract with `pdftotext -layout`.
  53 of the 54 in the first batch had a usable text layer. Whole batch: about
  three minutes.
- `WebFetch` is no use here, as it is for every PDF source in this register.
  Fetch the bytes.

### What is actually usable

The form's own sections, and they changed twice:

| form | years | where the payload is |
|---|---|---|
| 10-300 (July 1969) | to about 1976 | `SPECIFIC DATE(S)` field, then a free-prose `STATEMENT OF SIGNIFICANCE` |
| 10-300 (Rev. 10-74) | about 1975–1980 | `SPECIFIC DATES` **and** `BUILDER/ARCHITECT` as adjacent fields — the densest single line in the source |
| 10-900 (from 1982) | 1980 on | same two fields, plus longer continuation sheets |

A worked example, from the Stadtmuller House (76000523, 819 Eddy Street):

> `SPECIFIC DATES BUILDER/ARCHITECT 1880 (Construction)` … "Designed by
> architect P. R. Schmidt, this building was constructed in 1880"

and one from the Mish House (79000534, 1153 Oak Street), which is the shape to
hope for — a dated move with the trade press quoted:

> "It was moved to this site in 1897. In September of that year this entry
> appeared in the *California Architect and Building News*, 'Oak and
> Divisadero. Moving a house. … Architect: MacDougall Brothers. Contractor:
> John H. McKay. Cost: $1700.'"

### Cautions

- **The address in the index is not always the address in the document, and the
  1973 Western Addition group is the reason.** Nine of the ten listings
  certified 8 March 1973 are Victorians the San Francisco Redevelopment Agency
  bought in project area A-2 and **physically moved** rather than demolished.
  The NPS index carries the address they were moved **to**; the form's own
  "street and number" is where they stood when it was written, months before
  the move. Reading either one alone puts the fact on the wrong parcel.

  | refnum | form's address | index address |
  |---|---|---|
  | 73000435 | 736–738 Franklin Street | 33–35 Beideman Place |
  | 73000436 | 848 Octavia Street | 45–57 Beideman Place |
  | 73000437 | 751 Turk Street | 1840–1842 Eddy Street |
  | 73000439 | 743 Turk Street | 1321 Scott Street |
  | 73000440 | 216–220 Elm Street | 1331–1335 Scott Street |
  | 73000441 | 1350–1362 Scott Street | 1239–1245 Scott Street |
  | 73000442 | 770 Turk Street | 1249–1251 Scott Street |
  | 73000443 | 1624 Post Street | 1813–1813B Sutter Street |
  | 73000444 | 773 Turk Street | 1735–1737 Webster Street |

  **Their stated destination blocks and lots are not reliable.** 751 Turk and
  743 Turk are both said to be going to Block 1127 Lot 15, and 736–738 Franklin
  and 848 Octavia both to Block 1100 Lots 31–33. These were intentions written
  before the move; the index address is what actually happened.
- **These forms date a building by its water connection, and it is a proxy,
  not a construction date.** The whole 1973 group rests on "the San Francisco
  Water Department records show this building as being connected to the water
  system in ⟨year⟩." That is a real, dated, checkable fact and it is worth
  publishing as one — but it is when the house got water, not when it was
  finished, and where the Junior League's *Here Today* is also quoted the two
  sometimes disagree by a decade (73000437: 1884 against 1875; 73000444: 1876
  against "late 1880's"). **Record both and set `conflict`.**
- **The OCR is 1970s typescript and it is bad.** "San Franctsco" for San
  Francisco, "1382" for 1882, "Emd Sales" for Enid Sales, checkbox glyphs
  scattered through every line. A year read out of running prose needs the
  `SPECIFIC DATE(S)` field or a second sentence to confirm it.
- **One document in the first batch has no text layer at all**: 77000334, the
  Mills Building and Tower. `pdftotext` returns 76 characters. It needs OCR or
  a person.
- **Half of every nomination is not about this building.** Sections 9 and 10
  are bibliography and boundary description, and the significance section
  routinely reaches for comparisons at other addresses — the Whittier Mansion's
  nomination dates the Flood mansion at 1000 California Street, the Phelps
  House's dates the Mish House. Those are real facts about *other* parcels and
  they are second-hand here; take them from the nomination that is about them.

### People

Nominations name people constantly, and most of them are **owners**, which the
module's privacy limits exclude. Nearly every 1973 Western Addition form gives
the Victorian's original owner by name, adds that they lived a few doors away,
and lists the absentee landlords who followed. None of that is taken.

What is taken is what the root [AGENTS.md](../../AGENTS.md) allows and this
source is rich in: **architects, builders, contractors and named firms** — Willis
Polk, McDougall Brothers, Woollett & Woollett, McLeran & Peterson, Bliss and
Faville, Clinton Day. Where a form's own `BUILDER/ARCHITECT` field names
somebody, that is the field to read.

### Citation label

```
National Register of Historic Places nomination, <property name>
(reference number <refnum>), National Park Service.
```

with `https://npgallery.nps.gov/NRHP/GetAsset/NRHP/<refnum>_text` as the query
URL. Worked example:

> National Register of Historic Places nomination, Stadtmuller House
> (reference number 76000523), National Park Service.

### Coverage

- **Read:** all 54 San Francisco listings certified before 1980, plus the
  Civic Center district (78000757) fetched but not read.
  [`../findings/nrhp-nominations/listed-1966-1979.json`](../findings/nrhp-nominations/listed-1966-1979.json)
- **Not read:** 111 listings certified 1980 or later — 1980-1989 (42),
  1990-1999 (17), 2000-2009 (22), 2010-2015 (15), 2016-2023 (15) — plus
  78000757 and the untextured 77000334. **The next batch is 78000757**, a
  district nomination naming buildings across the Civic Center, and then the
  1980s group, which is the largest and uses the 10-900 form with its
  `SPECIFIC DATES` / `BUILDER/ARCHITECT` pair.
- **A caution for the post-2016 group before anyone plans it:** the nine-digit
  reference numbers do **not** serve a PDF at the `_text` path — 100008228 (the
  Timothy L. Pflueger House) returns a 1.6 KB PNG placeholder. Those documents
  need a different route, and finding it is part of that batch.

- **Verified:** 2026-09-06 (promoted from the leads table, where it had been
  triaged on 2026-08-15 and left, and read end to end in the same run. Read 54
  nominations, found 56, resolved and published as recorded in the run's PR.

  What the run learned, beyond the cautions above:

  - **The triage note's "one nomination is one batch" was wrong, and usefully
    so.** One nomination is five prose pages and two or three facts; taken one
    at a time this source would be 165 sessions. The batch that works is a
    **certification-date era**, because the era is also the form revision, and
    the form revision is where the payload sits. 54 documents fetch in three
    minutes and read in one session.
  - **The index and the document disagree about the address, and neither is
    wrong.** See the 1973 table above. This is the first source in the register
    where the *listing's* address and the *building's* address are routinely
    different, and it is the reason to read the form's own header rather than
    trusting the index the batch was planned from.

  - **The renumbering guard refused twenty of these before a one-line
    exemption.** The tool declines a pre-1910 date resolved on the EAS join
    alone, because a pre-1909 number is not today's number. That is right for a
    newspaper of 1895 and wrong for a nomination of 1976 about an 1880 house:
    the address in the document is already a modern address. `resolve_eas.py`
    now reads **`extra.record_date`** — the year the record was written — and
    skips the guard where that is 1910 or later, while still printing the
    assessor's year for the parcel into the method, because the guard's other
    error mode (a modern number pointing at a later building on the lot)
    survives the exemption. It took this batch from 8 resolved to 30. Measured
    before it was wired in: 0 of 15,230 committed findings carried the field,
    so nothing already published changed.
  - **Eight of the published facts contradict the assessor, and all eight are
    the roll's 1900 default rather than a real disagreement.** The overlap scan
    flags a fact that predates the building the roll says is on the parcel, and
    for this source that fires constantly: the roll gives 1900 for the Octagon
    House (1861), the Feusier Octagon House (1857), the Stadtmuller House
    (1880) and the Atherton House (1881). Each is recorded as a conflict in the
    page's `.unknowns` rather than adjudicated, which is what the rule requires
    and also the honest reading — the assessor's 1900 is a placeholder, but
    saying so would be adjudicating.
  - **A "status index" lead can be a document source.** This was ranked first on
    the leads table for three weeks on the strength of a triage sample and never
    promoted. It should have been promoted the day it was triaged.)
