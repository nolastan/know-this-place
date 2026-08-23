# Rules of thumb

**Generated.** Distilled from the layers by `/design`, and regenerated as the
corpus grows. Do not hand-edit — edit the source layer and let the next
regeneration pick it up. A rule with no source in a layer file is a bug in the
distillation.

This is the first thing `/design` reads, so a board can be on screen before the
full corpus is consulted, and the only design file `/ui` reads besides
[IMPLEMENTATION.md](IMPLEMENTATION.md).

*Regenerated: seeded from `design/AGENTS.md` at module creation. Corpus:
PRINCIPLES, CONVENTIONS, PAPER, IMPLEMENTATION.*

## Deciding

1. Rank the facts out loud first — "what is most interesting here?" — and let
   the layout fall out of the ranking. → [P](PRINCIPLES.md#rank-the-facts-out-loud-before-you-touch-the-type)
2. Count the channels on a distinction. Two carry it; the third is a cost.
   → [P](PRINCIPLES.md#each-extra-channel-costs-more-than-it-carries)
3. What the thing *is* goes with the name; what it is *on or off* goes in the
   list; *when* it mattered is a dateline. → [P](PRINCIPLES.md#identity-versus-standing-is-the-test-for-what-belongs-in-a-list)
4. Icon carries the step on a scale, words carry the subject. Repeat one mark
   for the negatives. → [P](PRINCIPLES.md#a-glyph-that-repeats-is-worth-more-than-a-glyph-that-varies)
5. No accent unless this is the place to spend it — never on the second-most
   interesting fact next to the first. → [P](PRINCIPLES.md#spend-no-accent-unless-this-is-the-place-to-spend-it)
6. Three type styles, not five. Rank by order, colour, position, lane — size
   only for the headline. → [P](PRINCIPLES.md#count-the-type-styles)
7. Plain words first, citation demoted inline to a reference. → [P](PRINCIPLES.md#plain-language-first-citation-demoted-to-a-reference)
8. Compose dark first; derive light from it. → [P](PRINCIPLES.md#build-dark-first)

## Before a rule that reads data ships

9. Does it hold for every value? What does the longest value do? What are the
   junk values? Which records are a different shape? → [P](PRINCIPLES.md#checks-to-run-before-committing-to-a-rule-that-reads-data)
10. Read the generator (`scripts/seed_pages.py`), not one page — one page shows
    one shape. → [C](CONVENTIONS.md#before-you-mock-a-module)
11. Glob every `data.json` for the value domain and counts before picking
    specimens; counts go stale, regenerate them. → [C](CONVENTIONS.md#before-you-mock-a-module)

## Building

12. `shared/site.css` is the source; a mock that disagrees is stale. → [C](CONVENTIONS.md#direction-of-truth)
13. Module width is **368px**, not 360. → [I](IMPLEMENTATION.md#metrics)
14. One token set, redefined under `prefers-color-scheme: dark` — `--paper`,
    `--panel`, `--ink`, `--muted`, `--rule`, `--note-bg`, `--accent`. → [I](IMPLEMENTATION.md#tokens)
15. New classes are scoped to the module; `.spec` / `.speclist` are shared with
    three other panels. → [C](CONVENTIONS.md#porting-a-design-back-into-the-site)
16. `index.html` is regenerated from `data.json`, never hand-edited; migrations
    are scratchpad scripts. → [C](CONVENTIONS.md#porting-a-design-back-into-the-site)
17. Verify with `getComputedStyle`, not screenshots, and hard-reload first. → [C](CONVENTIONS.md#porting-a-design-back-into-the-site)

## In Paper

18. Build one specimen, `duplicate_nodes`, `set_text_content` via the
    `descendantIdMap`, `delete_nodes` — never re-write HTML per variant. → [T](PAPER.md#variants)
19. Flex, padding and gap only. No margin, no grid, no tables, px not rem. → [T](PAPER.md#write_html-limits)
20. Custom properties don't scope per node — a dark board is a second token set
    plus a rebind by role. → [T](PAPER.md#tokens-and-dark-variants)
21. Judge colour from artboard screenshots only; node shots render on black. → [T](PAPER.md#screenshots)
22. `get_font_family_info` before the first type each session;
    `height: "fit-content"` and `finish_working_on_nodes` at the end. → [T](PAPER.md#order-of-operations)

**P** [principles](PRINCIPLES.md) · **C** [conventions](CONVENTIONS.md) ·
**T** [tool](PAPER.md) · **I** [implementation](IMPLEMENTATION.md)
