# News

Watching the city's newsrooms for the day something happens at a San Francisco
address — and giving that address a page if it hasn't got one.

The [research module](../research/) mines sources search engines cannot see.
This one does the opposite thing for the opposite reason: these outlets are
indexed and ranking, but **nothing joins what they publish to the address it
happened at.** A story about a building is filed under a neighborhood, a
reporter and a date, and it is unfindable a year later from the street number.
Putting it on the building's timeline is the work.

A run carries two things off an article: the **headline**, which becomes the
dated entry on the timeline, and the **facts about the building** — architect,
builder, developer, the year it was finished — which fill the page's own fields
and are attributed from the Sources footer. Filing the headline and dropping
the architect throws away the half a page is actually for. AGENTS.md →
"Putting it on the page" has the limits, and the sharpest is that the `building`
block describes the building that stands there: a proposal's design team does
not go on the page of the parking lot it would replace.

**Start with [AGENTS.md](AGENTS.md).** It is the rulebook, and its privacy
section is the part to read twice — a news story is about people, and these
pages are about buildings.

## Layout

```
news/
  AGENTS.md           The rulebook: pipeline, cursors, the screen, privacy
  README.md           This file
  feeds.json          The register — one row per source, and why it behaves as it does
  state/cursors.json  What each feed has already been considered up to
  queue/<date>.json   One poll run: what to read, what was skipped and why
  items/<feed>/*.json Findings files — the research schema, the research resolver
  tools/poll.py       Fetch, screen, queue, advance the cursors
  tools/read.py       Read queued articles; report the addresses in them
  tools/check.py      Register ↔ cursors ↔ items ↔ schema
  tools/test_screen.py  Every case the screen got wrong once, kept as a test
```

`queue/` is empty between passes by design: a queue file is deleted once it has
been drained, and anything still in one is still work. `poll.py status` lists
them.

## Running it

```bash
python3 news/tools/poll.py poll                          # every open feed
python3 news/tools/poll.py status                        # where the cursors stand
python3 news/tools/read.py news/queue/2026-08-16.json
python3 news/tools/check.py --stats                      # yield so far
```

Then, for anything worth keeping: write it into `news/items/<feed>/<date>.json`,
resolve it with the research module's resolver, seed the parcel if it has no
page yet, publish it as a timeline entry per [AGENTS.md](AGENTS.md) → "Putting
it on the page", and put its card on the homepage's **In the news** grid per
[AGENTS.md](AGENTS.md) → "The homepage is the news". The grid holds the twelve
newest entries on the site and is most of what the homepage is, each card also
a pulsing dot on the map above it — and a story filed on a page nobody has a
reason to open yet is a story nobody reads.

```bash
python3 research/tools/resolve_eas.py apply news/items/hoodline/2026-08-16.json
python3 scripts/seed_pages.py seed-list --manifest research/manifests/news-2026-08-16.json
python3 scripts/build_sitemap.py
python3 scripts/build_map_index.py
python3 scripts/validate.py
```

`read.py` marks which addresses already have pages. That is information, not a
work order: an address with no page is a page to create, and `--only-pages`
exists to narrow a long backlog by hand, not to decide which stories matter.

## What a good day looks like

Low yield is the design, exactly as in research. The first full pass, on
2026-08-16, is the honest benchmark:

| | |
|---|---|
| Items in the nine polled feeds | 167 |
| New (inside the two-week backfill) | 161 |
| Queued to read | 45 |
| Skipped by the screen, with a reason | 116 |
| Facts extracted and resolved to a parcel | 5 |
| Read, resolved, and declined with a reason | 2 |
| Parcels seeded because the story had nowhere to go | 5 |
| Facts published to a page | 5 |

Five buildings in a day's news across nine newsrooms: 2918 Mission Street,
2740 McAllister Street, 400 Divisadero, 350 Bay Street and 520 Geary Street.
All five resolved cleanly to active parcels — and none of the five had a page,
which is the ordinary case rather than the exception: 10,828 pages is a small
slice of the city. So the pass seeded them from
[research/manifests/news-2026-08-16.json](../research/manifests/news-2026-08-16.json)
and put the headlines on the pages it had just created. A day's news is a list
of buildings the city is talking about, and that is as good a reason to
document one as any survey's inventory.

The two declines are the more instructive half. An obituary of the broker
behind 101 California Street is the only story all day whose address *does*
have a page, and it was declined: a story about a person that mentions a
building is not a building story. A Union Square retail story names 50 Powell
Street in a closing roundup rather than as its subject, so attaching the
headline to that number would have been a guess. Both are recorded in full —
`publish.status: declined` with the reason — because a decision nobody can
audit is indistinguishable from an oversight.

That is the expected arithmetic, not a fault to explain away. Five facts and
two audited refusals is a good day, whether or not the site had heard of the
buildings that morning.

**The screen was audited the same day.** All 116 skipped stories were re-read
in full (`read.py <queue> --skipped`): 28 of them named an address, and every
one was out of the city, a Muni line, a venue mentioned in passing, or a
column of batting averages that looks like a column of addresses. The one
genuine building story among them — an Examiner piece on a Divisadero bar —
had already been queued from the Examiner's own section page, so nothing was
lost. Re-run that audit whenever you change the screen; the traps it caught
are now cases in `tools/test_screen.py`.

## Why the feeds are what they are

Ten sources are registered; nine are polled. They divide into three shapes,
and [feeds.json](feeds.json) records what each one does wrong:

- **Ordinary RSS** — Mission Local, Hoodline, SFist, The Registry, The
  Standard, What Now. Hoodline and SFist syndicate the whole article in the
  feed, which is how we read Hoodline at all: its article pages answer a
  fetcher with 403.
- **Bluesky accounts** — the Chronicle and the Examiner. These are posts, not
  articles: no title element at all, and the article link is the last URL in
  the post text, often a bit.ly.
- **A section page** — the Examiner's `/news/`. No dates, no summaries, so the
  cursor is the set of article URLs seen.

The San Francisco Business Times is registered but **not polled**: its feed
host's robots.txt ends in a blanket disallow. That is a conversation with a
publisher, not a flag to flip — see `access` in feeds.json.
