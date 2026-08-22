# argonaut-sfhs — *The Argonaut*, journal of the SF Historical Society (secondary)

> **Research dossier.** Rules: [../AGENTS.md](../AGENTS.md) · register:
> [../SOURCES.md](../SOURCES.md) · cited on pages by the source id `argonaut-sfhs`.
>
> - **Kind:** journal (print, per-article PDFs) · **Tier:** secondary · **Status:** open
> - **Search-invisibility:** high — see the register for what that rates.
> - **Coverage:** Volumes read are listed below; the run continues.
> - **Local corpus:** `research/corpora/argonaut-sfhs/`
>
> Update this dossier at the end of every pass — the `Verified:` line, the
> coverage note, and anything the pass learned about getting at the source.

- **What:** *The Argonaut: Journal of the San Francisco Historical Society*, a
  twice-yearly peer-reviewed local-history journal. Articles are researched from
  the city directories, period newspapers, corporate records and family papers,
  and they name streets and buildings constantly. Volumes read into the repo so
  far:
  - **29 no. 2 (Winter 2018)** — Robert Bardell, "The Presidio & Ferries
    Railroad" (pp. 6–33); Robert Cherny, "A New Eyewitness Account of the 1906
    Earthquake" (pp. 34–43); Ken Sproul, ed., "Letter by William Hindshaw"
    (pp. 44–55).
  - **30 no. 1 (Summer 2019)**, the Midwinter Fair issue — Taryn Edwards,
    "Before the Midwinter Fair: The Mechanics' Institute's 'Pacific Rim'
    Industrial Exhibitions of 1869 and 1871" (pp. 8–23); Lee Bruno, "The Winter
    of Our Dreams" (pp. 24–33); Lorri Ungaretti, "A Look at the Midwinter Fair"
    (pp. 34–65); Rodger C. Birt, "A Rare Midwinter Exposition Artifact"
    (pp. 66–71); Sofia Herron Geller, "Art Activism" (pp. 74–79).
  - **30 no. 2 (Winter 2020)** — Vincent Ring, "A Second Tunnel for The Sunset"
    (pp. 6–21); Hudson Bell, "The Last Bastion of San Francisco's Californios:
    The Mission Dolores Settlement, 1834–1848" (pp. 22–41); Peter M. Field,
    "A Tenderloin District History: The Pioneers of St. Ann's Valley: 1847–1860"
    (pp. 42–83).
  - **31 no. 1 (Summer 2020)** — Stefanie E. Williams, "The Rise and Decline of
    the German-Speaking Community in San Francisco, 1850–1924" (pp. 6–51);
    William R. Huber, "Sutro's San Francisco—What's Left?" (pp. 52–71); Alan
    Ziajka, "World War I and the University of San Francisco" (pp. 72–80).
  - **31 no. 2 (Winter 2021)**, the Black San Francisco issue — James L.
    Taylor, "Introduction: A Paradigm for Civil Rights in California"
    (pp. 6–11); Paul Gutierrez, "Mary Ellen Pleasant's Quest for Equality for
    All" (pp. 12–27); Lee Bruno, "We Are Brethren: San Francisco's
    19th-century African American Newspapers' Relentless Pursuit of Liberty and
    Justice" (pp. 28–41); Hudson Bell, "Exodus: San Francisco's Black Community
    in the 1850s" (pp. 42–53); Philip M. Montesano, "San Francisco Black
    Churches in the Early 1860s: Political Pressure Group" (pp. 54–61); Rodger
    C. Birt and Charles Wong, "The Western Addition District: Documentary
    Project" (pp. 88–103); Winnie Quock, "Botany and Horticulture: Symbols of
    Flourishing Against the Odds" (pp. 106–110).
  - **32 no. 1 (Summer 2021)** — Angus Macfarlane, "Putting San Francisco on
    the Map, Part 1: A Riddle Wrapped in a Mystery, Inside an Enigma"
    (pp. 8–29); Gary F. Kurutz, "Woodward's Gardens: Robert B. Woodward's
    'Central Park of the Pacific'" (pp. 30–63); Lisa Dunseth, "The Junior
    Recreation Museum in Balboa Park: The Brainchild of Josephine Randall and
    Bert Walker" (pp. 64–80).
- **Format:** print journal; no API and no per-article URL. Cite author,
  article title, volume, issue, season, year and page range. Publisher: San
  Francisco Historical Society, P.O. Box 420470, San Francisco, CA 94142-0470.
