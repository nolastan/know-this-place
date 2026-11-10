# noehill — NoeHill in San Francisco (secondary)

> **Research dossier.** Rules: [../AGENTS.md](../AGENTS.md) · traps:
> [../LESSONS.md](../LESSONS.md) · register:
> [../SOURCES.md](../SOURCES.md) · cited on pages by source ids `noehill-<page>`, one per NoeHill page (for example `noehill-cal0080`, `noehill-nat1991000957`).
>
> - **Kind:** web guide · **Tier:** secondary · **Status:** done
> - **Search-invisibility:** low — see the register for what that rates.
> - **Coverage:** all 682 landmark, register, state-landmark, district and point-of-interest pages read; 619 findings, 549 resolved, 368 published
> - **Local corpus:** `research/corpora/noehill/` (gitignored: `default.html`, `links.txt`, `pages/`)

- **What:** A long-running private guide to San Francisco's designated
  places, one page per city landmark (`sf/landmarks/sf<NNN>.asp`), California
  historical landmark (`cal<NNNN>.asp`), National Register listing
  (`nat<refnum>.aspx`), historic district (`sf_<name>.aspx`) and city
  "point of interest". Each page carries photographs, the plaque text where
  there is one, and NoeHill's own notes; most of the rest is quoted from the
  city's designation report or the National Register form.
- **Where:** the index is <https://noehill.com/sf/landmarks/default.aspx>; each
  page is cited at its own URL under `https://noehill.com/sf/landmarks/`.
- **How to get at it:** a plain `curl` of the index, then every linked page
  under `sf/landmarks/` (682 fetched; 5 links returned errors). No rate
  limiting was met at one request a second. Pages are old ASP with inline
  markup: the building header is `<span>` or `<p>` with class
  `NameAddress…`, and blocks on a page are split by a `blue_diamonds` image.
- **What is actually usable:**
  - **District building tables.** The district pages carry a table of every
    contributor — name, year, address, architect or remarks. Fourteen tables
    key their rows by street address (583 rows). This is the one part of the
    site that is denser than what the project already held: Jackson Square,
    Lower Nob Hill Apartment Hotel, Second and Howard, the Market Street
    Theatre and Loft district, Dogpatch and the Market Street masonry
    district had not been read from their nominations. Eleven more tables key
    rows by federal building number or park area and were not taken.
  - **NoeHill's own notes** on landmark and point-of-interest pages: plaque
    sites (the Montgomery Block, the California Star, the Jenny Lind), the
    city's firehouses, hotel and theatre openings, later uses, and notable
    past residents (Edgar Mathews at 2980 Vallejo, Ruth Cravath at 893
    Wisconsin).
  - **Not usable:** the passages quoted from designation reports and
    National Register forms (already mined as `article-10-landmarks` and
    `nrhp-nominations`, and better read there), and passages credited to
    Wikipedia.
  - Example district row (Lower Nob Hill): `Dennis T. Sullivan Fire Chief's Home
    | 1922 | 870 Bush Street | John Reid Jr.`
- **Cautions:**
  - **It quotes its sources without saying so.** Most of a landmark page is
    the designation report verbatim, so the page overlaps the project almost
    completely. 154 district rows and 24 prose facts were declined as
    duplicates of what pages already carried.
  - **Typos in addresses and names**: "Marketv", "Buah", "Joes" (Jones),
    "Russsian Hill", "Dashiell Hammitt", "Van Ttees" (Van Trees). Corrected on
    the findings, each with a note.
  - **Some district years disagree with better sources**, most often in
    Jackson Square, where several rows give 1906 for buildings the designation
    reports date to the 1850s. 17 disagreements are written to the pages'
    `unknowns`, not their timelines.
  - **Known wrong:** it says the 1920 Democratic convention in the Civic
    Auditorium nominated Franklin Roosevelt (Roosevelt was the vice-presidential
    nominee; only the convention itself is taken); it dates Bloody Thursday to
    6 July 1934 (it was 5 July); it gives the Miramar Apartments 1911 on one
    table and 1917 on another; it gives Top of the Mark both 1936 and 1939.
  - Plaque sites often have no EAS address now (608 Commercial, 243
    Sacramento, 1538 Valencia, 269 Bush, 406 Market, 202 Green). They are left
    unresolved, so no page carries them.
- **People:** architects and builders, and notable past residents the page
  names, written as `notable_residents` rows. Names in district tables'
  building names ("Eugene McCoy House") are historic names from the
  nominations. No current occupant is taken.
- **Citation label:** `NoeHill in San Francisco, "<page title>"`, linking the
  page. Example: `NoeHill in San Francisco, "California Historical Landmark
  #80: Montgomery Block Site"` → `https://noehill.com/sf/landmarks/cal0080.asp`.
- **Coverage:** every page linked from the index was read once
  (`findings/noehill/districts.json`, `findings/noehill/landmark-pages.json`).
  Nothing remains. Reopen only if the site adds pages.
- **Verified:** 2026-11-05. Read 682 pages and 583 table rows. Found 619
  findings (465 district rows, 154 prose facts), resolved 549 and published
  368 on 335 pages, 85 of them seeded. **Lesson:** a secondary web guide
  to designated places will repeat the designation reports. Read its tables
  first, because that is where its new material is, and run `--overlap` before
  writing anything.
