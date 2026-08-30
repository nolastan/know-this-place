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

## Cursors: what "already considered" means

Every feed has a cursor in [state/cursors.json](state/cursors.json), and the
rule it encodes is the module's memory:

> **An item is considered once. Considered means a verdict was recorded — read
> *or* skipped — not that anything was published.**

- **Identity is the item's id**, not its date. Feeds re-date stories they edit,
  and a date cursor hands the same story back every run.
- **A cursor remembers the last few hundred ids** it has seen. A feed shows ten
  to thirty items, so that is many runs of overlap.
- **A feed's first run has no cursor**, so it takes only the last two weeks
  (`--backfill-days`). Without that, a first run queues a feed's whole backfill.
- **A failed fetch does not move a cursor.** One dead feed must not silently
  swallow a day of another's stories, and the run reports it.
- **Cursors move on a skip.** That is the point of recording the reason: a skip
  is a decision the module stands behind, not an item it never got to.

`poll.py status` prints where every cursor stands.

**The queue file is the durable worklist, and the cursor is not.** Polling
advances the cursor for everything it screened, so a story only survives in
`queue/<date>.json` — delete that file when it has been drained, and leave it
alone when it hasn't. An unfinished queue is picked up by the next pass;
`poll.py status` lists every queue file still waiting. This is the one place
where deleting a file is the right way to record that work is done.

**A cursor is only true on the branch it was advanced on.** Nothing this module
produces reaches `main` without a human merging it, which means the cursors,
the queue and the items files live on a branch until then — and a run that
started from `main` while a previous run's PR sat unmerged would re-fetch,
re-screen and re-read everything that PR had already considered. So the daily
workflow looks for an open PR whose branch begins `news/` and **continues on
that branch**, merging `main` in to stay current. One PR accumulates until a
human merges it; only then does the next run start fresh.

That is why the workflow commits *every* run, including a run that found
nothing publishable. An empty-handed run still advanced the cursors, and if it
pushes nothing, the next run does its work again.

The cost of the alternative is worth knowing, because it is not just wasted
tokens: the feeds carry between one and five days. A PR left unmerged for a
week, with the cursors stranded on it, would let the stories it had queued age
out of the feeds entirely — lost rather than merely repeated.

## The screen

`poll.py` gives every new item a verdict from its headline, summary and tags
alone. It is cheap, it is wrong sometimes, and it is **deliberately asymmetric**:
it skips only on a clear signal and queues on doubt, because a queued story
costs a glance and a wrongly skipped one is invisible forever.

**San Francisco only.** Most of these outlets cover the whole Bay Area, and half
their stories are about somewhere else.

- The **headline** decides the geography. A feed that tags every item "San
  Francisco" — Hoodline tags a Redwood City arrest that way — must not let its
  tag outvote the headline's own subject.
- **"South San Francisco" is a different city**, and so are "San Francisco Bay
  Area", "the San Francisco Peninsula" and the Giants. Strip those before
  looking for the city.
- **Richmond is not in the elsewhere list.** The Richmond District is San
  Francisco and Richmond is the East Bay; dropping every "Richmond" would cost
  a whole district's coverage. Let the other signals decide.
- A story on a **bay-area** feed that names an address but not the city is
  queued anyway, with the doubt written into the reason. Confirming the city is
  the reader's first job.

**Might it name an address?** Three strengths, in order:

1. **A street address** — `2918 Mission Street`, or the bare `400 Divisadero`
   the city writes constantly. The bare form is only trusted on a street the
   site already has pages on, and a four-digit number that runs into another
   capitalized word is a year, not an address ("2026 Mission Local reported").
2. **A street the site has pages on**, without a number.
3. **The shape of the story** — opens, closes, sold, leased, evicted, burned,
   landmarked, demolished. These are the stories that carry an address in the
   body even when the headline names only the business.

A subject that never carries a street number — a ballgame, an election, a
recipe, a weather forecast — **outranks the third of those**, and only the
third. A headline with a real address in it is queued no matter what else it is
about.

