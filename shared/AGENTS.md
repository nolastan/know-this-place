# The page contract & design system

How to turn `index.md` + `data.json` into `index.html`. There is no template
engine and no build step: **you author the HTML directly.**

The goal is a **designed data page, not an article.** A good page looks like a
purpose-built dashboard for one building — stat tiles, a visual timeline,
small charts, icons, and horizontal layout — with prose reserved for genuine
narrative (history, an unusual story). If a section could be a component
instead of a paragraph, make it a component.

**You compose; you do not invent components.** `shared/site.css` is a small
library of reusable blocks (below), the way a component kit like Tremor works —
except implemented as plain CSS classes so the site stays static, dependency-
free, and JS-free. Every page is bespoke by *composing these blocks
differently* to fit the data it actually has — not by writing new CSS. Adding
or changing a component is a human decision (see "Extending the system").

## Hard rules

- **The library is the only styling.** `/shared/site.css`, no inline `<style>`,
  no per-page CSS, no `style` attributes **except** the documented data hooks
  that pass a number into a chart (`style="--v:86.7"`, `style="width:70%"`).
- **JavaScript is enhancement-only, and lives only in `/shared/site.js`.** No
  inline `<script>` and no per-page scripts (the sole exception is the JSON-LD
  data block). **Every page must be complete and readable with its HTML alone**
  — the custom elements only *add behavior* to content that is already in the
  markup. This is not stylistic: static, crawlable pages are the whole SEO
  strategy. If JS would be the only way something renders, it doesn't belong.
  (`validate.py` rejects stray scripts.)
- **No external resources** except the Street View iframe (loaded on click by
  the enhancement layer, never on page load).
- Use the pre-validated data hues as documented — never introduce new colors.
- **Text never wears a data color.** Bars/segments carry the hue; labels and
  values use normal ink. (Identity comes from the swatch beside the text.)

## Required skeleton

UPPERCASE = from this page's `data.json` / `shared/site-config.json`.

```html
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>ADDRESS — Know This Place</title>
  <meta name="description" content="PAGE-SPECIFIC ONE- OR TWO-SENTENCE SUMMARY">
  <link rel="canonical" href="SITE_URL + PATH">
  <link rel="stylesheet" href="/shared/site.css">
  <script type="module" src="/shared/site.js"></script>   <!-- enhancement layer -->
  <script type="application/ld+json"> { … "@type":"Place" … } </script>  <!-- see below -->
</head>
<body>
<header class="site-header">
  <a class="wordmark" href="/">Know This Place</a>
  <nav class="breadcrumb" aria-label="Breadcrumb"> … crumbs … <span aria-current="page">744</span></nav>
</header>
<main> … COMPOSE BLOCKS … </main>
<footer class="site-footer"> … sources · feedback-cta · colophon … </footer>
</body>
</html>
```

JSON-LD (`Place` with `PostalAddress` + `GeoCoordinates`), the `<footer>`
sources/feedback/colophon, and the **FEEDBACK_URL** are unchanged — copy them
from any existing address page (e.g. `castro-street/744/index.html`).
`validate.py` enforces canonical, description, breadcrumb, footer, JSON-LD,
and the prefilled feedback link; run it.

## Composing `<main>`: a typical order

Not a template — reorder, drop, or repeat blocks to fit the building. A
history-rich place might open with prose and photos; a plain one leans on the
stat band and timeline. A workable default spine:

1. `.hero` — `<h1>`, `.sub` locality line, `.tags`, and a `.media` slot.
2. `.lead` — one short orienting paragraph. **One.** Not three.
3. `.stats` — the numbers every building has, as tiles (not sentences).
4. `.cols` — main narrative/timeline on the left, `.aside` panels on the right.
5. Prose sections (`.section-head` + `.prose`) only where there's a real story.
6. `.unknowns` — what's missing, feeding the feedback link.

---

## The block library

Copy these patterns; fill in real values. All classes are defined in
`site.css`.

### Hero — `.hero`
Two columns (identity | media), stacks on mobile.
```html
<section class="hero">
  <div>
    <h1>744 Castro Street</h1>
    <p class="sub">Eureka Valley · San Francisco, CA 94114</p>
    <ul class="tags">
      <li class="tag"><span class="ic ic-calendar"></span>Built 1896</li>
      <li class="tag"><span class="ic ic-home"></span>Two-flat Victorian</li>
    </ul>
  </div>
  <!-- media slot: see "Media" -->
</section>
```

