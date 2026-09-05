# sf-environmental-review — SF Planning environmental review documents (primary)

> **Research dossier.** Rules: [../AGENTS.md](../AGENTS.md) · register:
> [../SOURCES.md](../SOURCES.md) · cited on pages by the source id `sf-environmental-review`.
>
> - **Kind:** PDF reports · **Tier:** primary · **Status:** open
> - **Search-invisibility:** high — see the register for what that rates.
> - **Coverage:** all 172 address-titled documents read, in 93 projects, plus the 36 named
>   single-site projects of 1974–1982 from the project-titled set; 497 findings, 322 resolved,
>   271 published. All ~617 project-titled documents are grouped and sampled in the triage note below.
> - **Local corpus:** `research/corpora/sf-environmental-review/`
>
> Update this dossier at the end of every pass — the `Verified:` line, the
> coverage note, and anything the pass learned about getting at the source.

- **What:** Draft and final environmental impact reports, initial studies and
  negative declarations published by the **San Francisco Department of City
  Planning / Planning Department** between **1975 and 2011**, digitized by the
  San Francisco Public Library. 789 of them are in the Internet Archive
  collection `sanfranciscopubliclibrary`; **172 are titled by street address**
  ("101 California Street : [draft] environmental impact report") and the rest
  by project or area name.

  **What this source gives that nothing else in the register does.** An EIR
  describes a site *as it stood before the project*, in the detail a
  preservation review demands — so it is the record of buildings that are no
  longer there, written while they still were. And it **states the assessor's
  block and lot outright**, which every other source has to be joined to EAS to
  get. 15 of the 16 documents in the first batch print the block; 11 print the
  lot as well, and two documents in the downtown batch print block *and* lot
  for every building in a table, their own site included.

  The address-level facts sit in three places, and they are the same three in
  every document: **"Project Site"** and **"Environmental Setting"** (what is
  standing, when it was built, of what, by whom, how big); **"Historic
  Architectural Resources"** (survey ratings, landmark and National Register
  status, the construction and alteration chronology, and often a page of the
  building's own history); and, in the older reports, a **"History of the Site"**
  section that goes back to the nineteenth century.

- **Where:** Cite the Internet Archive item page —
  `https://archive.org/details/<identifier>` — and name the report, its case
  number where it has one, and its year. The item page is what a reader can use;
  it carries the PDF, the page images and the text layer together.

- **How to get at it:**

  ```
  # the catalogue
  https://archive.org/services/search/v1/scrape
      ?q=collection:sanfranciscopubliclibrary AND (title:"environmental impact report"
         OR title:"initial study" OR title:"negative declaration")
      &fields=identifier,title,year,publisher&count=1000
  # the text layer for one item
  https://archive.org/download/<identifier>/<identifier>_djvu.txt
  ```

  Every item sampled is open: no `access-restricted-item`, no `licenseurl`, and
  a `_djvu.txt` on all of them. This is municipal work product, not a
  lending-library book, and that is the difference between this row and the
  *Here Today* row in the leads table. Fetch one item at a time with a
  three-second delay and a wall-clock deadline; `research/corpora/…/state.json`
  records what has come down, so a rerun resumes.

  **The batch unit is one project, not one document.** Almost every project has
  a draft and a final EIR and often an initial study as well, and the final is
  mostly comments and responses that restate the draft. **Read the draft.**

- **What is actually usable:** Sentences that pin a building to a year. The
  yield from sixteen documents was 61, and the shape is consistent:

  > "The existing wood and metal warehouse building was constructed in 1911 and
  > initially housed the Dyer Brothers Iron Works, which remained until 1935."
  > — 350 Rhode Island Street DEIR (1999)

  Two things that look promising and are not. The **project description** is a
  proposal: an EIR says what was intended, and whether it was built, and in what
  form, is a separate check against the assessor — nothing about the project
  itself belongs on a page. And the **cumulative-impacts and setting sections
  name dozens of nearby buildings**, but almost always by corner or by project
  name rather than by number.

