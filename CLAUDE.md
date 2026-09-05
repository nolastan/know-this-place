# Know This Place

A public, static encyclopedia of the built environment: one page per building,
in San Francisco so far. No framework, no build step, no dependencies — files, one
stylesheet, one enhancement script, five stdlib-only Python scripts.

## Read the file for the job, not the whole tree

Every directory's `AGENTS.md` is a **rules core**, meant to be read whole and
kept short. Beside each sits a **reference** you grep a section out of and never
read front to back. Start with the row that matches the task.

| Doing | Read | Then, per section |
|---|---|---|
| editing an address page | [AGENTS.md](AGENTS.md) + the neighborhood's `AGENTS.md` + [shared/AGENTS.md](shared/AGENTS.md) | [REFERENCE.md](REFERENCE.md), [shared/BLOCKS.md](shared/BLOCKS.md) |
| creating pages in bulk | [AGENTS.md](AGENTS.md) | [REFERENCE.md → Seeding](REFERENCE.md#seeding-a-new-area) |
| querying city data | — | [DATA-SOURCES.md](DATA-SOURCES.md) |
| mining a source | [research/AGENTS.md](research/AGENTS.md) | [research/RUNBOOK.md](research/RUNBOOK.md), [research/LESSONS.md](research/LESSONS.md), [research/findings/INDEX.md](research/findings/INDEX.md) |
| finding a new source | [research/AGENTS.md](research/AGENTS.md) | [research/SOURCES.md](research/SOURCES.md), [research/TRIAGE.md](research/TRIAGE.md) |
| running the news pipeline | [news/AGENTS.md](news/AGENTS.md) | [news/PIPELINE.md](news/PIPELINE.md) |
| changing the CSS or the renderer | [shared/AGENTS.md](shared/AGENTS.md) | [shared/BLOCKS.md](shared/BLOCKS.md) |
| designing a module | [design/AGENTS.md](design/AGENTS.md) | `design/*` |

There are skills for the four modules: `/research`, `/news`, `/design`, `/ui`.

## The four rules you cannot get wrong

Everything else is in [AGENTS.md](AGENTS.md). These four are the ones whose
breach is expensive to undo:

1. **`data.json` is the source of truth. `index.html` is generated.** Never
   hand-edit an address page's HTML — change `data.json` and run
   `python3 scripts/seed_pages.py render <path>` in the same commit.
   `validate.py` fails the build if the two disagree.
2. **Every fact needs a source**, cited in `data.json`'s `sources` array with
   the query URL and retrieval date. Never invent, estimate, or extrapolate.
3. **These pages describe buildings, not the people in them.** No current
   residents, occupants or owners — not even from public records. Historical
   figures (architects, builders, documented past residents) may be named with
   citations.
4. **No new tooling.** No frameworks, build systems, package manifests or
   dependencies, and every page must render completely from its HTML alone.

## Before you commit

```bash
python3 scripts/validate.py
```

Fix everything it flags. If pages were added or removed, run
`seed_pages.py districts`, `build_sitemap.py`, `build_map_index.py` and
`build_link_index.py` first — all four are derived indexes and `validate.py`
fails until each is current.

Branch names are `feedback/issue-<N>`, `refresh/<YYYY-MM-DD>` or
`seed/<area-slug>`. One concern per PR. Never push to `main`.
