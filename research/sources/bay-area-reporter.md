# bay-area-reporter — *Bay Area Reporter* archive, 1971–2005 (secondary)

> **Research dossier.** Rules: [../AGENTS.md](../AGENTS.md) · traps:
> [../LESSONS.md](../LESSONS.md) · register:
> [../SOURCES.md](../SOURCES.md) · cited on pages by the source id `bay-area-reporter`.
>
> - **Kind:** newspaper OCR · **Tier:** secondary · **Status:** open
> - **Search-invisibility:** high — see the register for what that rates.
> - **Coverage:** 1971–2003 read (1,431 of 1,514 issues). 2004–2005 remain. See the `Verified:` line.
> - **Local corpus:** `research/corpora/bay-area-reporter/`

- **What:** The *Bay Area Reporter*, San Francisco's gay community newspaper,
  founded 1 April 1971; fortnightly at first, weekly from the 1980s. The
  archive holds **1,514 issues, 1 April 1971 to 28 July 2005, 77,842 pages**,
  scanned by the GLBT Historical Society. In the 1970s it is a bar paper: bar
  and club columns, display advertising, and a few pages of community news.
  The address-level facts are the openings, moves, closings and fires of bars,
  clubs, baths, restaurants and shops, and the addresses of the community's
  institutions (the Society for Individual Rights center, the Metropolitan
  Community Church, switchboards, clinics, community houses).
  This is a different thing from the `local-news` row, which covers browsing
  the paper's current website per address.
- **Where:** Internet Archive collection `bayareareporter`, one item per
  issue, identifier `BAR_YYYYMMDD`. A reader is given
  `https://archive.org/details/BAR_YYYYMMDD/page/n<leaf>/mode/1up`, where
  `<leaf>` is the zero-based scan leaf. The issue list is
  `https://archive.org/advancedsearch.php?q=collection:bayareareporter&fl[]=identifier&fl[]=date&rows=2000&output=json`
  (a copy is `/mnt/project-files/bar/items.json`).
- **How to get at it:** the items have **no hOCR**, so
  `ocr_mentions.py leaf` cannot find a page. Each item has
  `BAR_YYYYMMDD_djvu.xml`; `/mnt/project-files/bar/dl_djvu.py` downloads it
  (four threads, about 20 issues a minute), writes the plain text to `raw/`
  and rebuilds the `hocr/<id>_hocr_searchtext.txt.gz` and
  `_hocr_pageindex.json.gz` pair from the XML's page objects, so the rest of
  the pipeline works unchanged: `python3 -I /mnt/project-files/bar/dl_djvu.py bay-area-reporter`
  after writing `items.tsv` (identifier, date) for the years wanted. Then
  `research/tools/ocr_mentions.py extract`, `cluster_bar.py` (groups the
  surviving windows by address, so one bar's forty advertisements are read
  once), and the event-word pass for places printed without a number. The
  scripts for the 1971–1975 run are in `/mnt/project-files/bar/`:
  `decisions_bar1.py` (one row per finding), `build_bar.py` (finds each quote
  on its leaf and writes the findings file), `patch_bar1.py` (by-hand
  placements, holds, gone buildings), `publish_bar.py`, `audit_bar.py`, and
  `c.py` (context for a phrase in one issue or all of them, which is how a
  garbled name is read from another issue).
