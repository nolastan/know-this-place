# sf-recreation-park-minutes — Minutes of the San Francisco Recreation and Park Commission (primary)

> **Research dossier.** Rules: [../AGENTS.md](../AGENTS.md) · traps:
> [../LESSONS.md](../LESSONS.md) · register:
> [../SOURCES.md](../SOURCES.md) · cited on pages by the source id
> `sf-recreation-park-minutes-<meeting date>`, e.g. `sf-recreation-park-minutes-1950-07-27`.
>
> - **Kind:** meeting minutes (scanned volumes, Internet Archive OCR) · **Tier:** primary · **Status:** open
> - **Search-invisibility:** high — one OCR text per volume, indexed only by a typed card index at the front of some volumes.
> - **Coverage:** Recreation Commission January 1948 – June 1950 and Recreation and Park Commission June 1950 – December 1952 and 1954–80 read (thirty-one volumes). Recreation Commission 1941–44, Park Commission 1947–50 (maintenance-heavy) and Recreation and Park Commission 1981–1995 unread; the 1953 items have no scans.
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
  2026-11-25 (1959, `minutesrecreatio1959sanf`: 10 findings on 8 pages. The
  Golden Gate Park tennis clubhouse (built by Clovis, named for William M.
  Johnston) and bowling green clubhouse, the Hall of Flowers contract
  (Midstate, $542,000), Jackson Playground's rehabilitation (Schubart &
  Friedman; Biltwell), McCoppin Square, Storyland's designer Donald G.
  Clever, the Clement Street courts renamed for Margaret Osborne duPont, and
  part of the restored Palace of Fine Arts promised to Walter S. Johnson.)
  2026-11-25 (1960, `minutesrecreatio1960sanf`: 9 findings on 9 pages. The
  Diamond Heights recreation areas named for Mayor George Christopher and
  for the commission's president Walter A. Haas; Helen Wills and McCoppin
  Square field houses; the Hall of Flowers, Noble Collection and Rose Garden
  dedications; the Japanese stone monument in Lincoln Park; McLaren Park's
  land acquisition cleared. Learned: from 1959 the page footers are in slash
  form ("11/10/60") and match the meeting.)
- 2026-11-25 · 1961-62 volumes (`minutesrecreati1961sanf_0`, `minutesrecreati1962sanf_0`)
  read by passage: 10 findings (rec-park-1961, rec-park-1962). (Got: Vincent
  G. Raney's McLaren Park playground and yard, the Hahn and Visitacion
  playground plans by William Gladstone Merchant & Associates, the Swiss Flower
  Clock dedication, the Queen Wilhelmina Garden name, Garrigan Field. Learned:
  by 1961 building contracts are let by the Department of Public Works, so the
  minutes carry approvals and names but few contracts; yield fell to about five
  findings a volume.)
- 2026-11-25 · 1963-64 volumes (`minutesrecreatio1963sanf`, `minutesrecreati1964sanf_0`)
  read by passage: 12 findings (rec-park-1963, rec-park-1964). (Got: the
  Allyne property fight of 1964, Raymond Kimbell Playground named, Ferry
  Building Park consultants and preliminary design (Halprin, Bolles, Ciampi),
  the Palace of Fine Arts restoration bid over budget, gifts of plans for the
  Strybing kiosk (Gardner Dailey) and the zoo's Orangutan Grotto. Learned:
  the meeting openers ("called to order ... on Thursday, <date>") are the
  reliable dates; OCR turns 28 into 20.)
- 2026-11-25 · 1965 volume (`minutesrecreatio1965sanf`) read by passage: 8
  findings (rec-park-1965). (Got: the Allyne property bought for $380,000,
  the Heritage Council's fight for the house, and its demolition at 2609 Gough
  Street; Herz Playground, the Golden Gate Park Senior Center and the Garden
  of Fragrance dedicated; zoo plans by J. Francis Ward and Corlett and
  Spackman. Held: the Civic Center Plaza competition, no page.)
- 2026-11-25 · 1966 volume (`minutesrecreatio1966sanf`) read by passage: 8
  findings (rec-park-1966). (Got: Alice Marble courts, Louis Sutter
  Playground and the McLaren Park names, the Washington Square garage approved
  in principle, the Hidalgo bell plaza in Dolores Park, the Japantown Peace
  Pagoda accepted. Held: John F. Kennedy Drive named, no page.)
