# Source register

Every source this project mines, in one table. **If it isn't here, it doesn't
exist** — a source with facts on published pages but no row is a bug, and
`python3 research/tools/check.py` will say so.

Each row's dossier (`sources/<id>.md`) holds the access notes, the cautions and
the coverage log. Sources are cited on pages by the `id` in the first column;
**ids are permanent** — changing one breaks every citation that uses it.

## Registered

| id | what | kind | search-invisibility | status | coverage so far |
|---|---|---|---|---|---|
| [`argonaut-sfhs`](sources/argonaut-sfhs.md) | *The Argonaut*, journal of the SF Historical Society | journal | high | open | 7 volumes read in full |
| [`celebrity-residence-guides`](sources/celebrity-residence-guides.md) | Notable-resident guides | web guides | low | done | 26 addresses, 25 resolved |
| [`corbett-heights-neighbors`](sources/corbett-heights-neighbors.md) | Corbett Heights Neighbors newsletter | newsletter | high | done | all 50 issues read (Nov 2023 – Sep 2026); 197 findings, 151 resolved, 115 published on 65 distinct pages. Exhausted until the association publishes again — roughly one issue a month |
| [`digitalsf`](sources/digitalsf.md) | DigitalSF — SF Public Library's catalogued digital archive | catalogued digital archive | high | open | harvested in full: 59,601 records; 8 of 44 collections read whole — SFP 23 (1,165 records → 1,122 findings → 923 on a parcel → 919 on 882 pages), SFH 371, the Redevelopment Agency Records (2,421 → 421 → 117 → 116 on 103 pages) and SFP 162, the Subjects Photograph Collection, the largest in the repository (34,738 → 1,186 → 663 → 546 on 482 pages, re-read once the caption name filter was fixed and 42 building names recovered onto 28 of them, then corrected again in #251 when a re-run showed the caption fixes had recovered **93** names in it rather than the five that had been filed, 42 of them landing as timeline rows on 38 pages), SFP 22, the Willard E. Worden glass plates of Ingleside Terraces and Jordan Park going up (433 → 77 → 72 → 60 on 59 pages), and the four small buildings collections read together in one run — SFP 42 (Durden slides), SFP 90 (Gordon murals), SFP 125 (Sims, the South of Market hotels before Yerba Buena) and SFP 169 (Martin slides), 1,744 records → 147 findings → 99 resolved → 99 on 88 pages; and the four institutional collections read together in one run — SFP 26 (DPW Bureau of Engineering, 984 records → 17 findings → 12 resolved → 7 on 6 pages), SFP 84 (Blaisdell, 483 → 13 → 1 → 1, the rest refused by the pre-1910 renumbering rule), SFP 103 (Brailove's 1964 Western Addition, 51 → 7 → 3 → 0, every resolution declined because the parcels carry the 1970s redevelopment buildings) and SFH 3 (school district, 1,603 → 3 → 2 → 0); plus the **1,678 records with no `524$a`**, read whole and closed with zero findings (#220) — six digital series, five of them not photograph catalogues, no address stated in any field. and the whole remaining tail read as one batch — **36 collections, 7,261 records → 137 findings → 73 resolved → 45 published on 45 pages**, of which the Junior League's *Here Today* building research files (SFH 611) are ten records, ten buildings, ten street numbers. and SFP 179, the Judi Iranyi Photographs of the Tenderloin, read under #217 after the dossier had written it off as a people collection (528 records → 29 findings → 25 resolved → **25 published on 24 pages**; its "151 addressed" was 100 records of "4 Corner Friday" read as street number 4, and the real count is 51). **One collection in the archive that holds an addressed record is still unread**: SFP 136 (30), a portrait collection assumed to raise the SFP 130 question and never measured. SFP 130 (184 addressed) is **closed unread** under #217 — its captions are a newspaper's reporting on named living tenants, and redacting the name leaves the household |
| [`hittell-1878`](sources/hittell-1878.md) | Hittell, *A History of the City of San Francisco* (1878) | book | medium | open | §12–14, 24, 27, 231 |
| [`loc-newspapers`](sources/loc-newspapers.md) | Chronicling America OCR — *Morning Call*, *SF Call* | newspaper OCR | high | open | 58,620 pages → 8,437 mentions, 2,025 addresses |
| [`sf-environmental-review`](sources/sf-environmental-review.md) | SF Planning environmental review documents (EIRs, initial studies, negative declarations) | PDF reports | high | open | **all 172 address-titled documents read**, in 93 projects, plus 165 projects out of the project-titled set — 916 findings, 637 resolved, 571 published. The 1975–2011 record of what stood on a site *before* a project, and the only source in the register that states the assessor's block and lot outright. Four batches: the sixteen outside downtown (61 findings, 29 resolved, 21 published on 13 pages), the earliest downtown reports of 1975–1982 (21 documents, 120 findings, 78 resolved, 73 published on 52 pages, 17 of them seeded), the downtown and South of Market projects of 1983–1991 (19 documents, 110 findings, 77 resolved, 59 published on 44 pages, 11 of them seeded) and the address-titled projects of 1995–2011 (37 documents, 147 findings, 96 resolved, 72 published on 43 pages, 12 of them seeded). Downtown is a different kind of document — its historic-resources chapters are rating indexes that give a building **name**, a street number and two survey grades for every building on and around the block, and its project-site chapters date every building the tower removed, building by building, in prose. From about 2000 the department stopped writing that itself and appended the historian's own report instead, and those appendices are the densest part of the document: the Carey & Co. Section 106 review bound into the 275 10th Street EIR dates twenty-nine properties around one block. A fifth batch takes the first group of the project-titled set: the **named single-site projects of 1974–1982** (36 documents, 59 findings, 43 resolved, 39 published on 20 pages, 2 of them seeded), and a sixth takes the second: the **projects whose titles carry a street address later than first position** (58 projects, 109 findings, 74 resolved, 73 published on 55 pages, 31 of them seeded). Those are the same kind of document as the address-titled downtown reports, named after the developer's project instead of the street — and the earlier batches' filter, a title beginning with a digit, could never reach them. A seventh batch takes the rest of the named single-site group — the **projects of 1979–2005 titled by project name**, 36 documents, 141 findings, 102 resolved, 98 published on 53 pages, 25 of them seeded by that run. Its richest documents are the Emporium site expansion (thirteen dated buildings on and around Jessie Street, all of them refused by the commercial condominium the block became), the Geneva Office Building demolition project (one City landmark documented from its 1900 groundbreaking to its closure after Loma Prieta) and the North Beach Hope VI survey, whose appendix evaluates 105 properties on Francisco, Mason, Taylor, Water and Vandewater Streets. An eighth takes the **institutional-campus group** — hospitals, universities, museums, libraries, churches, the zoo and the civic buildings around them, 38 documents in 35 projects, 169 findings, 139 resolved, 129 published on 37 pages, 17 of them seeded. A campus document names buildings and not street numbers, so the batch turns on whether the report prints an assessor block that is a single parcel: Laguna Honda, Grace Cathedral's close, the Zoo and the whole of Golden Gate Park each are, and each got one chronology; UCSF's Parnassus Heights and the University of San Francisco's block are many lots, and nothing on them resolved. Remaining: ~449 of the 617 project-titled documents are unread — 130 area and policy plans, 67 transportation and airport documents, 96 procedural notices, 35 documents about places outside San Francisco, and the finals and supplements of projects whose drafts are read |
| [`local-news`](sources/local-news.md) | Hoodline, Bay Area Reporter, SF Chronicle | news | low | reference | browsed per address, no corpus pass |
| [`sf-context-statements`](sources/sf-context-statements.md) | SF Planning historic context statements & surveys | PDF reports | high | open | 44 documents **and the 81-PDF DPR 523 survey-forms page** read. The survey forms are SF Planning's per-property record and answer #115: 583 per-address forms across two surveys — market-octavia-survey-forms 378 of 473 published on 374 pages, van-ness-auto-row-forms 94 of 110 on 92 pages — 472 published in all on 460 distinct pages, 260 of them seeded by that run and 242 of those in Hayes Valley. 43 of the 81 PDFs are Adobe PDF Packages whose forms are embedded files: `pdftotext` returns the same 621-character shell for every one of them and `pdfdetach` gets the forms out. What remains there is three district-level records and the dated alterations in 111 construction histories. 1 statement remains — the Market & Octavia survey (#115), still to acquire. The **South of Market Area statement is done**: 118 pages read 2026-08-25, then stranded on the abandoned branch of closed PR #161 because that session could not reach `data.sfgov.org`; recovered and published 2026-09-03 — 155 findings, 117 resolved, 103 published on 96 pages, 32 of them seeded by that run. It cites a separate South of Market Area Plan Survey (1,128 DPR 523 forms) as "attached" that is not in the PDF and is not collected. The eight-volume Architecture, Planning & Preservation Professionals biographies collection is **finished**. All thirty-nine with findings files are closed out: market-octavia-hcs 425 of 496 published, mission-dolores-hcs 66 of 83, van-ness-auto-row 352 of 453 on 133 pages, carnegie-libraries 1 of 2, north-beach-hcs 553 of 630 on 352 pages, japantown-hcs 83 of 125 on 53 pages, russian-hill-hcs 57 of 109 on 48 pages, parkside-hcs 147 of 160 on 142 pages, oceanside-hcs 20 of 32 on 19 pages, transit-center-district-survey 211 of 316 on 123 pages, showplace-square-survey 576 of 941 on 314 pages, sunset-builders-hcs 143 of 158 on 143 pages, ppie-marina-hcs 86 of 109 on 86 pages, earthquake-shacks 5 of 11 on 5 pages, neighborhood-commercial-hcs 76 of 99 on 75 pages, large-apartment-hcs 58 of 89 on 52 pages, flats-small-apartments-hcs 52 of 72 on 52 pages, umb-survey 159 of 200 on 159 pages, umb-survey-ratings 1,452 of 1,902 on 1,435 pages, new-deal-hcs 99 of 138 on 76 pages, african-american-hcs 180 of 248 on 174 pages, lgbtq-hcs 289 of 382 on 280 pages, russian-american-hcs 179 of 365 on 164 pages, victorian-era-styles 37 of 45 on 37 pages, progressive-era-styles 63 of 69 on 61 pages, early-settlement-era-styles 29 of 32 on 28 pages, modernistic-styles 20 of 25 on 20 pages, modern-postmodern-styles 182 of 224 on 177 pages, biographies-a-c 317 of 412 on 312 pages, biographies-d-f 138 of 208 on 138 pages, early-residential-development 18 of 26 on 18 pages, soma-filipino-heritage 73 of 153 on 63 pages, clubs-social-halls 38 of 53 on 41 pages, modern-architecture-landscape 273 of 466 on 268 pages, sexual-identity-subcultures 115 of 188 on 63 pages, counterculture-hcs 72 of 111 on 71 pages, biographies-g-i 115 of 176 on 115 pages, biographies-j-l 91 of 125 on 90 pages, biographies-m-o 158 of 247 on 157 pages, biographies-p-r 126 of 223 on 125 pages, biographies-s-u 75 of 152 on 74 pages, and biographies-v-z 43 of 96 on 43 pages; the LGBTQ+ Cultural Heritage Strategy was read in full and yielded nothing, recorded as a zero-finding batch. The 1990 UMB survey is finished — both its inventory forms and its 51-page appendix ratings table. The five-part styles series (Early Settlement, Victorian, Progressive Era, Modernistic, Modern & Postmodern) is complete. The Architecture, Planning & Preservation Professionals biographies are eight volumes and all eight are now read and published: 2,259 numbered-address mentions became 1,639 findings, 1,385 resolved and 1,063 published on 1,017 distinct pages. V-Z is the most duplicated volume in the set — 37 of its 82 resolved findings were already carried by the statement that had documented the same building first. M-O and P-R are the duplicate-heavy volumes: 115 of their 399 resolved findings were declined, 98 because a neighbourhood survey had documented the building first. G-I is the builders' volume of the three: two-thirds of its addresses come from five builder entries, and twelve of its thirty declines are Galli model homes the Sunset builders statement had already documented. The Modern Architecture and Landscape Design statement (2011) is the densest single document in the register: 330 pages, 521 numbered-address mentions, 466 findings. |
| [`spur-popos-guide`](sources/spur-popos-guide.md) | SPUR, *Secrets of San Francisco* | PDF guide | medium | done | read in full |

City APIs and bulk datasets are **not** registered here — they are in
[../DATA-SOURCES.md](../DATA-SOURCES.md). The split: things you *query* live
there, things you *read* live here.

### What the columns mean

- **kind** — newspaper OCR, book, journal, newsletter, PDF report, directory,
  photo archive, dataset export, web guide.
- **search-invisibility** — how hard it is for a reader to find this material
  by searching an address. **This is the module's priority signal.**
  - **high** — not indexed at all, or indexed as an undifferentiated PDF/scan
    an address query will never surface. Mine these first.
  - **medium** — findable in principle (a scanned book on a public site) but
    not per-address; a reader would have to know it exists.
  - **low** — already ranking for address queries. Use for verification and
    context; it adds little to the site's reason for existing.
- **status** — four values, and no more: `open` (being mined, material
  remains — the dossier's coverage note says what's left) · `done` (exhausted
  for now) · `blocked` (needs a person; the dossier says what would unblock
  it) · `reference` (consulted per address for cross-checking, never mined as
  a corpus). A source that won't be pursued at all is struck through with the
  reason on the row.
- **coverage so far** — one honest phrase. Counts, not adjectives. The dossier
  carries the detail.

## Leads — candidates, not yet verified

Starting points for a prospecting run — see
[RUNBOOK.md](RUNBOOK.md#a-prospecting-run). Availability, licensing, format and
whether a lead carries street numbers at all are exactly what a prospecting run
is for.

The **triaged** column says where a lead stands, in three states:

- **blank** — nobody has looked. Everything starts here.
- **a date** — checked and real on that date: it exists, it names street
  numbers with dates, and there is a lawful way in. The sampled evidence is in
  [TRIAGE.md](TRIAGE.md). Not yet worth a dossier.
- **struck through** — didn't pan out. Retire it in place with the reason on
  the row, so nobody rediscovers it.

A lead that gets **promoted** stops being a lead: it moves to the register
above with a dossier and a confirmed access path, and its row and triage note
are deleted here. Promotion and the first mining batch is a well-sized run —
see [RUNBOOK.md](RUNBOOK.md#a-prospecting-run).

**Triage is not a dossier.** A triage pass answers four questions — is it real,
does it give numbers with dates, can we get it lawfully, does it break into
finishable batches — and records one sampled example as proof. Writing thirteen
dossiers before knowing which three are worth mining is the failure this state
exists to prevent.

Ranked by expected value — search-invisibility × address density × datedness ×
access, and then by a fifth thing the runbook's four axes don't capture: **whether the source breaks into finishable
batches.** `sf-context-statements` works as a queue because one statement is one
issue is one session. A source with no natural batch boundary can be excellent
and still be unstartable, and the top of this list is where those two things
line up.

| lead | why it could be good | how to get at it | triaged |
|---|---|---|---|
| National Register nomination forms | Per-building PDFs with construction dates, architects and a full narrative. Densely addressed, almost never indexed per address. | NPS map service for the index, `npgallery.nps.gov/NRHP/GetAsset/NRHP/<refnum>_text` for the PDF | 2026-08-15 |
| SF neighborhood newspapers, 1956–2026 | Fifteen-plus papers covering neighborhoods this project has almost nothing on. Block-level reporting, businesses and institutions at numbered addresses. | Internet Archive collection `sanfrancisconewspapers` — one issue per item, OCR text included | 2026-08-15 |
| HABS/HAER documentation | Measured drawings and a historian's report per building. | LoC collection `historic-american-buildings-landscapes-and-engineering-records`; data pages are text-layer PDFs on `tile.loc.gov` | 2026-08-15 |
| Article 10 landmark designation reports (SF Planning) | One report per city landmark, address-specific, PDF-only — and the index hands over the APN. | DataSF `97yj-54sx` for the index (address + APN + document URL), then the PDF | 2026-08-15 |
| San Francisco City Planning Commission minutes | Every conditional use, variance and discretionary review case, by address, by date, with the decision — and the cross-street bearing ("north line, 112.5 to 137.5 feet north of Haight") that resolves an address the number alone won't. | Internet Archive collection `sanfranciscopubliclibrary`, 109 volumes 1946–1984, `_djvu.txt` on each | 2026-08-21 |
| SF Redevelopment Agency property summaries | A survey form **per parcel** — block, lot, dimensions, improvements, assessed value, condition, and the recommendation to retain, move or demolish. Nothing else on the internet says this about a Western Addition or Yerba Buena address. **Overlaps [`digitalsf`](sources/digitalsf.md)**: same SFH 371 archive, digitized twice — paper forms here, catalogued photographs there. | Internet Archive collection `sanfranciscoredevelopmentagencyrecords`, 106 items, public domain | 2026-08-15 |
| *Architect and Engineer of California* and period trade journals | Building contracts, architects, costs — the pre-DBI permit record. | Internet Archive: `usmodernist-AECA-*` (214 issues) and `buildingengineer*` (35 volumes of *Building & Engineering News*), OCR text included | 2026-08-15 |
| Bay Area Reporter archive | The Castro and the LGBTQ record at address level, digitized and OCR'd. | Internet Archive collection `bayareareporter`, identifiers `BAR_YYYYMMDD` | 2026-08-15 |
| *East/West: The Chinese-American Journal* | Chinatown and the Chinese-American city at address level across 22 years, in a paper no address query will ever surface. | Internet Archive collection `eastwestnews` — 1,125 issues, 1967–1989, OCR text on each | 2026-08-21 |
| Crocker-Langley San Francisco city directories | What occupied a numbered address, year by year, pre-1930. Businesses are fair game where residents are not. | Internet Archive full-text scans, 41 volumes | 2026-08-15 |
| SF Municipal Reports (19th c.) | City construction, schools, firehouses, by address. | Internet Archive, 68 volumes, FY1859–60 through FY1913–14 | 2026-08-15 |
| *Here Today* (1968, rev. 1978) and *Splendid Survivors* (1979) | The two standard building-by-building surveys of San Francisco architecture — the ones the city's own EIRs cite as authority. One entry per address, with dates and architects. | Internet Archive `heretodaysanfran00olms`, `heretodaysanfran0000olms`, `splendidsurvivor00corb` — **lending-restricted, `needs-human`** | 2026-08-21 |
| Journal of Proceedings, Board of Supervisors | Street name changes and acceptances, and assessment-appeal lines that put a **named firm** at a numbered address on a dated day. | Internet Archive collection `sanfranciscopubliclibrary`, 157 volumes 1906–1999 | 2026-08-21 |
| Western Neighborhoods Project *Outside Lands* magazine | The west side, per building, by local researchers. | outsidelands.org/publications/ — 36 PDFs; plain fetches are refused, a browser-context fetch works | 2026-08-15 |
| OpenSFHistory photo captions | Captions frequently name a street number and a date. Link/cite only — see `historical-imagery` in DATA-SOURCES.md. | opensfhistory.org; credit line `OpenSFHistory/<file number>` | 2026-08-15 |
| SFMTA Photo Archive | Muni photography 1903–1978, 95% digitized, captioned with location and date. | sfmta.photoshelter.com — copies free on request for non-commercial use; not bulk-accessible | 2026-08-15 |
| San Francisco block books (1894–1909) | Block and lot geometry with lot dimensions — a **resolver aid** for pre-1906 addresses, not a source of facts. | Internet Archive, 12 volumes. Map plates: the OCR is noise, and owner names are barred by the privacy limits | 2026-08-15 |
| Sanborn fire insurance maps | Building footprint, material, use and street number, by block, across decades. Not text-searchable anywhere. | LoC Sanborn collection, 40 SF volumes 1886–1950s. Images only — no OCR to mine | 2026-08-15 |
| Pacific Coast Architecture Database (PCAD) | Per-building records: address, construction and demolition dates, architect, contractor, sourced narrative. | pcad.lib.washington.edu — but see the note: it ranks **first** for address queries, so it is a cross-check, not a target | 2026-08-15 |
| California Digital Newspaper Collection (CDNC) | Holds *Daily Alta California* 1849–1891, filling the whole pre-1890 gap `loc-newspapers` leaves. | **Blocked** — the search endpoint sits behind a Cloudflare challenge | 2026-08-15 |
| ~~Sunnyside History Project~~ | ~~A neighbourhood historian's archive of Sunnyside, a district the site has almost nothing on — house-by-house posts with build dates, architects and street numbers.~~ | **Retired — the operator has opted out of AI use.** `sunnysidehistory.org/robots.txt` carries an "AI Scrape Protect" block that names `anthropic-ai`, `ClaudeBot`, `ClaudeResearchBot`, `AnthropicBot`, `Claude-User` and `Claude-SearchBot` under `Disallow: /`, and every page repeats it in markup (`<meta name="robots" content="noai, nosummary, DisallowAITraining">`). Unblocking this is a person writing to the site and asking — see #203. | ~~2026-09-02~~ |
| ~~McCord's Edwards Abstract from Records (1900–1931)~~ | ~~Abstracts of recorded property transfers, parcel by parcel.~~ | **Retired** — the entries are metes-and-bounds with no street number (`N Haight 131-6 W Gough W 27-6 x N 20`), the parties are individuals and barred by the privacy limits, and the OCR of the tabular pages is unusable. The only numbered addresses in a sampled 9 MB volume are the abstract company's own offices at 318 Pine and 210 Montgomery. | ~~2026-08-21~~ |
| ~~*Tenant Times* (SF Tenants Union, 1979–1996)~~ | ~~Buildings named in eviction and rent-control coverage.~~ | **Retired** — 40 issues on the Internet Archive (`tenanttimes`); a sampled 1981 issue carries **no numbered street address at all**, and what the paper is about is the people in the buildings, which the privacy limits bar. | ~~2026-08-21~~ |
| ~~SF Weekly archive~~ | ~~Alt-weekly coverage and listings at venue addresses.~~ | **Retired** — 451 issues on the Internet Archive (`sfweeklyarchive`), but the run starts in 2013 and SF Weekly is fully indexed on the open web. Low search-invisibility over a period the site can source elsewhere. | ~~2026-08-21~~ |
| ~~Calisphere~~ | ~~Statewide aggregator over 20+ institutions holding SF material.~~ | **Retired as a target, keep as a prospecting tool** — its metadata is item-level and carries no street numbers; four numbered-address queries returned zero hits each. Use it to find which institution holds what, then go there. | ~~2026-08-15~~ |
| ~~Online Archive of California~~ | ~~Finding aids to SF archival collections.~~ | **Retired as a target, keep as a prospecting tool** — finding aids describe collections by the box and the cubic foot, not by address. Useful for locating a physical collection; acting on one is a library visit, so `needs-human`. | ~~2026-08-15~~ |
| ~~Institutional centennial histories (churches, schools, clubs, unions)~~ | ~~One building, deeply documented, usually a single scanned booklet.~~ | **Retired as a lead** — this is a category, not a source, and nothing about it can be checked until a specific booklet exists. Register individual titles as they turn up. | ~~2026-08-15~~ |
| ~~University theses on SF neighborhoods~~ | ~~Deep research on one district, often with building-level detail.~~ | **Retired for the same reason** — a category, not a source. eScholarship and the USF repository are real and open, but a thesis becomes a lead when a specific one is found to carry numbered addresses, not before. | ~~2026-08-15~~ |
| ~~California Register nomination forms~~ | ~~Per-building PDFs, state-level.~~ | **Folded into the National Register row** — OHP's Built Environment Resource Directory is a status index, not a document archive; the nomination text it points at is the federal one. | ~~2026-08-15~~ |

When you add a lead, say what you'd expect to *get* from it, not just that it
exists. A lead with no plausible address-level payload is noise.

**Where to prospect next.** Five of the leads above came out of one sweep of a
single Internet Archive collection — `sanfranciscopubliclibrary`, **14,664
digitized texts** contributed by SFPL, almost all of it municipal and
periodical material with open text layers. Scraping its metadata
(`https://archive.org/services/search/v1/scrape?q=collection:sanfranciscopubliclibrary`)
and grouping the titles is a cheap way to find the next seam: environmental
review documents, Planning Commission minutes, Board of Supervisors journals
and *East/West* were all found that way, and 2,666 items titled `Minutes` or
`Agenda` and 566 titled `Plan` are still unexamined. Internet Archive's
collection search (`mediatype:collection AND title:"San Francisco"`) returns
738 more collections and is the same trick one level up.

### Triage notes

Every `hold` lead above has an entry in **[TRIAGE.md](TRIAGE.md)** recording
what the pass found and the sampled example behind the verdict. Look a lead up
there before triaging it again; delete its entry when the lead is promoted.

## Adding a source

See [RUNBOOK.md → A prospecting run](RUNBOOK.md#a-prospecting-run). In short:
copy [templates/source-dossier.md](templates/source-dossier.md) to
`sources/<id>.md`, add the row above with status `open`, delete the lead's row
and triage note — and then keep going and mine the first batch, rather than
filing an issue and stopping.
