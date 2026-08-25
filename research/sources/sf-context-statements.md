# sf-context-statements — SF Planning historic context statements (secondary)

> **Research dossier.** Rules: [../AGENTS.md](../AGENTS.md) · register:
> [../SOURCES.md](../SOURCES.md) · cited on pages by the source id `sf-context-statements`.
>
> - **Kind:** PDF reports (SF Planning) · **Tier:** secondary · **Status:** open
> - **Search-invisibility:** high — see the register for what that rates.
> - **Coverage:** 24 statements read; the rest are one open GitHub issue each.
> - **Local corpus:** `research/corpora/sf-context-statements/`
>
> Update this dossier at the end of every pass — the `Verified:` line, the
> coverage note, and anything the pass learned about getting at the source.

## Where this source stands

This dossier is long because the source is 50 documents, each with its own
shape. Read the front matter, this board, and then only the section for the
document you are about to mine.

| | |
|---|---|
| **Read in full** | 24 statements — listed under "Read into the repo so far" below, each with its own notes section |
| **Findings files** | 10: [`market-octavia-hcs`](../findings/sf-context-statements/market-octavia-hcs.json) (496 findings, 425 published, 71 declined), [`mission-dolores-hcs`](../findings/sf-context-statements/mission-dolores-hcs.json) (83 findings, 66 published), [`van-ness-auto-row`](../findings/sf-context-statements/van-ness-auto-row.json) (453 findings, 352 published, 101 declined), [`carnegie-libraries`](../findings/sf-context-statements/carnegie-libraries.json) (2 findings, 1 published, 1 declined), [`north-beach-hcs`](../findings/sf-context-statements/north-beach-hcs.json) (630 findings, 546 published on 349 pages, 1 declined, 83 unresolved), [`japantown-hcs`](../findings/sf-context-statements/japantown-hcs.json) (125 findings, 83 published on 53 pages, 39 unresolved, 3 rejected), [`russian-hill-hcs`](../findings/sf-context-statements/russian-hill-hcs.json) (109 findings, 57 published on 48 pages, 10 declined, 41 unresolved, 1 rejected), and [`parkside-hcs`](../findings/sf-context-statements/parkside-hcs.json) (160 findings, 147 published on 142 pages, 4 declined, 9 unresolved) [`oceanside-hcs`](../findings/sf-context-statements/oceanside-hcs.json) (32 findings, 20 published on 19 pages, 12 unresolved) and [`transit-center-district-survey`](../findings/sf-context-statements/transit-center-district-survey.json) (316 findings, 211 published on 123 pages, 50 declined, 55 unresolved). All ten loops closed. |
| **Remaining** | ~26 adopted statements, **one open GitHub issue each** — that is the queue. Search open issues for `sf-context-statements`. |
| **Batch unit** | one statement = one run. Most are 60–260 pages and go end to end in a session; take a second one if the first finishes early. |
| **Reading order** | the earlier statements each taught something the next one needed. The two under "Traps that apply to every statement" below are the ones nobody should re-learn. |

## Traps that apply to every statement

- **The inventory is often not in the statement.** Central SoMa, Central
  Waterfront, Corbett Heights, Duboce Triangle, Eureka Valley, Inner Sunset,
  OMI and Mission Dolores all have no appendix inventory table; the addresses
  are in adoption packets, reprinted earlier surveys, builder tables, figure
  captions or the narrative. Check what shape the document is *before* planning
  the read.
- **The addresses in a table are the survey's, not the city's.** Follow the
  APN, check both against EAS, and expect retired APNs.
- **A statement contradicts itself often enough to plan for it.** State the
  disagreement on the page's `.unknowns`; never adjudicate.
- **Condominium parcels take out a large slice of any Mission-area
  inventory** — 31 of the Market & Octavia addresses and 5 of the 18
  individually eligible Mission Dolores properties.
- **Drafts and finals coexist and the final can still say DRAFT.** Take the
  file the adopting body listed.
- **Two statements can cover the same buildings.** The Transit Center survey
  area (2008) sits inside the Central SoMa survey area (2016), and 57 of the
  123 pages the Transit Center pass reached already carried the Central SoMa
  panel and, on several, the same facts. Before publishing a district
  statement, check which of its parcels this repo has already documented from a
  neighbouring survey — the overlap decides where each fact can go, and the
  renderer holds one `historic_survey` panel per page.
- **The vault serves an HTML shell.** `SharedLinks.aspx` is not the PDF; the
  REST content URL is built from the page's own `accesskey`. Worked examples
  throughout the per-document notes below.


- **What:** The historic context statements SF Planning has adopted for
  individual neighborhoods and survey areas — consultant reports that set out
  an area's development history and then inventory its buildings. They are the
  richest address-level history available for the districts that have one, and
  they name streets and numbers constantly. The landing page listing the
  adopted statements is
  `https://sfplanning.org/project/sf-histories-historic-context-statements#completed`.
