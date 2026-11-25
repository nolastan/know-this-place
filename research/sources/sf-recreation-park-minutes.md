# sf-recreation-park-minutes — Minutes of the San Francisco Recreation and Park Commission (primary)

> **Research dossier.** Rules: [../AGENTS.md](../AGENTS.md) · traps:
> [../LESSONS.md](../LESSONS.md) · register:
> [../SOURCES.md](../SOURCES.md) · cited on pages by the source id
> `sf-recreation-park-minutes-<meeting date>`, e.g. `sf-recreation-park-minutes-1950-07-27`.
>
> - **Kind:** meeting minutes (scanned volumes, Internet Archive OCR) · **Tier:** primary · **Status:** open
> - **Search-invisibility:** high — one OCR text per volume, indexed only by a typed card index at the front of some volumes.
> - **Coverage:** Recreation Commission January 1948 – June 1950 and Recreation and Park Commission June 1950 – December 1952 and 1954–58 read (nine volumes). Recreation Commission 1941–44, Park Commission 1947–50 (maintenance-heavy) and Recreation and Park Commission 1959–1995 unread; the 1953 items have no scans.
> - **Local corpus:** `research/corpora/sf-recreation-park-minutes/` (IA `_djvu.txt`, one per volume, gitignored)
>
> Update this dossier at the end of every pass — the `Verified:` line, the
> coverage note, and anything the pass learned about getting at the source.

- **What:** The commission that runs the city's parks, playgrounds and
  recreation centers. Its minutes are in the SFPL collection on the Internet
  Archive: `minutesrecreatio1947sanf` to `…1995sanf` (with gaps), `minutesrecreati<year>sanf_N`
  duplicates and partial volumes, and the earlier Recreation Commission volumes
  (`minutesrecreati1941sanf_1`, 1941-44). The Board of Park Commissioners'
  minutes (`minutesboardofpa<year>sanf`, 1870 and 1896-1942) and annual reports
  (`annualreportofbo<year>sanf`, 1889-1924) are the parks' record before the
  1950 merger and are a separate, unread seam.
- **Why it matters here:** most of the 227 park and playground place pages had
  no history at all. The minutes give each playground its dated record: the
  1947 recreation bond program's field-house contracts (contractor and price),
  demolitions on new sites, namings and renamings, dedications.
- **Getting at it:** `https://archive.org/download/<id>/<id>_djvu.txt`. The
  `minutesrecreatio1950sanf` volume opens with a card index by place (the
  dates and page numbers fall in separate OCR columns, so use it to find
  events, not to date them). Meetings start "The <Nth> Regular Meeting of the
  Recreation and Park Commission was called to order on <Weekday>, <Month> <d>"
  — often with no year; `/mnt/project-files/sf-recreation-park/split.py` splits
  on that phrase and carries the year forward. Some headings are lost to OCR
  (the meeting of 23 August 1951 reads "Recreation and , Park oommission"),
  so the text of a missed meeting falls into the previous one: date each
  finding by the page-footer dates ("8-23-51") near it, not by the split alone.
- **What to take:** contract awards for buildings (field houses, clubhouses,
  recreation buildings, alterations), with the contractor (a firm) and the
  price; demolitions on park sites; resolutions naming or renaming a place;
  dedications, said as scheduled unless the index or a later meeting records
  them held. Leave out payments, leases, concessions, staff matters and the
  names of private people who wrote in.
