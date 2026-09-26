# The events module — agent constitution

This directory watches the calendars of San Francisco's public spaces and
parks for events announced there, and puts them in the three places a reader
looks: a panel for the next thirty days on the page of the park, plaza or
building the event is at, a pulsing dot on the homepage map for the next six
days that opens that page, and a listing on `/events` for everything
upcoming.

It is the [news module](../news/AGENTS.md)'s uncomplicated cousin. News watches
sources for a *story worth keeping forever* and puts a human's judgement in
the middle of it; events watches calendars for *what is happening soon* and
keeps everything they list — the daily read is mechanical, which is why
GitHub Actions runs it without a model in the loop, and the little judgement
the module needs is the `/events` skill's. Read the root
[AGENTS.md](../AGENTS.md) before working here: its privacy limits bind this
module too, and [shared/AGENTS.md](../shared/AGENTS.md) governs the surfaces
the events land on.

## What this module is for, and what it is not for

**For:** an announced, dated gathering in a public place — a concert at the
Bandshell, a cleanup on the Great Highway, a workshop at the farm, a dance
class on the plaza. The listing says when and where; the page says "something
is happening here" while it is.

**Not for:** a record of what happened. An event leaves no trace on a page
once it passes — it is not a `historical_record` entry and never becomes one.
When a *story* covers an event after the fact, that is the news module's
material, and it earns a timeline entry by the ten-year test, not by having
been on a calendar.

This is also the line on privacy. A calendar listing names a venue, a time and
an organizer — public information a venue wants publicized. The module carries
the title, the time, the venue and the link back, and nothing else: no
descriptions (which carry hosts, instructors and performers' names), no ticket
prices, no organizer contacts. A title that names a private individual — a
memorial, a birthday — should not be listed; if one slips through, the fix is
dropping it in `fetch.py`'s source parser, not editing `events.json`.

## The pipeline

Three stages, all mechanical:

```
fetch ──▶ check ──▶ build
read the   the data file   /events, the map's geojson,
calendars  obeys its own   and every page's panel
→ resolve  rules           follow from it
venues
```

| Stage | Who | Reads | Writes |
|---|---|---|---|
| 1 fetch | `tools/fetch.py` | `sources.json`, the calendars, `venues.json` | `events.json` |
| 2 check | `tools/check.py` | all three files + the page tree | a report |
| 3 build | `scripts/build_events.py`, `scripts/seed_pages.py render` | `events.json` | `events/index.html`, `shared/events.geojson`, the panels on address and place pages |

```bash
python3 events/tools/fetch.py            # fetch every source, write events.json
python3 events/tools/fetch.py venues     # the venues seen, and which have no page
python3 events/tools/check.py --stats    # the registers and the data file
python3 scripts/build_events.py          # /events + shared/events.geojson
python3 scripts/build_site.py            # the whole site, panels included
```

There is no screen and no queue: a listed event is a kept event. That is
deliberate, and it is what the issue asked for — the daily refresh runs in
Actions as plain code, with no model in the loop. A calendar that fails to
answer keeps the upcoming slice of `events.json` it last contributed, so one
publisher's bad morning never empties its venues' panels.

**What does take judgement is the `/events` skill's, run by hand** — the
events counterpart of `/news` and `/research`. Its work is the part code
can't do: reading `unlocated_venues` and the `venues` report and deciding
which place a new location string means, pointing a venue at its page,
dropping a listing whose title names a private person, and diagnosing a
calendar whose parser has stopped matching.

## The three files

- **`sources.json`** is the calendar register — one entry per publisher, like
  `news/feeds.json`. `id` becomes every event's `source`; `kind` picks the
  parser (`ical`, `ical-multi`, `squarespace`, `html`); `access` is `open`
  only where robots.txt permits the fetch — a source that forbids automated
  access is `needs-human`, and changing that flag is a human's call, never an
  agent's.
- **`venues.json`** is the venue register — how a calendar's free-text
  location becomes a named place with coordinates and, where the place has a
  page, the `path` of that page. Matching is substring on the normalized
  location, longest matcher first. **The `path` rule is the important one:**
  set it only where the venue *is* the page's place or parcel.
  - **A park, a plaza or a named place in a park points at its place page**
    (`/<city>/<area>/<place-slug>/`, see
    [REFERENCE.md → Place pages](../REFERENCE.md#place-pages)) — the Bandshell
    at the Spreckels Temple of Music, not Golden Gate Park's parcel on Fulton
    Street; Union Square at the square, not 333 Post. Search `place.json`
    names first.
  - **A building points at its address page** — City Hall, the Randall
    Museum — where EAS or the page's own data says the venue is that parcel.
  - A concert on the plaza in front of a building is an event at the plaza;
    it never belongs on the neighbouring parcel's page, and a pin that lands
    on a *neighbouring* residential parcel is never that parcel's page to
    borrow.
  - A venue in the public right of way — a stairway, an intersection, a
    block party — has no page and never gets one. That is not a failure: it
    still lists on `/events`. It gets no map dot, because a dot opens the
    venue's page and there is none to open.
  An event never seeds a page. When a venue clearly deserves one that doesn't
  exist, that is a separate concern for the seeder or the place manifest.
- **`events.json`** is the data file `fetch.py` writes — the module's one
  artifact, committed like the findings files the other modules write. Every
  event carries its source, its listing URL (we link back, always), its start
  and end, its venue name, and coordinates and `path` when the venue resolves.

Two invariants the pipeline rests on:

- **A coordinate is a cited fact.** Source-provided pins are used as given —
  except the Squarespace platform default, a real coordinate for a place in
  New York that means "no pin was set"; `fetch.py` drops it, and the SF
  bounding box drops every other miss. Register coordinates come from
  Nominatim or EAS, and `venues.json`'s `note` says which, because a pin in
  the wrong place is worse than no pin.
- **A stale build fades rather than being wrong.** The map's six-day window
  and a page's thirty-day window are both applied at read time — in the
  browser and in the renderer — so `events.json` left unfetched for a week
  shows less, never something that already happened.

## Being a good citizen

The news module's rules carry over unchanged: the user agent says who we are
(`know-this-place-events/1.0`), requests are rate-limited, robots.txt is
honoured — Alemany Farm's `Crawl-Delay: 20` is why its page is fetched exactly
once per run — and every entry links back to the listing that published it.
Nothing here would be worth taking without the link; the link is the deal.

## Amending this module

Meant to change, like its siblings: the register, the parsers, the matching,
this file — all yours to improve when the work fights the structure. The two
human decisions are the same as the news module's: **adding or un-blocking a
calendar** (a relationship with a publisher, which `access` records), and
**anything that changes what a page looks like** — the panel's shape, the map
dots, the `/events` page — which is the root AGENTS.md's territory. Adding a
*venue* to `venues.json` is neither: it is data, like registering a feed's
backfill route, and the run's output will tell you when one is missing —
`fetch.py` reports every location that resolved to no dot.