- **Read into the repo so far:**
  - Kelley & VerPlanck Historical Resources Consulting, *Bayview-Hunters Point
    Area B Survey: Town Center Activity Node — Historic Context Statement*,
    prepared for the San Francisco Redevelopment Agency, adopted February 11,
    2010 (197 pp.), source id `bvhp-area-b-context-statement`.
  - San Francisco Planning Department (Jonathan Lammers, project manager),
    *Central SoMa Historic Context Statement & Historic Resource Survey*,
    adopted by the Historic Preservation Commission March 16, 2016, Motion No.
    0277, Case No. 2011.1356E (115 pp.), source id
    `central-soma-context-statement`. The survey adopted with it — the
    property information catalog and the survey results table, which are in
    the hearing packet rather than the statement — is cited separately as
    `central-soma-survey`
    (`https://sfplanning.s3.amazonaws.com/commissions/hpcpackets/Central%20SoMa.pdf`,
    548 pp.). See "The Central SoMa statement" below.
  - San Francisco Planning Department, *Central Waterfront Cultural Resources
    Survey: Summary Report and Draft Context Statement*, prepared with the
    Central Waterfront Survey Advisory Committee, San Francisco Architectural
    Heritage, the Dogpatch Neighborhood Association and Page & Turnbull,
    Architects, October 2000 – October 2001, adopted 2001 (43 pp.), source id
    `central-waterfront-context-statement`. Listed on the SF Planning page as
    "Central Waterfront Survey and Context Statement (Adopted 2001)". See
    "The Central Waterfront statement" below.
  - Michael R. Corbett, *Corbett Heights, San Francisco (Western Part of
    Eureka Valley) Historic Context Statement*, prepared for Corbett Heights
    Neighbors and funded by the Historic Preservation Fund Committee, adopted
    by the Historic Preservation Commission 16 August 2017, Motion No. 0314,
    Case No. 2015-006003SRV (261 pp.), source id
    `corbett-heights-context-statement`. The PDF is served from
    `default.sfplanning.org`, not the S3 archive:
    `http://default.sfplanning.org/Preservation/CorbettHeightsHCS/hp_corbett_hcs_HCS_FINAL-081617.pdf`
    (there is a May 2017 draft alongside it — take the FINAL). See "The
    Corbett Heights statement" below.
  - Christopher VerPlanck, *Dogpatch Historic District Survey* (description of
    the neighborhood, context statement, illustrations and survey forms),
    September 2001, adopted 2001 (35 pp.), source id
    `dogpatch-context-statement`. Listed on the SF Planning page as "Dogpatch
    Historic Context Statement (Adopted 2001)". It is **not** on the S3
    archive; SF Planning serves it from an M-Files vault, and the
    `SharedLinks.aspx` URL returns an HTML shell, not the PDF. The file itself
    is at the REST path that page's script names —
    `https://citypln-m-extnl.sfgov.org/REST/sharedlinks/%7ba4a7dacd-b0dc-4322-bd29-f6f07103c6e0%7d/3e8b29b9c2a36962ffa191a884c1aabb534f7de60b3808d9f8d7bfd966aa6d57/content`
    — while the `SharedLinks.aspx` form is what a page cites. See "The Dogpatch
    survey" below.
  - Christopher VerPlanck (VerPlanck Historic Preservation Consulting), *Duboce
    Triangle Historic Context Statement*, prepared for the Duboce Triangle
    Neighborhood Association, dated August 26, 2022, adopted 2022 (181 pp.),
    source id `duboce-triangle-context-statement`. The PDF is on the S3 archive
    at
    `https://sfplanning.s3.amazonaws.com/default/files/Preservation/DuboceTriangleHCS/preserv_duboce_triangleHCS-draft.pdf`.
    The cover and every page header read **DRAFT**, and the SF Planning listing
    page carries it under "Duboce Triangle Historic Context Statement (Adopted
    2022)"; there is no non-draft file. Cite it as adopted 2022 and say the file
    is the draft. See "The Duboce Triangle statement" below.
  - Elaine B. Stiles, *Eureka Valley Historic Context Statement*, prepared for
    the Eureka Valley Neighborhood Association with the San Francisco Historic
    Preservation Fund Committee and the Planning Department, adopted by the
    Historic Preservation Commission December 20, 2017 (260 pp.), source id
    `eureka-valley-context-statement`. The PDF is served from
    `default.sfplanning.org`, not the S3 archive:
    `http://default.sfplanning.org/Preservation/EurekaValleyHCS/hp_eureka_valley_hcs_HCS_FINAL-122017.pdf`
    (there is an April 2017 review draft alongside it — take the FINAL). **The
    cover of the FINAL carries the adoption line, but every page header still
    reads "DRAFT ‐ Eureka Valley Historic Context Statement / May 2017."** Cite
    it as adopted 2017. See "The Eureka Valley statement" below.
  - Carey & Co., Inc., *Historic Resources Evaluation: Glen Park Community
    Plan*, prepared for PBS&J, dated December 21, 2010, adopted 2011 (118 pp.),
    source id `glen-park-context-statement`. **It is not titled a context
    statement** — it is the CEQA historic resources evaluation for the Glen
    Park Community Plan EIR, containing a context statement as one of its four
    tasks — and SF Planning lists it as "Glen Park Historic Context Statement
    (Adopted 2011)". SF Planning serves it from the same M-Files vault as the
    Dogpatch survey, so the `SharedLinks.aspx` URL returns an HTML shell; the
    file itself is at the REST path
    `https://citypln-m-extnl.sfgov.org/REST/sharedlinks/%7ba4a7dacd-b0dc-4322-bd29-f6f07103c6e0%7d/e21915779d1b8ac21bb5023f7b6d453afaec3018897014eb32cd699ef9af3fc3/content`
    while the `SharedLinks.aspx` form is what a page cites. See "The Glen Park
    evaluation" below.
  - Kelley & VerPlanck Historical Resources Consulting (Tim Kelley and
    Christopher VerPlanck), *India Basin Survey, San Francisco, California —
    Final Report*, prepared for the Bayview Historical Society, dated May 1,
    2008, adopted 2008 (120 pp.), source id `india-basin-context-statement`.
    Listed on the SF Planning page as "India Basin Survey and Context Statement
    (Adopted 2008)". It is on the S3 archive at
    `https://sfplanning.s3.amazonaws.com/archives/documents/4049-Final_India%20Basin_05.01.08.pdf`.
    Same consultants as the Bayview-Hunters Point Area B statement two years
    later, and the two overlap on the three India Basin buildings that already
    had pages here. See "The India Basin survey" below.
  - Kelley & VerPlanck Historical Resources Consulting, *Transit Center District
    Survey, San Francisco, California — Final*, prepared for the San Francisco
    Planning Department, dated July 22, 2008 (95 pp.), source id
    `transit-center-district-survey`. SF Planning lists it as "Transit Center
    District Survey (includes HCS) (Adopted 2012)"; the file itself is the July
    2008 final, so cite it as adopted 2012 and say the report is dated 2008. It
    is on the S3 archive at
    `https://sfplanning.s3.amazonaws.com/archives/documents/4039-Final%20Transit%20Center.pdf`.
    The 74-page context statement is followed by a DPR 523 D district record for
    the proposed New Montgomery, Mission & Second Historic District and three
    appendix tables. **Its survey area sits inside the Central SoMa survey area**,
    which this repo read in 2026-08-12 — expect half its parcels to have pages
    already. See "The Transit Center District survey" below.
  - San Francisco Planning Department, *Inner Mission North 1853-1943 Context
    Statement* (62 pp., dated on its own title page "October 2001 – September
    2005"; SF Planning's listing page files it as adopted 2004), source id
    `inner-mission-north-context-statement`. Prepared under a series of
    Certified Local Government grants documenting the northern Mission in
    three successive survey areas (2001–02, 2003–04, 2005–06). Served from the
    same M-Files vault as the Dogpatch survey and the Glen Park evaluation, so
    the `SharedLinks.aspx` URL again returns an HTML shell; unlike those two,
    the REST content URL's hash *is* the page's own `accesskey` —
    `https://citypln-m-extnl.sfgov.org/REST/sharedlinks/%7ba4a7dacd-b0dc-4322-bd29-f6f07103c6e0%7d/ef5726f8f01317048294fa4befc3151c63c7d0f43ec4a26cbf5c21877a313274/content`
    — confirmed from the `SharedLinks.aspx` page's own markup rather than
    assumed. See "The Inner Mission North statement" below.
  - William Kostura, *The Inner Sunset: A Historic Context Statement*,
    prepared for the San Francisco Office of Economic and Workforce
    Development, the Historic Preservation Fund Committee, and Inner Sunset
    Park Neighbors, adopted 2024 (238 pp.), source id
    `inner-sunset-context-statement`. Served from the same M-Files vault as
    Dogpatch, Glen Park and Inner Mission North, so the `SharedLinks.aspx`
    URL again returns an HTML shell; the REST content hash is once more the
    page's own `accesskey` —
    `https://citypln-m-extnl.sfgov.org/REST/sharedlinks/%7ba4a7dacd-b0dc-4322-bd29-f6f07103c6e0%7d/9971e8675ef958ced768dcf473ae90d4f57de4db30ba58a6056473462e5f67da/content`
    — confirmed from the `SharedLinks.aspx` page's own markup. See "The Inner
    Sunset statement" below.
  - Richard Brandi and Woody LaBounty (Western Neighborhoods Project), *San
    Francisco's Ocean View, Merced Heights, and Ingleside (OMI) Neighborhoods,
    1862-1959: A Historical Context Statement*, prepared for the San Francisco
    Historic Preservation Fund Committee, adopted January 2010 (64 pp.),
    source id `omi-context-statement`. Served from the same M-Files vault as
    Dogpatch, Glen Park, Inner Mission North and Inner Sunset, so the
    `SharedLinks.aspx` URL again returns an HTML shell; the REST content hash
    is once more the page's own `accesskey` —
    `https://citypln-m-extnl.sfgov.org/REST/sharedlinks/%7ba4a7dacd-b0dc-4322-bd29-f6f07103c6e0%7d/2d0ca8733f531763d1037c5664cf0854ee05d0a478351f4393e05b76d660539c/content`
    — confirmed from the `SharedLinks.aspx` page's own markup. See "The OMI
    statement" below.
  - Page & Turnbull, Inc., *Historic Context Statement: Market and Octavia
    Neighborhood Plan Area, San Francisco, California*, endorsed by the
    Landmarks Preservation Advisory Board 19 December 2007 (136 pp.), source id
    `market-octavia-context-statement`. On the S3 archive at
    `https://sfplanning.s3.amazonaws.com/archives/documents/4688-M%26O_Context-LPAB121907.pdf`.
    Every page footer reads "Draft Endorsed by Landmarks Preservation Advisory
    Board on December 19, 2007"; the SF Planning listing page carries it as
    "Market Octavia Plan Area Historic Context Statement (Adopted 2007)" and
    there is no non-draft file. Cite it as adopted 2007. Its Industrial
    Employment sub-context is separately authored — the PDF's own metadata
    names Timothy Kelley of Workplace History Organization — and the two
    appendices that matter come from it. See "The Market & Octavia statement"
    below.
  - San Francisco Planning Department, with Roland-Nawi Associates (2007),
    Carey & Company (2009) and consultants Katherine Petrin and Shayne E.
    Watson (2014–16), *Mission Dolores Neighborhood Historic Context
    Statement*, prepared for the Mission Dolores Neighborhood Association,
    adopted July 20, 2022 (104 pp.), source id
    `mission-dolores-context-statement`. Served from the same M-Files vault as
    Dogpatch, Glen Park, Inner Mission North, Inner Sunset and OMI, so the
    `SharedLinks.aspx` URL again returns an HTML shell; the REST content hash
    is once more the page's own `accesskey` —
    `https://citypln-m-extnl.sfgov.org/REST/sharedlinks/%7ba4a7dacd-b0dc-4322-bd29-f6f07103c6e0%7d/e312738442fad29bcb74b96538b857ca1a6e1bedd359bbfc0de2d4a255a1b7ae/content`
    — confirmed from the `SharedLinks.aspx` page's own markup. See "The Mission
    Dolores statement" below.
  - William Kostura, *Van Ness Auto Row Support Structures: A Survey of
    Automobile-Related Buildings along the Van Ness Avenue Corridor*, prepared
    for the San Francisco Department of City Planning, adopted 2010 (73 pp.),
    source id `van-ness-auto-row-context-statement`. SF Planning lists it as
    "Van Ness Auto Row Support Structures (Adopted 2010)" and serves it from
    its own site, not the S3 archive or the M-Files vault, at
    `https://sfplanning.org/sites/default/files/documents/preserv/DPRforms/Van%20Ness%20Auto%20Row%20Context%20revised%20June%202010.pdf`
    — a plain fetch, no shell. Same author as the Inner Sunset statement. See
    "The Van Ness Auto Row survey" below.
  - Tim Kelley, *Origins of the Seven San Francisco Carnegie Branch Libraries
    1901-1921*, the context statement inside the January 2001 landmark
    nomination of the Carnegie branch libraries (43 pp.), source id
    `carnegie-libraries-context-statement`. On the S3 archive at
    `https://sfplanning.s3.amazonaws.com/archives/documents/774-Carnegie.pdf`.
    SF Planning lists it as "Carnegie Branch Libraries of San Francisco
    (Adopted 2001)". See "The Carnegie branch libraries nomination" below.
  - Michael R. Corbett, with a 2019 updated survey and evaluation by Katherine
    T. Petrin and Shayne E. Watson, *North Beach, San Francisco Historic
    Context Statement*, prepared for the Northeast San Francisco Conservancy,
    dated 31 January 2018 with revisions as of 8 October 2020, adopted 2022
    (269 pp.), source id `north-beach-context-statement`. SF Planning serves it
    from the S3 archive as a plain fetch, no vault shell:
    `https://sfplanning.s3.amazonaws.com/default/files/Preservation/hcs_north_beach.pdf`.
    It updates and supplements the 1982 North Beach Survey (Bloomfield, Kortum
    and Olmsted), which the Board of Supervisors adopted in 1999 and whose 212
    listed resources it reprints as Appendix B. See "The North Beach statement"
    below.
  - Donna Graves and Page & Turnbull, Inc., *San Francisco Japantown Historic
    Context Statement*, prepared for the San Francisco Planning Department as
    part of the Japantown Better Neighborhood Plan, May 2009 (112 pp.), source
    id `japantown-context-statement`. Served from the same M-Files vault as
    Dogpatch, Glen Park, Inner Mission North, Inner Sunset, OMI and Mission
    Dolores, and the REST content hash is once more the page's own `accesskey` —
    `https://citypln-m-extnl.sfgov.org/REST/sharedlinks/%7ba4a7dacd-b0dc-4322-bd29-f6f07103c6e0%7d/cdea4663bca8a535d9838ce5da267e475c7aab3aa11603092015f6c92a81de15/content`
    — confirmed from the `SharedLinks.aspx` page's own markup. **SF Planning
    lists it as "Japantown Historic Context Statement (Revised 2011)" and serves
    the May 2009 file under that label**; the PDF's own metadata reads
    `Japantown Context Statement_FINAL 5-09.doc` and every page header reads
    "Final Draft". A separate, earlier "Japantown Draft Historic Context
    Statement" (April 2008) sits on the S3 archive at
    `https://sfplanning.s3.amazonaws.com/archives/documents/1862-San%20Francisco%20Japantown%20Better%20Neighborhood%20Plan%20Historic%20Context%204.11.08.pdf`
    and is **not** what the adopted listing points at. See "The Japantown
    statement" below.
  - William Kostura, *The West Slope of Russian Hill: A Historical Context and
    Inventory of Historic Resources for Residential Buildings around Lombard and
    Larkin Streets*, prepared for the Russian Hill Historic Resources Inventory
    Committee of the Northeast San Francisco Conservancy and funded by the David
    L. Klein, Jr. Foundation, 2006, revised 2009 (60 pp.), source id
    `russian-hill-context-statement`. SF Planning lists it as "Russian Hill
    Historic Context Statement (Adopted 2009)". Served from the same M-Files
    vault as Dogpatch, Glen Park, Inner Mission North, Inner Sunset, OMI,
    Mission Dolores and Japantown, and the REST content hash is once more the
    page's own `accesskey` —
    `https://citypln-m-extnl.sfgov.org/REST/sharedlinks/%7ba4a7dacd-b0dc-4322-bd29-f6f07103c6e0%7d/9512011f20332fb5a06a66154d79cd3439701dbf664afb9f6e58f39ad205d0f4/content`
    — confirmed from the `SharedLinks.aspx` page's own markup. Same author as
    the Inner Sunset statement and the Van Ness Auto Row survey. See "The
    Russian Hill statement" below.
  - Richard Brandi and Woody LaBounty (Western Neighborhoods Project),
    *San Francisco's Parkside District: 1905-1957 — A Historical Context
    Statement*, produced for the Mayor's Office of Economic and Workforce
    Development, March 2008, adopted 2008 (58 pp.), source id
    `parkside-context-statement`. SF Planning lists it as "San Francisco's
    Parkside District: A Historic Context Statement, 1905-1957 (Adopted 2008)".
    It is on the S3 archive and needs no vault dance — a plain fetch of
    `https://sfplanning.s3.amazonaws.com/archives/documents/4976-parkside-statement%20march%202008.pdf`
    returns the PDF, and it is born-digital InDesign, so `pdftotext -layout`
    gives clean text with no OCR damage anywhere. See "The Parkside statement"
    below.
  - William Kostura, architectural historian, with Kelley & VerPlanck LLC,
    *Historic Context Statement of the Oceanside: A Neighborhood of the Sunset
    District, San Francisco*, commissioned by SPEAK (Sunset Parkside Education
    and Action Committee) and funded by the Wallace Alexander Gerbode
    Foundation, the Historic Preservation Fund Committee and San Francisco
    Beautiful, May 2007, updated March 2010 (28 pp.), source id
    `oceanside-context-statement`. SF Planning lists it as "Historic Context
    Statement of the Oceanside: A Neighborhood of the Sunset District, San
    Francisco (Adopted 2012)". Served from the same M-Files vault as Dogpatch,
    Glen Park, Inner Mission North, Inner Sunset, OMI, Mission Dolores,
    Japantown and Russian Hill, and the REST content hash is again the page's
    own `accesskey` —
    `https://citypln-m-extnl.sfgov.org/REST/sharedlinks/%7ba4a7dacd-b0dc-4322-bd29-f6f07103c6e0%7d/b36ba92f20d231a0ee387f5dd551d1f2837730f658bd0a0888d5eb7b6842e9c8/content`
    — confirmed from the `SharedLinks.aspx` page's own markup. Same author as
    the Inner Sunset statement, the Van Ness Auto Row survey and the Russian
    Hill statement. See "The Oceanside statement" below.
- **Shape of the yield.** Two very different parts, and both are worth the
  pass:
  - **Appendix A, Table 1** is a per-property inventory — 159 rows carrying an
    APN, an address, a one-line description of the building, ratings from the
    earlier surveys (Here Today 1968, the 1976 citywide architectural survey,
    Article 10, the UMB survey, Carey & Company's South Bayshore survey) and a
    provisional California Register status code. This is structured data; parse
    it from the PDF's word positions rather than from `pdftotext` lines, or the
    superscript in "3<sup>rd</sup> Street" lands in the next row's address
    column.
  - **The narrative chapters** name maybe forty addresses with a real story
    attached, scattered through 190 pages of district history that names none.
    That is the normal ratio; see AGENTS.md → "Mining a corpus."
- **Cautions:**
  - **The addresses in the table are the survey's, not the city's.** Follow the
    APN, not the printed address, and check both against EAS: this one gives
    1420 Phelps Street for a parcel EAS calls 1450, 1773–75 Newcomb Avenue for
    a parcel on McKinnon, 5051 Third Street for the parcel EAS numbers 5075,
    and 1015 Third Street in its recommendations for the 5015 Third Street of
    its own table. Several APNs have since been retired.
  - **The status codes are provisional.** The report says so itself: they were
    assigned on architectural criteria alone. Its own recommendations define
    what the two "3" codes mean here — the 84 rows coded `3CS` are the
    properties it found may be eligible for the California Register under
    Criterion 3, and the rows coded `3S` are the properties it put forward as
    potential National Register or City Landmark listings. It never defines the
    Carey & Company or UMB rating scales, so record those without a gloss.
  - **The report contradicts itself in places** — 4408–42 Third Street is an
    Italianate commercial block in the table and a 1946 Streamline Moderne
    building in the text; 1552 Palou Avenue is an Eastlake farmhouse in one and
    a Queen Anne dwelling in the other. State the disagreement; don't
    adjudicate it.
  - Condition notes ("abandoned", "demolished") are as of 2009, and the
    assessor sometimes disagrees now.
- **The Central SoMa statement is shaped differently, and its inventory is not
  in it.** The adopted statement is 115 pages of narrative with no property
  table at all; the survey's per-property records live in the Historic
  Preservation Commission's adoption packet, which reprints the statement and
  then adds them. Read the packet, not just the statement.
  - **Packet pages 126–253 are the property information catalog**: one page per
    surveyed building, with the APN, the address, the year built, the proposed
    status code and Article 11 rating, the eligible district, and then the
    architect, historic name, style, frame, cladding, roofline, windows,
    ornament, integrity and the 1913 and 1950 Sanborn uses. 75 buildings.
  - **Packet pages 254–481 are the survey results table**, one row per parcel
    in the whole plan area — 1,004 of them. It is printed as six column-groups
    of 38 pages each (254, 292, 330, 368, 406, 444 are the group starts), so
    the columns for one parcel are spread across six pages. Parse it from word
    positions: rows are bottom-aligned, a row's band runs from just past the
    previous MAPBLKLOT anchor's y to its own, the first row of every page puts
    its wrapped opening line at y≈83.8 (above every anchor, below the y=74
    header), and the same band on the matching page of each group is the same
    parcel. Verified against the catalog: architect, historic name, style and
    frame agree on every property the two share.
  - **Take the short columns, not the long ones.** The join is exact but the
    wide free-text columns (ornament, windows, planning notes) overflow their
    column bounds and come back clipped. The catalog has the same fields laid
    out cleanly for the 75 buildings it covers; use it there and take only
    codes, ratings, names, styles and framing from the table.
  - **It contradicts itself between the two.** 633 Folsom Street is 6Z in the
    catalog and 3CS in the results table; 12 Mint Plaza is 6L and 6Z; 66 Mint
    Street is 3CD and 3CB. The catalog also splits a code the table combines
    (`1S, 3CD` against `3CB`). Record both and say which is which.
  - **The narrative contradicts itself too**: the Waldorf lodging house that
    survived 1906 is at 24–26 5th Street in one passage and 44–48 5th Street
    everywhere else; the California Casket Company building is 943 Mission in
    one and 959–965 Mission in the rest; the Central Hotel is 566–586 3rd
    Street twice and 576–586 once; the Southern Police Station is 360 4th
    Street throughout and 350 in a caption; the A. Carlisle building is 1948 in
    the text and 1947 in the recommendations.
  - **Most of the plan area was surveyed before.** For 386 of the parcels the
    only thing this document adds is which earlier survey covered them, and for
    33 it records nothing at all — those get no citation, because a page does
    not cite a source that told it nothing.
  - **A results-table row can describe a building that is gone.** 942 Mission
    Street is coded 6Z for a two-storey warehouse demolished in 2012; the
    assessor dates the hotel there now to 2015. Where the survey's year built
    and the roll's disagree the page states both.
**The Central Waterfront statement has no inventory in it at all, and that is
not a truncated download.** The archived PDF is the 43-page summary report and
context statement. Its table of contents promises eight appendices; six of them
are present only as one-line cover sheets. What is actually in the file:
- **Appendix C** — four maps (survey boundary, street names and the Dogpatch,
  P.G.&E. and Pier 70 sub-areas, the 1899 Sanborn, and the Bethlehem Steel
  general plan of 1957 with the Pier 70 building numbers).
- **Appendix E** — a one-page table of general periods of development.
- **Appendix F** — the definitions of the National Register status codes the
  survey used (1S, 2, 3B, 3D, 3S, 4D2, 4D5, 4R, 4S1, 4S2, 4X, 5S3, 5D1, 5N,
  5B1, 6Z1). Definitions only; no property is assigned one here.
- **Appendices A, B, D, G and H** — cover sheets. The DPR 523 forms, the NR
  Status Code Matrix, the Station A forms and Christopher VerPlanck's Dogpatch
  Historic Resource Survey and its own status-code matrix are all elsewhere.
  So **no per-property status code can be taken from this document.** The body
  gives them only by district and only as a majority ("the majority of
  resources in the Dogpatch neighborhood have been identified as 5D1"), which
  is not a finding about any one building — don't assign it to one. VerPlanck's
  Dogpatch survey is listed separately on the same SF Planning page as
  *Dogpatch Historic Context Statement*; the forms are the thing to go after
  when that one is read.
- **The addresses are in the narrative, and there are nine of them.** Two
  paragraphs on small oil companies and small Art Deco industrial buildings
  name four Third Street and 18th Street addresses as type examples; two more
  paragraphs on early dwellings name five. Everything else the report discusses
  is identified by Pier 70 building number (101, 102, 104, 105, 108, 109, 113,
  114, 116, 117, 118, 21, 38 — from a 1957 Bethlehem Steel plan, not a street
  grid) or by intersection: the California Canneries building at Minnesota and
  18th, the American Barrel Company at Sierra (22nd) and Illinois, the Western
  Sugar Refinery remnant at the foot of 23rd Street, the du Pont powder
  magazine at Maryland and Humboldt, the Union Iron Works administration
  building and Weeks & Day powerhouse at Illinois and 20th. None of those
  carries a street number and none of them became a page.
- **Cautions specific to it:**
  - **A named address can be a site, not a building.** 550 18th Street and
    2075 Third Street are one parcel (3994044), and the small oil-company
    buildings the survey pointed at are gone — the roll dates what stands there
    now to 2008 and Planning codes the parcel C. That address is documented as
    site history, not as a surveyed building.
  - **It contradicts itself on 718 22nd Street.** The text describes the
    dwelling at 718; footnote 32 and the bibliography both cite the DPR 523B
    form for it as "118 22nd Street". There is no 118 22nd Street in EAS. Both
    readings are on the page.
  - **Its dates run 20 to 30 years earlier than the assessor's.** The roll
    gives 1900 for four of these dwellings; the survey gives 1872, 1876, circa
    1875 and circa 1884. 1900 is the roll's default for a building it can't
    date, so the disagreement is worth recording rather than resolving.
  - **"Outside Dogpatch" means outside the 2001 survey's Dogpatch boundary.**
    Three of the buildings it files that way — 670–674 Tennessee, 2476–2478
    and 2636–2638 Third — are inside the Article 10 Dogpatch Historic District
    today. Don't read the survey's placement as a statement about the district.
  - Street renamings are given in passing and are worth keeping: Kentucky
    Street became Third Street, Sierra Street became 22nd Street, and the
    east-west streets were numbered in the first years of the 20th century.
**The Corbett Heights statement has three inventories and none of them is an
appendix table of the usual kind.** The document is a narrative history with
its address-level findings scattered across five places, and they disagree with
each other often enough that the disagreements are half the yield:
- **Section VI.B, "Potentially Significant Resources"** (pp. 188–189) — 48
  addresses with an estimated date and a one-line style. The report says in the
  same breath that it is *not a survey*, that the list is conservative rather
  than exhaustive, and that omission from it means nothing. Every page that
  carries a row from it says so.
- **Appendix F reprints two earlier surveys.** The 1968 Junior League *Here
  Today* listing (21 addresses with a one-line identifier) was adopted by the
  Board of Supervisors under Resolution No. 268-70, so Planning counts those
  buildings as individual historic resources — that is the one place in this
  document with real regulatory weight. The 1976 Department of City Planning
  architectural survey (74 rows) gives a block and lot, an address, and a
  rating of 0–5 where a second number is a reviewer's revision; it was never
  adopted. Appendix F also carries the two City Landmarks in the area,
  No. 79 (Miller-Joost House, 3224 Market) and No. 80 (Nobby Clarke Mansion,
  250 Douglass), both designated 7 December 1975.
- **Two "Partial List of Buildings" tables** (pp. 78 and 142) are the best
  thing in it — 23 buildings of 1860–1906 and 15 of 1906–1945 with a date and
  a named architect, contractor or builder drawn from *California Architect and
  Building News*, the historian Gary Goss's files and the 1900 census. **Their
  owner column is dropped on the way in**, per the privacy rules; the
  architects and contractors are kept.
- **The rest is in figure captions.** Roughly forty more dates and styles
  appear only under photographs, and several of them contradict the tables.
- **Cautions:**
  - **The 1976 block and lot are 1976's.** Nineteen of its 96 parcels no longer
    exist in EAS, and several that do have been re-lotted so the old lot now
    points at a different building: 2655/22 is printed "1262 Clayton" and
    resolves to 1272; 2656/27 is printed "3090 Market" and resolves to 3088;
    2654/8 is printed "48 Mars" and resolves to 52; 2625/18 is printed "2
    Douglass" and resolves to 7 Ord. Match on the printed address, record the
    printed block and lot beside it as `apn_as_surveyed`, and let a reader see
    both.
  - **It contradicts itself on dates.** 99 Ord Street is 1931 in the text and
    1932 in the potentially-significant list; 312 Caselli is 1894 in a caption
    and 1893 in the list; 64–68 Douglass is 1908 in a caption and 1909 in the
    architects' table; 4789 Nineteenth is 1908 in the table and 1909 in the
    text. Moody's candy factory is at 4655 Eighteenth in one passage and 4653
    in another, and the Coffin row on Caselli is seven houses in the text and
    eight in the builder's own advertisement. All of these are on the pages as
    stated disagreements.
  - **Its dates run ahead of the assessor's, and the roll's 1900 is a
    placeholder.** Where the two disagree the page shows the roll in the
    `Built …` tag and the report's date as `building.completed`, with the
    conflict named in `.unknowns`.
  - **Condominium conversion has eaten a lot of this area.** Fifteen of the
    parcels the report names are now condominium APNs the roll gives 0 lot
    area, so AGENTS.md holds them back — including three of the buildings the
    1968 survey listed.
  - **It names San Francisco addresses well outside the neighborhood**, as the
    other work of the architects who built in it (the Chancellor Hotel, the
    Native Sons Building, the James Lick Baths, the Chateau Tivoli) and as the
    house of the man who subdivided it. Those are documented as building
    credits on their own pages, not as anything the statement surveyed.
**The Dogpatch survey is the report the Central Waterfront statement points at,
and it stops one section short of its own inventory.** Its table of contents
promises four sections and the PDF carries three: the description of the
neighborhood, the context statement, and the illustrations. **Section 4,
"Dogpatch Historic District Survey Forms," is not in the file** — pages 30–35
are figures and the document ends there. So this one, like the Central
Waterfront statement, assigns no status code to any single building, and the
DPR 523B forms it cites in its own footnotes are still elsewhere.
- **What is in it is narrative, and dense with numbers.** The two prose
  sections name 90 distinct numbered San Francisco addresses in 28 pages, a far
  higher rate than the other statements here — the description section alone
  lists the neighborhood's builders address by address, and its non-contributor
  and heavily-altered paragraphs are effectively an inventory written as prose.
- **Cautions specific to it:**
  - **The survey's dates run 5 to 30 years ahead of the assessor's, and the
    roll's 1900 is a placeholder.** Of the 60 parcels documented here, 23 carry
    a dated conflict. Where the two disagree the page shows the roll in the
    `Built …` tag and the survey's date as `building.completed`, with the
    conflict named in `.unknowns`.
  - **Its printed ranges do not always match a parcel.** "800-04 22nd Street"
    spans two parcels (800–802 and 804–806) and both pages say so; "760-790
    Tennessee" spans three; "1103-05 Tennessee" and "1105-07 Tennessee" are the
    same building under two numbers in the same document, and only 1105–1107 is
    an address the city carries. Match on the printed address, record it as
    `address_as_surveyed`, and let a reader see both.
  - **It repeats the Central Waterfront statement's 118 22nd Street error** —
    the same author's footnote again gives the DPR 523B form for the dwelling
    at 718 22nd Street as "118 22nd Street", an address EAS has never had.
  - **It contradicts itself on the vacant lots**, listing "six vacant lots" and
    then naming seven, and on 740 Tennessee Street, which it says was
    constructed in 1881 and, four pages later, was moved to the site that year.
    Both readings are on the page.
  - **Two of the buildings it calls non-contributors predate the period of
    significance it gives.** 991 Tennessee (roll: 1933) and 1025 Tennessee
    (roll: 1937) are grouped with the 14 buildings it says were "constructed
    after the period of significance," which it defines as 1867–1945.
  - **Condominium conversion has taken out much of the best of it.** Fourteen
    of the addresses it names are now condominium APNs the roll gives 0 lot
    area, so AGENTS.md holds them back — including 920–922 Minnesota, half of
    the pair it names as a type example, and 1016–18 Tennessee.
  - **Business proprietors are named throughout** — the grocers, saloon-keepers
    and butchers of the 1890s to the 1940s, by name and address. Those are
    owners and occupants, so the pages carry the **firms** (Howley's Liquors,
    Dugan's Liquors, J. J. Twomey & Son's Market, Graham Fuel & Feed) and not
    the people. The architects, carpenters and contractors are kept.
  - Street renamings are given in passing, matching the Central Waterfront
    statement: Kentucky Street became Third Street, Sierra Street became 22nd
    Street, Butte Street became 19th, Solano Street became 18th, and Napa
    Street became 20th.
**The Duboce Triangle statement has no inventory table at all.** Like Central
SoMa, it is narrative from end to end: 130 pages of neighborhood history, a
chapter on property types and architectural styles, and a recommendations
chapter. The accompanying survey inventoried 552 properties and its
spreadsheet is not in the file, so the statement assigns no status code, rating
or per-property record to anything. What it does carry, and what the pages here
take, is a list of potential city landmark candidates, five proposed local
landmark districts with their member addresses printed out, and several dozen
buildings named in the narrative with a style, an estimated date and a reason
for the mention.
- **Cautions specific to it:**
  - **The candidate list is 38 entries and the text calls it 37.** "Presented
    below is a list of 37 potential city landmark candidates," the
    recommendations chapter says, and "Photographs of all 37 properties follow";
    the introduction says 38 twice. The bullets number 38. Every page that
    carries the candidacy says so.
  - **It contradicts itself on addresses more than most.** The Charles Strothoff
    House is 2274 15th Street in the narrative, 2272–2276 15th Street in the
    candidate list and 2272–2276 **16th** Street in the styles chapter; the
    apartment building at 221 Noe Street is 211 Noe in its figure caption; the
    1937 mixed-use building at 286–288 Noe Street is 266–268 Noe in its figure
    caption; 282 Castro Street is 282 **Church** Street in its figure caption;
    2168 15th Street is 2168 **18th** Street in its figure caption; the
    Norwegian-Danish Methodist church is 750 14th Street in the Scandinavian
    institution list and 754 14th Street in the narrative, and EAS has only 750.
    Follow EAS, record the printed form as `address_as_surveyed`, and name the
    disagreement.
  - **It contradicts itself on dates and on the Born tract's builder.** 963 14th
    Street is Ca. 1885 and Ca. 1880; 245 Castro Street is Ca. 1870 and Ca. 1875;
    101–111 Noe Street is Ca. 1890 and Ca. 1895; 106–112 Noe Street is 1924
    and 1922; 178–180 Church Street is a 1937 building and a 1911 building
    remodelled Ca. 1935; 3633–3635 16th Street is a 1940s building and a
    Victorian remodelled Ca. 1935; the St. Ansgar/Gethsemane merger is 1964 and
    1965; the Castro Street tract is Stephen A. Born's and William S. Born's.
    Both readings go on the page.
  - **Its "Ca." dates are estimates and the roll's 1900 is a placeholder**, so
    most of the disagreement between them is not a finding. The estimated date
    goes in `historic_survey.year_built_as_surveyed`, never in
    `building.completed`, which is reserved here for the dates the statement
    documents outright.
  - **Condominium conversion has taken out a quarter of what it names.**
    Twenty-eight of the parcels are now condominium APNs, which AGENTS.md holds
    back — including nine of the 38 landmark candidates. Ten of those
    twenty-eight are conversions since the last roll year their old APN appears
    in, so the APN EAS still carries has no 2025 roll row and the successor is a
    condominium.
  - **The Market Street frontage is deliberately outside its survey** — it was
    covered by the 2006–09 Market & Octavia survey — but the statement
    discusses those buildings anyway, so the Swedish American Hall, the José
    Theater and Safeway are all named without being inventoried.
  - **Business proprietors and building owners are named in passing**, as in the
    Dogpatch survey. Architects, builders and contractors are kept; residents
    and owners are not.
**The Eureka Valley statement has no appendix inventory either, and its
address-level findings are spread across four places.** Like Central SoMa and
Duboce Triangle it is narrative from end to end — 240 pages of neighbourhood
history, property types and styles, evaluation frameworks and recommendations —
with no property table and no status code assigned to any building. What it
carries at address level is:
- **The builder tables in the Streetcar Suburb chapter** (pp. 51–55), the best
  thing in it. Fernando Nelson's is a real inventory: ~50 rows of address, date,
  house form and style. Shorter runs follow for Charles L. Hinkel (5 houses),
  Louis Landler (11), John Anderson (2 rows covering 19 houses) and John A.
  Swenson (2).
- **The figure captions in the property-type and architectural-style chapters**
  (pp. 135–201), which are effectively a second inventory written as captions:
  roughly ninety buildings with a date, a form and a style.
- **The narrative chapters**, which name the churches, halls, banks, garages,
  schools, the library, the post office, the recreation centre, the breweries
  and bottling works, and — through long quotations from the 2015 citywide
  LGBTQ context statement — several dozen bars, shops and organisations.
- **The evaluation frameworks** (pp. 204–240), which name about twenty-five
  buildings as worked examples of what might be eligible under each criterion,
  and the **recommendations** (pp. 241–243), which put forward three potential
  San Francisco Landmarks — the Fernando Nelson House, the Kirby House and
  Phoenix Brewery, and the Charles Hinkel House — plus four concentrations of
  developer housing to study as potential historic districts.
- **Cautions:**
  - **Check a printed disagreement against the parcel before recording it as
    one.** This statement names buildings by whichever of a parcel's street
    numbers is to hand, and several apparent contradictions are nothing of the
    kind: Cliff's Variety is 471 Castro Street in the property-type chapter and
    479 in a footnote, and EAS puts 471, 479 and 483 on one parcel; the bank at
    Castro and Market is 410 in most passages, 400 and 400–410 in two captions,
    and 400 and 410 are one parcel. Collingwood Hall's 4144 and 4150 18th
    Street, and the Elephant Walk's 500 and 506 Castro Street, are the same
    again. Resolve both numbers before writing the disagreement down.
  - **The disagreements that survive that test cluster on its own landmarks.**
    The Castro Theater is 429 Castro Street in the landmark list and the style
    chapter and 429–431 in a caption, but the recommendations and an LGBTQ HCS
    quotation attach **Landmark #100 to 479 Castro Street** — a different parcel,
    and the one the statement itself identifies as the site of the Nasser
    Brothers' theatre of 1910, this theatre's predecessor, so the slip is
    between the two theatre sites rather than random. The Twin Peaks Tavern is
    401 Castro Street in the landmark list and **410** in an LGBTQ HCS
    quotation, 410 being the bank across the intersection. The Kirby/Phoenix
    Brewery building is 552 Noe Street in a caption and **560** in the
    industrial-production framework — two parcels — while the Kirby residence is
    560 in the narrative and **550** in a caption, a number EAS has never
    carried. Collingwood Hall is on 18th Street throughout and on **Collingwood
    Street** once. The Swedish-American Hall is 2168–2173 Market Street in the
    landmark list and **1274 Market Street** twice; the Women's Building is 3543
    18th Street once and **3548** twice, a different block. Nelson's Hartford
    Street row is 20–64 in the builder table and **2–64** in the
    recommendations. Record both readings and follow EAS.
  - **It contradicts itself on dates too.** Most Holy Redeemer is 1901 in the
    narrative and 1900 in the style chapter; the recreation centre is 1954 in a
    caption and 1956 in the text; 3951–3959 17th Street is 1910 with 28 units in
    one caption, 1910 with 20 units in the evaluation framework and ca. 1915 in
    another caption; 546 Liberty Street is 1897 in Nelson's table and ca. 1900 in
    a caption; 187 Douglass Street is ca. 1900 in one caption and ca. 1870 in
    another; 2500 Market Street is 1933 in the text and 1920 in a caption; the
    Hinkel house is 1892 in the builder table and 1891 in the recommendations,
    and Hinkel dies in 1908 in one passage and "sometime between 1900 and 1910"
    in another. The Castro group is 740–748 Castro, ca. 1892 in one caption and
    742–750 Castro, 1895/1898 in another.
  - **Its dates are reconnaissance-level and the statement says so twice** — it
    is "an evaluative tool, not a decision-making document," and inclusion or
    exclusion "does not represent a value judgement." Every page carrying a row
    from it says so.
  - **The roll's 1900 is a placeholder here as elsewhere**, so most of the gap
    between the statement's dates and the assessor's is not a finding. The
    statement's date goes in `historic_survey.year_built_as_surveyed` and is
    dropped where it simply matches the roll.
  - **Condominium conversion and stale APNs take out a tenth of what it names.**
    Twelve of the parcels are condominium APNs AGENTS.md holds back — including
    both halves of Nelson's 4141–4143 20th Street and his best house, the
    towered 4138 20th Street — and twenty more have no 2025 roll row, among them
    the Most Holy Redeemer neighbours at 150 Eureka Street, the earthquake
    cottages at 300 Cumberland Street and the Swedish-American Hall.
  - **Business proprietors, club presidents and bar owners are named
    throughout.** The firms are kept (Cora Lou Confectioners, Eggers & Company,
    the Phoenix Brewery, Ruby's Clay, Littleman's, McNaughton & Turner) and the
    proprietors are not. Architects, builders and contractors are kept, as are
    the public figures the historical record already covers — Harvey Milk, Bob
    Ross, Cleve Jones, Bobbi Campbell, Mayor P. H. McCarthy — and the civic-club
    leaders whose houses the statement names as their significance.
  - **It names addresses well outside the study area** as landmarks "related to
    Eureka Valley," as the earlier homes and first houses of its builders, and
    as citywide style examples. Those are documented as what they are, not as
    anything this statement surveyed.
**The Glen Park evaluation is a CEQA document, not a survey report, and that
changes the shape of everything in it.** Carey & Co. wrote it for the Glen Park
Community Plan EIR: a context statement of the neighborhood, a reconnaissance
survey of 110 parcels, an intensive survey of eight, a district analysis, an
impacts analysis and mitigation measures. It is 118 pages, of which roughly 30
are the context statement and 25 the property evaluations; the rest is
regulatory framework, prehistory, CEQA impact findings and the project
description. Where it carries address-level facts:
- **The "Description and Evaluation of Surveyed Properties" chapter**
  (pp. 44–60), the best thing in it — a full description, a documented
  construction date, an architect or builder from the building permits, an
  eligibility finding and an integrity assessment for each of seven properties
  on eight parcels: 584 Bosworth Street, 21 Brompton Avenue, 23–25 Brompton
  Avenue, 2830–2842 and 2852–2862 Diamond Street, the Glen Park BART station
  and its power station, and the Glen Park Elementary School. Five are found
  not eligible, the station eligible for the California Register only, and the
  school eligible for the National Register, the California Register and City
  Landmark designation.
- **A five-entry list in the impacts chapter** (p. 67) of the buildings the
  **San Francisco Planning Department** — not Carey & Co. — found eligible for
  the California Register in its own survey of the area west of Lippard Avenue
  and the NC district: 601 Bosworth Street, 657, 683 and 701–703 Chenery
  Street, and 2784–2786 Diamond Street. That survey, "Glen Park Area Plan HRE:
  West of Lippard and NCT" (SFPD 2010), holds the DPR forms and is a separate
  document.
- **The cultural-context and property-type chapters**, which name about
  thirty addresses as dated examples of a builder's cottages, a style or a
  building type, mostly in photograph captions.
- **Cautions:**
  - **Appendix C is a cover sheet.** The introduction says every one of the 110
    surveyed parcels was recorded on a DPR 523A form and the eight evaluated
    ones on 523B forms, "which are located in Appendix C." The appendix in the
    archived PDF is one title page and nothing else, so **no per-property DPR
    record, rating or status code can be taken from this document** — the
    reconnaissance survey of the other 102 parcels is effectively not in it.
    Appendices A-1 and A-2 are maps and Appendix B is the project description.
  - **It assigns no California Historical Resource Status Codes at all.** It
    lists the seven code headings in its regulatory chapter and then evaluates
    in prose. Pages carry the finding in `historic_survey.finding`, which is
    why that key exists; never translate a finding into a code.
  - **It contradicts itself on addresses, and the archived scan is annotated.**
    The Planning Department's eligible list prints "2784-2786 Chenery Street"
    for a Diamond Street parcel, and someone has written DIAMOND above it in
    ink on the archived copy. A photograph caption gives 701 Chenery Street as
    "107 Chenery Street"; the Spanish Eclectic commercial building at Chenery
    and Diamond is 664–670 in the text and 664–676 in both its captions, which
    is three parcels rather than two; 645 Bosworth Street is "645 Bosworth
    Avenue" four times and never "Street"; and 23–25 Brompton Avenue is
    "Brompton Street" twice.
  - **Its own counts do not always match.** The Craftsman row it prints as
    "763-791 Chenery Street" is "a row of five Craftsman homes" in the text and
    six parcels on the roll, all of them built 1921–1922.
  - **The city has since disagreed with its district finding.** The evaluation
    examined four concentrations, including the commercial core at Diamond and
    Chenery, and concluded that no eligible historic district exists in the
    plan area; Planning now carries seven of these parcels in the California
    Register-eligible **Glen Park Center Historic District** (period of
    significance 1897–1929). Planning also gives the BART station as
    individually listed on the National Register, which this evaluation found
    it not yet eligible for. Both disagreements are stated on the pages.
  - **Its dates are from building permits, not estimates**, so where they
    disagree with the roll the disagreement is real: 657 Chenery Street is 1872
    against the roll's 1900, 701–703 Chenery is "the early 1890s" against 1904,
    and 2852–2862 Diamond is 1925 against 1924. It also describes 21 Brompton
    Avenue as a three-story apartment building where the roll has a two-story
    single-family dwelling.
  - **It is dense with residents, and they are the bulk of its property
    histories.** Each of the five evaluated non-eligible properties gets a
    paragraph tracing owners and tenants through the census, city directories,
    voter registrations and the assessor's sales ledgers, by name and
    occupation, some of them still the owners. All of that is left out under
    the privacy rules. The **firms** are kept (the Mission Building Company,
    Van's Barber & Beauty Shop, Kerr's Toggery, the Glen Park Cleaners, Lucas'
    Hair Designing, the Glen Park Barber Shop, Derian Jewelers, the Enterprise
    Steam Beer Saloon, the G. H. Umbsden Realty Company), and so are the
    architects and builders (V. Teslo, Christopher J. Kernan, H. Barker, Lewis
    P. Hobart, Bliss & Fairweather, J. L. McLaughlin, Leo Epp, DeLuca and Sons,
    Ernest Born, Corlett & Spackman, Douglas Baylis, William G. Merchant, and
    the dairyman William Tietz who built his own house).
**The India Basin survey is the one document in this set whose own DPR 523
forms are in it**, and they are most of its value. It is 120 pages: 51 of
narrative, bibliography and recommendations, and the rest an appendix holding
38 Primary Records (523A), 13 Building, Structure and Object Records (523B) and
one District Record (523D) for a proposed boat-yard district. Where its
address-level facts are:
- **The 38 Primary Records** cover every building in the survey area built in
  or before 1962 — an APN, a street address, a construction date from the
  Department of Building Inspection, a resource-attribute code and a paragraph
  of physical description apiece. A Primary Record carries no status code and
  no eligibility finding, so most of these become a survey panel with a note
  and nothing else.
- **The 13 Building, Structure and Object Records** are the evaluated ones:
  a National Register status code (3S, 3CS, 6L, 6Y, 6Z), an architectural
  style, a builder, a construction history and a written eligibility finding.
  Four properties are found eligible — the Albion Brewery (881 Innes, National
  Register), and 900 Innes, 911 Innes, 967 Innes and 702 Earl Street for the
  California Register — and the rest are found ineligible, two of them with a
  note that they nevertheless warrant special consideration in local planning.
- **The District Record** proposes an India Basin Boat Yards district of eight
  parcels centred on Hudson Avenue and Griffith Street, eligible for the
  California Register under Criteria 1 and 3, period of significance 1893–1935.
  It describes each parcel's docks, ways, shops and sheds by APN, and it is the
  only place the report dates the boat-yard buildings.
- **The narrative chapters** name about a dozen more addresses — the school,
  the co-operative store, Anderson's own house and shop, the war-worker
  "junior fives" — of which most are numbers the city no longer carries.
- **Cautions:**
  - **The locational-data field (P2e) on a Primary Record is often the
    previous form's APN, copied down a run of adjacent properties.** 714, 718
    and 724 Innes all print Lot 003B; 939, 943 and 947 all print Lot 016B;
    1064 and 1068 both print Lot 007A. The form's own identifier field (P1) is
    the correct one in every case checked, and it is what the assessor's
    `property_location` agrees with. Take P1, not P2e.
  - **Two forms print the wrong block.** 951 and 955 Innes are given as Block
    3653; both are Block 4653.
  - **Its own counts do not match the appendix.** The methodology chapter says
    it prepared 523B forms "for twelve individual properties built before
    1939"; the appendix holds thirteen, all of them pre-1939. The report also
    gives the Hunters Point Restaurant a 1976 summary rating of 1 at 850 Innes
    while filing the restaurant's Primary Record under 840 Innes.
  - **EAS is the stale side here, not the survey.** 863 and 869 Innes Avenue
    resolve in EAS to Lots 014B and 014A, parcels the assessor has retired and
    the parcel dataset marks inactive; the survey's Lots 022 and 021 are the
    live ones and carry those addresses on the current roll. 714 Innes has an
    EAS row with no parcel number at all, and the survey's Lot 003 is what the
    roll puts the address on.
  - **It contradicts itself on the Hunters Point Restaurant, and on two
    dates.** The restaurant is 840 Innes Avenue in the property-type chapter
    and on its own form, and 850 Innes Avenue — Pop Anderson's house — in the
    1976-survey list and the condition chapter. 869 Innes is 2003 on its form
    and a 1938 "junior five" in the narrative; 967 Innes is 1917 on its form
    and in its building record and 1920 in the narrative; 963 Innes is the
    Wilmer and Hilda Wilson Residence on its form and "the Jorgensen cottage"
    in the narrative. Two of the building records date a house a year before
    its own Primary Record does (935 Innes: June 1934 against 1935; 993 Innes:
    November 1937 against 1938).
  - **Its addresses for the church do not agree either.** Our Lady of Lourdes
    at 410 Hawes Street is also identified as 955 Innes Avenue, which is a 1956
    dwelling on a different parcel across the avenue.
  - **The eight-parcel district it proposed is not the district the city now
    carries.** Planning maps the India Basin Scow Schooner Boatyard Vernacular
    Cultural Landscape over these parcels, California Register-eligible with a
    period of significance of 1875–1936, against the survey's 1893–1935. Both
    are on the pages.
  - **A large block of the waterfront has left the secured roll.** 702 Earl
    Street and 840 Innes Avenue, and four of the eight boat-yard parcels
    (4630/006, 4645/010, 010A and 011), are active parcels with EAS addresses
    whose APNs last appear on the 2023 roll, so the seeder makes no page for
    them — including the Heerdt boat yard at 702 Earl, one of the four
    properties the survey found individually eligible.
  - **The Building, Structure and Object Records are chains of title.** Each
    one traces owners and tenants by name through deeds, city directories and
    the census, often to the present owner, and the Primary Records print the
    current owner's name and address outright. All of that is left out under
    the privacy rules. The **builders** are kept (William J. Heerdt, Leo R.
    Miller, Konrad W. Richter, Arthur Simpson, Wilmer W. and Hilda A. Wilson,
    Ingeborg Jorgenson, Paul Runge, George M. Moore, James F. Gibbs and
    Katherine Stauffer), as are the shipwrights the repo already names —
    Johnson J. Dircks, William I. Stone, Henry P. "Pop" Anderson, Charles J.
    Jorgenson, Fred Siemer — the architects of the brewery's 1938
    reconstruction (Bakewell & Weihe), and the **firms** (Anderson &
    Cristofani, Allemand Brothers, Siemer & Bruer & Co., Wm. J. Heerdt Boat
    Building, Surfside Liquors, Nueva Castilla Iron Works, the Mountain Springs
    Water Company, R. F. J. Meiswinkel Co., Skyscraper Crane and Rigging Co.,
    Market Fellowship, the Hunters Point Co-operative Society).
  - Street renamings are given throughout and are worth keeping: Innes Avenue
    was 9th Avenue South and, for a decade from about 1880, Corea Avenue;
    Hudson was 8th Avenue South and Banama; Galvez was Trinidad; Griffith was
    'G' Street, Hawes 'H' Street, Lane 'L' Street; Evans was 5th Avenue South;
    Ingalls Street became Middle Point Road. The present names date from 1910.
**The Inner Mission North statement is short — 62 pages against the 118–261 of
the others read so far — and names far more addresses per page than any of
them, because its yield is almost entirely contributor lists rather than
individual write-ups.** There is no appendix inventory table of the usual
kind; instead Part 5, "Survey Findings," carries five proposed historic
districts and locally significant areas, each with its own contributory and
non-contributory building list printed as a comma-separated run of street
numbers, plus a short "properties of individual significance" list and a
"designated resources" list of buildings already landmarked. **453 distinct
numbered addresses are named**, counting a printed range by its low number:
the Guerrero Street Fire Line and Ramona Street National Register eligible
districts; the Hidalgo Terrace and South Van Ness Avenue–Shotwell–Folsom
Streets (SVN-S-F) California Register eligible districts; the Mission
Reconstruction District and Inner Mission Commercial Corridor (formerly the
"16th Street Commercial Corridor") locally significant areas; sixteen
properties of individual significance; eight designated resources (Tanforan
Cottages, the Mission Armory, the Sheet Metal Workers Hall, the Victoria
Theater, the Levi Strauss & Co. factory, the San Francisco Labor Temple, and
the Liberty Street Historic District); and the "Mission Historic
Entertainment theme," a short list of 16th Street and Mission Street theaters.
- **Cautions:**
  - **The document's own cover reads 2005; SF Planning's listing page reads
    2004.** The title page dates the survey "October 2001 – September 2005"
    and the PDF's own metadata title is "IMN Context 2005.doc," but the
    listing page files it as "Inner Mission North Historic Context Statement
    (2004)." Cited here as adopted 2004, per the listing page, with the
    cover's 2005 recorded alongside it.
  - **It is served from the same M-Files vault as the Dogpatch survey and the
    Glen Park evaluation, and the `SharedLinks.aspx` URL again returns an HTML
    shell.** Unlike those two, this document's REST content hash *is* its own
    `accesskey` — `…/REST/sharedlinks/%7ba4a7dacd-b0dc-4322-bd29-f6f07103c6e0%7d/ef5726f8f01317048294fa4befc3151c63c7d0f43ec4a26cbf5c21877a313274/content`
    — which is not something to assume from the other two documents' pattern;
    it was confirmed by fetching the `SharedLinks.aspx` page and reading the
    link its own markup embeds.
  - **The district lists are the survey's own boundary calls, not the city's
    Article 10/11 districts.** None of the five is currently a designated
    historic district; the survey proposes them as eligible or locally
    significant. Planning's own historic-resource-status data (`sf-planning`)
    independently flags many of the same parcels; where it does, the two
    agree without exception in what's been checked.
  - **An APN off the 2025 roll is usually a condominium conversion in
    progress, not a dead end.** Of the 43 addresses named here whose EAS
    parcel has no 2025 secured-roll row, 41 resolve to a live successor parcel
    via `sf-parcels` (`acdm-wktn`) rather than nothing at all, and 38 of those
    41 successors are themselves condominium or commercial-condo units —
    including 330 South Van Ness Avenue, whose retired APN last appears on the
    2021 roll as a tenancy-in-common building. Following the retired APN
    forward is what tells a genuine re-lotting (a live building parcel under a
    new number, as at 245 14th Street, 1834 15th Street, 80 Julian Avenue and
    87-89 Ramona Avenue, all four seeded here) apart from a condominium
    conversion, rather than treating "off the 2025 roll" as the end of the
    inquiry either way. AGENTS.md holds condominium unit parcels back the same
    as any other neighborhood's.
  - **The printed ranges are not always one parcel.** Twenty-one of the
    contributor-list entries print a range that spans more than one parcel on
    the block face (same-parity numbers only) — "3200-3214 17th St," for
    example, covers two. Each is documented on the parcel of its printed low
    number; the entry is not split into a page per parcel it happens to touch.
  - **376 Shotwell Street is 376-382 Shotwell Street four pages later.** The
    historical note on St. Charles School gives the single number; the
    individual-significance list gives the range. Both readings are on the
    page.
  - **The Louis Roesch Company plant the report names at 1886-1898 Mission
    Street, "to be demolished 2006," is gone.** EAS still carries the address
    on parcel 3547003, but no roll row exists for it on the 2025 secured roll
    at all — not even a condominium one — consistent with the report's own
    prediction and not documented here.
  - **Business proprietors are not named in this statement**, unlike the
    Dogpatch and India Basin surveys; nothing had to be withheld for that
    reason. The Thompson sisters who deeded Hidalgo Terrace to the city in
    1916 are named as subdividers of the land, not as residents or owners of
    any building documented here.
**The Inner Sunset statement has no appendix inventory table at all — the
narrative chapters are the whole of it, and they name addresses far more
densely than any other statement read so far.** Its "Architecture and
building types" chapter (pages 116–224 of 238) profiles builders and
architects one at a time and illustrates each with several of their houses,
so a single builder's profile can name a dozen addresses in a page or two.
Many entries are figure captions in a consistent shorthand — "1049 Irving
Street. Year built: 1894. Contractor: Henry Behrens." — which read directly
into a `historical_record` entry; the surrounding prose fills in style,
moves, and later use.
- **Cautions:**
  - **The rural-years chapters (pages 12–72) name very few street numbers.**
    Addressing hadn't reached the Inner Sunset yet for most of the period they
    cover; land is identified by cross streets and tract names, not numbers,
    and the few numbered addresses that do appear (early roadhouses,
    landowners' final home sites) mostly predate the buildings that stand on
    those parcels today. This chapter was read in full; its low yield is the
    expected shape, not a sign anything was skipped.
  - **A number sometimes gets two different construction dates from the same
    document.** 1225 Eighth Avenue is dated 1900 in the "surviving nineteenth
    century houses" chapter and 1903 in builder Alphonso Harrington's own
    profile. Both readings are recorded, per AGENTS.md.
  - **A printed range can span two EAS parcels that are genuinely two
    buildings, not a clerical range.** 320–326 Judah Street is one landmark
    building (Article 10, "DOELGER BUILDING") split across parcels 1763020
    and 1763021 with identical assessor figures; documented once, at 320,
    the parcel that already had a page. 1352–1360 Irving Street is different:
    the statement's own text ties both halves to one 1926 building by
    architect Samuel Heiman flanking the since-demolished Irving Theater, and
    EAS confirms two live parcels (1340/1342/1360 and 1352/1356, the latter
    sharing frontage with 1288 Fifteenth Avenue) — both are documented, since
    both are real, standing buildings.
  - **Only architects, builders, contractors and named firms are recorded
    here** — no first owners, residents or occupants, including where the
    statement names one as a building's architect *and* its first occupant
    (Charles J. Colley at 1329–1331 Ninth Avenue); only the architect role is
    kept.
**The OMI statement is short — 64 pages, no appendix inventory table, and a
narrative built around four distinct sub-neighborhoods (Ocean View, Ingleside,
Ingleside Terraces, Merced Heights) rather than one continuous history.**
Its addresses come almost entirely from figure captions illustrating each
neighborhood's property types — "Ocean View residential: 222 Plymouth Avenue,
built 1904" — plus a handful of addresses named in the narrative text
(the Ingleside Racetrack land sale, the Geneva car barn, earthquake-cottage
examples). This is the low end of the density range for the series: about
0.6 addresses per page, against the Inner Sunset's ~1.5.
- **Cautions:**
  - **The four sub-neighborhoods split across two different DataSF analysis
    neighborhoods, and Ingleside Terraces is its own EAS category.** Ocean
    View, Ingleside and Merced Heights addresses all resolve to
    `nhood='Oceanview/Merced/Ingleside'`; Ingleside Terraces addresses
    (Cedro, Moncada, Borica, Cerritos, Victoria, and the upper 1500–1900
    block of Ocean Avenue) resolve to `nhood='West of Twin Peaks'` instead,
    a category shared with several unrelated neighborhoods. Following the
    root AGENTS.md precedent that split Corbett Heights out of Castro/Upper
    Market, Ingleside Terraces got its own neighborhood directory
    (`san-francisco/ingleside-terraces/`) rather than folding into a future
    catch-all `west-of-twin-peaks/` directory; the rest filed under a new
    `san-francisco/oceanview-merced-ingleside/`, matching the EAS category
    name.
  - **A photo caption's street name doesn't always match EAS's.** "302 Jules
    Street" (a figure caption) is EAS's Jules *Avenue*; the parcel spans
    300–302, and is documented at 300 with the printed form kept as
    `address_as_surveyed`.
  - **Two dates for the same building, in the same document.** 1345 Ocean
    Avenue (Ingleside Presbyterian Church) is dated 1921 in the narrative
    text and 1923 in a photo caption of the same building; the assessor
    separately dates it 1909. All three readings are recorded rather than
    picking one. 215 Randolph Street is dated "circa 1878" here against the
    assessor's 1907, and 301 De Montfort Avenue (St. Emydius Catholic
    Church) is dated 1928 here against the assessor's 1939 — both are
    recorded as disagreements, not resolved.
  - **One printed address has no EAS record at all**: 5 Plymouth Avenue, a
    mixed-use building at the corner of Sagamore Street and San Jose Avenue.
    EAS carries only 1 and 3 Plymouth Avenue nearby, neither with a parcel
    number, and no record at 5. Stays undocumented.
  - **One parcel's governing APN is retired.** 501–505 Faxon Avenue (the
    Robinson Apartments) resolves in EAS to block/lot 6934009, which was
    dropped from the assessor's map in 2002; the current roll carries the
    same building, still addressed 501/505 Faxon, under 6934029 — the
    parcel `sf-parcels` returns for that point, fronting 202–206 De Montfort
    Avenue on the block's other side. Documented under 6934029 at 501 Faxon,
    per DATA-SOURCES.md's guidance to follow the assessor's own
    `property_location` when a retired APN and a spatial join disagree.
  - **One address named in the document is not in the OMI district at all.**
    A footnote locates Jose de Jesus Noe's ranch house — a building that
    predates and has nothing to do with the OMI subject area — at "today's
    55 Woodward Street," a Noe Valley/Mission-area address well outside the
    Subject Area's boundaries. Left as a candidate for whichever
    neighborhood's pass covers Woodward Street, not this one.
  - **Only architects, developers and named firms are recorded** — no
    residents, owners or occupants, per AGENTS.md's privacy rules. This
    includes the two African-American families named in the demographic
    chapters as early Merced Heights homeowners; neither is named on any
    page.
**The Market & Octavia statement is the first in this set whose best yield is a
pair of appendix tables built from city directories, and the first whose
appendix build years are not its own research.** It is 136 pages: an
introduction defining a plan area that crosses nine neighbourhoods, a chapter on
the surveys that came before, a 60-page chronological history, a property-type
chapter, a bibliography, and five appendices. There is no per-property survey
table of the usual kind — the Market & Octavia Historic Resources Survey, some
1,500 DPR 523 forms, is a separate document this statement was written to
accompany and is not in the file. Where its address-level facts are:
- **Appendix A** lists the 98 residential buildings standing in the Industrial
  Employment Study Area from the reconstruction of 1906–1909: block, lot, street
  number, street, year built.
- **Appendix D** lists all 148 industrial buildings standing in that study area,
  with block, lot, address, year built, and — the real find — the occupant of
  each in the **1936 telephone directory** and the **1953 city directory**.
  Appendices B, C and E are period subsets of D and add nothing but a few
  disagreeing years.
- **The narrative chapters** name about 90 numbered addresses with a date, an
  architect, a designation or a use: the landmarks and the previously surveyed
  buildings in chapter III, the Gilded Age builders' work, the Scandinavian and
  union halls, the post-quake institutions, and the property-type chapter, whose
  figure captions are effectively a small illustrated inventory.
- **Table 2** (p. 92) is a directory of the unions and labour agencies in the
  study area in 1953, by address — eleven more addresses, and the only place the
  Building Trades Temple's seventeen tenant locals are listed.
- **Cautions:**
  - **The appendices' build years are the Assessor's Office data the survey
    worked from in 2006–07, not dates it researched** — its own footnotes say
    so. Where they agree with the current roll they add nothing, and where they
    differ the difference is a revision by the same office, not a second
    opinion. Pages carry the appendix year as `year_built_as_surveyed` only when
    it differs from the 2025 roll, with a note saying where it came from.
  - **The report contradicts itself about which building is where.** 54 Waller
    Street is Fire Department Engine House No. 19 on p. 63 and the First Baptist
    Church in the caption on p. 111; the Swedish-American Hall is 2174 Market
    Street on p. 46 and 2168 Market Street on p. 64; the Building Trades Temple
    is at 200 Guerrero Street, at Fourteenth and Guerrero, and at Fourteenth and
    Valencia in three passages; the Recorder Building is 1935 in the text and
    1934 in a caption; Carpenters Hall is 112 Valencia Street in Table 2 and
    "the former site of Carpenter's Hall" at 100 Valencia Street in Appendix D.
    Its own appendices disagree on five buildings' years (1450 Howard, 3384 16th,
    165 Grove, 30 Otis, 1340 Mission), and the narrative disagrees with the
    appendix on four more (the Lick Baths, the Levi Strauss factory, the
    Coca-Cola warehouse and the Bekins Warehouse). All of these are on the
    pages as stated disagreements.
  - **Follow the appendix's block and lot, not its printed address.** Nine
    findings resolve only that way: 3 Pearl Street is the parcel the assessor
    addresses 1815–1819 Market, 74 Otis is 86 Otis, 145 10th is 147 10th, 40
    Lafayette is 99 South Van Ness, 1760 Mission is 1764 Mission, 1661 Market is
    1663 Market, 40 Woodward is 44 Woodward, and 67 Haight has an EAS row with
    no parcel number at all. **The printed address can also lead to the wrong
    building**: EAS carries 224 Guerrero Street with no parcel number and its
    coordinates fall in the parcel next door, a 1916 building Planning codes C;
    the Sheet Metal Workers' Hall is the parcel beside it, which the assessor
    addresses 224 Guerrero, the roll dates 1906 and Planning flags as an Article
    10 landmark.
  - **Condominium conversion has taken out most of the Mission Dolores blocks it
    inventories.** 31 of the addresses are condominium parcels AGENTS.md holds
    back — the whole Pearl Street and Elgin Park run, seven of the Clinton Park
    contributors, and the Church, Dolores and 16th Street rows the statement
    counted as post-quake reconstruction.
  - **The directory columns name proprietors as well as firms**, in the usual
    "Surname Initials trade" form. The firms are kept and the proprietors are
    not: Murasky W. F., E. Percival Wetzel, Barney H. Barnard, H. Hartzell,
    George Katz, H. L. Auger, Henry E. Lapkin, Lawrence DeLong, E. A. Bailing,
    Norbert I. Epping, John H. Shaw and E. P. Fisher are all in the source and
    on no page. The architects, builders and contractors are kept — including
    Leonard Mosias, an architect listed at 1488 Howard Street in 1953, and
    Alfred S. Gough, a contractor and builder at 10 Washburn Street in 1936.
  - **The columns also carry the compiler's own annotations**, which are not
    occupants: `nl` (not listed), cross-references to a neighbouring number
    ("#165-67", "(155-57)", "(1445= Wuelker Infra Red Ltg"), and one "yrblt
    1971". Those are dropped; "vacant" and "residence" are kept, because they
    are what the directory found.
  - **A page can already belong to another survey.** 25 of the parcels here were
    documented from the Inner Mission North statement, whose panel occupies the
    one `historic_survey` slot the page contract gives; on those, this survey's
    identity findings ride the timeline as a 2007 entry instead. Those pages
    also had their `district`/`status` keys renamed to the renderer's
    `eligible_district`/`finding`, which is what the earlier pass meant and what
    keeps `data.json` and `index.html` round-tripping.
  - **The James Lick Baths is filed under another street.** The statement, the
    assessor and Planning all address City Landmark No. 246 as 165 Tenth Street;
    EAS puts more addresses for that parcel on Grace Street, so the page the
    site already had for it is 66 Grace Street, with 165 10th Street as an
    alias.
  - **Its bibliography cites Page & Turnbull's other reports by address** — 361-65
    Brannan, 425 and 650 First, 869 Folsom, 333 and 350 Fremont, 178 and 388
    Townsend, 35 Stanford, 465 Tenth, 100 First Plaza. None is a property in the
    plan area and none was pursued.
**The Mission Dolores statement is the shortest in this set and the one whose
address-level yield is most concentrated in a single chapter.** It is 104 pages
— methodology, an 80-page history running from Ohlone ethnography to Mission
Action Plan 2020, a property-type chapter, and Part IV, "Survey Findings". It
has no appendix inventory table. What it carries at address level is:
- **Part IV's four lists** (p. 82): 31 addresses reprinted from the 1968 Junior
  League *Here Today* survey; 7 properties listed in or formally determined
  eligible for the National Register and the California Register; 8 San
  Francisco landmarks with their numbers; and the names of six existing
  historic districts in the neighbourhood.
- **The Department's own eligibility finding** (p. 89): 18 properties found
  individually eligible for the National Register and the California Register
  under Criterion C/3 (Architecture), possibly also under Criterion A/1 for
  their association with post-1906 reconstruction.
- **Three sites put forward for further landmark evaluation** (pp. 94–95):
  St. Nicholas Cathedral (2005 15th Street), St. Matthew's Church (3281 16th
  Street) and Congregation Sha'ar Zahav (290 Dolores Street), each with a
  character-defining-features paragraph drawn from a Planning DPR Primary
  Record of 2002, 2003 or 2007.
