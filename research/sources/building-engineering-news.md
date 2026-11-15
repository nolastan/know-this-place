# building-engineering-news — *Building and Engineering News* (primary)

> **Research dossier.** Rules: [../AGENTS.md](../AGENTS.md) · traps:
> [../LESSONS.md](../LESSONS.md) · register:
> [../SOURCES.md](../SOURCES.md) · cited on pages by the source id `building-engineering-news`.
>
> - **Kind:** journal OCR · **Tier:** primary · **Status:** open
> - **Search-invisibility:** high — see the register for what that rates.
> - **Coverage:** 3 of 34 half-year volumes read (vol. 26 pts. 1 and 2 and vol. 27 pt. 1, January 1926 – June 1927): 1,003 facts on 963 page writes (668 pages seeded). Resume at vol. 27 pt. 2 (`buildingengineer2127cont`). See the `Verified:` line.
> - **Local corpus:** `research/corpora/building-engineering-news/`
> - **Claimed:** every unread volume, and the 1,417 placed-and-held rows (543 in vol. 26 pt. 1, 425 in pt. 2, 449 in vol. 27 pt. 1), by the project run that opened this source (Stan, since 2026-11-14). The held rows wait on his decision about how many pages to seed.
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
  owner-builder printed under Contractor is given as the contractor.
- **Citation label:** "Building and Engineering News, 23 January 1926", with
  the page link. Page source ids are
  `building-engineering-news-<issue date>-n<index>`.
- **Coverage:** vol. 26 pt. 1 (26 issues, 2 January – 26 June 1926), permits
  and contracts only. 4,373 numbered entries; 2,404 San Francisco rows; 1,610
  placed on a parcel; 385 picked (page exists, or an architect is named, or
  the building is flats, apartments or commercial) and read against the image;
  368 published on 345 pages, 242 of them seeded. Unread: the other 33
  volumes. Unfinished in this volume: 543 placed single houses held for a
  page-count decision, 682 rows with a nearest parcel not accepted, 794 not
  placed (354 unparsed location lines, 245 street pairs that do not cross
  under the names read, 160 street numbers with no EAS row).
- **Coverage, vol. 26 pt. 2** (`buildingengineer226cont`, 3 July – 31 December
  1926): 3,765 numbered entries; 2,264 San Francisco rows; 1,318 placed on a
  parcel; 306 picked and read against the image; 290 published on 282 pages,
  186 of them seeded. Unfinished: 425 placed single houses held for the same
  page-count decision, 586 rows with a nearest parcel not accepted, 946 not
  placed. Unread: the other 32 volumes.
- **Coverage, vol. 27 pt. 1** (`buildingengineer227cont`, 8 January – 25 June
  1927): 3,479 numbered entries; 2,165 San Francisco rows; 1,343 placed on a
  parcel; 358 picked and read against the image; 345 published on 336 pages,
  240 of them seeded. Unfinished: 449 placed single houses held for the same
  page-count decision, 536 rows with a nearest parcel not accepted, 822 not
  placed. Unread: the other 31 volumes.
- **Verified:** 2026-11-15 (vol. 27 pt. 1: read 3,479 entries, found 2,165
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
