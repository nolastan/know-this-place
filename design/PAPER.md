# Tool quirks — paper.design

Facts about the tool, isolated here so a different tool could replace this file
without touching anything else. No design judgement lives here, and no facts
about this codebase — those are [PRINCIPLES.md](PRINCIPLES.md) and
[CONVENTIONS.md](CONVENTIONS.md).

## Order of operations

```
get_guide({topic: "paper-mcp-instructions"})
  → get_basic_info
  → get_font_family_info
  → create_tokens
  → create_artboard
  → small write_html calls, one visual group each
  → screenshot and critique
  → finish_working_on_nodes
```

`get_font_family_info` before the first typographic style **each session** is a
required step, not a formality.

## Tokens and dark variants

**Paper does not scope CSS custom properties per node.** Setting a token like
`--paper` on an artboard via `update_styles` is accepted silently and changes
nothing.

A dark variant therefore needs a **second token set** plus a rebind of every
coloured node by role — background, border, text colour, SVG `stroke`. Batch
those into a handful of `update_styles` calls **grouped by role**, not one call
per node.

## Variants

**`duplicate_nodes` returns a `descendantIdMap`.** That map is the whole variant
workflow:

1. Build one specimen completely.
2. `duplicate_nodes` once per variant.
3. `set_text_content` the values through the map.
4. `delete_nodes` for the rows a variant doesn't render.

**Never re-write HTML per variant.**

## `write_html` limits

- **No `margin`, no `display: grid`, no tables.** Flex, padding and gap only.
- Right-alignment (`margin-left: auto`) becomes `flexGrow: 1; textAlign: right`.
- An icon becomes a **fixed slot with `flexShrink: 0`**. That fixed slot is what
  keeps the icon / key / value lanes aligned down a column of rows whose content
  lengths differ.
- **Paper wants px.** Convert before writing — the rem table is in
  [IMPLEMENTATION.md](IMPLEMENTATION.md).

## No rich text

An inline `<span style="color: ...">` inside a paragraph is **silently
flattened** to the parent's colour. No error, no emphasis. A phrase that needs a
different weight or colour has to be its own text node, which means breaking the
sentence into a flex row — usually not worth it. Write the emphasis into the
wording instead.

## Screenshots

**A node-level `get_screenshot` renders on transparent, which the viewer shows
as black.** Dark text on a panel will look broken in that shot. Judge colour and
contrast from an **artboard-level** screenshot only.

## Finishing

- Set the artboard to `height: "fit-content"` once the content is in.
- Call `finish_working_on_nodes` at the end.

Both are easy to forget.