- **The property-type chapter's figure captions** (pp. 75–81), a small
  illustrated inventory of type examples — single-family residences, flats,
  Romeo flats, apartment buildings, mixed-use and single-story commercial
  buildings, schools and churches.
- **The narrative chapters**, which name the churches, the schools, the Levi
  Strauss factory, the buildings that survived 1906 west of Dolores Street, and
  the one commercial building, one apartment building, one 1942 duplex and one
  1940–41 apartment building it counts as the whole of the survey area's new
  construction in those years.
- **Cautions:**
  - **Two of the *Here Today* rows print a 15th Street number the street has
    never reached.** "3639-3641 15th Street" and "3650-3652 15th Street" sit
    between 2047 15th Street and 3656 17th Street in a list otherwise sorted by
    street then number; EAS carries no 15th Street address above 3500, and both
    numbers exist on several of the neighbourhood's other numbered streets.
    Neither was resolved, and guessing which street was meant is exactly the
    stretch AGENTS.md forbids.
  - **It contradicts itself on four buildings.** St. Matthew's Church is 3281
    16th Street in the recommendations and 3321 16th Street in a figure caption
    — two parcels a block apart, and the second is on the Mission Dolores
    block. The Holy Family Day Home is 229 Dolores Street in the survey
    findings and 299 Dolores Street in the bibliography — two parcels on the
    same block, and only 299 is the one Planning names. St. Nicholas Cathedral
    is constructed in 1904 in the recommendations and in 1919 in the chapter on
    modern development. Mission High School is a two-phased construction of
    1925 and 1927 in one passage and 1926 in another. All are on the pages as
    stated disagreements.
  - **A printed disagreement is often two numbers on one parcel.** The Second
    Church of Christ, Scientist is 651 Dolores Street in the recommendations and
    655 in a caption; the Women's Building is 3543 18th Street in the National
    Register list and 3541-3543 in the landmark list. Both pairs are single
    parcels, so neither is a finding. Resolve both numbers before writing a
    disagreement down.
  - **Four buildings are named on a street other than the one their parcel is
    addressed on.** 3703 and 3697 17th Street are 500–512 and 505–507 Church
    Street to the assessor; 3750 18th Street is 440 Dolores Street; 450 Church
    Street is 325 Sanchez Street; 3250 18th Street is 376–382 Shotwell Street;
    3689 19th Street is 601 Dolores Street. Each page is titled on the
    assessor's street and records the statement's number as
    `address_as_surveyed`.
  - **The district summaries and map are not in the adopted file.** Part IV
    defines two eligible districts — Chula-Abbey Early Residential and Alert
    Alley Early Residential — and says "a map and district summaries are
    attached". Pages 83 and 91 are blank and carry no image, and Appendix I,
    the archeological zones the property-type chapter says is attached, is
    absent too. So **the statement names no district contributors.** Planning's
    own boundary dataset (`sf-historic-districts`) does carry both districts,
    plus a third — Chula-Dolores-17th Fire Survivors and Reconstruction — that
    the adopted statement never names, and the Chula-Abbey district is now
    listed under Article 10. District membership on a page comes from that
    dataset, not from this document.
  - **Its survey materials are drafts and the state declined them.** The DPR
    forms Carey & Co. prepared were never accepted by the California Office of
    Historic Preservation, which in 2013 decided not to enter the 2010 survey
    findings in the State Historic Resources Inventory. The 2022 eligibility
    findings are the Planning Department's own, made on review of those
    materials. Every page carrying the eligibility finding says so.
  - **Condominium conversion takes out a sixth of what it names**, and the
    conversions are recent enough that the parcel EAS still carries is often the
    retired one: 154 Dolores Street, 200 Dolores Street, 718 Church Street, 93
    Cumberland Street (with 651–655 Dolores) and 48 Landers Street all resolve
    to a retired APN whose live successors are condominium units. 216 Dorland
    Street, 96 Cumberland Street, 83–85 and 38–44 Sharon Street, 574–576 Church
    Street, 3663–3665 17th Street and 229 Dolores Street are condominium units
    outright. Between them they take out five of the 18 individually eligible
    properties and the Second Church of Christ, Scientist.
  - **The 1968 rows can describe a building that is gone.** 542–546 Church
    Street is in the *Here Today* list; the assessor dates the 21-unit apartment
    building on that parcel to 1975.
  - **It is dense with people and most of them are not the building's.** The
    history chapters read census returns and voter registers block by block and
    describe households by occupation, and the Latino, LGBTQ and labour chapters
    name residents and congregants. The **firms and institutions** are kept
    (Levi Strauss, the Leonard Lumber Company, Mission Marble Works, the Dairy
    Delivery Company, the Columbia Park Boys Club, Congregation Sha'ar Zahav,
    the Mission Turn Verein), as are the **architects and builders** (John Reid,
    Jr., Charles I. Havens, Theodore Lenzen, Willis Polk, Frank T. Shea, John O.
    Loftquist, Harry S. Weiss, William H. Crim, Francis W. Reid), the patron
    Virginia Fair Vanderbilt, and the public figures the historical record
    already covers — Alexander Berkman, whose year at 569 Dolores Street the
    statement documents outright.
