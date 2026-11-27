# building-industrial-news — *Building and Industrial News* (primary)

> **Research dossier.** Rules: [../AGENTS.md](../AGENTS.md) · traps:
> [../LESSONS.md](../LESSONS.md) · register:
> [../SOURCES.md](../SOURCES.md) · cited on pages by the source id `building-industrial-news`.
>
> - **Kind:** journal OCR · **Tier:** primary · **Status:** open
> - **Search-invisibility:** high — see the register for what that rates.
> - **Coverage:** 7 of 8 half-year volumes read (July 1911 – December 1914): 912 facts on 803 pages (315 seeded). Unread: vol. 11 pt. 1 (January – June 1911). See the `Verified:` line.
> - **Local corpus:** `research/corpora/building-industrial-news/`
> - **Claimed:** every unread volume, by the project run that opened this source (2026-11-24). The placed-and-held rows are **not** claimed: they stay logged and unpublished until another fact gives the parcel a page, and whoever seeds that page takes them up after reading each against the page image (`check.py --held <manifest>`; [AGENTS.md](../AGENTS.md#facts-held-for-a-page)).
>
> Update this dossier at the end of every pass — the `Verified:` line, the
> coverage note, and anything the pass learned about getting at the source.

- **What:** the San Francisco building-trade weekly that became *Building and
  Engineering News* (see [building-engineering-news.md](building-engineering-news.md),
  whose run starts in January 1915). Published Wednesdays. The title changed
  with the issue of 9 December 1914, inside vol. 14 pt. 2, so the last four
  issues of that volume are cited as *Building and Engineering News*. Each
  issue prints the week's **building permit applications** and recorded
  **building contracts** for San Francisco and the East Bay as numbered
  entries, in the same form as the 1915 volumes: where the lot is, what is to
  be built, the owner, the architect, the contractor and the cost.
- **Where:** Internet Archive, scanned by the San Francisco Public Library,
  eight half-year volumes: `buildingindustri11111cont`,
  `buildingindustri11211cont` (1911), `buildingindustri1212cont`,
  `buildingindustri12212cont` (1912), `buildingindustri1313cont`,
  `buildingindustri13213cont` (1913), `buildingindustri1414cont`,
  `buildingindustri14214cont` (1914). Reader link
  `https://archive.org/details/<id>/page/n<index>/mode/1up`, `<index>` the
  zero-based page index of `<id>_djvu.xml` (one less than the jp2 number).
- **How to get at it:** as for `building-engineering-news`: the `_djvu.xml`
  (about 100 MB a volume) for text with word boxes, page jp2s from the
  item's `_jp2.zip` for the image check.
- **Method:** the `building-engineering-news` method and its cautions apply
  unchanged (split the OCR into numbered entries, set the East Bay aside,
  build the lot from the block corner against today's parcel shapes, accept
  on a lot line where the roll year fits, **read every row to be published
  against the page image**, hold plain single houses with no page). The
  pipeline is a copy of that run's scripts in the project's shared files
  under `building-industrial-news/` (not in the repository): `env.sh <item>
  <tag>`, `lines.py`, `issues_wed.py` (lists the dated Wednesday heads; the
  issue starts are the cover leaves, "Issued Weekly … Fourteenth Year, No.
  N"), `BEN_LOOSE=1 extract.py`, `place.py`, `select.py`, `leafmap.py`,
  `crops.py`, `gen.py`, `sheets.py`, `tall.py` (tall crops of the contracts,
  for the contractor and TOTAL COST the short crop cuts off), `fx.py`,
  `seedprep.py`, `refile.py`, `publish.py`, `post14214.py`,
  `scrub_owner.py`.
- **People:** architects, designers, engineers, contractors and firms are
  published. **Owners who are private individuals are never published** and
  are cut from `raw.text`; a firm or institution named as owner is kept.
  Sureties are cut. A contractor or architect who is the owner, shares the
  owner's surname, or is listed at the owner's premises is cut with the
  owner.
- **Citation label:** "Building and Industrial News, 15 July 1914" (from 9
  December 1914, "Building and Engineering News, 9 December 1914"), with
  the page link. Page source ids are
  `building-industrial-news-<issue date>-n<index>`.
- **Coverage, vol. 14 pt. 2** (`buildingindustri14214cont`, 1 July – 30
  December 1914, 27 issues): 2,231 numbered entries; 1,416 San Francisco
  rows; 735 placed on a parcel; 204 picked and read against the image; 149
  published on 134 pages, 52 of them seeded. Unfinished: 212 placed single
  houses and small alterations held until the parcel gets a page, 347 rows
  with a nearest parcel not accepted, 681 not placed.
- **Coverage, vol. 14 pt. 1** (`buildingindustri1414cont`, 7 January – 24
  June 1914, 25 issues; cover leaves 6, 60, 114 … 1330, 54 leaves an issue
  with two longer ones): 2,065 numbered entries; 1,282 San Francisco rows;
  609 placed on a parcel; 139 picked and read against the image; 98
  published on 93 pages, 51 of them seeded. Unfinished: 157 placed single
  houses and small alterations held until the parcel gets a page, 673 not
  placed.
- **Coverage, vol. 13 pt. 2** (`buildingindustri13213cont`, 2 July – 31
  December 1913, 27 issues; cover leaves 6, 60, 114 … 1414): 1,990 numbered
  entries; 1,339 San Francisco rows; 645 placed on a parcel; 173 picked and
  read against the image; 118 published on 110 pages, 36 of them seeded
  (2 more declined as repeats of the page).
  Unfinished: 157 placed single houses and small alterations held until the
  parcel gets a page, 694 not placed.
- **Coverage, vol. 13 pt. 1** (`buildingindustri1313cont`, 7 January – 25
  June 1913, 25 issues, Tuesdays until 20 May and Wednesdays after; cover
  leaves 6, 44, 82 … 952, 38 leaves an issue with a few longer ones): 2,547
  numbered entries; 1,494 San Francisco rows; 785 placed on a parcel; 205
  picked and read against the image; 151 published on 139 pages, 46 of them
  seeded. Unfinished: 162 placed single houses and small alterations held
  until the parcel gets a page, 709 not placed.
- **Coverage, vol. 12 pt. 2** (`buildingindustri12212cont`, 2 July – 31
  December 1912, 27 issues, all Tuesdays; cover leaves 8, 42, 76, 152,
  194 … 1058, the 16 July issue 76 leaves with the City Hall competition
  plates): 2,458 numbered entries; 1,549 San Francisco rows; 722 placed on
  a parcel; 228 picked and read against the image; 153 published on 139
  pages, 51 of them seeded. Unfinished: 142 placed single houses and small
  alterations held until the parcel gets a page, 827 not placed. Unread:
  the three volumes before July 1912.
- **Coverage, vol. 12 pt. 1** (`buildingindustri1212cont`, 2 January – 25
  June 1912, 26 issues, all Tuesdays; cover leaves 4, 32, 60, 90, 122 …
  822): 2,274 numbered entries; 1,383 San Francisco rows; 434 placed on a
  parcel; 122 picked and read against the image; 90 published on 83 pages,
  28 of them seeded. Unfinished: 91 placed single houses and small
  alterations held until the parcel gets a page, 949 not placed.
- **Coverage, vol. 11 pt. 2** (`buildingindustri11211cont`, 4 July – 26
  December 1911, 26 issues, all Tuesdays; cover leaves 8, 40, 74, 108, 140 …
  828): 3,105 numbered entries; 1,846 San Francisco rows; 731 placed on a
  parcel; 209 picked and read against the image; 151 published on 140
  pages, 51 of them seeded. Unfinished: 147 placed single houses and small
  alterations held until the parcel gets a page, 1,115 not placed. Unread:
  vol. 11 pt. 1.
- **Verified:** 2026-11-24 (vol. 14 pt. 2: read 2,231 entries, found 1,416
  San Francisco rows, resolved 149, published 149 on 134 pages. Learned: the
  entries have the 1915 layout, with "COST, $…" closing each permit;
  `extract.py` here reads a label followed by ". ." so the contractor field
  survives (1,462 of 2,231 entries); the issue covers, not the mastheads,
  start each issue; DataSF's EAS table no longer has
  `address_number_suffix` or `unit_number`, so `dl_eas.py` asks for neither;
  on 15 existing pages the paper names the architect the page already
  credited from a survey, which is the independent check on the placements;
  one corner placement was held because the page credits other architects;
  a permit and its contract can be read together across issues (935
  Sanchez, 2280 Vallejo, the Clift Hotel's trade contracts); one held fact
  of the later run was taken up on a page seeded here. Vol. 14 pt. 1, same
  day: read 2,065 entries, found 1,282 San Francisco rows, resolved 97,
  published 97 on 92 pages. Learned: an offset printed with a fraction
  ("310-4 13-16 S Cabrillo") is parsed as two lots and has to be merged by
  hand in `all.json` before `publish.py`; an interior fit-up contract must
  not set the building's architect (449 Powell); where the instalments and
  the printed total disagree, give no cost; `post<tag>.py` and
  `cuts<tag>.py` are per-volume, copy them; three held facts of the later
  run were taken up on pages seeded here, with the later run's
  `takeup.py`. Vol. 13 pt. 2, same day: read 1,990 entries, found 1,339 San
  Francisco rows, resolved 120, published 118 on 110 pages. Learned: for 1913 the pages
  often carry the same contract already from the San Francisco Call's daily
  list (26 of 120), so run `check.py --overlap` and decline or trim before
  the build, and where the two prices differ by a digit trust the page
  image read here; the OCR
  misreads a leading or middle digit of the item number often enough
  ("3357" among 2356 and 2358) that the run of numbers on the leaf should
  be checked for every published row; a contract paid part in cash and part
  by a deed gets no cost; `heldcrop.py <item> <leaf> <words> <out.png>`
  crops a held fact's entry from any Internet Archive item for the image
  check; four held facts were taken up, three of the later run and one of
  vol. 14 pt. 1. Vol. 13 pt. 1, same day: read 2,547 entries, found 1,494
  San Francisco rows, resolved 151, published 151 on 139 pages. Learned:
  the paper came out on Tuesdays until 20 May 1913, so `issues_wed.py`
  finds nothing and the covers ("Year, No. N. JANUARY 7, 1913") date the
  issues; list the Call entries beside the candidates before the image
  check (40 of 205 here) so repeats are dropped or trimmed as the sentences
  are written; a permit for a building that was not the one built (Geary
  and Mason) is a record only and must not set a builder; a corner whose
  page credits another architect is held (Geary and Jones). Vol. 12 pt. 2,
  2026-11-27: read 2,458 entries, found 1,549 San Francisco rows, resolved
  153, published 153 on 139 pages. Learned: `prep.sh <year>` and
  `finish1.sh <manifest>` now hold the steps between `select.py` and the
  seeding; a crop cut by a column break can be finished from
  `lines.jsonl` (the entry runs on in the next column), taking a cost only
  where the instalments add up; a held fact's cost should be read on the
  image before it is believed ($15,500 in the OCR was $450); #761 merged
  while vol. 13 pt. 1 was being pushed, so check the PR is still open
  before pushing and stamp `publish.pr` with the PR that carries the
  commit. Vol. 12 pt. 1, same day: read 2,274 entries, found 1,383 San
  Francisco rows, resolved 90, published 90 on 83 pages. Learned: the
  Call's one-line entry can add up two contracts of this paper (2152 Union:
  $11,280 there is $5,600 and $5,680 here), so compare the scope before
  calling a price different; the tall crops show the printed total where
  the sheet crop stops at the first instalment, so read them before going
  to the OCR; a name printed under the wrong label (J. F. Dunn as
  "Contractor") is left out, not corrected. Vol. 11 pt. 2, same day: read 3,105
  entries, found 1,846 San Francisco rows, resolved 151, published 151 on
  140 pages. Learned: the 1911 volumes print the street before the side
  ("Valley S 255 E Castro", "Octavia and Union SW", "Andover No. 754"), so
  `place.py` needs `BEN_STREET_FIRST=1` or it places nothing; a contact
  sheet of the entry headings is the quick way to check the item numbers
  that break the running order.)
