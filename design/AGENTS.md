# Mocking site modules in Paper

This directory is for design work *about* the site, not part of the site. The
canonical design system is [`shared/site.css`](../shared/site.css); a Paper
file is a mirror of it, never a source for it. Nothing here is served, linked,
or included in `sitemap.xml`.

**Direction of truth is one-way: code → design.** When a mock and the
stylesheet disagree, the stylesheet is right and the mock is stale. Do not
"improve" a module in Paper and then port the improvement back without a human
asking for that — see ground rule 5 in the root [AGENTS.md](../AGENTS.md).

## The file

- Paper file **Know This Place** — `app.paper.design/file/01M01MQRKCPHMF7DXZPF3D032H`
- One page per module. Page **Historic District** holds three artboards: a
  light and a dark specimen sheet for the district panel from the address-page
  aside, and a layout study comparing two redesign directions.
- The two specimen boards do **not** stay in sync. A change to one is a change
  to one.

**Build dark first.** Stan works in dark mode; a light-only board is a board he
has to squint at. Compose new work with the `--color-dark-*` tokens from the
outset and derive the light board from it if one is wanted, rather than the
other way round. The rebind is mechanical either direction, but the board you
are actually judging should be the dark one.

## Before you mock a module

1. **Read the generator, not a sample page.** One address page shows one
   shape. The full key set, the row order, the icon per row and the label
   rewrites all live in the generator function in
   [`scripts/seed_pages.py`](../scripts/seed_pages.py) — for the district
   panel, `district_panel_html`. Reading `459/index.html` alone would have
   missed the repeatable `Also within` row entirely, because no page in Haight
   Ashbury has one.
2. **Scan every `data.json` for the value domain.** A one-line Python glob over
   `san-francisco/**/data.json` gives you the real set of values each key
   takes, and how many pages take each. That is what makes a specimen sheet
   worth having: the variants are the ones that exist, with counts, not the
   ones you imagined.
3. **Watch for labels the generator rewrites.** `district_panel_html` prints
   `None` when the source says `No local landmark protection`, and the row is
   called *District protection*, not *Local landmark protection*, because it
   describes the district and not the building. Mock what the panel prints.

## Content rules for a mock

Same standard as a page: **every specimen is a real record, cited by path.**
Caption each one with the page it came from (`/haight-ashbury/carmelita-street/50/`)
so a reader can check it.

A composite — one panel showing every key at once — is legitimate and useful,
but it is not a real record. Say so in its caption, and say which page it is
based on. In the Historic District sheet the composite carries two `Also
within` rows to show the generator's loop; no live page has two, and the
annotation column says that outright rather than implying a shape the data
doesn't have.

Counts belong in the mock (they are the reason to pick those five variants),
and counts go stale. Regenerate them from `data.json` rather than copying them
forward from an older board.

## Porting `shared/site.css` into Paper

Do not invent a palette. The stylesheet's `:root` is the palette; its
`prefers-color-scheme: dark` block is the dark palette. Both are already token
sets in the file:

| Role | Light token | `site.css` | Dark token | `site.css` |
|---|---|---|---|---|
| Ground | `--color-paper` | `#fbf9f4` | `--color-dark-paper` | `#191816` |
| Surface | `--color-panel` | `#fffdf8` | `--color-dark-panel` | `#201e1b` |
| Body text | `--color-ink` | `#1f1d1a` | `--color-dark-ink` | `#e8e4dc` |
| Keys, titles, icons | `--color-muted` | `#6b6560` | `--color-dark-muted` | `#9b948b` |
| Hairline | `--color-rule` | `#e4dfd4` | `--color-dark-rule` | `#35312b` |
| Note surface | `--color-note-bg` | `#f2ede2` | `--color-dark-note-bg` | `#232019` |
| Accent | `--color-accent` | `#8a3b2a` | `--color-dark-accent` | `#d98b6f` |

Type: `--serif` maps to Paper's **System Serif**, `--sans` to **System
Sans-Serif**. Call `get_font_family_info` before the first typographic style
in a session regardless — it is a required step, not a formality.

Paper wants px. The stylesheet is in rem at a 16px root:

