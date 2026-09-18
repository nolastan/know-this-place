# nrhp-nominations — National Register of Historic Places nomination forms (primary)

> **Research dossier.** Rules: [../AGENTS.md](../AGENTS.md) · traps:
> [../LESSONS.md](../LESSONS.md) · register:
> [../SOURCES.md](../SOURCES.md) · cited on pages by the source id `nrhp-nominations`.
>
> - **Kind:** PDF reports (federal nomination forms) · **Tier:** primary · **Status:** open
> - **Search-invisibility:** high — the listings are indexed everywhere; the forms are not. A search for a street number returns the Wikipedia list entry and the NPS map pin, never the paragraph inside the PDF that dates the building and names its architect.
> - **Coverage:** 153 of 165 San Francisco listings read — every one certified before 2016, plus the Civic Center district the index omits and the Uptown Tenderloin Historic District (08001407) read in full. All six Anne Bloomfield district nominations and the Southern Pacific Company Hospital Historic District (89000319) are read. 1,177 findings, 1,033 resolved, 989 published.
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
- Fetch the PDFs at 2–3 seconds apart **with `curl`** and extract with
  `pdftotext -layout`. 53 of the 54 in the first batch and 41 of the 42 in the
  second had a usable text layer. A 42-document batch takes about three
  minutes this way and about two hours through `urllib.request` — see the
  caution below.
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

- **A district nomination is a per-property inventory, and that is the whole
  reason to read one.** Six of the listings in this source are districts, and
  five of those six were written by Anne Bloomfield in a single regular format:
  a numbered appendix entry per building giving `Type, ADDRESS: YEAR, style,
  storeys, description`, then a paragraph naming the architect and contractor,
  then the citation. 83001230 (Liberty Street) has about fifty of them.
  Everything after the address in that line is publishable and everything about
  the first owner in the paragraph is not. The one district read so far,
  78000757 (Civic Center), is the exception in shape — no appendix, a prose
  walk through eleven buildings with a date in each heading and a street number
  in each first line — and it is also the exception in access, being in neither
  the city nor the county index query.

- **A district nomination will not give every building a number, and City Hall
  is the worked example.** 78000757 describes City Hall by the block it
  occupies — Polk, McAllister, Van Ness, Grove — and never prints a street
  number for it anywhere in 99,000 characters, so no finding was written for
  the building the district is named after. Ten of its eleven structures do
  carry a number.

- **The nomination's own numbers can be superseded, `record_date`
  notwithstanding.** 78000757 addresses the War Memorial Opera House as 309 Van
  Ness Avenue and the Veterans Building as 459; EAS has neither, and holds 301
  and 401 on one parcel. `extra.record_date` correctly stops the renumbering
  guard from refusing a 1978 document, but it does not make 1978's number
  current. Resolve on the building's name and its stated block, mark it
  `"by_hand": true`, and put the arithmetic in `method`.

- **`urllib` is unusably slow against npgallery and `curl` is not.** The same
  fetch that takes about three minutes per document through
  `urllib.request.urlopen` takes about one second through `curl`. The 1966-1979
  batch's "about three minutes for 54 documents" was a `curl`-speed figure; a
  Python loop written for the 1980s batch was on course for two hours before
  the difference was measured.

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

**And the notable past occupant, always — this is the decision issue #310
made, and it is settled.** A nomination is a published federal record about a
building; where its prose names somebody the building is known for and puts
them in the past, that is a fact about the building and a run publishes it,
cited, without filing a question. The rule it seemed to collide with exists so
this site can't be used to look somebody up or to launder a name out of a
permit, and neither reaches a figure a nomination already covers. The root
[AGENTS.md](../../AGENTS.md) and [../AGENTS.md](../AGENTS.md) now say so
affirmatively. **What is still a judgement is where the fact lands**, and the
Uptown Tenderloin's eleven person-naming rows are the worked case:

| the nomination records | where it goes | example |
|---|---|---|
| a residency with a period | `notable_residents` — name and period, nothing else renders | Frank Capra, 1921, 233-237 Eddy Street |
| a residency with no period | `notable_residents` with `period: null`, which prints "Undated"; a qualifier worth keeping earns a one-clause `narrative.lead` instead, and the renderer then drops the panel row | Dashiell Hammett at 620 Eddy Street, "when he began writing" |
| a **use of the building** | a `historical_record` entry on the one timeline, like any other dated fact | Jessie Hayman's and Tessie Wall's brothels |
| a dated event at the building | the same | John Galen Howard's death at 227-231 Ellis Street, July 1931 |
| a plaque the building carries | the same, dated by what the plaque records | the Isadora Duncan plaque at 501-525 Taylor Street |
| an owner who is **independently notable**, or whom the building is named for | `notable_residents` if they lived there with a period, otherwise the timeline entry the ownership belongs to | Louis Feusier, 1875–1914, 1067 Green Street; Paul Verdier's 1919 purchase of 1001 Vallejo Street, the Verdier Mansion |
| an **ordinary** owner — first owner, client, landlord — in any era | nothing — owners are out whatever their date | "A.A. Louderback lived in a house on this site until 1906" |