- **Citation label:** name the consultant(s), the report and its adoption
  date, and link the SF Planning listing page.

**The Van Ness Auto Row survey is the most densely addressed document in this
set**, and the only one so far that hands over an assessor block *and lot* for
every building it evaluates.

- **Shape of the yield.** Three parts, all of them usable:
  - **Section IV, pp. 67–70** — the evaluation tables: **112 buildings**, each
    with a printed address, a block/lot, a date built, a property type and a
    California Register status code, grouped by the code (`1S`+`3CS`, `3CS`+
    `5D3`, `3CB`, `3CD`, `3CS`, `6Z`, `7`). The status code is in the group
    heading, not the row, so a row parsed on its own loses it.
  - **Section V, p. 71** — 44 more auto-related buildings identified but not
    evaluated, with year built, architect or builder, and a terse reason.
  - **Sections II–III, pp. 11–66** — the narrative, which is where the
    architects, first tenants, garage capacities, building names and the
    demolished buildings are. Roughly 90 numbered addresses beyond the tables.
- **Cautions:**
  - **`pdftotext -layout` gets 97 of the 112 evaluation rows on a two-space
    column split.** The other 15 print the address and the block/lot separated
    by one space (`1350 Van Ness/1465 Bush 670/16, 19`); match on the block/lot
    pattern instead. Four rows of Section V run the architect column into the
    notes the same way and need transcribing by hand.
  - **A row's address is sometimes two frontages** (`730 Polk St./771 Ellis`).
    Put the second in `extra.address_note_as_recorded` and let the resolver
    compare them.
  - **The survey abbreviates the high end of a range** — `1523-25 Franklin`,
    `1243-5 Van Ness`. Spell it out before handing it to the resolver, or the
    range expands downwards.
  - **The report disagrees with itself on three addresses**, all recorded as
    conflicts rather than reconciled: the Hub Garage is 1663–1667 Market Street
    in the table and 1661–1667 in the text; the Marine View Garage is
    2020–2034 Van Ness Avenue in the table and 2020 in the text; and the
    narrative puts an electrical servicing company at 930–980 Van Ness Avenue,
    a number the avenue does not carry, where the tables have 928 and 950.
  - **Fourteen of its build dates disagree with the assessor's roll**, most of
    them because the block was redeveloped after 2010 — 1000 Van Ness Avenue
    (survey 1920–21, roll 1998), 550–590 Van Ness (1908–09 / 1999), 1335 Larkin
    (1913–14 / 2022), 500 Turk (1935 / 2022) and so on. The survey calls these
    buildings extant; it was written in 2010. Record both, adjudicate neither.
  - **Its assessor blocks are right except one:** 1725 Sacramento Street is
    printed `641/1A` and resolves to parcel 0643001A.
  - **People.** The survey is built on city directories and is thick with
    proprietors — the machinists and repairmen who opened shops, the dealers
    whose names are on the showrooms. Kept: the **firms** (Chanslor and Lyon,
    Goodyear, Firestone, Michelin, the Electric Storage Battery Company, Kahn
    and Keville, the Middleton Motor Car Company, the Pioneer and National
    Automobile Companies), the **architects and builders** (Bernard Maybeck,
    Willis Polk and Company, John Galen Howard, Weeks and Day, Ernest Coxhead,
    Sylvain Schnaittacher, the O'Brien Brothers, MacDonald and Applegarth,
    MacDonald and Kahn, George Applegarth, Frederick H. Meyer, Herman Barth,
    Cunningham and Politeo, John E. Dinwiddie, T. Paterson Ross, Arthur S.
    Bugbee, A. Lacy Worswick, William Knowles, James R. Miller, Ward and
    Blohme, John H. Powers, W. L. Schmolle, S. Heiman, Hladik and Thayer, and
    the builders Joseph Pasqualetti and William Helbing), and the two dealers
    the city's own landmarks are named for. Dropped: every individual
    proprietor of a repair shop, machine shop or specialty trade.
- **Citation label:** `William Kostura, Van Ness Auto Row Support Structures: A
  Survey of Automobile-Related Buildings along the Van Ness Avenue Corridor,
  prepared for the San Francisco Department of City Planning, adopted 2010`.

**The Carnegie branch libraries nomination is the clearest case in this set of
a document about buildings that never names their addresses.** Forty-three
pages on the seven San Francisco Carnegie branches: the grant programme, the
politics, the architecture, the architects, the property type, the defining
features, a photographic appendix and a reprint of Bertram's "Notes on the
Erection of Library Buildings". The branches are named by neighbourhood, dated
and credited — Richmond 1914 (Bliss & Faville), Mission 1915–16, Sunset 1918,
North Beach/Chinatown 1921 and Presidio 1921 (all G. Albert Lansburgh), Noe
Valley 1916 (John Reid, Jr.), Golden Gate Valley 1918 (Ernest Coxhead) — and
located only by street name in figure captions or by cross street. **Not one
street number for any of the seven.** The two numbered addresses in the whole
document are other work by one of its architects. Anyone tempted to fill the
gap from outside should read "The evidence bar" first; the branch addresses are
resolvable from the Article 10 landmark index (DataSF `97yj-54sx`), which is a
different source and should be registered as one.

- **Citation label:** `Tim Kelley, Origins of the Seven San Francisco Carnegie
  Branch Libraries 1901-1921 — context statement for the landmark nomination of
  the Carnegie branch libraries, San Francisco Planning Department, January
  2001`.

