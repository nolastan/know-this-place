---
name: events
description: Run this repo's events module (events/) locally — the pipeline that reads the registered public-space calendars and puts upcoming events on place and address pages (30 days), the homepage map (6 days, pulsing dots), and the /events listing. Invoked as /events with no argument for a full refresh (fetch, resolve new venues, screen, check, build, PR), or /events <request> for one piece of that work. Use whenever the task touches events/ — sources.json, venues.json, events.json, fetch.py, check.py, the venue register, the event panel, the map's event layer, or the GitHub Actions events workflow — even when the user doesn't say "events".
---

# Events module

`events/` reads the calendars of San Francisco's public spaces and puts what
they announce in the three places a reader looks. The daily read runs in
[.github/workflows/events.yml](../../../.github/workflows/events.yml) as plain
code — no model, because a model per day is expensive and the read needs
none. **This skill is the part that needs judgement**, the events counterpart
of `/news` and `/research`: it refreshes the data like the workflow does, then
does what code can't — names the venues the register doesn't know, points
them at their pages, and drops what shouldn't be listed.

**The module's own documents are the authority.** Read them first, in this
order:

1. **[events/AGENTS.md](../../../events/AGENTS.md)** — the rulebook: the
   pipeline, the venue register's `path` rule, the coordinate invariants,
   privacy. Read it whole; it is short.
2. **[AGENTS.md](../../../AGENTS.md)** (root) — the privacy limits and the
   ground rules.
3. **[REFERENCE.md → Place pages](../../../REFERENCE.md#place-pages)** — most
   venues are parks and plazas, and they point at place pages.

## A full refresh

```bash
python3 events/tools/fetch.py            # every open source → events/events.json
python3 events/tools/fetch.py venues     # every venue seen; "no page" = no dot, no panel
python3 events/tools/check.py --stats    # the registers and the data file
```

A calendar that fails (a timeout, a block) keeps its previous upcoming slice
and the run exits 1 naming it — say so in the PR, don't treat it as done.

Then the judgement pass, in this order:

1. **New venues.** For every location in `events.json`'s `unlocated_venues`,
   and every venue the `venues` report shows with no `path`, decide what place
   it means. Search the page tree first — `place.json` names for a park, plaza
   or place in a park, then `data.json` for a building — and set `path` only
   under the rule in events/AGENTS.md. Add the entry to `events/venues.json`
   with `lat`/`lng` from the place page, EAS or Nominatim, and a `note` saying
   which. A stairway, an intersection or a block party has no page, so it
   gets no `path` and no map dot — it lists on `/events` only.
2. **Re-run `fetch.py`** so the new entries resolve (it re-matches events
   carried over from a failed calendar too), then `check.py`.
3. **Screen titles.** A title that names a private individual — a memorial,
   a birthday, a named instructor's private class — is not listed. Fix it in
   the source's parser in `fetch.py` (a drop rule), never by editing
   `events.json`.
4. **Build and look.**

   ```bash
   python3 scripts/build_site.py && python3 scripts/validate.py
   ```

   Spot-check one place page's "Upcoming events" panel and `/events/`.

Commit `events/events.json`, plus `venues.json` and any `fetch.py` change,
and open or update the PR. Continue the open `events/` PR if there is one
rather than branching fresh — the workflow does the same.

## Known source quirks

- **Illuminate** — its iCal feed carries no per-event URL. Each event is a
  WordPress post, so `fetch.py` reads the REST API (`links` in
  `sources.json`) and matches on start time and title; slugs can't be
  guessed, since reused names get `-2`, `-3`. Only an event the API doesn't
  return falls back to the public events page. Its titles end in the date
  (`| September 26`); `clean_title` strips it, so a series reads as one
  name. Its `LOCATION` is a bare
  street address, so `venues.json` does the naming.
- **SF Rec & Park** — one iCalendar feed per calendar ID. `LOCATION` reads
  `"<Venue> - <address>  San Francisco CA 94122"`, occasionally wrapped in
  `<p>` tags; `clean_location` strips both, and the venue half is what to
  add as a matcher. The host resets connections from some cloud IPs — a
  failed read there is the host's, not the parser's.
- **Squarespace (Nature in the City, Sunset Dunes)** — an unset pin is the
  platform default in New York; `fetch.py` drops it.
- **Alemany Farm** — hand-written HTML, `Crawl-Delay: 20`: one request a run.

## What this module will not do

- **It does not judge events on merit.** There is no ten-year test — a
  listed event is a kept event. The only filters are time, space (the SF
  bounding box), access (`access: needs-human` is never fetched) and the
  privacy screen above.
- **It does not seed pages.** An event never creates a page. If a venue
  clearly deserves one, that is the seeder's or the place manifest's job in a
  separate concern.
- **It never edits generated files.** `events.json` is written by `fetch.py`;
  `events/index.html` and `shared/events.geojson` by `build_events.py`; the
  panels by `render`. A wrong event means a wrong parser or a missing venue
  entry — fix those, not the artifacts.

## When the work is the module itself

Parser changes, a new calendar, register tuning: read the rulebook first, keep
`check.py` honest about the new state, update `events/AGENTS.md` and this
skill in the same commit when the shape of the work changes, and say *why* in
the commit message. A new calendar source is a human's call (it is a
relationship with a publisher); a new venue entry is data and is yours to make.