Two things this case taught that generalise. **Count the people, not the
sentences**: the run that read the inventory reported "twelve rows" naming a
notable resident and listed seven names; the sweep under #310 found eleven rows,
nine of them publishable, and two of the nine — Howard and Duncan — had never
been listed, because one has no full stop at the end of its clause and the other
is inside the `signs:` field rather than in a tail. And **a district nomination
contradicts itself about addresses**: section 8 places Howard's death at 227-231
Eddy Street where the inventory places it at 227-231 Ellis, and there is no
227-231 Eddy row at all. Publish on the inventory row, put the disagreement in
the page's `unknowns`, and don't adjudicate it.

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

- **Read:** all 54 San Francisco listings certified before 1980
  ([`listed-1966-1979.json`](../findings/nrhp-nominations/listed-1966-1979.json)),
  the San Francisco Civic Center district nomination of 1978
  ([`civic-center-district.json`](../findings/nrhp-nominations/civic-center-district.json)),
  and the 37 single-building nominations among the 42 listings certified
  1980-1989
  ([`listed-1980-1989.json`](../findings/nrhp-nominations/listed-1980-1989.json)),
  and the **Uptown Tenderloin Historic District nomination of 2008 (08001407) in
  full** — its whole section 7 inventory, 477 rows across 33 blocks
  ([`uptown-tenderloin-district.json`](../findings/nrhp-nominations/uptown-tenderloin-district.json)),
  whose **prose tails** were re-swept under #310 for the people the first pass
  left
  ([`uptown-tenderloin-notable-residents.json`](../findings/nrhp-nominations/uptown-tenderloin-notable-residents.json)),
  and whose **section 8, the statement of significance**, is now also read end
  to end, under #346
  ([`uptown-tenderloin-section8.json`](../findings/nrhp-nominations/uptown-tenderloin-section8.json)),
  and two of the five remaining 1982-1989 district nominations — **82000983
  Bush Street-Cottage Row**
  ([`bush-cottage-row-district.json`](../findings/nrhp-nominations/bush-cottage-row-district.json))
  and **83001230 Liberty Street**
  ([`liberty-street-district.json`](../findings/nrhp-nominations/liberty-street-district.json)),
  both read in full, and the **three Russian Hill district nominations of May
  1987**, all read in full — **87002286 Macondray Lane**
  ([`russian-hill-macondray-lane-district.json`](../findings/nrhp-nominations/russian-hill-macondray-lane-district.json)),
  **87002288 Paris Block**
  ([`russian-hill-paris-block-district.json`](../findings/nrhp-nominations/russian-hill-paris-block-district.json))
  and **87002289 Vallejo Street Crest**
  ([`russian-hill-vallejo-street-crest-district.json`](../findings/nrhp-nominations/russian-hill-vallejo-street-crest-district.json)),
  and the last 1980s district nomination, **89000319 Southern Pacific Company
  Hospital Historic District**
  ([`southern-pacific-hospital-district.json`](../findings/nrhp-nominations/southern-pacific-hospital-district.json)),
  and **all 17 listings certified 1990-1999**
  ([`listed-1990-1999.json`](../findings/nrhp-nominations/listed-1990-1999.json)),
  and **all 40 listings certified 2000-2015** apart from the Uptown Tenderloin
  district — 26 of 2000-2009
  ([`listed-2000-2009.json`](../findings/nrhp-nominations/listed-2000-2009.json))
  and 14 of 2010-2015
  ([`listed-2010-2015.json`](../findings/nrhp-nominations/listed-2010-2015.json)).
- **Not read, and this is the queue in order:**
  1. **The 7 listings certified 2017-2019** — 100001018 Federal Office
     Building, 100001338 Henry Geilfuss House, 100001665 Sacred Heart Parish
     Complex (a district: four buildings), 100002287 Central YMCA, 100002359
     The Women's Building, 100004413 Swedish American Hall, 100004531 Glen
     Park BART Station. All seven serve a PDF at the `_text` path (tested
     2026-09-18); they are the next batch and one session's work.
  2. **The 8 listings certified 2020 or later** (100004868 onward), whose
     `_text` path serves a 1.6 KB PNG placeholder — every one of them, tested
     2026-09-18. Finding another route to these PDFs is that batch's first
     job; the index carries no `NARA_URL` for any of them.
  3. **77000334** (Mills Building and Tower) and **01000281** (Maritime
     National Historic Site, Fort Mason), whose PDFs have no text layer.