- **Use for:** what a site was before its present building — a car barn, a
  factory, a pleasure resort — and for dated events (a house reported nearly
  completed, a service that ended). Record each as one `historical_record`
  entry, usually `"kind": "site history"`.
- **Cautions:**
  - **Most of what it names has no street number.** These articles locate
    things by corner ("Union and Laguna," "Fillmore and Bay") or by landmark
    ("the site of today's Marina Safeway"). Nothing here resolves a corner to a
    parcel without guessing, so those get no page — the same rule as
    `hittell-1878`.
  - **Numbered addresses still have to clear EAS.** 847 Valencia Street and 616
    Filbert Street, both named in the Winter 2018 volume, have no modern EAS
    record; under the directory contract that is the end of the matter.
  - **A demolished building can take its number with it.** The Summer 2021
    volume gives 600 Ocean Avenue as the address of the Junior Recreation
    Museum's original home in Balboa Park, which it says was demolished for
    freeway construction. EAS has no record of 600 Ocean Avenue today — the
    number itself didn't survive the building — so it gets no page, the same
    outcome as a corner that never had a number at all. 1661 Octavia Street,
    Mary Ellen Pleasant's "House of Mystery" in the Winter 2021 volume, goes
    the same way: no EAS record, and no active parcel range on Octavia covers
    the number (1650 and 1700 are the nearest).
  - **A nineteenth-century street number is not a modern one.** The Winter 2021
    volume gives 273 Washington Street for the Atheneum Institute and locates
    it on Washington between Stockton and Powell. Today's 273 Washington would
    be eight blocks east, between Battery and Front, and EAS has no such
    address in any case. 184 Clay Street "at Kearny" and 119 Merchant Street
    "between Montgomery and Kearny" fail the same way — EAS's Merchant Street
    now begins at 408. A number that contradicts its own cross-streets is a
    pre-renumbering address, not a second building and not a resolvable one.
  - **A city survey name can resolve a segment the volume leaves open.** The
    same volume puts Third Baptist's first church on "Dupont (now Grant Avenue)
    between Greenwich and Filbert," with no number. Planning's `3tsw-4idn`
    names parcel 0087009 — 1640–1644 Grant Avenue — `SITE OF FIRST COLORED
    BAPTIST CHURCH; TH`, and SF Planning's landmark designation report for the
    congregation cites the State DPR registration application for "1642-44
    Grant Avenue." No guessing is involved, so it gets a page. Query the `name`
    field on candidate parcels before writing a segment off.
  - **A congregation's present address resolves what its history doesn't.** The
    Winter 2021 volume locates the three churches formed in 1852 by corner and
    segment throughout — Scott Street, Powell between Jackson and Pacific,
    Stockton between Clay and Sacramento — and then gives each congregation's
    present-day numbered address. Those three clear EAS and become pages
    (1399 McAllister, 970 Laguna, 2155–2159 Golden Gate); the nineteenth-century
    corners behind them do not. The page is about the building at the modern
    number; the earlier sites are `historical_record` entries on it.
  - **Golden Gate Park is one parcel.** Parcel 1700001 carries more than sixty
    EAS addresses, among them the de Young Museum at 50 Hagiwara Tea Garden
    Drive, the Japanese Tea Garden at 75, and the California Academy of Sciences
    at 55 Music Concourse Drive. A page on that parcel would describe the park,
    not any of them, so the Winter 2021 volume's whole Golden Gate Park walking
    tour lands on no page — the same outcome as the SFSU campus below.
  - **The journal isn't only about San Francisco.** The Summer 2021 volume
    follows General Vallejo to Casa Grande in Sonoma and Robert Woodward to
    Oak Knoll in Napa County. Both are real, dated, numbered-enough facts, and
    neither gets a page here — this site covers San Francisco only.
  - **Its dates will disagree with the assessor.** Bardell dates the Casebolt
    house to a March 1868 newspaper report; the roll and Planning both say 1865.
    Record both and name the disagreement in `.unknowns` — never adjudicate.
  - **A relocated building is a claim about a structure, not a parcel.** Where
    the journal says a house was moved to an address, say so and leave the
    roll's year built standing beside it.
  - **A whole block named by the building on it today is resolvable; a corner
    is not.** The Summer 2019 volume puts the Mechanics' Institute's exhibition
    building on "the block that now contains the Bill Graham Civic Auditorium."
    That block is one parcel (0812001) carrying one EAS address, 99 Grove
    Street, which SF Planning names `EXPOSITION AUDITORIUM` — no guessing is
    involved, so it gets a page. "Larkin and Grove," a corner of the same block,
    still doesn't.
  - **A volume can contradict itself about a site.** The Summer 2019 volume
    describes the pavilion of the 1868–71 exhibitions as being at Union Square
    *and* at Larkin and Grove, which is where the 1882 building went. Record
    only what a page can support and leave the conflation alone.
  - **A named present-day building resolves a street segment; two named
    buildings resolve nothing.** The Winter 2020 volume puts Jonathan
    Kittredge's 1855 house on "the north side of Ellis Street between Powell and
    Mason" and adds that the property is now the Hotel Fusion. The hotel gives
    its own address as 140 Ellis Street — parcel 0326023, on the even-numbered
    (north) side of that block, which the EAS coordinates confirm — so the
    segment resolves without guessing and gets a page. The same volume puts an
    1847 pond at "Powell, Eddy, Market and Fifth" and names **two** present-day
    buildings for it, the Flood Building and San Francisco Centre. One
    intersection, two buildings, four corners: that resolves to no parcel, the
    same as "Larkin and Grove."
  - **A tunnel, a proposed route and a settlement are not parcels.** Most of the
    Winter 2020 volume is about things no parcel can hold — the Sunset Tunnel's
    bore under Buena Vista Park, two portals at Merrit/Danvers and Cole/Alma
    that were never built, a dedication crowd at an intersection, and the
    Mission Dolores and Yerba Buena settlements. A whole article can name places
    constantly and still yield nothing; record the pass and move on.
  - **A street number in the journal can point at the wrong building.** The
    Summer 2020 volume gives the German House as 624 Polk Street. 624 Polk is
    parcel 0741006B, which SF Planning names `MAYFAIR HOTEL` and dates to 1928.
    Every other detail in the same entry — the cornerstone ceremony at Polk and
    Turk, five storeys, completion in 1912, the landmark designation — matches
    0742002 across the street, which Planning names `CALIFORNIA HALL` and dates
    to 1912. Check a number against the parcel before taking it: a number that
    contradicts its own entry is a transcription error, not a second building.
  - **A campus is one parcel, and a floor of one building on it is not a page.**
    The volume puts the Sutro Library on the fifth and sixth floors of the
    J. Paul Leonard Library at 1600 Holloway Avenue. EAS gives 7299005 for that
    address, a retired APN; the parcel that exists now is 7299006, the whole
    3.9-million-sq-ft SFSU campus carrying three EAS addresses. A page there
    would describe the campus, not the library, so it gets none. The library's
    earlier home at 480 Winston Drive is its own parcel and does.
  - **An exempt public parcel reads as vacant on the roll.** 7298008 (470–480
    Winston Drive) is `Vacant Lot Public Use` with no building area, no year
    built and no assessed value in every roll year from 2007 through 2025 —
    including the years the Sutro Library was open on it. On land exempt from
    the secured roll the classification records the exemption, not what stands
    on the ground. Say that; never report the parcel as empty.
  - **People.** These articles are full of private individuals — earthquake
    survivors, families, children in an orphanage. Take the businessmen,
    builders and public figures the historical record already covers; leave
    everyone else out, per the root `AGENTS.md`.
