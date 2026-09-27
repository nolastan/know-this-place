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
- **Campuses, parks and street furniture.** Grace Cathedral's case report is the
  Cathedral School's (the designation is the whole close, 246/1); the High School
  of Commerce page is a campus of several buildings. Neither takes a
  `building.architect` from the report. The Third Street Bridge (No. 194) and the
  Path of Gold standards (No. 200) have no parcel and stay unresolved.

## Structure for mining

| batch | landmarks | designated | state |
|---|---|---|---|
| `batch-1-lm001-lm050` | LM001–LM050 | 1968–1972 | read whole, resolved, published |
| `batch-2-lm051-lm100` | LM051–LM100 | 1973–1977 | read whole, resolved, published |
| `batch-3-lm101-lm200` | LM101–LM200 | 1977–1991 | read whole, resolved, published |
| next | LM201+ | 1991–2025 | PDFs on disk (`pdf_rest/`); mostly text layers; not read |

---

**Verified:** 2026-09-27 — LM001–LM200 read whole. **LM001–LM100** (99 reports;
No. 93 has no index row): 330 findings, 307 resolved, 289 published on 84 pages
(6 seeded). **LM101–LM200** (98 reports; Nos. 116 and 126 have no row, No. 166 is
the row mislabelled 65): 232 findings from 92 reports (six gave nothing the page
lacked), 210 resolved, 205 published on 81 pages (6 seeded: 1265 Battery,
964 Eddy, 1190 Noe, 893 Wisconsin, 2501 25th Street, 1648 Pacific), 5 declined as
repeats, 22 unresolved over 10 landmarks — condominiums (Nos. 101, 129, 141,
168), no EAS address (105, 111), a double house now on two parcels (191), and
no parcel at all (114, 194, 200). The earlier attempt (PR #439, closed unmerged)
had read only the text-layer reports and published nothing; its branch was not
built on. **Next:** LM201 onward, mostly text-layer designation reports of
1991–2025.