- **Never guess a reference number.** 08001407 is the Uptown Tenderloin
  Historic District. 08000209 — a plausible guess for an early-2008 San
  Francisco listing — downloads with HTTP 200 and serves 154 pages of nomination
  for Johnston's Inn in Paris, Kentucky. The fetch succeeds, `pdftotext`
  succeeds, and the only quick tell is the PDF's own title metadata. Take the
  refnum from the index query and read the property name on page 1 before
  extracting.
- **A district inventory's block-and-lot column is OCR, and its neighbours are
  the check.** The Uptown Tenderloin inventory prints `540/11` for 76-80 Turk
  Street; block 0540 is in the Western Addition and has no Turk Street frontage.
  The five consecutive rows 34-48, 50, 62-64, 66-74 and 76-80 carry lots 7, 8,
  9, 10 and 11, the first prints its block correctly as `340/7`, and the
  assessor's APNs for the site's published pages at those numbers are 0340007,
  0340008, 0340010 and 0340011. Resolve an inventory row against its neighbours
  and against the parcels the site already holds, never on its own.
- **The nine-digit reference numbers split at 2020, not at 2016.** The
  first run of the post-2016 group assumed none served a PDF because
  100008228 (the Timothy L. Pflueger House) returned a 1.6 KB PNG placeholder.
  A ranged request against all fifteen showed the seven certified 2017-2019
  serve `application/pdf` and all eight certified from 2020 on serve the
  placeholder (HTTP 206, `image/png` to a `-r 0-200` request). Test the whole
  group before generalising from one number.

- **Verified:** 2026-09-18 (tenth run. Two batches: **all 26 listings
  certified 2000-2009** apart from the Uptown Tenderloin district, and **all 14
  certified 2010-2015** — 40 nominations, every one with a usable text layer.
  **196 found, 169 resolved, 167 published on 33 pages, 6 of them seeded; 2
  declined, 27 unresolved.** Per batch: 2000-2009 131 found, 104 resolved, 103
  published on 19 pages (3 seeded); 2010-2015 65 found, 65 resolved, 64
  published on 14 pages (3 seeded). Five residencies went into
  `notable_residents` rather than the timeline — John C. Spencer, Constance de
  Young Tobin and Joseph O. Tobin, Julian R. Waybur, Nell Sinton and Benjamin
  H. Swig.

  What this run learned, beyond the cautions above:

  - **The 2000s nominations are about buildings the site already knew; what
    they add is the second layer.** Twenty-seven of the 33 pages existed, most
    already carrying a construction date and architect from a context
    statement. What survived the overlap scan was dated alterations, openings,
    occupants and events no statement had: the Bank of Italy's founding in the
    building that stood where the Colombo Building is (17 October 1904), the
    Superior Court and the Graft Prosecution in Temple Sherith Israel
    (1906-1908), the United Nations Charter negotiations in the Fairmont's
    penthouse, the Coit Tower lock-out of July 1934, the police firing on the
    Bayview Opera House on 28 September 1966, Diego Rivera's 1931 fresco and
    Ansel Adams's photography department at the Art Institute.
  - **The unresolved are all one of two things, and both are known holes.**
    Nine findings are on Port or Navy land EAS does not address with a parcel
    (the Central Embarcadero piers; the five Treasure Island and Yerba Buena
    Island listings, which give no street number at all). Fifteen more are
    condominium-mapped: the Coffin-Redington Building, whose second address
    300 Beale Street is unit 605 of live/work parcel 3747075, and the
    State Teachers' College campus at 55 Laguna Street — both wait on #228.
    The other three are the Hale Brothers warehouses at 423-429 Stevenson
    Street, which have no EAS record.
  - **The pages disagree with the NPS index about listing dates, and one
    source is the cause.** Colombo Building and North Beach Library pages
    carried National Register listings dated 2018; 700 7th Street carried
    1995 for Baker & Hamilton. Each is now a sentence in the page's
    `unknowns`. The 2018 dates are the North Beach context statement's own
    year — six entries share the pattern — and fixing them is a separate
    task, not this run's.
  - **Ask whether a building has a page by its parcel, not its address.** A
    pre-read `ls` for `*/mint-street/54`, `*/columbus-avenue/1` and
    `*/market-street/700` found nothing, and all three buildings had pages —
    under `mint-plaza/14`, `columbus-avenue/7` and `kearny-street/1`, the
    parcel's lowest number. Run the resolver before judging what the site
    already carries.
  - **A resident belongs in the panel, and a household's other members do not
    belong in `raw.text` either.** Residencies with a period were published
    as `notable_residents` rows. Three raw spans named a spouse or child who
    is not the notable figure (the Waybur and Burr houses); those names were
    redacted by hand and the spans carry `raw.note`.
  - Where this run stopped: the 2017-2019 listings, seven PDFs that fetch,
    are the next batch.)

