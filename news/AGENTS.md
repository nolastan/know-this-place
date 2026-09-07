# The news module — agent constitution

This directory watches the city's newsrooms for stories that name a **specific
San Francisco street address**, and turns the ones that do into a dated entry on
that address's page.

It is the [research module](../research/AGENTS.md)'s fast-moving sibling.
Research mines archives that nobody has indexed; news watches sources everybody
has indexed, and earns its place a different way: **the news says what is
happening at an address now, and a page that stops in 1906 is a page that stops
being true.** Read [research/AGENTS.md](../research/AGENTS.md) before working
here — its evidence bar, its citation rules and its corpus discipline bind this
module unchanged — and read the root [AGENTS.md](../AGENTS.md), whose privacy
limits bind hardest of all here, because a news story is mostly about people.

**This file is the rules core.** The mechanics of each stage — cursors, the
screen, reading an article, the markup, the items-file schema — are in
[PIPELINE.md](PIPELINE.md). Read the section for the stage you are on.

## What this module is for, and what it is not for

**For:** a dated, sourced, address-level fact a reader would want on the
building's timeline. A building sold. A restaurant opened in it. It burned. Its
permits were finally pulled after a decade. It was landmarked, evicted,
demolished, rebuilt.

**Not for:** a summary of the news. This is not a clippings file, and a page is
not a feed. A story that merely *mentions* an address in passing — as the venue
of a meeting, the backdrop of a photograph, the office of someone quoted —
gives a page nothing, and the entry it would produce is noise on a timeline
that runs a century deep. When in doubt, the test is:

> **Would this still be worth reading on the building's page in ten years?**

An eviction fight, a fire, a sale, an opening: yes. A city hall press
conference that happened to be held there: no.

## The pipeline

Five stages. The first is mechanical, the middle two are judgement, and the
last two are the research module's, reused unchanged.

```
poll ──▶ read ──▶ extract ──▶ resolve ──▶ publish
cursors   which    what the     which      seed the page
+ screen  stories  story says   parcel?    if there isn't
          say an   about the               one; headline,
          address  building                outlet and date
                                           onto the timeline,
                                           the building's own
                                           facts into its
                                           fields, and a card
                                           onto the homepage
```

| Stage | Who | Reads | Writes |
|---|---|---|---|
| 1 poll | `tools/poll.py` | the registered feeds | `queue/<date>.json`, `state/cursors.json` |
| 2 read | an agent, with `tools/read.py` | the queued articles | nothing yet |
| 3 extract | an agent | what it read | `items/<feed-id>/<batch>.json` |
| 4 resolve | `research/tools/resolve_eas.py` | the items file | `resolution` in the same file |
| 5 publish | an agent, with `scripts/seed_pages.py` | resolved items | `research/manifests/news-<batch>.json`, `san-francisco/**` pages (timeline entry *and* `building` fields), the homepage's news grid, a PR |

Stages 3–5 use the research module's own findings schema and resolver. That is
deliberate: a fact from Mission Local and a fact from an 1895 newspaper are the
same kind of object, and they go through the same gate.

```bash
python3 news/tools/poll.py poll             # fetch, screen, queue, advance cursors
python3 news/tools/read.py news/queue/<date>.json
python3 news/tools/check.py                 # feeds ↔ cursors ↔ items ↔ schema
python3 research/tools/resolve_eas.py apply news/items/<feed>/<batch>.json
python3 scripts/seed_pages.py seed-list --manifest research/manifests/news-<batch>.json
```

Two invariants the stages rest on, both detailed in
[PIPELINE.md](PIPELINE.md):

- **An item is considered once**, and considered means a verdict was recorded —
  read *or* skipped — not that anything was published. That memory is the
  cursor, and **a cursor is only true on the branch it was advanced on**, which
  is why a run continues on the open `news/` PR rather than starting fresh.
- **The screen is deliberately asymmetric**: it skips only on a clear signal
  and queues on doubt, because a queued story costs a glance and a wrongly
  skipped one is invisible forever. Tuning it is expected.

## Privacy — the hardest rule here

The root [AGENTS.md](../AGENTS.md) says these pages describe **buildings, not
the people in them**, and news is where that rule is under constant pressure,
because a news story is a story about people almost by definition.

- **Take the building, leave the person.** "The building sold for $8.6 million"
  — yes. "The tech investor who bought it" — no, unless the buyer is a company
  or a firm.
- **Tenants, residents, owners, victims, the accused, the quoted: never.** Not
  their names, not their apartment numbers, not a description that identifies
  them. An eviction is a fact about a building; the six households fighting it
  are not the page's business.
- **Architects, builders, developers and named firms may be named**, per the
  root rules — they are the historical record of how the building got there.
  A private individual who developed their own building is not a `developer`
  for this purpose.
- **A story about a person that mentions a building is not a building story.**
  An obituary that names the tower someone developed belongs on no page.
- A death, an arrest, a crime at an address: the building's page records what
  happened to the *building*. It is not a crime blotter, and it never names or
  describes the people involved.
- **A headline that names a private individual cannot go on a page.** We no
  longer write the entry, so there is no rewriting your way out of it: if the
  headline names someone who is not an architect, builder, developer or firm,
  decline the story.

## What an entry is

A news entry on the timeline is **the article's headline, the outlet, and the
date** — and nothing else. It reaches a page as an entry in `historical_record`,
the same key a newspaper fact from 1901 uses, and renders as one item on the
page's single timeline, in date order among the permits.

