# habs-haer — HABS, HAER and HALS documentation, San Francisco (primary)

> **Research dossier.** Rules: [../AGENTS.md](../AGENTS.md) · traps:
> [../LESSONS.md](../LESSONS.md) · register:
> [../SOURCES.md](../SOURCES.md) · cited on pages by the source id
> `habs-haer-<loc item id>`, e.g. `habs-haer-ca1239`.
>
> - **Kind:** PDF reports with a text layer · **Tier:** primary · **Status:** done
> - **Search-invisibility:** high — the historians' reports are PDFs behind an item page whose catalogue record carries only a title and a location.
> - **Coverage:** every San Francisco item with data pages read: 129 of 384 items (the rest are photographs and drawings only).
> - **Local corpus:** `research/corpora/habs-haer/` (one `pdftotext -layout` file per item)
>
> Update this dossier at the end of every pass — the `Verified:` line, the
> coverage note, and anything the pass learned about getting at the source.

- **What:** The National Park Service's three documentation programs — the
  Historic American Buildings Survey (HABS, since 1933), the Historic American
  Engineering Record (HAER, since 1969) and the Historic American Landscapes
  Survey (HALS, since 2000) — deposited at the Library of Congress. Each
  documented place has photographs, sometimes measured drawings, and **data
  pages**: a written report with a fixed head (location, present owner and use,
  significance, date of erection, architect, original owner, builder,
  alterations) followed by a historian's narrative and bibliography. San
  Francisco has 384 items. Most date from three bursts: 1958-1965
  photograph-data books on landmarks (Old Mint, Octagon House, Montgomery
  Block); 1977-1995 mitigation reports written before a building was
  demolished or gutted (Sheldon, Blake Moffitt & Towne, Holbrook and Grace
  Buildings, City of Paris, the 1952 North Beach Place); and 2010-2020 HALS
  landscape reports (Alta Plaza, Fay Park, Mission Dolores cemetery, University
  Mound Nursery).
- **Where:** The page a reader is given is the item:
  `https://www.loc.gov/item/caNNNN/`. The data pages are served from
  `https://tile.loc.gov/storage-services/master/pnp/habshaer/ca/ca<NN00>/caNNNN/data/caNNNNdata.pdf`
  (where `<NN00>` is the item number rounded down to the hundred, e.g.
  `ca1200/ca1239`). The HABS, HAER or HALS number (e.g. HABS CA-2203) is in the
  item's "Data Pages from Survey ..." caption, which is the reliable place to
  read it; the PDF's own header is often OCR-mangled ("CA-20^6").
- **How to get at it:** The collection listing is
  `https://www.loc.gov/collections/historic-american-buildings-landscapes-and-engineering-records/?q=san+francisco&fo=json&c=100&sp=N`,
  four pages for San Francisco. **The JSON API sits behind Cloudflare and
  returns a "Just a moment" page** to fast or repeated requests; space the four
  requests 20-25 seconds apart and keep each good page the moment it arrives.
  The `tile.loc.gov` PDFs are not behind the challenge and download directly.
  Each item's `resources` tells you whether data pages exist (the caption
  "Data Pages from Survey ..."); 129 of 384 do. `pdftotext -layout` reads the
  text layer; no OCR is needed, though the 1950s-60s typescripts carry
  character errors in numbers ("18S8", "S70-S98") — skip a garbled number, do
  not correct it.
- **What is actually usable:** The data-page head and the narrative's dated
  events: construction with architect, engineer and builder; additions with
  their architects; changes of use and owner; moves; demolitions of
  predecessors; and incidental credits in the architect biography ("A list of
  his work includes the Standard Oil Building at 200 Bush Street ..."). Not
  usable: the ~60 one-page cover sheets that give only a name and a location;
  undated passing credits where the page already names an architect.
- **Cautions:**
  - **Many reports describe a building that is gone.** A mitigation report is
    written because the building is about to be demolished; the address it
    gives may be retired, and the page for that parcel holds the replacement.
    Read the roll year against the report's date of erection, put the fact on
    the page as `site history` and say "since replaced". The record's own block
    and lot, where printed, is the way to the parcel (`acdm-wktn` keeps retired
    lots and tells you which are still active).
  - **The address is today's number, whatever the fact's date.** Set
    `extra.record_date` to the report's year so `resolve_eas.py` does not refuse
    an 1886 fact under the 1909-renumbering guard.
  - **Half of what it says is on the page already.** The reports document
    landmarks, and Article 10, the National Register and the environmental
    reviews have usually covered the same building: 50 of 116 placed findings
    were repeats. Run `check.py --overlap` before writing anything.
  - ca0729's data PDF is an Old Sacramento form filed under the wrong item.
  - The Thomas Church garden report withholds the address on purpose; leave it.
- **People:** The reports name architects, engineers, builders, original
  owners (mostly firms and long-dead clients), and notable residents of
  landmark houses (Daniel O'Connell at the Octagon House; Adolph and Alma
  Spreckels; the Montgomery Block's writers and artists; the Phelps family).
  Those are used, as `occupancy` entries. The 1970s-90s reports sometimes name
  the owner at the time of the report and the families displaced by a housing
  project; none of that is transcribed.
- **Citation label:** label `Historic American Buildings Survey, Library of
  Congress` (or Engineering Record, Landscapes Survey); name `Historic American
  Buildings Survey, HABS CA-2203, Sheldon Building (1982), data pages. Library
  of Congress, Prints and Photographs Division.`; `cites` gives the data pages
  the entries rest on.
- **Coverage:** All 129 San Francisco items with data pages read
  (`san-francisco-2026-11`). Skipped on purpose, and recorded in the findings
  file's coverage note: cover sheets, the Loma Prieta damage-survey stubs,
  Golden Gate Park features with no page, the Aquatic Park pier, the Market
  Street HALS parcel inventory, and the 13 per-building North Beach Place
  reports. Seven facts are held for a page (`check.py --held`): the Blake,
  Moffitt and Towne Building on block 3709 lot 11, and single credits at 2003
  Franklin, 2083 Pacific, 412 Jackson and 900 North Point (Ghirardelli Square).
- **Verified:** 2026-11-20 (129 reports read, 145 findings, 116 placed (101 by
  `resolve_eas.py`, 15 by hand from the record's block and lot or bounds), 62
  published on 31 pages, 3 of them seeded (North Beach Place's two blocks and
  University Mound Nursery), 54 declined (50 as repeats of the page), 7 held,
  22 unplaced. Learned: a HABS report is the last record of a building about to
  go, so resolve it to the replacement's parcel by the printed block and lot,
  and expect landmark reports to repeat what Article 10 and the Register
  already gave the page.)
