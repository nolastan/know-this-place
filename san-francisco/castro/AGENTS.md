# Castro / Eureka Valley — neighborhood guidance

Applies to everything under `san-francisco/castro/`, in addition to the root
`AGENTS.md`.

## Naming — the Castro *is* Eureka Valley

They are one neighborhood with two names, and the city's own datasets
disagree: the addressing and planning data say **Castro/Upper Market**, the
assessor's roll says **Eureka Valley/Dolores Heights**, and everyone says
**the Castro**. A page that shows one name in the breadcrumb and another in
the subtitle reads as though they are two different places.

- The breadcrumb and directory always use **Castro**.
- The `.sub` locality line is always exactly
  `Castro (Eureka Valley) · San Francisco, CA <zip>` — the parenthetical is
  what tells a reader the two names are the same place. Don't drop it, and
  don't substitute a dataset's name for it.
- The explanation lives once, on the neighborhood hub page. Don't repeat it
  on address pages.

## Scope

Eureka Valley, commonly called the Castro: roughly bounded by Market Street
(northeast), Douglass Street and the hillside (west), 22nd Street (south),
and Church Street (east). The authoritative test for whether an address
belongs here is the SF Planning "Analysis Neighborhoods" / neighborhood
boundary data — when in doubt, check, and refine this paragraph once the
boundary dataset is verified.

**Residential addresses first** (root rule). Castro Street's commercial core
(roughly 400–600 Castro) and Market Street storefronts are mostly business
addresses — defer them.

## Orientation (context, not citable facts)

Useful background so pages are written with the right instincts. **Verify
before asserting any of this about a specific building** — cite per-address
sources, not this file.

- Housing stock is heavily Victorian and Edwardian (1880s–1910s). Eureka
  Valley largely escaped the 1906 fire, so pre-quake buildings are common.
- Working-class Irish and Scandinavian neighborhood through the mid-20th
  century; became the center of San Francisco's LGBTQ community in the
  1960s–70s (Harvey Milk's shop and residence at 573–575 Castro Street).
- The Castro Theatre (1922, Timothy Pflueger) anchors the commercial strip.
- Many buildings appear in SF Planning historic resource surveys — check
  historic status for every page (see `sf-planning` in DATA-SOURCES.md).

Good deep-context sources for this neighborhood: OpenSFHistory (Western
Neighborhoods Project), the GLBT Historical Society, Bay Area Reporter
archives, Hoodline's Castro coverage.

## Street slugs

Street type spelled out, official name lowercased: `castro-street`,
`collingwood-street`, `hartford-street`, `noe-street`, `sanchez-street`,
`eureka-street`, `diamond-street`, `douglass-street`, `states-street`,
`caselli-avenue`, and numbered streets as `17th-street` … `22nd-street`.
The EAS dataset is canonical for which streets and numbers exist.

## Hub pages

- `san-francisco/castro/index.*` — the neighborhood page: shared history
  lives HERE (not duplicated across address pages), plus links to street
  indexes.
- Each street directory's `index.*` lists its covered numbers with a
  one-line hook per building.
