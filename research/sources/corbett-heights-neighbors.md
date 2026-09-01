# corbett-heights-neighbors — Local history research (secondary)

> **Research dossier.** Rules: [../AGENTS.md](../AGENTS.md) · register:
> [../SOURCES.md](../SOURCES.md) · cited on pages by the source id `corbett-heights-neighbors`.
>
> - **Kind:** newsletter archive · **Tier:** secondary · **Status:** open
> - **Search-invisibility:** high — see the register for what that rates.
> - **Coverage:** Page 1 of 5 combed through September 2026; pages 2–5 (38 issues) untouched.
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
  - **A worked 1909 renumbering pair:** 77 Clara Avenue is today's **81 Ord
    Street** (August 2026 issue), alongside the 110 Clara → 110 Ord and
    1200 Ashbury → 1200 Clayton pairs already in
    `san-francisco/corbett-heights/AGENTS.md`.
  - **An issue can disagree with itself in passing.** The August 2026 piece
    dates 99 Ord Street to 1932 twice, with a day-precise completion, and
    writes "1937" once in a sentence about the lot's dimensions. Take the
    date the article argues for and record the slip in the finding rather
    than on the page.
- **Coverage so far:** the archive holds 50 issues across 5 pages. All twelve
  issues on **page 1** (Dec 2025 – Sep 2026) have now been combed; pages 2–5
  (38 issues) are untouched. The August and September 2026 issues were read
  into `findings/corbett-heights-neighbors/vol-viii-no-8.json` and
  `vol-viii-no-9.json` — 34 findings, 20 resolved, 16 published across 7 pages.
  Page 1 still holds unwritten material on Hattie Street and upper Clayton —
  see issue #3.
- **Verified:** 2026-09-01 (page 1 of the archive, Dec 2025 – Sep 2026; the
  August and September 2026 issues read in full and published)