- **Citation label:** "Author, 'Article title,' *The Argonaut: Journal of the
  San Francisco Historical Society*, vol. N, no. N (Season Year), pp. N–N"
- **Verified:** 2026-08-06 (vol. 29 no. 2, Winter 2018: 17 places named, 3 of
  which resolve to an EAS address — 440–444 Jackson, 2727 Pierce, 2460 Union.
  vol. 30 no. 1, Summer 2019: 12 places named, 3 of which resolve — 57–65 Post,
  1 Montgomery, 99 Grove. The other nine are located by corner, by street
  segment or by park feature: Montgomery between Post, Sutter and Kearny; Bush
  Street; 8th Street between Mission and Market; Larkin and Grove; Pier 70 /
  First and Mission; the Music Concourse; the Administration Building site at
  its western end; the Fine Arts Building site; and Strawberry Hill)
- **Verified:** 2026-08-11 (vol. 31 no. 1, Summer 2020: 36 places named, 7 of
  them with a street number, 2 of which become pages — 601–625 Polk, which the
  volume gives as 624 Polk, and 470–480 Winston Drive. Of the other five
  numbered addresses, 526 California, 117 Capp and 304 Turk have no EAS record;
  141 Albion is now five condominium parcels and is held back under the
  condominium rule in AGENTS.md; and 1600 Holloway is the whole SFSU campus
  parcel. The remaining 29 are located by corner, by street segment, by park
  feature or by venue name — Temple Emanu-El on Sutter, Belden Place, Woodward's
  Gardens, 18th near Valencia, 15th and Mission, 20th and Folsom, Army Street,
  Golden Gate Avenue, O'Farrell and Gough, Eddy and Gough, Sutter near
  Divisadero, Third and Market, the Golden Gate Park bandstand, Eighth and
  Brannan, Sutro Heights, the Cliff House, Sutro Baths, 48th and Point Lobos,
  the Sutro Depot, the Battery Street warehouse, the Montgomery Street offices,
  22nd near Howard, Turk Street, 12th and Folsom, Sutter Street, 2nd between
  Howard and Folsom, Hayes and Shrader, Fulton and Parker — and one, the
  Deutsches Altenheim, is in Oakland)