| `site.css` | px | Where |
|---|---|---|
| `0.82rem` | 14px | `.panel > h3` |
| `0.88rem` | 15px | `.spec` |
| `0.95rem` | 16px | `.spec .ic` |
| `0.55rem` | 9px | `.speclist` gap |
| `0.6rem` | 10px | `.spec` gap |
| `1.1rem 1.2rem` | 18px 19px | `.panel` padding |
| `0.06em` | — | `.panel > h3` tracking, keep in em |

**Real module width: 368px.** `main` is `62rem` (992px) minus `1.25rem`
padding each side = 952px; `.cols` is `1.5fr 1fr` with a `2rem` gap, so the
aside is `(952 − 32) / 2.5 = 368px`. The current specimen sheets are drawn at a
round **360px** — fine for a specimen, wrong for pixel handoff. If someone asks
for measurements, give them 368.

## Paper mechanics worth knowing before you start

- **Paper does not scope CSS custom properties per node.** Setting
  `--color-paper` on an artboard via `update_styles` is accepted silently and
  changes nothing. A dark variant therefore needs a *second token set* and a
  rebind of every colored node by role — background, border, text color, and
  SVG `stroke`, batched into a handful of `update_styles` calls grouped by
  role, not per node.
- **`duplicate_nodes` returns a `descendantIdMap`.** That map is the whole
  variant workflow: build one specimen completely, duplicate it once per
  variant, `set_text_content` the values, and `delete_nodes` the rows a variant
  doesn't render. Do not re-write HTML per variant.
- **No `margin`, no `display: grid`, no tables in `write_html`.** Flex,
  padding, and gap only. `.spec`'s `margin-left: auto` on the value becomes
  `flexGrow: 1; textAlign: right`, and the icon becomes a fixed 16px slot with
  `flexShrink: 0` — that fixed slot is what keeps the icon/key/value lanes
  aligned down a column of rows with different content lengths.
- **Icons are the CSS-mask set from `site.css` redrawn as inline SVG.** Same
  24-unit viewBox, same paths, `stroke-width: 2` (2.5 for `ic-check`), round
  caps and joins. The panel's five rows use `ic-permit`, `ic-check`, `ic-plan`,
  `ic-calendar`, `ic-pin`, in that order.
- **Paper has no rich text.** An inline `<span style="color: ...">` inside a
  paragraph is silently flattened to the parent's color — you get no error and
  no emphasis. If a phrase needs a different weight or color, it has to be its
  own text node, which means breaking the sentence into a flex row. Usually not
  worth it; write the emphasis into the wording instead.
- **A node-level `get_screenshot` renders on transparent, which the viewer
  shows as black.** Dark text on a panel will look broken in that shot. Judge
  color and contrast from an artboard-level screenshot only.
- **Set the artboard to `height: "fit-content"` when the content is in**, and
  call `finish_working_on_nodes` at the end. Both are easy to forget.

## Order of operations

`get_guide({topic: "paper-mcp-instructions"})` → `get_basic_info` →
`get_font_family_info` → `create_tokens` → `create_artboard` → build in small
`write_html` calls, one visual group each → screenshot and critique →
`finish_working_on_nodes`.

## What the redesign settled

The district panel was rebuilt over five passes and is now in the codebase
(`.panel-district` / `.standing` — see [shared/AGENTS.md](../shared/AGENTS.md)).
The reasoning is worth keeping, because most of it generalises to the other
panels, which still carry the flaws this one shed.

**Rank the facts out loud before touching the type.** The whole redesign turned
on one question from Stan — what is most interesting here? — answered in order:
that it is in a historic district; that it is eligible for the California
Register; when it was significant; and last, the None and Not-listed values.
The old panel had that order exactly inverted: the district's name was set in
label type while four undifferentiated rows carried the paperwork. Ask for the
ranking first; the layout falls out of it.

**Identity versus standing is the test for what goes in a list.** A register is
something the district is on or off, so it is standing and belongs in the list.
A period of significance is when the district mattered — it qualifies the name,
so it sits with the name as a dateline. A designation is what the district *is*,
so it moved to the eyebrow. Applying that test twice took two rows out of the
panel and dissolved a redundancy that wording could only have managed.

