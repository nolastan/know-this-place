# building-industrial-news — *Building and Industrial News* (primary)

> **Research dossier.** Rules: [../AGENTS.md](../AGENTS.md) · traps:
> [../LESSONS.md](../LESSONS.md) · register:
> [../SOURCES.md](../SOURCES.md) · cited on pages by the source id `building-industrial-news`.
>
> - **Kind:** journal OCR · **Tier:** primary · **Status:** open
> - **Search-invisibility:** high — see the register for what that rates.
> - **Coverage:** 1 of 8 half-year volumes read (vol. 14 pt. 2, July – December 1914): 149 facts on 134 pages (52 seeded). Unread: vol. 11 pt. 1 (1911) to vol. 14 pt. 1 (January – June 1914). See the `Verified:` line.
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
  with a nearest parcel not accepted, 681 not placed. Unread: the seven
  volumes before July 1914.
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
  of the later run was taken up on a page seeded here.)
