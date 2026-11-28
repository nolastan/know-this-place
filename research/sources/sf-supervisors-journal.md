# sf-supervisors-journal — Journal of Proceedings, Board of Supervisors (primary)

> **Research dossier.** Rules: [../AGENTS.md](../AGENTS.md) · traps:
> [../LESSONS.md](../LESSONS.md) · register:
> [../SOURCES.md](../SOURCES.md) · cited on pages by the source id
> `sf-supervisors-journal-<meeting date>`, e.g. `sf-supervisors-journal-1971-03-29`.
>
> - **Kind:** printed minutes of the Board's meetings (scanned, Internet Archive OCR) · **Tier:** primary · **Status:** open
> - **Search-invisibility:** high — scanned volumes in the SFPL collection, no index on the web.
> - **Coverage:** 157 volumes 1906–1999 on IA (`sanfranciscopubliclibrary`). 1967–1997 (71 items, volumes 62–92) read for zoning actions at an address on 2026-11-26. 1946–1966 (22 items, volumes 41–61) read the same day for every measure at a numbered address (`board-actions-1946-1966`). 1926–1931 (vols 21–26) read on 2026-11-28 for the Board's garage, filling-station and parking-station permits (`board-permits-1926-1931`). 1926–1945 (vols 21–40) read the same day for every other measure at a numbered address (`board-measures-1926-1945`). 1906–1907 (vols 1–2) not read; vols 3–20 (1908–1925) are not on IA; leases and other non-zoning measures in 1967–1997 not read.
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