- **Verified:** 2026-08-11 (vol. 30 no. 2, Winter 2020: 16 places named, **none
  of them with a street number**, and 1 of which resolves — 140 Ellis Street,
  reached through the present-day hotel the volume names on the site. The other
  15 are corners, street segments, an intersection, a tunnel alignment, two
  portals that were never built and two settlements: Mason between Eddy and
  Ellis; Powell/Eddy/Market/Fifth; Ellis between Stockton and Powell; Powell and
  Ellis; Turk and Polk; Eddy between Market and Mason; Geary and Mason; Market
  between Fourth and Fifth; O'Farrell between Mason and Taylor; O'Farrell
  between Taylor and Jones; Taylor and Eddy; the Merrit/Danvers and Cole/Alma
  portals; the Duboce Avenue tunnel route; 48th and Judah; the Mission Dolores
  settlement; and Yerba Buena. The Ring and Bell articles land on no page)
- **Verified:** 2026-08-12 (vol. 32 no. 1, Summer 2021: 10 places named, 2 of
  which become pages — 678 Mission Street, reached through the California
  Historical Society building the volume names on the O'Farrell grant site
  (occupied 1993–2024, since sold), and 199 Museum Way, reached through the
  Randall Museum the volume names on the Corona Heights site. Of the other
  eight: Casa Grande (Sonoma) and Oak Knoll (Napa County) are outside San
  Francisco; 600 Ocean Avenue's building was demolished and the address no
  longer clears EAS; and the west side of Grant Avenue between Clay and
  Washington, the site southeast of the Richardson home, the corner of
  Sacramento and Leidesdorff, Mission Street between 13th and 15th, and Laurel
  Hill Cemetery are all located by segment, corner or landmark rather than a
  resolvable number)
- **Verified:** 2026-08-12 (vol. 31 no. 2, Winter 2021: 17 places named, plus
  the present-day address the volume gives for each of the three congregations
  it follows — 20 in all — 4 of which become pages. Three are those present-day
  addresses: 1399 McAllister Street (Third Baptist Church, Landmark No. 275),
  970 Laguna Street (Bethel A.M.E. Church) and 2155–2159 Golden Gate Avenue
  (First A.M.E. Zion Church, landmark designation initiated March 2026). The
  fourth is 1640–1644 Grant Avenue, reached through Planning's survey name for
  the parcel. Of the other 16: 1661 Octavia, 273 Washington, 184 Clay and 119
  Merchant are numbered but have no EAS record, and the last three are
  pre-renumbering addresses whose own cross-streets place them elsewhere;
  Jessie and Ecker, Battery and Washington, Post and Kearny, and Jane and
  Natoma are corners; Sansome between California and Pine, Powell between
  Jackson and Pacific, Stockton between Clay and Sacramento, and Scott Street
  are segments; and Golden Gate Park, the de Young Museum, the Japanese Tea
  Garden and the California Academy of Sciences all sit on parcel 1700001, the
  park itself. Only Montesano's article yields a page; the Taylor, Gutierrez,
  Bruno, Bell, Birt/Wong and Quock articles land on none)
- **Coverage:** volumes 29 no. 2, 30 nos. 1–2, 31 nos. 1–2 and 32 no. 1 read in
  full.