- **Cautions:**
  - **Downtown is most of the collection.** The 1970s–80s office-tower boom is
    what generated the reports, so the address-titled set is heavily Financial
    District, South of Market and Rincon Hill. The first batch was deliberately
    picked to be everything *but* that, which is why it is spread over fourteen
    neighbourhoods; the unread ones are not.
  - **A converted industrial complex is a condominium now, and the directory
    contract refuses it.** The two richest documents in the first batch — 900
    Minnesota Street (the Schilling Wine Cellars) and 55 Laguna Street (the San
    Francisco State Teachers College campus) — are exactly the sites whose
    reuse turned them into condominiums, and **15 of the batch's 32 unresolved
    findings are that one cause.** Expect it: the buildings an EIR documents
    most fully are the ones a project was about to convert.
  - **The report contradicts itself, and the summary is the least reliable
    part.** 420-430 29th Avenue dates the parish hall 1925 "according to
    building permits" in the historic-resources chapter and 1926 twice in the
    project description; 55 Laguna dates Woods Hall 1926 twice and 1927 once;
    900 Minnesota gives the wood-frame additions as 1912–1941 and 1912–1949 and
    the winery's tenancy as ending in 1960 and in 1971. **Take the chapter that
    cites the permit or the survey, and record the disagreement in `conflict`.**
  - **The block and lot the report prints is the block and lot of its own
    day.** `resolve_eas.py` compares it against the parcel it resolves and
    prints the difference: of the 24 stated in the first batch, 5 matched
    exactly, 3 had been re-lotted since, and 1 crossed a block — 3575 Geary
    Boulevard, whose report names *two* parcels (Block 1083 Lot 2 and Block
    1084 Lot 4) and whose address resolves onto the second. **The printed
    parcel is evidence, not an answer**; it is at its most useful when it
    disagrees, because that is a lot line that has moved.
  - **The title address is the project's name, not necessarily an address on
    its own site — and resolving on it silently lands on someone else's
    building.** The 1981 report titled *2222 23rd Street* states its site as
    Assessor's Block 4216, Lot 1, the whole block bounded by Kansas, Rhode
    Island, 23rd and 24th. EAS's 2222 23RD ST is parcel 4158034 on a different
    block — a 1906 building across the street — while block 4216 today is many
    lots all addressed **2225** 23rd Street, the condominiums built on the site
    the report was about. `resolve_eas.py` resolved it, and only the printed
    block caught it. Two rules follow: **put the record's stated block on every
    finding from that record, not just the first**, or the resolver's
    printed-parcel comparison skips them silently and the check never runs; and
    where the title address and the stated block disagree, the finding is
    unresolved.

  - **The downtown reports are a rating index, not a building history.** The
    first batch was neighbourhood reports, where the yield is construction dates
    and architects. The 1975-1982 downtown reports are different in kind: their
    historic-resources chapters exist to say which buildings a tower would harm,
    so what they carry is **survey ratings for every building on and around the
    block, by street number, often with the assessor's block and lot beside it**.
    The 333 Bush initial study prints an eighteen-row table of block, lot,
    address, 1976 city inventory code and 1979 Heritage grade; the 222 Kearny
    DEIR prints twenty-four rows of address, building name and both ratings. Two
    thirds of this batch's findings came out of tables like those, and the
    building **name** attached to each number is the part no other source in the
    register supplies.
  - **A table is worth taking only if it survives its own OCR.** The same figure
    in the 101 Montgomery FEIR lists the same buildings, and its rating columns
    are dumped into the text layer detached from their rows — twenty ratings in a
    heap after the names. The tell is a spot check against a document that got
    the table right: three of its apparent alignments were wrong. **Read the
    names and the numbers off a scrambled table; do not read the values.** Where
    the only thing a row survives with is a marker meaning "of architectural
    importance", it is not worth a page.
  - **A demolition in a draft EIR is a proposal, not an event.** Every one of
    these reports describes buildings it is about to remove, in the future tense.
    A demolition finding needs a record that states it in the past tense — the
    101 California building "was demolished in 1974 after a destructive fire",
    the 201 Spear structure on lot 16 "was demolished in 1979", the 101 Mission
    brick building "has been demolished" in a *neighbouring* project's 1981
    report. Everything else is a **site-history** finding dated to the year the
    report saw the building standing.
  - **Check the parcel's build year against the fact's date before writing the
    description.** Two thirds of this batch resolved onto parcels the assessor
    dates *after* the fact — a 1907 building's page is a 1987 tower's page. A
    fact written flat ("the Robins Building was built to the design of T.
    Paterson Ross") then reads as a description of the building standing there
    now. Every one of them needs the frame: *stood here until*, *then on the
    corner*, *a building then standing here*. The check is one comparison per
    finding and it caught eleven in this batch.
  - **Resolve past the pre-1910 renumbering guard with the block and lot, not
    the number.** Four findings dated 1851-1907 were refused by the guard and
    resolved by hand on what the record itself supplies: the stated assessor
    block and lot (505 Sansome, 201 Spear), the stated corner (201 Spear again),
    or the roll agreeing with the record's own construction year (216 Pine, where
    the assessor also says 1907). The guard is right to refuse them; the record
    is what overrides it.
  - **`resolve_eas.py` refuses a number EAS puts on parcel 1300001.** That parcel
    is not a city block — it carries 101 through 106 Montgomery together — and
    its presence makes a clean single-parcel address look like an ambiguous one.
    Where the record names a block, the candidate on that block is the answer:
    105 Montgomery is 0288006 on block 288, and the California Pacific Building
    survives there as its own parcel.

  - **The block and lot a report prints belong to its own site, and attaching
    them to a vicinity finding turns the resolver's parcel check into noise.**
    Every one of these documents states the project's assessor block, and the
    same document then rates twenty buildings around the block that are on
    other blocks entirely. Carrying the project's block onto those findings made
    `report` print two "another block" lines and three re-lottings that were
    nothing of the kind, and would have buried a real OCR error if there had
    been one. Put the printed parcel on a finding only where the record prints
    it *for that building* — which downtown means the project site, the rare
    rating table that prints block and lot per row, and nothing else.

  - **Several parcels can be one building, and the assessor says so by filing
    them all at one address.** The 505 Montgomery tower stands on seven lots of
    block 227 and the 100 First tower on six lots of block 3721; every one of
    those parcels is active, carries its demolished predecessor's street number
    in EAS, and comes off the roll with **no build year and no storeys**, filed
    at 505 Montgomery Street and 100 First Street respectively. Resolving each
    finding onto its own parcel and seeding from the manifest would have made
    eleven pages for two towers. The tell is the roll's `property_location`
    against the parcel's own number, and the two lots on block 227 that do
    *not* match it — 0227011 (640 Sacramento, built 1907) and 0227027 (653
    Commercial, built 1923) — are exactly the two buildings the project kept.

  - **A scrambled site table is readable when the document restates it in
    prose, and these documents always do.** The 100 First Street and 505
    Montgomery Street reports both print their site buildings and their
    construction dates as two detached heaps in the text layer, and both walk
    the same list again, building by building with the year in parentheses, in
    the impacts chapter. Read the prose and use the table only to confirm the
    count. Where the roll can be checked afterwards it has agreed every time:
    the 521 Mission garage's 1952, 640 Sacramento's 1907 and 653 Commercial's
    1923 are all the roll's years too.

  - **The pre-1910 guard fires on a third of a downtown batch and is wrong
    about all of it.** These are 1980s surveys of buildings then standing, so
    the address is the surveyor's, not a number carried over from before 1909,
    and the renumbering question does not arise. Ten findings were refused this
    way and nine were resolved by hand on the roll year, the record's own block
    and lot, or both; the tenth was a genuine duplicate. Say so in the method
    rather than leaving them unresolved.

  - **The nineteenth-century material is pre-renumbering.** 2222 23rd Street's
    "History of the Site" quotes an 1884 gazetteer placing the San Francisco
    Pioneer Varnish Works on "Sonoma Street, between Twenty-third and
    Twenty-fourth" — a street name the report footnotes and the text layer does
    not carry. Nothing dated before 1910 in this source resolves without the
    renumbering checks in [loc-newspapers.md](loc-newspapers.md).
  - **OCR of a typewritten 1980s report is poor.** Numerals break ("1 964",
    "191 1", "Landmark No. 1 90"), and one alternatives chapter in the 299
    Dolores Street DEIR is scrambled beyond reading. Search for the fact in more
    than one place in the document; these reports repeat themselves constantly,
    and that redundancy is what makes them readable at all.

  - **Triage of the 617 project-titled documents.** The catalogue query above
    returns 789 items. 172 have a street number at the front of the title and are
    read; the other 617 fall into eight groups, and the group predicts the yield
    far better than the size does. Sampled 2026-09-05.

    | group | docs | carries street numbers? | sampled evidence |
    |---|---|---|---|
    | **Named single-site projects** — one tower, hotel, store or apartment block, titled after the developer's project rather than its address ("One Sansome", "Daon Building", "Russ Tower", "Neiman-Marcus department store") | **162** in 93 projects | **Yes, densely.** The same document as the address-titled downtown reports. | The Russ Tower DEIR dates and credits 350, 334–340 and 344–346 Bush Street; the One Sansome DEIR dates the Holbrook Building at 58 Sutter Street to 1912 and names MacDonald and Applegarth. **Batch `named-sites-1974-1982` read 36 of these.** |
    | **Titles carrying a street address, but not in first position** — "Case No. 2003.0273E : 46 Geary Street", "Draft EIR : 1634-1690 Pine Street", "Francisco Place : office/condominiums, 530 Chestnut Street" | **50** | **Yes.** Single-site documents the leading-digit filter missed; the 1998–2013 ones append a consultant's historic resource evaluation. | The titles name the buildings outright. Not yet read — this is the next batch to take. |
    | **Institutional campuses** — hospitals, museums, libraries, schools, churches | **77** | **Yes, but few buildings each.** A campus document describes two or three buildings and restates them hundreds of times. | The 1992 Main Library FEIR carries 387 numbered-address mentions and nearly all are 100 Larkin Street and 45 Hyde Street; the 1998 Asian Art Museum DSEIR is the same two buildings, and records that 45 Hyde Street was demolished in November 1997. |
    | **Area and policy plans** — Mission Bay, Yerba Buena Center, the Downtown Plan, Rincon Hill, South of Market, Eastern Neighborhoods, the Housing Element, planning code amendments | **130** | **Mostly no.** They describe by street, block face and project name. | The 1,068 KB Downtown Plan DEIR yields **18** numbered-address mentions and the only building among them is 522/528 Howard Street, the plan's own case-study site; the rest are the department's own office address and figure captions. The South of Market plan tabulates development sites by cross street ("First & Harrison"). The exception is a redevelopment plan naming a surviving building outright: Rincon Point–South Beach names the Oriental Warehouse at 650–622 First Street. |
    | **Procedural notices** — notices of preparation, notices that an EIR is required, notices of availability | **96** | **Redundant.** A notice restates its own project's address and nothing else, and the project usually has a full document in the collection. | The 2008 CityPlace NOP names 935–939, 941–945 and 947–965 Market Street; the 2009 CityPlace DEIR names the same buildings *and dates them*. Read the DEIR. |
    | **Transportation corridors** — Third Street light rail, Caltrain downtown extension, Van Ness BRT, the bicycle plan, the Embarcadero Freeway | **30** | **No.** Stations and cross streets. | The Third Street LRT DEIS/DEIR's 286 apparent mentions are table-of-contents artefacts and agency addresses. |
    | **Airport** — SFO master plan and expansion, BART–SFO extension | **37** | **No, and outside the city.** | The 1992 SFO master plan FEIR: 34 mentions in 1.4 MB, none of them a San Francisco building. |
    | **Outside San Francisco** — Calaveras Dam, Lower Crystal Springs, Hetch Hetchy, San Andreas Pipeline, the Larkspur and Sausalito ferry terminals, Novato, Oakland Harbor | **35** | **No.** Not San Francisco addresses at all. | The Calaveras Dam DEIR: 19 mentions in 1.7 MB, all in Alameda and Santa Clara counties. |

    **Size predicts nothing here.** The two largest documents in the collection are
    Mission Bay and the Downtown Plan, and both are area plans that name almost no
    street numbers, while the 500 KB Russ Tower DEIR dates five buildings and
    credits four architects.

  - **A filter on the shape of a title is a filter on the source, and this one
    silently dropped a third of it.** The address-titled set was defined as "the
    title begins with a digit", and four batches carried that definition as though
    it were a property of the documents. It is not: **162** documents describe
    exactly one site in exactly the same way and are titled after the developer's
    project (*Russ Tower*, *Pan Magna Plaza*, *Welsh Commons*), and **50** more
    print the address in the middle of the title (*Case No. 2003.0273E : 46 Geary
    Street*). **Before treating a catalogue filter as a description of a source,
    check what falls outside it** — the check here was one regular expression over
    617 titles, and it found the best unread material in the collection.

  - **The pre-1978 reports predate the historic-resources chapter.** CEQA's
    architectural-resources requirement had not yet produced the chapter this
    source is mined for, and a 1974–1977 report answers the question in one
    sentence: nothing on the site is in *Here Today* or on the Board of
    Supervisors' landmark list. Nine of the ten empty documents in the 1974–1982
    batch are from those four years. **Start a batch of this source at 1978**, and
    read the earlier ones only for an appendix — the 1975 Bank of Tokyo DEIR is
    the exception precisely because it binds in a Heritage-commissioned history of
    the Alaska Commercial Building as its Appendix B.

  - **A merged downtown parcel keeps one of its old street numbers, and the block
    the report prints is what finds it.** Thirteen of the 1974–1982 batch's
    findings came back "the address does not exist today" and every one resolved
    on the record's own printed block: block 3712's buildings are 101 Market
    Street, block 289's are 1 Sansome Street, block 227's Old Sub-Treasury is 555
    Montgomery Street, block 3749's are 303 Second Street, block 313's City of
    Paris is 150 Stockton Street, block 238's Alaska Commercial Building is 350
    California Street. The project description states the block in the first two
    pages; read it before the historic-resources chapter.

  - **The seeder knows which parcel already has a page, and it is not always the
    path the resolver formed.** 46 Kearny Street resolved to parcel 0311007, whose
    page `seed-list` reported as already documented at
    `/san-francisco/union-square/kearny-street/30/` — a different street number and
    a different neighborhood from the `/financial-district/kearny-street/88/` the
    resolver had formed from the roll's address. **Run `seed-list` before writing
    the facts** and take its "already documented at" lines as corrections to the
    findings' paths.

