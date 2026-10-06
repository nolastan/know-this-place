# sf-planning-commission-minutes — Minutes of the San Francisco City Planning Commission (primary)

> **Research dossier.** Rules: [../AGENTS.md](../AGENTS.md) · traps:
> [../LESSONS.md](../LESSONS.md) · register:
> [../SOURCES.md](../SOURCES.md) · cited on pages by the source id `sf-planning-commission-minutes`.
>
> - **Kind:** meeting minutes (scanned volumes) · **Tier:** primary · **Status:** open
> - **Search-invisibility:** high — see the register for what that rates.
> - **Coverage:** 6 of 53 volumes read (July 1968 – December 1969): 957 pages,
>   286 cases, 372 findings, 163 resolved, 162 published on 91 pages. 47
>   volumes remain — 1970–1980 and 1994–2005.
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
| 12–39 | 1970–1980 (quarters to 1973, then halves, then whole years) | unread |
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
  page separators, and a citation has to name a page. Dropping the leaves
  `scandata.xml` marks `addToAccessFormats>false` (two colour cards per volume,
  the first and the last) makes the index position equal the Internet Archive
  viewer's own page number, so the citation URL is
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
  `findings/sf-planning-commission-minutes/minutes-1968-1969.json`. Nothing of
  those volumes is known to remain unread. **Next: volume 12 (January–March
  1970) and onwards**, one or two volumes a run; the 1994–2005 volumes are a
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