**Tuning it is expected.** `poll.py screen "<a headline>"` explains a verdict.
When a skip turns out to have been wrong, fix the table it came from and say so
in the commit — the lists in `poll.py` are the module's accumulated judgement,
not a fixed dictionary. `read.py <queue> --skipped` re-reads a run's skips and
measures what they cost; do that when you change the screen.

## Reading an article

`read.py` fetches each queued story, strips it to text, and reports every
address in it with the page it belongs to. What it prints is **evidence, not
copy.**

- **The headline is the only text of theirs we publish.** These outlets are
  alive and paying reporters, and a headline carried verbatim with the outlet
  named and linked is a citation. A summary of the article is not: never
  reproduce a sentence, a paragraph's structure, or the shape of the reporting,
  and never write our own precis of it onto a page. What you write in the items
  file is a note for the next reader of that file, not copy.
- **An address is not a fact.** "The mayor spoke at 1 Dr Carlton B Goodlett
  Place" names an address and says nothing about the building. Apply the
  ten-year test above.
- **A building with no page counts exactly as much as one with a page.**
  `read.py` says which addresses already have pages, and that is a convenience,
  not a ranking: 10,828 pages is a small slice of the city, so ranking by it
  would confine the module to the slice of San Francisco that happens to be
  documented already. The story decides, and the page is created to receive it —
  see "No page yet? Seed it" below. `--only-pages` narrows a read when you are
  triaging a long backlog by hand; it is not the default and it is not the
  order to work in.
- **A paywall that cuts off after the lede is not a source you can extract
  from.** Record what you could read and mark the item unpublished with the
  reason. The Registry and the Chronicle both do this.
- **Some article pages refuse a fetcher (Hoodline answers 403) while their feed
  syndicates the whole story.** `read.py` falls back to the feed's own copy.
  That text stays in memory: source text is never committed, per
  research/AGENTS.md → "Corpora on disk".
- **A feed's title is not always the headline, and its link is not always the
  article.** A social feed carries a post *about* a story: the sf-chronicle feed
  is a Bluesky account, so its title is a teaser sentence and its link a bit.ly
  shortlink. Neither can be published — the headline is the only text of theirs
  a page carries, and a shortlink is not a citation anyone can check. So
  `read.py` reads the article's own `og:title` and canonical URL and prints them
  as `headline:` and `article:` **whenever they differ from what the feed said**;
  build the citation from those two lines when they appear, and from the feed
  when they do not. A run over well-behaved feeds prints neither.

  This cost the module three findings once. The run of 2026-08-28 extracted
  them, resolved them, and then could not publish any of them, because it had a
  teaser where the headline goes; they sat pending for two days until a run read
  the headlines by hand. Nothing is expected to need that again.
- **Never let a story's own words about a person into the repo.** See below.

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
- **A story about a person that mentions a building is not a building story.**
  An obituary that names the tower someone developed belongs on no page.
- A death, an arrest, a crime at an address: the building's page records what
  happened to the *building*. It is not a crime blotter, and it never names or
  describes the people involved.

## Putting it on the page

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
  "OMA"`, never `"OMA, according to SF YIMBY"`. research/AGENTS.md → "an
  ordinary fact about a building must be stated as a fact, with the attribution
  left to the Sources footer".
- **The `building` block describes the building that stands there.** A story
  about a *proposal* names the team for a building that does not exist, and
  writing its architect onto the page tells a reader that a surface parking lot
  was designed by someone. A proposal or a permit filing leaves its team in the
  items file's `extra` and puts nothing in `building` — the headline entry is
  what carries that news. The same goes for a conversion designed but not yet
  built: the architect of the alteration is not the architect of the building.
- **Only what the article states plainly, about this building.** Not the
  neighbouring building it describes on the way past, not what the reporter
  expects to happen, not a name that appears only in a rendering's caption or
  the outlet's own tags.
- **The privacy rule binds hardest here.** Architects, builders, developers and
  named firms may be named — that is what these fields are for. Owners, buyers,
  tenants and residents may not, and a private individual who developed their
  own building is not a `developer` for this purpose.
- **Never overwrite the assessor with the article.** On a newly finished
  building the two routinely disagree, because the roll lags by years. Set
  `building.completed` and record the disagreement in
  `building.completed_conflict` or `unknowns` — both render into the same note.
  The roll's own year stays where it is.
- **Enriching an existing page is editing someone else's work.** Fill a field
  that is empty; do not revise one a person or another source already filled.
  An article that contradicts a field already on the page is an `unknowns`
  line, not an edit.

```json
{ "date": "2026-08-14",
  "kind": "construction",
  "headline": "Mission Laundromat Site That Fueled S.F. Housing Wars Finally Rises as Apartments",
  "outlet": "Hoodline",
  "url": "https://hoodline.com/2026/08/…",
  "source": "hoodline-2026-08-14" }
