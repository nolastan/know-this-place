# sfra-minutes — Minutes of the San Francisco Redevelopment Agency (primary)

> **Research dossier.** Rules: [../AGENTS.md](../AGENTS.md) · traps:
> [../LESSONS.md](../LESSONS.md) · register:
> [../SOURCES.md](../SOURCES.md) · cited on pages by the source id
> `sfra-minutes-<meeting date>`, e.g. `sfra-minutes-1979-02-13`.
>
> - **Kind:** meeting minutes (scanned volumes, Internet Archive OCR) · **Tier:** primary · **Status:** open
> - **Search-invisibility:** high — one OCR text per year or half-year, no index by address.
> - **Coverage:** 1974-2011 read (45 volumes, every volume on IA, through the Agency's dissolution in 2012). Exhausted.
> - **Local corpus:** `research/corpora/sfra-minutes/` (IA `_djvu.txt`, one per volume)
>
> Update this dossier at the end of every pass — the `Verified:` line, the
> coverage note, and anything the pass learned about getting at the source.

- **What:** Minutes of the regular meetings of the Redevelopment Agency
  Commission, 45 volumes in the SFPL collection on the Internet Archive, 1974 to
  2011 (`29minutefregular1974sanf`, `30minutesofregula1974sanf` … `73minutesregular2009sanf`,
  `minutesofregula2010sanf_0`, `minutesofregular2011sanf`; the numeric prefix is
  SFPL's volume number). The Agency owned, cleared, rehabilitated, moved and
  sold buildings across its project areas (Western Addition A-1 and A-2,
  Yerba Buena Center, Hunters Point, India Basin, Diamond Heights, Golden
  Gateway, Rincon Point-South Beach, Mission Bay), so its agenda names
  buildings by street address with the firm that rehabilitated or demolished
  them, the price, and the redeveloper it was sold to.
- **Getting at it:** `https://archive.org/download/<id>/<id>_djvu.txt`. Each
  agenda item opens `(a) Resolution No. NN-YY …` (1974-87, 1995-2000) or
  `(c) Mr. X introduced item (c), which …` with the resolution number only in
  the adoption line (1988-94), or `3 (a) Resolution No. N-2002, …` (2001-11).
  Every page carries the header `Minutes of a Regular Meeting, <date>`, which
  dates the item; an item that runs across a page break into a new header
  belongs to the later meeting only if it starts on that meeting's first page,
  so check doubtful ones. `/mnt/project-files/sfra-minutes/items.py` splits a
  volume into items; `classify.py` keeps address-bearing items about
  demolition, design, disposition, construction and rehabilitation;
  `pages.py` matches their addresses to existing pages; `show.py PREFIX:LINE`
  prints an item. 939 Ellis Street, the Agency's own office, appears on every
  page and is noise.
- **Yield:** about 3,240 items name a street address; 1,100 are of a useful
  kind, and about 415 match an existing page. 1974-81 gave 15 findings on
  pages that exist. Most of the Agency's buildings of the 1970s were cleared
  and their parcels merged, so many addresses have no page today.
- **Privacy:** buyers of rehabilitated houses, relocated tenants and
  certificate-of-preference holders are private people: never name them.
  Nonprofit and business redevelopers (Kimochi, the JCCCNC, KPOO and
  Associates) and contractors are named.

## Passes

- 2026-11-25 — 1974-81 (`29…1974` to `44…1981`): 15 findings (sfra-minutes-1974-81)
  on existing pages: Victorian Square's rehabilitation contracts (1961 and 1971
  Sutter, 1712 and 1740 Fillmore), 951 Eddy for the Housing Authority, the
  Kimochi sites at 1734 Laguna and 1529 Sutter, the JCCCNC's designation at
  1840 Sutter, the Goodman Building's truck-damage repair, Opera Plaza's last
  demolition (the Doggie Diner), 1400-12 Golden Gate's condominium conversion,
  KPOO and Associates at 1325 Divisadero. Unplaced items listed in the batch's
  coverage note.

- 2026-11-25 — 1982-87 (`45…1982` to `50…1987`): 16 findings (sfra-minutes-1982-87):
  Tenderloin Section 8 financing (441 Ellis, 249 Eddy), A-2 rehabilitation sales
  (1362 Post to the Multi-Services Center for Koreans, 1101 Fillmore, 1329 Pierce,
  1800 Eddy, 1207 and 1211 Scott), the Goodman Building emptied in 1983 and
  Alan Wofsy & Associates, the JCCCNC's 1986 opening and 1852 Sutter's
  clearance, the Bush Street Temple proposals, Coleridge Park Homes.
- 2026-11-25 — 1988-94 (`51…1988` to `57…1994`): 33 findings (sfra-minutes-1988-94).
  From 1989 the Agency funded nonprofit housing citywide (the Tax Increment
  Housing Program, HOPWA), so the minutes reach far outside the project areas:
  SRO hotels bought by Conard House and TNDC, group homes (Baker Places, Progress
  Foundation, Walden House), Tenderloin Family Housing at 201 Turk, Hospice by
  the Bay on Leland, Diamond View Apartments, the Bush Street Synagogue
  agreement and its termination.
- 2026-11-25 — 1995-2000 (`58…1995` to `62…2000`): 17 findings (sfra-minutes-1995-2000).
  Hamilton Family Center, the Knox Hotel's dedication, Asian, Inc. at 479 Natoma,
  Mary Elizabeth Inn, Habitat for Humanity at 1272 South Van Ness, the Japanese
  American Religious Federation's assisted living at 1881 Bush.
- 2026-11-25 — 2001-11 (`63…2001` to `minutesofregular2011`): 19 findings
  (sfra-minutes-2001-11). Schematic design approvals, Mercy Housing and TNDC
  loans and ground leases, the Elouise Westbrook naming at 227-255 Seventh, and
  2008 SRO rehabilitation loans (owners are private people: not named). Watch
  the side of the street: pages.py matched 988-992 Howard to 989 and 1355-1375
  Sutter to 1368, both wrong.
- **Verified:** 2026-11-25 (1974-2011, all 45 volumes: items split, 100 curated findings published on existing pages).