**A glyph that repeats is worth more than a glyph that varies.** The old set
gave every row its own icon, so the icons distinguished rows their own labels
already distinguished — and one of them put a checkmark beside "Not listed".
The icon now carries the *step on a scale* (`ic-check` listed, `ic-eligible`
eligible, `ic-none` neither) and the sentence carries the subject. Negatives all
take the same mark: repeated, it stops reading as a glyph and the lower half of
the list reads as one fact.

**Emphasis is a third signal too.** The designated eyebrow briefly took ink
while the undesignated one stayed muted. It sits directly above a 25px serif
headline, so the one line that changed colour competed with the thing the panel
exists to deliver — and the eyebrow already reports the designation in words.
It is muted in every state now. The pattern repeats through this whole exercise:
each time a distinction was given a second or third channel, the extra channel
cost more than it carried.

**Spend no accent unless the panel is the place to spend it.** Stan picked the
one specimen that happened to have no accent colour, which was the answer. The
accent was marking the second most interesting fact directly beneath the most
interesting one, so it pulled the eye off the headline. Ink against muted was
already carrying affirmative against negative; the accent was a third signal
for a distinction two signals had covered. The tier gap went the same way a
pass later — colour and repetition separate the halves without it.

**Count the type styles.** The third pass ran five (11/13/15/16/25px across
three weights). It ships with three: eyebrow, headline, and one style for every
fact line. Rank is carried by order, colour, position and the icon lane —
nothing is carried by size except the headline itself.

**Plain language first, citation demoted.** "Article 10" means nothing to a
reader. The eyebrow says `ARTICLE 10 CITY LANDMARK DISTRICT`, with the number in
line with the label as a reference rather than as information.

## Checks this exercise earned

Run these against the data before committing to a rule that reads it:

- **Does the rule hold for every value?** The eyebrow lifts a type phrase out of
  the district name; a scan of all 113 names found 110 that end in one, three
  that don't, and — the check that mattered — no conservation-named district
  that isn't Article 11, which is what makes the eyebrow safe to trust.
- **What does the longest value do?** "Showplace Square Heavy Timber and
  Steel-frame Brick Warehouse and Factory Historic District" is the ceiling at
  four headline lines. Trimming the suffix did *not* save a line, contrary to
  what the mock's notes first claimed — long names are long in their proper
  part.
- **What are the junk values?** The survey stores a literal `N/A` for undated
  districts. A design that renders the field verbatim produces "Significant
  N/A". Look for these before drawing, not after.
- **Which records are a different shape?** Sixteen hand-authored pages store the
  district under `california_register` / `article_10` rather than the seeder's
  `*_status` keys, and eight more carry a `historic_district` block whose only
  job is to record that there is no district. Both had to be handled in code
  before a migration could touch them.

## Porting a Paper design back into the site

- **Scope new classes to the module.** `.spec` / `.speclist` are shared with
  *At a glance* and the open-space panels. The district redesign added
  `.panel-district` and `.standing` rather than changing them, so one module
  could move without dragging three others with it.
- **`index.html` is regenerated, never hand-edited** — the page contract holds
  during a redesign too. Change the generator in `scripts/seed_pages.py` first,
  then re-render the affected block on every existing page from its
  `data.json`.
- **Migrations are one-off scripts, not repo tooling.** Ground rule 6 caps the
  repo at its four stdlib scripts. Write the migration in the scratchpad, run
  it, and commit only the HTML it produced.
- **Expect a tail of pages the migration cannot touch.** The district migration
  rewrote 2,471 pages and left 8, all of them hand-authored pages whose district
  facts are mixed into a differently-shaped panel. Report the tail; do not force
  a regex onto pages whose markup was written by a person.
- **Verify with computed styles, not screenshots.** The Browser pane returned
  blank frames for these pages; `getComputedStyle` on the real page confirmed
  the panel renders at 368px with the right sizes and colours in both schemes.
  Prefer the measurement either way — it is the check that would catch a
  specificity bug.
- **Hard-reload before believing a CSS result.** A stale `site.css` made the
  first verification pass look like a specificity failure when nothing was
  wrong.
