# celebrity-residence-guides — Notable-resident claims (tertiary)

> **Research dossier.** Rules: [../AGENTS.md](../AGENTS.md) · traps:
> [../LESSONS.md](../LESSONS.md) · register:
> [../SOURCES.md](../SOURCES.md) · cited on pages by the source id `celebrity-residence-guides`.
>
> - **Kind:** web guides · **Tier:** tertiary · **Status:** done
> - **Search-invisibility:** low — see the register for what that rates.
> - **Coverage:** The one guide used is exhausted; treat new ones as leads, not finds.
> - **Local corpus:** —
>
> Update this dossier at the end of every pass — the `Verified:` line, the
> coverage note, and anything the pass learned about getting at the source.

- **What:** Tourism and pop-history guides that list addresses where public
  figures lived. Used so far: SF Tourism Tips, "Where Famous People Lived in
  San Francisco" — <https://www.sftourismtips.com/where-famous-people-lived-in-san-francisco.html>.
- **Treat as the weakest tier of source.** These pages rarely cite where
  their own claims come from, and they contradict each other on dates and
  even on which building. That doesn't make them unusable — it makes them
  *attributed* rather than asserted.
- **How to use:**
  - **Attribute in the page body, not just the footer** ("a published guide
    to notable residences records…"), so a reader can see the claim is
    second-hand. This is the opposite of the corbett-heights rule, where the
    underlying research is primary and the newsletter name means nothing to
    a reader.
  - **Carry the source's own hedges and conflicts through.** Where the guide
    flags a claim as disputed, or two addresses compete for the same story,
    say so on both pages and cross-link them — never silently pick a winner.
  - **Put the claim where the renderer will show it.** A dated claim is one
    `historical_record` entry (`kind: "occupancy"`, or `"event"` for the SLA
    addresses), which lands on the page's one timeline and names the guide in
    the item's meta row — that is the body attribution. An undated one is a
    one-sentence `narrative.lead`. A notable resident never earns a prose
    section.
  - **`notable_residents` renders now — this caution is spent.** It once did
    not: a claim parked there, or in `notable_events` or `filming_location`,
    was invisible on any page the renderer owned, which was issue #174. The
    renderer since grew `residents_panel_html`, so `notable_residents` is a
    panel of `.speclist` rows carrying a name and a period ("Undated" where
    the source gives none), and it is the right home for a dated residency.
    It **skips a name the page's own prose already states**, which is why the
    seventeen older pages that put their resident in a `lead` render no panel.
    `notable_events` and `filming_location` are gone the other way — no page
    carries either and the seeder does not recognise them, so writing one now
    fails the key check rather than rendering nothing. Keep the
    guide's own hedges (`disputed`, a competing address, a figure that
    disagrees with the assessor) in the entry's `description`.
- **Privacy — the binding constraint.** The root AGENTS.md bars naming or
  alluding to **current** residents, publicly available or not. These guides
  routinely name people who still live at the address, often in the present
  tense ("when he's in town"). **Omit any claim phrased as present or
  ongoing occupancy**, and record the omission in the page's `unknowns`
  without naming anyone. Only past residency — dated, or stated in the past
  tense about someone who has plainly moved on or died — may be named.
- **Citation label:** name the guide and its title, and link the page.
- **Verified:** 2026-09-05 (re-read whole for issue #174; unchanged since the
  2026-07-23 pass — 26 San Francisco addresses listed, all but one resolve in
  EAS. Every address it names now has its claim on the page, except the two
  where the guide's claim is present-tense occupancy and the omission is
  recorded in `unknowns` instead.)
- **Findings:** `findings/celebrity-residence-guides/sftourismtips.json`, written
  retroactively under #422. The guide's byline now reads "Updated: March 10,
  2025"; the page is fetched with a browser-like User-Agent and its text is
  saved beside it in the corpus directory.
- **1235 Masonic is the one address that "doesn't resolve", and the reason is
  the condominium rule, not EAS.** The guide says "Masonic Street"; EAS has 1235
  MASONIC AVE in Haight Ashbury, matching the guide's "in The Haight", but on
  parcel 1244004, which is retired. The building is now three condominium
  parcels, 1244042–1244044, one per number of 1233–1237, so it gets no page
  (#228). Nothing recorded that until the rebuild.
- **The guide's number is not always the page's.** 2047 Taylor and 288 Precita
  are on pages filed under 2043 Taylor and 286 Precita, the lowest EAS number on
  each parcel; 131 24th Avenue is carried on the page for 129.
- **Two sidewalk plaques are not buildings.** The guide gives 4550 and 5099
  Mission Street for Jerry Garcia plaques set in the sidewalk; both resolve and
  both are declined as facts about the pavement.
- **Verified:** 2026-09-26 (re-fetched and re-read whole for #422: unchanged in
  substance. 28 numbered addresses, 26 claims on 24 pages, 2 current-resident
  claims recorded only as omissions, 1235 Masonic a condominium unit.)
