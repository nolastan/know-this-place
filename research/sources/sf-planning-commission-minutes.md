# sf-planning-commission-minutes — Minutes of the San Francisco City Planning Commission (primary)

> **Research dossier.** Rules: [../AGENTS.md](../AGENTS.md) · traps:
> [../LESSONS.md](../LESSONS.md) · register:
> [../SOURCES.md](../SOURCES.md) · cited on pages by the source id `sf-planning-commission-minutes`.
>
> - **Kind:** meeting minutes (scanned volumes) · **Tier:** primary · **Status:** open
> - **Search-invisibility:** high — see the register for what that rates.
> - **Coverage:** 31 of 52 volumes read (July 1968 – November 1978): 9,011
>   pages, 3,221 findings, 1,538 resolved, 1,407 published. 21 volumes
>   remain — 1979, 1980 and 1994–2005. July–December 1975 is in no
>   volume, nor is the regular meeting of 16 March 1978, and volume 37
>   holds only 17 of June – November 1978's meetings.
> - **Local corpus:** `research/corpora/sf-planning-commission-minutes/`
>
> Update this dossier at the end of every pass — the `Verified:` line, the
> coverage note, and anything the pass learned about getting at the source.

- **What:** The minutes of the City Planning Commission's regular meetings,
  as the Commission's own secretary kept them. Each meeting runs through a
  calendar of cases, and each case prints a case number (`CU68.18`, `ZM69.9`,
  `R68.35`), the property, the request, who spoke, and the resolution with the
  vote. Two things in that are address-level facts, and no city dataset holds
  either: **what the Commission decided about a building**, dated to the day,
  and **what the staff said was standing on the property** when it decided —
  storeys, units, beds, rooms, the use, the business or institution occupying
  it, whether it was vacant.
- **Where:** The San Francisco Public Library contributed 52 volumes to the
  Internet Archive, digitized under a California State Library Califa/LSTA
  grant. Identifiers are of the form `<n>minutesofsanfran<year>san[f]`, where
  `<n>` runs 6 to 58 in date order, skipping 31; the volume's own span is in its
  `volume` metadata field (`July-Sept 1968`), never in `date`, which is
  usually empty.

| volumes | span | state |
|---|---|---|
| 6–11 | July 1968 – December 1969, one quarter each | **read in full** 2026-10-06 |
| 12–15 | January – December 1970, one quarter each | **read in full** 2026-10-09 |
| 16–19 | January – December 1971, one quarter each | **read in full** 2026-10-10 |
| 20–23 | January – December 1972, one quarter each | **read in full** 2026-10-11 |
| 24–27 | January – December 1973, one quarter each | **read in full** 2026-10-12 |
| 28–29 | January – December 1974, one half each | **read in full** 2026-10-12 |
| 30 | January – June 1975 | **read in full** 2026-10-13 |
| — | July – December 1975 | in no volume: the sequence skips 31 |
| 32 | January – June 1976 | **read in full** 2026-10-14 |
| 33 | July – December 1976 | **read in full** 2026-10-15 |
| 34 | January – June 1977 | **read in full** 2026-10-16 |
| 35 | July – December 1977 (`35minutesofsanfran1977sa`, no final `n`) | **read in full** 2026-10-17; its last page breaks off inside the 22 December meeting |
| 36 | January – March 1978 | **read in full** 2026-10-18; it holds no minutes for the regular meeting of 16 March 1978 |
| 37 | June – November 1978 (`volume` "June-Nov 1978") | **read in full** 2026-10-19; it holds only 17 meetings — no regular meeting of June, and none of 6, 13 and 27 July, 31 August, 21 and 28 September, 12, 19 and 26 October, or 2 and 30 November |
| 38–39 | 1979 and 1980 whole | unread |
| 40–58 | 1994–2005 | unread |
| — | 1981–1993 | in no volume |
| — | before July 1968 | not in this collection. The Commission dates from 1942 |

- **How to get at it:** `archive.org` serves everything over plain HTTPS with
  no challenge; the advanced-search API lists the volumes
  (`collection:sanfranciscopubliclibrary AND title:(planning commission) AND
  title:minutes`, asking for `identifier,volume,title`). For each volume take
  three files, about 500 KB together:
  - `<id>_hocr_searchtext.txt.gz` — the OCR text
  - `<id>_hocr_pageindex.json.gz` — byte offsets into it, one span per leaf
  - `<id>_scandata.xml` — the leaf list, and which leaves are colour cards
  **Split on the page index, not on the `_djvu.txt`.** The one-file text has no
  page separators, and a citation has to name a page. The page index carries
  **one span per scandata leaf, the two colour cards included** (leaf 0 and the
  last), so count a leaf's viewer number among the leaves `scandata.xml` does
  not mark `addToAccessFormats>false`, skipping the cards' spans rather than
  just dropping their files: span *i* is viewer page *i − 1*. Taking the span
  index as the page number puts every citation one page late. That makes the
  number the Internet Archive viewer's own page number, so the citation URL is
  `https://archive.org/details/<id>/page/n<i>/mode/1up` and it opens on the
  page the fact is on.
