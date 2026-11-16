# architect-engineer-california — *The Architect and Engineer of California* (primary)

> **Research dossier.** Rules: [../AGENTS.md](../AGENTS.md) · traps:
> [../LESSONS.md](../LESSONS.md) · register:
> [../SOURCES.md](../SOURCES.md) · cited on pages by the source id `architect-engineer-california`.
>
> - **Kind:** journal OCR · **Tier:** primary · **Status:** open
> - **Search-invisibility:** high — see the register for what that rates.
> - **Coverage:** all 116 Internet Archive volumes (1905–1959) read for numbered San Francisco addresses in building news, plate captions and text; corner-only and lot-line items not yet read. See the `Verified:` line.
> - **Local corpus:** `research/corpora/architect-engineer-california/`
>
> Update this dossier at the end of every pass — the `Verified:` line, the
> coverage note, and anything the pass learned about getting at the source.

- **What:** *The Architect and Engineer of California* (later *The Architect and Engineer*), a San Francisco monthly for
  architects, engineers and builders, September 1905 to 1959. Each issue carries illustrated articles on new buildings,
  a plate section of photographs and drawings with the architect's name, and, through most of its run, building-news
  columns ("With the Architects", "Building Trades", later "Architects' and Engineers' News") that report plans being
  drawn, contracts let and work finished.
- **Where:** Internet Archive, the `usmodernist` uploads: one item per bound volume or issue run, ids
  `usmodernist-AECA-<YYYY-MM>` or `usmodernist-AECA-<YYYY-MM>-<YYYY-MM>` (116 items; a few are index volumes). Public domain
  scans from usmodernist.org with Internet Archive OCR.
- **How to get at it:** per item, `https://archive.org/download/<id>/<id>_djvu.txt` (plain OCR, one paragraph per blank-line
  block) and `<id>_hocr_searchtext.txt.gz` with `<id>_hocr_pageindex.json.gz` (text with page offsets). The hocr page index
  counts leaves from 0, and **that index is the reader's `n`**: cite `https://archive.org/details/<id>/page/n<leaf>/mode/1up`.
  The whole set is about 185 MB and downloads in a few minutes with parallel `curl`. Page images:
  `https://archive.org/download/<id>/page/n<leaf>.jpg`. The fulltext search endpoint
  (`https://<d1>/fulltext/inside.php?item_id=<id>&doc=<id>&path=<dir>&q=<term>`, with `d1` and `dir` from
  `https://archive.org/metadata/<id>`) returns the page and word box of a hit, which is the fast way to crop a check image.
- **What is actually usable:** building-news items that give a street number, the work and the architect or builder;
  plate captions and the issue's list of plates, which name a building and its architect; short notices of a firm
  moving into a new building of its own. About 67,000 number-plus-street mentions across the run reduce to roughly 1,400
  that sit in building news with a verb of work, and to 149 findings once offices, advertisements, out-of-town jobs and
  repeats are cut.
- **Cautions:**
  - Most numbered addresses are **offices**: an architect's, a contractor's, a supplier's. Advertisements and the
    directory pages repeat them in every issue. Read the sentence: "of 251 Kearny street" is a firm's office, not a job.
  - Building news mixes San Francisco with the whole West; the city is often unnamed. Drop anything that names another
    town, and check the street exists in San Francisco at that number.
  - **The list of plates names the building first and the architect after it**, so read across a line, not down a
    column; one run put four 1935 remodelings on the wrong architect before this was caught.
  - Plans are not buildings. A job reported as "plans being prepared" may never have been built, or built to other
    plans; credit an architect on the page only when the roll's build year fits and the item says the work went ahead.
  - Many volumes bind several months, so the item id is not the issue date: date each fact from the issue heading on its
    page (`months.json` in the run's scratch folder maps leaf ranges to months).
  - OCR is fair; hyphenated line breaks come through as "word- word" and need joining before matching.
- **People:** the journal names architects, engineers and contractors, all fine to credit. It also names owners and
  clients, usually private people; leave them off unless independently notable or the building bears their name.
  Firms trading from a building may be named.
- **Citation label:** "The Architect and Engineer of California, <Month> <Year>", linking the leaf as above.
  Page source ids are `architect-engineer-california-<item date>-n<leaf>`.
- **Coverage:** 1905–1959, all 116 items: every number-plus-street mention in building news, plate captions and the list
  of plates screened by script and read by hand; 149 findings, 84 resolved, 73 published on 70 pages (10 seeded), 11
  declined as repeats of the page, 65 unresolved (offices with no building job, numbers that no longer exist, roll
  years after the fact, or parcels holding a later building). **Not yet read:** items that place a job only by corner or
  by feet from a corner ("northeast corner of Jackson and Laguna", "south line of Bush, 137 feet west of Jones"), about
  250 paragraphs in the 1905–1920 building news. They need the lot-geometry engine from the pre-1909 newspaper run
  (`/mnt/project-files/pre1909/`) and are the next batch. The corpus is gitignored and lost with each container.
- **Verified:** 2026-11-15 (first run, the whole journal read for numbered addresses; 73 facts published, 10 pages
  seeded, and 3 held Building and Engineering News permits taken up by the seeded pages after reading them against the page
  image; every resolved finding checked with `check.py --overlap` before and after seeding).
