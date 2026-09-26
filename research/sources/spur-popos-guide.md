# spur-popos-guide — SPUR, *Secrets of San Francisco* (secondary)

> **Research dossier.** Rules: [../AGENTS.md](../AGENTS.md) · traps:
> [../LESSONS.md](../LESSONS.md) · register:
> [../SOURCES.md](../SOURCES.md) · cited on pages by the source id `spur-popos-guide`.
>
> - **Kind:** PDF field guide · **Tier:** secondary · **Status:** done
> - **Search-invisibility:** medium — see the register for what that rates.
> - **Coverage:** Read in full for the downtown POPOS pages.
> - **Local corpus:** `research/corpora/spur-popos-guide/`
>
> Update this dossier at the end of every pass — the `Verified:` line, the
> coverage note, and anything the pass learned about getting at the source.

- **What:** SPUR's field guide to the downtown POPOS, written from site visits.
  It carries what the city's own inventory doesn't: what a space is actually
  made of, how you get into it, whether the seating has quietly been annexed by
  a restaurant, and a plain quality rating (Excellent / Good / Fair / Poor).
  The best available second opinion on the `sf-popos` rows.
- **Guide:** <https://www.spur.org/sites/default/files/2013-10/popos-guide.pdf>
  (SF Planning publishes its own map and guide at
  <https://sfplanninggis.org/popos/POPOS_and_PublicArt.pdf>, which is the
  better source for entrances and hours.)
- **Cautions:**
  - **Fetch it as a PDF and extract the text** — `WebFetch` returns nothing
    usable for either file. Agents that have got at it used `pdftotext` or
    `pypdf`.
  - **It is dated.** The guide is a 2010s snapshot; hours, furniture and food
    service have changed, and several spaces have been renovated since.
    Prefer `sf-popos` for the facts a page states, and use SPUR for design
    description and for a documented discrepancy.
  - **Its ratings are judgements, not facts.** Never carry "rated Excellent"
    onto a page as if it were a property of the space.
  - It sometimes assigns a space to the wrong address — it places a kinetic
    ring sculpture at 560 Mission that another source gives to 201 Mission.
    Check the address against `sf-popos` before using an entry.
- **Citation label:** "SPUR, *Secrets of San Francisco: A Guide to San
  Francisco's Privately-Owned Public Open Spaces*"
  - **A citation to this guide is not proof the guide says it.** Until 2026-09-26
    the 101 California plaza's designer credit (OJB, with Bohlin Cywinski
    Jackson) cited this guide, which names no designer there and predates that
    renovation; it now cites OJB's own project page, already in the page's
    sources. Only one other entry names a designer — 101 Second Street, by
    Skidmore, Owings & Merrill.
  - **Its year column is the building's year, not the space's.** The layout sets
    a "year built" and rating label beside each entry; they are separate text
    runs, matched to their entry by page column and baseline (pypdf's
    `visitor_text` gives the coordinates). Where it disagrees with `sf-popos`'s
    `established` — 100 First Street, 1988 against 1985 — it gives the tower's
    completion, not the space's approval, so it is not a conflict.
  - **It records spaces the city no longer lists.** 505 Sansome's lobby
    greenhouse and 45 Fremont's south plaza are entries 2 and 29 and have no row
    in DataSF `65ik-7wqd` as queried 2026-09-26. That is the discrepancy this
    guide is for: both pages carry the 2011 entry and an unknowns line.
- **Guide date:** the PDF was created 6 February 2011 (its metadata); the URL's
  2013-10 is the upload folder. Its latest dated space is 2008.
- **Findings:** `findings/spur-popos-guide/popos-guide.json`, all 56 entries,
  written under #422.
- **Verified:** 2026-09-26 (re-fetched and read whole for #422: 56 map entries
  covering 68 spaces. 54 resolve to a page, 53 of them already carrying the
  space from `sf-popos`; Embarcadero Center West and Foundry Square each span
  several parcels and stay unresolved. 3 published: 101 Second's designer credit
  and the two spaces the inventory no longer lists.)
- **Verified:** 2026-08-06
