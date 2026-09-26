# Know This Place

A public, static encyclopedia of the built environment: one page per building,
in San Francisco so far. No framework, no dependencies — files, one stylesheet,
one enhancement script, nine stdlib-only Python scripts. The site is built
from those files by `scripts/build_site.py` and published by Actions; the
repository holds the sources, not the pages.

## Read the file for the job, not the whole tree

Every directory's `AGENTS.md` is a **rules core**, meant to be read whole and
kept short. Beside each sits a **reference** you grep a section out of and never
read front to back. Start with the row that matches the task.

| Doing | Read | Then, per section |
|---|---|---|
| editing an address page | [AGENTS.md](AGENTS.md) + the neighborhood's `AGENTS.md` + [shared/AGENTS.md](shared/AGENTS.md) | [REFERENCE.md](REFERENCE.md), [shared/BLOCKS.md](shared/BLOCKS.md) |
| creating pages in bulk | [AGENTS.md](AGENTS.md) | [REFERENCE.md → Seeding](REFERENCE.md#seeding-a-new-area) |
| a park, plaza or place in a park | [AGENTS.md](AGENTS.md) | [REFERENCE.md → Place pages](REFERENCE.md#place-pages) |
| querying city data | — | [DATA-SOURCES.md](DATA-SOURCES.md) |
| a question about the whole corpus | — | `corpus.jsonl`, [REFERENCE.md → The corpus index](REFERENCE.md#the-corpus-index) |
| mining a source | [research/AGENTS.md](research/AGENTS.md) | [research/RUNBOOK.md](research/RUNBOOK.md), [research/LESSONS.md](research/LESSONS.md), [research/findings/INDEX.md](research/findings/INDEX.md) |
| finding a new source | [research/AGENTS.md](research/AGENTS.md) | [research/SOURCES.md](research/SOURCES.md), [research/TRIAGE.md](research/TRIAGE.md) |
| running the news pipeline | [news/AGENTS.md](news/AGENTS.md) | [news/PIPELINE.md](news/PIPELINE.md) |
| running the events pipeline | [events/AGENTS.md](events/AGENTS.md) | `events/tools/fetch.py` + `check.py`, `scripts/build_events.py` |
| adding merchants to their buildings — a `monetization` issue | [merchants/AGENTS.md](merchants/AGENTS.md) | [REFERENCE.md → occupants](REFERENCE.md#occupants) |
| changing the CSS or the renderer | [shared/AGENTS.md](shared/AGENTS.md) | [shared/BLOCKS.md](shared/BLOCKS.md) |
| adding a number to the `/stats/` dashboard | [AGENTS.md](AGENTS.md) | `scripts/build_stats.py` |
| designing a module | [design/AGENTS.md](design/AGENTS.md) | `design/*` |

There are skills for the five modules: `/research`, `/news`, `/events`,
`/design`, `/ui`.

## The four rules you cannot get wrong

Everything else is in [AGENTS.md](AGENTS.md). These four are the ones whose
breach is expensive to undo:

1. **`data.json` is the source of truth. `index.html` is generated and not
   committed.** Never hand-edit an address page's HTML — change `data.json`
   and run `python3 scripts/seed_pages.py render <path>`. The HTML is
   gitignored, so a render leaves nothing in `git status`; that is correct.
   `validate.py` fails the build if the two disagree.
2. **Every fact needs a source**, cited in `data.json`'s `sources` array with
   the query URL and retrieval date. Never invent, estimate, or extrapolate.
3. **These pages describe buildings, not the people in them** — so that this
   site never becomes a way to look somebody up, and never launders a name out
   of a permit or a deed onto a public page. No current residents, occupants or
   owners, not even from public records. **Notable past occupants are always
   added**, with a citation: an architect, a builder, a documented past
   resident, whoever the building is known for, wherever a published source
   already covers them and they are plainly no longer there. A business trading
   from the building is not a person: it may be named as the current occupant,
   but never its owners, staff or customers.
4. **No new tooling.** No frameworks, no package manifests, no dependencies.
   The build is `scripts/build_site.py` calling eight stdlib-only siblings,
   and every page must still render completely from its HTML alone — nothing
   the build produces needs JavaScript to be readable.

## Before you commit

```bash
python3 scripts/build_site.py && python3 scripts/validate.py
```

`build_site.py` runs every generator in the one order that works — hubs,
districts, link index, render, map index, events, sitemap, corpus index, stats — in
about a minute. Almost all of what it writes is gitignored, so the only things
it can leave in `git status` are `corpus.jsonl` and a hub `index.md`; commit
those. Then fix everything `validate.py` flags.

To look at the result: `python3 scripts/build_site.py --serve` and open
`http://localhost:8517`. That port, and no other — the map keys are restricted
to it.

Branch names are `feedback/issue-<N>`, `refresh/<YYYY-MM-DD>` or
`seed/<area-slug>`. One concern per PR. Never push to `main`.
