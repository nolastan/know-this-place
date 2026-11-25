# sf-municipal-reports — San Francisco Municipal Reports (primary)

> **Research dossier.** Rules: [../AGENTS.md](../AGENTS.md) · traps:
> [../LESSONS.md](../LESSONS.md) · register:
> [../SOURCES.md](../SOURCES.md) · cited on pages by the source id
> `sf-municipal-reports-<fiscal year>`, e.g. `sf-municipal-reports-1909-10`.
>
> - **Kind:** annual reports (scanned volumes, Internet Archive OCR) · **Tier:** primary · **Status:** open
> - **Search-invisibility:** high — thousand-page volumes whose OCR text is reachable only item by item; no index names a building.
> - **Coverage:** the City Architect's reports for fiscal years 1907-08 through 1912-13 (vols 57-62) read. Earlier and later volumes unread.
> - **Local corpus:** `research/corpora/sf-municipal-reports/` (IA `_djvu.txt`, one file per volume)
>
> Update this dossier at the end of every pass — the `Verified:` line, the
> coverage note, and anything the pass learned about getting at the source.

- **What:** The city's annual bound reports, one volume per fiscal year
  (July to June), printed by the Board of Supervisors from 1859 to 1917. Each
  holds every department's report. For buildings the useful parts are the
  **Report of the City Architect** (from 1907-08: each school, firehouse, police
  station, hospital and the new City Hall built from the 1904 and 1908 bonds,
  with contractor, architect, contract price and dates of letting and
  completion), the **Superintendent of Schools' property list** ("Names and
  location of schools", one line per school with its street corner) and the
  **Fire Department roster** (each company with its house number).
- **Where:** Internet Archive, collection of the San Francisco Public Library
  scans. Items `sanfranciscomuni56sanfrich` to `…61sanfrich` (FY1906-07 to
  1911-12) and `munisanfrancisco62sanfrich` to `…66sanfrich` (FY1912-13 to
  1916-17). Download `https://archive.org/download/<id>/<id>_djvu.txt`.
- **Getting at it:** grep the volume for "CITY ARCHITECT" to find the report
  (vol 57 pp. 736-742, vol 58 pp. 565-571, vol 59 pp. 606-632, vol 60
  pp. 919-927, vol 61 pp. 1077-1087, vol 62 pp. 579-582). Page numbers are the
  printed running numbers in the OCR. Vol 56 has no City Architect report.
- **Usable:** one finding per building contract or completion, with the
  contractor (builder) and the architect where the report names one. The
  City Architect designed most buildings himself; outside architects are named
  for the big schools and the firehouses of 1909-12.
- **Cautions:**
  - The reports name a school or engine company, not an address. Place a school
    by the same volume's school property list and a firehouse by the Fire
    Department roster (both give the corner or house number), then by the
    `near` search of the scratch locator. Three schools (Garfield, Laguna
    Honda, Sunnyside) were left unplaced because the reports and lists give
    different corners.
  - Outside Lands lettered avenues: B = Balboa, C = Cabrillo, H = Irving,
    I = Judah, J = Kirkham.
  - The roll's `year_property_built` of 1900 on school parcels is a
    placeholder; check the building against the page before setting spec rows.
    Spec rows (`building.builder`, `building.architect`) were set only where the
    standing building is the one the report describes; replaced buildings get a
    `site history` entry.
  - The 1913-14 bond tables (vol 63 pp. 322-340, Board of Public Works
    bookkeeper's report) come out column-scrambled in the OCR: the school, the
    contractor and the amounts land in separate runs, and rows slide between
    schools (the OCR puts Albert Pissis under Girls' High; the image puts him
    under Oriental). Read them from the page images,
    `https://archive.org/download/munisanfrancisco63sanfrich/page/n<page+17>_w1400.jpg`;
    the names are on the even page and the amounts on the odd page facing it.
    Vols 64-66 print no comparable tables that the OCR finds.
  - Landmark pages (firehouses, City Hall) already carry National Register or
    Article 10 text: trim to what is new and note price conflicts (contract
    price against finished cost).
  - Skipped as not building facts: the 1908 survey of the City Hall ruin,
    temporary schools and sheds, repairs, yard work and playground field houses.
- **People:** contractors, architects and the City Architect only. The reports
  name no private owners.
- **Citation label:** "San Francisco Municipal Reports for the fiscal year
  <fy>, Report of City Architect, p. N", URL the IA item page.
- **Scripts:** `/mnt/project-files/sf-municipal-reports/` (`F.py` the findings
  spec, `convert.py` builds the findings file and must not be re-run over a
  resolved file, `publish.py` with `MR_PR`).
- **Remaining:** the pre-1906 volumes (Board of Public Works and
  Superintendent of Schools reports on the 1870s-1900s schools and
  firehouses), and the 1913-17 tables from the page images. One fact is held
  for a page (`check.py --held`): Engine No. 1 at 451 Pacific (block 175 lot 27).
- **Verified:** 2026-11-25 (FY1913-14 bond tables read from the images: 6
  school contracts, 5 on pages and 1 held (Marshall, 1575 15th); builder set
  on Columbus, 1541 12th, and Washington Irving, 350 Broadway; Glen Park and
  Cooper not placed.) 2026-11-25 (6 City Architect reports read, 72 findings, 38
  placed and published on 35 pages, 14 of them seeded school pages, 33
  unplaced with a reason, 1 held. Learned: a public-works report names
  buildings, not addresses; the same volume's school list and fire roster are
  the address book for it.)