- **What is actually usable:** in 1971–1975, 4,702 numbered mentions gave 75
  findings. Three kinds. **Openings, moves and closings** of bars and shops as
  businesses, usually from a "Grand Opening" advertisement and a line in a
  columnist's round-up. **Fires**, which the news pages report with times,
  causes and damage (the SIR Center, 9 July 1972; Toad Hall, June 1973;
  Tiffany's under the Allen Arms at 1900 Market, January 1974). **Community
  institutions at an address**: "The National Transsexual Counseling Unit ...
  has moved to 243 Turk St." (1972). **Not usable:** the weekly bar guide
  and bare repeating advertisements (presence only); personal and classified
  advertisements; political endorsements; arrests and raids, which are
  reported by the names of the people arrested; out-of-town bars (Oakland,
  San Jose, the Russian River, Los Angeles).
- **Cautions:**
  - **Display advertisements OCR badly.** A bar's name set in display type is
    often unreadable where its address is clean. Read the name from another
    issue (`c.py all "<number> <street>"`) and say so in
    `extra.placement_note`; drop the candidate if no issue prints it.
  - **Columnists print wrong numbers.** The Windjammer is "745 Geary" in one
    column and 645 in its own advertisements; Club Fugazi is "568 Green" once
    and 678 after. Take the number the place's own advertisement gives, keep
    the printed one in `extra.number_as_printed`.
  - **Stories about a known place print no number.** The SIR Center fire
    story never says 83 Sixth Street. The number comes from another issue of
    the paper, never from outside it, and the note says which.
  - **Many of the buildings are gone.** South of Market, the Tenderloin and
    upper Market have been rebuilt; `check.py --overlap` flags a fact older
    than the roll's building. On a page that exists the fact is framed as the
    building then on the site; where there is no page it stays unresolved.
  - **EAS has dropped many of the numbers.** 20 of 75 had no parcel join. A
    number that sits inside one surviving parcel's own range is placed by
    hand (482 Castro inside 480–498); one that falls between two parcels is
    left unresolved. `/mnt/project-files/bar/eas.py "<STREET> <TYPE>" lo hi`
    prints the block's number line with parcels.
  - **Context statements already carry many of these places.** The LGBTQ and
    sexual-identity context statements name Toad Hall, Big Town, Peg's Place
    and Casey's with year ranges. The paper gives the day and sometimes
    contradicts the range; state the conflict in `extra.unknown_sentence`,
    and decline a finding that only repeats the page.
  - **Copyright.** The items carry "Copyright BAR Media, Inc." Facts extract
    freely; `raw.text` is a clause, and no text is committed.
- **People:** the paper names owners, managers, bartenders, performers,
  contest winners, columnists and patrons on every page, and reports arrests
  by name. None of that is taken, and a bar is never described by who owns or
  runs it. Taken: the business or institution, the building, the event. A
  business whose name is a person's name is used as the business name only.
  The Golden Gate Gay Liberation House, a shelter, is named as an institution;
  nothing about who stayed there.
- **Citation label:** "Bay Area Reporter, D Month YYYY", for example
  "Bay Area Reporter, 12 July 1972". The finding's `citation.url` points at
  the leaf.
- **Coverage:** 1971–1975 (121 issues, 4,702 mentions, 466 address clusters
  and 149 event-word passages read by hand): 75 findings, 54 resolved and
  published on 45 pages (3 seeded), 21 unresolved (5 held on parcels with no
  page, 16 gone or between parcels). Read on from 1976 in the next entry. The paper grows from 24 pages an issue to over 60 by the
  1980s; batches of about five years at first, two or three later, are the
  size one run reads.
  1976–1979 (104 issues, 7,322 mentions, 616 address clusters): 61 findings,
  49 resolved and published on 47 existing pages, none seeded, 12 unresolved.
  From 1976 the clusters are too many to read whole: the first 67 were read in
  full and then only the 401 holding an event word, plus the event-word
  passages (`kw_bar.py`). The renaming of the Harvey Milk
  Center, 50 Scott Street (26 May 1979), is unresolved because it belongs on
  the Duboce Park place page.
  1980–1981 (58 issues, 4,841 mentions, 446 address clusters): 35 findings,
  24 resolved and published on 21 existing pages, none seeded; three more
  were placed or taken up by later batches (the two at 150 Eureka in
  1990–1991), leaving 5 held and 3 at numbers EAS no longer has. Only the 148 clusters holding an
  event word were read, then 145 event-word passages.
  Spurs, the Valencia Street bar that opened, was firebombed and burned in
  these two years, is not placed: the paper never prints its number.
  1982–1983 (104 issues, 9,246 mentions, 640 address clusters): 32 findings,
  28 resolved and published on 27 pages (2 seeded: 1488 Pine, which took up a
  held fact of 1972, and 356 Seventh, the fire station the 1981 paper printed
  as 365); 77 Battery's held fact was taken up in 1990–1991, leaving 2
  unresolved at numbers EAS no longer has. The paper is
  weekly from 1982, so two years is 104 issues and a full run.
  1984–1985 (104 issues, 12,154 mentions, 550 address clusters): 33 findings,
  28 resolved and published (one taken up when 1988–1989 seeded its page),
  5 unresolved (2 held, 3 at numbers EAS no longer has). Fourteen of the 33 are the health
  director's closure order of 9 October 1984, whose list of businesses and
  addresses the paper printed.
  1986–1987 (106 issues, 13,519 mentions, 596 address clusters): 26 findings,
  21 resolved and published on 18 existing pages, none seeded or held, 5
  unresolved at numbers EAS no longer joins to one parcel. They include the
  Larkin Street Youth Center fire and reopening, the Coming Home Hospice
  conversion, the Stud's move from Folsom Street to Ninth and Harrison, and
  the office the Names Project shared with the March on Washington.
  1988–1989 (104 issues, 13,030 mentions, 647 address clusters): 27 findings,
  20 resolved and published on 20 pages, one of them seeded (2166 Market
  Street, taking up the fact held for it since 1984–1985), 4 held, 3
  unresolved at numbers EAS no longer joins to one parcel. They include the
  Castro and 18th Street fire of 2 December 1988, the closing of Maud's and of
  Peg's Place, Dignity's last service at St. Boniface, and the paper's own
  move to Ninth Street.
  1990–1991 (104 issues, 12,603 mentions, 607 address clusters): 28 findings,
  25 resolved and published on 25 pages, 3 of them seeded (77 Battery, 150
  Eureka, 1340 Golden Gate, each taking up facts held for it), 1 held, 2
  unresolved. They include the firebombing of the Metropolitan Community
  Church, the fires at Club Screw and My Place, the Lone Star Saloon's return
  after the earthquake, and the Center for Positive Care. Two pages dated a
  club's opening differently and now state both.
  1992–1993 (105 issues, 13,916 mentions, 582 address clusters): 20 findings,
  16 resolved and published on 15 pages, none seeded, 3 held, 1 unresolved.
  They include the fire at A Different Light, the closing of the Center for
  Positive Care and of 1800 Square Feet, the Metropolitan Community Church's
  community center on 18th Street, and the burning of the Dolores Street
  Baptist Church.
  1994–1995 (104 issues, 16,534 mentions, 677 address clusters): 28 findings,
  23 resolved and published on 22 pages, 1 of them seeded (4035 18th Street,
  taking up the fact held for it since 1992–1993), 3 held, 2 unresolved. They
  include the AIDS Health Project's center at 400 Castro, the Shanti Project's
  move to 1546 Market, the Elephant Walk losing its lease, the fire at 425
  Castro, and the openings of the Hole in the Wall Saloon, Daddy's and Books
  Inc.
  1996–1997 (104 issues, 17,283 mentions, 633 address clusters): 28 findings,
  26 resolved and published on 25 pages, none seeded, 3 of them placed by hand
  where EAS no longer holds the number, 1 held, 1 unresolved. They include
  Maitri's groundbreaking at 401 Duboce, Brava's purchase of the York Theatre,
  the Community Center board's vote to demolish the Fallon Building at 1800
  Market, Sha'ar Zahav's last services on Danvers Street, the reopening of the
  Powerhouse and of the Harvey Milk branch library, and the moves of the AIDS
  Health Project, Project Open Hand and Continuum.
  1998–1999 (105 issues, 14,532 mentions, 898 address clusters): 27 findings,
  23 resolved and published on 22 pages, none seeded, 1 held, 3 unresolved at
  numbers EAS no longer holds between two parcels. They include the Community
  Center board's vote to keep the Fallon Building, Under One Roof's move to
  549 Castro, Shanti's move into 730 Polk, the Castro Station becoming The Bar
  on Castro, the Hot Cookie fire, the groundbreaking for Lark-Inn at 869
  Ellis, the failed youth shelter at 2500 Market, and the closing of Josie's.
  2000–2001 (104 issues, 12,209 mentions, 891 address clusters): 24 findings,
  all resolved and published on 23 pages, none seeded, 1 placed by hand. They
  include the Community Center's groundbreaking and its lost tax credits, the
  opening of Lark-Inn and of the youth housing at 2500 Market, Pottery Barn at
  2390 Market, the Gay Men's Chorus leaving 400 Castro, the Castro Foundation
  for the Castro Theatre, the reopening of Badlands and of the Castro Country
  Club, and the lot at 2299 Market twenty years after the church fire.
  2002–2003 (104 issues, 12,127 mentions, 847 address clusters): 29 findings,
  25 resolved and published on 22 pages, none seeded, 4 held (2187 and 2189
  Market, two commercial units of the 2002 condominium building at 15th
  Street that has no building page; 525 and 511 Harrison). They include the
  Community Center's opening on 3 March 2002, the demolition of the I-Beam,
  the Harvey's fire and reopening, Diesel at 400 Castro, the closing of the
  Bearded Lady, of Club Townsend, of CHAMP and of the CD Record Rack, the
  Names Project bench at 2362 Market, Mezzanine at 444 Jessie, and Cliff's
  Variety's addition at 479 Castro.
  **Resume at 2004.**
- **Verified:** 2026-11-24 (lead promoted and 1971–1975 read in one run: 121
  issues downloaded from `_djvu.xml`, 555 windows after the advertisement
  filter in 466 clusters read in full, 149 event-word passages read, 75
  findings, every quote found again on its leaf; 11 take their number from
  another issue and say so. Learned: cluster by address before reading, since
  the paper is repeating advertisers; and that the advertisement filter drops
  the grand-opening advertisements that are the paper's best facts, so the
  event-word pass over "grand opening" is not optional. Same day, 1976–1979:
  104 issues, 61 findings, each quote found again; learned that filtering the
  clusters to those holding an event word loses little, and that the event-word
  pass must drop "dedicated" and "landmark", which match a weekly
  advertisement and every tribute. Same day, 1980–1981: 58 issues, 35
  findings, each quote found again; two issues a month in these years, so two
  years is a small batch and three or four would fit one run. Same day, 1982–1983: 104 issues, 32 findings, each quote found again; the classified pages now swamp the event-word pass, so it was narrowed to fire, closed and lost-lease words after the first 20 issues. Same day, 1984–1985: 104 issues, 33 findings, each quote found again; `evf.py` now filters the clusters, and from mid-1984 a second, tighter filter drops classified pages and calendar listings, which hold no building facts. Same day, 1986–1987: 106 issues, 26 findings, each quote found again; by now most findings are openings, closings and moves of institutions already on a page, so the overlap check matters more than seeding. Same day, 1988–1989: 104 issues, 27 findings, each quote found again; a pass over the weeks after the 1989 earthquake found no damage report tied to a street number, and `evf2.py` now does the tighter filtering in one step. Same day, 1990–1991: 104 issues, 28 findings, each quote found again; three parcels gained a second fact and were seeded with what had been held for them, one of those a Redevelopment Agency form read again against its page image. Same day, 1992–1993: 105 issues, 20 findings, each quote found again; `evf2.py` was tightened again (more classified vocabulary dropped, at most two clusters per address), and no parcel gained a second fact. Same day, 1994–1995: 104 issues, 28 findings, each quote found again; the paper now runs a business column whose items give an opening day and a number, which is where a third of the batch comes from. Same day, 1996–1997: 104 issues, 28 findings, each quote found again; a fact for a library that is a place page was published to its `place.json`, which the batch's publisher now accepts. Same day, 1998–1999: 105 issues, 27 findings, each quote found again; three findings name a business whose number the paper prints only in other issues, and say so in their placement notes. Same day, 2000–2001: 104 issues, 24 findings, each quote found again; by now the paper's news pages report Castro storefronts and nonprofit moves closely, and nearly every finding lands on a page that already has planning-commission entries for the same years. Same day, 2002–2003: 104 issues, 847 clusters, the 100 left by the tighter filter and 28 event-word passages read, 29 findings, every quote found again in its issue; the audit flags 2, both explained in the batch's coverage note.)
