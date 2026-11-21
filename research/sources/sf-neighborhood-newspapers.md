# sf-neighborhood-newspapers — San Francisco neighborhood newspapers, 1956–2026 (secondary)

> **Research dossier.** Rules: [../AGENTS.md](../AGENTS.md) · traps:
> [../LESSONS.md](../LESSONS.md) · register:
> [../SOURCES.md](../SOURCES.md) · cited on pages by the source id
> `sf-neighborhood-newspapers-<IA identifier>-n<leaf>`.
>
> - **Kind:** newspaper OCR · **Tier:** secondary · **Status:** open
> - **Search-invisibility:** high — monthly community papers whose only text is an Internet Archive OCR layer; no address query reaches them.
> - **Coverage:** three titles of 18 read: the Visitacion Valley Grapevine (289 issues, 1986–2011), the Glen Park Association's paper under all its names (124 issues, 1977–2012) and OMI News (85 issues, 1969–1980) — 178 findings, 150 resolved, 144 published on 107 pages (56 seeded).
> - **Local corpus:** `research/corpora/sf-neighborhood-newspapers/<title>/`
>
> Update this dossier at the end of every pass — the `Verified:` line, the
> coverage note, and anything the pass learned about getting at the source.

- **What:** The Internet Archive collection `sanfrancisconewspapers`, 2,358
  items contributed by "a collaborative of San Francisco neighborhood history
  groups": one item per issue of a neighborhood monthly, each with an OCR text
  layer. Titles and issue counts (title spellings vary; count by title
  prefix): Noe Valley Voice (305 + 31, 1977–2011), The Potrero View (221,
  1970–2009), **Visitacion Valley Grapevine (289, 1986–2011)**, Richmond
  ReView (151 + 76, 1988–2008), New Mission News (127, 1992–2004), Tenderloin
  Times (91, 1978–1993), OMI News (85, 1969–1980), North Mission News (70,
  1983–1992), New Bernal Journal and Bernal Journal (69 + 52, 1970–1999), Park
  Bell (64, 1987–1999), Telegraph Hill Semaphore and The Semaphore (50 + 42,
  1976–1999, plus later strays), Glen Park News (39, 1982–2007), The New
  Fillmore (27, 1986–1990), Sunnyside Neighborhood Association News (11), St.
  Mary's Park Improvement Club newsletter (8, 1959–1985), Telegraph Hill
  Bulletin (4, 1957–1964) and singletons. *Tenant Times* (25) is in the
  collection too and is retired in SOURCES.md for carrying no numbered
  addresses. Marina Times and Westside Observer are **not** in it.
- **Where:** an issue is `https://archive.org/details/<identifier>`; a page
  cites `https://archive.org/details/<identifier>/page/n<leaf>/mode/1up`,
  where `<leaf>` is the 0-based index into the item's hOCR page index (what
  `ocr_mentions.py leaf` prints).
- **How to get at it:** the item list is one advancedsearch query —
  `https://archive.org/advancedsearch.php?q=collection%3Asanfrancisconewspapers&fl[]=identifier&fl[]=title&fl[]=date&rows=3000&output=json`
  — filtered on the title. Per issue, fetch
  `https://archive.org/download/<id>/<id>_hocr_searchtext.txt.gz` and
  `<id>_hocr_pageindex.json.gz` (together ~100 KB) rather than the
  `_djvu.txt`: the search text *is* the OCR, and the page index splits it into
  leaves, so the same two files give the text and the citation. Four parallel
  workers fetched 289 issues in under ten minutes; a single sequential
  fetcher managed a third of that in ten. Write each issue's search text to
  `<title>/raw/<id>.txt` and move the hOCR files into `<title>/hocr/`, then
  `research/tools/ocr_mentions.py extract <title> --items <title>/items.tsv
  --from 1900 --to 2099` gives the mention windows and `ocr_mentions.py leaf`
  finds a phrase's leaf from the cached hOCR files (it fetches
  `_page_numbers.json` itself when missing). One title is one batch.
- **What is actually usable:** news items and features, for the three kinds
  of fact the East/West run defined (see
  [east-west-journal.md](east-west-journal.md)): dated events at a building
  (an opening, a groundbreaking, a demolition, a fire, a renovation, a move),
  retrospective history in features, and occupancy where an institution is
  stated to be *based* at a number. **Not usable:** display advertisements,
  which are most of every issue's numbered addresses; business-directory
  pages; calendars naming a venue for a one-off meeting; classifieds; the
  paper's own masthead and subscription address.