### Stat band — `.stats` / `.stat`
The dashboard KPI row: one tile per measurement. Big value in sans, small
label, an icon. Compact big numbers (`$2.67M`, `2,266`); put units in `<small>`.
**Never duplicate a fact that's already a tag or lives in another block.**
Categorical identity (year built, building type, stories, zoning, district)
belongs in the `.tags`; the stat band is for *measurements* not shown there
(building area, lot area, room count). If a number is detailed elsewhere (e.g.
assessed value, which the sidebar chart owns), don't also make it a tile.
```html
<div class="stats">
  <div class="stat"><span class="ic ic-plan"></span><span class="stat-val">2,266<small> sq ft</small></span><span class="stat-label">Building area</span></div>
  <div class="stat"><span class="ic ic-lot"></span><span class="stat-val">3,125<small> sq ft</small></span><span class="stat-label">Lot area</span></div>
  <!-- a few tiles is fine; they reflow automatically -->
</div>
```

### Section header — `.section-head`
Icon + title + trailing hairline. Opens each major section.
```html
<div class="section-head"><span class="ic ic-clock"></span><h2>Permit history</h2></div>
```

### Two-column region — `.cols` + `.aside`
Main content left, stacked side panels right. Stacks under 720px.
```html
<div class="cols">
  <div class="main"> … timeline / narrative … </div>
  <aside class="aside"> … one or more <section class="panel"> … </aside>
</div>
```

### Panel — `.panel`
A titled card for a sidebar chart or fact group. `<h3>` renders as a small
uppercase kicker.
```html
<section class="panel"><h3>Assessed value · 2025 roll</h3> … </section>
```

### Visual timeline — `.vtl`
A rail with dots; each item has a date, description, and a meta row (status
pill, a link to the record, a cost tier). Order reverse-chronological
(newest first) unless another order tells the story better. Add `is-muted` to
an item for expired/withdrawn records.
```html
<ol class="vtl">
  <li class="vtl-item">
    <div class="vtl-date">Aug 2005</div>
    <p class="vtl-desc">Kitchen remodel — cabinets, counter, five windows.</p>
    <div class="vtl-meta">
      <span class="pill pill-ok"><span class="ic ic-check"></span>Complete</span>
      <a href="https://dbiweb02.sfgov.org/dbipts/default.aspx?page=Permit&amp;PermitNumber=200508261366">Permit 200508261366</a>
      <span class="cost" data-tier="3" aria-label="Estimated cost over $25,000"><b>$</b><b>$</b><b>$</b></span>
      <span class="cost-amt">$26,822</span>
    </div>
  </li>
</ol>
```
Link every permit to its DBI record (see DATA-SOURCES.md → sf-building-permits
for the URL pattern). Status pills: `.pill-ok` (complete), `.pill-warn`
(open/issued/in progress), `.pill-muted` (expired/withdrawn). **A pill always
carries an icon + word** — never color alone.