- **People:** These reports name project sponsors, property owners and the
  neighbours who wrote comment letters, and all of that is barred by "Privacy —
  hard limits" in the root [AGENTS.md](../../AGENTS.md). Take the **architect,
  the builder, the firm that occupied the building and the artist credited with
  a work in it** — Willis Polk and Company at 299 Dolores, the Fisk Rubber
  Company at 1611 Pine, Reuben Kadish's 1936 mural at 55 Laguna. Leave the rest.
  Two shapes to watch: a building **named after its owner** in the report's own
  shorthand ("the McNear building" at 22-30 Alta Street) can be used as the
  building's name but not as a biography — the first batch takes the name and
  drops the owner's office and company; and a **designated landmark's official
  name** carries a person's name by definition (City Landmark No. 190, the
  Charles L. Hinkel House), which is a published designation, not a fact about
  a resident.

- **What this source is for, in one case.** The page for 20-30 Alta Street
  carried a 1937 building by Angus McSweeney, from the Modern Architecture and
  Landscape Design context statement, with no hint that it is gone. This
  source's 1998 report for the site says the building went up in 1935, was
  remodelled in 1937 and was **demolished by the City in 1992** after storm and
  roadwork damage — and the 2025 assessor's roll still classes the parcel
  "Vacant Lot Residential w/ Restriction". A context statement records what a
  survey found; an EIR records what a project was about to remove. **Where the
  two disagree about whether a building still stands, this is the source that
  knows.**

