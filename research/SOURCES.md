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
| [`corbett-heights-neighbors`](sources/corbett-heights-neighbors.md) | Corbett Heights Neighbors newsletter | newsletter | high | open | page 1 of 5 (10 of 48 issues) |
| [`digitalsf`](sources/digitalsf.md) | DigitalSF — SF Public Library's catalogued digital archive | catalogued digital archive | high | open | harvested in full: 59,601 records; SFP 23 read whole, resolved and published (1,165 records → 1,122 findings → 923 on a parcel → 919 on 882 pages), 43 collections to go |
| [`hittell-1878`](sources/hittell-1878.md) | Hittell, *A History of the City of San Francisco* (1878) | book | medium | open | §12–14, 24, 27, 231 |
| [`loc-newspapers`](sources/loc-newspapers.md) | Chronicling America OCR — *Morning Call*, *SF Call* | newspaper OCR | high | open | 58,620 pages → 8,437 mentions, 2,025 addresses |
| [`local-news`](sources/local-news.md) | Hoodline, Bay Area Reporter, SF Chronicle | news | low | reference | browsed per address, no corpus pass |
| [`sf-context-statements`](sources/sf-context-statements.md) | SF Planning historic context statements & surveys | PDF reports | high | open | 20 statements read; ~30 remain (one issue each). All six with findings files are closed out: market-octavia-hcs 425 of 496 published, mission-dolores-hcs 66 of 83, van-ness-auto-row 352 of 453 on 133 pages, carnegie-libraries 1 of 2, north-beach-hcs 553 of 630 on 352 pages, japantown-hcs 83 of 125 on 53 pages |
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
  [Triage notes](#triage-notes) below. Not yet worth a dossier.
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
| San Francisco environmental review documents (EIRs, initial studies, negative declarations) | One document per project, most titled by street address, and it hands over the **assessor's block and lot outright** — plus what stood on the site, when it was built and when it came down. The record of what was demolished, which nothing else on this list covers. | Internet Archive collection `sanfranciscopubliclibrary` — 823 items, 1973–2013, published by the SF Planning Dept., open PDFs each with a `_djvu.txt` text layer | 2026-08-21 |
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

One entry per lead marked `hold` above — what the triage pass actually found,
with the sampled example that proves it carries numbered addresses with dates.
Delete an entry when its lead is promoted; the dossier takes over from there.

**San Francisco environmental review documents.** The San Francisco Public
Library's Internet Archive collection (`sanfranciscopubliclibrary`, 14,664
items) holds **823 environmental review documents** published by the SF
Planning Department between **1973 and 2013** — draft and final EIRs, initial
studies, negative declarations and supplements. **172 of them are titled by
street address** ("101 California Street : [draft] environmental impact
report"); the rest are area plans and project names. Ten sampled at random were
**all** open — no `access-restricted-item`, a `_djvu.txt` text layer on every
one — and all name the SF Dept. of City Planning as publisher, so this is
municipal work product, not a lending-library book. One document is one batch,
which makes it as startable as the National Register row.

**What it gives that nothing else here does.** An EIR describes the site
*before* the project, so it is the record of buildings that no longer exist —
and it states the parcel outright. **Sampled:** `280divisaderostr5200sanf`
puts 280 Divisadero Street at "Assessor's Block 1238, Lot 23", a 6,875 sq ft
double lot, identifies it as City Landmark No. 190, the Charles L. Hinkel House
and carriage house, and dates the carriage house's second residential unit to
before 1964 and its abandonment to around 1981. A second, `101californiastr1819sanf`
(1979), records that the 49,000 sq ft building formerly at 101 California
Street "was demolished in 1974 after a destructive fire". Both give a date, a
street number and a page-level citation.

**Cautions.** Downtown is heavily over-represented — the 1970s–80s highrise
boom is most of the run — so neighborhood coverage is thin and clustered.
Project descriptions are proposals, not outcomes: an EIR says what was
*intended*, and whether it was built is a separate check against the assessor.
And these documents name project sponsors and property owners, which the
privacy limits bar; take the buildings.

**National Register nomination forms.** 166 San Francisco listings, 135 of them
with a numbered street address. The NPS map service
(`mapservices.nps.gov/arcgis/rest/services/cultural_resources/nrhp_locations/MapServer/0`,
query `City='San Francisco'`) returns reference number, resource name, address
and certification date in one call — that is the index. The nomination PDF is
then at `npgallery.nps.gov/NRHP/GetAsset/NRHP/<refnum>_text`, and all three
sampled (73000441, 78000757, 71000183) returned a PDF with a usable OCR text
layer. Federal work product, public domain. **Sampled:** the Civic Center
district nomination (78000757, 85K characters of text) names 99 Grove Street,
355 and 450 McAllister Street, 45 Hyde Street and 200 Larkin Street among
others; the 1973 form 73000441 gives 762 Fulton Street. One nomination is one
batch, which makes this the most startable thing on the list.

**SF neighborhood newspapers, 1956–2026.** The original lead named five papers
and pointed at each one's own website; that is the wrong access path. The right
one is a single Internet Archive collection, `sanfrancisconewspapers`, holding
**2,358 issues** contributed by a collaborative of neighborhood history groups,
each with a `_djvu.txt` OCR file. Titles include Noe Valley Voice (273 issues),
The Potrero View (190), Richmond ReView (228 across two title spellings),
Visitacion Valley Grapevine (116), New Mission News (111), OMI News (71), North
Mission News (68), New Bernal Journal and Bernal Journal (118), Tenderloin
Times (64), Park Bell (51), The Semaphore / Telegraph Hill Semaphore (75), Glen
Park News (33), The New Fillmore (23). **Sampled:** *The Potrero View*, June
1999 — the Victoria Theater at 2961 Sixteenth Street, the Potrero Hill Health
Center at 1050 Wisconsin Street, the Neighborhood House at 953 DeHaro Street.
OCR doubles its spaces, so match on `\d+\s+Street` rather than a single space.
Two cautions: no explicit license on the items (facts are free, the OCR text is
not ours to redistribute), and these papers are thick with residents, obituaries
and donors — the privacy limits bite harder here than anywhere else in the
register. Marina Times and Westside Observer, both named in the original lead,
are **not** in this collection.

**SF Redevelopment Agency property summaries.** 106 items on the Internet
Archive under `sanfranciscoredevelopmentagencyrecords`, from SFPL's SFH 371,
covering Western Addition A-1 and A-2 and Yerba Buena. **Public domain, CC0
marked**, with a requested credit line: "From the San Francisco History Center,
San Francisco Public Library." The payload is a per-parcel SFRA survey form
(FORM P-10, dated 8/10/62) carrying block and lot, parcel dimensions, number and
type of improvements, assessed land and improvement value, zoning, an exterior
and interior condition survey with dates, and a **recommendation for disposition
— retain, rehabilitate, move, or demolish**. For the neighborhoods the
redevelopment program erased, this is the record of what stood there, and it is
keyed to block and lot, which is the resolver's answer handed over directly.
**Sampled:** item `SFH371-5054_0`, "Western Addition Property Summary", blocks
1126 to 1130. **Two hard cautions.** The forms are handwritten on printed
stock and the OCR of them is close to unusable — dimensions come through as
`25! x [Ob` — so extraction here means a vision pass over page images, not a
text scan. And the collection includes items titled "Western Addition.
Community: Identified People" and "Identified people relocated" — files about
displaced residents by name. Those are exactly what the root
[AGENTS.md](../AGENTS.md) privacy limits forbid, the displacement makes them
more sensitive rather than less, and no amount of public-domain status changes
it. Take the buildings. Leave the people.

**HABS/HAER documentation.** 384 San Francisco items, 104 with a street number
in the title. 126 are military installations (Presidio, Treasure Island,
Alcatraz, Fort Mason), whose addresses will mostly not exist in EAS, and the
numbered civilian ones cluster heavily in a handful of projects — real distinct
coverage is perhaps 40–60 buildings. The payload is the "data pages": a written
historian's report, reachable at
`tile.loc.gov/storage-services/master/pnp/habshaer/ca/ca<NN00>/ca<NNNN>/data/ca<NNNN>data.pdf`
and carrying a text layer that `pdftotext` reads directly — no OCR step needed.
Public domain. **Sampled:** ca3559, North Beach Place Building 1 at 415 Bay
Street — designed 1941–42, built 1950–52, demolished 2001–03, with the
architect and the housing authority named.

**Article 10 landmark designation reports.** DataSF's `97yj-54sx` carries 370
rows, each with the landmark name, address, **APN** and a direct URL to the
designation document — so this is the one lead where resolution is handed over
for free rather than being the hard part. The documents themselves live on
`files.sfplanning.org` or `sfplanninggis.org`, not DataSF. Text quality is
mixed: LM100 (the Castro Theatre) has a clean text layer naming "429-431 Castro
Street, Assessor's Parcel Block No. 3582, Lot No. 085", and the two district
documents sampled are large and text-bearing (LM271, 75pp; LM300, 235pp), but
LM11 and LM200 are image-only and would need OCR. Same publisher as
`sf-context-statements` but an entirely separate corpus.

**San Francisco City Planning Commission minutes.** 109 volumes in the same
SFPL collection, **1946–1984**, each with a `_djvu.txt`. The payload is the
case calendar: a case number, the address, the zoning, the request, the date
and the Commission's decision. **The address line carries a survey bearing**,
which is exactly what the resolver needs where a street number alone is
ambiguous. **Sampled:** `10minutesofsanfran1969san` — "CU67.13 960 Haight
Street, north line, east of Broderick Street; and Broderick Street, east line,
between 112.5 feet and 137.5 feet north of Haight Street. Request for 100-bed
convalescent hospital for long-term psychiatric care on property zoned R-3 and
R-4", carried over from the meeting of 7 August 1969. The same volume names 801
and 731 Grove, 751 and 725 Webster, 1280 Ellis and 6021 Geary. **Caution:** 100
Larkin Street is the top numbered token in every volume and it is the library's
and the Commission's own address, not a case — the same advertiser-address trap
the trade-journals note describes. Volumes are undated in the IA metadata; the
year is in the text.

**Period trade journals.** Two runs, mined identically, so they are one lead.
***Architect and Engineer of California***: 214 issues on the Internet Archive
under `usmodernist-AECA-*`. ***Building & Engineering News***: 35 volumes under
`buildingengineer*`, digitized with SFPL funding, roughly 9 MB of OCR text per
volume. Both are dense with architects, contractors, costs and dates, and both
carry the weekly contract-award column — a sampled 1928 entry gives a
three-storey 69-room apartment building, $80,000, with the owner, the heating
contractor and the architect's firm all named and addressed.

**The catch is the same one `loc-newspapers` already documents, twice over.**
First, the contract notices identify buildings by corner, not by number: the
1912 *Architect and Engineer* award for the Sharon building places it "on the
northeast corner of New Montgomery and Jessie streets" with a $375,000 price and
the architect named, and no street number anywhere. Second, the numbered
addresses that *are* dense in the text are mostly advertisers' and architects'
own offices — in one *Building & Engineering News* volume the 5,427 numbered
street tokens are topped by 354 Hobart (125 times) and 251 Kearny (102), which
are firms' addresses, not building facts. The usable material is in the long
tail. Expect a low resolve rate and a resolver-heavy pass, and note that a
sampled volume ran heavily to Oakland and the wider Bay Area, so a filtering
step for San Francisco comes before anything else.

**Bay Area Reporter archive.** 1,529 issues on the Internet Archive under
collection `bayareareporter`, contributed by the GLBT Historical Society,
identifiers of the form `BAR_YYYYMMDD`, each with OCR text. This is a much
cleaner path than CDNC, which also holds the paper but is walled. **Caution:**
the items carry an explicit "Copyright BAR Media, Inc." — facts extract freely
under the evidence bar, the text does not get committed or reproduced. Note the
register already lists Bay Area Reporter under `local-news` as a browse-only
reference; mining the archive is a different activity and wants its own id.

***East/West: The Chinese-American Journal.*** 1,125 issues on the Internet
Archive under collection `eastwestnews`, **1967–1989**, contributed through
SFPL, with OCR text on each. Chinatown, the Richmond and the Sunset in a
weekly that no address query will ever return. **Density is thin and it is
mostly commercial:** five issues sampled across the run (1967, 1972, 1978,
1984, 1989) carried roughly 5–15 numbered addresses each — 758 Commercial
Street, 900 and 857 Grant Avenue, 724 Pacific Avenue, 777 Stockton Street, 1119
Clement Street, 1127 Market Street. Over 1,125 issues that is a few thousand
mentions, which is a real harvest at this module's usual rate. **Three
cautions.** The OCR is mixed Chinese and English and the Latin text is mangled
(commas render as `，`, and `838 Grant Avenue` recurs across years as an
advertiser, not a fact). The masthead address (863 Stockton Street) will top
any frequency count. And the issues carry an explicit "Copyright 1967 by
EAST/WEST Publishing Company" — facts extract freely, the text does not get
committed.

**Crocker-Langley city directories.** 41 volumes on the Internet Archive with
full OCR. **The privacy limit removes most of the book.** A sampled slice of the
1900 volume is almost entirely residents, marked with `r.` for residence — all
of it off-limits under the root AGENTS.md. What survives is the business entry
sitting in the same alphabetical run: a contractors-and-builders firm at 667
Market, a laboratory director's office at 803 Sutter. An extractor here must
filter on the `r.` marker and keep only firms, which is a narrow slice of a
13 MB text file. OCR is also poor — words are space-broken mid-token. The lead
said "pre-1930"; the successor Polk's Crocker-Langley volumes are on the
Internet Archive too (`polkscrockerlang194849dire` and siblings), so the run
extends at least to 1949 if the business slice proves worth mining.

**SF Municipal Reports.** 68 volumes on the Internet Archive covering FY1859–60
through FY1913–14, plus a separate index volume to the appendices 1859–1901.
Not yet sampled for address density — that is the first thing an acquire pass
should measure.

***Here Today* and *Splendid Survivors*.** The two standard building-by-building
surveys of San Francisco's architecture, and the ones the city's own
environmental documents cite as authority — the 101 California EIR sampled
above refers to "the 1968 catalogue and description of architecturally
outstanding buildings built before 1920 (Olmsted, Roger, and T.H. Watkin, 1968,
*Here Today*)". All three editions are on the Internet Archive
(`heretodaysanfran00olms` 1968, `heretodaysanfran0000olms` 1978,
`splendidsurvivor00corb` 1979, the downtown survey). **All three are
lending-restricted**: `access-restricted-item: true`, collection `inlibrary`,
and a direct fetch of the `_djvu.txt` returns **401**. Per "Corpora on disk" in
[AGENTS.md](AGENTS.md) that makes this `needs-human`, not something to route
around — a person borrows the scan or reads the copy at SFPL. Worth the ask:
these are per-address entries with dates and architects, in books that have
been out of print for decades. Not yet sampled for content, because sampling it
is the thing that needs a person.

**Journal of Proceedings, Board of Supervisors.** 157 volumes in the SFPL
collection, **1906–1999**, roughly 4 MB of OCR each. **Sampled:**
`journalofproceed34sanfrich` (1939) — the assessment-appeal schedules put named
firms at numbered addresses on dated days: "Barron & Rossi, 998 Folsom St.
Assessment erroneous, excessive, reassessed. Tax paid to Assessor, Aug. 11,
1938"; the same run gives Crosley Radio Corporation, Lewittes & Sons and
Stakmore Co. all at 1355 Market St. That is a dated occupancy record for a
business at a street number, which is usable. **But it ranks low, for two
reasons.** The appeal schedules interleave firms with individuals — "Anna
Crljenko, 930 Fillmore St." on the next line — so an extractor needs the same
person-name filter the city-directories note describes, and most of a volume is
not about buildings at all. Street name changes and street acceptances are the
other seam here and have not been sampled.

**Western Neighborhoods Project *Outside Lands* magazine.** 36 issue PDFs listed
at outsidelands.org/publications/. **Access caution:** a plain `curl` for the
PDF returns 403; a browser-context fetch retrieves it fine. **Sampled:** volume
21 number 3 names Little Woman Variety & Foods at 2722 Clement Street with a
photo credit. The weakness is datedness — captions run to "circa 1980" as often
as to a year, and undated claims are nearly unusable under the evidence bar.
Same organization as OpenSFHistory, so reuse terms are one conversation, not
two.

**OpenSFHistory photo captions.** Same organization as WNP above. Terms are
explicit and workable: 1,000-pixel watermarked images are free for personal and
educational use, the watermark must not be cropped, WNP does not hold copyright
to everything in the collection, and the requested credit line is
`OpenSFHistory/<file number>` — for example `OpenSFHistory/wnp15.556` — linking
back to opensfhistory.org. That is the citation label a page would print. Facts
in a caption are free regardless. **Sampled:** a caption dating a single-family
residence at 1354 32nd Avenue, between Irving and Judah, to 1950.

**SFMTA Photo Archive.** Muni photography from 1903 to 1978, of which the
agency says over 95% is digitized, browsable on PhotoShelter. Copies up to 1,200
pixels are free on request for non-commercial use; they are not to be sold or
used in advertising, and there is no bulk download — every image is a request.
That request gate, plus the likelihood that transit photography is captioned to
the intersection rather than the street number, puts this well down the list.
Worth a pass only once the cheaper sources are exhausted, or when a specific
address needs a photograph and nothing else has one.

**San Francisco block books, 1894–1909.** Twelve volumes on the Internet
Archive (`handyblockbookof1894hick`, `sanfranciscobloc1901hick`,
`merysblockbookof1909bloc`, the 1906 volumes and others), digitized with SFPL
funding. **This is not a page source and should not be treated as one.** The
volumes are map plates: block outlines with lot lines, lot dimensions and owner
names lettered onto the drawing. The `_djvu.txt` is consequently noise — a
sampled page of the 1901 volume yields scattered surnames and fragments like
`S7-` where dimensions should be. Owner names are people and barred regardless.
What survives is genuinely useful but narrow: **pre-1906 lot geometry**, which
the resolver already uses as a corroborating check (see the cautions in
[sources/loc-newspapers.md](sources/loc-newspapers.md) on matching 25x125 against
a parcel's `lot_area`). Register it, if at all, as a resolver aid.

**Pacific Coast Architecture Database.** Per-building records of real quality —
the Crocker Building entry gives 600 Market Street, constructed 1890–1891,
demolished 1968, ten storeys, the architect, the building contractors, latitude
and longitude, and a narrative with its sources named. **And that is the
problem.** A plain web search for "600 Market Street San Francisco Crocker
Building history" returns the PCAD record as the **first result**. By the
standard set at the top of [AGENTS.md](AGENTS.md), a source already ranking for
address queries adds little to why this site exists. Keep it where `local-news`
sits — a cross-check for a fact found elsewhere, and a way to catch an
architect attribution that contradicts ours. Not a mining target.

**Sanborn fire insurance maps.** 40 San Francisco volumes at the Library of
Congress, 1886 onward, explicitly public domain and free to reuse. **But the
online format is `image` with no OCR and no text layer at all**, so every fact
has to be read off a map by eye or by vision model. Nothing else on this list
has that cost. There is also no obvious finishable batch unit yet — "one sheet"
is too small to be worth an issue and "one volume" may be hundreds of sheets.
Working out the batch unit is the precondition for this one, not the mining.

**California Digital Newspaper Collection.** The prize is real: CDNC holds 33
San Francisco titles, and the one that matters is ***Daily Alta California*,
1849–1891**, which covers the entire period before `loc-newspapers` begins in
1890. Also there: the Elevator (1865–1898) and Pacific Appeal (1862–1880), both
Black press; Organized Labor (1900–1988); Labor Clarion (1906–1947); Vestkusten
(1887–2007); Italia (1897–1919). **The search endpoint returns a Cloudflare
managed challenge to automated requests.** Under "Corpora on disk" in
[AGENTS.md](AGENTS.md) that makes it a `needs-human` matter, not something to
route around. Two things a person could do, in order: check whether Chronicling
America itself holds *Daily Alta California* — if it does, the existing
`loc-newspapers` tooling mines it with no wall to negotiate — and, failing that,
ask UCR whether they will grant API or bulk access.

**Rejected in the 2026-08-21 pass, with what was actually checked.**
*McCord's Edwards Abstract from Records* (37 volumes, 1900–1931, collection
`sfpl_mccords-edwards-abstract-from-records`) is the metes-and-bounds trap in
its purest form: a sampled 9 MB volume gives transfers as `N Haight 131-6 W
Gough W 27-6 x N 20` with no street number anywhere, the grantors and grantees
are individuals and barred, and the only numbered addresses in the whole file
are the abstract company's own offices at 318 Pine (126 times) and 210
Montgomery (54). *Tenant Times* (40 issues, `tenanttimes`) — a sampled 1981
issue contains no numbered street address at all, and the paper's subject is
the people in the buildings. *SF Weekly archive* (451 issues, `sfweeklyarchive`)
— the run starts in 2013 and the paper is fully indexed on the open web.

## Adding a source

See [RUNBOOK.md → A prospecting run](RUNBOOK.md#a-prospecting-run). In short:
copy [templates/source-dossier.md](templates/source-dossier.md) to
`sources/<id>.md`, add the row above with status `open`, delete the lead's row
and triage note — and then keep going and mine the first batch, rather than
filing an issue and stopping.
