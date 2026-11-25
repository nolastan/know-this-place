# corcoran-icon — Corcoran Icon Properties listing and sale posts (tertiary)

> **Research dossier.** Rules: [../AGENTS.md](../AGENTS.md) · traps:
> [../LESSONS.md](../LESSONS.md) · register:
> [../SOURCES.md](../SOURCES.md) · cited on pages by one id per post,
> `corcoran-icon-<YYYY-MM-DD>` (the post's date).
>
> - **Kind:** brokerage web pages · **Tier:** tertiary · **Status:** open
> - **Search-invisibility:** low — see the register for what that rates.
> - **Coverage:** every San Francisco post on the blog to 2026-11-25 (5 of 85 posts); the 1,100 San Francisco property pages measured, not mined.
> - **Local corpus:** `research/corpora/corcoran-icon/` (gitignored; the five posts as fetched)

- **What:** Corcoran Icon Properties, a Bay Area brokerage (a Corcoran
  franchise). Two kinds of page carry San Francisco addresses:
  1. **Blog posts** (`/blog/<slug>`, listed in `sitemap-blog-dpages.xml`): a
     press-release paragraph per listing or sale. 85 posts in all on
     2026-11-25, most of them agent awards and company news; 5 name a San
     Francisco building, about one a month lately. These are written by the
     listing agent with some research behind them: a builder or architect, the
     building's history, an addition, a recent restoration.
  2. **Property pages** (`/property/<address>-<mls id>`, in
     `sitemap-property-dpages--0.xml`): the MLS record for each listing, about
     1,100 in San Francisco. The remarks are marketing copy about kitchens and
     light; the year built is the roll's ("per tax records").
- **Where:** cite the post's own URL. Posts stay up after the sale; property
  pages may not.
- **How to get at it:** plain `curl` with a browser user agent; robots.txt
  disallows only `/api/`, account and search paths. No feed (`/blog/feed` and
  `/blog/rss` 404); the blog sitemap is the complete list. A page is ~330 KB
  of site chrome around a few paragraphs; the post body follows the line
  "Noteworthy Properties" or "Company News".
- **What is actually usable:** the building facts, never the event. A listing
  is not a sale, and a sale is not something this site records from a
  brokerage: no asking or sale price, no "record-breaking", no agents, buyers
  or sellers. Example of the usable kind: "Built in 1910 by Bakewell & Brown,
  the firm behind San Francisco City Hall" (2550 Baker Street, 11 December
  2025).
- **Cautions:**
  - **A brokerage is selling the building.** Its dates and attributions are
    claims, not records. Where the roll or a permit disagrees, state both in
    `unknowns` (naming it "a 2025 sale listing") and pick neither; never
    overwrite a roll year from a listing. 2550 Baker: listing 1910, roll 1907.
    44 Page: listing "three floors added in 1984, six storeys", DBI permit
    8402211 "addn of two floors", roll three storeys.
  - **The year built in a property page is the roll's.** It confirms nothing.
  - **Square footage and storeys are marketing figures** (44 Page: "±35,493
    square feet" against the roll's 36,186). Don't take them.
  - **"Designed by" in property-page remarks is often the interior designer**
    (Ken Fulk at 401 Harrison and 1940 Broadway): an interior is the unit, not
    the building. Take only an architect of the building.
  - A renovation credit with no date is an `architect_note`, not a timeline
    entry; the permits on the page already date the work.
- **People:** agents, buyers, sellers and their quotes are never taken. Firms
  and architects of the building are; so is a developer (Joseph Eichler at
  1027 Duncan). A tenant is never named, even when the post does.
- **Citation label:** the brokerage, the post's headline in quotes, its date.
  Example: Corcoran Icon Properties, “Lowrie MacLean Lists Historic Pacific
  Heights Home at 2550 Baker Street,” 11 December 2025. The page's short
  `label`: "Corcoran Icon Properties, 2550 Baker Street listing, 11 December
  2025".
- **Coverage:** blog: all 85 posts to 2026-11-25 screened by slug and body; the
  five San Francisco property posts read whole (44 Page, 2550 Baker, 752
  Elizabeth, 1027 Duncan, 415 Fillmore). Next: any post after 6 November
  2026 (the newest on 2026-11-25). Property pages: not mined; see Verified.
- **Verified:** 2026-11-25 (first run, moved here from the news module at
  Stan's request: listing posts were declined as news, since the event is a
  price). Read 5 San Francisco posts, found 8 facts, resolved 8 (one held),
  published 6 on 3 pages (44 Page; 2550 Baker and 1027 Duncan seeded), 1
  declined as already on the page. Learned: the posts' value is the
  attribution and alteration history; everything else is price. Property
  pages measured on a sample (see the PR): about 3% of remarks name an
  architect of the building or a former use, mostly recent condominium
  buildings.