- **What is actually usable:**
  - **A decision.** "CU68.18  905 California Street, southwest corner of Powell
    Street … Request for authorization to convert the existing Stanford Court
    Apartment House into a hotel" — then, pages later, the motion and the vote.
    The *decision* is the dated event; the request is not (LESSONS.md: a
    proposal in a source is not an event).
  - **A statement of what stood there.** The staff report inside the same case:
    126 apartments of which 30 had no kitchen, a garage holding 110
    attendant-parked cars, 433 hospital beds, a vacant warehouse of 18,650
    square feet, a grocery built in 1945. These are the facts a page has
    nowhere else to get.
  - **Landmark designations.** Article 10 began in 1967, so these volumes carry
    the Commission's approval of the city's first landmarks — eleven in the
    last quarter of 1968 alone, most of them in Jackson Square, several over
    the owners' objection and with the vote recorded.
  - **A bearing instead of a number**, on perhaps half the cases: "north line,
    112.5 feet north of Haight Street". That is what the resolver needs where
    a number alone is ambiguous — but see the cautions: on its own it rarely
    places a parcel.
- **Cautions:**
  - **100 Larkin Street is the Commission's own meeting room**, printed in
    every meeting's opening paragraph, and it is never a case. The same
    advertiser-address trap the trade journals have.
  - **The volume's binding order is not its date order.** Volume 7 opens with
    a July cover page and then runs the 26 September meeting before October's;
    two of volume 8's meetings and two of volume 6's are bound under the wrong
    quarter. **Date every page from the meeting header it sits under** ("Minutes
    of the regular meeting held Thursday, July 11, 1968"), never from the
    volume's span: a header-based pass found six meetings the span-based guess
    had wrong.
  - **A case's header can be on a leaf the scan lost**, and then the decision
    is on the page with no address at all. Four cases in these six volumes
    read that way; each stays unresolved unless the building is named.
  - **A decision reached at a later meeting belongs to that meeting.** Cases
    are postponed, taken under advisement and carried for months; 32 of 286
    were still open when the volume ended. The decision's date is the meeting
    that decided, and the finding's `extra.case` is what links the two.
  - **The OCR mangles case numbers and street numbers in the headers**
    (`CU6S.4S`, `1*1*5 Jackson`, `222U Sacramento`, `ZM63.34`), while the
    resolution text lower on the same page often prints the number cleanly.
    Read both: the Bank of Lucas, Turner and Company's header says 300
    Montgomery and its resolution says 800, which is the right one.
  - **A 1968 decision lands on a parcel the assessor dates later** more often
    here than in any period source, because the Commission was deciding about
    buildings the city then replaced. Seventeen of this batch's resolutions sit
    on a parcel rebuilt afterwards (1972 to 2007); the fact is still the lot's,
    and it needs the frame `check.py --overlap` asks for ("the warehouse then
    on the site"), not a decline.
  - **The street numbers are modern** — this is 1968, long after the 1909
    renumbering — but the buildings often are not, so a number that resolves
    cleanly can still point at a later building.
  - **The page with the text is the even one.** Every odd viewer page in the
    1970 volumes is a blank verso or bleed-through noise, and a few minutes
    pages were scanned twice (vol. 14, n0030 and n0032).
  - **A record that prints its own block and lot needs no street number.**
    About a third of the cases locate the property as "Lot 15, Block 4209, north
    side of 24th Street west of York Street" — no number at all — and the
    resolver can only call those unplaceable by address. Looking the lot up in
    `acdm-wktn` and EAS by parcel placed 33 of the 1970 findings: one active lot
    with one address on the street the record names. Several lots, or a lot
    with no address, stay unresolved. `resolve_eas.py` now says so in the note
    instead of "it cannot become a page".
  - **The mini-park lots are place pages now.** From 1970 the Commission
    passed the City's purchase of a run of vacant lots for its mini-park
    programme, each named only by block and lot. Some are Recreation and Park
    places today (Howard & Langton, 24th & York, the Roosevelt and Henry
    stairs) and take the fact on the `place.json`; others were built on
    instead, 1972–1990, and take it framed as what was then on the lot.
  - **A Board of Supervisors action reported in the minutes is dated to the
    Board's meeting**, which the report names ("at its meeting of September 28,
    1970"), not to the Commission meeting that heard the report.
  - **The 1971 volumes stop naming the Board's date.** "The Board of
    Supervisors, at its meeting on Monday, approved…" is the 1971 form: seven
    of that year's reported actions (four landmark designations, two
    reclassifications, a Finance Committee vote on the Opera House) print no
    date of their own, and three of ten readers dated each one to the
    Commission meeting that reported it — a date the action never had. Working
    out the Monday is arithmetic the spec forbids. Frame it instead: "By 26
    August 1971, the Board of Supervisors had approved…", dated to the reporting
    meeting, which is true as written.
  - **From June 1971 the page headers drop the meeting date** in places (vol.
    17 from n272); date those pages from the meeting's opening paragraph.
  - **The same case number can be printed for two cases** (R71.21 for 2750
    Hyde and for a Loomis Street lot) and **a case's number can change between
    hearings** (2352 Pine: CU71.38 on 5 August, CU71.28 on 12 August). Link a
    decision to its hearing by the address, not the number alone.
  - **1971 is the year of the downtown towers.** Discretionary review brought
    the Metropolitan Life, Tishman-Cahill, Standard Oil, One Market Plaza and
    100 Van Ness towers before the Commission, each with the buildings then on
    its site; none of them prints a street number, and each was placed by name
    on the page the site already had for the tower.
  - **Readers supply numbers the minutes do not print.** One 1970 reader
    turned a speaker's "built 112 years ago" into "about 1858", and two
    corrected a resolution number from the sequence. The year was declined;
    the resolution numbers are kept as printed with the doubt in
    `reader_note`. Say in the spec that a date is what the page states, not
    what can be worked out from it.
  - **A condominium tower keeps its number on its original lot in EAS.** The
    1972 height hearings list the Russian Hill towers by street number with
    units and height — 1100 Union, 2164 and 2240 Hyde, 945 and 947 Green — and
    EAS joins each cleanly to one active parcel. That parcel has no row on the
    secured roll: the building's units are `<block>C…` lots of the same block,
    and `seed-list` skipped all five. They are condominiums waiting on #446,
    not pages. `resolve_eas.py report` now lists every resolution onto a
    parcel with no roll row.
  - **1972 is the year of the height-and-bulk hearings.** Eight special
    meetings (16 and 30 March, 12 and 26 April, 13 June, 22 June evening,
    and the open-space hearings of 16 November and 12 December) are almost all
    public testimony and citywide maps. What they locate is a speaker's
    "the Summit at 297 feet", "Harkness Hospital on Fell Street" — named
    buildings with no number and no decision, left unresolved. The staff
    tables of neighbouring tower heights in the Green-and-Jones and
    Hyde-and-Lombard cases are the exception, and gave the year's Russian Hill
    pages their units-and-height facts.
  - **The Commission's landmark vote and the Board's ordinance are two
    entries' worth only where the page lacks the vote.** The Article 10 report
    already dates each designation; the minutes add the Commission's own vote
    (the House of the Flag carried 4-3 on 10 February 1972) and, new in 1972,
    the 180-day suspension of a demolition application on a designated
    landmark (the Old Mint and the House of the Flag, both 15 June 1972). The
    Board's undated second reading adds nothing beside the ordinance date and
    was declined.
  - **A header's number and its resolution's number can name different
    buildings, and the join takes the header.** The Haslett Warehouse case
    (LM73.4) prints 600 Beach Street in its header and 680 Beach in the
    resolution; EAS joins 600 Beach to the Cannery's parcel next door, and the
    finding went there until a by-name check moved it to 680. Wherever a
    reader's `reader_note` says the two disagree, place the finding by hand.
  - **A landmark's printed number can be on two parcels in EAS.** "1820
    California Street", the Lilienthal-Orville Pratt House, is filed on both
    0641004 (the landmark, the site's 1818 California page) and 0641006, and
    the join chose 0641006. For a designation, check the parcel against the
    page that already names the landmark.
  - **A landmark's minutes repeat its Article 10 report.** From 1974 the
    Commission's landmark hearings read the Landmarks Board's case report into
    the record — the 1853 and 1859 maps under the Tanforan Cottages, the 1869
    party-wall houses under the Goodman Building. The site already carries
    those from the Article 10 reports: 14 of 1974's 24 declines are that. What
    the minutes add is the Commission's vote, its date, and what the building
    was being used for that year.
  - **1974 is the year of the residential care homes.** On 27 June 1974 the
    Commission legalised fifteen state-licensed group homes in houses —
    residents, years in operation, operating organisation — in one sitting; the
    1973 and 1974 volumes hold about thirty such cases. They are a use of the
    building and are published; no resident is ever named.
  - **1975 is the year the Board overrides the Commission.** Three of the
    half-year's Board actions reported in the minutes reverse it — the Atherton
    House and Goodman Building landmark designations it had refused, and a
    Bryant Street wrecking yard it had denied — all "on Monday", undated, and
    framed "by" the reporting meeting. They are worth publishing where the page
    carries the Commission's refusal: the override is the new fact.
  - **A header and its report can print numbers a thousand apart.** R75.5's
    header reads "1050 Kearny Street, at Chestnut" and the staff report "1850
    Kearny Street, 90 feet south of Francisco"; the printed Lot 3, Block 56
    settled it for 1850. Put the block and lot on such findings and read the
    report's "matches the parcel's block" line.
  - **EAS can join a street of the wrong type.** "20 Edgar Place" joined to
    20 EDGAR AVE, the only Edgar in EAS, with the mismatch noted in the method
    but the finding resolved. Read every "EAS files this street as …, not …"
    line; on a one-line mention, take it back to unresolved.
  - **The residential care homes keep coming.** The 1975 volume has eight
    more — Lake, La Playa, 12th Avenue, Fulton, Broderick, Randolph — and the
    Commission's one-home-per-block-face guideline refused one of them (24
    Randolph, across from the 24-person home at 27–45 Randolph).
- **1976 changes the Commission and its minutes.** Mayor Moscone's new
  Commission took office at the special meeting of 3 February 1976 (no
  regular meetings in January after the 7th; 22 January lacked a quorum).
  From then the minutes run long: whole hearings are verbatim testimony on
  institutional master plans, the parapet ordinance, the tree ordinance and
  the citywide residential rezoning, and none of it locates a building. Of
  519 pages with text, about 300 hold no property at all. Budget the reader's
  time by meetings, not pages.
- **Discretionary review on commercially zoned land is new in 1976.** The
  Commission refused the 316-318 Laurel psychiatrists' offices on C-2 land
  and steered the two Sacramento Street corner lots into one building with
  parking. The minutes name the lot split (recorded 8 July 1975) that started
  it, which is the date the parcel history needs.
- **A record's lots can be found by area after they were merged.** The two
  Sacramento Street lots at Laurel, 41.25 x 62 feet each, have no parcel at
  either printed number; parcel 1009029 (3490 Sacramento, built 1977) is
  exactly 5,115 square feet — the two together. Belgrave Avenue's two 25-foot
  lots are likewise 65 Belgrave's 5,000-square-foot lot of 1981. Where the
  minutes print lot dimensions and EAS has nothing, add the lots up.
- **A printed block and lot can outlive the street number.** "Lot 27, Block
  2626, commonly known as 7 Vulcan Stairway": EAS has no 7 Vulcan, but the
  lot survives as 60 Lower Terrace, and the minutes say it fronts Lower
  Terrace too. Look the lot up before calling the number dead.
- **Speakers are not staff.** 1976 hearings are dense with neighbourhood
  testimony that dates buildings ("most of the cottages were built in 1906",
  "a nurses' residence built in 1963 and torn down six years later"). Take
  dates and descriptions from the staff report or the resolution; a speaker's
  date goes in `reader_note` or is declined.
- **The second half of 1976 is the interim-zoning half-year.** The residential
  rezoning initiated on 20 May 1976 made every building over 30 feet in a
  proposed RH district, and every second unit on a large RH-1 lot, a matter
  for discretionary review until the new code passed; about a third of the
  half-year's property cases are those (Foerster, Miguel, Ashbury, Buena Vista
  East, Laguna). They print the lot, what stands on it and the decision, and
  they resolve well. The rest is fast-food and branch-bank guidelines (two
  Doggie Diners, Bell Savings, Sumitomo Bank), billboard ordinances and the
  Inner Richmond traffic barriers, which locate nothing.
