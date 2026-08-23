# Codebase conventions for design work

How design work is done **in this repo** specifically. Anything here that would
still be true in a different codebase belongs in
[PRINCIPLES.md](PRINCIPLES.md); anything that is a fact about paper.design
belongs in [PAPER.md](PAPER.md).

Same confidence convention as the principles file: *tentative* until it has held
across sessions.

## Direction of truth

One-way: **code → design.** [`shared/site.css`](../shared/site.css) is the
canonical design system; a Paper file mirrors it and is never a source for it.
When a mock and the stylesheet disagree, the stylesheet is right and the mock is
stale.

Porting an improvement back into the codebase is a thing a human asks for, and
an invocation of `/design` **is** the human asking. The rule still binds an
agent doing other work: nobody "improves" a module in Paper and lands it in
`shared/site.css` on their own initiative. See ground rule 5 in the root
[AGENTS.md](../AGENTS.md), and [AGENTS.md](AGENTS.md) in this directory.

## Before you mock a module

**Read the generator, not a sample page.** One address page shows one shape. The
full key set, the row order, the icon per row and the label rewrites live in the
generator function in [`scripts/seed_pages.py`](../scripts/seed_pages.py) — for
the district panel, `district_panel_html`. Reading a single page's `index.html`
would have missed the repeatable *Also within* row entirely, because no page in
Haight Ashbury has one.

**Scan every `data.json` for the value domain and the counts.** A one-line
Python glob over `san-francisco/**/data.json` gives the real set of values each
key takes and how many pages take each. That is what makes a specimen sheet
worth having: the variants are the ones that exist, with counts, not the ones
you imagined. Do this before choosing specimen variants, not after.

**Watch for labels the generator rewrites.** `district_panel_html` prints `None`
where the source says `No local landmark protection`, and calls the row
*District protection* rather than *Local landmark protection*, because it
describes the district and not the building. Mock what the panel actually
prints.

## Content rules for a mock

Same standard as a page: **every specimen is a real record, cited by path.**
Caption each one with the page it came from
(`/haight-ashbury/carmelita-street/50/`) so a reader can check it.

A composite — one panel showing every key at once — is legitimate and useful,
but it is not a real record. **Label it as one**, and say which page it is based
on. The Historic District composite carries two *Also within* rows to show the
generator's loop; no live page has two, and the annotation column says so
outright rather than implying a shape the data doesn't have.

Counts belong in the mock — they are the reason those five variants were picked
— and **counts go stale**. Regenerate them from `data.json` rather than carrying
them forward from an older board.

## The Paper file

- **Know This Place** — `app.paper.design/file/01M01MQRKCPHMF7DXZPF3D032H`
- One page per module. Page **Historic District** holds three artboards: a light
  and a dark specimen sheet for the district panel from the address-page aside,
  and a layout study comparing two redesign directions.
- **The specimen boards do not stay in sync.** A change to one is a change to
  one. Nothing propagates.

## Porting a design back into the site

**Scope new classes to the module.** `.spec` / `.speclist` are shared with *At a
glance* and the open-space panels. The district redesign added `.panel-district`
and `.standing` rather than changing them, so one module could move without
dragging three others with it.

**`index.html` is regenerated, never hand-edited.** The page contract holds
during a redesign too — change the generator in `scripts/seed_pages.py` first,
then re-render the affected block on every existing page from its `data.json`.

**Migrations are one-off scripts, not repo tooling.** Ground rule 6 caps the
repo at its stdlib scripts. Write the migration in the scratchpad, run it, and
commit only the HTML it produced.

**Expect a tail of pages the migration cannot touch, and report it.** The
district migration rewrote 2,471 pages and left 8, all hand-authored pages whose
district facts are mixed into a differently-shaped panel. Report the tail; do
not force a regex onto markup a person wrote.

**Verify with computed styles, not screenshots.** The Browser pane returned
blank frames for these pages; `getComputedStyle` on the real page confirmed the
panel renders at 368px with the right sizes and colours in both schemes. Prefer
the measurement either way — it is the check that catches a specificity bug.

**Hard-reload before believing a CSS result.** A stale `site.css` made the first
verification pass look like a specificity failure when nothing was wrong.

## What the data checks turned up here

Findings, not rules — these are what
[PRINCIPLES.md → Checks](PRINCIPLES.md#checks-to-run-before-committing-to-a-rule-that-reads-data)
produced in this codebase, kept as worked examples of what to expect. Counts
were current when written; regenerate before quoting them.

- **Every value.** The eyebrow lifts a type phrase out of the district name. A
  scan of all 113 district names found 110 ending in one and three that don't —
  and, the check that mattered, no conservation-named district that isn't
  Article 11, which is what makes the eyebrow safe to trust.
- **The longest value.** "Showplace Square Heavy Timber and Steel-frame Brick
  Warehouse and Factory Historic District" is the ceiling, at four headline
  lines. Trimming the suffix did *not* save a line, contrary to what the mock's
  notes first claimed.
- **Junk values.** The survey stores a literal `N/A` for undated districts. A
  design that renders the field verbatim produces "Significant N/A".
- **Different shapes.** Sixteen hand-authored pages store the district under
  `california_register` / `article_10` rather than the seeder's `*_status` keys,
  and eight more carry a `historic_district` block whose only job is to record
  that there is no district. Both had to be handled in code before a migration
  could touch them.
