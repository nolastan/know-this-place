---
name: news
description: Run this repo's news module (news/) locally — the daily pipeline that watches San Francisco newsrooms for stories naming an address and turns the ones that earn it into a dated entry on that building's page. Invoked as /news with no argument to do a full run (poll, read, extract, resolve, seed, publish), or /news <request> for one piece of that work. Use whenever the task touches news/ — feeds, the screen, cursors, a queue file, items files, reading queued stories, deciding what earns a timeline entry, seeding a page for a news address, the homepage news grid, or the GitHub Actions news workflow — even when the user doesn't say "news".
---

# News module

`news/` watches the city's newsrooms for the day something happens at a San
Francisco address, and puts it on that building's timeline. This skill is the
door into that module, and it does locally what
[.github/workflows/news.yml](../../../.github/workflows/news.yml) does on a
schedule against the Anthropic API.

**The module's own documents are the authority, and this skill does not restate
them.** Read them first, in this order:

1. **[news/AGENTS.md](../../../news/AGENTS.md)** — the rulebook: the pipeline,
   the ten-year test, privacy, what a timeline entry is and is not. Read it
   whole; it is short.
2. **[news/PIPELINE.md](../../../news/PIPELINE.md)** — the working detail per
   stage: cursors, the screen, reading an article, the markup an entry becomes,
   the homepage card, the items-file schema. **Read the section for the stage
   you are on**, not the file.
3. **[AGENTS.md](../../../AGENTS.md)** (root) — the privacy limits, which bind
   hardest here because a news story is mostly about people.
4. **[research/AGENTS.md](../../../research/AGENTS.md)** — the evidence bar and
   the findings schema, reused by this module unchanged.
5. **[shared/AGENTS.md](../../../shared/AGENTS.md)** — the page contract, if you
   will touch a page.

Then get the current state, which is the first thing to do in any run:

```bash
python3 news/tools/poll.py status   # cursors, and every queue file still waiting
python3 news/tools/check.py         # feeds ↔ cursors ↔ items ↔ schema
```

## Where a run starts

**The branch is the module's memory, not `main`.** Nothing here reaches `main`
without a human merging it, so an unmerged PR holds the cursors, the queue and
the items files that a new run must continue from. Starting fresh off `main`
while one sits open re-fetches, re-screens and re-reads everything it already
considered — and because the feeds carry only one to five days, the stories it
had queued age out and are lost rather than merely repeated.

So before anything else:

```bash
gh pr list --state open --base main --limit 50 --json number,headRefName \
  --jq '[.[] | select(.headRefName | startswith("news/"))][0] // empty'
```

- **A `news/` PR is open** → check out its branch, merge `origin/main` in, and
  continue there. Pushing updates that PR; do not open a second one. Resolve any
  merge conflict yourself. The site is not committed, so almost nothing
  generated can conflict; the two that still can (`corpus.jsonl` and a hub
  `index.md`) are rebuilt, never hand-merged — take main's side and re-run
  `python3 scripts/build_site.py`.
- **None is open** → branch `news/$(date -u +%F)` off `main`. If that name
  already exists on the remote from a cycle closed unmerged, suffix it.

Locally you may already be on a working branch the user gave you. That is fine —
say which branch you are using and why, and don't create another one behind
their back.

**Re-run this check before every backfill window, not just once at the start.**
A worklist that says "walk the archive back, one month at a time" (issue #337 is
the worked example) reads like an invitation to open one PR per month — it
isn't. Each month's PR starts fresh off `main`, so it has no idea the PR you
opened for last month even exists; if that PR is still open, the fact that
you're the one who opened it minutes ago carries no weight. And because an
outlet's archive is its own past coverage, the same address surfaces across
different months — SF YIMBY covers a given project again and again — so two
backfill branches that never merge into each other *will* independently seed or
enrich the same page, and whichever merges second conflicts with the first.
Do the whole worklist on one branch: after draining a window's queue and
publishing, run the open-PR check again before listing the next window, and
keep pushing to that same PR until you actually stop (session end, or the
worklist is exhausted) — only then does it get merged and a later session
starts the next one fresh. "Each batch is its own PR" (when a worklist says
that) means each batch is independently reviewable and mergeable, not that
batches done back-to-back in one sitting should each fork their own branch.

## An unfinished run outranks a new one

**Work down this ladder and take the first thing with something in it.** The
order is by what it costs to redo, cheapest-to-lose last:

1. **Findings with `publish.status: "pending"`** anywhere under `news/items/`.
   They are already screened, read and resolved, so publishing one costs a
   fraction of reading a new story. Clear them first — including re-checking any
   whose reason was "the resolver could not join this address to a parcel", which
   is a condition that changes over time.
2. **A finding with no `publish` block at all.** That is a run that died
   mid-decision, and it is easy to miss: check for it explicitly rather than
   assuming every finding carries a verdict.
3. **A queue file still on disk.** It is the durable worklist; the cursor has
   already moved past its stories, so what is in that file exists nowhere else.
   Read an older one before today's.
4. **A fresh poll**, then the full pipeline below.

## A full run

```bash
python3 news/tools/poll.py poll          # fetch, screen, queue, advance cursors
python3 news/tools/read.py news/queue/<date>.json
```

The feeds reach two days back, so a poll is only ever today's news. Everything
older is reached through the outlet's own archive, one bounded window at a time:

