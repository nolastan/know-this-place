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
"What an entry is" has the limits, and the sharpest is that the `building`
block describes the building that stands there: a proposal's design team does
not go on the page of the parking lot it would replace.

**Start with [AGENTS.md](AGENTS.md).** It is the rulebook, and its privacy
section is the part to read twice — a news story is about people, and these
pages are about buildings.

## Layout

```
news/
  AGENTS.md           The rulebook: what an entry is, privacy, the pipeline map
  PIPELINE.md         The working detail per stage: cursors, the screen,
                      reading an article, the markup, the items schema
  README.md           This file
  feeds.json          The register — one row per source, and why it behaves as it does
  state/cursors.json  What each feed has been considered up to, and which
                      archive windows have been walked
  queue/<date>.json   One poll run: what to read, what was skipped and why
  queue/backfill-…    One archive window, named for the window rather than the day
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

For anything published before the feeds reach — which is nearly everything —
`backfill` lists one window out of an outlet's own archive and screens it
exactly as the daily poll does:

```bash
python3 news/tools/poll.py backfill --since 2026-07-01 --until 2026-07-31 --feed sfyimby
python3 news/tools/read.py news/queue/backfill-2026-07-01-to-2026-07-31.json
```

The window is capped at a month and a new one is refused while a backfill queue
is still waiting. That is the batching rule, and the reason for it is in
[PIPELINE.md](PIPELINE.md) → "Backfill": a month of the eight routed sources
lists 2,558 stories and queues 538, and every queued one is read by hand.

Then, for anything worth keeping: write it into `news/items/<feed>/<date>.json`,
resolve it with the research module's resolver, seed the parcel if it has no
page yet, publish it as a timeline entry per [AGENTS.md](AGENTS.md) → "What an
entry is", and put its card on the homepage's **In the news** grid per
[PIPELINE.md](PIPELINE.md) → "The homepage grid". The grid holds
the six newest entries on the site, and a story filed on a page nobody has a
reason to open yet is a story nobody reads.

```bash
python3 research/tools/resolve_eas.py apply news/items/hoodline/2026-08-16.json
python3 scripts/seed_pages.py seed-list --manifest research/manifests/news-2026-08-16.json
python3 scripts/seed_pages.py districts
python3 scripts/build_sitemap.py
python3 scripts/build_map_index.py
python3 scripts/build_link_index.py
python3 research/tools/check.py --index
python3 scripts/validate.py
```

`read.py` marks which addresses already have pages. That is information, not a
work order: an address with no page is a page to create, and `--only-pages`
exists to narrow a long backlog by hand, not to decide which stories matter.

Under an address that has a page, it also lists the news entries that page
already carries. Read those before extracting: the duplicate that "one event,
one entry" forbids is usually an entry an earlier run published days ago, not a
second story in today's queue.

It also prints a `headline:` and an `article:` line when the feed's own title
and link disagree with the article's — which is what a social feed always does,
since it carries a post about the story rather than the story. Cite those two
lines when they appear: the headline goes on the page verbatim, and the link is
the attribution.

Agents working in Claude Code have a `/news` skill
([../.claude/skills/news/SKILL.md](../.claude/skills/news/SKILL.md)): `/news` on
its own does a whole run — finding the branch a previous run left, clearing
what it did not finish, then polling, reading and publishing — and `/news
<request>` routes a request into the stage it belongs to. It is a door into the
documents above, not a substitute for them, and it is the local equivalent of
[../.github/workflows/news.yml](../.github/workflows/news.yml), which runs the
same pipeline daily against the Anthropic API.

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

## What is behind the feeds

**An RSS feed is not an archive.** The open feeds carry between one and sixteen
days — most of them two — so the daily poll sees about two days of news whatever
`--backfill-days` is set to: the floor never binds, the feed does. Eight of the
eleven polled sources publish their archive somewhere else, and `feeds.json`
records the route into each one.

| feed | route | listed in July 2026 | queued to read |
|---|---|---|---|
| sf-chronicle | Bluesky API, paged by cursor | 1,546 | 245 |
| sf-standard | monthly sitemaps, back to 2021-01 | 269 | 52 |
| the-registry | `?paged=N` | 248 | 64 |
| sf-examiner | per-day sitemaps, listed by year | 186 | 49 |
| mission-local | `?paged=N` | 150 | 60 |
| sfyimby | `?paged=N`, back to Dec 2021 | 60 | 21 |
| the-voice-sf | `?paged=N`, complete to Apr 2024 | 51 | 24 |
| sf-examiner-social | Bluesky API, paged by cursor | 48 | 23 |

Three have none. Hoodline answers 403 to its sitemap as it does to its article
pages, What Now publishes no sitemap we can read and 404s on `?paged=N`, and
SFist's is a single 17MB document of 50,000 URLs — a workable route, measured
and not yet wired, because it costs the whole file per window. Those three are
going-forward sources: a run that misses two days of them loses those stories.

**sfyimby is where the addresses are.** It is development-only, its first
`<category>` is the street address itself, and the rest name the architect,
developer and contractor. The Chronicle's account is the opposite shape — a
third of everything listed, and most of it national wire, sport and weather.

## Why the feeds are what they are

Twelve sources are registered; eleven are polled. They divide into three
shapes, and [feeds.json](feeds.json) records what each one does wrong:

- **Ordinary RSS** — Mission Local, Hoodline, SFist, The Registry, The
  Standard, What Now, SF YIMBY, The Voice. Hoodline and SFist syndicate the
  whole article in the feed, which is how we read Hoodline at all: its article
  pages answer a fetcher with 403.
- **Bluesky accounts** — the Chronicle and the Examiner. These are posts, not
  articles: no title element at all, and the article link is the last URL in
  the post text, often a bit.ly.
- **A section page** — the Examiner's `/news/`. No dates, no summaries, so the
  cursor is the set of article URLs seen.

The San Francisco Business Times is registered but **not polled**: its feed
host's robots.txt ends in a blanket disallow. That is a conversation with a
publisher, not a flag to flip — see `access` in feeds.json.
