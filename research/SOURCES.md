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
| [`argonaut-sfhs`](sources/argonaut-sfhs.md) | *The Argonaut*, journal of the SF Historical Society | journal | high | mining | 7 volumes read in full |
| [`celebrity-residence-guides`](sources/celebrity-residence-guides.md) | Notable-resident guides | web guides | low | mined | 26 addresses, 25 resolved |
| [`corbett-heights-neighbors`](sources/corbett-heights-neighbors.md) | Corbett Heights Neighbors newsletter | newsletter | high | mining | page 1 of 5 (10 of 48 issues) |
| [`hittell-1878`](sources/hittell-1878.md) | Hittell, *A History of the City of San Francisco* (1878) | book | medium | mining | §12–14, 24, 27, 231 |
| [`loc-newspapers`](sources/loc-newspapers.md) | Chronicling America OCR — *Morning Call*, *SF Call* | newspaper OCR | high | mining | 58,620 pages → 8,437 mentions, 2,025 addresses |
| [`local-news`](sources/local-news.md) | Hoodline, Bay Area Reporter, SF Chronicle | news | low | reference | browsed per address, no corpus pass |
| [`sf-context-statements`](sources/sf-context-statements.md) | SF Planning historic context statements & surveys | PDF reports | high | mining | 13 statements read; ~38 remain (one issue each) |
| [`spur-popos-guide`](sources/spur-popos-guide.md) | SPUR, *Secrets of San Francisco* | PDF guide | medium | mined | read in full |

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
- **status** — `lead` (not yet acquired) · `acquiring` · `mining` (partly
  read, more to go) · `mined` (exhausted for now) · `blocked` (needs a human)
  · `retired` (won't pursue; the dossier says why).
- **coverage so far** — one honest phrase. Counts, not adjectives. The dossier
  carries the detail.

## Leads — candidates, not yet verified

Unverified starting points for a [prospector](roles/prospector.md). **Nothing
here has been confirmed** — availability, licensing, format and whether it
carries street numbers at all are exactly what the prospecting pass is for.
Promote a lead to the table above only after it has a dossier and a confirmed
access path; retire it in place (strike it, say why) when it doesn't pan out.

Ranked roughly by expected value — search-invisibility × address density:

| lead | why it could be good | first check |
|---|---|---|
| National Register / California Register nomination forms | Per-building PDFs with construction dates, architects, owners and a full narrative. Densely addressed, almost never indexed per address. | NPS NPGallery and the OHP listings for San Francisco County |
| Article 10 landmark designation reports (SF Planning) | One report per city landmark, address-specific, PDF-only. | The landmark list in `sf-planning`, then the case report per landmark number |
| Sanborn fire insurance maps | Building footprint, material, use and street number, by block, across decades. Not text-searchable anywhere. | Library of Congress Sanborn collection; SFPL for the later sheets |
| Crocker-Langley San Francisco city directories | Who and what occupied a numbered address, year by year, pre-1930. Businesses are fair game where residents are not. | Internet Archive full-text scans |
| California Digital Newspaper Collection (CDNC) | SF titles Chronicling America doesn't hold, same OCR shape as `loc-newspapers`. | cdnc.ucr.edu search API and title list |
| *Architect and Engineer of California* and period trade journals | Building contracts, architects, costs — the pre-DBI permit record, by address. | Internet Archive / HathiTrust runs |
| HABS/HAER documentation | Measured drawings and historian's reports for individual buildings. | Library of Congress HABS collection, San Francisco |
| Neighborhood papers with archives (Potrero View, Noe Valley Voice, Richmond Review / Sunset Beacon, Marina Times, Westside Observer) | Decades of block-level reporting; PDF archives that rank for nothing. | Each paper's archive page; check reuse terms before mining |
| Bay Area Reporter archive | The Castro and the LGBTQ record at address level, digitized and OCR'd. | The digital archive's terms and its search interface |
| OpenSFHistory photo captions | Captions frequently name a street number and a date. Link/cite only — see `historical-imagery` in DATA-SOURCES.md. | The collection's search and its terms of use |
| SF Municipal Reports (19th c.) | City construction, schools, firehouses, by address. | Internet Archive / HathiTrust |
| Institutional centennial histories (churches, schools, clubs, unions) | One building, deeply documented, usually a single scanned booklet. | Case by case; often SFPL or the institution itself |
| Western Neighborhoods Project newsletters and articles | The west side, per building, by local researchers. | outsidelands.org archive; check reuse terms |

When you add a lead, say what you'd expect to *get* from it, not just that it
exists. A lead with no plausible address-level payload is noise.

## Adding a source

See [AGENTS.md](AGENTS.md) → "Handoff artifacts" and the
[prospector](roles/prospector.md) playbook. In short: copy
[templates/source-dossier.md](templates/source-dossier.md) to
`sources/<id>.md`, add the row above, and file a `research:acquire` issue.