- **Citation label:** the publisher, the report's own title, its case number
  where it has one, and the year:

  > San Francisco Planning Department, *900 Minnesota Street: Draft
  > Environmental Impact Report*, Case No. 2004.0027E, 2005.

  On a page, name the report and the year and link the Internet Archive item.

  - **The consultant's report bound into the back of an environmental review is
    where the dates are.** From about 2000 the Planning Department stopped
    describing buildings itself and started appending the historian's own work: a
    Page & Turnbull historic resource evaluation, a McGrew Architecture report, a
    Carey & Co. Section 106 review. Those appendices are the densest part of the
    document by a wide margin — Carey & Co.'s twenty-nine-property survey in the
    275 10th Street EIR gives a construction year, an architect or builder and an
    occupancy history for each, taken from the building permits on microfilm, and
    the EIR's own chapters repeat perhaps a fifth of it. **Read to the end of the
    appendices**; the summary chapters are a table of contents for them.
  - **The appended report and the chapter that summarises it disagree, and the
    appendix is the one that did the research.** The 275 10th Street EIR's own
    setting chapter says the building was commissioned by John Cassaretto for the
    G & H Price Pump and Engine Company; the Section 106 review it appends names
    the architect E. A. Neumarkel and the owner as G. W. Price, from the original
    permit. Its initial study then swaps two of the three site buildings' dates.
    This is the "the summary is the least reliable part" caution above, one layer
    further in: **the chapter that cites the permit or the survey wins, and from
    2000 on that chapter is usually in the appendices.**
  - **A project site that is a surface parking lot yields nothing, and the report
    says so on its first page.** Six of the thirty-seven projects in the
    1995–2011 batch — 631 Folsom, 888 Howard, 55 Ninth, 201 Folsom, 300 Spear and
    both 450 Rhode Island projects — sit on cleared ground, and their initial
    studies never come back to buildings. The tell is in the project description:
    "currently occupied by a surface parking lot".
  - **Two projects prepared together share one report's text.** 201 Folsom Street
    and 300 Spear Street were the two halves of one requested rezoning, and their
    2002 draft EIRs repeat each other's setting chapters almost word for word.
    Read one, note the other as read, and record the findings once.
  - **The buildings a report describes are mostly gone, and the assessor says
    which — but not all of them are.** Twenty-four of the fourth batch's findings
    landed on a parcel the roll dates after the fact, and the split is even: some
    are demolitions (248 Front, 560 Mission, 350 Fremont, 275 10th, 340 Mission,
    250 10th, 227 7th) and some are rehabilitations of the very building described
    (21 Clarence Place, 1000 Van Ness, 50 Oak). The report itself distinguishes
    them — a project that *converts* a building says so in its project
    description — so read that before choosing between "stood here until" and an
    ordinary construction date with the roll year stated as a disagreement.
  - **A retired street number resolves through the project's own merged parcel,
    not through the street.** Half of the fourth batch's unresolved findings are
    numbers EAS no longer holds, and for a project's own site buildings the answer
    is usually one query away: the report names the lots, the lots merged, and the
    merged parcel keeps one of the old numbers. 246 and 250 Front Street are 248
    Front Street; 64 and 72 Dore Street are 275 10th Street; 70 Oak Street is 50
    Oak Street; 562–572 and 554–560 Mission Street are both 560 Mission Street.
    The vicinity buildings are the ones that genuinely die.
  - **The Klockars blacksmith shop is 443 Folsom Street, not 449.** Two reports in
    this source give City Landmark No. 149 at 449 Folsom Street, which EAS does
    not hold; the parcel next door at 443 Folsom Street is active, industrial and
    dated 1913 by the roll against the landmark's 1912.