```

with the matching citation in `sources`:

```json
{ "id": "hoodline-2026-08-14",
  "name": "Hoodline, “Mission Laundromat Site That Fueled S.F. Housing Wars Finally Rises as Apartments,” 14 August 2026",
  "query": "https://hoodline.com/2026/08/…",
  "retrieved": "2026-08-16" }
```

`python3 scripts/seed_pages.py render <path to the page>` then regenerates
`index.html`, where the entry becomes one `.vtl-item` — the headline in
italics, the outlet as the link, no meta row. You write the JSON above and
nothing else; the markup here is what to expect, not what to type:

```html
<li class="vtl-item">
  <div class="vtl-date">Aug 14, 2026</div>
  <p class="vtl-desc"><em>Mission Laundromat Site That Fueled S.F. Housing Wars Finally Rises as Apartments</em> — <a href="https://hoodline.com/2026/08/…">Hoodline</a></p>
</li>
```

Rules that catch people out:

- **The headline goes up verbatim, so read it as something we are publishing.**
  It is the outlet's wording, quoted as a citation, which is what makes it fair
  to reproduce — but it is now the only text on the page from this story, and
  every rule below applies to it rather than to a sentence we wrote.
- **A headline that names a private individual cannot go on a page.** Eviction,
  arrest, crime and death stories routinely name people in the headline, and
  the root [AGENTS.md](../AGENTS.md) forbids naming residents, tenants, owners
  and occupants. There is no rewriting your way out of it, because we no longer
  write the entry: if the headline names someone who is not an architect,
  builder, developer or firm, decline the story. `publish.status: declined`
  with the reason.
- **Never edit a headline** — not to trim it, not to fix its capitalization, not
  to drop the outlet's brand from the end. A quoted headline that has been
  altered is no longer a citation. If a headline is unusable, the entry is
  unusable; decline it.
- **One source id per article**, `<feed-id>-<YYYY-MM-DD>`, following the
  newspaper convention already on the site (`loc-sf-call-1901-04-06`). Two
  stories from one outlet on one page are two ids, suffixed `-2`.
- **The date is the event's date where the story gives one**, and the article's
  publication date otherwise. A store that opened on the Thursday is dated the
  Thursday, not the Friday it was written up.
- **The `description` in the items file stays.** It is the extractor's record of
  what the story actually said and why it earned an entry — evidence for the
  auditor, the thing a reviewer checks the headline against. It simply never
  reaches a page now.
- **No page yet? Seed it.** Most news addresses are in this state, and a fact
  parked in an items file waiting for a page nobody creates is a fact nobody
  reads. Seeding is a stage of this pipeline, not a question to put to a human:
  name the parcels in a manifest under `research/manifests/news-<batch>.json`,
  seed them, and put the entries on the pages in the same PR that extracted
  them.

  ```bash
  python3 research/tools/resolve_eas.py apply news/items/<feed>/<batch>.json
  python3 scripts/seed_pages.py seed-list --manifest research/manifests/news-<batch>.json
  python3 scripts/build_sitemap.py
  python3 scripts/build_map_index.py
  python3 scripts/validate.py
  ```

  Everything the seeder does elsewhere holds here — root
  [AGENTS.md](../AGENTS.md) → "Page lifecycle" is unchanged. It creates only
  pages that don't exist, it leaves every existing page alone, it rebuilds the
  street hubs it touched, and what it writes is a first draft whose every fact
  came from a DataSF API. Read a sample of the drafts before committing them,
  the same as any other seed.
- **The manifest's numbers must be derived the way the resolver derives them.**
  `resolve_eas.py` unions the addresses reached through a parcel's retired APNs,
  so a manifest built from the active APN alone can name the page at a different
  street number than the finding resolved to. The numbers and the lead are in
  the resolution's own `method` — "EAS puts 300, 330, 350, 360 BAY ST on that
  parcel, so … the lowest, 300" — so take them from there rather than from the
  number the story printed, and check the manifest's `apn`, `area` and
  `street_slug` against `resolution.apn` and `resolution.path`.
  `research/manifests/news-2026-08-16.json` is the worked example: 350 Bay
  Street resolves to a page at 300 Bay Street.
- **A parcel the seeder refuses is not a page to force.** It skips condominium
  units and parcels with no row on the current roll, and prints the reason for
  each. That is the site's rule about what may be a page, and it outranks the
  story: leave the finding at `publish.status: "pending"` with the seeder's
  reason in the note, and it stays in the items file as a fact with nowhere
  legitimate to go.
- **A seeded page's own data may contradict the story that prompted it.** The
  roll described 2740 McAllister as a one-storey house built 1900 five years
  after it was demolished. That is an `.unknowns` line, not something to
  quietly drop from either side. Keep such a note only while the page still
  shows the claim it contradicts — usually in the headline itself.
- **The page is only half of it.** The same headline goes on the homepage's
  news grid in the same PR — see "The homepage carries the newest six" below.
- `python3 scripts/validate.py` must pass — it asserts `index.html` is exactly
  what the renderer produces from `data.json`, so re-render before you commit.

## The homepage carries the newest six

A story that reaches a page reaches the homepage too. The root
[index.html](../index.html) opens on an **In the news** grid — the first
section under the map, above "Start here" — `.place-cards.news-cards`, holding
the six most recent news entries on the site, newest first.

**An entry is not published until its card is in.** The pages this module writes
are mostly pages nobody has a reason to visit yet, on streets the site had never
heard of that morning; the homepage is the only thing that puts a day's news
where a reader will actually meet it. A fact filed on a page nobody opens is the
failure this module exists to avoid, and it does not stop being that failure
because the fact is on a page rather than in an items file.

The card is the "Start here" card — picture, then address — with two lines hung
underneath it: the headline, verbatim, linking to the article, and the outlet
beneath that. The building is still what the card names first; the news is what
it says about it.

```html
<li>
  <a href="/san-francisco/mission/mission-street/2918/">
    <ktp-streetview location="37.750313,-122.418539" label="2918–2920 Mission Street">
      <figure class="media">
        <div class="media-empty">
          <span class="ic ic-pin"></span>
          <span>37.7503, −122.4185</span>
        </div>
      </figure>
    </ktp-streetview>
  </a>
  <a class="card-label" href="/san-francisco/mission/mission-street/2918/">2918–2920 Mission Street</a>
  <p class="card-news"><a href="https://hoodline.com/2026/08/…"><em>Mission Laundromat Site That Fueled S.F. Housing Wars Finally Rises as Apartments</em><span class="card-ext">&nbsp;<span class="ic ic-link" aria-hidden="true"></span></span></a><span class="card-outlet">Hoodline</span></p></li>
