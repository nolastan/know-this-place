# sffd-reports — San Francisco Fire Department histories and station studies (primary)

> **Research dossier.** Rules: [../AGENTS.md](../AGENTS.md) · traps:
> [../LESSONS.md](../LESSONS.md) · register:
> [../SOURCES.md](../SOURCES.md) · cited on pages by the source id
> `sffd-reports-<year>`, e.g. `sffd-reports-1969`.
>
> - **Kind:** department history and consultant's station study (scanned, Internet Archive OCR) · **Tier:** primary · **Status:** open
> - **Search-invisibility:** high — scanned city reports in the SFPL collection.
> - **Coverage:** the 1967 *Historical Review, 1849-1967* and the 1969 Gage-Babcock station study read whole. The Board of Fire Commissioners' annual reports 1869-1901 (IA `annualreportofbo<year>sanf`, `reportofboardoff<year>sanf`) are unread.
> - **Local corpus:** `research/corpora/sffd-reports/` (IA `_djvu.txt`)
>
> Update this dossier at the end of every pass — the `Verified:` line, the
> coverage note, and anything the pass learned about getting at the source.

- **What:** `sanfranciscof18491967sanf` is the department's own narrative
  history to 1967: the drill towers, the Central Fire Alarm Station (1915), the
  1952 and 1964 firehouse bonds, the training centre at Folsom and 19th (1954),
  the Pioneer Memorial Museum at 655 Presidio (1964) and the headquarters at
  260 Golden Gate (1967). `studyoffiredepar1969gage` is a consultant's study
  whose Tables 4 and 5 (pp. 76-80) give every one of the 47 stations of 1969:
  address, companies housed, year built and remodelled, bays, dormitory,
  ground-floor area, storeys and condition.
- **Getting at it:** `https://archive.org/download/<id>/<id>_djvu.txt`. Table
  4's columns come out of the OCR in reading order (station, address,
  companies, year, lot area); transcribed by hand in
  `/mnt/project-files/sffd/T.py`.
- **Fire statements (measured 2026-11-25):** ten of the Board of Fire
  Commissioners' reports (1882-1895 fiscal years) carry a statement of every
  fire: date, alarm box, street address, occupancy, frame or brick, cause and
  loss (the facing page also names owners; leave them out). The page images
  read cleanly (`page/n<leaf>_w1400.jpg`; leaves found from `_djvu.xml` by
  searching for "OCCUPIED"). But across all ten years only about 16 rows give
  a street number that has a page today outside the 1906 burn and the
  renumbered districts, and most are trivial (a woodshed, a $10 loss) at
  buildings the roll dates only to its 1900 placeholder. On 2026-11-26 Stan
  asked for them anyway: 14 rows in the Mission and Eureka Valley read from the
  images (`fire-statements-1883-1895`, `/mnt/project-files/sffd/fires.py`),
  cause and loss matched row by row from the facing page and left out where
  the rows did not line up. Each is written as the building then at the
  address. Pacific Heights and Hayes Valley rows were left alone for the 1909
  renumbering.
- **Cautions:** Station numbers in 1969 are not today's. The table's year
  built disagrees with some pages' dated contracts by a year or more (460 Bush,
  100 Hoffman, 1298 Girard); where a page already dates the building, the year
  is left out of the 1969 entry. Firefighters named in the history are left
  out, as are the people they rescued.

- **Verified:** 2026-11-25 (both documents read; 50 findings in
`fire-stations-1967-1969`, 35 published on 34 pages; 15 unresolved because
the station, the headquarters or the training centre has no page.)
