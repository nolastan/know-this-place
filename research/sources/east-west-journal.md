# east-west-journal — *East/West: The Chinese-American Journal* (secondary)

> **Research dossier.** Rules: [../AGENTS.md](../AGENTS.md) · traps:
> [../LESSONS.md](../LESSONS.md) · register:
> [../SOURCES.md](../SOURCES.md) · cited on pages by the source id `east-west-journal`.
>
> - **Kind:** newspaper OCR · **Tier:** secondary · **Status:** open
> - **Search-invisibility:** high — see the register for what that rates.
> - **Coverage:** 1967–1972 read (286 of 1,125 issues); resume at the first 1973 issue. See the `Verified:` line.
> - **Local corpus:** `research/corpora/east-west-journal/`

- **What:** *East/West: The Chinese-American Journal* (at first "The
  Chinese-American News Magazine"), a bilingual Chinatown paper published by
  the EAST/WEST Publishing Company, first every ten days and from 1968 weekly,
  **1 January 1967 to 1989**. Its English pages report Chinatown, North Beach,
  the Richmond and the Sunset at the level of the block: who opened, moved,
  burned, sold, was struck or picketed, and where the community's
  associations, churches, clinics, schools and programmes met. 1,125 issues,
  scanned by the San Francisco Public Library with NHPRC funding.
- **Where:** Internet Archive collection `eastwestnews`. One item per issue;
  identifiers are not chronological (`eastwest01east_5` is 1 January 1967,
  `eastwest02east` is 3 January 1968, `eastwest05east_31` August 1971). The
  page a reader is given is `https://archive.org/details/<id>/page/n<leaf>/mode/1up`,
  where `<leaf>` is the zero-based scan leaf. The issue list with dates is
  `research/corpora/east-west-journal/items.tsv`, rebuilt from
  `https://archive.org/advancedsearch.php?q=collection:eastwestnews&fl[]=identifier&fl[]=date&rows=2000&output=json`.
- **How to get at it:** `https://archive.org/download/<id>/<id>_djvu.txt` per
  issue (about 100 KB each, 110 MB for the run). Four parallel `curl`s took
  about 45 minutes for all 1,125; one at a time is several times slower. The
  djvu text has **no page breaks**, so a finding's page comes from
  `<id>_hocr_searchtext.txt.gz` plus `<id>_hocr_pageindex.json.gz` (character
  ranges per leaf) and `<id>_page_numbers.json` (printed page per leaf, often
  blank on the front page, where leaf + 1 is the page). Volume and number come
  from `https://archive.org/metadata/<id>/metadata` (`volume`, `issue`).
  The run's scripts: the mention extractor matches a number followed by a
  street name in the EAS street list (`3mea-di5p`, grouped by
  `street_name, street_type`) and keeps a 600-character window; a filter drops
  windows naming another city just after the address, residences ("lives at",
  "son of", "Mr. and Mrs."), windows with no event or institution word, and
  windows that read as advertisements (phone numbers, ZIP codes, hours); and
  every address appearing in six or more issues is set aside as an advertiser.
  What survives is read by hand.
- **What is actually usable:** news items and the community calendar
  ("Diversions"), for three kinds of fact. **Dated events at a building**:
  fires (818–820 Washington, 20 December 1970), demolitions (the Kong Chow
  building at 863 Stockton, 5 February 1972), sales (259 Post, 1972),
  dedications and openings of new buildings (the Northeast Health Center over
  the Broadway tunnel, 1971; the Salvation Army's 1450 Powell, 1972), and the
  fights over the International Hotel and the Kong Chow temple at 520 Pine.
  **Retrospective histories** in features and obituaries: the Republic Pharmacy
  opening at 704 Grant in November 1912 before its building was finished;
  the 1937–38 strike at the National Dollar Store factory at 720 Washington.
  **Dated occupancy**: which association, church, clinic, school, bank branch,
  theatre or social-service programme was at a number in a given year. A
  sample: "The Chinese Immigrants Association, an organization to aid new
  arrivals, has been formed with headquarters at 705 Columbus Avenue"
  (28 August 1968). **Not usable:** display advertisements, classifieds,
  wedding, obituary and award notices giving a family's home address, crime
  reports naming victims at their homes, and the Los Angeles, Oakland,
  Sacramento and Hawaii pages.
- **Cautions:**
  - **The OCR mangles digits in a pattern.** A leading `6` reads as `0` or is
    dropped (`015 Jackson` for 615, `001 Commercial` for 601, `0600 Lombard`
    for 660); `9` is inserted before a `0` or `6` (`9065 Clay`, `9605 Clay`
    for 965); a `½` becomes `12` (`73712 Clay` for 737½). Record the number as
    written and resolve by hand only where a clean mention of the same place
    in another issue gives the number; otherwise leave it unresolved.
  - **The same institution is printed at two numbers.** The Great Star Theater
    is 636 Jackson in the news columns and 630 Jackson in its own ads; the
    Chinatown VFW post is 23 Ross Alley in 1967 and 25 in 1968; the Asian
    Community Center is 845 and 846 Kearny in one issue. State the number the
    finding prints and carry the other in `address_note_as_recorded`.
  - **A named building with no number in the article.** Mandarin Tower's 1967
    announcement prints no address; the paper's own 1971 lawsuit story gives
    950 Stockton. That is the same source naming the building, so it resolves
    by hand with the later issue cited in the note.
  - **Adler Place is now Jack Kerouac Alley.** The Chinese Historical Society
    of America's 1969 address, 17 Adler Place, has no EAS record; the article
    gives 1140 Grant Avenue as the frontage.
  - **Calendar listings repeat for weeks.** One event appears in three or four
    consecutive issues; cite the first.
  - **Copyright.** Each issue carries "Copyright 1967 by EAST/WEST Publishing
    Company". Facts extract freely; quotations in findings are the minimum
    clause, and no text is committed.
- **People:** the paper is full of private individuals — residents giving
  their home address in award and wedding notices, crime victims at their
  apartments, tenants, landlords, shopkeepers. None of that is taken. Taken:
  institutions, associations, firms, theatres, churches, schools, and
  architects and contractors of new buildings. A business whose name is a
  family's name (a "___ Bros." or a person's own name) is left out. Fire and
  crime victims are never named; a building's owner is never named, even where
  the paper does.
- **Citation label:** "East/West: The Chinese-American Journal, vol. N, no. N
  (D Month YYYY), p. N" — e.g. "East/West: The Chinese-American Journal,
  vol. 4, no. 50 (23 December 1970), p. 1". The finding's `citation.url` points
  at the leaf.
- **Coverage:** 1967–1969 (136 issues, 2,045 mentions, 256 windows read by hand) and 1970–1972 (150 issues, 2,294 mentions, 360 windows): 91 findings, 70 resolved, 63 published on 54 pages (14 seeded), 7 declined, 21 unresolved. 1973–1989 (839 issues) not yet read; the djvu text for every issue is already in the local corpus.
- **Verified:** 2026-11-13 (1967–1972 read through the mention pass; every resolved finding checked against its page with `check.py --overlap` before and after seeding; PR #615). The extractor and filter scripts are kept in `/mnt/project-files/east-west-journal/`.