- **Cautions:**
  - **The ad filter eats news, because every community item ends in a phone
    number.** `ocr_mentions.py`'s advertisement rule drops any window with a
    phone number, ZIP code or hours — 8,065 of the Grapevine's 10,382
    mentions — and the advertiser rule (an address in six or more issues)
    drops the community center, the library and the churches whose news is
    the best in the paper. The Grapevine pass therefore read the filtered
    windows **plus** every advertiser- or ad-dropped window carrying a strong
    event word (opened, demolished, dedicated, renovated, moved, built, fire,
    anniversary), deduplicated on the words around that event word: 545 +
    92 + 148 = 785 windows.
  - **Leland Avenue OCRs as Leiand, Letand, Ldand, Lebnd, Loland; Sunnydale
    as Sunnydate; Schwerin as Schwenn.** `ocr_mentions.py` only matches EAS
    spellings, so those mentions are lost to the extract; a later run on this
    title should squash these before extracting.
  - **Bayshore Boulevard, Geneva Avenue and Mission Street run into Brisbane
    and Daly City.** A high number on any of them may not be in the city.
  - **A neighborhood title prints its own main streets with no type word.**
    "690 Chenery", "1350 Ocean", "201 Granada": `ocr_mentions.py` counted an
    untyped name only for downtown streets, so the Glen Park and OMI papers'
    commonest addresses were invisible to it. Count `<number> <Name>` with no
    type in the raw text and pass each as `--untyped NAME` (Glen Park:
    Chenery, Diamond, Monterey, Bosworth, Sanchez, Laidley, Arlington,
    Whitney, Sussex, Lippard, Castro, Cortland, Elk; OMI: Ocean, Granada,
    Broad, Randolph, Holloway, Plymouth, Capitol, Ramsell, Phelan, Faxon,
    Orizaba, Alemany).
  - **The Glen Park paper changed its name four times** — Glen Park
    Association Newsletter, Glen Park Newspaper, Glen Park Perspective
    (also catalogued "Persepctive" and "Perspetive"), Glen Park News — and
    one 2003 issue is catalogued "Glen Park Association". Select on the
    `Glen Park` title prefix and leave out the `glenparkpapers` collection
    record; the OMI equivalent is `ominews`.
  - **Most of what a community paper prints at a number is an institution's
    address, not news about it.** Of 293 reader candidates over the two
    titles, about half were a library, school or church named as a venue
    or in a directory, with no event. They were set aside; a bare address is
    not a dated fact.
- **People:** these papers are dense with residents — obituaries, honor rolls,
  crime, block-club officers, the businesses' proprietors in their own ads.
  None of that is taken. Taken: institutions, churches, schools, agencies,
  housing developments, architects, builders and named firms. A business named
  for its proprietor is left out, and a business's bare presence is not taken
  at all.
- **Copyright:** the items carry no licence statement. Facts extract freely;
  the OCR text is not ours to redistribute and is never committed, and
  quotations in findings are the minimum clause.
- **Citation label:** source `name` "Visitacion Valley Grapevine, June 1995,
  p. 3"; `label` "San Francisco neighborhood newspapers collection (Internet
  Archive)"; `query` the leaf URL above; source id
  `sf-neighborhood-newspapers-<identifier>-n<leaf>`, with the same
  `<identifier>-n<leaf>` token in the finding's `citation.locator` so
  `check.py --overlap` recognises the batch's own entries.