```bash
python3 news/tools/poll.py backfill --since 2026-07-01 --until 2026-07-31 --feed sfyimby
python3 news/tools/read.py news/queue/backfill-2026-07-01-to-2026-07-31.json
```

The window is capped at a month and a second one is refused while a backfill
queue is waiting — **drain it, then go again.** A backfilled story is published
by exactly the route below; nothing about the rest of the run changes. `sfyimby`
is the highest-yield source to point it at. See
[news/PIPELINE.md → Backfill](../../../news/PIPELINE.md#backfill-the-archive-behind-the-feed).

**Commit and push the moment the read is done, before publishing anything.**
Polling and reading is the expensive, irreplaceable half — a run cut short after
this point loses only judgement, one cut short before it loses the stories
themselves.

```bash
git add -A && git commit -m "news: queue and cursors for <date>" && git push
```

Then, per the rulebook: write what survives the ten-year test into
`news/items/<feed-id>/<date>.json`, resolve, seed the pages that don't exist,
put the entry on each page, and put its card on the homepage.

```bash
python3 research/tools/resolve_eas.py apply news/items/<feed>/<date>.json
python3 scripts/seed_pages.py seed-list --manifest research/manifests/news-<date>.json
python3 scripts/build_site.py
python3 research/tools/check.py --index
python3 scripts/seed_pages.py render <path to the page>
python3 news/tools/check.py && python3 scripts/validate.py
```

**Commit and push each page as you finish it.** Not one commit at the end: work
that is pushed survives a session running out of room, work that is staged does
not.

**Delete the queue file once you have read it through**, and leave it in place,
committed, if you did not. That deletion is how the module records the work is
done.

### Finish the run

**There is no page cap here.** Publish every finding that earns a page, and
leave the run with nothing deferred.

The three-page cap you may have seen belongs to
[the workflow](../../../.github/workflows/news.yml), and it is a fact about
that job rather than about this work: it runs on `--max-turns 90` and a
45-minute timeout, and either one kills the agent where it stands — the first
run to get that far spent $5.36, hit the turn cap mid-flight and pushed nothing
at all. Capping the expensive half is how that job leaves something behind.
A `/news` run has neither limit, so importing the number just strands work that
was ready to publish, and the stories it strands are the ones a later run has
to re-establish from scratch.

So **`publish.status: "pending"` means blocked, not deferred**: the resolver
could not join the address, the seeder may not make a page for that parcel, the
story needs something only a human can settle. A finding that is merely *next*
is not pending — it is unfinished work, and the run is not over. Say in the PR
what is pending and what is blocking each one.

**Commit and push each page as you finish it** all the same. That is not about
spend; it is that a session can run out of room, and work that is pushed
survives it while work that is staged does not.

**Nothing left worth publishing is a finished run, not a failed one.** A thin
day is a good day if the timeline stays honest.

## What goes wrong

Everything else is in the module docs. These are the ones worth carrying:

- **An address is not a fact.** Most queued stories name no address, and many
  that do name it in passing — the venue of a concert, the courthouse steps, the
  backdrop of a photo. The ten-year test is the whole filter, and it is meant to
  decline generously.
- **The headline is published verbatim, and it is the only text of theirs that
  reaches a page.** Never edit it, never write a sentence summarizing the story
  under it. **A headline naming a private individual cannot be published at
  all** — there is no rewriting your way past it, because you are not writing
  the entry. Decline it.
- **One event, one entry.** Two outlets covering the same opening is one
  timeline entry; decline the duplicate and say in its note which one carries it.
- **The page is only half of it.** An entry that never reached the homepage's
  news grid is not published — that grid is the only thing putting a day's news
  where a reader will meet it. Twelve cards, newest first, ordered by the entry's
  date.
- **Derive the manifest's numbers from `resolution.method`, not from the
  story.** The resolver unions the addresses reached through retired APNs, so
  the page's street number is often not the one the article printed.
- **Read a seeded page before you commit it.** `attach_permits` has joined
  permits on street name and number before, and San Francisco has two Montgomery
  Streets; a parcel the seeder refuses is not a page to force.
- **Never verify the Street View embed.** Its API key is restricted to the
  production domain and always fails elsewhere.

## Leave the module better than you found it

Same rule as the research module, and
[news/AGENTS.md → Amending this module](../../../news/AGENTS.md#amending-this-module)
is explicit about it: the screen's word lists, the feed register and the stage
boundaries are yours to improve when the work fights the structure. When a skip
turns out to have been wrong, fix the table it came from and say so in the
commit — `poll.py screen "<a headline>"` explains a verdict,
`read.py <queue> --skipped` measures what a run of skips actually cost, and
`poll.py audit` shows which rules queue stories that never come to anything,
and fails if a change would skip one that was published.

Two things still need a human: **adding or un-blocking a feed**, and **anything
that changes what a page looks like**.

## Before you stop

- Every finding carries its decision, in the same commit that edits the pages.
- `python3 news/tools/check.py`, `python3 research/tools/check.py` and
  `python3 scripts/validate.py` all clean. **CI runs all three**, so a failure
  here is a failure on the pull request. Seeding a page writes a manifest that
  stales `research/findings/INDEX.md` — rebuild it with
  `python3 research/tools/check.py --index`.
- `git diff` read through, and every change is a real fact about a building.
- The homepage grid holds twelve cards and the newest are the twelve.
- The PR lists every page touched and seeded, every story used, and the run's
  counts: **considered / queued / read / found / seeded / published / pending**.

Report the same way: counts, plainly, including what you left pending and why.