### Cost tier — `.cost` ($ / $$ / $$$)
Communicates a dollar magnitude at a glance *without* a bar (bars read as
progress meters, which money isn't). Three `$` glyphs; `data-tier` colors the
first N in a rising warm hue. Show the exact amount beside it in `.cost-amt`,
and give the element an `aria-label`. Tiers for permit cost:
`$` under $5k · `$$` $5k–$25k · `$$$` over $25k.
```html
<span class="cost" data-tier="2" aria-label="Estimated cost $5,000 to $25,000"><b>$</b><b>$</b><b>$</b></span>
<span class="cost-amt">$12,000</span>
```

### Stacked part-to-whole bar — `.stack` (two categories)
For splitting one total in two (land vs improvement value). Two segments whose
widths are percentages of the total, plus a legend that labels **both** (the
two data hues are only distinguishable-enough with labels present). Wrap it in
`<ktp-figure>` and give each segment a `data-tip` so hover/focus reveals the
exact value (see "Enhancement layer"):
```html
<ktp-figure>
  <div class="stack" role="group" aria-label="Assessed value breakdown">
    <div class="stack-seg seg-cool" style="width:70%" tabindex="0"
         data-tip="Land · $1,870,163 · 70%" aria-label="Land, $1,870,163, 70 percent"></div>
    <div class="stack-seg seg-warm" style="width:30%" tabindex="0"
         data-tip="Improvements · $801,498 · 30%" aria-label="Improvements, $801,498, 30 percent"></div>
  </div>
  <div class="legend">
    <span class="legend-item"><span class="swatch seg-cool"></span><span>Land</span>&nbsp;<b>$1,870,163</b></span>
    <span class="legend-item"><span class="swatch seg-warm"></span><span>Improvements</span>&nbsp;<b>$801,498</b></span>
  </div>
</ktp-figure>
```
`seg-cool` = blue (use for the base/larger share, e.g. land), `seg-warm` =
brick. The legend is the text-truth that survives with no JS; the `data-tip` /
`aria-label` on each segment carries the value for pointer and keyboard.

### Spec list — `.speclist`
Secondary facts that don't merit a stat tile: icon · key · right-aligned value.
```html
<dl class="speclist">
  <div class="spec"><span class="ic ic-lot"></span><span class="spec-k">Zoning</span><span class="spec-v">RH-2</span></div>
</dl>
```

### Media / Street View — `<ktp-streetview>` wrapping `.media`
Always author the **placeholder** below — never a raw iframe. The
`<ktp-streetview>` enhancement handles the rest: when `maps_embed_key` is set
in `site-config.json` it swaps the placeholder for a click-to-load facade and
only contacts Google after a click; when there's no key (or no JS), the
placeholder stands. This means imagery turns on across the whole site the day
the key is set — with no page regeneration.
```html
<ktp-streetview location="LAT,LNG" label="ADDRESS">
  <figure class="media">
    <div class="media-empty"><span class="ic ic-pin"></span><span>LAT, LNG</span>
      <small>Street View appears here once a Google Maps embed key is configured.</small></div>
  </figure>
</ktp-streetview>
```
(A `<figcaption>` is optional — use it for a real photo's credit, not to repeat
facts shown elsewhere like the parcel number.)
Committed `assets/` photos use the same `.media` frame with `<img>` (always
`alt`, `width`, `height`, `loading="lazy"`, and credit + license in the
caption) and need no wrapper. Never commit Street View captures to `assets/`.

### Notes — `.community-note` and `.unknowns`
`.community-note` wraps clearly-attributed unverified contributions (auto-
labeled by CSS). `.unknowns` is the "what we don't know yet" block that leads
into the feedback link:
```html
<div class="unknowns"><span class="ic ic-help"></span>
  <p>Not yet documented: the architect and builder, the early residents.
  <a href="FEEDBACK_URL">Know any of it? Tell us — just describe it in plain words.</a></p>
</div>
```

### Icons — `.ic .ic-NAME`
`<span class="ic ic-calendar"></span>`; sized in `em`, colored by surrounding
text. Available: `ic-calendar` `ic-home` `ic-layers` `ic-plan` `ic-lot`
`ic-value` `ic-permit` `ic-pin` `ic-clock` `ic-help` `ic-link` `ic-check`
`ic-ruler`. `ic-lg` enlarges. **Use only icons in this list.** Need a new one?
That's a `site.css` change — see below.

---

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

---

## Enhancement layer (web components)

`/shared/site.js` defines a few custom elements that add behavior on top of the
markup. **The governing rule: they enhance, never generate.** Author the full
content in the light DOM exactly as if the script didn't exist; the element
just wraps it. A page with JS disabled — or a search crawler — must see
everything. (Content rendered only inside a component would be invisible to
search, which is the opposite of this project's goal.)

Available elements:

- **`<ktp-streetview location="LAT,LNG" label="ADDRESS">`** — wraps the
  `.media` placeholder; see "Media / Street View" above. Click-to-load, keyed
  off `site-config.json`. Fallback = the placeholder you wrote.
- **`<ktp-figure>`** — wraps a chart. Any descendant carrying a `data-tip="…"`
  becomes keyboard-focusable and shows that text as a tooltip on hover/focus.
  Use it for marks whose value isn't already printed beside them (stacked-bar
  segments). The values must still exist in the DOM (legend, `aria-label`);
  the tooltip only surfaces them at the mark.

**Adding or changing an element is a `site.js` PR for a human** — never an
inline `<script>` on a page (`validate.py` rejects stray scripts). Keep the
same law: if a new element were the *only* way some content appears, redesign
it so the content is in the HTML and the element merely enhances it.

## Writing voice (prose only)

See "Writing pages" in the root `AGENTS.md`. In this design, prose is the
exception, not the frame: a short `.lead`, and `.prose` sections only where a
building genuinely has a story. Don't narrate numbers the tiles already show.

**No editorial flourishes.** State facts; don't characterize them or the
record. Cut writerly framing like "its public record is the quiet kind," "the
record is silent on…," "hints at a longer story," "a decade before the
earthquake." The `.unknowns` block just names what isn't documented, plainly
(e.g. "Not yet documented: the architect, the early residents…").

**One new fact = one tag or one spec row, never a new section.** The reflex to
introduce a fact with a `.section-head` and explain it in a paragraph is the
single most common way these pages drift back into being articles. Historic
status is a tag (`Historic status: unevaluated`) plus a `.speclist` row
(`CEQA B — unevaluated`) — not six lines of prose. Reserve `.section-head` for
several related facts or a real narrative, and don't reuse an icon that
already labels another section on the page.

## Extending the system

A new block, icon, chart type, or color = **a `site.css` PR**; a new behavior
or custom element = **a `site.js` PR** — each in its own PR, for a human to
review. Never solve a one-page need with an inline `<style>` or `<script>`:
that fragments the system, the next agent won't reuse it, and (for scripts) it
risks putting content where crawlers can't see it. If a page's data doesn't fit
an existing block, prefer the closest block and note the limitation on the
page's PR.
