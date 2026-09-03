# Corbett Heights — neighborhood guidance

Applies to everything under `san-francisco/corbett-heights/`, in addition to
the root `AGENTS.md`.

## Scope

Corbett Heights is the hillside neighborhood around Corbett Avenue, between
Market Street and Twin Peaks, north-west of the Castro. Its streets include
Corbett Avenue, Ord, Hattie, Danvers, Mars, Romain, Levant, Museum Way and
the upper reaches of Clayton and Ashbury.

**It is filed separately from the Castro** even though the city's addressing
data labels both `Castro/Upper Market`. Local sources — the Corbett Heights
Neighbors association and Michael Corbett's 2017 *Corbett Heights: San
Francisco, An Historic Context Statement* — treat it as a distinct
neighborhood with its own subdivisions and development history, and its
streets don't overlap the Castro tree.

- The `.sub` locality line is `Corbett Heights · San Francisco, CA <zip>`.
- If a source calls a Corbett Heights address "Castro/Upper Market," that's
  the city's analysis-neighborhood label, not a reason to refile the page.

## Presenting history from newsletters and context statements

The sources themselves — the Corbett Heights Neighbors newsletter archive and
the 2017 Context Statement — are cataloged in the research module:
[corbett-heights-neighbors](../../research/sources/corbett-heights-neighbors.md)
and
[sf-context-statements](../../research/sources/sf-context-statements.md). Go
there for access notes, coverage and the cautions learned so far; what follows
is how to put what they say onto a page.

Local history writing is a rich source, but it is prose written by someone
else.
Two hard rules when using it:

- **Extract facts; never paraphrase the source's prose.** A dated event
  becomes a `.vtl` timeline item; a discrete fact (contractor, architect,
  build cost, first owner) becomes a `.speclist` row or a stat tile; a
  category (style, subdivision) becomes a tag. Do not reproduce the source's
  sentences or their structure — that reads as an article and risks copying
  someone else's expression. Facts are not copyrightable; wording is.
- **Never name the newsletter in the page body.** "The newsletter says…" is
  meaningless to a reader with no context for it. The citation goes in the
  **Sources footer only**, naming the specific issue (title, volume, number,
  date) and linking it, and repeating any original source the newsletter
  itself names (a permit date, a census year, a dated newspaper item).

## Orientation (context, not citable facts)

Verify before asserting any of this about a specific building.

- The land was subdivided in stages. The **McKee Subdivision** (forty
  numbered lots) and the **Park Lane Tract** (from 1885) both recur in the
  record. McKee's central street, Clara, was renamed **Ord** in 1909; Hattie
  Street was named for his daughter.
- **Street numbers changed in 1909**, and some streets were renamed. An
  address given in a pre-1909 source often does not correspond to today's
  number — 1200 Ashbury became 1200 Clayton, 110 Clara became 110 Ord. Always
  check today's number against the EAS dataset before creating a page.
- Much of the housing is early-20th-century, with post-war infill on the
  upper slopes.

## The assessor's year built disagrees with the photographs — say so

The neighborhood's history writing dates buildings from photographs, and the
assessor's `year_property_built` frequently contradicts them. Both are on the
record; **neither gets quietly dropped.** Put the assessor's date in the
`Built …` tag (it is the structured field the rest of the page is built from),
put the photograph in the timeline, and name the disagreement plainly in the
`.unknowns` block. Do not average them, pick a favourite, or write "about".
Worked examples in this tree:

| Page | Assessor | Photograph |
|---|---|---|
| 46–48 Mars | 1903 | standing c. 1895 |
| 52 Mars, 56 Mars | 1900 | standing c. 1895 |
| 328 Corbett | 1908 | standing April 1906 |
| 349 Corbett | 1900 | under construction 1909 |

Round years (1900, 1890) in the assessor roll are placeholders as often as
they are facts — treat them as the weaker evidence, and say in `.unknowns`
that the date has not been checked against a permit.

## Buildings here were moved

A construction date does not always belong to the site. **11–23 Mars Street was
moved to Mars from Falcon Street** — the assessor's 1909 is the date it was
built somewhere else, and photographs of about 1921 show its Mars lot still
empty. When a source says a building "moved here from" somewhere, that is a
`Relocated building` tag plus separate timeline entries for the construction
date and the move; never fold them into one "built" claim.

## Historical addresses that no longer exist

The neighborhood's history writing frequently discusses buildings that have
been demolished or addresses that were renumbered out of existence. **Do not
create a page for an address that isn't in the EAS dataset** — record the
history on the surviving building's page or the street hub instead. Two
examples found while seeding:

- **110 Ord Street** — the Cassin cottage. Ord runs 7–91 today; no 110 exists.
- **1200 Clayton Street** — the 1909 Stoddart building was replaced; the
  address is now thirteen condominium parcels built in 1986.
- **Anything on Falcon Street** — Falcon was expunged by the Market Street
  extension. Fred G. Horner's grocery and saloon at **2 Falcon Street** recurs
  in the record; its story belongs on the surviving buildings nearby
  (`danvers-street/56/`, `danvers-street/60/`) and the Danvers Street hub.
- **2 Mars Street** — appears in a 1925 photograph, but no such address exists
  in EAS today; Mars begins at 4. The site is the corner parcel 2654001, which
  the city addresses **4465 17th Street**: the Belle-V Apartments of 1961, whose
  build year on the roll matches the one the newsletter gives. The newsletter
  itself hedges the corner as "2 (?) Mars or 4465 17th".
- **The 3000 block of Market Street was Merritt Street.** Upper Market Street
  was cut through in the 1920s and Merritt was eliminated; the north side of the
  block, 3000 to 3094, carries the numbers that replaced it. Two pairs are
  stated in the record: **2 Merritt is 3000–3002 Market** (the corner at Hattie,
  built 1890) and **4 Merritt is 3004 Market** — except that no 3004 exists in
  EAS, which runs 3000, 3006, 3008, 3012, so that one resolves to nothing.

## `building_history` is on hand-written pages only

Several pages in this tree carry a `building_history` object instead of
`historical_record` — 4, 11, 33, 46, 52, 56, 64 and 75 Mars Street. **The
renderer does not know that key.** Those pages are in
`scripts/render-backlog.txt` with hand-written HTML, which is the only reason
their events appear at all. Writing `building_history` onto any other page puts
the fact in `data.json` and nowhere a reader can see it, and `validate.py` will
not say so. A dated fact on a rendered page goes in `historical_record`.

## Contributed memoirs: take the building, leave the people

Several issues are first-person accounts by living residents (the Shiloh's Way
piece in January, the Corbett Avenue childhood memoir in July). They are good
sources for building facts — a contractor's name, a stair, a rebuild — and are
**not** licence to name the writer, their family, or who lives where. Attribute
them in the footer as an account published in the issue, not by name. Deceased
figures already published with dates (first owners, builders, nineteenth-century
grocers) may be named, as elsewhere.
