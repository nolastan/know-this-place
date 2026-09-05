# The page contract

How `data.json` becomes `index.html`. `data.json` is the single source of truth
for an address page — structured facts *and* prose (in its `narrative` field);
there is no `index.md`. Every fact and sentence in the HTML traces back to
`data.json`, so the page can be regenerated from that file alone.

There is no template engine and no request-time rendering: the committed
`index.html` is the whole page, byte for byte what a reader gets. But it is a
**build artifact, and you never author it.** `scripts/seed_pages.py` composes
the blocks from `data.json`, and

```
python3 scripts/seed_pages.py render <a page, street, neighborhood, or city>
```

rewrites the HTML from the data, in place, idempotently. Change a fact, run
that, don't open the file. `validate.py` asserts every page's `index.html` is
exactly what the renderer produces, so a hand edit fails the build.

**So this file is the contract, not a set of instructions to follow by hand.**
It says what a page is made of and which `data.json` key produces each part.
The markup itself — every block, its classes, its worked example — is
[BLOCKS.md](BLOCKS.md); go there to understand a page in front of you or to
change the renderer.

The goal is a **designed data page, not an article.** A good page looks like a
purpose-built dashboard for one building — stat tiles, a visual timeline, small
charts, icons, horizontal layout — with prose reserved for genuine narrative.
`shared/site.css` is a small library of reusable blocks, the way a component
kit like Tremor works, except implemented as plain CSS classes so the site
stays static, dependency-free and JS-free. Every page is bespoke by *composing
those blocks differently* to fit the data it actually has — never by writing
new CSS.

## Hard rules

- **The library is the only styling.** `/shared/site.css`, no inline `<style>`,
  no per-page CSS, no `style` attributes **except** the documented data hooks
  that pass a number into a chart (`style="--v:86.7"`, `style="width:70%"`).
- **JavaScript is enhancement-only, and lives only in `/shared/site.js`.** No
  inline `<script>` and no per-page scripts (the sole exception is the JSON-LD
  data block). **Every page must be complete and readable with its HTML alone**
  — the custom elements only *add behavior* to content already in the markup.
  This is not stylistic: static, crawlable pages are the whole SEO strategy. If
  JS would be the only way something renders, it doesn't belong.
  (`validate.py` rejects stray scripts.)
- **No external resources in a page's markup.** The only three the site loads
  at all are the Street View image, the Mapbox static map, and the analytics
  script — all three requested by `site.js`, never written into a page. Don't
  add a fourth without a human's say-so, and never as a tag in `index.html`.
- **The site's homepage (`/index.html`) is the one exception to the three rules
  above**, by explicit human decision: it is a map, not a content page, so it
  carries its own `<style>`, its own `<script>`, and Mapbox GL JS. `validate.py`
  skips the stray-script check for that one file. **This is not a precedent.**
  Nothing under `san-francisco/` may do the same — a page whose facts render
  only in JS is invisible to search, which is the whole point of the rules.
- Use the pre-validated data hues as documented — never introduce new colors.
- **Text never wears a data color.** Bars and segments carry the hue; labels
  and values use normal ink. (Identity comes from the swatch beside the text.)
- **One `.vtl` per page**, holding every dated entry, oldest first.
  `validate.py` fails a page carrying more than one.
- **Never state a fact twice.** A structured fact renders in exactly one block.
  Categorical identity (building type, stories, zoning, district) belongs in
  `.tags`; the year built is dated, so it opens the `.vtl` instead; the stat
  band is for *measurements* not shown there. If a
  number is detailed elsewhere — assessed value, which the sidebar chart owns —
  it is not also a tile.

## Which key becomes which block

Where a new fact goes. Full markup for each is in [BLOCKS.md](BLOCKS.md).

| `data.json` | renders as | for |
|---|---|---|
| `address`, `coordinates` | `.hero` `<h1>` + `.sub`, `<ktp-map>`, `<ktp-streetview>` | identity and the locator band |
| `parcel`, `historic_status` | `.tags` in the hero | categorical identity — type, stories, zoning, district |
| `parcel.year_built` | the first `.vtl` item | the year the building went up, on the rail with everything else dated |
| `parcel`, `assessment` | `.stats` / `.stat` tiles | measurements: building area, lot area, rooms |
| `assessment` land/improvement split | `.stack` inside `<ktp-figure>` | one total split in two, both parts labeled |
| `permits` | `.vtl` items, each with a `.pill` status and a `.cost` tier | the dated record of work |
| `permit_summary` | one line *below* the `.vtl` | what the timeline left out, and why |
| `historical_record` | `.vtl` items, interleaved by date | dated facts from historical sources and from news |
| secondary scalars (zoning, use) | `.speclist` rows | a detail that doesn't merit a tile |
| `historic_district`, `also_in_districts` | `.panel-district` + `.standing` | the district's own record, not the building's |
| `public_art` | `.section-head` + `.place-list` | 1% art on the parcel — main column |
| `public_open_space` | one `.panel` per space | POPOS — aside |
| `narrative.lead` | `.lead` | one or two sentences, or nothing |
| `narrative.sections[]` | `.section-head` + `.prose` | a genuine story |
| `narrative.community_note` | `.community-note` | labeled, unverified contribution |
| `unknowns` | `.unknowns` | what isn't documented, feeding the feedback link |
| *(none — `shared/nearby.json`)* | `.nearby` | lateral links, generated by `build_link_index.py` |

