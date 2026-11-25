# sf-art-commission-minutes — Minutes of the San Francisco Art Commission (primary)

> **Research dossier.** Rules: [../AGENTS.md](../AGENTS.md) · traps:
> [../LESSONS.md](../LESSONS.md) · register:
> [../SOURCES.md](../SOURCES.md) · cited on pages by the source id
> `sf-art-commission-minutes-<meeting date>`, e.g. `sf-art-commission-minutes-1954-05-03`.
>
> - **Kind:** meeting minutes (scanned volumes, Internet Archive OCR) · **Tier:** primary · **Status:** open
> - **Search-invisibility:** high — one OCR text per year, no index by building.
> - **Coverage:** 1932-1983 read: building design approvals 1932-1969 (1960-61 not found), works of art 1934-41, and murals, works of art and civic buildings 1970-1983. Source exhausted for buildings to 1983; later volumes not on the Internet Archive.
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
  the minutes are narrative, with no Designer line. From 1962 to 1966 (items
  `artcommissionmin<year>sanf`) each resolution again has a number, a title and
  "held on <date>", and the architect is named in the body ("Appleton & Wolfard,
  Architects"); splitting the flattened text on `RESOLUTION NO.` gives 488
  resolutions (`res6.py`). The 1964-66 stages are Phase 1 (schematic), Phase 2
  and Phase 3 (final drawings), and the architect is often named only at one of
  them. The 1960 and 1961 downloads return Internet Archive error pages. From
  1967 a resolution reads "RESOLVED, That this Commission hereby approves Phase
  N of plans for ..." with no meeting date, so date it by the meeting heading
  before it ("San Francisco, California <date>" or "was held on <date>"; some
  headings are lost to OCR, then use the agenda or page-header dates nearby):
  `res7.py` splits, `mdate2.py` lists headings around a phrase. Architects are
  seldom named after 1967.
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
  curated list, `convert.py`, `publish.py` with `AC_PR` and `AC_FILE`; for
  1962-66 `res6.py`, `F2.py`, `convert2.py`; for 1970-83 `res8.py`, `where.py` (meeting-date evidence around a match), `F6.py`, `convert6.py`, and `AC_ONLY` in `publish.py` to publish named findings of an older file). A design approval that
  contradicts a page's date or credit goes in `conflict` and so in the page's
  `unknowns`.
- **Verified:** 2026-11-25 (14 volumes, 1970-1983: 1,940 resolutions split
  (res8.py), architects almost never named; 36 findings curated onto 28 pages,
  29 of them murals and works of art of the Neighborhood Arts Program and CETA
  years (Crumpler at George Washington High, the Blue Whale on the Oak Street
  firehouse, the SOMArts wall, the General Hospital mosaics, Cloud Hall East at
  City College) and a few civic building approvals. 1501-1525 Silver Avenue
  (Bayview Health Center) seeded: the 1967 stained-glass resolution for it
  (David Arnold; Hertzka and Knowles, architects) is the second fact for the
  parcel held in the 1962-66 batch, which is now published. Learned: from 1981
  the page headers "Minutes (d Month yyyy)" carry the meeting date; earlier,
  "A/C minutes m/d/yy"; res8's dates are a meeting off as often as not. The
  1973 "Bayview Health Center (Marquis & Stoler)" is not the Silver Avenue
  building. Many mural sites (housing projects, Valencia Gardens, Ping Yuen,
  community centres) have no page; listed in the findings file's coverage.)
- **Verified (earlier):** 2026-11-25 (11 volumes, 1949-1959: 771 resolutions extracted,
  182 about a building with a named designer, 31 findings curated onto 29
  pages, 2 of them seeded school pages (Bret Harte, Jose Ortega); 6
  architect credits set where the working drawings and the roll agree.
  Learned: the commission's resolutions are the dated design history of the
  city's own buildings, and engine company numbers are not stable addresses.)
  2026-11-25 (5 volumes, 1962-1966: 488 resolutions, 25 findings curated, 21
  onto 18 pages and 4 held for a page (Lowell, the West Side Health Center at
  1301 Pierce, El Dorado, the Paul Revere annex); 1 architect credit (Wurster,
  Bernardi and Emmons, Golden Gateway garage, roll 1967). Two conflicts stated:
  Station 26 at 80 Digby, dated 1963 by the Modern context statement, had its
  drawings approved in 1965-66; Diamond Heights School, credited to Charles W.
  Griffith, was approved at Phase 1 as Corlett and Spackman's. Learned: Cowell
  Hall in the 1966 minutes is the Academy of Sciences, not City College, and
  the Southeast Health Center is not the 1966 District Health Center No. 3,
  which is the Bayview (Silver Avenue) health center at Barneveld and Silver.)
  2026-11-25 (3 volumes, 1967-1969: 416 resolutions, 15 findings curated, 13
  onto 13 pages and 2 held (Cabrillo School, the Sunset-Richmond health center
  at 1351 24th Avenue). Learned: the meeting dates res7.py guesses from the
  nearest date string are often a month off; check every one against the
  heading.)
  2026-11-25 (17 narrative volumes, 1932-1948: 11 approvals curated onto 11
  pages, mostly the 1933-bond schools approved at the special meeting of
  October 26, 1934; 1 architect credit (William Mooser, Francis Scott Key
  School). These volumes have few numbered resolutions before 1935; search for
  "plans for <named building>" with an architect named nearby. The murals and
  other works of art approved for city buildings in 1934-41 are a separate,
  unread seam.)
  2026-11-25 (8 narrative volumes, 1934-1941, works of art: 26 approvals
  curated onto 13 existing pages: the 1934 Public Works of Art Project
  sketches for Coit Tower, the Mother's House, the Board of Education room,
  Roosevelt, Balboa and John Muir schools; the George Washington High
  frescoes and the frieze's history from Bufano to Sargent Johnson; Mission
  High and Beach Chalet murals; City Hall's Assessor's-room mural and
  vestibule busts; City College's Olmsted sculpture and murals, Volz mosaics
  and the 1940 Rivera fresco. Learned: the Internet Archive items for
  1932-1959 are `minutesofartcomm<year>sanf`, not `artcommissionmin<year>sanf`
  (1962 on); the 1932-48 batch had the wrong one and was corrected. Not
  placed: the Lafayette School lunette, Maynard Dixon's Presidio High murals
  (no page), the Morgue mural and the Exposition works.)