- **Verified:** 2026-09-17 (ninth run. Two batches. First 89000319, the
  Southern Pacific Company Hospital Historic District (Elizabeth Krase, Page &
  Turnbull, 1988; certified 5 May 1989), the last unread district nomination of
  the 1980s — 16 pages, 22 findings, 21 resolved, 20 published on 2 pages, both
  seeded. Then **all 17 listings certified 1990-1999**, read in full — 135
  findings, 106 resolved, 105 published on 24 pages, 5 of them seeded; 1
  declined, 29 unresolved. Run total: **157 found, 127 resolved, 125
  published on 26 pages, 7 seeded.**

  What this run learned, beyond the cautions above:

  - **A campus district has one address and it may not exist.** 89000319 is
    titled 1400 Fell Street and EAS has no such address; the nearest numbers
    are 1380 and 1390, on the next block. What it does print is its own
    parcel — "Lots 2 and 3, City block 1206" — and those are exactly the two
    active parcels on that block, split in 1982, the year of the rehabilitation
    the nomination describes. Their lot areas sum to 2.51 acres against the
    stated 2.5. **Resolve a campus on the printed parcel and check it with the
    acreage**, not on the title address.
  - **The other half of that lesson is which parcel gets which building.** Lot
    3 is 333 Baker Street, six storeys and 158 units on the roll: the hospital,
    whose entrance the 1982-83 conversion moved off the monumental Fell Street
    stair round to the Baker Street portico. Lot 2 is 1500-1599 Hayes Street,
    four addresses on one point, carrying the four buildings along Hayes —
    powerhouse, paint shop, nurses' annex and Huntington Social Hall, of 1908,
    about 1923, 1907 and 1911. One roll year for four buildings is a
    `building.completed_conflict`, not four pages.
  - **The 1990s are Anne Bloomfield's and Page & Turnbull's decade, and the
    documents are long.** 97000348 (Hunter-Dulin) runs to 151,000 characters,
    most of it the architects' and engineer's biographies and a bank-merger
    history; the building's own story is about 200 lines. **Grep for the
    section headings first** — `SITE HISTORY`, `BUILDING HISTORY`, the
    property name repeated as a running head — and read those ranges.
  - **Three of the seventeen are on land EAS does not address**, and that is
    the whole reason 13 findings are unresolved: the Yerba Buena Island
    lighthouse (no number at all), Quarters 1 at 1 Whiting Way (EAS holds 15,
    20, 25, 50, 61, 71 and 81 Whiting Way on the island and no 1, and none of
    them carries a parcel number), and Pier One (The Embarcadero's numbering
    in EAS starts at 5 and there is no PIER street). Federal and Port land is
    a standing gap in this source, not a resolver failure.
  - **Two more give no address at all and still resolve, because they name the
    building standing over them.** The Apollo and Niantic storeships are buried
    hulls; 91000561 names "the former Federal Reserve Bank of San Francisco
    building" at Battery and Sacramento (parcel 0229003, 301-325 Battery
    Street) and 91000563 names the construction at Clay and Sansome in 1978
    (parcel 0207037, 505 Sansome Street, the tower whose foundations the dig
    was for). Both were resolved by hand. 91000561 contradicts itself about
    the corner — northwest in its heading, southwest in its description — and
    that disagreement is in the page's `unknowns`.
  - **A second stated address is worth putting in `extra.address_note_as_recorded`
    every time.** 97001189's own 855 Front Street has no EAS record; its
    second address, 101 Vallejo Street, does, and the resolver said so and
    left the call. The parcel's lot area, 5,064 sq ft, is within 22 sq ft of
    the 45 ft 10 in by 110 ft a city surveyor measured in 1861, and Planning's
    survey name for it is GIBB SANBORN WAREHOUSE. That is the strongest
    identification this source has produced.
  - **Condominium mapping cost this batch two whole buildings**, both of them
    conversions of the very buildings the nominations describe: 465 Tenth
    Street became 19 unit parcels in 1998 and 1489 Folsom Street 8 in 1993.
    Eleven findings are unresolved on that account, and the page that already
    exists at 1489 Folsom is one of the eight units — one of issue #228's
    twenty-nine.
  - **A bare 1906 sorts before 1906-04-18 on the rail**, so a reconstruction
    entry dated only to the year prints above the fire it followed. State the
    sequence in the description rather than reaching for a month the source
    does not give.
  - **99001265 is a supplier's building, and its section 8 lists nine
    buildings its product went into** — the lifts in the Pacific Telephone,
    Mark Hopkins, Brocklebank, Hunter-Dulin, Russ, Shell, Medical-Dental,
    Mills Tower and Lurie buildings were all assembled at 1 Beach Street.
    Those are facts about nine other parcels that only the nomination *about
    the supplier* states, so they were taken — while the storey counts,
    architects and dates that list also prints were left to the nominations
    about those buildings. Nine one-line findings on nine existing pages.
  - Where this run stopped: the 2000-2023 listings are the whole of what is
    left, and the post-2016 `_text` caution above should be tested before
    anyone plans that group.)