**The North Beach statement is the densest document in this set after Central
SoMa**, and the only one whose yield is split about evenly between a reprinted
inventory, three architect appendices and a narrative that dates buildings in
its figure captions.

- **Where the addresses are.** Five places, and a run that reads only the
  narrative gets about a fifth of them:
  - **Appendix B, printed pp. B1–B7** — the 1982 North Beach Survey's listed
    resources: **210 rows**, each an address, an assessor block and lot, and a
    district or individual listing. This is the structured core. Seven of the
    rows are objects in Washington Square rather than buildings.
  - **Appendix A, printed pp. A1–A33** — twelve reconstruction-era architects,
    almost all Italian or Swiss-Italian, each sketch ending in a list of
    buildings **with construction years**. About 90 dated attributions.
  - **Appendix C, printed pp. C1–C2** — a clean table of modern architects,
    address, year and property type. 39 rows.
  - **Chapter X, printed pp. 188–190** — the landmark, National Register,
    California landmark, *Here Today* (1968) and Legacy Business lists, all
    address-keyed, several with founding years for the businesses.
  - **Chapter XI, printed pp. 191–192** — the 2019 updated survey's 44
    individually eligible resources, with what each is.
  - **The narrative, pp. 6–186** — construction dates and architects in figure
    captions, the 1913 and 1949 Sanborn readings (stables, photography studios,
    club rooms, theatres), the speakeasies, and the schools and churches.
- **Cautions:**
  - **`pdftotext -layout` handles Appendix B on a two-space column split**, but
    four rows wrap: `700 Filbert St./1811-21 Powell St./700 Columbus Ave./4-12
    Via Bufano` and `651-73 Union St./1656 Powell St./585 Columbus` continue on
    the next line, and two designation cells do the same. Transcribe those four
    by hand.
  - **The survey abbreviates the high end of a range** — `530-50 Chestnut`,
    `1453-59 Grant`, `465-67 Broadway`. Spell it out before the resolver, or
    the range expands downwards.
  - **An abbreviated range usually has one number EAS never gave a parcel.**
    `545-55 Green`, `1628-30 Grant`, `1445-49 Grant`, `1859-67 Powell`, `55-59
    Osgood` and `843-845 Filbert` all read as split across two parcels, and in
    every one of them the odd number out carries no `parcel_number` in EAS and
    was placed by its coordinate point onto the lot next door. Where the numbers
    that *state* a parcel agree, the record is on one lot and the split is the
    point-placement caution firing. The assessor's `property_location` is the
    tie-breaker: it reads `1630 1628 GRANT AV`, `1449 1445 GRANT AV` and `0845
    0843 FILBERT ST` — the recorded range, on one parcel.
  - **`ptn` after a lot means the resource is a portion of that lot** — and
    since 1982 that portion has often become a lot of its own with a *different*
    number, so `ptn` names the 1982 lot, not today's parcel. `545-55 Green St.,
    0131/019 ptn` is the worked example: lot 0131019 today is 460-468 Columbus
    Avenue, an office building of 1936, while the Green Street frontage is
    0131020, of 1908. Keep the value in `assessor_lot_as_recorded`, but treat it
    as a check on the *block*, not as the parcel. A hyphenated run of lots
    (`0088/049-051`, `0115/066-069`) names no single parcel at all, and those are
    the rows whose ranges really have been split across parcels.
  - **Streets with no type in EAS.** Broadway and Via Bufano carry no
    `street_type`, which is what `scripts/seed_pages.py`'s `build_inventory`
    crashed on until this pass. `Bob Kaufman Place` is `BOB KAUFMAN ALY`,
    `Medau St.`/`Medau Place` is `MEDAU PL`, `Cadell Alley` is `CADELL PL`,
    `Nobles Alley` is `NOBLES ALY`, and `Adler Place`/`William Saroyan Place`
    is **`SAROYAN PL`**, which has exactly one address record in EAS.
  - **The document disagrees with itself constantly** — 18 conflicts recorded,
    not one of them reconciled. The pattern is a figure caption against the
    body: 555 Francisco is 1923 in Appendix A and 1928 in the caption and the
    property-type chapter; the Dante Building and the Italian Athletic Club
    have their captions apparently swapped (1927/1935 against 1935/1927, with
    the halls chapter giving 1936); St Francis of Assisi is 610 Vallejo in the
    landmark list and 620 in the property-type chapter; the Francisco school is
    2170 Powell in one chapter, 2190 in another, and 330 Francisco Street dated
    1931 in one and 1939 in the other; Saints Peter and Paul is credited to
    Fantoni in one appendix and Porporato in another.
  - **The city's analysis neighborhood splits the survey area.** North Beach as
    this document draws it runs across four of the city's own neighborhoods:
    251 of the pages this pass wrote are `north-beach`, 68 `chinatown`
    (everything around Grant, Stockton and lower Columbus, including City
    Lights, Fugazi Hall and the Bank of Italy building), 25 `russian-hill`, and
    one each in `nob-hill`, `marina` and `financial-district`. That is the
    city's boundary, not this project's judgement, and `resolve_eas.py
    --area-from-nhood` — added in this pass — is what files them that way.
  - **People.** The architect sketches are biographies: they give each man's
    own house, his family's addresses and his office. **Kept:** the design
    attributions, the contractors and building companies (DeMartini Building
    Company, Devincenzi Brothers & Company, Cuneo and Costa, C.N.P. Ahlgren,
    Kidd & Anderson), the firms a building was put up for, and the historical
    figures the city's own survey names as the reason a building is
    significant — John F. Fugazi commissioning Fugazi Hall, Abe Ruef
    commissioning the Hildebrand Stables, A. P. Giannini and Andrea Sbarboro at
    the two bank buildings, Ferlinghetti and Peter D. Martin founding City
    Lights, the artists whose studio 521–23 Francisco was built as. **Dropped:**
    every residence, including the architects' own homes, Allen Ginsberg's
    apartment at 1010 Montgomery, Lawrence Ferlinghetti's flat at 333–43
    Chestnut, the labour leader's cottage at 115 Telegraph Boulevard, and the
    home address of the man shot in 1932. Where the *only* stated significance
    of a building is that someone lived there, the finding records the
    building's eligibility and leaves the residency out.
- **Citation label:** `Michael R. Corbett, with a 2019 updated survey and
  evaluation by Katherine T. Petrin and Shayne E. Watson, North Beach, San
  Francisco Historic Context Statement, prepared for the Northeast San
  Francisco Conservancy, 31 January 2018 (revised 8 October 2020), adopted
  2022`. Page source id `north-beach-context-statement`; the PDF is a plain
  fetch from
  `https://sfplanning.s3.amazonaws.com/default/files/Preservation/hcs_north_beach.pdf`.

**The Japantown statement is the clearest case in this set of a document whose
whole yield is in its prose and its picture captions.** 112 pages, no appendix
inventory: the appendix is nine pages of Ben Pease's copyrighted Japantown maps
(PDF pages 95–103), images with no text layer and not ours to redistribute.

