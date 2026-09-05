---
name: ui
description: Implement UI for a feature directly in this codebase's HTML and shared/site.css, applying the repo's distilled design rules without a Paper design process. Invoked as /ui <what to build>. Use when the task is to build, adjust or fix visible UI in the site and the design is not in question — a new block, a panel tweak, a layout fix, matching an existing module. Optimizes for speed and consistency with existing UI. Not for exploring a design, generating options, or mocking a module; that is /design.
---

# UI — the fast path

Implement the UI, in the codebase, now. No Paper, no exploration, no options, no
multi-pass refinement. The goal is speed and **consistency with the UI that
already exists**.

## Read exactly this

1. [design/RULES-OF-THUMB.md](../../../design/RULES-OF-THUMB.md) — the distilled
   design rules.
2. [design/IMPLEMENTATION.md](../../../design/IMPLEMENTATION.md) — tokens, type,
   rem→px, metrics, icons.
3. [shared/AGENTS.md](../../../shared/AGENTS.md) — the page contract and the
   map from `data.json` key to block.
4. [shared/BLOCKS.md](../../../shared/BLOCKS.md) — the block whose markup you
   are about to touch. One block, not the file.

Do **not** read the rest of `design/`. The principles, conventions, tool quirks
and meta notes are the `/design` loop's material; reading them here is how a
fast path stops being fast.

Then look at the nearest existing module in
[`shared/site.css`](../../../shared/site.css) and match it. Reuse a block before
adding one.

## Rules that bind here

- `shared/site.css` is the design system and the source of truth. New classes go
  in it, scoped to the module — never inline styles on a page, never a second
  stylesheet.
- `index.html` on an address page is generated. Change the generator in
  [`scripts/seed_pages.py`](../../../scripts/seed_pages.py), then re-render.
- Run `python3 scripts/validate.py` before you finish.
- The root [AGENTS.md](../../../AGENTS.md) binds without exception.

## Strictly read-only against the design module

`/ui` **never writes** to PRINCIPLES.md, CONVENTIONS.md, PAPER.md,
IMPLEMENTATION.md, META.md or RULES-OF-THUMB.md. It does not learn, promote,
distil, or correct. If something in those files looks wrong, say so in your
reply and leave the file alone — `/design` owns them.

The one exception is the gap log.

## The gap log

When the rules of thumb and the implementation file **don't cover a case and you
have to guess**, append one line to
[design/GAPS.md](../../../design/GAPS.md):

```
- `YYYY-MM-DD` **What was being built** — what wasn't covered; what was guessed.
```

- These are **observations about missing guidance, not learnings.** No
  confidence level. They are never promoted into principles, and nothing —
  including a later `/ui` run — treats them as design advice.
- **Deduplicate.** If the gap is already logged, merge into that line and note
  that it recurred. Keep the log scannable; it is read by a human and by
  `/design` at session start.
- Log the gap, then get on with the implementation. Do not stop to fix the
  module.

## Stop when it's built

Report what you changed and where. No options, no critique of the design, no
follow-up passes unless asked.
