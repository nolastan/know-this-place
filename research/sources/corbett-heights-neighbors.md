# corbett-heights-neighbors — Local history research (secondary)

> **Research dossier.** Rules: [../AGENTS.md](../AGENTS.md) · register:
> [../SOURCES.md](../SOURCES.md) · cited on pages by the source id `corbett-heights-neighbors`.
>
> - **Kind:** newsletter archive · **Tier:** secondary · **Status:** open
> - **Search-invisibility:** high — see the register for what that rates.
> - **Coverage:** 32 of the archive's 50 issues read — everything from January 2025 to September 2026. The 18 issues of 2024 and earlier are untouched.
> - **Local corpus:** `research/corpora/corbett-heights-neighbors/`
>
> Update this dossier at the end of every pass — the `Verified:` line, the
> coverage note, and anything the pass learned about getting at the source.

- **What:** The Corbett Heights Neighbors newsletter carries researched
  per-building history — first owners, contractors, permit dates and stated
  build costs, drawn from building permits, federal censuses and period
  newspapers. The association also publishes Michael Corbett's *Corbett
  Heights: San Francisco, An Historic Context Statement* (2017).
- **Archive:** <https://corbettneighbors.optin.com/newsletter/awlist6655060>
  (association site: <https://corbettneighbors.com>)
- **How to cite:** name the specific issue — title, volume and number, and
  publication date — and link that issue, not the archive index. Where the
  newsletter names its own underlying source (a permit date, a census year, a
  dated newspaper item), **repeat that in the citation** so the chain is
  auditable.
- **Facts, not prose — and cite in the footer only.** Extract discrete facts
  and present them as timeline items, spec rows, tiles and tags; never
  paraphrase the source's sentences (facts aren't copyrightable, wording is).
  **Never name the newsletter in the page body** — it means nothing to a
  reader with no context for it; the citation lives in the Sources footer.
  See `san-francisco/corbett-heights/AGENTS.md`.
