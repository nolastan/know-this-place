# sf-art-commission-minutes — Minutes of the San Francisco Art Commission (primary)

> **Research dossier.** Rules: [../AGENTS.md](../AGENTS.md) · traps:
> [../LESSONS.md](../LESSONS.md) · register:
> [../SOURCES.md](../SOURCES.md) · cited on pages by the source id
> `sf-art-commission-minutes-<meeting date>`, e.g. `sf-art-commission-minutes-1954-05-03`.
>
> - **Kind:** meeting minutes (scanned volumes, Internet Archive OCR) · **Tier:** primary · **Status:** open
> - **Search-invisibility:** high — one OCR text per year, no index by building.
> - **Coverage:** 1949-1959 design-approval resolutions read. 1932-1948 and 1960-1983 unread.
> - **Local corpus:** `research/corpora/sf-art-commission-minutes/` (IA `_djvu.txt`, one per year)
>
> Update this dossier at the end of every pass — the `Verified:` line, the
> coverage note, and anything the pass learned about getting at the source.

- **What:** The Art Commission's minutes, one volume a year in the SFPL
  collection: `minutesofartcomm1932sanf` to `…1959sanf`, then
  `artcommissionmin1960sanf` to `…1983sanf` (plus undated `artcommissionmin19sanf_N`
  items). Under the 1932 charter the Commission approved the design of every
  city building, structure and park work, so each school, firehouse, library,
  recreation center and pool built by the city passed through it, usually two
  or three times (preliminary drawings, final preliminary, working drawings).
- **Getting at it:** `https://archive.org/download/<id>/<id>_djvu.txt`. From
  1949 to 1959 each approval is printed as `RESOLUTION NO. NNNN-YYYY-S <PROJECT>
  RESOLVED, That at a Regular Meeting ... held on <date> ... the commission
  approved the <stage> drawings for <project>. Submission by <department>.
  Designer: <architect>.` — a regex over the dehyphenated, whitespace-flattened
  text pulls 771 resolutions, 314 with a Designer line
  (`/mnt/project-files/sf-art-commission/ext2.py`). Before 1949 and after 1959
  the minutes are narrative, with no Designer line.
- **Usable:** the project, the design stage approved, the date and the
  designer. The designer is a credit for the building where the approval is at
  the working-drawings stage or later and the roll or the facility confirms the
  building was built then; a preliminary approval alone does not set
  `building.architect`.
- **Cautions:**
  - Resolutions name a project, not an address. Place a school by the CDE
    school directory, a firehouse, library or police station by the city
    facilities register (DataSF `nc68-ngbr`, now on data.sf.gov), a
    playground or pool by its Recreation and Park place page.
  - **Engine company numbers moved:** the 1959 "Engine House No. 14, Oak between
    Gough and Franklin" is today's Station 36 at 109 Oak, and "Engine House No.
    15, 2150 California" is today's Station 38. Place by the location the
    resolution gives, never by the company number.
  - Many of these buildings were later credited from *Architect and Engineer*
    (`architect-engineer-california`); the minutes add the dated approvals.
  - OCR garbles resolution numbers and some names (Cantlin for Cantin,
    Wolford/Wolpard for Wolfard); the year in a resolution number is
    unreliable.
  - Out of scope: works outside the city (the airport in San Mateo County,
    Hetch Hetchy, Crystal Springs, Camp Mather, Log Cabin Ranch), engineering
    works, signs and marquees on private buildings (whose owners are named).
- **People:** architects, landscape architects and engineers; commissioners'
  names are not transcribed.
- **Citation label:** "Minutes of the Art Commission of the City and County of
  San Francisco, <date>, Resolution No. <n>", URL the IA item page.
- **Scripts:** `/mnt/project-files/sf-art-commission/` (`ext2.py`, `F.py` the
  curated list, `convert.py`, `publish.py` with `AC_PR`).
- **Verified:** 2026-11-25 (11 volumes, 1949-1959: 771 resolutions extracted,
  182 about a building with a named designer, 31 findings curated onto 29
  pages, 2 of them seeded school pages (Bret Harte, Jose Ortega); 6
  architect credits set where the working drawings and the roll agree.
  Learned: the commission's resolutions are the dated design history of the
  city's own buildings, and engine company numbers are not stable addresses.)
