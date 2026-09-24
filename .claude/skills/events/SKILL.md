---
name: events
description: Run this repo's events module (events/) locally — the pipeline that reads the registered public-space calendars and puts upcoming events on building pages (30 days), the homepage map (6 days, pulsing dots), and the /events listing. Invoked as /events with no argument for a full run (fetch, check, build, PR), or /events <request> for one piece of that work. Use whenever the task touches events/ — sources.json, venues.json, events.json, fetch.py, check.py, the venue register, the event panel, the map's event layer, or the GitHub Actions events workflow — even when the user doesn't say "events".
---

# Events module

`events/` reads the calendars of San Francisco's public spaces and puts what
they announce in the three places a reader looks. This skill is the door into
that module, and it does locally what
[.github/workflows/events.yml](../../../.github/workflows/events.yml) does on
a schedule — the whole run is code, no agent in the loop, by design.

**The module's own documents are the authority.** Read them first, in this
order:

1. **[events/AGENTS.md](../../../events/AGENTS.md)** — the rulebook: the
   pipeline, the venue register's `path` rule, the coordinate invariants,
   privacy. Read it whole; it is short.
2. **[AGENTS.md](../../../AGENTS.md)** (root) — the privacy limits and the
   ground rules.
3. **[shared/AGENTS.md](../../../shared/AGENTS.md)** — the page contract, if
   you will touch a page or `shared/site.css`.

## A full run

```bash
python3 events/tools/fetch.py            # every open source → events/events.json
python3 events/tools/fetch.py venues     # which venues produced no dot — worth a look
python3 events/tools/check.py --stats    # the registers and the data file
python3 scripts/build_events.py          # /events + shared/events.geojson
python3 scripts/build_site.py            # the whole site, panels included
python3 scripts/validate.py
```

Then read the diff: `events/events.json` should be the only tracked file that
changed (`events/index.html` and `shared/events.geojson` are build artifacts,
gitignored). New or renamed venues the run saw but could not locate print in
the fetch output and land in `events.json`'s `unlocated_venues` — add them to
`events/venues.json` when a trustworthy coordinate exists (Nominatim or EAS;
record which in the venue's `note`), and leave them listed-but-dotless when
none does. Commit `events.json` (and `venues.json` if you touched it), push,
and open or update the PR — see "Where a run starts" in
[the news skill](../news/SKILL.md), which this run follows unchanged: continue
the open `events/` PR if there is one rather than branching fresh.

## What this module will not do

- **It does not judge events.** There is no screen and no ten-year test — a
  listed event is a kept event. The only filters are time (past events fall
  out), space (the SF bounding box), and access (`access: needs-human` is
  never fetched). A title that names a private individual is the one content
  problem worth a parser change, per events/AGENTS.md.
- **It does not seed pages.** An event never creates a page; a venue with no
  documented parcel simply gets no `path` — the dot and the listing still
  publish. If a venue clearly deserves a page, that is the seeder's job in a
  separate concern, not this run's.
- **It never edits generated files.** `events.json` is written by `fetch.py`;
  `events/index.html` and `shared/events.geojson` by `build_events.py`;
  address-page panels by `render`. A wrong event means a wrong parser or a
  missing venue entry — fix those, not the artifacts.

## When the work is the module itself

Parser changes, a new calendar, register tuning: the same shape as everywhere
else here — read the rulebook first, keep `check.py` honest about the new
state, update `events/AGENTS.md` and this skill in the same commit when the
shape of the work changes, and say *why* in the commit message. A new calendar
source is a human's call (it is a relationship with a publisher); a new venue
entry is data and is yours to make.
