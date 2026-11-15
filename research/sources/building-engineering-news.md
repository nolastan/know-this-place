# building-engineering-news — *Building and Engineering News* (primary)

> **Research dossier.** Rules: [../AGENTS.md](../AGENTS.md) · traps:
> [../LESSONS.md](../LESSONS.md) · register:
> [../SOURCES.md](../SOURCES.md) · cited on pages by the source id `building-engineering-news`.
>
> - **Kind:** journal OCR · **Tier:** primary · **Status:** open
> - **Search-invisibility:** high — see the register for what that rates.
> - **Coverage:** 31 of 34 half-year volumes read (vol. 16 pt. 2 to vol. 31, July 1916 – January 1932, the end of the run): 5,845 facts on 5,455 page writes (3,220 pages seeded). Resume backwards at the first 1916 volume (`buildingengineer1616cont`; the July to December 1919 item is `buildingengine1921919cont`, whose id breaks the pattern; find item ids with the Internet Archive search `buildingengineer*cont`). See the `Verified:` line.
> - **Local corpus:** `research/corpora/building-engineering-news/`
> - **Claimed:** every unread volume, by the project run that opened this source (Stan, since 2026-11-14). The 8,043 placed-and-held rows are **not** claimed: Stan decided on 2026-11-14 that they stay logged and unpublished until another fact gives the parcel a page, and whoever seeds that page takes them up after reading each against the page image (`check.py --held <manifest>`; [AGENTS.md](../AGENTS.md#facts-held-for-a-page)). `check.py --held pages` lists those whose parcel already has a page. The 105 found on 2026-11-15 were each read against the page image or judged from the listing: 72 were published and 33 stay held, each with the reason in its note (the roll disagrees with the listing, several houses on one listing, a repeat of a published record, an address outside San Francisco); any others it lists are overdue.
>
> Update this dossier at the end of every pass — the `Verified:` line, the
> coverage note, and anything the pass learned about getting at the source.

- **What:** *Building and Engineering News*, a San Francisco weekly for the
  building trades (published Saturdays), scanned by the San Francisco Public
  Library. Each issue prints, for San Francisco County and separately for
  Alameda County, the week's **building permit applications** and recorded
  **building contracts** as numbered entries: where the lot is, what is to be
  built (storeys, material, use, number of flats or apartments), the owner, the
  architect, the contractor and the cost. Contracts add the lot dimensions, the
  filing date, the payment schedule, the total and the sureties. It is the
  permit record for the years before the city's own permit data begins.
- **Where:** Internet Archive, identifiers `buildingengineer<vv><pp>cont`: 34
  half-year volumes, vol. 15 (1915) to vol. 31 (January 1932);
  `buildingengineer2616cont` is vol. 26 pt. 1. A reader is given
  `https://archive.org/details/<id>/page/n<index>/mode/1up`, where `<index>` is
  the zero-based page index of `<id>_djvu.xml`. **That is one less than the
  number in the jp2 file name**: the reader hides scan leaf 0, so
  `<id>_0145.jp2` is `n144`.
- **How to get at it:** `https://archive.org/download/<id>/<id>_djvu.xml`
  (about 90 MB a volume) for the text with word boxes; the plain `_djvu.txt`
  loses the columns. Page images for checking:
  `https://archive.org/download/<id>/<id>_jp2.zip/<id>_jp2%2F<id>_<NNNN>.jp2`,
  one request a page, a second or two each. The IIIF crop endpoint works and
  takes about 25 seconds a crop, so download the page and crop locally. The
  djvu.xml word boxes are in jp2 pixels.
- **What is actually usable:** the numbered entries under BUILDING PERMIT
  APPLICATIONS and BUILDING CONTRACTS. A real one:
  `(1167) E BRODERICK 87-6 S North Point. 3-story and basement frame (2) flats. Owner — … Architect — … Contractor — … $8000`
  — the east line of Broderick, 87 feet 6 inches south of North Point. New
  work never carries a street number; alterations usually do (`NO. 2221
  LARKIN`). A tract entry lists several offsets and is one building each
  (`W 20TH AVE 100, 125, 150 … S Vicente. Six one-story frame dwellings`).
  Not taken: completion notices and liens (people, not buildings),
  sub-contracts printed "on above", and the news columns, which place a job
  only "near" a street.
- **Method that worked (vol. 26 pt. 1):** split the OCR into entries on the
  numbers; keep the San Francisco ones (the Alameda County lists run in the
  same numbered series and name the city after the location, so test the
  heading only, with the street-type context: San Francisco has streets named
  Sacramento, Stockton, San Jose and Alameda); read the location line; build
  the lot from the block corner on the DPW centrelines against the sf-parcels
  shapes; accept where the lot starts within two feet of a lot line of today
  and the roll dates the building 1925–1928. Then **read every row to be
  published against the page image**, on contact sheets that put the image
  crop beside the parsed row. The parsed location was right on 384 of 385
  rows; the wording was not: about 160 needed a name, a cost or the
  description corrected.
- **Cautions:**
  - Costs lose or gain a digit in the OCR ($6,000 read as $16,000, $2,500 as
    $250), and a contract's total can be checked against its payment
    schedule, which is how four wrong totals were caught.
  - Entries run together where the next entry's number is garbled or the
    entry crosses a column or page break; the tail of one entry then carries
    the architect and cost of the next.
  - The running head misprints the year on some pages; take the year from the
    volume.
  - Corners on the diagonal streets (Market, Columbus, Cervantes) use compass
    words by convention and cannot be placed by geometry.
  - The same job is often listed twice: a permit and a contract in the same or
    a later issue, or a repeat listing. One page entry per dated event.
  - The paper spells names inconsistently (Erlendsen and Erlendson, De
    Martini and DeMartini). Names are given as printed in that entry.
  - Sub-trade contracts (plumbing, glass, roof tile, excavation) name a
    contractor who is not the building's builder: they go on the timeline and
    not into `building.builder`.
- **People:** architects, designers, engineers, contractors and firms are
  published. **Owners are private individuals and are never published**, and
  are cut from `raw.text`; a firm or institution named as owner (a company, a
  church, a club) is kept. Sureties are private individuals and are cut. An
  owner printed again as contractor, architect or designer (the same person,
  or the same surname at the owner's address) is cut with the owner; a firm
  is kept. The first volumes read (1926 and early 1927) had kept those names
  and were brought into line on 2026-11-15: 32 names cut, with the credits
  that rested on them (`cut_owner_trade.py` in the pipeline folder).
- **Citation label:** "Building and Engineering News, 23 January 1926", with
  the page link. Page source ids are
  `building-engineering-news-<issue date>-n<index>`.
- **Coverage:** vol. 26 pt. 1 (26 issues, 2 January – 26 June 1926), permits
  and contracts only. 4,373 numbered entries; 2,404 San Francisco rows; 1,610
  placed on a parcel; 385 picked (page exists, or an architect is named, or
  the building is flats, apartments or commercial) and read against the image;
  368 published on 345 pages, 242 of them seeded. Unread: the other 33
  volumes. Unfinished in this volume: 543 placed single houses held until the parcel gets a page, 682 rows with a nearest parcel not accepted, 794 not
  placed (354 unparsed location lines, 245 street pairs that do not cross
  under the names read, 160 street numbers with no EAS row).
- **Coverage, vol. 26 pt. 2** (`buildingengineer226cont`, 3 July – 31 December
  1926): 3,765 numbered entries; 2,264 San Francisco rows; 1,318 placed on a
  parcel; 306 picked and read against the image; 290 published on 282 pages,
  186 of them seeded. Unfinished: 425 placed single houses held until the parcel gets a page, 586 rows with a nearest parcel not accepted, 946 not
  placed. Unread: the other 32 volumes.
- **Coverage, vol. 27 pt. 1** (`buildingengineer227cont`, 8 January – 25 June
  1927): 3,479 numbered entries; 2,165 San Francisco rows; 1,343 placed on a
  parcel; 358 picked and read against the image; 345 published on 336 pages,
  240 of them seeded. Unfinished: 449 placed single houses held until the parcel gets a page, 536 rows with a nearest parcel not accepted, 822 not
  placed. Unread: the other 31 volumes.
- **Coverage, vol. 27 pt. 2** (`buildingengineer2127cont`, 2 July – 31
  December 1927): 2,777 numbered entries; 1,858 San Francisco rows; 1,336
  placed on a parcel; 318 picked and read against the image; 304 published on
  284 pages, 201 of them seeded. Unfinished: 421 placed single houses held until the parcel gets a page, 597 rows with a nearest parcel not accepted,
  522 not placed. Unread: the other 30 volumes.
- **Coverage, vol. 28 pt. 1** (`buildingengineer2828cont`, 7 January – 30 June
  1928): 2,542 numbered entries; 1,741 San Francisco rows; 1,098 placed on a
  parcel; 276 picked and read against the image; 269 published on 247 pages,
  166 of them seeded. Unfinished: 376 placed single houses held until the parcel gets a page, 446 rows with a nearest parcel not accepted, 643 not
  placed. Unread: the other 29 volumes.
- **Coverage, vol. 28 pt. 2** (`buildingengineer28128cont`, 7 July – 29
  December 1928): 2,133 numbered entries; 1,335 San Francisco rows; 821 placed
  on a parcel; 200 picked and read against the image; 186 published on 171
  pages, 94 of them seeded. Unfinished: 284 placed single houses held until the parcel gets a page, 337 rows with a nearest parcel not accepted, 514
  not placed. Unread: the other 28 volumes.
- **Coverage, vol. 29 pt. 1** (`buildingengineer2929cont`, 5 January – 29
  June 1929): 1,935 numbered entries; 1,086 San Francisco rows; 627 placed on
  a parcel; 160 picked and read against the image; 151 published on 147
  pages, 77 of them seeded. Unfinished: 203 placed single houses held until the parcel gets a page, 264 rows with a nearest parcel not accepted, 459
  not placed. Unread: the other 27 volumes.
- **Coverage, vol. 29 pt. 2** (`buildingengineer29229cont`, 6 July – 28
  December 1929): 1,653 numbered entries; 944 San Francisco rows; 561 placed
  on a parcel; 135 picked and read against the image; 122 published on 118
  pages, 54 of them seeded. Unfinished: 155 placed single houses held until the parcel gets a page, 271 rows with a nearest parcel not accepted, 383
  not placed. Unread: the other 26 volumes.
- **Coverage, vol. 30 pt. 1** (`buildingengineer3030cont`, 4 January – 28
  June 1930): 1,776 numbered entries; 980 San Francisco rows; 569 placed on a
  parcel; 121 picked and read against the image; 112 published on 104 pages,
  43 of them seeded. Unfinished: 184 placed single houses held until the parcel gets a page, 264 rows with a nearest parcel not accepted, 411 not
  placed. Unread: the other 25 volumes.
- **Coverage, vol. 30 pt. 2** (`buildingengineer30230cont`, 5 July – 27
  December 1930): 1,529 numbered entries; 991 San Francisco rows; 500 placed
  on a parcel; 110 picked and read against the image; 99 published on 96
  pages, 44 of them seeded. Unfinished: 156 placed single houses held until the parcel gets a page, 234 rows with a nearest parcel not accepted, 491
  not placed. Unread: the other 24 volumes.
- **Coverage, vol. 31 pt. 1** (`buildingengineer3131cont`, 3 January – 27
  June 1931): 1,610 numbered entries; 1,033 San Francisco rows; 571 placed
  on a parcel; 122 picked and read against the image; 83 published on 79
  pages, 34 of them seeded. Unfinished: 218 placed single houses held until the parcel gets a page, 35 row-of-houses permits held at the image, 231
  rows with a nearest parcel not accepted, 462 not placed. Unread: the other
  23 volumes.
- **Coverage, vol. 31 pt. 2** (`buildingengineer31232cont`, 4 July 1931 – 9
  January 1932, the last issue held): 1,542 numbered entries; 1,054 San
  Francisco rows; 561 placed on a parcel; 100 picked and read against the
  image; 92 published on 90 pages, 42 of them seeded. Unfinished: 216 placed
  single houses held until the parcel gets a page (15 are row-of-houses
  permits), 245 rows with a nearest parcel not accepted, 493 not placed.
  Unread: the 22 volumes before 1926.
- **Coverage, vol. 25 pt. 2** (`buildingengineer2525cont`, 4 July – 26
  December 1925): 4,526 numbered entries; 2,382 San Francisco rows; 1,480
  placed on a parcel; 360 picked and read against the image; 331 published
  on 312 pages, 203 of them seeded. Unfinished: 551 placed single houses held until the parcel gets a page (35 are row-of-houses permits), 569 rows
  with a nearest parcel not accepted, 902 not placed. Unread: the 21 volumes
  before July 1925.
- **Coverage, vol. 25 pt. 1** (`buildingengineer255cont`, 3 January – 27
  June 1925): 5,484 numbered entries; 2,891 San Francisco rows; 1,931
  placed on a parcel; 505 picked and read against the image; 467 published
  on 446 pages, 292 of them seeded. Unfinished: 670 placed single houses held until the parcel gets a page (63 are row-of-houses permits), 756 rows
  with a nearest parcel not accepted, 960 not placed. Unread: the 20 volumes
  before 1925.
- **Coverage, vol. 24 pt. 1** (`buildingengineer244cont`, 5 January – 28
  June 1924): 4,505 numbered entries; 2,513 San Francisco rows; 1,479
  placed on a parcel; 368 picked and read against the image; 306 published
  on 288 pages, 195 of them seeded. Unfinished: 523 placed single houses held
  until the parcel gets a page (46 are row-of-houses permits), 599 rows with
  a nearest parcel not accepted, 1,034 not placed. Unread: the 18 volumes
  before 1924.
- **Coverage, vol. 23 pt. 2** (`buildingengineer2193cont`, 7 July – 29
  December 1923): 3,875 numbered entries; 1,982 San Francisco rows; 1,188
  placed on a parcel; 355 picked and read against the image; 269 published
  on 252 pages, 168 of them seeded. Unfinished: 359 placed single houses held
  until the parcel gets a page (39 are row-of-houses permits), 481 rows with
  a nearest parcel not accepted, 793 not placed. Unread: the 17 volumes
  before July 1923.
- **Coverage, vol. 16 pt. 2** (`buildingengineer16916cont`, 5 July – 27
  December 1916): 1,866 numbered entries; 1,045 San Francisco rows; 536
  placed on a parcel; 128 picked and read against the image; 90 published
  on 82 pages, 35 of them seeded. Unfinished: 141 placed single houses held
  until the parcel gets a page, 276 rows with a nearest parcel not
  accepted, 509 not placed. Unread: the 3 volumes before July 1916.
- **Coverage, vol. 17 pt. 1** (`buildingengineer1717cont`, 3 January – 27
  June 1917): 2,013 numbered entries; 1,147 San Francisco rows; 570
  placed on a parcel; 136 picked and read against the image; 103 published
  on 98 pages, 50 of them seeded. Unfinished: 116 placed single houses held
  until the parcel gets a page, 319 rows with a nearest parcel not
  accepted, 577 not placed. Unread: the 4 volumes before 1917.
- **Coverage, vol. 17 pt. 2** (`buildingengineer1727cont`, 4 July – 26
  December 1917): 1,938 numbered entries; 1,054 San Francisco rows; 588
  placed on a parcel; 180 picked and read against the image; 123 published
  on 106 pages, 47 of them seeded. Unfinished: 85 placed single houses held
  until the parcel gets a page, 325 rows with a nearest parcel not
  accepted, 466 not placed. Unread: the 5 volumes before July 1917.
- **Coverage, vol. 18 pt. 1** (`buildingengineer1818cont`, 2 January – 26
  June 1918): 1,720 numbered entries (about 1,100 items, most printed
  twice); 986 San Francisco rows; 485 placed on a parcel; 103 picked and
  read against the image; 70 published on 66 pages, 31 of them seeded.
  Unfinished: 82 placed single houses held until the parcel gets a page,
  303 rows with a nearest parcel not accepted, 501 not placed. Unread:
  the 6 volumes before 1918.
- **Coverage, vol. 18 pt. 2** (`buildingengineer1828cont`, 3 July – 25
  December 1918): 1,264 numbered entries; 561 San Francisco rows; 216
  placed on a parcel; 53 picked and read against the image; 36 published
  on 34 pages, 11 of them seeded. Unfinished: 31 placed single houses held
  until the parcel gets a page, 133 rows with a nearest parcel not
  accepted, 345 not placed, one contract on a parcel with no address row.
  Unread: the 7 volumes before July 1918.
- **Coverage, vol. 19 pt. 1** (`buildingengineer1919cont`, 1 January – 25
  June 1919): 1,992 numbered entries; 1,115 San Francisco rows; 535
  placed on a parcel; 134 picked and read against the image; 98 published
  on 90 pages, 27 of them seeded. Unfinished: 109 placed single houses held
  until the parcel gets a page (6 are row-of-houses permits), 293 rows with
  a nearest parcel not accepted, 580 not placed, one contract on a parcel
  with no address row. Unread: the 8 volumes before 1919.
- **Coverage, vol. 19 pt. 2** (`buildingengine1921919cont`, 2 July – 31
  December 1919): 2,706 numbered entries; 1,475 San Francisco rows; 802
  placed on a parcel; 195 picked and read against the image; 119 published
  on 112 pages, 48 of them seeded. Unfinished: 154 placed single houses held
  until the parcel gets a page (7 are row-of-houses permits), 455 rows with
  a nearest parcel not accepted, 673 not placed. Unread: the 9 volumes
  before July 1919.
- **Coverage, vol. 20 pt. 1** (`buildingengineer2020cont`, 7 January – 30
  June 1920): 2,017 numbered entries; 1,282 San Francisco rows; 601
  placed on a parcel; 148 picked and read against the image; 116 published
  on 106 pages, 45 of them seeded. Unfinished: 123 placed single houses held
  until the parcel gets a page (14 are row-of-houses permits), 331 rows with
  a nearest parcel not accepted, 681 not placed. Unread: the 10 volumes
  before 1920.
- **Verified:** 2026-11-15 (vol. 16 pt. 2: read 1,866 entries, found 1,045
  San Francisco rows, resolved 90, published 90 on 82 pages. Learned:
  the second 1916 volume runs through `vol1.sh` and `extract.py` as it
  is, but set `issues.json` by hand from the cover lines (every
  Wednesday, 5 July to 27 December; item numbers run from about 1,574
  to 3,641); `extract.py` reads few contractor fields here ("Contractor.
  ." with two dots), so the generated sentences lack them and each one
  is written from the image; a builder's own company at the builder's
  home address as owner (day's work, no other name) is left unnamed; a
  "dwelling" permit for a few hundred dollars on a lot the roll dates
  later sets no builder credit; a held fact of the same volume can sit
  on a page this volume seeds, so run `check.py --held pages` after
  publishing.)
- **Coverage, vol. 20 pt. 2** (`buildingengineer2010cont`, 7 July – 25
  December 1920): 2,156 numbered entries; 1,064 San Francisco rows; 535
  placed on a parcel; 119 picked and read against the image; 88 published
  on 81 pages, 29 of them seeded. Unfinished: 111 placed single houses held
  until the parcel gets a page (10 are row-of-houses permits), 309 rows with
  a nearest parcel not accepted, 529 not placed. Unread: the 11 volumes
  before July 1920.
- **Verified:** 2026-11-15 (vol. 20 pt. 2: read 2,156 entries, found 1,064
  San Francisco rows, resolved 88, published 88 on 81 pages. Learned:
  the paper came out on Wednesdays until 8 September 1920, so redate.py
  now takes a Wednesday where the running head says so; where the permit
  and the recorded contract name different builders (530 Taylor Street)
  both are kept and the builder credit is not set; two held facts were
  taken up on pages seeded here.)
- **Coverage, vol. 21 pt. 1** (`buildingengineer21119cont`, 1 January – 25
  June 1921): 2,803 numbered entries; 1,322 San Francisco rows; 570
  placed on a parcel; 179 picked and read against the image; 134 published
  on 126 pages, 53 of them seeded. Unfinished: 123 placed single houses held
  until the parcel gets a page (15 are row-of-houses permits), 270 rows with
  a nearest parcel not accepted, 752 not placed. Unread: the 12 volumes
  before 1921.
- **Verified:** 2026-11-15 (vol. 21 pt. 1: read 2,803 entries, found 1,322
  San Francisco rows, resolved 134, published 134 on 126 pages. Learned:
  a bare "Sixth" in a heading can be the avenue (the owner's address on a
  repeat listing gave it away), so an alteration by number alone stays
  held; where two permits a year apart sit on one lot (4726 Fulton Street)
  both are kept and the builder credit is not set; one held fact was taken
  up on a page that already existed.)
- **Coverage, vol. 21 pt. 2** (`buildingengineer2921cont`, 2 July – 31
  December 1921): 3,117 numbered entries; 1,553 San Francisco rows; 759
  placed on a parcel; 217 picked and read against the image; 165 published
  on 151 pages, 82 of them seeded. Unfinished: 178 placed single houses held
  until the parcel gets a page (31 are row-of-houses permits), 365 rows with
  a nearest parcel not accepted, 794 not placed. Unread: the 13 volumes
  before July 1921.
- **Verified:** 2026-11-15 (vol. 21 pt. 2: read 3,117 entries, found 1,553
  San Francisco rows, resolved 165, published 165 on 151 pages. Learned:
  an entry at the foot of a column can finish on the next page, so read
  that page before leaving a name or cost out; a store listed as one
  storey against two on the roll is held back even where three listings
  agree; five held facts were taken up on pages that already existed.)
- **Coverage, vol. 22 pt. 1** (`buildingengineer222cont`, 7 January – 24
  June 1922): 2,677 numbered entries; 1,596 San Francisco rows; 614
  placed on a parcel; 201 picked and read against the image; 158 published
  on 152 pages, 95 of them seeded. Unfinished: 172 placed single houses held
  until the parcel gets a page (9 are row-of-houses permits), 249 rows with
  a nearest parcel not accepted, 982 not placed. Unread: the 14 volumes
  before 1922.
- **Verified:** 2026-11-15 (vol. 22 pt. 1: read 2,677 entries, found 1,596
  San Francisco rows, resolved 158, published 158 on 152 pages. Learned:
  the OCR item number can be a thousand off (3136 for 2136), so check it
  against its neighbours; a permit can name a second architect the page
  does not carry (300 Page Street: Julia Morgan and Dorothy Wormser); three
  held facts were taken up on pages that already existed.)
- **Coverage, vol. 22 pt. 2** (`buildingengineer2222cont`, 1 July – 30
  December 1922): 2,782 numbered entries; 1,519 San Francisco rows; 733
  placed on a parcel; 211 picked and read against the image; 174 published
  on 159 pages, 89 of them seeded. Unfinished: 210 placed single houses held
  until the parcel gets a page (22 are row-of-houses permits), 317 rows with
  a nearest parcel not accepted, 786 not placed. Unread: the 15 volumes
  before July 1922.
- **Verified:** 2026-11-15 (vol. 22 pt. 2: read 2,782 entries, found 1,519
  San Francisco rows, resolved 174, published 174 on 159 pages. Learned:
  the same contract can be printed again two issues later, so before taking
  up a held contract compare it with what the page already carries; a
  permit and a later contract can name different builders (3120 Jackson:
  the page keeps the permit's); a fact for a whole building is not put on a
  condominium unit page when the building has no page of its own; five held
  facts were taken up when this volume seeded their pages.)
- **Coverage, vol. 23 pt. 1** (`buildingengineer233cont`, 6 January – 30
  June 1923): 4,231 numbered entries; 2,260 San Francisco rows; 1,238
  placed on a parcel; 355 picked and read against the image; 272 published
  on 254 pages, 175 of them seeded. Unfinished: 364 placed single houses held
  until the parcel gets a page (54 are row-of-houses permits), 532 rows with
  a nearest parcel not accepted, 1,022 not placed. Unread: the 16 volumes
  before 1923.
- **Verified:** 2026-11-15 (vol. 23 pt. 1: read 4,231 entries, found 2,260
  San Francisco rows, resolved 272, published 272 on 254 pages. Learned:
  select.py's row-of-houses test misses headings that spell 'dwlgs' or put
  the count on a second line, so check for them on the sheets; an owner's
  address printed in one volume can show that a contractor in another is the
  owner's own firm (Kiernan & O'Brien was cut from a July 1923 permit on
  that evidence); one held fact (650 34th Avenue, July 1923) was taken up
  when this volume seeded its page.)
- **Verified:** 2026-11-15 (vol. 23 pt. 2: read 3,875 entries, found 1,982
  San Francisco rows, resolved 269, published 269 on 252 pages. Learned: an
  alteration listed by lot line rather than street number is held unless the
  owner's printed address or an unmistakable use confirms the building; one
  held fact (1538 Green Street, 1927) was taken up when this volume seeded
  its page, and the permit printed beside it stays unpublished because it
  calls the six-unit building a dwelling.)
- **Verified:** 2026-11-15 (vol. 24 pt. 1: read 4,505 entries, found 2,513
  San Francisco rows, resolved 306, published 306 on 288 pages. Learned: Stan
  confirmed on 2026-11-15 that an owner printed again as architect or
  contractor stays off the page, tradesmen and speculative builders included,
  and a two-name partnership or family firm at the owner's own address is
  treated the same way; a permit for a foundation or an excavation sets no
  builder credit; one held fact (431 Gennessee Street, 1931) was taken up
  when this volume seeded its page.)
- **Coverage, vol. 24 pt. 2** (`buildingengineer24219cont`, 5 July – 27
  December 1924): 3,858 numbered entries; 1,969 San Francisco rows; 1,073
  placed on a parcel; 269 picked and read against the image; 228 published
  on 212 pages, 122 of them seeded. Unfinished: 387 placed single houses held
  until the parcel gets a page (32 are row-of-houses permits), 424 rows with
  a nearest parcel not accepted, 896 not placed. Unread: the 19 volumes
  before July 1924.
- **Verified:** 2026-11-15 (vol. 24 pt. 2: read 3,858 entries, found 1,969
  San Francisco rows, resolved 228, published 228 on 212 pages. Learned: the
  Owner field survives extract.py wherever the OCR mangles the word
  ("Owne';'^-", "OwiuT —"), in unresolved findings as much as resolved ones,
  so run scrub_owner.py over the whole source after every publish; in 1924
  an architect is named on many plain houses, and when that architect is the
  owner the house has nothing left to publish and joins the held rows
  (`held for a page` in the fixes file).)
- **Verified:** 2026-11-15 (vol. 25 pt. 1: read 5,484 entries, found 2,891
  San Francisco rows, resolved 467, published 467 on 446 pages. Learned: the
  largest volume of the run; the raw text is now brought into line with the
  image-checked description by rule (post255.py: a name or cost the
  description does not carry is cut from the raw text), which replaces the
  hand lists of earlier volumes; the same lot can carry two permits months
  apart for different buildings (1624 8th Avenue, 1485 Waller), and the
  later one is not always the one built, so leave both on the timeline and
  flag the credit.)
- **Verified:** 2026-11-15 (vol. 25 pt. 2: read 4,526 entries, found 2,382
  San Francisco rows, resolved 331, published 331 on 312 pages. Learned: 1925
  is the peak of the run, three times the entries of a 1931 volume and two
  thirds of the picked rows flats or apartments; the two-column crop often
  pulls the next entry's contractor and cost into a permit, so a permit that
  ends "Architect - None" with a contractor after it needs the image; a
  whole-building credit from a permit that starts "a " can come from a small
  structure (a roof garden, a tank enclosure), so after publish list the
  credits whose sentence names anything but a building.)
- **Verified:** 2026-11-15 (vol. 31 pt. 2: read 1,542 entries, found 1,054
  San Francisco rows, resolved 92, published 92 on 90 pages. Learned: the
  volume holds 28 issues and runs into 1932, so redate.py (one year) folds
  the January issues into December and the covers must be listed by hand;
  unpicking rows whose heading says "dwellings" before the crops saved 15
  image checks; a contract's metes-and-bounds line can place on the lot next
  to its own permit, so read same-week pairs together.)
- **Verified:** 2026-11-15 (vol. 31 pt. 1: read 1,610 entries, found 1,033
  San Francisco rows, resolved 83, published 83 on 79 pages. Learned: by 1931
  a third of the picked permits are for rows of two to eight houses by
  owner-builders ("two 1-story and basement frame dwellings ... each $4000");
  the parser reads them as one dwelling, so select.py should skip a heading
  that counts dwellings; one issue (30 May) had no readable running head and
  was dated from its cover; publish.py does not undo a page write when a
  finding is dropped after the first run, so restore that page with git.)
- **Verified:** 2026-11-15 (vol. 30 pt. 2: read 1,529 entries, found 991
  San Francisco rows, resolved 99, published 99 on 96 pages. Learned: the
  cover-line reader missed two of the 26 covers, so the issue starts were
  listed by hand and dated weekly from 5 July; a permit for a row of houses
  ("ten 1-story dwellings") places on the first lot only and is held unless
  the page says which lot it is; a permit and its same-issue contract can
  give different distances from the corner, and the roll's use decides which
  lot the building stands on.)
- **Verified:** 2026-11-15 (vol. 30 pt. 1: read 1,776 entries, found 980
  San Francisco rows, resolved 112, published 112 on 104 pages. Learned: this
  scan's running heads and cover lines both date all 26 issues and agree; a
  crop that ends at a column or page break shows only the heading, and then
  only the heading is published (the cost and names in the OCR belong to the
  continuation and were not read); a permit filed under the contracts column
  by the parser is caught at the image and worded as a permit; a contract
  worded "all work for decorating" is a trade contract and is phrased so the
  publish step sets no builder.)
- **Verified (earlier):** 2026-11-15 (vol. 29 pt. 2: read 1,653 entries, found 944
  San Francisco rows, resolved 122, published 122 on 118 pages. Learned:
  neither dater works alone on this scan (running heads date 82 of 897
  leaves, and the cover-line dater misses the 20 July cover, printed
  "Twenty. ninth Year"), so the 26 issue starts were listed by hand from both;
  an owner sometimes gives the contractor's office as his own address, so a
  shared address with a different surname is not proof of an owner-builder
  (R. Harms, 1217 Stanyan, appears for three unrelated owners); a permit and
  its contract can print different street numbers for one job (1031 and 1032
  Broadway), and the one that matches the roll is published; a ten-flat
  contract at a corner was five two-flat buildings on a tract and was held.)
- **Verified (earlier):** 2026-11-15 (vol. 29 pt. 1: read 1,935 entries, found 1,086
  San Francisco rows, resolved 151, published 151 on 147 pages. Learned: the
  cover-line dater misses a cover whose date line is garbled (1 June 1929)
  and shifts every later issue, so check its issue starts against the
  running-head dates before writing either; building slowed in 1929, about a
  third fewer entries than a 1927 half-year; a builder who files a second
  permit for a lot in a ten-house row drops the first permit's architect, so
  compare each new entry with what the page already carries from earlier
  volumes (1767 18th Avenue).)
- **Verified (earlier):** 2026-11-15 (vol. 28 pt. 2: read 2,133 entries, found 1,335
  San Francisco rows, resolved 186, published 186 on 171 pages. Learned: the
  paper sometimes prints one permit twice in an issue under two serial
  numbers, and re-records a contract weeks later with a new filing date, so
  compare a lot's entries across issues before adding one; a later steel or
  trade contract can say which of two schemes was built (Eddy and Laguna: the
  five-storey building of the 1928 permit) while naming a third firm as
  architect or engineer, and then no architect is credited; the publish
  script now credits a builder only from a whole-building permit or an "all
  work" contract.)
- **Verified (earlier):** 2026-11-15 (vol. 28 pt. 1: read 2,542 entries, found 1,741
  San Francisco rows, resolved 269, published 269 on 247 pages. Learned: this
  volume's running heads are too garbled to date the issues, and the cover
  line of each issue ("SAN FRANCISCO, CALIF., <date>") dates them instead; a
  big building's sub-trade contracts (steel, marble, lathing, refrigeration,
  painting for the hotel at Powell and Sutter) come one a month and none of
  them names the builder, so they must not set `building.builder`; a
  condominium building page with unit sub-pages takes the fact, the unit lot
  does not; where a later permit by another owner falls on a lot credited
  from an earlier tract listing, the credit comes off until the roll says
  which was built (1759 18th Avenue, 1201 Laguna).)
- **Verified (earlier):** 2026-11-15 (vol. 27 pt. 2: read 2,777 entries, found 1,858
  San Francisco rows, resolved 304, published 304 on 284 pages. Learned: the
  listing often names the owner again as contractor or architect (same
  surname at the owner's address), and that name has to be cut with the
  owner; the seeder keeps a cache per manifest file name, so a temporary
  manifest reused under the same name skips every parcel until its
  `.cache/*<name>*` files are removed; a later permit marked "previous
  application withdrawn" explains two schemes on one corner (2299 Pacific).)
- **Verified (earlier):** 2026-11-15 (vol. 27 pt. 1: read 3,479 entries, found 2,165
  San Francisco rows, resolved 345, published 345 on 336 pages. Learned: a lot
  can carry a permit in each of two volumes, and the later one is usually the
  plan that was built, so read the earlier volume's entry and its credit
  again before adding a second (163 Avila: the 1926 two-storey scheme's
  architect was uncredited once the 1927 one-storey permit and the roll
  agreed); a later volume can also settle an earlier doubt (1840 Sacramento:
  the 1927 permit names the architect the page already credited); condominium
  building pages are not keyed by the lot's parcel number, so look for the
  page by address before deciding a parcel has none.)
- **Verified (earlier):** 2026-11-15 (vol. 26 pt. 2: read 3,765 entries, found 2,264
  San Francisco rows, resolved 290, published 290 on 282 pages. Learned: the issue date
  must be read from every running-head form ("Saturday, October 30th, 1926",
  "September 18, 1926" with no weekday, and the Friday issues of 24 and 31
  December) and checked to be weekly and unbroken, or a whole issue takes its
  neighbour's date; the
  reader index and the scan leaf drift apart inside an item, so fetch the
  item's leaf map before cropping; a page-writing script must strip only its
  own volume's entries on a re-run, or it deletes the earlier volume's; where
  two volumes put different plans on one lot, the roll's storey count says
  which was built.)
- **Verified (earlier):** 2026-11-14 (vol. 26 pt. 1: read 4,373 entries, found 2,404
  San Francisco rows, resolved 368, published 368 on 345 pages. Nine existing
  pages already credited the same architect from a survey, which is the
  independent check on the placements. Learned: the reader's page index is
  the djvu index, not the jp2 number; the OCR location is reliable and the
  OCR cost and names are not; the resolver's default filed 44 of 242 new
  pages under a neighbouring directory, caught by comparing each new page's
  analysis neighborhood with the directory the city's pages for that
  neighborhood mostly use. The pipeline scripts are not in the repository;
  they are in the project's shared files under `building-engineering-news/`.)