- **Where the addresses are.** Three places, and a run that reads only the
  history chapters gets about two-thirds of them:
  - **The narrative chapters, printed pp. 10–70** — the Western Addition's
    Victorian development, the Jewish congregations, the African American and
    Filipino communities, Nihonmachi's commercial and institutional life,
    internment, resettlement, and the A-1 and A-2 redevelopment areas. Churches,
    schools, halls, hostels, shops, hotels, associations and newspapers, each
    normally with a year.
  - **The Property Types chapter, printed pp. 71–92** — every figure caption
    names a street number *and* a style ("An Italianate style single-family
    house at 1807 Octavia Street"), and each property-type section ends by
    listing what in the survey area is designated or has been found eligible.
    This is the closest thing the document has to an inventory, and it is
    entirely in captions.
  - **The footnotes** — three addresses appear nowhere else: the Knights of
    Dimas-Alang at 1717 Sutter Street, the Japantown Art & Media Workshop's
    first home at 1852 Sutter Street, and the Hokubei Mainichi building's 2008
    demolition at 1746 Post Street.
- **It contradicts itself four times, and every one is about an address.** State
  them; do not pick. Congregation Ohabai Shalom's synagogue is 1831 Bush Street
  from the 1890s Sanborn maps and the 1895 temple is 1881 Bush Street. The
  national JACL headquarters is 1765 Sutter Street in one chapter and the site
  of 1761–65 Post Street in another. The Japanese Cultural and Community Center
  of Northern California is secured at 1840 Sutter Street, sited at 1858 Sutter
  Street and footnoted at 1852 Sutter Street. And the Fillmore Auditorium
  building is 1912 in the property-type chapter and 1910 — as Majestic Hall — in
  the history. A fifth, in a footnote, is a plain slip: the Kokoro Assisted
  Living data sheet is cited as "1881 Post Street" for the building the text
  puts at 1881 Bush Street.
- **Half the addresses it names no longer exist**, which is the substance of the
  document rather than a defect in it: the A-1 and A-2 clearances and the Geary
  Expressway took the numbers with the buildings. 1500, 1516, 1609, 1661, 1690,
  1705 and 1760 Post Street, 1617 Gough Street, 1623 Webster Street, 1698, 1717,
  1823, 1826, 1858 and 1898 Sutter Street, 1433 Divisadero Street, 1540 Ellis
  Street, 1440 and 1620 O'Farrell Street, 1534 and 1669 Geary, 1612 and 1859
  Fillmore Street and 1901, 1905 and 1919 Bush Street have no EAS record at all.
  Expect a run on this statement to leave a third of its findings unresolved and
  to be right to.
- **Two addresses appear only as households** — 1812 Bush Street and 1628 Post
  Street — and one landmark report names the family who lived at 2066 Pine
  Street. None were extracted. The privacy limits bite here as hard as anywhere
  in the register: this is a document about a community, and most of its people
  are residents.
- **A footnote number welds itself to the next caption.** `pdftotext -layout`
  renders "…reestablish the California Cleaners.<sup>136</sup> *Pine Street
  Laundry, 1946.*" as "California Cleaners.136 Pine Street Laundry, 1946", which
  scans as an address at "136 Pine Street". There is no such finding. Check any
  hit whose number is far outside the block range around it.
- **The consultants' own office is on the title page** — 724 Pine Street, Page &
  Turnbull. The advertiser trap in AGENTS.md, in its simplest form.
- **The neighborhood directory needs `--area-from-nhood`.** The site had two
  pages under `japantown/` when this run started, so proximity scattered the
  corridor into `tenderloin` and `presidio-heights` — 1975 Post Street came back
  as Presidio Heights. With the flag the city's own analysis neighborhoods
  decide: 34 pages Pacific Heights, 12 Japantown, 4 Western Addition, 1 Presidio
  Heights. Note that the Japantown analysis neighborhood is much smaller than the
  statement's study area, so most of the yield files under `pacific-heights/`.
- **Eight construction dates disagree with the assessor**, all recorded and none
  adjudicated: 2006 and 2031 Bush, 1848 and 1881 Pine, 1530 Buchanan, 1691
  Laguna, 1801 Octavia and 1940–1946 Fillmore. Five of the eight are the roll's
  1900 placeholder against a real year in the document.
- **Citation label:** `Donna Graves and Page & Turnbull, Inc., San Francisco
  Japantown Historic Context Statement, prepared for the San Francisco Planning
  Department as part of the Japantown Better Neighborhood Plan, May 2009 final
  draft; SF Planning lists it as revised 2011`. Page source id
  `japantown-context-statement`; cite the `SharedLinks.aspx` URL and fetch the
  REST content path.

**The Russian Hill statement is the smallest study area in this set and one of
the densest.** 60 pages covering the block bounded by Greenwich, Lombard, Larkin
and Polk plus three buildings at the northwest corner of Lombard and Larkin — 30
properties, 35 buildings. There is no appendix inventory table; the facts are in
the narrative, the figure captions, the footnotes, the architect biographies and
a twenty-one-page appendix of resident biographies.

- **Its Larkin Street numbers were changed, and the report prints both.** This
  is the only statement read so far that carries a renumbering inside its own
  study area, and it is the trap that would cost a run the most. The appendix
  heads each profile with the historical number and adds "site of today's
  #N" — 2507 → 2525, 2509 → 2525, 2513 → 2537-2539, 2517 → 2555, 2519 → 2555
  and 2565, 2612 Polk → 2650, 2614 Polk → 2652. **Every one of those historical
  numbers is a live address in EAS today, on a different parcel**, so the
  resolver placed six of them on a neighbour's page until they were repointed at
  the number the report itself gives. The give-away was 2509 Larkin landing on
  the parcel of the extant 1888 house next door. Read the appendix's "site of"
  parentheses before running the tool, not after.
- **The same printed number can be two buildings.** 2515 Larkin Street is the
  1888 Stick-Eastlake house that still stands *and*, before the renumbering, the
  1882 cottage on the site of today's 2543-2545. The report prints the second as
  "2515 Lombard" once and "2515 Larkin" twice.
- **The OCR is the worst in this set.** "Hil" for Hill, "Kostua" for Kostura,
  "l2l2 Lombard" for 1212, "100 I Front Street" for 1001, "1205 Filbert2061
  Hyde" for two addresses run together, "80s and Quandt" and "Dos and Quandt"
  for Boss and Quandt. A mechanical scan of the text misses several addresses
  entirely for that reason. Take a number only where it reads cleanly or a
  second mention confirms it.
- **It contradicts itself on addresses five times**, all recorded on the pages'
  `.unknowns` and none adjudicated: the 1926 house is 2505-2507 Larkin twice and
  2507 Larkin three times; the 1904-1905 flats are 1257-1259 Lombard three times
  and 1257-1261 twice, and 1261 is the separate 1876 house behind them; the 1908
  flats are 1263-1267 Lombard three times and 1263-1267 *Larkin* once, and the
  appendix numbers them 1257-1259 as well; 1208 Lombard is "1208 Larkin" in
  footnote 11; and the buyer of the 2614 Polk house is at 1233 Lombard on p. 18
  and 1271-1275 Lombard everywhere else.
- **The second seam is the architect biographies, pp. 33-38.** Seven architects,
  and their profiles name about thirty numbered buildings elsewhere in the city
  with a date apiece — Meussdorffer's Pacific Heights apartment houses, Ross's
  Islam Temple and West Side Christian Church, Righetti's hotels, Young's
  Francesca Club and Hotel Californian. That seam yielded 37 findings against 52
  from the study area itself, and it is the reason this run touched eight
  neighborhood directories rather than one. **Expect the same shape from the
  other Kostura statements.**
- **Appendix I is entirely residents** and is why the yield is not larger. It
  carries real building facts — construction dates, alterations, demolitions,
  the "site of today's" mapping — and they were taken; the biographies were not.
  Two exceptions were published under the root AGENTS.md's allowance for notable
  past residents already covered by published sources: Gelett Burgess at
  1210-1212 Lombard Street and Alice Eastwood at 1241 Lombard Street.
- **Ten resolved findings could not become pages**, and eight of them are the
  same thing: the parcel carries no row on the assessor's secured roll at all,
  which the seeder requires. They are the large apartment houses — 945 and 947
  Green, 2555 Larkin, 2500 Steiner, 2000 and 2006 Washington, 1925 Gough — and
  the report says why: several are the 1910s-1920s "cooperative" apartment
  buildings, whose parcel is not assessed as one property. The ninth and tenth
  are 2652 Polk Street, whose own parcel is retired and whose EAS point falls in
  the parcel next door.
- **Nineteen construction dates disagree with the assessor**, all recorded in
  `building.completed_conflict` and none adjudicated. Most are the roll's 1900
  placeholder against a real year in the document.
- **Citation label:** `William Kostura, The West Slope of Russian Hill: A
  Historical Context and Inventory of Historic Resources for Residential
  Buildings around Lombard and Larkin Streets, prepared for the Russian Hill
  Historic Resources Inventory Committee of the Northeast San Francisco
  Conservancy, 2006, revised 2009; SF Planning lists it as the Russian Hill
  Historic Context Statement, adopted 2009`. Page source id
  `russian-hill-context-statement`; cite the `SharedLinks.aspx` URL and fetch
  the REST content path.

**The Parkside statement is a narrative history with a list stapled to the
back, and the list is nearly the whole yield.** 58 pages, no appendix inventory
table, no APN printed anywhere, and the address-level material is concentrated
in three plain lists on a single page.

- **Page 50, "Other Structures of Interest", is the batch.** Three lists —
  *Parkside Cottages* (59 numbers, all of them 1908 Parkside Realty Company
  cottages), *Other Residential* (65 numbers from an informal 2007 walking
  survey of houses predating the stucco Sunset row house) and
  *Commercial/Civic/Religious* (11). That is 135 of the 160 findings. The other
  25 come from the six Notable Buildings write-ups (pp. 44–49), the photograph
  captions and the footnotes — and those are the *better* findings, because
  they carry architects, contractors and firm dates where the lists carry only
  a number.
- **House numbers on the numbered avenues are hyphenated to the street name.**
  "2476-20th Avenue" is 2476 20th Avenue. It is the Western Neighborhoods
  Project's house style and it appears in every caption and every narrative
  mention. A range-aware reader parses it as a range and a plain
  address-regex misses it entirely, which is why a first pass over this file
  finds eleven addresses in a document that has a hundred and sixty. *Read the
  lists; don't regex the prose.*
- **The lettered street names are historical and are never addresses.** The
  Sunset and Parkside streets were known by initial letters (T Street for
  Taraval, U for Ulloa, W for Wawona, H for Lincoln Way) until the Parkside
  Realty Company petitioned for full names, and the statement deliberately uses
  the letter name whenever it writes about a pre-1909 event. No number in this
  report needs a 1909 conversion — the district had almost nothing built before
  1905 and its numbering arrived with its names — but a reader who takes "20th
  Avenue and T Street" for an address has misread the convention, not found one.
- **The cottage list is 59 numbers and the text says 62 were built and 61 still
  stand.** The report calls the list "complete" and it is not; nothing
  reconciles the three counts. Take the 59 that are printed and leave the
  arithmetic alone.
- **The Other Residential list is the weakest material in the document** and
  says so itself: an informal walking survey, expressly "not intended as a
  comprehensive survey", with the only dating being "most" are Craftsman
  buildings put up "before 1925". Four of its numbers have no EAS record at all
  — 2532 22nd Avenue, 2454 and 2458 28th Avenue, 2499 30th Avenue — and three
  of those sit one or two off a number that does exist. *That near-miss is the
  trap: 2454 and 2458 are a digit away from a real 2456, and nothing in the
  record chooses.* Leave them unresolved.
- **Assessor years disagree with the statement constantly, and it is the 1908
  cottages that do it.** 49 of the 147 published findings carry a
  `building.completed_conflict`; 41 of those are cottages the report dates to
  1908 against roll years scattered from 1906 to 1916. The roll is dating the
  raised-and-remodelled building, the report is dating the original cottage.
  Record both; the conflict is the honest state.
- **800 Taraval Street is in the report's Parkside and the city's West of Twin
  Peaks.** Its parcel is a corner lot the assessor addresses as 2399 18th
  Avenue and files under West of Twin Peaks. `--area-from-nhood` put the page
  there, which is right: the district a consultant drew is not a neighborhood
  directory. Expect one or two of these from any statement whose study area is
  a named district rather than an analysis neighborhood.
- **Four addresses appear in this report only as somebody's home** — Parkside
  District Improvement Club officers, named with their houses in the narrative.
  Not recorded, per the root AGENTS.md. Two of those houses are also on the
  1908 cottage list and one carries a dated photograph caption; the building
  facts were taken and the residents were not.
- **A second entry from the same source on the same page is a duplicate, not a
  finding.** Four addresses appear both in a p. 50 list and in a caption or a
  Notable Buildings write-up. The caption always says more — a firm year, a
  builder, a style — so the list entry was declined rather than published
  alongside it. *Check for this before publishing any statement that carries
  both an inventory and a narrative: the generic entry lands next to the
  specific one on the same timeline, at the same date, saying less.*
- **Citation label:** `Richard Brandi and Woody LaBounty, Western
  Neighborhoods Project, San Francisco's Parkside District: 1905–1957 — A
  Historical Context Statement, produced for the Mayor's Office of Economic and
  Workforce Development, March 2008, adopted 2008`. Page source id
  `parkside-context-statement`; the S3 URL is both the citation and the fetch.

**The Oceanside statement is 28 pages, two columns, and its endnotes are the
best part of it.** A Kostura statement, so it behaves like the Inner Sunset and
Russian Hill ones: narrative history, no appendix inventory, and the addresses
scattered through the prose rather than tabulated.

- **`pdftotext -layout` interleaves the two columns line by line** and makes the
  file unreadable and un-greppable — "the Nels Hagerup Residence at 1218-24 46th
  out during the middle of the 19th century, the Avenue." Extract each page one
  column at a time (`-x 0 -W 308` then `-x 300 -W 312` on a 612pt page) before
  reading. Five of the document's addresses are invisible to a regex over the
  interleaved text, including two of its best.
- **Four of the findings come from the endnotes**, which is a higher share than
  any other statement in this set: the Stick-Eastlake cottage moved onto 1575
  48th Avenue in 1924, the two restored Harrington houses at 1231 and 1255 42nd
  Avenue, and the Oceanside Riding Club at 1370 48th Avenue that gives the
  neighbourhood's name its last recorded use. *Read the notes section of a
  Kostura statement as material, not as apparatus.*
- **Note 45 contradicts the sentence it is attached to.** The text calls the
  Lodge at 1300-1304 La Playa demolished; its own footnote says the building was
  converted to apartments, doubled in size before 1929, and still stands. Stated
  on the page's `.unknowns`, unadjudicated.
- **Half the buildings this report calls extant have numbers EAS no longer
  carries.** 1315 48th Avenue ("extant—converted to a dwelling"), 4131 Kirkham
  ("extant but heavily remodeled") and 1534 Great Highway ("extant but heavily
  remodeled") all come back with no EAS record, and in each case the neighbouring
  numbers are one or two off. Conversion and rebuilding along the Great Highway
  and the outer avenues has renumbered these lots; the report's number is the
  historical one. *Do not reach for the neighbour.*
- **The block-face rows are real facts with no address.** The fifteen Craftsman
  houses Alonzo Harrington built on the 1200 block of 42nd Avenue in 1911-13,
  Lincoln U. Grant's eighteen on the 1200 block of 37th Avenue in 1912-13, the
  row of six on the 1200 block of 41st Avenue and the row of five on the 1600
  block of the Great Highway are each given as a block, never as numbers. Kept
  as unresolved findings rather than dropped, because a later run with a Sanborn
  or a permit run could place them.
- **The survey this statement accompanies is not in this file.** Kelley &
  VerPlanck produced 511 DPR 523 A forms, 60 B forms and 5 district forms for
  the Oceanside between 2008 and 2010. None of them are here. That is a separate
  corpus and a good lead.
- **The lettered street names are historical**, exactly as in the Parkside
  statement: H Street is Lincoln Way, I is Irving, J Judah, K Kirkham, L Lawton,
  M Moraga, N Noriega, O Ortega, P Pacheco. The 1909 renaming is described in
  the document itself at p. 11.
- **Citation label:** `William Kostura, with Kelley & VerPlanck, Historic
  Context Statement of the Oceanside: A Neighborhood of the Sunset District, San
  Francisco, commissioned by SPEAK (Sunset Parkside Education and Action
  Committee), May 2007, updated March 2010; SF Planning lists it as adopted
  2012`. Page source id `oceanside-context-statement`; cite the
  `SharedLinks.aspx` URL and fetch the REST content path.


**The Transit Center District survey is 95 pages and its inventory is all in
the back.** A Kelley & VerPlanck report, so it behaves like the Bayview-Hunters
Point and India Basin ones: a narrative history, and then the addresses in
tables. Four places carry them, and the citation locator should say which.

- **The four tables, and what each gives.** Appendix Table 1, *Existing Survey
  Ratings within Study Area*, is the long one — 170 rows, each with the
  assessor's block as a row header and the lot per row, the address (often as a
  **range**: "20-8 2nd Street", "601-5 Market Street"), a building name, and up
  to six earlier ratings: the 1976 citywide survey, the Heritage *Splendid
  Survivors* letter, the Article 10 landmark number, the Article 11 category,
  whether it is listed in the National Register, and a status code. It gives no
  construction dates. The DPR 523 D district record carries two more —
  86 contributors and 33 non-contributors — with address, APN, construction
  date, property type and status codes. Appendix Table 2 lists the 24
  individually significant properties outside the district in the same shape.
  The narrative adds architects, alterations and events the tables never
  mention.
- **The rating columns can be read by vocabulary, not by position.** The column
  positions shift from page to page and `pdftotext -layout` will not hold them,
  but the six rating vocabularies barely overlap: a 1976 rating is a bare digit
  0-5, a Heritage rating a letter A-D, an Article 10 entry reads "No. 144", an
  Article 11 category is a Roman numeral, National Register listing is "Y" or
  "Y-D", and a status code looks like 3S or 6Y2. Classifying each token by which
  vocabulary it belongs to parsed 170 rows with one token left over.
- **An asterisk on a 1976 rating** means the building was not in the Planning
  Department's historic resource database when KVP checked, "most" of them, the
  report says, through demolition or lot merger. Worth carrying onto the page.
- **The survey is a redevelopment-area survey, and it says so.** It lists
  thirteen active projects that would demolish buildings it had just recorded,
  and several of those projects were built. Check the assessor's year built on
  every parcel before publishing a construction date: where the roll year is
  later than 2008, the building the survey described is not the one standing.
  Three parcels here are in that state (645 Howard Street, 652 Mission Street,
  350 Mission Street); the honest treatment is to state both years and let the
  page's `.unknowns` carry the disagreement, never to assert a demolition the
  report does not record.
- **It contradicts itself often, and mostly about addresses.** The Marine
  Electric Company Building is 195-97 Fremont Street in the narrative and
  342-56 Howard Street in the tables; the Crellin Estate Building is 585 Howard
  Street in the narrative and 583 in the table; the Aronson Building is 700
  Mission Street in the narrative and 86 3rd Street in the table; the Rialto is
  100 New Montgomery Street in the table and 116 in the narrative; the Pacific
  Telephone & Telegraph Building is 134-40 New Montgomery Street and 1925
  everywhere except one passage that says 130 and 1924. Its table also marks
  the Folger Coffee warehouse at 200 Spear Street demolished while its narrative
  calls it standing, and dates the Veronica Building to 1907 in the table and
  1947 in one narrative sentence. Every one of these is a `conflict` on the
  finding, and none of them is ours to settle.
- **Its survey area overlaps the Central SoMa survey area**, which this repo
  read in August 2026. 57 of the 123 pages this pass reached already carried the
  Central SoMa `historic_survey` panel, and a handful already carried the same
  narrative facts. The renderer holds one survey panel per page, so on those
  pages this survey's ratings could not be shown at all and only the fact the
  other survey does not carry — that the building contributes to the proposed
  New Montgomery, Mission & Second Historic District — went onto the page, as a
  dated listing entry on the timeline.
- **Hunt Street has no EAS record**, so the Hemphill Building at 15 Hunt Street
  cannot become a page. Nor can 83 Stevenson Street, 177 and 183 and 195 Fremont
  Street, 200 Spear Street, 525 and 676 Howard Street, 666 Folsom Street, 201
  Main Street or 693 Mission Street — the addresses this part of downtown lost
  to the Transbay project, Foundry Square and the towers of the 2010s.
- **Two parcels here are open questions for a person**, filed as issue #163:
  the Paramount at 680 Mission Street, whose parcel's lowest EAS number is the
  page of the parcel next door, and 678 Mission Street, which
  `scripts/render-backlog.txt` grandfathers because the renderer crashes on it.
  The survey's facts for that second one are recorded and declined, not lost.
- **Citation label:** `Kelley & VerPlanck Historical Resources Consulting,
  Transit Center District Survey, San Francisco, California — Final, prepared
  for the San Francisco Planning Department, July 22, 2008, adopted 2012`. Page
  source id `transit-center-district-survey`; the S3 URL is both the citation
  and the fetch.


## Verification log

One entry per pass, oldest first. Each says what was read, what it yielded in
counts, and what it taught — the last of those is the part that matters to the
next run.

- **Verified:** 2026-08-11 (read all 197 pages; 159 inventory rows plus ~60
  numbered-address mentions in the narrative, resolving to 190 parcels with
  EAS records and a current assessor roll row. Not resolvable, and so not
  documented: 4417–23 Third Street, rowhouses the survey records as demolished
  and whose parcels are retired; 894 Innes Avenue; 420 Pacific Street; and the
  two dozen addresses the report itself marks "no longer extant". Coverage
  note: the Central Waterfront, Market & Octavia, Japantown and other adopted
  statements on the same page are untouched.)
- **Verified:** 2026-08-12 (Central SoMa: read all 115 pages of the statement
  and all 548 of the adoption packet. 108 numbered addresses in the narrative
  chapters, 75 property records in the catalog and 1,004 rows in the survey
  results table, naming 995 distinct APNs between them. 755 of those resolve to
  a parcel with a 2025 assessor roll row and an EAS address and become a page:
  717 new pages citing this document, 3 pre-existing pages edited by hand, and
  35 new pages that cite nothing from it because its results table records
  nothing for them. A fourth pre-existing page, 845 Market Street, was edited
  by hand although its APN carries no EAS address of its own — the survey names
  it, and the page was already here. 240 APNs do not resolve: 91 are
  condominium parcels the roll gives 0 lot area and which AGENTS.md holds back,
  88 have no 2025 roll row, and 61 have no EAS address record. Of the addresses
  named only in the narrative, these clear none of that and stay undocumented:
  95 Jack London Alley, 222–226 Jessie Street, 465 Stevenson Street, 666 Folsom
  Street, 40 Hawthorne Street, 34 Mint Street, 935 Market Street, 935 Folsom
  Street, 336 Ritch Street, 83 6th Street and 790 Folsom Street have no EAS
  record at all; 128 King Street, 271 Clara Street, 365 5th Street, 434 Brannan
  Street, 633 Folsom Street and 801 Market Street resolve in EAS to a parcel
  with no current roll row; and 357 Tehama Street and 601 4th Street are
  condominium parcels. The report's own demolished addresses — 171 Howard
  Street, 693 Mission Street, 49 4th Street, 239 Minna Street, 820 Howard
  Street, 740 Harrison Street, 365 3rd Street, 727 Folsom Street and 390 4th
  Street — are named as gone and were never candidates. Coverage note: the
  statement and the packet are read in full; nothing in this document set is
  outstanding.)
- **Verified:** 2026-08-13 (Central Waterfront: read all 43 pages, which is the
  whole archived PDF — the report, its bibliography and image list, and the
  three appendices that carry content. 11 numbered San Francisco addresses
  appear in the text. Nine of them name buildings the survey recorded, and all
  nine resolve in EAS to 8 parcels, every one of them active in `acdm-wktn`
  with a 2025 roll row: 550 18th Street and 2075 Third Street are the same
  parcel, 3994044. All 8 became new pages under `san-francisco/dogpatch/`, a
  new neighborhood directory; no page here already covered any of them, so
  none were edited. The other two numbered addresses are not documented: 118
  22nd Street, which the bibliography and footnote 32 give as the DPR form's
  address for the dwelling the text calls 718 22nd Street, has no EAS record on
  22nd Street at all; and 536 Clay Street is the Hinton Printing Company's own
  address in an 1895 bibliographic citation, not a property in the survey area.
  The parcels: 3994044 (550–560 18th), 4043001 (707 18th), 4108006 (718 22nd),
  3996004 (670–674 Tennessee), 4044052 (2130 Third), 4108003R (2360–2364
  Third), 4108003D (2476–2478 Third), 4172020 (2636–2638 Third). Coverage note:
  this document is read in full and nothing in it is outstanding, but its own
  appendices are not in it — the DPR 523 forms, the NR Status Code Matrix and
  VerPlanck's Dogpatch Historic Resource Survey are separate documents and are
  untouched, as are the Market & Octavia, Japantown and other adopted
  statements on the same SF Planning page.)
- **Verified:** 2026-08-13 (Corbett Heights: read all 261 pages of the adopted
  final. 226 distinct numbered San Francisco addresses are named — 216 in the
  study area, across the five inventories and the figure captions, and 10
  elsewhere in the city as architects' other work or Pioche's own house. 200 of
  the 216 resolve in EAS, to 193 parcels. 174 pages now cite the document: 80
  new and 94 edited, across `castro` (101), `corbett-heights` (63),
  `nob-hill` (4, a new neighborhood directory with a hand-written hub),
  `mission` (2) and one each in `chinatown`, `south-of-market`, `tenderloin`
  and `western-addition`. Five of the edited pages are hand-authored HTML and
  were edited by hand, as was the Danvers Street hub, which carries
  hand-written sections the hub generator refuses to overwrite.
  Not documented, and why: **29 are condominium parcels** the roll gives 0 lot
  area, which AGENTS.md holds back — 4343 and 4378–4380 Seventeenth; 4515,
  4547, 4569, 4627, 4655, 4658, 4666 and 4683 Eighteenth; 4594 Nineteenth; 18,
  58, 246 and 248 Caselli; 4 Corwin; 64, 180 and 272 Douglass; 54 Lower
  Terrace; 2805 and 3393 Market; 68 Saturn; 38 Yukon; 1366 Clayton; 218 and 238
  Corbett; 25 Hattie; and 32 Eagle. Three of those (58 Caselli, 238 Corbett, 25
  Hattie) are buildings the adopted 1968 survey listed, so the condominium rule
  is holding back real historic resources here, not marginal ones. **Thirteen
  are named at a number EAS has never had**: 100 Ord, 228 Douglass, 360
  Caselli, 4513 Eighteenth, 201 Corbett, 111–123 Douglass (the California
  Brewing Company site), 50 Yukon, 98 Levant, 98 Carson, 24 Mars, 4695
  Eighteenth, 4228 Nineteenth and 1 Eagle. **Five more have an EAS row with no
  parcel number**: 4502 Eighteenth, 29 Ord, 4547 and 4569 Eighteenth, and 67
  Hattie. The first two are documented on the parcel their printed range or
  1976 lot lands on (4500 Eighteenth and 31 Ord); the last three are not.
  Three addresses printed as the report's own are documented under the number
  EAS gives the parcel: 4365–4369 Seventeenth on the 166 Corbett Avenue page,
  3064 Market on 3066 Market, and 4676–4680 Eighteenth on 4678. The addresses
  the report itself
  gives as historical — 2 and 103 and 427 Falcon Street, 3084 Merritt Street,
  1018 Seventeenth Street (where 126–128 Ord stood before 1894) and 110 Ord —
  are on streets the Market Street extension erased or numbers that no longer
  exist, and were never candidates; 126 Museum Way, demolished about 2008, is
  documented as site history on the parcel that carries the address today.
  Seven rows of the 1860–1906 research table give a cross-street rather than a
  number ("Hattie between Seventeenth and Eighteenth", "Ord and Seventeenth")
  and stay unresolved. Coverage note: this document is read in full and nothing
  in it is outstanding. The Corbett Heights Neighbors newsletter archive it
  draws on is a separate source (`corbett-heights-neighbors`, pages 2–5 still
  untouched), and the Eureka Valley, Duboce Triangle, Market & Octavia,
  Japantown and other adopted statements on the same SF Planning page are
  untouched.)
- **Verified:** 2026-08-13 (Dogpatch: read all 35 pages, which is the whole
  file — 28 of them carry text and the last six are figures. 90 distinct
  numbered San Francisco addresses appear in them. 58 resolve in EAS to 60
  parcels with a 2025 assessor roll row, and all 60 are now pages: 60 new ones
  under `san-francisco/dogpatch/` (37 Tennessee Street, 12 22nd Street, 9
  Minnesota Street, 1 Third Street) and `san-francisco/potrero-hill/`, a new
  neighborhood directory with a hand-written hub holding 1202–1204 19th Street.
  Three pages that already existed were edited by hand instead: 707 18th Street
  and 718 22nd Street, both from the Central Waterfront pass, and 132–142
  Second Street in `east-cut`, which the survey names as 140–42 2nd Street for
  a second Pelton skyscraper. 63 pages cite the document. 23 of them record a
  date the survey and the roll disagree on. Not documented, and why:
  **fourteen are condominium parcels** the roll gives 0 lot area, which
  AGENTS.md holds back — 900 and 920–22 Minnesota; 724–26, 900, 901, 950, 993,
  1011, 1016–18, 1108–10, 1159–63 and 1167–69 Tennessee; and 812–14 22nd. Two
  of those are buildings the survey treats as type examples (920–22 Minnesota,
  half of a named pair, and 1108–10 Tennessee, one of the four Welch flats), so
  the condominium rule is holding back contributors here, not intrusions.
  **Fifteen are named at a number EAS has never had**: 627, 699, 750, 800–50,
  850, 1005, 1007, 1009, 1185 and 1191 Tennessee; 118, 700 and 807 22nd; 2310
  Third; and 1532 Kentucky Street, whose street was renamed and renumbered as
  Third Street. Three of those are on parcels documented under another number —
  700 22nd on the 702 22nd Street page, 2310 Third on the 2300 Third Street
  page, and 807 22nd behind 1100 Tennessee — and are recorded there as the
  survey printed them. **One has an EAS row but no active parcel**: 1095–99
  Tennessee. **One is a strong match at a number the city does not carry**: the
  Kentucky Hotel of 1902, printed "2500-03 3rd Street", which is a range across
  both sides of the street; EAS has 2501 (the Muni yard) and 2502–2504 (an
  18-unit multi-family building of 1900 on the corner of 22nd). Neither number
  is the one printed, so it stays undocumented. Coverage note: this document is
  read in full and nothing in it is outstanding, but Section 4, its own survey
  forms, is not in the file — the DPR 523 forms are a separate document and are
  untouched, as are the Eureka Valley, Duboce Triangle, Market & Octavia,
  Japantown and other adopted statements on the same SF Planning page.)
- **Verified:** 2026-08-13 (Duboce Triangle: read all 181 pages of the adopted
  draft — the ten chronological chapters, the property-type and
  architectural-style chapters, the recommendations and the bibliography. **186
  distinct numbered San Francisco addresses are named**, counting a printed
  range by its low number: most of them in Duboce Triangle itself, the rest as
  the Scandinavian and Finnish institutions of the wider Upper Market area, as
  citywide examples of a style, or as the site of the Ham and Eggs Fire. **172
  have an EAS row and 171 of those carry a parcel number.** 138 pages now cite
  the document: **24 new and 114 edited**, across `castro` (130), `mission` (5),
  and one each in `hayes-valley`, `financial-district` and `inner-sunset` (a new
  neighborhood directory with a hand-written hub, for the Henry Doelger Building
  at 320 Judah Street). Of the 38 entries in the statement's landmark-candidate
  list, **29 are documented and 9 are held back as condominium parcels**.
  Not documented, and why: **28 are condominium parcels** the roll classes
  `Condominium`, which AGENTS.md holds back — 951–955 Fourteenth; 2150,
  2179–2183, 2229–2231, 2253–2255 and 2263–2265 Fifteenth; 45–49 and
  56–58 Beaver; 45–49 Belcher; 74–76, 84–86, 164–166, 210–212,
  214–216, 222–224 and 301–303 Castro; 200 Dolores; 19–23 Henry; 47,
  201–203, 207–209, 229–231, 233, 247–251 and 255–259 Noe; and 43–45,
  71 and 151–153 Sanchez. Nine of those are candidates on the statement's own
  landmark list, so the condominium rule is holding back the buildings it most
  wanted protected. Ten of the 28 converted after the roll year their old APN
  last appears in, so EAS still carries an APN with no 2025 roll row while the
  live successor is a condominium; 229–231 Noe has an EAS row with no parcel
  number at all. **Fourteen are named at a number EAS has never had**: 754
  Fourteenth, 2272 Sixteenth, 3276 Sixteenth, 3555 Sixteenth, 3744 Seventeenth,
  4032 Seventeenth, 2168 Eighteenth, 32 Beaver, 431 Duboce, 211 Noe, 250 Noe,
  479 Market, 725 O'Farrell and 320 Sansome. Four of those are the statement's
  own misprints and are documented under the number the city carries — 754
  Fourteenth on the 80 Belcher Street page, 2272 Sixteenth and 2168 Eighteenth
  on 2272–2276 and 2168 Fifteenth, and 211 Noe on 221 Noe — with the printed
  form recorded as `address_as_surveyed`. Six are buildings the statement itself
  records as demolished (the Swedish Athletic Club, the Swedish Home for Girls,
  Finnila's Finnish Baths, the Norwegian Singing Society hall, the villa at 32
  Beaver Street, and the apartment building at 250–258 Noe Street that burned
  in 1963 and is now the Noe-Beaver Mini Park). 3555 Sixteenth is the old
  Eureka Valley branch library, which the statement itself renumbers to 1 José
  Sarria Court; 479 Market is Cliff's Variety, which is on Castro Street, not
  Market; and 725 O'Farrell and 320 Sansome are a 1905 florist's shop and an
  1859 society's rooms, both long gone. Two addresses stand on parcels the roll
  has renumbered since EAS was last refreshed and are documented on the live
  APN: 300 Castro Street (2622002, not the 2622088 EAS gives) and 2168–2174
  Market Street (3542062, not 3542017). Coverage note: this document is read in
  full and nothing in it is outstanding, but the reconnaissance survey adopted
  alongside it — the GIS field application and the spreadsheet of all 552
  properties, with their estimated dates, methods of construction, uses, styles
  and alterations — is not in the file and is untouched, as are the Eureka
  Valley, Market & Octavia, Japantown and other adopted statements on the same
  SF Planning page.)
- **Verified:** 2026-08-14 (Eureka Valley: read all 260 pages of the adopted
  final — the seven chronological themes, the property-type and
  architectural-style chapters, the evaluation frameworks, the recommendations
  and the bibliography. **325 distinct numbered San Francisco addresses are
  named**, counting a printed range by each of its numbers: most of them in the
  study area between 16th and 21st streets, the rest as landmarks "related to
  Eureka Valley" outside it, as the earlier homes and first houses of its
  builders, or as citywide style examples. **305 of them resolve in EAS to a
  parcel; the 302 that also carry a usable fact collapse onto 297 parcels, 262
  of which may be documented.** 263 pages now cite the
  document: **36 new and 227 edited**, across `castro` (258) and one each in
  `mission`, `haight-ashbury`, `tenderloin`, `glen-park` and `noe-valley` — the
  last two new neighbourhood directories with hand-written hubs. Sixteen of the
  edited pages carry hand-authored HTML and had the survey panel and source
  line inserted by hand rather than regenerated.
  Not documented, and why: **15 are condominium parcels** the roll classes
  Condominium, which AGENTS.md holds back — and the conversions have taken most
  of one Fernando Nelson row: 4138, 4140, 4141 and 4143 20th Street, including
  the towered Queen Anne at 4138 that is the most elaborate house he built on
  that block. The rest are 39 Hartford Street; 571 and 573 Liberty Street, two
  of John Anderson's five; 129 Hancock Street; 294 Collingwood Street; 19 Eureka
  Street; 3918 and 3920 20th Street; 189 Collingwood Street; 356 Collingwood
  Street; and 336 Cumberland Street.
  **Twenty more have an EAS parcel with no 2025 roll row**, so the seeder will
  not make a page for them: 4000, 4036 and 4052 18th Street (three of Nelson's);
  40 Hartford Street; 750 and 757 Castro Street (one of them Hinkel's); 158 and
  150 and 201 Eureka Street — 150 being the Bethel/Central Baptist church that
  became the Metropolitan Community Church; 3936 and 3942 19th Street; 3525 16th
  Street; 482 Liberty Street; 3943 17th Street; 179 Douglass Street; 617 and 627
  Castro Street; 72 Collingwood Street, Mayor P. H. McCarthy's house; and 300
  Cumberland Street, the pair of 1906 earthquake cottages the statement calls the
  study area's one resource directly associated with the earthquake and fire.
  One of those twenty is documented anyway: EAS gives the Swedish-American Hall
  the retired APN 3542017, but the building already has a page under its current
  parcel 3542062, and that page carries the citation — which is why 263 pages
  cite the document against 262 documentable parcels.
  **Fourteen are named at a number EAS has never carried**: 406 and 709 Castro
  Street, 4062 and 4103–4105 18th Street, 4032 17th Street, 17 and 76
  Collingwood Street, 4448–4450 Douglass Street, 450 Sanchez Street, 1074
  Guerrero Street, and two of the report's own misprints — 2 Hartford Street,
  where the recommendations mean 20, and 4144–4150 Collingwood Street, where
  they mean 18th. **Six more have an EAS row with no parcel number**: 511 Castro
  Street, 3897 and 3988 18th Street, 4400 19th Street, and 65 and 234
  Collingwood Street. 1274 Market
  Street resolves, but the only thing the statement says about it — that it is
  the Swedish-American Hall — is a misprint for 2168–2174 Market Street, so it
  gets no page and the disagreement is recorded on the hall's own. The buildings
  the statement itself calls no longer extant — 406, 470–476 and 511 Castro
  Street, 17 and 76 Collingwood Street, the Douglass and Everett and McCreery
  buildings, the Trinity Methodist Episcopal church and the Twin Peaks Lodge Hall
  — were never candidates. Coverage note: this document is read in full and
  nothing in it is outstanding. The 2015 Citywide Historic Context Statement for
  LGBTQ History in San Francisco, which it quotes at length and defers to, is a
  separate document and is untouched, as are the Market & Octavia, Japantown and
  other adopted statements on the same SF Planning page.)
- **Verified:** 2026-08-14 (Glen Park: read all 118 pages, which is the whole
  archived PDF — the introduction and findings, the methodology, the regulatory
  framework, the cultural context, the property-type overview, the seven
  property evaluations, the district analysis, the impacts and mitigation
  chapters, the bibliography, and the four appendices, of which A-1 and A-2 are
  maps, B is the project description and C is a cover sheet with no DPR forms
  behind it. **58 distinct numbered San Francisco addresses are named**,
  counting a printed range by each of its numbers: 17 on Chenery Street, 14 on
  Diamond, 10 on Brompton, 5 on Bosworth, 4 on Wilder, 2 each on Joost and
  Lippard, and one each on Arlington, Congo, Monterey and Mission. **52 have an
  EAS row and 50 of those carry a parcel number** — the two that do not are 2856
  and 2901 Diamond Street. 44 pages now cite the document:
  **44 new and 0 edited**, all under `san-francisco/glen-park/`, across ten new
  street directories — chenery-street (16), brompton-avenue (10), diamond-street
  (5), bosworth-street (4), wilder-street (3), joost-avenue (2), and one each on
  arlington-street, congo-street, lippard-avenue and monterey-boulevard. Seven
  of the eight parcels the evaluation surveyed intensively are documented; the
  eighth, 23–25 Brompton Avenue, is documented as two pages because its Lot 030
  has since been split into Lots 033 and 034. Not documented, and why: **45
  Wilder Street** is now four condominium APNs on mapblklot 6745101, which
  AGENTS.md holds back. **The Glen Park BART power station** (Block 6745, Lot
  066) is an active parcel with a 2025 roll row, but the report gives it no
  street number and EAS carries no address for the parcel at all, so one of the
  eight evaluated properties has no page. **Six are named at a number EAS has
  never had**: 107 and 702 Chenery Street, 612 Bosworth Street, 2440 and 2909
  Diamond Street, and 2862 Diamond Street. 107 Chenery is the report's own
  caption misprint for 701 and is recorded on that page; 2440 Diamond is a
  firehouse the report calls no longer extant; 2909 Diamond is where the Glen
  Park Branch Library stood before BART, recorded on the station's page; 702
  Chenery is the Enterprise Steam Beer Saloon of 1898–1920 and 612 Bosworth the
  Mission Building Company's own address, neither of which the city carries;
  2862 Diamond is the assessor's high number for a parcel EAS tops out at 2860.
  **Two more resolve but are not documented**: 180 Lippard Avenue, where the
  only thing the report says is which named individual lived there, which the
  privacy rules withhold; and 1650 Mission Street, the Planning Department's own
  office in five footnotes, not a property in the survey. The Glen Park BART
  station is documented on the APN the report itself gives (6755026) — EAS
  carries 2901 Diamond Street with no parcel number, and the address point falls
  inside that parcel. Coverage note: this document is read in full and nothing
  in it is outstanding, but the DPR 523A and 523B forms its Appendix C promises
  are not in it, and the Planning Department's companion survey, "Glen Park Area
  Plan HRE: West of Lippard and NCT" (SFPD 2010) — which holds the DPR forms for
  the five buildings it found California Register-eligible and for 24 more — is
  a separate document and is untouched, as are the Market & Octavia, Japantown
  and other adopted statements on the same SF Planning page.)
- **Verified:** 2026-08-14 (India Basin: read all 120 pages, which is the whole
  archived PDF — the seven chronological context chapters, the property-type
  and recommendations chapters, the bibliography, Appendix A (three scanned
  Sanborn sheets of 1899–1900, 1913–15 and 1948–50, pp. 56–58, images with no
  text) and Appendix B, which holds 38 DPR 523A Primary Records, 13 523B
  Building, Structure and Object Records and one nine-page 523D District
  Record. **50 distinct numbered San Francisco addresses are named**, counting a
  printed range by the number the survey files it under: 39 on Innes Avenue, 3
  on Middle Point Road, 2 each on Earl and Hawes streets, and one each on
  Hunters Point Boulevard, Galvez Avenue, Jerrold Avenue and Revere Avenue. The
  ten owner and consultant addresses the Primary Records print — including 4000
  Third Street and 671 Illinois Street — are withheld under the privacy rules
  and are not counted. **41 of the 50 resolve to a parcel with an EAS address
  and a 2025 assessor roll row.** 43 pages now cite the document: **40 new and 3
  edited**, all under `san-francisco/bayview-hunters-point/` — innes-avenue
  (32), hudson-avenue (3), middle-point-road (3), hawes-street (2), and one each
  on earl-street, griffith-street and hunters-point-boulevard, six of those
  seven being new street directories. The three edited pages — 881, 900 and 911
  Innes Avenue, from the Area B pass — carry hand-authored HTML and had the
  survey panel, the new spec rows and the source line inserted by hand rather
  than regenerated. Of the eight parcels in the boat-yard district the survey
  proposed, four are documented (4629A/010 as 900 Hudson Avenue, 4630/002 as
  890 Hudson, 4646/001 as 901 Hudson, and 4646/002 as 404 Griffith Street, the
  parcel the district record addresses as 900A Innes Avenue). Not documented,
  and why: **six parcels are active, addressed and off the current roll** —
  their APNs last appear on the 2023 roll, so the seeder makes no page — namely
  702 Earl Street (the Heerdt boat yard of 1935, one of the four properties the
  survey found individually eligible), 840 Innes Avenue (the Hunters Point
  Restaurant), and the four remaining district parcels 4630/006, 4645/010,
  4645/010A and 4645/011, which hold the Allemand Brothers yard and its office
  of about 1930. **Five are named at a number EAS has never had**: 850 Innes
  Avenue (Pop Anderson's own house, and the address the 1976-survey list and
  the condition chapter give the Hunters Point Restaurant), 892 Innes (his
  boat-building shop and planing mill on the 1913–15 Sanborn, gone), 901 Innes
  (the Hunters Point School of 1911–1930, removed), 615 Galvez Avenue and 690
  Jerrold Avenue (the Hunters Point Co-operative Society's store of 1939 and
  the house it started in). Three more of the report's own numbers are
  documented under the number the city carries: 5 Earl Street and 700 Innes
  Avenue on the 740 Earl Street page, and 904½ Innes Avenue on 904 Innes, each
  with the printed form recorded as `address_as_surveyed`; 700A Innes Avenue is
  the report's own earlier number for 702 Earl Street, which has no page. 1109
  Revere Avenue is a grocer's shop named only as an owner's business and is
  withheld under the privacy rules. Two vacant lots the survey folds into the
  930 Innes Avenue record, 934 and 936 Innes, are documented within that page
  rather than as pages of their own, and so is 4646/005A, which carries no
  street address. Coverage note: this document is read in full and nothing in it
  is outstanding. The Market & Octavia, Japantown and other adopted statements
  on the same SF Planning page are untouched.)
- **Verified:** 2026-08-15 (Inner Mission North: read all 62 pages, the whole
  file — the introduction and methodology, the historical synthesis, the
  property-type overview, the goals and priorities chapter, the survey
  findings (five district/area contributor lists, the individual-significance
  list and the designated-resources list), the recommendations and the
  bibliography. **453 distinct numbered San Francisco addresses are named**,
  counting a printed range by its low number. **449 resolve to a parcel with
  an EAS address record.** Of those, **392 resolve to a parcel with a 2025
  assessor roll row that is not a condominium unit**, and 391 pages now cite
  the document (two of the addresses, 3165-3197 16th Street and 417-427
  Guerrero Street, name the same parcel): **84 new pages and 307 edited**, all
  under `san-francisco/mission/` except six parcels a neighboring Castro pass
  already gave pages under `san-francisco/castro/` (15th Street 1906 and 1912,
  16th Street 3310, 3314 and 3336, and Dolores Street 114). Not documented, and why: **57 resolve
  to a parcel that is not on the current roll**, of which 56 are condominium
  or commercial-condo unit parcels — 54 the roll classes `Condominium` (one of
  them, 330 South Van Ness Avenue, only after following its own retired,
  since-converted APN forward) and two `Commercial Store Condo`, at 1875
  Mission Street and 2931 16th Street — which AGENTS.md holds back, and one,
  1886-1898 Mission Street, is the Louis Roesch Company plant the
  report itself calls "to be demolished 2006," now off the secured roll
  entirely with no successor parcel of any kind. **Four have no EAS address
  record at all**: 565 14th Street, 390-398 Guerrero Street, 72-74 Ramona
  Avenue, and 1538 Valencia Street — the last is where CHL plaque No. 791
  places the 1881 site of the Bancroft Library, moved to Berkeley in 1906.
  Coverage note: this document is read in full and nothing in it is
  outstanding. The Market & Octavia, Japantown and other adopted statements on
  the same SF Planning page are untouched.)
- **Verified:** 2026-08-15 (Inner Sunset: read all 238 pages, the whole file —
  the general introduction, the rural years (1850s–1887), the suburban years
  (1887–1902) including its "surviving nineteenth century houses" catalog and
  1900 census analysis, the urban years (1903–1960s) including Windsor
  Terrace, the N-Judah and its 1910 census analysis, the architecture and
  building types chapter (builders and architects, residential styles,
  commercial buildings, apartment buildings, churches, institutional and
  civic buildings, and buildings of the 1950s–60s), and the bibliography.
  **349 distinct numbered addresses are named**, counting a printed range by
  its low number except where the range itself spans two live parcels (see
  "Cautions" above). **329 resolve to a parcel with an EAS address record**,
  to 314 distinct parcels. Of those, **302 resolve to a parcel with a 2025
  assessor roll row that is not a condominium unit**, and 302 pages now cite
  the document: **301 new pages and 1 edited** (320 Judah Street, already
  documented from the 2022 Duboce Triangle statement), all under
  `san-francisco/inner-sunset/`. Not documented, and why: **12 resolve to a
  parcel not on the current roll or not a building** — 3 are condominium
  units (1209 and 1211 Second Avenue, 5 Hugo Street), and 9 have no 2025
  secured-roll row at all (504 Hugo Street; 1285 and 1307 Fifth Avenue; 1285
  Fourth Avenue; 1314 Sixteenth Avenue; 1455 Irving Street, the Kleinclaus
  service station the statement itself says was "demolished in 2018"; 1491
  Eighteenth Avenue; 1738 Ninth Avenue; and 430 Judah Street). **20 named
  addresses have no EAS record at all**: most are early Ninth Avenue and
  Irving Street commercial buildings the statement itself says were
  demolished, moved, or completely rebuilt (620, 811, 826 and 830 Irving
  Street; 1261, 1301 Ninth Avenue; 1332 Irving Street; 1350 Tenth Avenue; 235
  Kirkham Street; 1305 Seventh Avenue, an 1889 house the statement says was
  moved to 627-633 Irving Street in 1913; and 1343 Seventh Avenue, another
  19th-century house; 1328 Fourteenth Avenue), five are outside the Inner Sunset
  altogether and cited only as an architect's or builder's other work (1151
  Post Street; 21-23 Beulah Street; 225 Moncada Way; 1719 and 1739 Waller
  Street), one is a pre-addressing street name the statement doesn't resolve
  itself (545 K Street), and the statement never gives a street number for
  either the second St. Anne of the Sunset church building or the surviving
  1908–1909 Laguna Honda School building (now Independence High School) — both
  stay unresolved rather than guessed. Coverage note: this document is read
  in full and nothing in it is outstanding. The Inner Sunset Park Neighbors'
  companion "Evaluative Framework" and the related Sunset District Residential
  Builders statement, both linked from the same SF Planning project page, are
  untouched.)
- **Verified:** 2026-08-15 (OMI: read all 64 pages, the whole file — the
  introduction and methodology, the historical synthesis for each of the
  four sub-neighborhoods (natural history through the 1970s), the property
  types addendum with its per-neighborhood building-type captions, the
  resource-registration significance findings, the goals and priorities, and
  the bibliography. There is no appendix inventory table. **40 distinct
  numbered addresses are named**, counting a printed range by its low number;
  one of them (55 Woodward Street, the site of Jose de Jesus Noe's ranch
  house) is outside the Subject Area entirely and was not pursued. Of the
  **39 addresses within the OMI district, 38 resolve to a parcel with an EAS
  address record and a current, non-condominium assessor roll row** (one,
  501–505 Faxon Avenue, only after following its retired APN 6934009 forward
  to its current 6934029). All 38 are new pages: 23 under a new
  `san-francisco/oceanview-merced-ingleside/` (Ocean View, Ingleside and
  Merced Heights streets, matching the EAS analysis-neighborhood name), 13
  under a new `san-francisco/ingleside-terraces/` (the Ingleside Terraces
  streets, which resolve to the separate `West of Twin Peaks` EAS category —
  split out on the Corbett Heights/Castro precedent rather than filed under a
  future catch-all), and 2 under the existing `san-francisco/outer-mission/`
  (2301 San Jose Avenue and 1 Sergeant John V Young Street). Not documented,
  and why: **5 Plymouth Avenue has no EAS address record at all** — EAS
  carries only 1 and 3 Plymouth Avenue at that corner, neither with a parcel
  number. Three genuine date conflicts between this document and the
  assessor roll are recorded on their pages rather than resolved: 1345 Ocean
  Avenue (1921 in the narrative, 1923 in a caption, 1909 on the roll), 215
  Randolph Street (circa 1878 here, 1907 on the roll), and 301 De Montfort
  Avenue (1928 here, 1939 on the roll). Coverage note: this document is read
  in full and nothing in it is outstanding. The Market & Octavia, Japantown
  and other adopted statements on the same SF Planning page are untouched.)
- **Verified:** 2026-08-16 (Market & Octavia: read all 136 pages, the whole file
  — the introduction and definition of the plan area, the methods and
  previous-surveys chapters, the eight chronological context chapters, the
  Industrial Employment context with its union directory, the property-type
  chapter, the bibliography, and Appendices A through E. **322 distinct numbered
  San Francisco addresses are named**, counting a printed range by its low
  number: 98 in Appendix A, 148 in Appendix D (of which none overlap Appendix A),
  and about 90 in the narrative chapters and Table 2. **264 of them resolve to a
  parcel that may be documented**, collapsing onto 260 parcels — nine of those 264
  only by following the appendix's own block and lot rather than its printed
  address, and one by rejecting the parcel the printed address's coordinates fall
  in (224 Guerrero Street; see "Cautions" above). 260 pages now cite the
  document: **158 new and 102 edited**, across `mission` (139),
  `south-of-market` (46), `castro` (38), `hayes-valley` (32), `tenderloin` (3),
  `haight-ashbury` (2) and `western-addition` (1); no new neighbourhood or street
  directory was needed. One further page was seeded and cites nothing from the
  document — 1659 Market Street, whose parcel the appendix's printed address
  pointed at before the block and lot moved the finding next door to 1663.
  Not documented, and why: **31 are condominium parcels** the roll classes
  Condominium, which AGENTS.md holds back — 54, 61 and 65 Pearl Street; 73 and 84
  Elgin Park; 176, 251, 255, 267 and 281 Clinton Park; 19 Rosemont Place; 440
  14th Street; 1918 and 1983 15th Street; 3330 and 3394 16th Street; 321 and 349
  Church Street; 25 and 272 Dolores Street; 256 and 260 Guerrero Street; 14, 30
  and 42 Otis Street; 74 and 90 12th Street; 375 Grove Street; 555 Fulton Street;
  41 Van Ness Avenue; and 1500 Mission Street, the Coca-Cola bottling warehouse
  that Splendid Survivors recorded. **28 are named at a number EAS has never
  carried**: 1 Van Ness Avenue; 100 Page Street; 100 South Van Ness Avenue; 101,
  106, 108, 112, 154 and 227 Valencia Street; 1022 and 751 Golden Gate Avenue;
  125 12th Street; 1360 and 1582 Market Street; 1400 Howard Street; 155 10th
  Street; 155 Grove Street; 1536 Mission Street; 1841 and 2091 15th Street; 1927
  Market Street; 208 Dolores Street; 2698 16th Street; 271 Hayes Street; 30 Otis
  Street; 316 14th Street; 54 Waller Street; and 69 9th Street. Eleven of those
  are the union halls and labour offices of Table 2, on the Valencia Street and
  Tenth Street block faces the Central Freeway took; the rest are buildings the
  report itself calls no longer extant, or numbers the city has since retired.
  **One is a second appendix row on a parcel that cannot have a page**: the
  appendix lists 134 10th Street twice, once per parcel, and block 3510 lot 007
  has an active parcel and a 2025 roll row but no EAS address at all. Coverage
  note: this document is read in full and nothing in it is outstanding. The
  Market & Octavia Historic Resources Survey it was written to accompany — the
  DPR 523 forms for some 1,500 properties built before 1961 — is a separate
  document and is untouched, as are the Japantown and other adopted statements
  on the same SF Planning page.)
- **Verified:** 2026-08-17 (Mission Dolores: read all 104 pages, the whole file
  — the introduction and project history, the field, research and evaluation
  methodology, the eleven chronological context chapters from Ohlone
  ethnography to Mission Action Plan 2020, the property-type chapter, Part IV's
  survey findings, the evaluative framework, the individually eligible
  properties, the eligible districts, the recommendations and the bibliography.
  **83 distinct printed address forms are named**, counting a printed range by
  its low number, resolving to **74 distinct parcels**. **66 of the forms
  resolve to a parcel that may be documented**, collapsing onto **62 parcels
  and 62 pages: 10 new and 52 edited**, 44 under `san-francisco/castro/` and 18
  under `san-francisco/mission/`; no new neighbourhood or street directory was
  needed. Five of the 66 resolve only by following the assessor's own address
  rather than the statement's printed one — 3703 and 3697 17th Street, 3750
  18th Street, 450 Church Street and 3250 18th Street, which the roll numbers on
  Church, Dolores, Sanchez and Shotwell. Not documented, and why: **14 forms, on
  12 parcels, are condominium units or parcels whose live successors are**,
  which AGENTS.md holds back — 154 Dolores Street, 200 Dolores Street, 718
  Church Street, 93 Cumberland Street (with 651 and 655 Dolores Street) and 48
  Landers Street resolve to a retired APN whose successors are condominium
  units, and 96 Cumberland Street, 216 Dorland Street, 229 Dolores Street,
  38–44 and 83–85 Sharon Street, 574–576 Church Street and 3663–3665 17th
  Street are condominium units outright; between them they take out five of the
  18 individually eligible properties and the Second Church of Christ,
  Scientist. **3 name a number EAS has never carried**: 208 Dolores Street,
  cited only in the bibliography, and the two *Here Today* rows printed as
  3639-3641 and 3650-3652 15th Street, a street that stops well below 3500 —
  both numbers exist on several of the neighbourhood's other numbered streets
  and the statement gives nothing to choose between them. Coverage note: this
  document is read in full and nothing in it is outstanding. Its own missing
  parts are separate documents: the district summaries and map Part IV says are
  attached, Appendix I's archeological zones, and Carey & Co.'s *Revised
  Mission Dolores Neighborhood Survey* of 2009 with the DPR 523A/523B forms
  behind it. The Japantown and other adopted statements on the same SF Planning
  page are untouched.)
- **Verified:** 2026-08-21 (Market & Octavia, publish loop closed — bookkeeping
  only, no page edited. PR #114 put the batch on the pages but left
  `findings/sf-context-statements/market-octavia-hcs.json` at `stage: resolved`
  with no `publish` block on any of its 496 entries, so the next publisher would
  have re-published all 425 resolved findings onto the 260 pages that already
  carry them. Every resolved finding was re-checked against its page's
  `data.json` before being marked, and **425 of 425 are on the page**: 213 match
  their record text outright, 77 are carried by the Appendix A line in
  `historic_survey` and 135 by the Appendix D line — the reworded ones are the
  publisher re-expressing the fact, which is the contract, not a miss. The file
  is now `stage: published`: **425 `published`** against PR #114 and **71
  `declined`** — 39 findings on the condominium parcels listed above, 31 at
  numbers EAS has never carried, and 1 the second 134 10th Street appendix row
  on block 3510 lot 007. Nothing in the document is outstanding. **The lesson
  for the next publisher: mark the findings file in the same PR that edits the
  pages.** `check.py --stats` is where this shows up — a `resolved` column above
  the `published` column is either work to do or a loop someone forgot to
  close, and telling the two apart costs a full verification pass.)
- **Verified:** 2026-08-22 (Van Ness Auto Row: read all 73 pages of the adopted
  survey. **195 distinct printed address forms**, yielding **453 findings** —
  one per fact, not per passage: a construction record and a survey evaluation
  for each of the 112 buildings evaluated on DPR 523 forms, the same pair for
  the 44 identified but not evaluated, and 118 narrative facts (architects and
  builders, first tenants, garage capacities, building names, and the buildings
  the survey records as gone). **352 resolve to a parcel that may be
  documented, on 133 pages: 122 new and 11 edited**, across `tenderloin` (46),
  `nob-hill` (24), `western-addition` (18), `russian-hill` (15), `hayes-valley`
  (13), `mission` (8), `pacific-heights` (7), `presidio-heights` (1) and
  `haight-ashbury` (1). Not documented, and why: **82 findings name a number
  sf-eas-addresses has never carried** — 1644, 1650 and 1670 Pine Street among
  them, all three extant buildings the survey evaluated, whose numbers the city
  has since dropped; **30 have an EAS row that joins to no parcel**; **4 are
  condominium parcels**, which AGENTS.md holds back; and **1 names City Hall
  Avenue**, a street taken for the Civic Center that EAS no longer holds.
  **18 conflicts are stated on pages and reconciled on none.** Coverage note:
  this document is read in full and nothing in it is outstanding. Its own
  appendices are separate documents and are untouched: the DPR 523 forms for
  the 112 buildings, the Pine Street district record, and the map of the
  corridor. **What the run learned, beyond the cautions above:** the resolver
  looked up only the low end of a recorded range whenever a finding also
  carried that number on its own, which lost every building whose low number
  has been retired — 550–590 and 731–799 Van Ness Avenue among them — and it
  now expands the range; and a survey that prints its own assessor block *and*
  lot can choose between the parcels a range spans today, which is reading the
  record rather than adjudicating it.)
- **Verified:** 2026-08-22 (Carnegie branch libraries: read all 43 pages of the
  January 2001 nomination. **2 numbered San Francisco addresses in the whole
  document**, both other work by one of its architects: 333 Grant Avenue, the
  Home Telephone Building of 1908, and 455 Fair Oaks Street, the Church of the
  Holy Innocents of 1890, both by Ernest Coxhead. **1 resolves and is
  published** — 455 Fair Oaks Street, a new page, carrying the one conflict the
  batch produced (the nomination dates the church to 1890, the 2025 roll dates
  the parcel to 1904). 333 Grant Avenue is a condominium today and is declined.
  **The seven Carnegie branches the document is about carry no street number
  anywhere in it**, so none of them can be resolved from this source; that is
  the finding, not a shortfall in the pass. Coverage note: this document is
  read in full and nothing in it is outstanding.)
- **Verified:** 2026-08-22 (North Beach: read all 269 pages of the adopted PDF
  — the eleven narrative chapters, the regulatory and recommendation lists and
  all four appendices. 1,225 numbered-address mentions; 630 findings; 547
  resolve to a parcel with an EAS address and an active 2025 roll row, 546 of
  them now on **349 pages** — 339 new and 10 edited — across `north-beach`
  (251), `chinatown` (68), `russian-hill` (25) and one each in `nob-hill`,
  `marina` and `financial-district`. One resolved finding is declined: the
  California State Landmark number for the Third Baptist Church site, because
  1640 Grant Avenue is a hand-authored page that already documents the site
  from the State's own registration application and this source gives no
  designation year, so a dated timeline entry would have invented one.
  **83 unresolved**, in four groups: 35 where the recorded range has since been
  split across parcels and the record names no single lot (the Romeo flats rows
  are most of these — 19–33 Medau Place is eight parcels today); 34 with no EAS
  record at all, which is where most of the narrative's lost buildings sit (620
  Vallejo, 638 Union, 599 Jackson, 631 Green, 649 Broadway, 14–18 Osgood, 683
  Green); 7 condominium parcels the directory contract holds back; 3 EAS rows
  that carry no parcel number; and Washington Square itself, which has no street
  number. What the pass taught, beyond the cautions above: **a `conflict` on a
  finding is not always an address conflict** — `resolve_eas.py` treated every
  one as a disagreement with a second recorded address and printed `"290
  Lombard Street" against "None"` into eighteen methods before it was fixed;
  and **the resolver had no way to act on the lesson the module already
  wrote down** after Van Ness about thin streets, so `--area-from-nhood` and a
  `manifest` subcommand were added here rather than the paths being
  hand-patched again.)
- **Verified:** 2026-08-23 (Japantown: read all 112 pages of the file SF
  Planning serves as the adopted "Japantown Historic Context Statement (Revised
  2011)", which is the May 2009 final draft. 130 candidate numbered-address
  mentions over 94 distinct printed addresses; 91 are San Francisco properties
  the statement documents and 3 are rejected — the consultants' own office at
  724 Pine Street, a Berkeley address at 1538 Parker Street, and "136 Pine
  Street", which is the footnote number 136 run onto the caption "Pine Street
  Laundry, 1946". 125 findings: 83 resolved onto 53 parcels and published (51
  new pages, 2 existing edited), 39 unresolved, 3 rejected. The unresolved are
  what redevelopment did to the neighborhood: 26 addresses have no EAS record at
  all — 1500, 1516, 1609, 1661, 1690, 1705 and 1760 Post; 1698, 1717, 1823,
  1826, 1858 and 1898 Sutter; 1901, 1905, 1919 and 1831 Bush; 1623 Webster; 1617
  Gough; 1661 Octavia; 1612 and 1859 Fillmore; 1534 and 1669 Geary; 1540 Ellis;
  1433 Divisadero; 1440 and 1620 O'Farrell — three are printed ranges that
  genuinely span several parcels today (2115–2125 and 2226–2232 Bush, a row of
  six houses and a pair of lots; 1717–1719 Webster, one duplex on two lots), two
  are condominium parcels the roll gives zero lot area (1409 Sutter, 2255 Bush,
  2130–2140 Bush), and 1808A Sutter Street has no EAS row for its lettered
  number. Two addresses named only as households (1812 Bush, 1628 Post) were not
  extracted. Coverage note: this document is read in full and nothing in it is
  outstanding; its appendix maps are images with no text layer, and the Japantown
  Better Neighborhood Plan's own historic property survey, the April 2008
  Japantown draft context statement on the S3 archive and the Japantown Task
  Force data sheets it cites are separate documents and are untouched.
  **What it taught, beyond the per-document notes above:** a printed range whose
  high end is abbreviated ("1843-47") was expanded literally by
  `resolve_eas.py` into 47–1843 and came back spanning eighty parcels, and a
  number whose EAS row carries no parcel of its own was placed by its point onto
  a neighbouring lot and outvoted three numbers that stated a parcel, declining
  the extant National Register building at 1940–1946 Fillmore Street. Both are
  fixed in the tool. And `seed_pages.py names` missed two real personal names
  because DBI writes them behind a "one-stop:" prefix with no role label
  anywhere near them; that is fixed too, and the names are on the redaction
  list.)
