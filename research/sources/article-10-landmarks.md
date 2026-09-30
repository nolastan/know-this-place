# article-10-landmarks — SF Planning landmark designation reports

> **Research dossier.** Rules: [../AGENTS.md](../AGENTS.md) · traps:
> [../LESSONS.md](../LESSONS.md) · register:
> [../SOURCES.md](../SOURCES.md) · cited on pages by one source id per report,
> `article-10-lm<NNN>` (e.g. `article-10-lm061`), whose `query` is the report's PDF.
>
> - **Kind:** PDF reports · **Tier:** primary · **Status:** open
> - **Search-invisibility:** high — scanned or text-poor PDFs, one per landmark, not indexed in any useful way
> - **Coverage:** Article 10 of the Planning Code — the city's individually designated landmarks, one designation document each; DataSF `97yj-54sx` lists 372 rows
> - **Local corpus:** `research/corpora/article-10-landmarks/` (gitignored) — `index.json` (the DataSF rows), `matched.json` (rows joined to pages by APN), `pdf/` and `pdf_rest/`, `txt*/` (text layers), `ocr*/` (Tesseract output)

Update this dossier at the end of every pass — the `Verified:` line, the coverage
note, and anything the pass learned about getting at the source.

## What

Each landmark's designation document, as the city filed it: the Board of
Supervisors' ordinance, the Planning Commission's resolution, and the Landmarks
Preservation Advisory Board's **case report** — owner, location, HISTORY,
ARCHITECTURE, surrounding land use. From about LM070 the case report grows into
several pages of history; from the 1990s it is a full designation report with a
bibliography, and a few early landmarks (Nos. 72, 100) have modern amendment
reports appended. What a report gives, per building: the construction date and
often the architect and builder, alterations and moves with dates, a line of
occupants — the people the building is named for, its businesses and institutions —
and the designation's own dates.

## Access

- **Index:** DataSF `97yj-54sx` — `https://data.sfgov.org/resource/97yj-54sx.json?$limit=1000`
  gives name, address, APN, landmark number, year designated and the PDF's URL.
- **PDFs:** `files.sfplanning.org/documents/preservation/LM<n>.pdf` and
  `sfplanninggis.org/docs/landmarks_and_districts/LM<n>.pdf`, as the index links
  them. No login. About 140 MB for all 370.
- **Text:** `pdftotext -layout`. Most reports before about LM100 are **image-only**
  (72 of LM001–LM100, 117 of LM101 on) and need OCR; the rest carry an old,
  noisy OCR layer. The container this project runs in does not ship Poppler or
  Tesseract — install them for the session: `apt-get install poppler-utils
  tesseract-ocr tesseract-ocr-eng`. Nothing is committed, so this is not new
  tooling.
- **OCR:** `pdftoppm -r 300 -gray` then `tesseract <page> stdout --psm 3`, **with
  `OMP_THREAD_LIMIT=1`** when running several in parallel — without it four
  workers each spawn four OpenMP threads and a page takes 70 s instead of 2.

**Citation label on pages:** "SF Planning, landmark designation"; the source
entry's `name` names the landmark and number, and its `query` is the PDF.

## Cautions

- **DataSF's APN is a hint, not the parcel.** Joining `97yj-54sx` to pages by APN
  found pages for 267 of 372 landmarks, but the APN was stale for several that had
  pages all along: Hallidie Building (0288030 → the building is on 0288027),
  San Francisco Gas Light Co. (0459003, retired 2025 → 0459062), Sunnyside
  Conservatory (6770056 is now the private house at 234 Monterey; the
  conservatory is on 6770057). Run the resolver on the address as well and
  compare; where they disagree, check `sf-parcels` for retirement and the roll's
  build year.
- **One DataSF APN can mean one lot of a much-divided block.** Jackson Square's
  Belli and Genella Buildings (Nos. 9, 10) sit on lots retired or split in 2019
  with no current EAS address; they stay unresolved rather than landing on the
  Golden Era Building next door (No. 19), which the EAS join for "728–730
  Montgomery" picks.
- **The index has errors.** Its row for Trinity Presbyterian Church, 3261 23rd
  Street, says No. 65 but links `LM166.pdf`; that church is No. 166, and 65 is
  Trinity Episcopal on Bush Street. Numbers 93, 116, 126, 166 (as a row), 216,
  219, 224, 230 and 240 have no row. Names are sometimes misspelt ("Bourne",
  "Frances Scott Key") or are a later business's ("Merryvale Antiques" for the
  Gas Light Co. building) — take the report's name.