**The page does not restate the story in its own words.** An earlier version of
this module wrote a sentence of fact under each headline; it read as commentary,
it duplicated what the headline already said, and it put us in the business of
summarizing other people's reporting. The headline is the entry. A reader who
wants the story follows the link, which is the whole point of carrying it.

**But the entry is not all a story is worth.** What the article establishes
about the building goes into the page's own structured fields, where it is
stated as a fact and attributed from the Sources footer like any other — the
same shape a fact from an 1895 newspaper takes. A run that files the headline
and drops the architect has thrown away the part of the story a page is for.

The fields are `building.name`, `building.former_name`, `building.architect`,
`building.builder`, `building.developer` and `building.completed`; the article's
citation is already in `sources`, because the entry put it there.

This is not the banned sentence coming back under another name. The difference
is shape, and it is the whole distinction: a named field holding a name is a
fact the page states, and a paragraph under a headline is us summarizing
someone else's reporting.

- **Attribution belongs in the footer, never in the value.** `"architect":
  "OMA"`, never `"OMA, according to SF YIMBY"`.
- **The `building` block describes the building that stands there.** A story
  about a *proposal* names the team for a building that does not exist. A
  proposal or a permit filing leaves its team in the items file's `extra` and
  puts nothing in `building` — the headline entry is what carries that news.
  The same goes for a conversion designed but not yet built.
- **Only what the article states plainly, about this building.** Not the
  neighbouring building it describes on the way past, not what the reporter
  expects to happen, not a name that appears only in a rendering's caption or
  the outlet's own tags.
- **Never overwrite the assessor with the article.** On a newly finished
  building the two routinely disagree, because the roll lags by years. Set
  `building.completed` and record the disagreement in
  `building.completed_conflict` or `unknowns`. The roll's own year stays where
  it is.
- **Enriching an existing page is editing someone else's work.** Fill a field
  that is empty; do not revise one a person or another source already filled.
  An article that contradicts a field already on the page is an `unknowns`
  line, not an edit.
- **One event, one entry, and the entry it collides with is usually already
  published.** Two outlets on one morning is the easy case; a filing written up
  again a week later is the one that gets through, because the earlier entry
  went up in an earlier run and nothing in today's queue argues with it. Read
  what the page already carries before writing to it — `read.py` prints it — and
  decline the second account, naming in its note the entry that carries the
  event.
- **Never edit a headline** — not to trim it, not to fix its capitalization,
  not to drop the outlet's brand from the end. A quoted headline that has been
  altered is no longer a citation. If a headline is unusable, the entry is
  unusable; decline it.
- **No page yet? Seed it.** Most news addresses are in this state. Seeding is a
  stage of this pipeline, not a question to put to a human.

The JSON and the markup an entry becomes, the manifest traps, and the rest of
the publishing rules are in [PIPELINE.md → Rules that catch publishers
out](PIPELINE.md#rules-that-catch-publishers-out).

## The homepage carries the newest six

A story that reaches a page reaches the homepage too — `.place-cards.news-cards`
in the root [index.html](../index.html) holds the six most recent news entries
on the site, newest first.

**An entry is not published until its card is in.** The pages this module writes
are mostly pages nobody has a reason to visit yet, on streets the site had never
heard of that morning; the homepage is the only thing that puts a day's news
where a reader will actually meet it. A run that published an entry and left the
grid alone left the job half done.

Six, ordered by the entry's date, one card per page, and every rule above
applies to the card unchanged. **The `.place-cards` grid below it is not this
module's** — featured addresses turn over by hand on the root
[AGENTS.md](../AGENTS.md)'s criteria; never move a card between the two. The
card's markup and the rest of the rules are in [PIPELINE.md → The homepage
grid](PIPELINE.md#the-homepage-grid).

## Being a good citizen

- **The user agent says who we are** (`know-this-place-news/1.0` with the site
  URL) and every run rate-limits itself.
- **robots.txt is honoured, and a feed that forbids automated access is not
  polled.** [feeds.json](feeds.json) records `access: needs-human` for
  `sf-business-times` for exactly that reason. Changing that flag is a human's
  call, not an agent's.
- **We link back, always.** Every entry on a page names the outlet, links the
  article, and cites it in the footer — the outlet's name *is* the link. Taking
  a headline and burying where it came from is the one thing that would make
  this module a bad citizen. That is the deal.
- **Never commit the article text.** The queue file keeps titles, links and
  reasons; the syndicated body stays in memory.

## Amending this module

Same rule as the research module: **it is meant to change.** The screen's word
lists, the feed register, the stage boundaries, this file — all of it is yours
to improve when the work fights the structure. Update
[README.md](README.md), this file and [PIPELINE.md](PIPELINE.md) in the same
commit, record *why* in the commit message, and leave the module easier to use
than you found it.

Two things need a human: **adding or un-blocking a feed** (it is a relationship
with a publisher, and `access: needs-human` exists for that), and **anything
that changes what a page looks like** — that is the root AGENTS.md's territory.

**Keeping the homepage's news grid current is not one of them** — the card's
shape is settled, and a run that publishes an entry maintains the grid without
asking. Changing what that card *is* still needs a human.

**Seeding a parcel is not one of them.** It was, and the rule cost the module
its whole point: nearly every address in the news has no page, so a pipeline
that could only edit existing pages spent its days filing facts where nobody
would read them. The guards that make this safe are the ones already in place —
the seeder creates only pages that don't exist, refuses parcels the site may not
document, and writes nothing but city data — and every run still arrives as one
PR a human merges.
