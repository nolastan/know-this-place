# sfra-property-summaries — Redevelopment Agency parcel files, Western Addition Area 2 (primary)

> **Research dossier.** Rules: [../AGENTS.md](../AGENTS.md) · traps:
> [../LESSONS.md](../LESSONS.md) · register:
> [../SOURCES.md](../SOURCES.md) · cited on pages by the source id
> `sfra-property-summaries-<item>-p<pdf page>`.
>
> - **Kind:** scanned survey forms and file papers, read from page images · **Tier:** primary · **Status:** open
> - **Search-invisibility:** high — hand-filled forms whose OCR is noise; nothing in them is findable by address.
> - **Coverage:** the 7 Property Summary items (724 PDF pages), the 9 House Moves items (438), the 10 Parcel Appraisal Reports (1,388), the 50-building conservation study (40) all 23 Yerba Buena items (568) read whole, and the nine comparable-sales volumes 5030 to 5038 (1,072) parsed, with every sheet that reaches a page or a held parcel read against its image; the four-volume Market Data Study, 5020 to 5023 (868 pages, 278 sales), front pages read by eye and every used price read against its image; the 1962-64 A-2 acquisition appraisals 5001 to 5013 (1,188 sheets) parsed, with every sheet that reaches a page read against its image; the later appraisals 5014 to 5019 and 5024 to 5029 unread.
> - **Local corpus:** `research/corpora/sfra-property-summaries/`
>
> Update this dossier at the end of every pass — the `Verified:` line, the
> coverage note, and anything the pass learned about getting at the source.

