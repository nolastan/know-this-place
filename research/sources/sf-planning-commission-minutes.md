# sf-planning-commission-minutes — Minutes of the San Francisco City Planning Commission (primary)

> **Research dossier.** Rules: [../AGENTS.md](../AGENTS.md) · traps:
> [../LESSONS.md](../LESSONS.md) · register:
> [../SOURCES.md](../SOURCES.md) · cited on pages by the source id `sf-planning-commission-minutes`.
>
> - **Kind:** meeting minutes (scanned volumes) · **Tier:** primary · **Status:** open
> - **Search-invisibility:** high — see the register for what that rates.
> - **Coverage:** 14 of 53 volumes read (July 1968 – December 1971): 3,521
>   pages, 1,150 findings, 567 resolved, 539 published on 264 distinct pages. 39 volumes
>   remain — 1972–1980 and 1994–2005.
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
- **Where:** The San Francisco Public Library contributed 53 volumes to the
  Internet Archive, digitized under a California State Library Califa/LSTA
  grant. Identifiers are of the form `<n>minutesofsanfran<year>san[f]`, where
  `<n>` runs 6 to 58 in date order; the volume's own span is in its
  `volume` metadata field (`July-Sept 1968`), never in `date`, which is
  usually empty.

| volumes | span | state |
|---|---|---|
| 6–11 | July 1968 – December 1969, one quarter each | **read in full** 2026-10-06 |
| 12–15 | January – December 1970, one quarter each | **read in full** 2026-10-09 |
| 16–19 | January – December 1971, one quarter each | **read in full** 2026-10-10 |
| 20–39 | 1972–1980 (quarters to 1973, then halves, then whole years) | unread |
| 40–58 | 1994–2005 | unread |
| — | 1981–1993 | in no volume; 31 is missing from the sequence |
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
  into `findings/sf-planning-commission-minutes/minutes-1971.json`. Nothing
  of those volumes is known to remain unread. **Next: volume 20
  (January–March 1972) and onwards**, four quarterly volumes a run (one year,
  about 1,100 text pages, ten readers of ~110 pages each, about six minutes);
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