- 2026-11-25 · 1967 volume (`minutesrecreatio1967sanf`) read by passage: 7
  findings (rec-park-1967). (Got: Vaillancourt's fountain for Embarcadero
  Plaza, Coffman Pool named, the Cowell Hall site set apart, the Marina harbor
  restaurant, Garfield Square's community plan, Alice Marble courts dedicated.)
- 2026-11-25 · 1968 volume (`minutesrecreatio1968sanf`) read by passage: 7
  findings (rec-park-1968). (Got: the McLaren Park amphitheater's architects,
  the Portsmouth Square bridge from the Chinese Cultural Center approved in
  principle, Bay View pool and bathhouse, zoo aviary, Strybing work center.)
- 2026-11-25 · 1969 volume (`minutesrecreatio1969sanf`) read by passage: 7
  findings (rec-park-1969). (Got: the Helen Crocker Russell Library, the
  McLaren amphitheater's final plans, Raney's Palace of Fine Arts theater
  agreement, the Landmarks Board's windmill certificate and Conservatory
  proposal. Learned: the index fills the first ~26,000 lines and few meeting
  openers survive OCR; date by footers.)
- 2026-11-25 · 1970 volume (`minutesrecreatio1970sanf`) read by passage: 7
  findings (rec-park-1970). (Got: the Palace of Fine Arts little theater's
  plans and Walter S. Johnson's $250,000, the McLaren amphitheater contract,
  the Coit Tower road made a public street, Strybing's John Muir Trail and
  Demonstration Gardens. Learned: from 1970 the openers read "The Four
  Hundred ... Regular Meeting ... called to order ... on Thursday, <date>".)
- 2026-11-25 · 1971 volume (`minutesrecreatio1971sanf`) read by passage: 7
  findings (rec-park-1971). (Got: dedications of the Christopher and Sunnyside
  recreation centers, the McLaren amphitheater and the first mini-parks; the
  Chinese Playground play area by Eckbo, Dean, Austin and Williams; the Music
  Concourse fountains restored.)
- 2026-11-25 · 1972 volume (`minutesrecreatio1972sanf`) read by passage: 6
  findings (rec-park-1972). (Got: John Pflueger's Academy master plan with
  the fish roundabout, a preservation grant sought for the Conservatory,
  Raney's Palace of Fine Arts lobby and marquee, the West Portal station plan.)
- 2026-11-25 · 1973 volume (`minutesrecreatio1973sanf`) read by passage: 6
  findings (rec-park-1973). (Got: the Palace colonnades restored by Walter S.
  Johnson, the Buchanan Street Mall by Sasaki, Walker, Ridgetop Plaza, the
  zoo's animal hospital. Learned: from 1973 contract awards are recorded
  again, but mostly small maintenance jobs.)
- 2026-11-25 · 1974 volume (`minutesrecreatio1974sanf`) read by passage: 6
  findings (rec-park-1974). (Got: architects for the Chinese Playground
  building (EDAW), the Golden Gate Park Senior Center (Germano Milono) and the
  Children's Playground (Michael Painter); the zoo hospital and Alice Eastwood
  Garden dedicated; Walter Johnson's theater lobby gift.)
- 2026-11-25 · 1975 volume (`minutesrecreatio1975sanf`) read by passage: 10
  findings (rec-park-1975). (Got: Koshland Park's plans, the Palace colonnades
  and Justin Herman Park's second phase dedicated, Taipei's offer of the
  Chinese Pavilion, the de Young renovation, the MLK Pool enclosure, the
  Sharon Building fire repairs.)
- 2026-11-25 · 1976 volume (`minutesrecreatio1976sanf`) read by passage: 5
  findings (rec-park-1976). (Got: Esherick, Hornsey, Dodge and Davis's zoo
  plan adopted, architects for the Jackson Playground field house, Noe Valley
  Courts and the Senior Center remodel, Osmundson for McLaren Park.)
- 2026-11-25 · 1977 volume (`minutesrecreatio1977sanf`) read by passage: 13
  findings (rec-park-1977). (Got: the July batch of architects' agreements for
  Crocker-Amazon, James Rolph, Galvez, Duboce and Helen Wills; Youngblood-
  Coleman Playground and James P. Lang Field named; the Key statue
  rededicated; the MLK Pool enclosure finished. Learned: Galvez Playfield is
  today's Youngblood-Coleman Playground.)
- 2026-11-25 · 1978 volume (`minutesrecreatio1978sanf`) read by passage: 10
  findings (rec-park-1978). (Got: Moscone Playground and the Harvey Milk
  Center named in December; the rebuilt Mary B. Connolly Children's
  Playground, Heidelberg Hill, Ridgetop (Hilltop) Park and Rochambeau
  dedicated; Alamo Square and Excelsior Playground architects. Learned: the
  1970s "Ridgetop Park" is today's Hilltop Park, next to Ridgetop Plaza.)
- 2026-11-25 · 1979 volume (`minutesrecreatio1979sanf`) read by passage: 8
  findings (rec-park-1979). (Got: Dorothy Erskine Park and Youngblood-Coleman
  dedicated, Shoreview Park named, West Portal and Herz rededicated, Del Campo
  Associates' Mission Community Recreation Center program plans. Knudsen-Bloom
  still unplaced.)
- 2026-11-25 · 1980 volume (`minutesrecreatio1980sanf`) read by passage: 13
  findings (rec-park-1980). (Got: the Oliver C. Chang Recreation Building,
  Pieretti Field, Duboce and Alamo Square rededications, Margaret Hayward and
  Moscone designs, Central City (Boeddeker) Park taken by eminent domain on
  Block 332. Knudsen-Bloom contract let at $869,320, still unplaced.)