- **Coverage:** all 172 address-titled documents read, in 93 distinct projects.
  The first sixteen were deliberately outside downtown — 61 findings, 29 resolved
  onto 13 pages; 1055 Stockton yielded nothing, its EIR saying neither building
  on the site was on any list of historical, architectural or cultural interest
  and giving no construction date for either. The second batch is **the earliest
  downtown reports, 1975–1982**: 21 documents, one per project, the draft where a
  project has a draft and a final — 120 findings, 78 resolved, 73 published on 52
  pages, 17 of them seeded by that run. Three of the 21 yielded nothing (750
  California Street, a vacant site whose neighbours are all named without street
  numbers; 71 Stevenson Street, a final initial study that defers historic
  buildings to the EIR; 135 Main Street, whose only usable fact is a demolition
  it records at 101 Mission Street). The third batch is **the downtown and South
  of Market projects of 1983–1991**: 19 documents, one per project — 110 findings,
  77 resolved, 59 published on 44 pages, 11 of them seeded by that run. Two of
  the 19 were near-empty: 600 Harrison Street is a surface parking lot whose
  initial study found historic resources insignificant, and 101 Second Street
  gives its three site buildings a Heritage rating and neither a name nor a date.
  Its richest documents are 505 Montgomery Street and 100 First Street, which
  between them date thirteen demolished buildings, and 343 Sansome Street, which
  gives the 1908 Howard and Galloway building and its 1929 Crown Zellerbach
  remodelling by Sam Hyman and Abe Appleton. The fourth batch is **the address-titled projects of
  1995–2011**: 37 documents, one per project — 147 findings, 96 resolved, 72
  published on 43 pages, 12 of them seeded by that run. It finishes the
  address-titled set. Six of its 37 projects yielded nothing, all surface parking
  lots or cleared sites: 631 Folsom Street, 888 Howard Street, 55 Ninth Street,
  201 Folsom Street, 300 Spear Street and both 450 Rhode Island Street projects.
  Its richest documents are the ones that append a consultant's report — 275 10th
  Street, whose Carey & Co. Section 106 review dates twenty-nine properties around
  the block of Tenth Street between Howard and Folsom; 178 Townsend Street, whose
  building history walks the California Electric Light Company's Station B from
  its 1888 commission to Percy & Hamilton through to the 1995 demolition of its
  150-foot smokestack; and 949 Market Street, which dates the Empress Theater to
  the day it opened. The fifth batch is the **named single-site projects of
  1974–1982**: 36 documents, one per project — 59 findings, 43 resolved, 39
  published on 20 pages, 2 of them seeded by that run. It is the first batch out of
  the project-titled set, and its richest documents are One Sansome (the Holbrook
  Building of 1912 by MacDonald and Applegarth), the Bank of Canton headquarters
  (the first U.S. Branch Mint of 1849 and the Sub-Treasury of 1875–77 on the same
  spot), Russ Tower (the Mining Exchange Building of 1923 by Miller & Pflueger and
  two demolished neighbours by T. Paterson Ross and S. Heiman), the Daon Building
  (280 Battery Street by Lewis P. Hobart, 1908, and two by B. G. McDougall),
  Neiman-Marcus (the City of Paris building of 1896 and its 1909 Bakewell and Brown
  interior) and the Bank of Tokyo (the Alaska Commercial Building of 1909 by Meyers
  and Ward). Ten of its 36 yielded nothing, nine of them from 1974–1977, before the
  historic-resources chapter existed.
  **Remaining: 581 of the 617 project-titled documents, grouped and sampled in the
  triage note above — 18 more named single-site projects of 1983–1987 and 39 of
  1988–2005, the 50 documents whose titles carry a street address but not in first
  position, 77 institutional campus projects, 130 area and policy plans, 67
  transportation and airport documents, 96 procedural notices and 35 documents
  about places outside San Francisco — and the finals and supplements of projects
  whose drafts are read.**

