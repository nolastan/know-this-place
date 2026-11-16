# architect-engineer-california — *The Architect and Engineer of California* (primary)

> **Research dossier.** Rules: [../AGENTS.md](../AGENTS.md) · traps:
> [../LESSONS.md](../LESSONS.md) · register:
> [../SOURCES.md](../SOURCES.md) · cited on pages by the source id `architect-engineer-california`.
>
> - **Kind:** journal OCR · **Tier:** primary · **Status:** open
> - **Search-invisibility:** high — see the register for what that rates.
> - **Coverage:** all 116 Internet Archive volumes (1905–1959) read for numbered San Francisco addresses in building news, plate captions and text; corner-only and lot-line items read for 1905–1920. See the `Verified:` line.
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
- **How to get at it:** per item, `https://archive.org/download/<id>/<name>_djvu.txt`, where **`<name>` is the id without its `usmodernist-` prefix** (`AECA-1910-02_djvu.txt`; the prefixed name 404s with an HTML page that a quiet `curl` saves as the text file) (plain OCR, one paragraph per blank-line
  block) and `<name>_hocr_searchtext.txt.gz` with `<name>_hocr_pageindex.json.gz` (text with page offsets). The hocr page index
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
  - **Corner items list a building twice, months apart** — plans, then the contract, then a contractor's job list
    naming the same corner. A contractor's list ("plumbing installed in…") names the building and architect but is no
    evidence of date; it takes the corner, not the year. Two such lists put Albert Schroepfer at the SE corner of Geary
    and Jones, where the corner lot (552 Jones / 595 Geary, 1913, seven storeys) and its neighbour (585 Geary, 1912, six
    storeys, credited to Hladik and Thayer by the National Register) both fit; left unresolved.
  - OCR is fair; hyphenated line breaks come through as "word- word" and need joining before matching.
- **People:** the journal names architects, engineers and contractors, all fine to credit. It also names owners and
  clients, usually private people; leave them off unless independently notable or the building bears their name.
  Firms trading from a building may be named.
- **Citation label:** "The Architect and Engineer of California, <Month> <Year>", linking the leaf as above.
  Page source ids are `architect-engineer-california-<item date>-n<leaf>`.
- **Coverage:** 1905–1959, all 116 items: every number-plus-street mention in building news, plate captions and the list
  of plates screened by script and read by hand; 149 findings, 84 resolved, 73 published on 70 pages (10 seeded), 11
  declined as repeats of the page, 65 unresolved (offices with no building job, numbers that no longer exist, roll
  years after the fact, or parcels holding a later building). Corner and lot-line items, 1905–1920: read (`aeca-1905-1920-corners`, below). **Not yet read:** corner and
  lot-line items after 1920; the building news from then on gives street numbers far more often, so expect few. The
  corpus is gitignored and lost with each container.
- **Verified:** 2026-11-15 (first run, the whole journal read for numbered addresses; 73 facts published, 10 pages
  seeded, and 3 held Building and Engineering News permits taken up by the seeded pages after reading them against the page
  image; every resolved finding checked with `check.py --overlap` before and after seeding).
- **Verified:** 2026-11-16 (second run, corner and lot-line items 1905–1920: 50 items, 432,661 OCR paragraphs screened
  by script for a corner, side, line, block face or offset beside a verb of building work, 706 survivors read by hand
  into 422 San Francisco jobs; 409 name two streets and went through `corner.py --batch`; 30 placed on 30 parcels, 24
  published on 24 pages (1 seeded, 2330 Bush, St. Dominic's priory), 6 declined as repeats of the page, 392
  unresolved. **What it learned:** the method holds here — of the 30 placements, 13 landed on pages already crediting
  the same architect or the same building from the *Call*, *Building and Engineering News*, the National Register or
  an EIR (Meyer at 701 Post, Sexton at 701 Sutter, Denke at 601 Polk, Cahen at 501 Taylor, Lapachet & Larsen at 711
  Leavenworth). A corner with no lot needs one check beyond the roll year — the storey count the item prints, a
  Planning building name, or an existing credit; 13 corner-only candidates that had only the year were left
  unresolved, and four that failed the storey count (the plans were not built as drawn). Most of the journal's corner
  items are plans: 256 of 422 jobs were "plans prepared", and most corners have been rebuilt since. Building news
  is dated by the issue's month from the running heads; where a volume's heads skip months the finding is dated to
  the year.)
