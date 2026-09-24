# Events

Reading the calendars of San Francisco's public spaces for what is happening
soon — a concert at the Bandshell, a cleanup on the Great Highway, a workshop
at the farm — and putting it where a reader looks.

The [news module](../news/) watches what everyone indexes for the one thing
nobody joins up. This one watches calendars that announce their own events —
the join problem is smaller, so the pipeline is smaller too: there is no
screen and no judgement stage, a listed event is a kept event, and the whole
run is three commands of plain code.

An event surfaces three ways:

- **on the building's page**, as an "Upcoming events" panel for the next 30
  days — only when the venue is a parcel the site documents;
- **on the homepage map**, as a pulsing plum dot for the next 6 days;
- **on `/events`**, the full upcoming list, day by day.

An event leaves no trace once it passes. What happened at a place afterwards
is the news module's material, not this one's.

**Start with [AGENTS.md](AGENTS.md).** It is the rulebook — short, because the
pipeline is — and its venue-register and coordinate rules are the part to read
twice.

## Layout

```
events/
  AGENTS.md           The rulebook: the pipeline, the venue register, privacy
  README.md           This file
  sources.json        The calendar register — one entry per publisher
  venues.json         The venue register — location text → name, coords, page
  events.json         The data file fetch.py writes — committed
  index.html          /events, generated — gitignored
  tools/fetch.py      Fetch every calendar → events.json
  tools/check.py      Consistency: registers ↔ data file ↔ page tree
```

The build step lives with the other generators: `scripts/build_events.py`
writes `/events` and `shared/events.geojson`, `scripts/seed_pages.py render`
writes each page's panel, and `.github/workflows/events.yml` runs the fetch
daily — code only, no agent.
