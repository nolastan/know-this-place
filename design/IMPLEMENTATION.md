# Front-end implementation

A translation table from a design decision to this stack, and nothing else. No
principles, no reasoning, no taste. If a line here would still make sense in a
different codebase, it is in the wrong file — move it to
[PRINCIPLES.md](PRINCIPLES.md).

Read by `/design` when a board goes to handoff, and by `/ui` when writing code.
Every value below is a reading of [`shared/site.css`](../shared/site.css), which
is the source. When they disagree, the stylesheet is right — fix this file.

## Tokens

There is **one** token set. The dark values are the same custom properties
redefined inside `@media (prefers-color-scheme: dark)`, not a second set of
names.

| Role | Token | Light | Dark |
|---|---|---|---|
| Ground | `--paper` | `#fbf9f4` | `#191816` |
| Surface | `--panel` | `#fffdf8` | `#201e1b` |
| Body text | `--ink` | `#1f1d1a` | `#e8e4dc` |
| Keys, titles, icons | `--muted` | `#6b6560` | `#9b948b` |
| Hairline | `--rule` | `#e4dfd4` | `#35312b` |
| Note surface | `--note-bg` | `#f2ede2` | `#232019` |
| Accent | `--accent` | `#8a3b2a` | `#d98b6f` |
| Data — warm | `--warm` | `#8a3b2a` | `#c2694a` |
| Data — cool | `--cool` | `#1568a6` | `#3d8fc9` |
| Data — warm tint | `--warm-soft` | `#efdcd3` | `#3a2a23` |
| Data — cool tint | `--cool-soft` | `#d8e5f2` | `#1e2c3a` |
| Status ok | `--ok` / `--ok-bg` | `#2f7d32` / `#e4efe2` | `#5cba63` / `#1e2a1d` |
| Status warn | `--warn` / `--warn-bg` | `#9a6400` / `#f3ebd8` | `#d0a24a` / `#2a2416` |
| Cost tiers | `--cost-lo` / `-mid` / `-hi` | `#bf8a5e` / `#b5601f` / `#8a3b2a` | `#8f6f52` / `#c07a45` / `#e0946f` |

Paper needs a second token set per scheme — see [PAPER.md](PAPER.md).

## Type

| `site.css` | Stack | In Paper |
|---|---|---|
| `--serif` | `ui-serif, Georgia, "Times New Roman", serif` | System Serif |
| `--sans` | `ui-sans-serif, system-ui, -apple-system, "Segoe UI", sans-serif` | System Sans-Serif |

## rem → px at a 16px root

Paper wants px; the stylesheet is in rem. Exact, then rounded as drawn.

| `site.css` | px | Rounded | Where |
|---|---|---|---|
| `0.3rem` | 4.8 | 5 | `.district-dateline` top margin |
| `0.5rem` | 8 | 8 | `.standing` gap |
| `0.55rem` | 8.8 | 9 | `.speclist` gap |
| `0.6rem` | 9.6 | 10 | `.spec` gap |
| `0.62rem` | 9.92 | 10 | `.standing li` gap |
| `0.69rem` | 11.04 | 11 | `.district-kind` (eyebrow) |
| `0.8rem` | 12.8 | 13 | `.panel > h3` bottom margin |
| `0.82rem` | 13.12 | 13 | `.panel > h3`, `.tag` |
| `0.88rem` | 14.08 | 14 | `.spec`, `.district-also` |
| `0.9rem` | 14.4 | 14 | `.district-also` top margin |
| `0.94rem` | 15.04 | 15 | `.standing`, `.district-dateline` |
| `0.95rem` | 15.2 | 15 | `.spec .ic` |
| `1.05rem` | 16.8 | 17 | `.standing .ic` |
| `1.1rem 1.2rem` | 17.6 / 19.2 | 18 / 19 | `.panel` padding |
| `1.35rem` | 21.6 | 22 | `.standing` top margin |
| `1.56rem` | 24.96 | 25 | `.panel-district > h3` |
| `0.06em` | — | — | `.panel > h3` tracking — keep in em |
| `0.12em` | — | — | `.district-kind` tracking — keep in em |

## Metrics

| Value | Derivation |
|---|---|
| Page frame | `--wide: 62rem` = 992px |
| Frame padding | `1.25rem` = 20px each side → 952px of content |
| `.cols` | `1.5fr 1fr`, `gap: 2rem` (32px) |
| Main column | `(952 − 32) × 1.5 / 2.5` = **552px** |
| **Aside / module width** | `(952 − 32) / 2.5` = **368px** |
| Prose measure | `--measure: 42rem` = 672px |
| Corner | `--radius: 8px` |
| Column collapse | `max-width: 720px` → `.cols` becomes one column |

Existing specimen sheets are drawn at a round **360px**. Fine for a specimen,
wrong for handoff — **quote 368** for measurements.

## Icons

`site.css` carries the set as CSS masks: `<span class="ic ic-name"></span>`,
sized `1em × 1em`, painted with `background-color: currentColor`,
`vertical-align: -0.14em`. `.ic-lg` is `1.4em`.

Redraw for Paper as inline SVG:

- `viewBox="0 0 24 24"`, `fill="none"`, same paths — copy them out of the `--i`
  data URI in `site.css` rather than redrawing by eye.
- `stroke-width="2"`, except `ic-check` at `2.5`.
- `stroke-linecap="round"` throughout; `stroke-linejoin="round"` on every icon
  with a join (`ic-eligible` and `ic-none` declare the cap only).
- Stroke colour is a bound value, not `currentColor` — Paper rebinds it by role
  along with every other coloured node.

Set as of this writing: `ic-calendar`, `ic-home`, `ic-layers`, `ic-plan`,
`ic-lot`, `ic-value`, `ic-permit`, `ic-pin`, `ic-clock`, `ic-help`, `ic-link`,
`ic-check`, `ic-eligible`, `ic-none`, `ic-ruler`.

## Blocks

The HTML each block expects is specified in
[`shared/AGENTS.md`](../shared/AGENTS.md) — that file is the contract, this one
is only the measurements. New classes go in `site.css`, never in a page.
