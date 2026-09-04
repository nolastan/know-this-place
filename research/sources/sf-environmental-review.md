# sf-environmental-review — SF Planning environmental review documents (primary)

> **Research dossier.** Rules: [../AGENTS.md](../AGENTS.md) · register:
> [../SOURCES.md](../SOURCES.md) · cited on pages by the source id `sf-environmental-review`.
>
> - **Kind:** PDF reports · **Tier:** primary · **Status:** open
> - **Search-invisibility:** high — see the register for what that rates.
> - **Coverage:** 37 of 172 address-titled documents read; 181 findings, 106 resolved.
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

- **Coverage:** 37 documents read whole, all from the **address-titled** set.
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
  it records at 101 Mission Street). **Remaining: 135 address-titled documents**
  — the 1983–2011 downtown and South of Market projects, plus the finals and
  supplements of projects whose drafts are read — and the ~617 titled by project
  or area rather than address, which have not been assessed at all.

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