- **Verified:** 2026-09-04 (two runs on the same day. The first promoted the row
  from the leads table and mined the outside-downtown batch: 16 documents, 61
  findings, 29 resolved, 21 published on 13 pages. What it learned: **the
  assessor's block and lot come free from this source**, which no other
  registered source gives; **the batch unit is the project, not the document**,
  because draft and final restate each other; **condominium conversion is the
  dominant refusal**, and it hits precisely the best-documented sites; and **the
  reports contradict themselves between chapter and summary**, so the chapter
  citing the permit or the survey is the one to take.

  The second run read the earliest downtown reports, 1975–1982: 21 documents,
  120 findings, 78 resolved, 73 published on 52 pages. What it learned: downtown
  reports are **rating indexes** rather than building histories, and their tables
  of address, name and survey grade are the yield — but **only where the OCR kept
  the table's columns with its rows**; a **demolition in a draft EIR is a
  proposal**, so it is a site-history finding until a later record states it in
  the past tense; **the parcel's build year has to be compared with the fact's
  date before the description is written**, because most of these facts land on
  the page of the tower that replaced the building they describe; and the
  **pre-1910 renumbering guard is overridden by the record's own block and lot**,
  not by the street number.)

  **2026-09-04**, third run: the 1983–1991 downtown and South of Market projects,
  19 documents, 110 findings, 77 resolved, 59 published on 44 pages. What it
  learned: **a report's printed block and lot belong to its own site**, so
  attaching them to the twenty buildings it rates around the block turns the
  resolver's parcel check into noise; **several parcels can be one building**,
  and the roll says which by filing them all at one address with no build year,
  which is what separates the two buildings the 505 Montgomery project kept from
  the seven lots of the tower; **a scrambled site table is readable because these
  documents restate it in prose**, building by building, in their impacts
  chapter; and **the pre-1910 guard is wrong about a modern survey of old
  buildings** — it refused ten findings here and nine were resolved by hand on
  the roll year and the record's own parcel.)

  **2026-09-04**, fourth run: the address-titled projects of 1995–2011, 37
  documents, 147 findings, 96 resolved, 72 published on 43 pages. It finishes the
  address-titled set. What it learned: **the historian's report bound into the
  appendices is where the dates are** from about 2000 onward, and it outranks the
  chapter that summarises it; **a surface-lot project yields nothing**, and its
  initial study says so on page one; **two projects prepared for one rezoning
  share a report**, so 300 Spear Street's findings are 201 Folsom Street's; **a
  retired street number usually resolves through the project's own merged
  parcel** rather than dying on the street; and **the roll's later year is a
  demolition on some of these parcels and a conversion on others**, which the
  project description itself distinguishes.

  **2026-09-05**, fifth run: the triage of all 617 project-titled documents, and
  the first batch out of it — the named single-site projects of 1974–1982, 36
  documents, 59 findings, 43 resolved, 39 published on 20 pages. What it learned:
  **the filter that defined the address-titled set was a filter on title shape and
  not on the documents**, and 212 single-site reports fall outside it, 162 named
  after the developer's project and 50 printing their address later in the title;
  **the group predicts the yield and the size does not**, so a thousand-page area
  plan gives eighteen numbered mentions and a five-hundred-kilobyte single-site
  DEIR gives five dated buildings and four architects; **the pre-1978 reports
  predate the historic-resources chapter** and answer the question in a sentence,
  which is where nine of this batch's ten empty documents come from; **a merged
  downtown parcel keeps one of its old street numbers**, so thirteen findings the
  resolver refused for having no EAS record resolved on the block the report
  prints on its own first pages; and **`seed-list` corrects a path the resolver
  formed**, which is how 46 Kearny Street's fact reached the page its parcel
  actually has.)