```

**Copy that `card-ext` wrapper exactly.** The `ic-link` glyph marks the headline
as the one link on the homepage that leaves the site, and an inline-block is a
line-break opportunity in its own right — a bare `&nbsp;` does not stop the
browser stranding the icon alone on a line of its own. The nowrap wrapper, with
no whitespace ahead of it, is what keeps the icon on the last word.

- **Six, and the newest are the six.** The new card goes on the top and the
  oldest comes off the bottom. Nothing generates this list — like the featured
  cards below it, it changes only because an agent changed it, and a run that
  published an entry and left the grid alone left the job half done.
- **Order by the entry's date** — the same date that put it on the timeline,
  which is the event's date and not the date of the run.
- **One card per page.** A second story on a building that already holds a card
  replaces that card; it does not earn the building a second one.
- **The address is the page's, the headline is the outlet's.** `location` is
  `coordinates` from `data.json` verbatim, the label is the page's address up to
  the comma (`2918–2920 Mission Street`), and the placeholder coordinates are
  four decimals with a real minus sign (−), matching the cards below.
- **Every rule in "Putting it on the page" applies here unchanged.** The
  headline is quoted verbatim and never edited, the outlet is named, and a
  headline that names a private individual is declined. A headline that cannot
  go on a page cannot go on the homepage — there is no lighter bar here because
  the homepage is the more public of the two.
- **The `.place-cards` grid below is not this module's.** Featured addresses are
  chosen on the root [AGENTS.md](../AGENTS.md)'s criteria — an early timeline,
  sources beyond the city's own — and turn over by hand. Two grids, two rules;
  never move a card between them, and never drop a featured card to make room
  for a news one.
- **A declined or pending item has no card**, the same as it has no entry. The
  grid is a view of what is on the pages, so anything in it can be checked
  against the page it names.

`python3 scripts/validate.py` covers the homepage like any other page, so run it
after editing the grid.

## Items files

`items/<feed-id>/<batch>.json`, where the batch is the run date. They are
[research findings files](../research/findings/README.md) — same schema, same
resolver, same rule that an entry is never deleted once written:

- `source_id` is the feed id; the directory name matches it.
- **`kind` describes the fact, not the source** — `sale`, `construction`,
  `development`, `occupancy`, `fire`, `eviction`, `designation`. A sale is a
  sale whether it came from The Registry this week or the Call in 1901, and the
  citation is what says where it came from. `kind: "news"` says nothing about
  what happened, and the timeline is a list of things that happened.
- `citation.label` names the outlet, the headline and the date; `citation.url`
  is the article.
- `raw.text` is the shortest span that justified the extraction. **It never
  reaches a page**, and it is the one place a source's own words may sit.
- **`resolution` belongs to the resolver; a refusal goes in `publish`.**
  `resolve_eas.py apply` rewrites the whole `resolution` object every time it
  runs, so a hand-written `rejected` there is silently replaced the next time
  anyone resolves the file. A decision *not* to put a fact on a page is
  `publish: {"status": "declined", "note": "…"}` — nothing else touches that
  field, and the note is where the judgement is recorded. Decline generously
  and delete nothing: a declined finding is the record that the story was read
  and considered.
- **`conflict` means the *address* is disputed, and nothing else.** The
  resolver reads that field as "this record states two addresses" and switches
  to its adjudication path, which prints archive language about a catalogue
  title and an archivist's note that has no meaning here. A story that
  disagrees with itself about a building's size or its acreage records that in
  `extra`, not in `conflict`.
- An item whose address has no page is a page to seed, not an item to shelve;
  the resolver's "the parcel is the publisher's to seed" note is addressed to
  this pipeline. Record the seeding in `publish.note`, naming the manifest, so
  the page's origin is auditable from the finding. An item that names no usable
  address is still written, `rejected`, with the reason — that is what stops it
  being read again.

Validate with `python3 news/tools/check.py`.

## Being a good citizen

- **The user agent says who we are** (`know-this-place-news/1.0` with the site
  URL) and every run rate-limits itself.
- **robots.txt is honoured, and a feed that forbids automated access is not
  polled.** [feeds.json](feeds.json) records `access: needs-human` for
  `sf-business-times` for exactly that reason: its host's robots.txt ends with
  a blanket disallow. Changing that flag is a human's call, not an agent's.
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
[README.md](README.md) and this file in the same commit, record *why* in the
commit message, and leave the module easier to use than you found it.

Two things need a human: **adding or un-blocking a feed** (it is a relationship
with a publisher, and `access: needs-human` exists for that), and **anything
that changes what a page looks like** — that is the root AGENTS.md's territory.

**Keeping the homepage's news grid current is not one of them** — the card's
shape is settled above, and a run that publishes an entry maintains the grid
without asking. Changing what that card *is* still needs a human, like any other
change to how a page looks.

**Seeding a parcel is not one of them.** It was, and the rule cost the module
its whole point: nearly every address in the news has no page, so a pipeline
that could only edit existing pages spent its days filing facts where nobody
would read them. The guards that make this safe are the ones already in place —
the seeder creates only pages that don't exist, refuses parcels the site may not
document, and writes nothing but city data — and every run still arrives as one
PR a human merges.