- **1946–1966: what the volumes hold.** Before 1960 a rezoning is almost
  always written by frontage or by lot and block ("south side of Jerrold
  Avenue, 275 feet from Phelps"), so the zoning yield before 1960 is nearly
  nil; numbered addresses appear in zoning titles only from the 1960 Planning
  Code on. The address-dense measures are instead the city's own **leases**
  ("Authorizing lease of ground floor space at 498 Sanchez Street, required
  for the Noe Valley Health Center"), purchases, sales of surplus property,
  and appropriations for work on city buildings. The lease titles name the
  lessor, usually a private person: cut it from `raw.text` and the page;
  firms and public bodies (Kohler & Chase, the Red Cross, the Housing
  Authority, the Regents) may be named. Before 1949 the measure is printed in
  full under its title ("Proposal No., Resolution No. … Resolved …"), and the
  body carries the floor, term, rent and purpose; from 1949 a title, "File No.,
  Resolution No.", a bracketed note and the vote. A blank "Resolution No." means
  the measure was not adopted at that meeting.
- **Dates:** take the meeting date from the upper-case running head ("MONDAY,
  OCTOBER 24, 1966"), never from a date in the text — continuances and hearing
  dates ("continued to Monday, November 7, 1966") are written in the same form
  and moved 19 of 448 dates when matched case-blind.
- **A list keyed by company is not a list of sites.** The 1953 firehouse bond
  appropriation (Ordinance No. 7953) lists "land purchases for new sites for:
  Engine 39 — 1091 Portola Drive; Engine 13 — 1458 Valencia Street …"; those are
  the companies' existing firehouses, not the sites bought. Declined.
- **Scripts** for 1946–1966 (scratch, not in the repository): a title scan for
  street number + street over every measure-shaped paragraph, then a reader
  that prints each measure from its title to its "Adopted by"/"Finally passed"
  line.

- **Verified:** 2026-11-26 (volumes 62–92 searched; 160 findings in
`board-actions-1967-1997`.) 2026-11-26 (volumes 41–61, 1946–1966: read 22
items, 448 address-bearing measure titles over 157 addresses, found 93
findings, resolved 63, published 60 on 53 pages, 4 seeded; 3 declined, 9 held,
21 not placed. Learned: the leases are the yield, not the zoning; where a
building replaced the one leased (68 Post, 1255 California) the entry says "the
building then on this lot"; 45 Hyde Street was the Main Library Annex on the
Asian Art Museum's parcel, demolished 1997; one held fact of the 1967–1997
batch, 2232 Webster's 1967 rezoning, was taken up on a page seeded here.)

- **1926–1931: the Board's own use permits.** Until the City Planning
  Commission took them over (the last in vol. 26, 1931), the Board granted
  "revocable at will" permits by resolution to operate a public garage, an
  automobile supply station (a filling station) or an automobile parking
  station, and to transfer one to a new operator. Each resolution appears
  twice: passed for printing under the day's new business, adopted the next
  week under **Unfinished Business**; the section a resolution falls in is
  its status (`permits.py` marks N/U), and a grant seen only once under N is
  dropped. About a third give a street number; most filling stations are
  "the northeast corner of X and Y", placed with `corner.py --json` only where
  one parcel on the quadrant lies within 80 ft of the crossing and 25 ft
  nearer than the next (23 of 193); offsets along a block face were not
  extracted. One fact per site and use, the earliest adopted grant or
  transfer. Permittees are individuals and are left out; a garage's own name
  ("Granada Garage") is kept. Where the roll's building is more than four
  years younger the entry reads "This site previously held …". Laundry,
  dyeing-and-cleaning, oil-tank and boiler permits run through the same
  volumes (laundries also 1906–07) and were not extracted: hundreds a year,
  each naming a private permittee, one thin fact apiece. Scripts:
  `/mnt/project-files/sf-supervisors-journal/early/` (`permits.py` → `mk.py` →
  `resolve_eas.py` → `corners.py` → `publish.py`).
- **1932–1966 rezonings by frontage:** a scan of vols 27–61 for rezonings and
  Planning appeals near a street number found 83 numbered addresses in 35
  volumes; the rest are corners and frontages ("the northwesterly corner of
  37th Avenue and Taraval Street for a distance of 100 feet"). Not pursued.

- **Verified:** 2026-11-28 (volumes 21–26, 1926–1931: 1,256 permit
  resolutions → 315 sites with an adopted grant → 67 published on 67 pages
  (19 framed as an earlier use of the site), 20 held, 228 not placed.)
- **1926–1945: the other measures.** A scan of every title that follows a
  blank line, ends in a period, is mostly capitalised and carries a street
  number (`early/titles.py`) gives about 1,650 lines over vols 21–40, nearly
  all noise: the Recorder's imprint, letterheads, election-officer lists, the
  1937 business-licence roll, and the permits already taken. About sixty are
  measures, read one by one: the city's leases for public use (two 1935
  storefront library reading rooms, WPA and NYA projects, 1943–45 air-raid
  warden, war-housing and teen-age centres), city-owned houses sold for
  removal ahead of street openings, The Emporium's 1932 bridge and subway
  across Jessie Street, the municipal kitchen for the unemployed at 52 Ritch
  (1931–33), the German consulate at 2090 Jackson (1941), and the Mayor's
  annual report for 1942, printed in the Journal of 25 January 1943, which
  lists the buildings the federal government leased or bought for the war.
  **Nuisance abatements** (about fifteen, 1932–43) are bare declarations
  with nothing about the premises; left out. A lease to the city names an
  individual lessor; left out, a company lessor (Daily News Company,
  Arrillaga Musical College) kept where it tells what the building was.
- **Verified:** 2026-11-28 (volumes 21–40 measures: 46 findings, 27
  resolved, 23 published on 23 pages, 2 held, 1 declined as already on the
  page, 1 left unplaced by hand (60 Harold, a house moved off land taken for
  Mount Vernon Avenue); 19 at numbers the city no longer has.)

- **2026-11-28, held facts taken up:** parcel 3722126 (199 New Montgomery)
  got a page, so its two held permits were published as site history: an
  automobile parking station on the corner (30 April 1928) and a gasoline
  filling station (22 April 1929).