- **Cautions:**
  - **Historical addresses.** Street numbers changed in 1909, streets were
    expunged by the Market Street extension, and buildings have been
    demolished, so an address in the newsletter may not exist today. Check
    EAS before creating a page (see
    `san-francisco/corbett-heights/AGENTS.md` for worked examples).
  - **Photograph dates contradict the assessor.** The newsletter dates
    buildings from photographs; the assessor's `year_property_built` often
    disagrees, in both directions. Record both and name the conflict in the
    page's `.unknowns` — never reconcile them silently.
  - **Buildings were moved.** At least one (11 Mars, from Falcon Street) was
    relocated, so a construction date may belong to a different site.
  - **Living people.** Some issues are personal memoirs naming family
    members and the houses they lived in. Take the building facts; leave the
    people out, per the privacy rules in the root AGENTS.md. Deceased
    figures already published with dates (first owners, builders) may be
    named with citations.
  - **The issues follow a family, not a building.** A single article walks
    an owner from address to address — the September 2026 brewery piece
    names eight addresses across four neighbourhoods, most of them somebody's
    house rather than a subject in its own right. The dated construction and
    site facts are the harvest; a bare "he later moved to" is an undated
    occupancy with no component to carry it, and is declined.
  - **The star address is often the one that no longer exists.** The
    brewery the September issue is about, at 111–121 Douglass Street, was
    demolished in 1915 for the Market Street extension and has no EAS record;
    its site is now the eleven condominium parcels of 2750 Market Street,
    which cannot carry a page either. Eight dated facts about it are
    `unresolved` for that reason. What reached a page is the site history of
    **109 Douglass Street**, the partner's house that survived next door.
  - **Filing a lost address on the street hub costs the hub's automation.**
    `seed_pages.py hubs` refuses to rebuild any street hub that has grown a
    section beyond the generated template, which is why the Danvers Street hub
    carries "The lost corner". Danvers has four pages; Douglass Street has a
    hundred and gains more with each seeding run, so freezing its list was the
    worse trade and the brewery went onto the surviving building's page
    instead. **Weigh the hub route by how big the hub is.**
  - **Archive page numbers are not a stable batch unit.** The archive
    paginates by recency, ten or eleven issues to a page, so an issue slides
    from page 1 to page 2 as new ones are published. The January 2026 issue was
    read as part of "page 1" and came back as part of "page 2" two months
    later, and four of its facts had to be declined as already published.
    **Batch by issue date, and check the newest unread date, not the page.**
  - **The masthead's volume number is wrong twice.** September and October 2025
    print "Vol. VI"; the run of volumes either side makes them Vol. VII. Cite
    the volume as printed and let the publication date carry the identification.
  - **The 1976 assessor block photographs are a recurring feature and are
    mostly captions.** A street number and the make of a car parked outside it
    — 68 of the 96 numbered-address mentions across ten issues. Extract one
    only where the caption states something about the *building*: "destroyed by
    fire October 20, 2016", "formerly Wilt Chamberlain's home", "demonished".
  - **The historical article, not the feature, is where the yield is.** One
    researched piece — April 2025 on 310 Corbett Avenue — produced an
    architect, a dated set of plans, a fire, a repair permit and eight years of
    ownership. The photograph lists produced two facts in ten issues.
  - **A renumbering the newsletter states itself is still worth a cross-check.**
    It converts 2 Merritt Street to 3000–3002 Market and 4 Merritt to 3004
    Market. The first checks out — EAS has 3000 MARKET ST on the corner
    parcel at Hattie, built 1890, four years before the 1894 event. The second
    resolves to nothing: EAS has no 3004, the block face runs 3000, 3006, 3008,
    3012.
  - **2 Mars Street is 4465 17th Street.** The neighborhood AGENTS.md recorded
    that no 2 Mars exists; the corner parcel 2654001 is the Belle-V Apartments,
    and the roll's 1961 matches the build year the January 2026 issue gives.
  - **655 Corbett Avenue cannot have a page.** It is a 39-unit condominium of
    1964 and EAS carries the number on one parcel only, which is unit 105. The
    resolver used to read that as the building; it no longer does.
  - **A worked 1909 renumbering pair:** 77 Clara Avenue is today's **81 Ord
    Street** (August 2026 issue), alongside the 110 Clara → 110 Ord and
    1200 Ashbury → 1200 Clayton pairs already in
    `san-francisco/corbett-heights/AGENTS.md`.
  - **An issue can disagree with itself in passing.** The August 2026 piece
    dates 99 Ord Street to 1932 twice, with a day-precise completion, and
    writes "1937" once in a sentence about the lot's dimensions. Take the
    date the article argues for and record the slip in the finding rather
    than on the page.
- **Coverage so far:** the archive holds 50 issues. **32 have now been read**
  — every issue from January 2025 to September 2026 — in three passes:
  the August and September 2026 issues (`vol-viii-no-8`, `vol-viii-no-9`, 34
  findings, 20 resolved, 16 published on 7 pages); the ten issues of June 2025
  to January 2026 (`archive-page-2`, 22 findings, 19 resolved, 9 published on 7
  pages, and ten declined because the earlier pass had already read the January
  2026 issue); and the ten of January to May 2025 (`archive-page-3`, 36
  findings, 32 resolved, 31 published on 26 pages). **What remains is 2024 and earlier, 18
  issues on the last two archive pages** — and the February 2025 issue names
  three of them as substantial: March/April 2024 on Denis Kearney of the
  Workingman's Party, who lived on the stretch of Ord Street that is now the
  Saturn Street Stairway; June 2024 on the grocery at 4499 17th Street and Raisa
  Gorbachev's visit to it; and August 2024 on Ruth Asawa's Saturn Street
  residence. Take those first.

- **Verified:** 2026-09-03 (twenty more issues read in full, January 2025 through
  January 2026, into `archive-page-2.json` and `archive-page-3.json`)