- **Verified:** 2026-08-24 (North Beach, Van Ness Auto Row, Market & Octavia,
  Mission Dolores and `digitalsf/sfp-23`, re-run in `report` mode against a
  `resolve_eas.py` that no longer lets a point-placed parcel outvote the ones
  EAS states. **80 entries were candidates** — `unresolved` with a method saying
  the range spans more than one parcel — and **21 now resolve**: 7 in North
  Beach, 1 in Van Ness Auto Row, 13 in SFP 23. Market & Octavia and Mission
  Dolores have no candidates and were unchanged. The 7 North Beach entries are
  the ones this pass published, because they were the only newly-resolvable
  candidates carrying no publish decision; the other 14 were already `declined`
  under the old behaviour and were left for a human to reopen, since their
  decline note now states something the tool no longer believes. **6 pages** —
  545 Green Street, 1630 Grant Avenue and 843 Filbert Street new; 1445 Grant
  Avenue, 1859 Powell Street and 55 Osgood Place edited. Every one of the seven
  was checked against the assessor's `property_location` before publishing, and
  three of them are recorded there as the survey's full range on one parcel.
  What the pass taught, beyond the cautions above: **a closed findings file is
  not a settled one** — `report` over the five closed files also showed 93
  entries whose resolution has drifted since it was written for reasons that
  have nothing to do with this fix, every one of them already `published` (77)
  or `declined` (16), so a blanket `apply` over any of these files would
  silently overwrite hand judgement. Mission Dolores is the
  worst of them: a fresh `apply` would drop all 14 of its `rejected` entries and
  take it from 66 resolved to 44. *Scope a re-run to the entries you mean to
  change, and diff before you write.*)- **Verified:** 2026-08-24 (Russian Hill: read all 60 pages of the M-Files copy
  — the historical context, the architecture and architects chapters, the figure
  captions, the footnotes, the bibliography and the twenty-one-page Appendix I.
  298 numbered-address mentions by a mechanical scan of the OCR, plus several
  the OCR hides in run-ons. **109 findings over 104 distinct addresses: 67
  resolved, 41 unresolved, 1 rejected; 57 published on 48 pages, 10 declined.**
  The 48 pages are 44 new and 4 edited, across `russian-hill` (26),
  `nob-hill` (5), `tenderloin` (5), `financial-district` (4), `pacific-heights`
  (4), `western-addition` (2), `south-of-market` (1) and `marina` (1) — the
  spread comes from the architect biographies, not the study area. Ten
  findings carry a conflict; the six on published findings are stated on their
  pages' `.unknowns`, and nineteen construction dates disagree with the assessor
  in `building.completed_conflict`. None adjudicated.
  Not documented, and why: **the historical Larkin and Polk numbers** the report
  prints for demolished buildings are historical and were repointed at the
  current number the report itself gives, except 2519 Larkin, whose site the
  report spreads over two of today's parcels; **eight resolved parcels carry no
  row on the assessor's secured roll**, so the seeder makes no page for them —
  945 and 947 Green, 2555 Larkin, 2500 Steiner, 2000 and 2006 Washington and
  1925 Gough, several of them the 1920s co-operative apartment houses the report
  itself describes; **2652 Polk Street's own parcel is retired** and its EAS
  point falls in the 1299 Lombard parcel next door, so both its findings were
  declined rather than published onto a building the report describes
  differently; **nine printed ranges now span two
  parcels apiece** — 1249-1251 and 1271-1275 Lombard, 1326-1328, 1330-1332 and
  1342-1344 Greenwich, 1376-1392 and 1351-1361 McAllister, and 870-874 and
  2240-2268 Chestnut — and the report names no parcel, so none was placed;
  **five parcels are condominiums** the directory contract holds back
  (1268-1270 and 1269 Lombard, 1324 and 1330 Greenwich, 1167-1169 Green);
  **1205 Filbert Street and 2061 Hyde Street, which the OCR runs together as one
  address, are two parcels today**, so choosing between them would be
  adjudicating; and **twenty-six addresses have no EAS record at all**, among
  them 2501, 2503 and 2513 Larkin, 2601, 2615 and 2650 Polk, 532 Clay, 632
  Montgomery, 318 Post, 236 Stockton, 134 Sutter, 321 Davis, 1234 Union,
  205-209 California, 285 Second and 1940 and 1960 Pacific — the last two being
  Boss and Quandt apartment towers the report documents. Ten printed addresses were never candidates: five appear solely as
  somebody's home, one is in Alameda, and four are given by cross street with no
  number.
  What the pass taught, beyond the cautions above: **a source that prints both a
  historical and a current address will silently resolve on the wrong one**, because
  the historical number is usually still a live address somewhere on the same
  block — see the renumbering caution above; and **`resolve_eas.py` could not
  look up a street a source spells out**, because EAS holds the numbered streets
  as zero-padded ordinals (`02ND`, `24TH`). That killed 285 Second Street at the
  street, not the number. The tool now maps spelled-out ordinals to EAS's form
  and says so in the method. The Parkside statement (issue #56) was fetched to
  `research/corpora/sf-context-statements/parkside-hcs.pdf` in the same session
  and **not read** — this batch was much larger than one block suggested.)
- **Verified:** 2026-08-24 (Parkside: read all 58 pages of the adopted PDF, the
  whole file — the introduction and methodology, Part 1's suburbanisation
  context, Part 2's history from natural history through land ownership, the
  roadhouses, the Parkside Realty Company, the Boss Ruef graft trials, the
  1908 cottages, Pinelake Park, the Improvement Club, patterns of development
  and demographics, Part 3's property types and its six Notable Buildings, the
  three lists under "Other Structures of Interest", Next Steps, the Conclusion,
  every figure caption, every footnote and the bibliography. There is no
  appendix inventory table and the report prints no APN anywhere. **160
  address-level facts were found, 158 of them carrying a street number across
  149 distinct number-and-street pairs** — 59 from the 1908 Parkside Cottages
  list, 65 from Other Residential, 11 from Commercial/Civic/Religious and 25
  from the Notable Buildings write-ups, captions and footnotes. **151 resolve
  to a parcel**, on 142 distinct parcels, and **147 are published on 142
  pages**: 141 new pages and 1 edited, 141 of them under
  `san-francisco/sunset-parkside/` and one under
  `san-francisco/west-of-twin-peaks/` (800 Taraval Street, a corner parcel the
  assessor addresses as 2399 18th Avenue). **One conflict is stated** in a
  page's `.unknowns` — the 1920 deed conditions at 2516 23rd Avenue requiring a
  $2,500 house against a construction permit valuing it at $1,500 — and **49
  construction dates disagree with the assessor**, all in
  `building.completed_conflict` and none adjudicated; 41 of those are 1908
  cottages against roll years from 1906 to 1916. Not published, and why: **four
  resolved findings were declined as duplicates** of a fuller entry from the
  same statement on the same page (the p. 50 list entries for 1830 Taraval
  Street, 2250 Ulloa Street, 2476 20th Avenue and 2514 23rd Avenue, each of
  which also has a caption carrying a firm year, a builder or a style).
  **Nine findings stay unresolved**: four have no EAS record at all (2532 22nd
  Avenue, 2454 and 2458 28th Avenue, 2499 30th Avenue — three of them a digit
  or two off a number that does exist, which is exactly the near-miss not to
  stretch), one is the demolished American Seed and Nursery building at 1550
  Taraval Street that the report itself calls no longer extant, one is a
  condominium (2337 Taraval Street), one is a printed range now split across
  two parcels with no parcel named (1634-44 Taraval Street), and two are
  Notable Buildings the statement gives no street number for — the Trocadero
  Inn, located only as "in the area now known as Sigmund Stern Grove", and
  Abraham Lincoln High School, located only as "24th Avenue between Quintara
  and Rivera streets". Never candidates, and so not recorded at all: five
  buildings given by cross street with no number, four photograph captions that
  give a number but assert nothing datable, and four addresses that appear only
  as a named person's home. What the pass taught, beyond the cautions above:
  **a generic inventory entry published next to a specific caption entry from
  the same source is a duplicate on the page's timeline**, which is why four
  were declined — check for it in any statement carrying both a list and a
  narrative; and **`seed_pages.py names` reports nothing once the pages exist**,
  because it only inspects parcels still marked seedable, so the privacy pass
  has to read the `data.json` files the run just wrote rather than trusting the
  command. `fetch_keyed` also crashed on a zero-key fetch, unlinking a
  `.partial` file no batch had ever created; fixed in this run. Coverage note:
  this document is read in full and nothing in it is outstanding. The Oceanside
  and Sunset District Residential Builders statements, both on the same SF
  Planning page and both covering neighbouring parts of the Sunset, are
  untouched.)
- **Verified:** 2026-08-24 (Oceanside: read all 28 pages of the adopted PDF,
  the whole file — the historical context, the synthesis for the Sunset District
  and then the Oceanside itself (the early community, Carville and its streetcar
  houses, the 1906 refugee shacks, the neighbourhood name, the 1909 street
  renaming, well water and piped water, the improvement clubs, the schools and
  churches), Part III's property types and architectural styles, SPEAK's goals
  and priorities, both parts of the methodology, the bibliography and all 51
  endnotes. Pages 12 and 13 are full-page maps and carry no text. There is no
  appendix inventory. **32 address-level facts were found, 28 of them carrying a
  street number across 27 distinct number-and-street pairs**, all in the outer
  Sunset west of 37th Avenue. **20 resolve to a parcel**, on 19 distinct parcels,
  and **all 20 are published on 19 new pages**, every one under
  `san-francisco/sunset-parkside/`. **One conflict is stated** in a page's
  `.unknowns` — the Lodge at 1300-1304 La Playa, which the text calls demolished
  and its own footnote says still stands — and **three construction dates
  disagree with the assessor**, in `building.completed_conflict`, unadjudicated.
  **Twelve findings stay unresolved**: five have no EAS record (1315 48th Avenue,
  4131 Kirkham Street, 2200 and 1534 and 1938 Great Highway — and three of those
  five are buildings the report itself calls extant, which is the caution above),
  two are printed ranges now split across parcels the record does not choose
  between (4329-4331 Kirkham Street, 1343-1353 48th Avenue), one is a
  condominium (1351 42nd Avenue, the Francis Scott Key School Annex), and four
  are the block-face rows the statement gives no numbers for. Never candidates,
  and so not recorded: eleven buildings located only by cross street, one cover
  photograph, and one address appearing only as a named person's home. What the
  pass taught, beyond the cautions above: **the natural way to write up an
  inventory-list finding is the one thing the design contract forbids.** "Picked
  out by a 2007 walking survey as a house predating…" is the `a survey records…`
  pattern the root AGENTS.md rules out, and it was written onto 129 pages across
  both this batch and the Parkside one before an audit caught it. A listing or
  designation *event* may be stated as an event — the North Beach pages already
  do — but an ordinary fact about a building must be stated as a fact, with the
  attribution left to the Sources footer. *Grep the descriptions you are about to
  publish for "survey", "statement" and "report" before rendering.* Coverage
  note: this document is read in full and nothing in it is outstanding. The
  Kelley & VerPlanck survey it accompanies — 511 DPR 523 A forms, 60 B forms and
  5 district forms — is a separate corpus and is not held here. The Sunset
  District Residential Builders statement on the same SF Planning page is
  untouched.)
- **Verified:** 2026-08-24 (Transit Center District: read all 95 pages — the
  74-page context statement, the DPR 523 D district record and the three
  appendix tables. **316 address-level facts across 171 distinct
  number-and-street combinations**, every one carrying a street number: 143 rows
  across the three inventory tables, 24 more parcels that appear only in the
  ratings table, and 52 from the narrative. **261 resolved to a parcel, 211 are
  on 123 pages** — 58 of them created by this run — and **50 were declined**,
  the largest group being 26 bare construction years the assessor already
  gives. **55 stay unresolved**: 35 have no EAS record at all (the addresses
  this part of downtown lost to the Transbay project and the towers of the
  2010s), 12 are condominium parcels today, 3 exist in EAS with no parcel to
  join to, 2 are on Hunt Street, which EAS does not hold, 2 are the Paramount at
  680 Mission Street, whose parcel's lowest number is the page of the parcel
  next door, and 1 is the pre-1909 number the report prints for John Parrott's
  1854 house on Rincon Hill — 620 Folsom Street is a live address on a 1922
  office building today, so the lookup matches cleanly and means nothing. **17 construction dates disagree with the assessor** and are stated
  unadjudicated in `building.completed_conflict`; **8 more disagreements the
  report has with itself** are in the pages' `.unknowns`. Never candidates, and
  so not recorded: 10 parking-lot and vacant-parcel rows with no building and no
  date, the 42 rows the ratings table marks "(Demo)", four buildings the
  narrative gives only by corner, and four given a number but no date. What the
  pass taught, beyond the cautions above: **a survey of a redevelopment area
  records buildings that were about to be demolished, and some were** — the
  assessor's year built is the check, and where it postdates the survey the
  page must state both years rather than assert a demolition; and **two
  overlapping surveys do not fit in one page's survey panel**, which is why 57
  pages here carry this survey's listing on the timeline and its ratings
  nowhere. Coverage note: this document is read in full and nothing in it is
  outstanding. The DPR 523 A and B forms the survey produced are a separate
  corpus and are not held here.)
