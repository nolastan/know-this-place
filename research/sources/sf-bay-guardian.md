# sf-bay-guardian — *San Francisco Bay Guardian* archive, 1966–2014 (secondary)

> **Research dossier.** Rules: [../AGENTS.md](../AGENTS.md) · traps:
> [../LESSONS.md](../LESSONS.md) · register:
> [../SOURCES.md](../SOURCES.md) · cited on pages by the source id `sf-bay-guardian`.
>
> - **Kind:** newspaper OCR · **Tier:** secondary · **Status:** done
> - **Search-invisibility:** high for 1966–2006 (print only, never on the paper's website); medium for 2008–2014, when the paper also published online.
> - **Coverage:** every issue in the collection read, 1966–2014 (996 of 996). See the `Verified:` line.
> - **Local corpus:** `research/corpora/sf-bay-guardian/`

- **What:** The *San Francisco Bay Guardian*, the city's alternative
  newspaper, founded 27 October 1966 and closed in October 2014; irregular at
  first, fortnightly in the early 1970s, weekly from 1975. The archive holds
  **996 issues**, unevenly: 1966–1976 has 173, 1977–1986 has 127 (nothing for
  1980 or 1987), 1988–1994 has 179, 1995–1997 nothing, 1998–2006 has 122 and
  2008–2014 has 395. It is an investigative and listings paper. The
  address-level facts are in the news and feature pages: tenant strikes and
  housing fights at a named building, highrise and redevelopment proposals,
  fires and code enforcement, the opening and moving of clubs, theatres,
  galleries, bookstores and restaurants as its guides report them, and the
  addresses of political and community institutions.
- **Where:** Internet Archive collection `sanfranciscobayguardian`, one item
  per issue. The identifiers are irregular (`Issue01.05`, `Iss09.05`,
  `iss07.14`, `bayguardian13brug_14`, `BayGuardianbrug35-04`, `Labor02.04`),
  so an issue is always named by its identifier and its date taken from the
  item's metadata. A reader is given
  `https://archive.org/details/<identifier>/page/n<leaf>/mode/1up`, where
  `<leaf>` is the zero-based scan leaf. The issue list is
  `https://archive.org/advancedsearch.php?q=collection:sanfranciscobayguardian&fl[]=identifier&fl[]=date&rows=2000&output=json`
  (a copy is `/mnt/project-files/sfbg/items.json`; `items_d.tsv` in the
  corpus directory holds identifier, date and citation label for all 996).
- **How to get at it:** every item has `<identifier>_djvu.xml`.
  `/mnt/project-files/sfbg/dl_djvu.py` downloads it, writes the plain text to
  `raw/` and builds the `hocr/<id>_hocr_searchtext.txt.gz` and
  `_hocr_pageindex.json.gz` pair from the XML's page objects, so the usual
  pipeline works: write `items.tsv` (identifier, date) for the years wanted,
  `python3 -I /mnt/project-files/sfbg/dl_djvu.py sf-bay-guardian`, then
  `research/tools/ocr_mentions.py extract ... --items items_d.tsv --rescue`.
  The scripts are in `/mnt/project-files/sfbg/`: `cluster.py` (groups windows
  by address), `prose.py` (keeps the clusters that read as article prose),
  `evf.py` and `evf2.py` (event-word clusters), `kw.py` (event-word passages
  with no number), `q.py` (context for a pattern in one issue or a year),
  `news.py` (prose with a numbered address and a building-news word, read
  straight from the raw text), `decisions_g1.py` (one row per finding), `build.py`, `patch_g1.py`
  (by-hand placements, holds, gone numbers), `publish.py`, `audit.py` and
  `eas.py`.
- **What is actually usable:** in 1966–1976, 25,304 numbered mentions gave 54
  findings, a far lower rate than a bar paper's, because nearly every
  numbered address is a display advertisement or a calendar listing. The
  facts come from article prose: "The people of 829 Fell St. have been
  withholding rent on the 16-unit building since Feb. 17" (17 April 1970).
  Three kinds: **housing and planning stories** (tenant unions, the
  International Hotel, the Goodman Building, a highrise proposed for an open
  lot); **guides** that date a place in passing ("a newly opened restaurant",
  "recently moved from its historic Clay St. location", "founded in 1911 and
  has been in the same location since 1918"); and **investigations** that
  describe a building (the welfare office "which happens to be a former coffin
  factory"). **Not usable:** advertisements, the calendar and classified
  pages, restaurant and club reviews with no dated fact, out-of-town places,
  and the paper's long political pieces, which name officials and landlords
  rather than buildings.
- **Cautions:**
  - **Read prose, not event words.** The event-word filter that worked for
    the *Bay Area Reporter* returns mostly advertisements here ("has moved
    to", "grand opening"). `prose.py` (stop-word ratio, few capitals, few
    advertisement markers) found most of the batch.
  - **The advertisement filter drops list-style articles.** The
    nursing-home inspection list of 13 December 1972 reads to the filter as
    advertising. A pass without the filter over a known article is worth
    doing where one is found.
  - **Stories about a known building print no number.** The Gartland
    Apartments fire story says only "Valencia Street"; the Western
    Merchandise Mart is "on Market St." Such a fact is placed only where the
    site already has a page that names the building, and the placement note
    says so.
  - **Many of the buildings are gone**, above all in the Western Addition
    and South of Market. `check.py --overlap` flags a fact older than the
    roll's building; on a page that exists the fact is framed as the building
    then on the site.
  - **The paper's dates for other people's buildings can be loose.** It
    gives 1969 for Bechtel's tower at 50 Beale, which the page's sources date
    to 1967; that finding was dropped.
  - **OCR of the 1960s issues is rough** (asterisks for full stops, digits
    read as letters: "9S Leland"). A number that cannot be read in the scan
    is not taken.
  - **Copyright.** The paper is in copyright. Facts extract freely;
    `raw.text` is a clause, and no text is committed.
- **People:** the paper names landlords, tenants, officials, club owners,
  performers and its own writers throughout, and its housing stories quote
  tenants by name. None of that is taken. Taken: the building, the business
  or institution in it, the event, and a corporation named as an owner or
  developer of a building since replaced (the Four Seas corporation and the
  International Hotel). A private buyer's or tenant's story (the 758 Steiner
  mortgage case of 1972) is not entered at all.
- **Citation label:** "San Francisco Bay Guardian, D Month YYYY", for example
  "San Francisco Bay Guardian, 17 April 1970". The finding's `citation.url`
  points at the leaf.
- **Coverage:** 1966–1976 (173 issues, 25,304 mentions, 1,264 address
  clusters; 134 prose clusters, 193 of 671 lines of event-word clusters and
  23 event-word passages read, then the 85 passages of the news-word pass):
  54 findings, 41 resolved and published on 39
  pages, none seeded, 1 placed by hand, 6 held (3220 Fillmore, 2695
  Sacramento, 2140 Clement, 2260 Van Ness, 917 Cole, 1632 Page), 7 at numbers EAS no longer holds
  (1330 Clay, 17 Second, 432 Mason, 17 Adler Place, 75 Fifth, 1898 Folsom,
  393 Folsom). They include the Straight Theatre's conversion, the rent
  strikes at 829 Fell and 940 Hayes, the newspaper strike headquarters on
  Natoma Street, Tadich Grill's move, the old sourdough bakeries, the
  International Hotel's demolition request, the Gartland Apartments fire, the
  Merchandise Mart fire of 1958 and the Goodman Building's rear flats.
  1977–1986 (127 issues, none for 1980; 33,064 mentions, 1,088 address
  clusters; 80 prose clusters, 16 event-word passages and the 55 passages of
  the news-word pass read): 21 findings, 15 resolved and published on 15
  pages, none seeded, 1 placed by hand, 2 held (1660 Bush, 3410 19th), 4 at
  numbers EAS no longer holds (842 Kearny, 128 The Embarcadero, 58-64
  Sutter, 22 Kearny). They include the Victory Building evictions beside the
  International Hotel, the Temple Beautiful, the Cadillac and Clayton
  hotels' purchase by nonprofits, the Swiss American Hotel's code hearing,
  1300 Sacramento, the Planning Commission's approvals of October 1983,
  100 First Street and the attack on the AIDS vigil at United Nations Plaza.
  1988–1994 (179 issues, 115 of them 1989 and 1990; 91,622 mentions, 1,849
  address clusters; the 119 news-word passages, 116 prose clusters and 71
  event passages read): 35 findings, 28 resolved and published on 27 pages,
  1 seeded (260 McAllister, taking up a held *Tenderloin Times* fact), 3 held
  (425 14th, 1529 Haight, 105 Quint), 4 unplaced (500 Eighth; 343, 355 and
  363 Golden Gate, told on the page for 333). They include the law college's
  demolitions and code citations on Golden Gate and McAllister after the
  1989 earthquake, KQED's purchase of 2601 Mariposa, Intersection for the
  Arts on Valencia Street, the Red Vic's reopening, Walden House's three
  houses, the Rent Board's move out of 170 Fell and the empty bank at 400
  Castro.
  1998–2006 (122 issues; 93,929 mentions, 2,122 address clusters; the 85
  news-word passages, 91 prose clusters and 62 event passages read): 39
  findings, 22 resolved and published on 22 existing pages, 8 held (444
  Battery, 595 Castro, 360 10th, 575 Harrison, 1207 Indiana, 1600 Webster,
  1335 Webster, 1547 Clay), 9 unplaced because the address is gone (699
  Columbus, 960 Bush, 2520 Third, 965 Market, 81 Third, 6114 California,
  2955 18th, 1300 Sutter, 701 Lombard). They include the paper's count of
  live-work lofts used as offices in 2000, the protest at 1800 Bryant, the
  nonprofits of the Grant Building and 995 Market, the approval of 1900
  Bryant and of the housing at 3620 19th, the earthquake shacks on Kirkham
  Street, code cases against a large landlord's buildings in 2002 to 2006,
  and a June 2000 retrospective that dates the punk scene's rooms of the
  1970s.
  2008–2010 (210 items, many issues scanned twice; 78,583 mentions): 15
  findings, 9 published on 9 pages, 4 held (55 Laguna, 3422 Mission, 736
  Valencia, 1268 Lombard), 2 unplaced (113 Steuart, 1856 Mission). They
  include the Academy of Art's conversions at the Flower Mart, 601 Brannan
  and 620 Sutter, the demolition of the Little House on Lombard Street (16
  March 2009) and the Power Exchange's closure at 34 Mason.
  2011–2014 (185 items; 34,281 mentions): 21 findings, 13 published on 13
  pages, 5 held (2441 Mission, 2200 Cesar Chavez, 555 Fulton, 75 Howard,
  1700 Mission), 3 unplaced (38 Dolores, 1639 Market, 2050 Bryant). They
  include the eviction letters at 1049 Market, the fire at 1448 Valencia,
  the school district's land swap for 1950 Mission, the Board of
  Supervisors' vote on 1050 Valencia, CounterPulse's move to 80 Turk and
  Zendesk's renovation of 1019 Market.
  **Exhausted.** Every issue in the collection is read. The collection
  itself has no issues for 1987, 1995–1997 or 2007; if the Internet Archive
  adds them, they are the only thing left. The event-word clusters under
  the tighter filter were skipped in every batch after the first, where
  they were nearly all advertisements.
- **Verified:** 2026-11-24 (source found by browsing the Internet Archive's
  San Francisco newspaper collections, promoted and 1966–1976 read in one
  run: 173 issues downloaded from `_djvu.xml`, about 100 candidates checked
  against the issue text, 48 findings, every quote found again on its leaf
  (six more, 54 in all, when the news-word pass was run over these years later the same day);
  the audit flags 2, both a building named without its number. Learned: this
  paper's addresses are advertisements, so filter for prose first; a fact
  already on the page from a context statement or the planning minutes is
  common for the famous buildings, so run the overlap check before writing
  more than a line; and the collection's identifiers carry no date, so every
  script keys on the identifier and reads the date from `items_d.tsv`. Same day, 1977–1986: 127 issues, 21 findings, each quote found again. Learned: `news.py`, a pass over the raw text for prose with a numbered address and a building-news word, finds the planning and housing stories the advertisement filter hides, and is now the first thing to read; by the 1980s the planning minutes and environmental reports already on the pages cover most of the paper's highrise stories, so a third of the candidates fell at the overlap check. Same day, 1988–1994: 179 issues, 35 findings, audit clean. Learned: the issues of 1989 and 1990 are four times the size of the 1970s ones and almost all of the growth is advertising and listings (88 percent of mentions marked as advertisements), so the three reading passes came to only 306 passages; a running story, here the law college's Tenderloin block, is best read as a whole across its issues before any row is written, because each issue adds a number or a date the others lack; and shops' own moving announcements, repeated for weeks, give exact dates the articles do not. Same day, 1998–2006: 122 issues, 39 findings, the audit flags 1 (a year written as ’89). Learned: by 2000 the paper's building news is housing politics, so most rows are a hearing, a lawsuit or a code case and need the landlord and tenants left out; a retrospective feature can date a dozen vanished rooms at once, but a quarter of this batch's addresses no longer exist in EAS; and when a quote occurs twice in an issue the builder cites the first leaf, so make the quote include the number. Same day, 2008–2010 and 2011–2014: 395 items, 36 findings, the audit flags 1. Learned: the last seven years yield a tenth of what the 1970s did per issue, because the paper's building stories had become policy arguments about projects already in the planning minutes, and what is left is closings, moves and the occasional fire; the archive holds many of these issues twice under different identifiers, so read one scan and cite it.)