- **What:** The San Francisco Redevelopment Agency's per-parcel files for
  Western Addition project area A-2 (Calif. R-54), from the San Francisco
  History Center's SFH 371. Each file opens with a **Property Summary** (SFRA
  FORM P-10, 8/10/62) filled in by hand through 1962: block and lot, address,
  parcel dimensions, number of buildings, assessed land and improvements,
  dwelling units and type, business names, zoning and any non-conforming use,
  and three ratings with their dates — exterior (#1 good to #4 very poor),
  comprehensive interior, and historical/visual merit (no, limited, notable,
  exceptional) — with a lot diagram and a small photograph. Behind the form the
  agency kept filing for twenty-five years: photo sheets captioned by a later
  archivist (before and during rehabilitation, **houses "before move to" a new
  address**, renumbered rows), bank and agency appraisal sheets, a compliance
  letter, a Form No. 1 permit history, 1957 acquisition dividers.
- **Where:** Internet Archive collection
  `sanfranciscoredevelopmentagencyrecords` (106 items, public domain; credit
  "From the San Francisco History Center, San Francisco Public Library").
  The Property Summary items are `SFH371-5049` (blocks 672-678, 144 PDF pages),
  `-5050` (683-697, 118), `-5051` (701-749, 160), `-5052` (754-795, 98),
  `-5053` (806, 14), `-5054` (1100-1125, 100) and `-5054_0` (1126-1130, 90).
  The House Moves items are `SFH371-5087` (Buchanan Street, 8 PDF pages),
  `-5088` (Octavia, 14), `-5089` (Turk, 18), `-5090` (Webster, 26), `-5091` and
  `-5092` (Victorian Square, 32 and 146) and `-5093` to `-5095`
  ("Unidentified", 24, 106 and 64): 438 pages, all dated 1974 by the library.
  A page cites `https://archive.org/details/<item>/page/n<pdf page - 1>/mode/1up`.
- **How to get at it:** `https://archive.org/download/<item>/<item>.pdf`, then
  `pdftoppm -r 100 -jpeg` to one image per page; the IA per-page JPEG endpoint
  is far slower. Odd pages are fronts, even pages mostly blank backs. **Read by
  eye, a handful of pages at a time**; 100 dpi is enough for all but faint
  pencil. The transcription is `read.jsonl` in the corpus directory (one JSON
  line per page: form, photo or doc), with a copy and the scripts in
  `/mnt/project-files/sfra-property-summaries/`: `build.py` (read.jsonl to
  findings), `decide.py` (the by-hand placements, holds and declines),
  `publish.py`, `takeup_ben.py`. The order is build, `resolve_eas.py apply`,
  decide, `resolve_eas.py manifest`, `seed-list`, publish.
- **What is actually usable:** The form, wherever its address survives; a
  later note on the form (`9/7/67 Permit #341719 repair fire damage $2500`);
  a dated caption; the permit history on a compliance letter or Form No. 1
  (`YR. BUILT 1925 … BUILDING PERMIT DATES 1925 TYPE WORK DONE New 4 unit
  apt.`). Not usable: the recommendation-for-disposition block, which is blank
  on nearly every form; undated photo sheets (most of them); the appraisal sheets,
  which give a parcel number and no street number.
- **Cautions:**
  - **The building at the address today is often not the building on the
    form.** This is the project area: most forms describe a building since
    cleared (52 of 205 findings have no address left; 16 more sit under a
    building the roll dates after 1962), and **the agency moved Victorians
    onto emptied lots in the 1970s**, so a surviving address with a roll year
    of 1900 can hold a different house from the one surveyed there. Five forms
    were declined for that (1714-16 and 1720 Fillmore, 1815 Sutter, 1335 Scott,
    45 Beideman). Treat every "re-lotted" line in `resolve_eas.py report` as a
    warning, and read the form's photograph against the building before
    publishing on a re-lotted parcel.
  - The same captions run the other way: a form at 743 Turk, 751 Turk,
    216-220 Elm or 1356-62 Scott describes a house that now stands at 1321
    Scott, 1840 Eddy, 1331-35 Scott or 1239-45 Scott. Those are carried to the
    page of the house, by hand, with the caption cited in `resolution.method`.
  - **Other sources' facts on the destination addresses predate the house.**
    A 1925 permit at 47 Beideman or a 1906 contract at 1840 Eddy is about the
    building that stood there before the move.
  - O'Farrell Street's Endicott Court row (block 728, lots 25-28) was
    renumbered after 1962 and the captions' old-to-new pairs are not in order;
    the four forms are held, not published.
  - Faint pencil: assessed values, lot numbers and a few street numbers are
    marked `unc` in read.jsonl and left out of descriptions. The last forms of
    `-5054_0` (blocks 1129-1130) were erased and reused; nothing but the block
    and lot is legible.
  - One lot can hold several buildings with one rating each ("743 - No. 3
    Poor; 751 - No. 1 Good"); `build.py` leaves a split rating out, and the
    by-hand findings restate it per building.
- **The House Moves items are photographs, not files.** Nearly every one of
  their 438 pages is a print of a house on dollies, or a contact sheet, whose
  back carries only a photographer's stamp and a negative or roll-and-frame
  number. Four captions name an address (5087 p. 4, 5089 pp. 9-13, 5090 p. 17,
  5094 p. 88), in the same "block/lot - address before move to block/lot -
  address" form as the Property Summary captions. Read them as a contact sheet
  of 24 pages at a time and zoom only the backs with writing; a full-size read
  of every page costs ten times as much and finds nothing more. Fourteen backs
  in 5094 (pp. 60-86) carry a 1970s block and lot alone (766/4 to 766/31,
  767/5 to 767/18) with no street number and no direction of move: below the
  evidence bar, and recorded in the findings file's coverage note, not as
  findings. A caption that names a resident "at time of move" names the
  1970s buyer, not a historic occupant; it is not transcribed.
- **The 1955 Parcel Appraisal Reports describe only what was cleared.** They
  are the Agency's appraisals of the A-1 parcels it meant to buy (blocks 713 to
  737, 754 to 756, 1078, 1097 to 1099): typed sheets with the address, a
  building description, sometimes the year built, a rent schedule, a photograph
  and, in the fuller reports, the deed history and owner. The Internet Archive
  text layer misses most sheets; Tesseract at 300 dpi reads them well (1,388
  pages in about 30 minutes with four workers). But no appraised property
  stands today: the 44 parcels on those blocks with a pre-1956 building are the
  ones the Agency did not buy. Run any further acquisition file
  resolution-first — ask the roll which parcels on its blocks still hold an old
  building, then look only for those (see LESSONS).
- **The Yerba Buena block files are undated photographs.** Prints labelled
  with a 1960s block and lot (red or pencil on the back, or typed on a
  1970s-80s colour mount), a few with an address or a building's name, none
  with a date except the Hotels item (1961, by the library). An undated print
  is below the evidence bar however good its address.
- **People:** Every form names the owner of record, with a home address and
  often a telephone number, and says whether the owner lives there. **None of
  that is transcribed**: read.jsonl has no owner field, so nothing downstream
  can leak it. A business named for its proprietor is flagged `pname` and is
  described by its trade only. Appraisers, photographers, loan applicants and
  letter addressees on the attached papers are not recorded. The collection's
  "Community: Identified People" items (SFH371-5079 to 5086) are files about
  displaced residents by name and are not to be read at all.
- **Citation label:** `Redevelopment Agency Records (SFH 371), San Francisco
  Public Library (Internet Archive)`, with the source `name` "Western Addition
  Area 2 property summary file, block 677 lot 13, 1942 Sutter Street. San
  Francisco Redevelopment Agency Records (SFH 371), San Francisco History
  Center, San Francisco Public Library." On a page a 1962 form is one
  `historical_record` entry of kind `inspection`; a moved house is
  `building.relocated_from`. Say what the inspectors found, never that the
  parcel "was surveyed".
- **Overlap:** [`digitalsf`](digitalsf.md) holds the catalogued photographs of
  the same SFH 371 archive. A fact in both is one fact.
- **Coverage:** Read: the seven Property Summary items, every page
  (`western-addition-a2-1962`); the nine House Moves items, 5087 to 5095
  (`house-moves-1974-1979`, 2026-11-18); the ten Parcel Appraisal Reports, 5039
  to 5048 (`parcel-appraisals-1955`, zero findings); the Yerba Buena Phase 1
  Hotels, Breen's and block files, 5061, 5063 and 5064 to 5076
  (`yerba-buena-subject-files`); the 50-building conservation study, 5000
  (`conservation-study-1962`, 2026-11-24); and the last eight Yerba Buena
  items, 5055 to 5060, 5077 and 5078 (`yerba-buena-photo-items`, 2026-11-24).
  The comparable-sales volumes, 5030 to 5038 (`comparable-sales-1966-1970`,
  2026-11-25): about 130 sheets on parcels with no page were parsed from the
  OCR but not read against their images (list in
  `/mnt/project-files/sfra-comparable-sales/nopage.txt`).
  The Market Data Study, 5020 to 5023 (`market-data-1965-1969`, 2026-11-28):
  about 77 sheets whose address reached neither a page nor a standing building
  were not hand-read.
  The 1962-64 acquisition appraisals, 5001 to 5013
  (`acquisition-appraisals-1962-1964`, 2026-11-28): about 146 sheets on
  standing parcels with no page were parsed but not read against their images
  (three held). **Not read: the later A-2 appraisals, 5014 to 5019 and 5024
  to 5029** (1963 and 1970 to 1990, specific parcels; 5017 is not online). Take the **comparable-sales volumes
  first** (5030 to 5038, 1969-70, about 1,100 pages): a comparable sale is a
  property the Agency did *not* buy, often outside the project area, so these
  sheets describe buildings that can still stand, and each one is typed with
  the address, block and lot, lot size, deed date, price and often the year
  built — the one sheet of this kind read so far (5059 p. 3) published. The
  acquisition appraisals (5001 to 5029) describe what was bought, so run them
  resolution-first, per LESSONS. Do not read 5077, the New Start Center: its
  prints are portraits of displaced residents, some named on the backs.
  Held for a page: 76 facts (`check.py --held`; 1340 Golden Gate was taken up with a Bay Area Reporter page on 2026-11-24). Left out as findings: two
  1957 appraisal sheets with no street number (block 702 lot 23, block 733
  lots 1 and 1A), an undated service-station appraisal at 1301 Golden Gate
  Avenue, and five 1957 acquisition dividers for the cleared 1700 block of
  Geary.
- **The 50-building conservation study (5000) is a captioned photo album.**
  Fifty prints, each typed with a sample number, a dwelling-type class
  (Single Family to 10+ Family, RH for rooming house, Hotel; a "-C" suffix the
  album never explains, left as recorded), the address and the 1962 block and
  lot, then the 15-building FHA Conservation Standards Sample repeated. No
  ratings and no text: the fact is the selection and the photograph. Sample
  14's caption is faint; the repeat gives 938-42 Buchanan. Sample 35 is lot 35
  in one place and lot 18 in the other. Being picked for a *conservation*
  study did not save a building: 9 of the 26 that resolve sit under a building
  the roll dates 1971 to 1991.
- **Verified:** 2026-11-28 (the Western Addition A-2 Market Data Study,
  5020 to 5023, compiled about 1970: four volumes, by kind of property —
  vacant land and single-family, residential-commercial and commercial, two
  and three units, four plus units — 868 PDF pages, 278 sales recorded 1964 to
  1969, each a front page and a sales page. 192 front pages read by eye from
  cropped strips (`addr.py`), matched by address to a parcel and checked
  against the roll's year built and building area, which agree to the square
  foot on most sheets; 101 findings: 45 published on 45 pages, 7 declined (two
  sales already on the page from the comparable-sales volumes, two
  foreclosure figures, three sheets whose comments describe a different
  building from the front page), 49 held on a parcel with no page. Learned:
  **the front page's typed fields (address, type, year built, area) are too
  faint to OCR** but read by eye at w1800; the sales page OCRs well, yet even
  a three-pass OCR vote got 5 of about 95 prices wrong ($55,000 as 58,000,
  $28,000 as 23,000), so every price was read against the image; the
  roll's building area is the best check that a sheet's building still
  stands; and a sheet's comments sometimes belong to a different property
  than its front page (2121 Sacramento, 640 Octavia, 2100 Post), so a
  contradiction between the two is a reason to leave the sale off. Corporate
  parties are named where the comments give them (the Scottish Rite's sale of
  1859 Geary to the Order of the Eastern Star, Twentieth Century-Fox buying
  645 Larkin, Harcourt, Brace and World buying 1000 Geary). Scripts in
  `/mnt/project-files/sfra-market-data/` (`strips.py`, `addr.py`, `res.py`,
  `match.py`, `pubset.py`, `mkfind.py`, `publish.py`).)
- **Verified:** 2026-11-28 (the A-2 acquisition appraisals 5001 to 5013:
  Maury Holmes's 1962 sheets by block and his first acquisition report of
  20 January 1964. 1,188 sheets parsed from the OCR, 494 resolved to a parcel,
  263 to a building the roll dates before 1962, 117 to an existing page; those
  117 read from cropped bands of the page images. 91 findings: 88 published on
  88 pages, 3 held; 15 sheets left out because their address only reached a
  page across the street or a renumbered lot whose building does not fit.
  Learned: **the A-2 rehabilitation area kept most of what Holmes appraised**
  (about half the resolved sheets still stand), so these volumes, unlike the
  1955 A-1 reports, land on pages; **many lots were renumbered after 1962**
  (684-21 is now 684-46), so place by parcel number first and by address
  within the block second, and check the roll's stories; the 1962 sheets
  carry a typed description and condition, the 1964 sheets only present use
  and building area. Scripts and the hand transcriptions in
  `/mnt/project-files/sfra-acquisition-appraisals/` (`extract.py`, `bands.py`,
  `T.py`, `table.py`, `mkfind.py`, `publish.py`).)
- **Verified:** 2026-11-25 (the comparable-sales volumes 5030 to 5038:
  1,072 PDF pages, about 330 typed sale sheets parsed from the OCR and
  resolved by their block and lot; 59 read against the page image, 52
  findings: 43 published on 40 pages, 5 of them seeded because a held fact
  already waited on the parcel (1590 Sutter, 1980 Eddy, 867 Oak, 66 Haight,
  1270 Fell), 6 held facts taken up with them, 7 sales held, 1 declined, 1
  unplaced. Learned: **the OCR misreads the price on most sheets** ($20,000 as
  "320,000", $25,000 as "925,000"), so nothing is published from the text
  layer; **the pasted photograph covers the SOLD block on about one sheet in
  eight**; a sheet's block and lot beats its address for placing it, since
  the OCR address often lands on the other side of the street; and a property
  can appear twice, sold and resold after a remodel (226-28 Haight, $50,000 in
  1968 and $72,000 in 1969), which is worth stating as two entries. Scripts in
  `/mnt/project-files/sfra-comparable-sales/` (`read.py` transcriptions,
  `mkfind.py`, `publish.py`).)
- **Verified:** 2026-11-24 (the conservation study and the last eight Yerba
  Buena items read: 302 PDF pages, 56 findings, 6 resolved, 6 published — five
  1962 sample photographs on 1 Cottage Row, 1868 Buchanan, 1843-49 Bush, 2109
  Bush and 1310 Turk, and a 1961 sale of the 1913 hotel at 265 Third Street,
  now a vacant lot — 10 held, 13 placed on a later or merged building and left
  unresolved, 27 with no surviving address. Learned: a comparable-sales sheet
  describes a property the Agency did not buy, so it is the part of an
  appraisal file most likely to land on a standing building or a page.)
- **Verified:** 2026-11-18 (House Moves, Parcel Appraisal Reports and Yerba
  Buena subject files read: 2,132 PDF pages, 12 findings, 4 resolved, 1
  published — 1737 Webster Street's `building.relocated_from` from the Turk
  Street move caption — and 2 declined as repeats; the appraisal batch is a
  recorded zero. Learned: in a redevelopment collection, the files about
  acquisition describe what was cleared, so ask the roll what survives before
  reading; and most of this archive's prints carry a negative number or a
  block and lot, not a caption.)
- **Verified:** 2026-11-15 (all seven items read from page images: 724 pages,
  211 forms, 205 findings, 80 resolved, 50 published on 37 pages, 7 of them
  seeded, 30 declined, 66 held, 59 unplaced, 52 of them with no surviving
  address. Three held
  *Building and Engineering News* facts on two seeded parcels were read
  against their page images and taken up. Learned: in a redevelopment area a
  surviving street number is not a surviving building, and the agency's own
  move captions are what tell them apart.)