- **Verified:** 2026-09-16 (eighth run. Read the three Russian Hill district
  nominations Anne Bloomfield wrote for the Russian Hill Neighbors in May 1987,
  all in full: 87002286 Macondray Lane (20 pages, 19 resources), 87002288 Paris
  Block (15 pages, 12 resources) and 87002289 Vallejo Street Crest (41 pages, 46
  resources). **135 findings, 107 resolved, 102 published on 54 pages, 37 of
  them seeded; 5 declined, 28 unresolved.** Per document: Macondray Lane 28
  found, 17 resolved, 17 published on 11 pages; Paris Block 18, 16, 15 on 9;
  Vallejo Street Crest 89, 74, 70 on 34. 24 findings are a notable past
  resident or a notable owner's tenure, and 77 carry a named architect,
  builder, contractor, developer, engineer or mason. Two historic-district hubs were generated for the first time,
  Macondray Lane and Paris Block, once each had five documented buildings.

  What this run learned, beyond the cautions above:

  - **These nominations are older than the condominium conversions of their
    buildings, and the conversions cost more than OCR did.** Every printed
    block and lot was right — 92 exact matches and 15 re-lottings, none on
    another block — but the city has since split two-unit flats into a parcel
    per flat: 1918-1920 Jones Street in 1996, 58-66 Macondray Lane in 1999,
    1017-1019 Green Street, 19 Macondray Lane in 2009 and 72 Macondray Lane in
    2013 — and 900 Green Street (1989), 1050 Green Street, 1 Florence Street
    and the Hermitage at 1020 Vallejo Street are condominiums outright.
    `sf-parcels`' `date_rec_add` dates each split. They are 14 of the 28
    unresolved findings, and they took two notable residents with them:
    Charles Caldwell Dobie at 1918-1920 Jones and Maynard Dixon and Dorothea
    Lange's first cottage at 1 Florence Street. Those wait on #228.
  - **Section 7 and section 8 number the buildings differently.** In the
    Macondray Lane nomination they agree to no. 12 and then section 8 runs
    one ahead (Ryer's Apartments is no. 14 in section 7 and no. 15 in section
    8); the owners table follows section 7. Vallejo Street Crest's section 8
    prints "5 Russian Hill Place" for no. 23, which section 7 and the owners
    table give as 7. Key every row on its address and printed lot, never on
    its map number.
  - **Vallejo Street Crest's section 8 is a history, not an inventory
    appendix**, and most of its value is there: the Livermore family's
    building programme of 1912-1917, Worcester's 1888 cottages and the
    contract notice that attributes them, and seventeen named artists, writers
    and patrons, most placed at a number with a period. It contradicts itself
    once: Joseph Worcester's cottage is "site of No. 36" (1019 Vallejo) on
    page 15 and in the chronology, and 1030 Vallejo on the site of no. 37 on
    page 27. It was placed on neither.
  - **An environmental review document had already summarised this district**
    on eleven of its pages (`sf-environmental-review-noticeofavailabi2920sanf`),
    with looser dates — Farr's two houses "1906", Julia Morgan's cottage "after
    1906". Where that entry already carried the building, this run added the
    credit as a `building` spec row and the precise year as
    `building.completed` or a dated contract entry, not a second construction
    entry.
  - **Three credited names are printed wrong and published right**, each
    identified inside the document itself: "Oscar Kaupt" (spelled Haupt in
    the same entry, with his Altenheim credit), "L.B. Button Company" (the
    biography given is Llewellyn B. Dutton's) and "Bruce E. Reiser" (Heiser in
    the chronology). The printed form is kept in `extra.name_as_printed`.
  - **Owners who are the notable figure are taken** — Charles M. Fickert,
    Louis Feusier, Luigi DeMartini, Paul Verdier, Isabel Stine — and ordinary
    owners and clients are not. See the People table above and
    [LESSONS.md](../LESSONS.md).
  - **Green Street is the Russian Hill / Nob Hill line on these blocks**, and
    the resolver's nearest-page rule filed 1809 Taylor Street and 1025 Green
    Street across it; both were corrected by hand to the parcel's analysis
    neighborhood before seeding.
  - Where this run stopped: the Southern Pacific Company Hospital (89000319)
    is the only 1980s district nomination left, and is first in the queue
    above.)