- **The Board of Permit Appeals is reported like the Board of Supervisors** —
  "on the previous evening", no date of its own — and it overruled the
  Commission at least twice this half-year (the 25th Avenue Doggie Diner on
  rehearing). Frame it "by" the reporting meeting, as for the Board.
- **Case numbers repeat within the half-year.** LM76.3 is both the Art
  Institute and the Jessie Street Substation; DR76.12 is both 2151 Laguna and
  370 Monterey; DR76.30 heads both 937 Union and 326 12th Avenue. Link
  hearings by address.
- **A dead number can live on the roll, and a record's lot size picks the
  parcel.** 5505 Geary has no EAS row, but the roll files parcel 1525001 as
  `5505 5501 GEARY` on exactly the 3,600 sq ft the record measures; the
  printed Lot 1, Block 1071 put "49 Masonic" on 3 Masonic by its 55,303 sq ft;
  and a 2,763 sq ft disagreement threw out 1650 Webster's exact EAS join.
  Where the record prints a lot size or a block and lot, check them before
  calling a number dead or a join good.
- **The second half of 1977 is the condominium-conversion half-year.** The
  1975 Subdivision Code amendments sent every conversion to the Commission
  for a Master Plan finding, and from October the hearings fill whole
  evenings: 950 Pine, 139 Commonwealth, 1990 Green (refused, then reversed by
  the Board), Diamond Heights Village (396 units, the first over fifty, its
  refusal voided by the City Attorney because the Commission ruled after the
  50-day limit), Laguna O'Farrell (150 units) and five more on 22 December.
  The buildings are condominiums today, so most of these stay unplaced
  (#446); a record that names the rental building is still worth reading for
  its rents and unit mix, which nothing else holds.
- **A tie is a refusal, and the minutes say so.** "A tie vote on any matter
  … shall be deemed to be a disapproval" — the Performing Arts garage
  resolution and the Diamond Heights Village finding both failed 3-3. Write
  the decision as a refusal on a tie, not as no decision.
- **Resolution numbers repeat in the minutes.** 7834 is printed for both 333
  Market (3 November) and Diamond Heights Village (10 November), and 7778 for
  both 180 Montgomery and the Four Embarcadero Center resolution; keep the
  number as printed and say so in `reader_note`.
- **A record's own lot catches a wrong number.** The 55, 75 and 95 Holyoke
  houses joined to 55 Holyoke on another block; the printed Lots 34, 35 and 45
  of Block 6204 are 1455 and 1475 Holyoke today, and a commissioner at the
  hearing had doubted the numbers. The Gartland Hotel's "3070 16th Street"
  has no EAS row, and its printed Lot 16 of Block 3554 is 3080-3092 16th.
- **A frontage number can join the wrong parcel of a big site.** "1850 Ocean
  Avenue (former Homewood Terrace site)" joins 3283124, a 1985 store of
  87,555 sq ft on the Ocean Avenue frontage; the record's 7.5-acre site
  behind it is many lots now. Compare the record's acreage with the parcel's
  before accepting a join on a large site.
- **January – March 1978 is the condominium-conversion quarter.** Of 19
  meetings, 8 are special hearings on the citywide residential rezoning and
  conversion policy, and the regular meetings fill with conversion maps:
  1097 Green tied 3-3 (a refusal), 1101 Green (the Bellaire Tower, 65 units)
  refused 3-4, both reversed by the Board within a month; on 23 February the
  Commission asked the Board for a 90-day moratorium on conversion
  applications. Every converted building is a condominium today, and two of
  them hide it — see the next caution.
- **A condominium's unit parcel can look like the building.** 1097 Green
  Street's EAS row joins one parcel, 0126031, which the roll files as `1896
  LEAVENWORTH ST0000` — the building's other frontage, unit `0000` — and 439
  Greenwich's 0087029 is `0439 GREENWICH ST0000`. Neither names a unit, so
  the resolver's sibling test let both through; but both have a lot area of
  zero. The resolver now treats zero lot area on a condominium-class parcel
  as a unit. The existing 1097 Green page sits on that unit parcel (#228).
- **People:** The minutes are *full* of them: applicants, their attorneys and
  architects, objecting neighbours, improvement-club officers, the
  commissioners and the staff, all named in the narrative of every hearing.
  **None of them may be extracted**, under the root
  [AGENTS.md](../../AGENTS.md)'s privacy limits — these are living or
  recently-living private people whose names the record happens to print, not
  published history of a building's occupants. What is kept: companies,
  institutions, churches, schools, hospitals, unions, government bodies, named
  buildings — and **the architect of the building**, which the minutes give for
  most large cases and which goes in `extra.reader_note` for a publisher to
  decide on. A business trading under a person's own name ("Joe Smith's
  Garage") is left out with the person. No notable past occupant has turned up
  in these volumes: the Commission's business is the building.
- **Citation label:** name the body, the meeting date and the page —
  "San Francisco City Planning Commission, minutes of the regular meeting of
  5 June 1969". A page's `sources` entry carries the id
  `sf-planning-commission-minutes-<YYYY-MM-DD>` and the viewer URL for the
  page the fact is on.
- **Coverage:** Volumes 6–11 — every meeting from 11 July 1968 to 18 December
  1969 — read in full into
  `findings/sf-planning-commission-minutes/minutes-1968-1969.json`; volumes
  12–15 — every meeting of 1970, 8 January to 17 December — read in full into
  `findings/sf-planning-commission-minutes/minutes-1970.json`; volumes
  16–19 — every meeting of 1971, 7 January to 23 December — read in full
  into `findings/sf-planning-commission-minutes/minutes-1971.json`; volumes
  20–23 — every meeting of 1972, 6 January to 21 December — read in full
  into `findings/sf-planning-commission-minutes/minutes-1972.json`. Nothing
  of those volumes is known to remain unread; volumes 24–27, every meeting of
  1973, 4 January to 20 December, into `minutes-1973.json`; volumes 28–29,
  every meeting of 1974, 3 January to 19 December, into `minutes-1974.json`;
  volume 30, every meeting of January – June 1975, into `minutes-1975.json`;
  volume 32, every meeting of January – June 1976, into
  `minutes-1976-h1.json`; volume 33, every meeting of July – December
  1976, into `minutes-1976-h2.json`; volume 34, every meeting of January –
  June 1977, into `minutes-1977-h1.json`; volume 35, every meeting of July –
  December 1977, into `minutes-1977-h2.json` (the scan ends inside the 22
  December meeting); volume 36, every meeting of January – March 1978 the
  scan holds, into `minutes-1978-q1.json`; volume 37, the 17 meetings of
  June – November 1978 the scan holds, into `minutes-1978-h2.json`.
  **Next: volume 38 (1979, `38minutesofsanfran1979san`)** into
  `minutes-1979.json` — volumes 36 and 37 took a single reader under half a
  session each (177 and 124 text pages), so a short volume and its
  successor fit one run; a half-year volume is one nightly run by a single
  reader (volumes 32–35, 519 to 572 text pages, all fitted). Volume 38 is a
  whole year and may need to be split across two runs — size it by its text
  pages first;
  the 1994–2005 volumes are a
  different kind of document (by then the Commission's own case reports are
  online and indexed) and are worth sampling before a run is sized on them.
- **Verified:** 2026-10-06 (volumes 6–11, July 1968 – December 1969: 957 OCR
  pages with text out of 1,856 scanned leaves, read by six readers from one
  spec. 286 cases heard, 180 of them about a property the minutes locate; 372
  findings — 198 statements of what stood on a property, 174 decisions. 163
  resolved on 110 parcels: 113 by the EAS join on a printed number, 46 by name
  on a building the minutes name and a page already carries, 4 by `corner.py`'s
  corner test. 209 unresolved, 142 of them located only by a block, a corner or
  a name with nothing to place them on. 162 published on 91 pages, 44 of them
  seeded; 1 declined. What the pass learned: split the volume on the hOCR page
  index and drop the colour cards, so a citation names the viewer's own page;
  date every page from its meeting header, because the binding order is not the
  date order; a bearing from a corner, which the triage note rated the source's
  strength, placed only 4 of 99 entries, because a 1968 case names no lot
  dimensions and `corner.py` has nothing to check an offset against.)
  **2026-10-09** (volumes 12–15, January – December 1970: 1,478 OCR pages with
  text out of 1,652 scanned leaves, read by eight readers from one spec in
  about ten minutes. 50 meetings, 281 agenda items, 233 about a property the
  minutes locate; 455 findings — 217 statements of what stood on a property,
  183 decisions, 47 dated past facts, 8 landmark designations. 250 resolved:
  199 by the EAS join on a printed number, 18 by name on a building a page
  already carries, 33 by the record's own block and lot. 205 unresolved, 148
  of them located only by a block, a corner or a name. 235 published on 116
  pages, 73 of them seeded and 3 of them place pages; 15 declined. The year's
  densest single sitting is 27 August 1970, 34 small shops in residential
  districts asking to extend a nonconforming use to 1980 — a grocery, a
  laundry, a barber, a cabinet shop, each dated to the day, on a corner no
  other source in the register reaches. What the pass learned: the page index
  holds a span for each colour card, so a citation must skip them, not drop
  them; a record with a block and lot and no number is placed by parcel; a
  reader will do arithmetic to supply a date, and the spec must forbid it.)
  **2026-10-10** (volumes 16–19, January – December 1971: 1,086 OCR pages
  with text out of 1,704 scanned leaves, read by ten readers from one spec in
  about six minutes. 39 meetings; 323 findings — 162 statements of what stood
  on a property, 113 decisions, 38 dated past facts, 10 landmark designations.
  154 resolved: 108 by the EAS join on a printed number, 46 by hand — by name
  on a building a page already carries, by the record's own block and lot, and
  one range. 169 unresolved, 128 of them located only by a block, a corner or a
  name; 11 are condominiums waiting on #446. 142 published on 71 pages, 34 of
  them seeded and 2 of them place pages; 12 declined. Fewer property cases
  than 1970 — whole sittings went to the Improvement Plan for Residence, the
  Urban Design Plan and the citywide transportation plan, which locate
  nothing. What the pass learned: the 1971 minutes report Board actions as
  "on Monday" with no date, and the frame is "by" the reporting meeting; the
  downtown towers of 1971 are found by name, not number.)
  **2026-10-11** (volumes 20–23, January – December 1972: 1,006 OCR pages
  with text out of 1,942 scanned leaves, read by ten readers from one spec in
  about twenty minutes. 43 meetings; 382 findings — 174 statements of what
  stood on a property, 128 decisions, 65 dated past facts, 15 landmark
  designations. 131 resolved: 107 by the EAS join on a printed number, 24 by
  hand on a named building the site already carries. 251 unresolved, 196 of
  them with no street number; 29 are condominiums waiting on #446. 101
  published on 53 pages, 20 of them seeded and 1 a place page; 30 declined, 18
  of them already on the page from an earlier volume or another source. The
  year's new kind of fact is the suspension of a demolition application on a
  designated landmark. What the pass learned: an EAS join can land on a
  condominium tower's original lot, which has no roll row, and the seeder
  then skips it silently — `resolve_eas.py report` now lists those; and the
  1972 height hearings, a quarter of the year's pages, locate almost
  nothing.)
  **2026-10-12** (volumes 24–29, January 1973 – December 1974, two years in
  one run: 1,673 OCR pages with text out of 3,248 scanned leaves, read by
  thirteen readers from the Reader spec below; 97 meetings; 881 findings — 399
  statements of what stood on a property, 339 decisions, 102 dated past facts,
  41 landmark designations. 385 resolved: 323 by the EAS join on a printed
  number, 62 by hand — 14 by the record's own block and lot, 48 by name on a
  building the site already carries. 496 unresolved, 323 of them with no
  street number; 8 are condominiums waiting on #228 and #446. 338 published on
  174 distinct pages, 94 of them seeded and 2 Golden Gate Park place pages; 47
  declined. What the pass learned: a header's number and its resolution's
  number can name neighbouring parcels, and a landmark's number can be on two
  parcels in EAS — both put a designation on the wrong building until a
  by-name check caught it; from 1974 the landmark hearings repeat the Article
  10 report, and what is new is the vote; `resolve_eas.py report` had never
  printed its "placed by point" list, an indentation bug fixed in this run.
  Five of the thirteen readers were stopped by a usage limit part-way and
  resumed from their own transcripts, losing nothing.)
  **2026-10-13** (volume 30, January – June 1975: 350 OCR pages with text out
  of 714 viewer pages, read in one session by a single reader with no
  sub-agents — the nightly-run shape; 23 meetings; 102 findings — 53
  decisions, 37 statements of what stood on a property, 7 landmark actions, 5
  dated past facts. 63 resolved: 53 by the EAS join, 10 by name on a building
  the site already carries. 39 unresolved, 26 of them with no street number, 4
  condominiums waiting on #446. 61 published on 40 pages, 18 of them seeded; 2
  declined as already on the page. One conflict stated: 361 Oak Street, 1868
  by the owner's account against the roll's 1885. What the pass learned: the
  July–December 1975 volume does not exist in the collection; a single reader
  with a page filter (skip any page with fewer than 40 four-letter words — the
  bleed-through versos) reads a half-year volume in one session; a header can
  print a number a thousand off its report; EAS will join Edgar Place to Edgar
  Avenue; and a publish script re-indented three one-space pages, a trap
  LESSONS.md had recorded four times — `research/tools/pagejson.py` now does
  the load and save so the next run cannot.)
  **2026-10-14** (volume 32, January – June 1976: 519 OCR pages with text out
  of 582 viewer pages, read in one session by a single reader with no
  sub-agents; 28 meetings; 114 findings — 57 statements of what stood on a
  property, 47 decisions, 6 dated past facts, 4 landmark actions. 69 resolved:
  54 by the EAS join, 15 by hand — 2 by the record's own block and lot, 3 by
  adding up the lots the record measures, 3 past an EAS stray, 7 by name on a
  building a page already carries. 45 unresolved, 29 with no street number, 7
  condominiums waiting on #446, 9 at a number with no parcel. 65 published on
  43 pages, 13 of them seeded; 4 declined. Four conflicts stated in unknowns.
  What the pass learned: the new 1976 Commission's minutes are half testimony
  that locates nothing; merged lots are found by area and dead numbers by the
  printed lot; and a hand override of the resolver must be written before
  `manifest`, or the manifest seeds the resolver's wrong parcel — here the
  point join had put 3480 Sacramento on the 1965 apartment house next door.)
  **2026-10-15** (volume 33, July – December 1976: 525 OCR pages with text out
  of 590 viewer pages, read in one session by a single reader with no
  sub-agents; 30 meetings, 23 regular and 7 special; 140 findings — 71
  decisions, 55 statements of what stood on a property, 8 dated past facts,
  6 landmark designations. 73 resolved: 61 by the EAS join (one re-filed by hand under
  portola), 12 by hand — 2 by the roll's own range and the record's lot area
  (5505 Geary), 2 by the record's printed lot (49 Masonic is 3 Masonic), 8 by
  name on a building a page already carries (Soko Hardware, Stonestown, the
  Abner Phelps House, the Southern Pacific hospital, Pacific Medical Center).
  67 unresolved: 30 with no street number, 14 condominiums waiting on #446,
  15 at a number EAS no longer has (two of them "No. 9 Fisherman's Wharf",
  which is no street in EAS), 6 where the record's range spans parcels today,
  2 where the record's lot area refused the join. 69
  published on 44 pages, 20 of them seeded; 4 declined as already on the
  page. One conflict stated (1455 Market's construction date). What the pass
  learned: the roll's `property_location` keeps numbers EAS has dropped; a
  record's lot area can refuse an exact join as well as confirm one; and
  `data.sfgov.org` now redirects to `data.sf.gov`.)
  **2026-10-16** (volume 34, January – June 1977: 572 OCR pages with text out
  of 748 viewer pages, read in one session by a single reader with no
  sub-agents; 25 meetings, 6 January to 30 June; 205 findings — 104
  decisions, 73 statements of what stood on a property, 15 landmark
  designations, 13 dated past facts. 125 resolved: 107 by the EAS join, 18 by
  hand — on a building a page already carries (the Palace of Fine Arts, the
  Ferry Building, the City of Paris, Pacific Medical Center, the Key Monument,
  Seward mini-park), by the record's lot (3398 22nd Street, 316 Laurel), and
  six Grove Street findings on the Performing Arts garage parcel that
  replaced them. 80 unresolved: 24 with no street number, 20 at a number EAS
  does not hold, 11 where the record's range spans parcels today, 11 where
  EAS does not join to one parcel, 7 condominiums waiting on #446, 7 by hand
  (3733 Sacramento joins the neighbour's three flats, not the hospital
  annex the record means; 501 Washington is merged into a 1930 building;
  400 Jefferson is a multi-business Port parcel). 112 published on 68 pages,
  30 of them seeded; 13 declined as already on the page or duplicated
  within the batch. What the pass learned: the text-page filter must keep a
  short page that carries a meeting header — six final pages holding votes
  fell under the 40-word floor; a record's header and its resolution can
  print different numbers for one property (38/998 Egbert, 1931/1981
  Funston, 3393/3398 22nd Street), so read both before resolving; and
  several buildings cleared for one later structure resolve to that one
  parcel, so their identical findings are duplicates on the page and one
  carries the count.)
  **2026-10-17** (volume 35, July – December 1977: 544 OCR pages with text
  out of 580 viewer pages, read in one session by a single reader with no
  sub-agents; 26 meetings, 23 regular and 3 special (the two joint Great
  Highway hearings, which locate nothing, and the residential-zoning
  presentation); 169 findings — 98 decisions, 53 statements of what stood on
  a property, 14 dated past facts, 4 landmark actions. 88 resolved: 71 by the
  EAS join, 17 by hand — by name on a building a page already carries (the
  Castro Theatre, Calvary Presbyterian Church by its 33,497 sq ft lot, Chinese
  Hospital, the Jewish Community Center, the Performing Arts garage parcel)
  and by the record's printed lot (725 and 777 Brotherhood Way, the Fitzhugh
  Building's corner, the Gartland Hotel's site). 81 unresolved: 39 located
  only by a corner, a block or a name, 18 condominiums today (#446), 17 at a
  number EAS does not hold, 5 ranges now split across parcels, and 2 sites
  whose joins the record's lots or acreage refused. 84 published on 51 pages,
  22 of them seeded (one seeded page, 1850 Ocean, was withdrawn when the
  join proved to be the frontage store); 2 declined as already on the page.
  Three conflicts stated in unknowns (950 Pine's year and units, Calvary's
  education-building dates, Mount Zion's Post and Scott building). What the
  pass learned: reading the volume in 45,000-character chunks put twelve
  `raw_text` quotes across a page break, so the quote has to be re-matched
  to one page before the findings file is written — the reader spec now says
  so; condominium conversions are the half-year's business and mostly stay
  unplaced; and a record's printed lot or acreage overruled three joins.)
  **2026-10-18** (volume 36, January – March 1978: 177 OCR pages with text
  out of 276 viewer pages (278 scanned leaves), read in one session by a
  single reader with no sub-agents; 19 meetings, 11 regular and 8 special —
  the joint open-space hearing with the Recreation and Park Commission, the
  Davies Medical Center evening hearing, the condominium-conversion policy
  hearing and five district hearings on the proposed residential zoning map,
  none of which locates a building; the regular meeting of 16 March is not in
  the scan. 39 findings — 36 decisions, 2 statements of what stood on a
  property, 1 landmark action. 12 resolved: 8 by the EAS join, 4 by hand — by
  name on a building a page already carries (CPMC Davies, the Western
  Merchandise Mart, the Abner Phelps House) and by the record's own lot (3904
  lot 2, at Bryant and Alameda). 27 unresolved: 15 condominiums today (#446),
  6 with no street number, 3 at a number EAS does not hold, 2 lots split since,
  and 1850 Ocean's frontage join again refused. 12 published on 12 pages, 3 of
  them seeded; none declined. What the pass learned: the quarter is the
  condominium-conversion quarter — 13 of the 39 findings are conversions; the
  four of January passed unanimously, the seven of February all split, and the Board of Supervisors reversed
  its refusals of 1097 and 1101 Green within a month; two of those joins came
  back as clean exact matches on unit parcels the roll files under `0000`
  with zero lot area, and `resolve_eas.py` now refuses a condominium-class
  parcel with no lot area even where EAS holds its number on that one parcel.)
  **2026-10-19** (volume 37, June – November 1978: 124 OCR pages with text
  out of 246 viewer pages (248 scanned leaves), read in one session by a
  single reader with no sub-agents; 17 meetings — the four June evening
  hearings that closed the citywide residential rezoning (adopted 27 June,
  Resolutions 7995–7997, 47 pages that locate almost nothing), nine regular
  meetings from 20 July to 16 November, and the Neiman-Marcus and Levi's
  Plaza draft-EIR hearings of 14 and 21 November, which are lists of
  speakers. 39 findings — 26 decisions, 11 statements of what stood on a
  property, 2 dated past facts. 27 resolved: 22 by the EAS join, 5 by hand —
  the de Young's ramp on the museum's place page by Golden Gate Park's block
  1700, and by the record's own lot 825 Brotherhood Way (the school and
  church site between 777 and 855), the Quality Inn at 2775 Van Ness (two
  findings; Lot 29 is merged into Lot 30) and 1401 Judah's station, which
  the city now files as 1401 19th Avenue. 12 unresolved: 5 condominiums
  today (#446) — four conversions and 3239 Mission's new seven-unit
  building — 3 with no number (Walden House, Gibraltar Savings' West Portal
  corner, Pier 23), 1 multi-lot site (the BART lots on Santa Rosa Avenue), 2 at numbers EAS no longer holds, and
  1373-79 47th Avenue's two lots taken back by hand. 26 published on 25
  pages, 12 of them seeded; 1 declined (117 Broad, the owner-resident's own
  testimony). What the pass learned: the volume's span label is not its
  content — it skips most of July, September and October; seven
  non-conforming service stations on 19th Avenue were heard as one package
  on 14 September and continued, so they are occupancy facts, not
  decisions; and a reader who copies one of a record's two lots into
  `assessor_lot_as_recorded` hands the resolver a choice the record never
  made — the reader spec now says to leave it empty.)

## Reader spec

The brief every reader of a run gets, verbatim, with its page list and output
path. Earlier runs wrote one each time and kept none; keep this one current
instead, and change it here when a run learns something a reader needs.

- Read **every page** assigned, start to finish; low yield is normal.
- **Date every page from the meeting header on it** or the meeting's opening
  paragraph; binding order is not date order, and a page with no header
  belongs to the meeting of the page before. Any date hint you were given is
  unreliable.
- Output JSON Lines, one finding per line: `volume`, `page` (`n12`),
  `meeting_date`, `date`, `date_precision`, `kind`, `address_as_written`,
  `street_number`, `street_name`, `street_type`, `description`, `extra`,
  `raw_text`, `confidence`; last line `{"_summary": {pages_read, first, last,
  meetings, notes}}`.
- `kind` is one of `planning decision` (dated to the meeting that decided),
  `occupancy` (what stood on or occupied the property at that date — storeys,
  units, beds, floor area, use, the business or institution, a vacant lot),
  `site history` (a dated past fact about the building, at the date and
  precision the page prints), `designation` (landmark or district action).
- **A speaker is not the staff.** Building dates and descriptions come from
  the staff report or the resolution; a date or claim from an applicant,
  neighbour or advocate goes in `extra.reader_note`, not in `description`.
- **A date or number is what the page prints.** Never compute one — not from
  an age, a sequence of resolution numbers or a neighbouring entry; working
  goes in `extra.reader_note`.
- **A Board of Supervisors or Board of Permit Appeals action reported without
  its own date** takes the reporting meeting's date and is framed "By 5 July 1973, the Board of
  Supervisors had approved…"; with its own date, use that.
- **A decision reached at a later meeting belongs to that meeting**; link the
  hearing with `extra.case`, and put the page carrying the address header in
  `extra.header_page`. A postponement, a continuance or a request withdrawn
  before a vote is not a decision.
- A proposal alone is not a finding; the staff's statement of what stood on
  the property is, even if the case was never decided.
- `address_as_written` is copied as printed; **never fix a number** — if the
  resolution prints it differently from the header, say so in
  `extra.reader_note`. `street_number` is the low number only; a range goes in
  `extra.address_range_as_recorded`. `street_name` is uppercase as EAS holds
  it (`24TH`, `19TH` with type `AVE`, `O'FARRELL`, `ARMY` as printed in 1973).
- No street number? Still write the finding: the printed block and lot in
  `extra.assessor_block_as_recorded` / `assessor_lot_as_recorded` (block 4
  digits, lot 3), a named building in `extra.building_name`, a bearing in
  `side`, `cross_street_name`, `direction`, `offset_ft`. Put the block and lot
  on numbered findings too, where printed for that property. **Several
  lots printed?** Put the block alone and the lots in
  `extra.assessor_lots_as_recorded` (`"10A; 11"`); the resolver treats the
  lot field as the record's choice of one parcel.
- `extra.record_date` is always the meeting date.
- `description` in your own words, past tense, one or two sentences; never
  refer to the source ("the minutes say", "the staff report"); include the vote
  where printed.
- `raw_text` is the shortest verbatim span (≤ 250 characters, copied exactly
  from the page file) that justifies the fact, chosen to contain no personal
  name. It is checked mechanically against the page. **It must sit on one
  page** — a reader working from concatenated pages will pick spans that run
  across a page break, and `page` must be the page the span is on.
- **No personal name in any field**: not applicants, owners, attorneys,
  objectors, improvement-club officers, commissioners or staff. The architect
  of a building may go in `extra.reader_note` as "architect: <name>". A
  business trading under a person's own name goes with the person. Keep
  companies, institutions, churches, schools, hospitals, unions, government
  bodies and named buildings.
- Skip 100 Larkin Street and any other meeting venue, citywide plans, text
  amendments, district rezonings, and street vacations — unless the passage
  pins a fact to one property.