Nothing else has a block. A fact that fits none of these is a renderer gap, not
a licence to write markup: see "Extending the system".

## Charts: the rules that keep them honest

The data hues in `site.css` (`--warm` brick, `--cool` blue, plus tints) are
**pre-validated** for contrast and colorblind-safety in both light and dark
mode. So:

- **Dollar magnitude** → the `.cost` tier ($ / $$ / $$$), never a bar. Bars
  read as progress/completion, which a cost isn't.
- **A total split in two** → the `.stack` (warm + cool), both parts labeled.
- More than two categories, a different chart type, or a non-currency
  magnitude comparison is **not yet a supported block** — don't fake it with
  inline styles. Present the data as a stat, spec list, cost tier, or timeline
  instead, and flag the gap for a human.
- Every chart gets a text equivalent that survives with no JS: the cost tier
  shows its exact amount; the stack's legend and per-segment `aria-label` carry
  the numbers.

## Enhancement layer (web components)

`/shared/site.js` defines a few custom elements that add behavior on top of the
markup. **The governing rule: they enhance, never generate.** The full content
is in the light DOM exactly as if the script didn't exist; the element just
wraps it. A page with JS disabled — or a search crawler — must see everything.

- **`<ktp-streetview location="LAT,LNG" label="ADDRESS">`** — swaps in a Street
  View still, keyed off `maps_embed_key` in `site-config.json`.
- **`<ktp-map location="LAT,LNG" label="ADDRESS">`** — the same contract for the
  locator band, keyed off `mapbox_token`: one flat image from the Mapbox Static
  Images API, in the basemap matching the reader's color scheme. A static
  image, not Mapbox GL JS — an address page loads no third-party script.
- **`<ktp-figure>`** — wraps a chart. Any descendant carrying `data-tip="…"`
  becomes keyboard-focusable and shows that text on hover/focus. The values
  must still exist in the DOM (legend, `aria-label`); the tooltip only surfaces
  them at the mark.

Each swaps its own placeholder for an image once the matching key is in
`site-config.json`, and leaves it standing when there is no key and when there
is no JS — so imagery turns on across the whole site the day a key is set, with
no page regeneration. `location` must equal `coordinates` in `data.json`.

**Never test or preview the Street View image.** `maps_embed_key` is restricted
to the production domain, so it fails from localhost, from any preview host,
and from `curl` — by design. There is no local check that can pass. The map is
the one exception, and only from one place: `mapbox_token` is URL-restricted to
`knowthis.place` *and* `http://localhost:8517`, so the locator map does render
for a human previewing with `python3 -m http.server 8517`. Any other port, any
other host, and `curl` all fail the restriction and prove nothing.

`site.js` also loads **analytics** (Fathom) on every page, gated on
`fathom_site_id` and on the page being served from the production host. It is
site-wide plumbing: never add a tracking tag to a page, and never build a
component to carry one. The footer holds the Sources citations and the feedback
link — content a crawler must see — so it stays in each page's HTML.

## Writing voice

Prose rules live in one place, [AGENTS.md → Writing
pages](../AGENTS.md#writing-pages) at the repo root, because prose is authored
in `data.json` rather than in markup: `lead` → `.lead`, each `sections` entry →
`.section-head` + `.prose`, `community_note` → `.community-note`. In this
design prose is the exception, not the frame — a short `.lead`, and `.prose`
sections only where a building genuinely has a story. A page that ends up with
no `.lead` at all is correct, not unfinished.

## Extending the system

A new block, icon, chart type, or color = **a `site.css` PR**; a new behavior
or custom element = **a `site.js` PR** — each in its own PR, for a human to
review. Never solve a one-page need with an inline `<style>` or `<script>`:
that fragments the system, the next agent won't reuse it, and (for scripts) it
risks putting content where crawlers can't see it. If a page's data doesn't fit
an existing block, prefer the closest block and note the limitation on the
page's PR.