- **Several landmarks share one parcel and one page.** Nos. 13–16 (407–445
  Jackson) and 22–23 (468–472 Jackson): no `city_landmark` row (it holds one
  landmark), one merged designation entry, and every description names its
  building and number.
- **Park landmarks go on place pages**: the Conservatory (No. 50) on
  `golden-gate-park/conservatory-of-flowers`, the Key Monument (No. 96) on
  `music-concourse`, Sunnyside Conservatory (No. 78) on
  `glen-park/sunnyside-conservatory`. Lotta's Fountain (No. 73) has no parcel.
- **The case report's OWNER line is the owner of the report's day — never take
  it.** Nor the 1950s–70s buyers the Jackson Square reports name, nor artists or
  tenants the report treats as still living. Take the people the building is
  named for and past residents the report puts in the past (a death date, "until
  1916"), with their period. See LESSONS → "A report's own day is 'current'".
- **The ordinance and the case report can disagree on the lot**: LM061's
  ordinance puts the Sylvester House on 4654/13 (the Albion Brewery's parcel);
  the resolution and DataSF say 5340/6.
- **OCR years need the second printing.** Early reports print the history twice
  (resolution and case report); where one copy's digits are garbled
  ("1228", "L341", "1996" for 1906) take the year only if the other copy or the
  context fixes it, and mark `raw.ocr_uncertain`.
- **Much of the early content is already on pages** from NRHP nominations and
  context statements that quote the same case reports. Summarise a page before
  writing notes for it (`research/corpora/article-10-landmarks/pg.py` in the
  run's corpus dir did this); what these reports add is usually the designation
  date, the residents and the post-1906 history.
- **Designation dates**: the effective date where a recorded Notice of Designation
  states one (day precision), else DataSF's `yeardesignated` (year precision).
  The ordinance's final-passage date is not the designation date; the Flood
  Mansion page's 1974-08-02 is the effective date, 30 days after the Mayor signed.
  Secondary sources often give the **Planning Commission's** year instead: the
  Fairmont's National Register nomination says 1986, the year the Commission
  approved it, but the Board finally passed the ordinance on 4 May 1987. Where a
  page already carries the other year, publish the final passage as its own dated
  event and say why in `unknowns`, rather than a second "Designated" entry.
- **Some PDFs are incomplete.** LM160 is one blank page, LM133 one bibliography
  page, LM102 stops mid case report and LM168 holds only the continuation sheets.
  Record the designation from DataSF and what the fragment gives; say so in the
  batch's coverage note.
- **From about LM160 the case report names the owners of its day in the
  narrative too** — the builder's granddaughter who owned 198 Haight in 1983, the
  preservationist who bought 4143 23rd Street in 1966, the last pharmacist of 500
  Divisadero, the Spreckels heirs of 1989. Leave each out and write the fact
  around them ("From 1966 the house was a meeting place of…"); `raw.note` says
  who was left out.
- **An existing page credit can be an alteration's architect.** The Mark Hopkins
  Hotel's page credited the hotel to Timothy Pflueger, who designed only the 1939
  Top of the Mark; the report gives Weeks & Day, and the credit was corrected.
  Where a report's construction credit disagrees with `building.architect`, read
  the page's source for that credit before letting "if not already set" keep it.
- **Landmark numbers quoted by context statements can be wrong.** The Bayview
  Hunters Point Area B statement made 900 Innes Avenue "City Landmark No. 260,
  the Dircks Residence"; it is No. 250, the Shipwright's Cottage (260 is the Tobin
  House). An audit of all 190 `city_landmark` rows against DataSF by APN found
  no other disagreement (bar the LM166 index error above). Our Lady of
  Guadalupe's page carries a similar "No. 244" in its unknowns.
- **From LM201 the reports are full designation reports** — Kalman ratings,
  DPR 523 forms, 10–100 pages of history, owners' names in the text and in
  permit tables. Read the history, significance and integrity sections whole;
  the rest is boilerplate. They are also where the timeline temptation is
  strongest: write one dated fact per entry from the start, or `--overlap`'s
  "by its own date" scan will send half the batch back (batch 4 needed 27
  splits before publishing).
- **A park landmark can span several place pages.** The Murphy Windmill and its
  millwright's cottage, and the Music Concourse with the Spreckels Temple of
  Music, each have a place page per structure; the findings name their page, and
  the park's own parcel page takes only what has no place page (the Park
  Emergency Hospital, No. 201).
- **Campuses, parks and street furniture.** Grace Cathedral's case report is the
  Cathedral School's (the designation is the whole close, 246/1); the High School
  of Commerce page is a campus of several buildings. Neither takes a
  `building.architect` from the report. The Third Street Bridge (No. 194) and the
  Path of Gold standards (No. 200) have no parcel and stay unresolved.

- **The index's APN is wrong outright for several of LM251–LM300**, not just stale:
  LM259 (Noe Valley library) repeats LM258's 0857001A — the ordinance gives 6539/034;
  LM265 (Doelger Building) gives 1762020, the wrong block — the building is 1763/020 and
  021, both with pages; LM292 (Lyon-Martin House) is a float, `6.60404e+006`, for
  6604036; LM291's row links a lookup for 0676035. LM254 (Doggie Diner sign) and LM293
  (Ingleside Terraces sundial) have no address at all. Take the parcel from the
  ordinance's own "Assessor's Block … Lot …" line.
- **Not every PDF is its landmark's report.** LM280–LM282 hold only the Board ordinance,
  whose findings are procedural — one designation finding each. LM262 is the 2009 report
  proposing all eight Appleton & Wolfard branch libraries, and LM300 binds the other
  Carnegie branches' reports after its own; LM289 is a 25-page fact sheet. LM256–LM258
  are one PDF for three buildings on the 55 Laguna campus.
- **From LM251 the reports are community-written nominations as often as staff
  reports** (the Paper Doll's is 224 pages of appendices, the Eagle's and Twin Peaks
  Tavern's are histories told through the bar's owners). They carry the report-day
  owners, bartenders and families on every page, and the owners of 1972–2003 who made a
  bar significant may well be living: name them only where the record says they have
  died. Twenty-one quotes in batch 5 carry `[name cut]`.
- **Designation reports list the architect's other works with addresses and years.**
  Worth taking — they credit buildings the site has pages for — but they are where the
  batch's wrong placements came from: 16 of about 125 such findings were demolished
  buildings (the Coronet, the Haight Theater, the Buena Vista School) or pre-1909
  numbers. Compare every one with the roll year on the parcel the join chose.
- **A report can contradict the building's own history.** LM297's list of Polk's works
  dates the Hallidie Building 1912 (it is 1917–18); LM287 dates the Paper Doll's opening
  1944 against 1949 elsewhere. State it in `unknowns`; don't publish the report's year
  over a page that has it right.

## Structure for mining

| batch | landmarks | designated | state |
|---|---|---|---|
| `batch-1-lm001-lm050` | LM001–LM050 | 1968–1972 | read whole, resolved, published |
| `batch-2-lm051-lm100` | LM051–LM100 | 1973–1977 | read whole, resolved, published |
| `batch-3-lm101-lm200` | LM101–LM200 | 1977–1991 | read whole, resolved, published |
| `batch-4-lm201-lm250` | LM201–LM250 | 1991–2008 | read, resolved, published |
| `batch-5-lm251-lm300` | LM251–LM300 | 2005–2022 | read, resolved, published |
| next | LM301+ | 2022–2025 | not read; fetch `LM<n>.pdf` from the index's `designationdocument.url` |

---

**Verified:** 2026-09-29 — LM001–LM300 read. Batches 1–4 as before (LM001–LM250:
752 findings, 688 resolved, 664 published on 204 pages). **LM251–LM300** (50 reports,
six of them image-only and OCR'd — LM251–255 and LM261): 819 findings, 712 resolved,
639 published on 107 pages (30 seeded), 73 declined — mostly repeats of what the page
had from a context statement, and fourteen of James F. Dunn's credits the pages
already carried — 100 unresolved (the 55 Laguna campus is 29 of them, condominium
parcels, #228), 7 rejected (demolished buildings). Corrected on pages: the Metro
Theater's architect (Reid Brothers; Deichmann was the 1941 remodel), One Montgomery's
(Willis Polk; SOM was the 1979–84 remodel), St. Brigid's (Shea & Shea), the Doelger
Building's and Sam Jordan's Bar's mislabelled "designation" entries, and **22 Beaver
Street's page, which named a current resident** out of a context statement — the
designation report says she still lives there. **Next:** LM301 onward.