- **Verified:** 2026-09-15 (seventh run. Read two of the five remaining
  1982-1989 district nominations in full: 82000983 Bush Street-Cottage Row (20
  residences, a walkway and a mini-park) and 83001230 Liberty Street (51
  buildings). 52 findings, 49 resolved, 49 published on 47 pages, 23 of them
  seeded — every resolved finding carries a named architect, builder,
  contractor or developer, except one dated event (Susan B. Anthony's 1896
  suffrage meeting at 159 Liberty Street, a notable past occupant under issue
  #310). 3 unresolved: 2117 Bush Street is a condominium today; 163 Liberty
  Street's two recorded numbers sit on different parcels now; 40-46 Liberty
  Street no longer exists as an address at all (nearest surviving numbers 20,
  21, 22, 23, 24, 25) and is left for a street-hub fact rather than a page.

  What this run learned, beyond the cautions above:

  - **This source's 1980s Bloomfield districts hit the roll's 1900 placeholder
    almost every time, and the fix is [LESSONS.md](../LESSONS.md)'s existing
    one: `building.completed_conflict`, not a reframe.** 33 of the 49 published
    facts — every one of the 18 Bush-Cottage credits but one, and 17 of
    Liberty's 31 — sit on a parcel whose `year_property_built` is 1900, 1902,
    1904 or 1907 against a nomination date of 1863-1913. `check.py --overlap`
    flags every one of them as "predates the building the assessor says is on
    the parcel", which is the right question and the wrong answer here: the
    nomination is describing the standing, still-photographed building in
    both cases, not a demolished one. Set `building.completed_conflict` and
    publish; do not decline or reframe the fact as being about a vanished
    predecessor.
  - **A per-building appendix is a poor source of unnamed credits and a good
    one for the named ones — read it for exactly the second.** Both districts
    are dense with owner-residents (their occupations, their tenancy years,
    sometimes their descendants), and none of that was taken. Liberty
    Street's appendix names an architect, builder or contractor on 29 of 51
    buildings; the other 22 have a construction date and nothing else citable,
    and were not extracted — a bare date with no credit and no notable
    occupant is not worth a finding of its own here, since `parcel.year_built`
    already carries a date (however unreliable) and the nomination's date adds
    only a disagreement, not a fact `building.completed_conflict` doesn't
    already carry more economically once one credited finding on the page has
    stated it.
  - **Two addresses in the Liberty Street appendix resolve to the same page as
    a neighbour and are not a resolver error.** 851 Guerrero Street (appendix
    #14) and 85 Liberty Street (#13) are one parcel, built by the same
    owner-builder back to back in 1924-1925; both facts belong on the one page
    at 85 Liberty Street, and the resolver placed them there correctly.

- **Verified:** 2026-09-15 (sixth run, targeted: issue #346, 08001407's section
  8 — the statement of significance — read end to end for the first time, all
  39 pages. It restates most of the section 7 inventory in prose, usually
  crediting the era's developer-owners rather than the architect section 7
  already names; per the dossier's People section that subsection is about
  owners, and none of its names were taken. About thirty address-bearing
  sentences were checked against the corpus and all but ten were already
  published. 10 findings: 7 new historical_record entries (650 Ellis Street's
  Japanese-American newspaper, 1923-1937; the Central Police Station at 64
  Eddy Street, gone from EAS today and left unresolved; the Poodle Dog's
  temporary post-earthquake stop at 824-826 Eddy, also gone from EAS; its
  1910-on home at 111 Mason Street; the Miles Brothers' pre-fire film exchange
  at 116 Turk Street, predating the surviving 1910 building; the Miles
  Brothers' 1911 relocation to 1145 Mission Street, which had no page and is
  now seeded; and the 1903 wood-flats building at 493-499 Eddy Street that
  preceded the Adrian Hotel), 2 recorded conflicts (868 and 724 Geary Street,
  where section 8's own construction dates disagree with the already-published
  inventory rows — recorded in each page's `unknowns`, not adjudicated), and 1
  duplicate declined (the Black Cat at 48-98 Mason Street is already published
  from a different source). 2 of the 7 new facts have no EAS record for the
  number as printed and stay unresolved, per the evidence bar, rather than
  forced onto the street hub or a neighbor's page.

  What this run learned, beyond the cautions above:

  - **The PROPERTY OWNERS subsection is exactly what its name says, and it is
    dense with dated construction facts anyway.** A dozen buildings get a
    year and an owner's name in the same sentence, but section 7's inventory
    already carries the correct architect for every one of them — Klimm
    Apartments were designed by Salfield and Kohlberg, not built by Klimm the
    plumbing contractor whose name the building keeps. Checking each sentence
    against the corpus before extracting is what kept this batch to ten
    findings instead of thirty.
  - **A conflict runs in either direction.** The #310 run recorded section 8
    disagreeing with an already-published section 7 fact (Howard's death
    address). This run found the reverse is just as common — 868 and 724
    Geary Street's construction dates are section 8 against section 7, this
    time with section 8 the newer, unpublished claim. Same handling: the
    inventory row is what stays published, the disagreement goes in
    `unknowns`, and nothing is adjudicated.
  - **A resolved address can still conflict with a resolved date.** 111 Mason
    Street's Poodle Dog placement ("by 1910") resolves cleanly to a real
    parcel, but that parcel's own inventory row dates the standing building to
    1914 — a conflict inside a single finding, not between two sources, and
    the finding stayed `resolved` with a `conflict` field rather than being
    forced into `unresolved`.

- **Verified:** 2026-09-13 (fifth run, targeted: issue #310, the people the
  fourth run left on the table. Re-swept all 477 section 7 inventory rows of
  08001407 for a person in the prose tail. **Eleven rows carry one; nine are
  published, on nine pages, none of them new.** The two that are not: 366-394
  Eddy Street, where the sentence is about the building's own owner, and
  161-165 Turk Street, whose tail names a former tenant's record shop by its
  proprietor and gives no date.

  The decision itself is recorded under People above and is now in both
  rulebooks: **a notable past occupant a published source already covers is
  always taken.** A run does not file that as a question again.

  What this run learned, beyond the decision:

  - **The fourth run's count was of sentences, not of people, and it was
    wrong in both directions.** It reported twelve rows and listed seven names.
    Eleven rows carry a person, and two of the nine publishable ones had never
    been listed at all: John Galen Howard, whose clause ends without a full
    stop, and Isadora Duncan, who is inside the `signs:` field rather than in a
    tail. *A sweep for people greps for people — `lived`, `home of`, `died`,
    `born`, `tenant:`, `plaque`, `ran a` — not for sentence shape.*
  - **The document contradicts itself about an address, across sections.**
    Section 8 puts John Galen Howard's death at 227-231 **Eddy** Street; the
    section 7 inventory puts it at 227-231 **Ellis**, and there is no 227-231
    Eddy row in the inventory at all. Published on the inventory row, with the
    disagreement in that page's `unknowns`. Section 8 is also where the
    Cadillac Hotel's address reads correctly as 366-394 Eddy Street, which is
    what the inventory's OCR'd "566-394" is.
  - **Two names are printed wrong and both are published right**: "Fritz
    Lieber" for Leiber and "Miriam Alien de Ford" for Allen, each consistent
    across section 7 and section 8. The printed spelling is kept in
    `extra.name_as_printed` and stated in the page's `notable_residents`
    detail, because the name is the fact here and shipping a misspelling of a
    real writer would be the error the LESSONS rule about credited names is
    guarding against — that rule's "fix only where the document spells it
    correctly elsewhere" is about an OCR singleton among repeats, not about a
    name the world spells one way.
  - **`notable_residents` renders, and `check.py` did not know it.** The tool
    rejected an undated published finding unless its `publish.note` named a
    spec row or the survey block; the residents panel is a third home that
    carries no year by design, and it now counts. Dashiell Hammett is the
    entry that found it.)

- **Verified:** 2026-09-11 (fourth run. Read the Uptown Tenderloin Historic
  District inventory (08001407) in full under #304 — 477 rows, 480 findings, 463
  resolved, 451 published across 414 pages, 194 of them created by this run's
  seeding of 199 parcels. The densest single document in this source: 308 of its
  findings name an architect.

  What this run learned, beyond the cautions above:

  - **The block column's OCR fails systematically, which is what makes it safe.**
    85 rows disagreed with the parcel their address resolves to, and 84 were one
    substitution: a leading 3 read as 5, dropped, or read as `H` in "31" or as
    `$`. The 85th — 800-806 O'Farrell, printed `520/14` — is the document's own
    filing error, and it stood out because parcel 0520014 is 1780 Filbert Street
    in the Marina. Resolve on the EAS address join and audit the printed block
    afterwards; the residue is the part to read by hand.
  - **The 73 conflicts the resolver recorded are that artefact, not a
    disagreement in the record**, so none of them was written to a page's
    `unknowns`. The seven `unknowns` sentences this run did write are all the
    other kind: the assessor's year against the nomination's.
  - **A parenthesised name is a later name.** 71 rows lead with one, and the year
    in the bracket is when that name was current — 134-144 Eddy Street is dated
    1907 and its first name is "Langham Hotel (1911)".
  - **People are in the prose tail, not the fields.** Twelve rows end with a
    sentence naming a notable past resident: Dashiell Hammett at 620 Eddy Street
    when he began writing, Frank Capra at 233-237 Eddy in 1921, Fritz Leiber at
    807-815 Geary 1969-1977, Miriam Allen de Ford at 35-65 Mason 1936-1975, Sally
    Stanford at 791-793 O'Farrell in 1931, and Jessie Hayman and Tessie Wall,
    whom the nomination cites to Gentry 1964. **None was taken.** All are dead
    and documented, which is the case the root AGENTS.md's `notable_residents`
    carve-out is written for, while this module's rulebook and #304 both say to
    leave residents — a real ambiguity, and publishing seven of them inside a
    450-fact batch is not a call this run should make. It is the one piece of
    08001407 deliberately left on the table, and it wants a person's decision.
  - **Five seeded pages carry no fact from this document**: 555-561 Ellis, 54
    McAllister, 131-153 Taylor, 421-425 Turk and 430-440 Turk, whose only finding
    is dated "built after 1984" or "ca. 2000" and was declined for having no date
    the timeline can order. They are ordinary DataSF pages, not empty ones.
  - **`pdftotext -layout` is not a fix here.** The committed `.txt` was
    re-extracted to test whether the collapsed columns were an extraction fault;
    it came back byte-identical at 451,531 characters. The damage is in the scan.)

- **Verified:** 2026-09-09 (third run, targeted. Fetched the Uptown Tenderloin
  Historic District nomination (08001407) and read its section 7 inventory only
  for the theatre addresses named in issue #302 — one row of roughly four
  hundred. One of the fifteen theatre parcels in that issue falls inside the
  district: 76-80 Turk Street, recorded as the Gaiety Theater, stores and a loft
  converted to a theatre in 1922 by the architect Earl B. Bertz. 2 findings, 2
  resolved, 1 published; the second is an alteration the nomination dates only
  as "after 1990s", declined because the page's one timeline is date-ordered.
  The document's remaining ~400 inventory rows are unread and are filed as
  issue #304. Three further theatre buildings were seen while searching it and are
  named in #304: 814-820 Larkin Street, 35-65 Mason Street and 156 Eddy
  Street. Both new cautions above — the guessed reference number and the OCR'd
  block column — cost this run time and are the reason it is worth a Verified
  line of its own.)

- **Verified:** 2026-09-06 (second run. Read the Civic Center district
  nomination (78000757) and the 37 single-building nominations among the 42
  listings certified 1980-1989 — 38 documents, 77 findings, 71 resolved, 53
  published on 34 pages, 10 of them seeded by this run. The five district
  nominations in the same date range are fetched, extracted and unread; they
  are the next batch and the reason for the new caution above about what a
  district nomination is.

  What this run learned, beyond the cautions above:

  - **The era-as-batch rule from the first run held, and the form is why.**
    Every 1980s listing is on the 10-900 form and 33 of the 37 single-building
    ones fill in both `SPECIFIC DATES` and `BUILDER/ARCHITECT`. Two documents
    give no street number at all — 86000207, addressed by the block it stands
    on, and 01000281 at Fort Mason — and one vessel, 86000089, is not a
    building.
  - **Splitting the districts out of the era was the right call and should be
    the default.** A single-building nomination is two or three findings; one
    of Bloomfield's districts is fifty. Mixing them makes a batch whose size
    nobody can estimate from its name.
  - **The declines are the measure of how well the site already covers this
    source's subjects.** 18 of the 71 resolved findings were declined as
    duplicates, almost all of them a construction date and an architect a
    citywide context statement had already put on the page. What survived was
    the second layer: dated alterations, opening dates, costs, contractors, and
    the two events of national record in the Civic Center — the signing of the
    United Nations Charter and of the peace treaty with Japan — which no source
    already on those pages carried.
  - **Nine conflicts were recorded and none adjudicated**, four of them a
    disagreement with the assessor's 1900 placeholder and the rest genuine
    disagreements between this source and a Planning Department document: 1915
    against 1916-17 for the State Building competition, 1956 against 1951 for
    the remodelling of the Supreme Court room, 1922 against 1923 for the Paige
    Motor Car Company extension, and 1906 against 1913 for St Joseph's rectory.)

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
    page's `unknowns` rather than adjudicated, which is what the rule requires
    and also the honest reading — the assessor's 1900 is a placeholder, but
    saying so would be adjudicating.
  - **A "status index" lead can be a document source.** This was ranked first on
    the leads table for three weeks on the strength of a triage sample and never
    promoted. It should have been promoted the day it was triaged.)
