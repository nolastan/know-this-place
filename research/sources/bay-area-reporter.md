# bay-area-reporter — *Bay Area Reporter* archive, 1971–2005 (secondary)

> **Research dossier.** Rules: [../AGENTS.md](../AGENTS.md) · traps:
> [../LESSONS.md](../LESSONS.md) · register:
> [../SOURCES.md](../SOURCES.md) · cited on pages by the source id `bay-area-reporter`.
>
> - **Kind:** newspaper OCR · **Tier:** secondary · **Status:** open
> - **Search-invisibility:** high — see the register for what that rates.
> - **Coverage:** 1971–1975 read (121 of 1,514 issues). 1976–2005 remain. See the `Verified:` line.
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
  page, 16 gone or between parcels). **Resume at 1976** (`BAR_19760108` is the
  first issue). The paper grows from 24 pages an issue to over 60 by the
  1980s; batches of about five years at first, two or three later, are the
  size one run reads.
- **Verified:** 2026-11-24 (lead promoted and 1971–1975 read in one run: 121
  issues downloaded from `_djvu.xml`, 555 windows after the advertisement
  filter in 466 clusters read in full, 149 event-word passages read, 75
  findings, every quote found again on its leaf; 11 take their number from
  another issue and say so. Learned: cluster by address before reading, since
  the paper is repeating advertisers; and that the advertisement filter drops
  the grand-opening advertisements that are the paper's best facts, so the
  event-word pass over "grand opening" is not optional.)