- **Coverage:** **Read:** the *Visitacion Valley Grapevine*, every issue the
  collection holds — 289 items, August 1986 to January 2011, 2,864 OCR pages
  (`findings/sf-neighborhood-newspapers/grapevine-1986-2011.json`).
  The Glen Park Association's paper, every issue the collection holds under
  any of its names — 124 items, March 1977 to December 2012, 1,686 OCR pages
  (`findings/sf-neighborhood-newspapers/glen-park-1977-2012.json`). *OMI
  News*, every issue — 85 items, May 1969 to 1980, 825 OCR pages
  (`findings/sf-neighborhood-newspapers/omi-news-1969-1980.json`).
  **Not read:** the other fifteen titles. The next batches, in the order
  this site needs them: **The Potrero View** (221) and **Noe Valley Voice**
  (336), the two longest runs; then New Mission News, North Mission News,
  the Bernal Journals, Park Bell (Excelsior/Portola), The New Fillmore, the
  Semaphore titles, Richmond ReView and Tenderloin Times. One title is one
  batch; take two in a session if the first is short.
  **Placed nowhere yet:** the Glen Park library's two lost buildings, 700
  Bosworth (opened January 1927, demolished for I-280 about 1964) and 2909
  Diamond (1964, demolished 1969 for the BART station). EAS has neither
  number. The second belongs on a Glen Park BART station page if one is
  ever made.
  **Held, not taken up:** the seeding of 15–19 Blanken Avenue surfaced one
  held *Building and Engineering News* permit (1931, "N Blanken Ave 50 W
  Tunnel Ave", `v31-pt2-1931-jul-1932-jan-0769`). It was not read against
  the page image this run and stays held; `check.py --held pages` lists it.
- **Verified:** 2026-11-20 (promotion and first batch, the
  Grapevine: read 289 issues, 824 windows by hand, found 87, resolved 71,
  published 66 on 45 pages, 18 of them seeded. The best of it is the
  neighborhood's own institutional history, which no other source here
  carries: the community center's three buildings at 66, 50 and 101 Raymond
  (1918, 1922, 1937–41, the 1942 deed to the city), the library's moves from
  a delivery station at 133 and 100 Leland (1911–35) to 45 Leland (1966) and
  the 2003 purchase of 201 Leland, the Church of the Visitacion's 1952
  dedication, the clinic storefront at 82 Leland through three operators,
  Geneva Towers' implosion and the John King Senior Community's build-out.
  **Learned:** (1) in a community monthly the advertisement filter is the
  wrong default, because news items end in a phone number and the
  institutions with the best news are the frequent addresses — read the
  dropped windows that carry an event word; (2) the paper's own OCR
  misspells its main street every issue, and `ocr_mentions.py --alias` now
  takes those spellings; (3) the paper reprints its own history — a 2001
  timeline, a 2006 retrospective, a 2011 anniversary article — so one event
  arrives from four issues and the earliest wins; seven readers produced 204
  candidates for 87 findings, nearly half of the cut being those repeats;
  (4) a number the paper prints in one issue can be wrong in a way its other
  issues settle: the Church of the Visitacion is "1655 Sunnydale" in 2007 and
  2008 and 655 in 1998, 2003 and 2007, and 655 is the parcel the roll dates
  to 1951; (5) the original community-center building is "101 Raymond" in
  three issues and "103 Raymond" in the 2003 demolition notice; 103 is a
  1907 house that still stands, so the demolition is not placed.)
  2026-11-21 (second run, PR 722, two titles: the Glen Park paper and OMI News.
  Read 209 issues, 2,511 OCR pages, 9,116 numbered-address mentions; 1,520
  windows by hand by eight readers; 293 candidates, 91 findings, 79
  resolved, 78 published on 62 pages, 38 of them seeded, 1 declined because
  the page already had it. The best of it: the Glen Park branch library's
  five homes (700 Bosworth 1927, 2909 Diamond 1964, 2838 Diamond until
  1978, 653 Chenery 1978–2007, 2825 Diamond 2007), the Merrill Conservatory
  at 236 Monterey part-demolished in December 1978 and then recommended for
  city purchase, a 1979 architecture walk dating cottages on Chenery and
  Bemis, the oldest house in Glen Park at 657 Chenery, the 1974 dedication
  of New Providence Baptist Church at 218 Granada, Glendale Federal's 1979
  Lakeside branch at 2499 Ocean, and the OMI's own offices and senior
  centers on Granada and Randolph. **Learned:** (1) a neighborhood paper
  prints its own streets untyped, and `ocr_mentions.py --untyped` now takes
  them; (2) the Glen Park title has five catalogue names; (3) half of what
  readers bring back is an institution's bare address, so the reader brief
  should ask for events only; (4) the 1979 architecture walk's dates
  disagree with the assessor on six of seven houses, all recorded as
  conflicts rather than adjudicated; (5) a retrospective's 1876 number
  (600 Divisadero, the Pacific Hebrew Orphan Asylum) was left unresolved:
  a modern article copying a pre-1909 number gives no way to check it.)
