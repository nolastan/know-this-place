# sf-supervisors-journal — Journal of Proceedings, Board of Supervisors (primary)

> **Research dossier.** Rules: [../AGENTS.md](../AGENTS.md) · traps:
> [../LESSONS.md](../LESSONS.md) · register:
> [../SOURCES.md](../SOURCES.md) · cited on pages by the source id
> `sf-supervisors-journal-<meeting date>`, e.g. `sf-supervisors-journal-1971-03-29`.
>
> - **Kind:** printed minutes of the Board's meetings (scanned, Internet Archive OCR) · **Tier:** primary · **Status:** open
> - **Search-invisibility:** high — scanned volumes in the SFPL collection, no index on the web.
> - **Coverage:** 157 volumes 1906–1999 on IA (`sanfranciscopubliclibrary`). 1967–1997 (71 items, volumes 62–92) read for zoning actions at an address on 2026-11-26. 1906–1966 not read.
> - **Local corpus:** `research/corpora/sf-supervisors-journal/` (IA `_djvu.txt`, one per item)
>
> Update this dossier at the end of every pass — the `Verified:` line, the
> coverage note, and anything the pass learned about getting at the source.

- **What:** The Board's own record of every meeting. For buildings, three
  kinds of entry: (1) **Zoning Map ordinances on final passage** — "Ordinance
  adopting Zoning Map amendment, changing use classification of property at
  2374 Eighteenth Avenue from R-2 to C-2 … File 36-71-4, Ordinance No. 159-71
  Finally passed"; (2) **appeals from the City Planning Commission** —
  conditional uses, reclassifications, a landmark refusal (the Goodman Building,
  1975), a Certificate of Appropriateness (Old Fire Station No. 2, 1983) — with
  the Board's vote; (3) landmark designation ordinances, which
  `article-10-landmarks` already carries and which are left out here.
- **Getting at it:** item ids from
  `https://archive.org/advancedsearch.php?q=collection:sanfranciscopubliclibrary+AND+title:(journal+of+proceedings)&fl[]=identifier,date&rows=500&output=json`.
  The volume number plus 1905 is the year (vol. 66 = 1971); from 1975 a year is
  split into two to four items (`journaljanjuneofproceed70sanfrich`,
  `journalofmayaugproceed81sanfrich` …). The `journalofproceed19NNsanf` items
  are not the Board's journal (one is the Police Commission's); skip them.
  OCR from about 1985 on double-spaces every word; collapse whitespace first.
- **Reading an appeal:** from about 1980 an appeal is decided by a pair of
  motions, "approving decision" and "disapproving decision", one adopted and
  the other tabled, then a "Motion adopting findings" a week later. The verdict
  word nearest the file number is often the companion motion's, so every
  appeal was read by hand (`OV.py`). An appeal needs eight votes to overturn
  the Commission (the Chair says so in 1972); "Refused adoption, 6 to 5" means
  the Commission's decision stood. "Disapproving decision … and granting
  conditional use permit with conditions" is the Board granting with its own
  conditions, not a reversal. Dates: the running heads carry the meeting date,
  but OCR sometimes misreads the year (1981 for 1988); check it against the
  file number's year.
- **Cautions:** Appellants, owners and speakers are named; leave them out.
  Supervisors are named in every vote; give the count only. A rezoning of a
  whole block front is written as the range on the first-numbered building.
  Scripts: `/mnt/project-files/sf-supervisors-journal/` (`extract.py` →
  `decide.py` → `cases.py` → `gen.py` → `OV.py` → `convert.py` → `publish.py`).

- **Verified:** 2026-11-26 (volumes 62–92 searched; 160 findings in
`board-actions-1967-1997`.)