- **Verified:** 2026-11-25 (June 1950 – December 1951: 23 findings on 21
  place and address pages — field houses at Silver Terrace, West Portal, Aptos
  and Grattan, McLaren Lodge's conversion to the department's offices, the
  Golden Gate Park Golf Course and Cow Hollow Playground named, the Randall
  Museum named for Josephine D. Randall, the Japanese Tea Garden's name, and
  the 1951 dedications of the bond-program playgrounds.)
  2026-11-25 (Recreation Commission, January 1948 – June 1950, items
  `minutesrecreatio1948sanf` and `minutesrecreati1950sanf_3`: 33 findings on
  22 pages. These cover the 1947 recreation bond program from the start:
  William G. Merchant's architect contracts for nearly every new field house
  and recreation center, the construction contracts (Burnett/Joseph Lee,
  Peixotto, Cayuga, J. P. Murphy, South Sunset, Byxbee/Merced Heights,
  Miley/Cow Hollow, Longfellow/Alice Chalmers, Presidio Heights, the Chinese
  Recreation Center, and one $842,000 contract for the Potrero Hill, Ocean
  View, St. Mary's and Sunset centers), and the playgrounds' namings.
  Learned: the 1948 volume holds 1948 and 1949, and its meeting headings
  give a weekday but often no year or a garbled one. The commission met on
  Thursdays, so check the weekday, the resolution-number order and the
  bid-opening dates ("proposals submitted November 1") against each
  heading. A missed heading leaves its meeting under the previous date.
  `minutesrecreatio1947sanf` and `…1949sanf` are the separate Park
  Commission's minutes, mostly maintenance contracts.)
  2026-11-25 (Recreation and Park Commission, 1952, `minutesrecreatio1952sanf`:
  28 findings on 25 pages. The official list of the 1951 dedications, which
  places the June 5, 1951 Richmond dedication on Richmond Playground (18th
  Avenue between Lake and California); the September 1952 architect contracts
  for the next bond projects (Mooser & Gloe for Duboce Park's Central
  Activities Building, Appleton & Wolfard for Eureka Valley, Mooser for
  Junipero Serra, Ryan & Lee for Laurel Hill, Strothoff for Hayward); the
  Argonne field house; Grattan's dedication; the Japanese Tea Garden name
  restored; the Frank Marini Memorial; the Strybing master plan; the Palace
  of Fine Arts demolition question. Learned: this volume's meeting headings
  are mostly unreadable, but its card index gives each resolution's date and
  page, and every page carries a footer date like "9-25-52". Date from those.
  Where the minutes record an earlier event, convert.py takes
  "event@meeting" dates so the entry sits on the event's day and cites the
  meeting.)
  2026-11-25 (1954, `minutesrecreati1954sanf_0`, and 1955,
  `minutesrecreatio1955sanf`: 17 findings on 14 pages. Construction
  contracts for the last 1947 bond buildings (Laurel Hill, Hamilton, Hayward,
  Eureka Valley, North Beach, Upper Noe, the Recreational Arts Building in
  Duboce Park), the Balboa Park stables made a clubhouse, the two planned
  indoor pools moved to Balboa Park and Garfield Square, the Chinese-American
  War Memorial in St. Mary's Square, Kezar's press box, the Hall of Flowers
  architects. Learned: the 1954 card index is too broken by OCR to parse, so
  scan the minutes for "Award of Contract", dedications and namings, and date
  by page footer. The two 1953 items (`minutesrecreatio1953sanf`, `minutesrecreati1953sanf_0`) carry no scan or text files, so 1953 cannot be read.)
  2026-11-25 (1956, `minutesrecreati1956sanf_0`: 11 findings on 9 pages. The
  1947 bond fund ran out: the Garfield and Rossi pools were let without their
  buildings; Balboa Park's pool and center (Reimers; Engstrum & Nourse); Pine
  Lake's field house; the Eureka Valley naming dispute (playground kept its
  name, ball field named for Monsignor Leo W. Powleson) and dedication; the
  North Beach pool; the Columbus statue offer for Telegraph Hill.
  `minutesrecreatio1956sanf` has no text file. The April 26, 1956 table of
  architects for the 1955 bond projects (Res. 2262) is unreadable OCR.)
  2026-11-25 (1957, `minutesrecreati1957sanf_0`: 17 findings on 14 pages. The
  1955 bond program's first contracts (Larsen and McLaren pools, Balboa
  soccer bleachers, Funston and Silver Terrace bleachers), Hayes Valley's
  architect and site clearance, Storyland, the Hall of Flowers final plans,
  the Mosias tennis and bowling clubhouses, the Balboa diamonds named for
  August Sundberg and Maurice J. Sweeney, the Kezar press box named for
  William M. Coffman, the Mountain Lake de Anza plaque, and the Upper Noe
  dedication. Learned: in this volume the page footers are often invoice
  dates, so date by the "San Francisco, California <date>" line that opens
  each meeting. `minutesrecreatio1957sanf` has no text file.)
  2026-11-25 (1958, `minutesrecreatio1958sanf`: 7 findings on 6 pages.
  Washington Square's improvement contract, Hayes Valley's site clearance and
  construction contract, the Lake Merced Sports Center, the Cayuga clubhouse
  extension, Strothoff for the Conservatory, the Balboa Park pool's opening.
  Learned: each meeting opens "The …th Regular Meeting … was called to order
  … on Thursday, <date>", followed by "Minutes of the Regular Meeting of
  <date> were approved"; together with the bid-opening dates they date every
  item even where the heading's date is lost. Portola Playground (Res. 3276)
  held back: unclear which present page it is.)
