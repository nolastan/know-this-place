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
  - **`notable_residents` renders nothing.** The early pages that show a
    resident in a `.speclist` row do it in hand-written HTML that
    `scripts/render-backlog.txt` grandfathers; on any page the renderer owns,
    a claim parked in `notable_residents`, `notable_events` or
    `filming_location` is invisible — the page cites the guide in its footer
    and states no fact from it. That was issue #174. Keep the guide's own
    hedges (`disputed`, a competing address, a figure that disagrees with the
    assessor) in the entry's `description`, not in a key nothing reads.
- **Privacy — the binding constraint.** The root AGENTS.md bars naming or
  alluding to **current** residents, publicly available or not. These guides
  routinely name people who still live at the address, often in the present
  tense ("when he's in town"). **Omit any claim phrased as present or
  ongoing occupancy**, and record the omission in the page's `.unknowns`
  without naming anyone. Only past residency — dated, or stated in the past
  tense about someone who has plainly moved on or died — may be named.
- **Citation label:** name the guide and its title, and link the page.
- **Verified:** 2026-09-05 (re-read whole for issue #174; unchanged since the
  2026-07-23 pass — 26 San Francisco addresses listed, all but one resolve in
  EAS. Every address it names now has its claim on the page, except the two
  where the guide's claim is present-tense occupancy and the omission is
  recorded in `.unknowns` instead.)
