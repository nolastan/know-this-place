# Know This Place

A map-less (for now), crowd-editable encyclopedia of the built environment —
one rich, Wikipedia-style page per building, starting with the Castro / Eureka
Valley neighborhood of San Francisco. Live at **https://knowthis.place**.

## How it works

There is deliberately **no CMS, no database, no build framework**:

- Content is a geographic tree of directories. Each address holds `data.json`
  (the single source of truth — structured facts with citations, plus any prose
  in a `narrative` field), `assets/` (openly licensed media), and `index.html`
  (the generated page). Keeping facts and prose in one file means the two can't
  drift into conflict.
- `index.html` is a **build artifact**, not a template render at request time.
  Pages are composed from a shared **design system** — a CSS component library
  ([shared/site.css](shared/site.css)) of stat tiles, a visual timeline, charts,
  and icons, plus a tiny progressive-enhancement layer
  ([shared/site.js](shared/site.js): web components for the Street View still,
  the Mapbox locator map, and chart tooltips). The JS only *enhances* — every
  page renders completely from its HTML alone, so pages stay static and
  crawlable.
  Consistency is enforced by a small contract checked in CI — see
  [shared/AGENTS.md](shared/AGENTS.md) and [scripts/validate.py](scripts/validate.py).
- **A page is seeded once, then edited by hand forever after.**
  [scripts/seed_pages.py](scripts/seed_pages.py) joins the DataSF datasets and
  writes the first `data.json` + `index.html` for every parcel that
  has no page yet. It never returns to a page it has written — a second run
  creates nothing. Everything after that first draft (corrections, research, a
  building's story, reader feedback) is a person or an agent editing the page
  directly.
- **Agents do the work a CMS would.** Rules live in `AGENTS.md` files through
  the tree; the live city APIs are cataloged in
  [DATA-SOURCES.md](DATA-SOURCES.md).
- **Finding things to say is a separate job from saying them.** Newspaper
  archives, books, newsletters and survey PDFs — the sources that make a page
  worth landing on — are mined in the [research module](research/README.md),
  which hands the site verified, sourced facts. Building the site and
  researching it are deliberately kept apart.
- **What happens at an address today is watched by the
  [news module](news/README.md).** It polls the city's newsrooms, keeps a
  cursor per feed, and puts the stories that name a building onto that
  building's timeline — the one thing an indexed news archive doesn't do for
  itself.

## The editing loop

1. Every page footer links to a prefilled **GitHub issue form**
   ([.github/ISSUE_TEMPLATE/page-feedback.yml](.github/ISSUE_TEMPLATE/page-feedback.yml)).
   Readers describe a change in plain words; the form carries the page path.
2. The issue triggers **Claude Code in GitHub Actions**
   ([.github/workflows/feedback-agent.yml](.github/workflows/feedback-agent.yml)),
   which verifies the claim against sources, updates `data.json` / `assets/`,
   edits `index.html` to match, and opens a **pull request** that closes the
   issue.
3. A human reviews and merges through normal GitHub PR review. Merging to
   `main` **is** the deploy — GitHub Pages serves the branch as-is.
4. A scheduled workflow ([.github/workflows/refresh.yml](.github/workflows/refresh.yml))
   periodically re-queries time-sensitive data (permits, assessments, news).

## Repo layout

```
AGENTS.md                     Agent constitution: rules for all edits
DATA-SOURCES.md               Catalog of live city APIs agents draw from
index.html                    Site homepage
san-francisco/
  castro/
    AGENTS.md                 Neighborhood-specific guidance
    <street-slug>/<number>/   One directory per building (see AGENTS.md)
shared/
  AGENTS.md                   The HTML page contract + design system
  site.css                    The only stylesheet (component library)
  site.js                     Enhancement layer (progressive web components)
  site-config.json            Site URL, repo URL, Maps embed key,
                              Mapbox token
  addresses.geojson           Derived index of every address + its
                              coordinates — the homepage map's dots
research/
  AGENTS.md                   Research rulebook: the run and its rules
  RUNBOOK.md                  The procedure for a run, step by step
  SOURCES.md                  Register of every source mined, and leads
  sources/<id>.md             One dossier per source: access, cautions,
                              coverage log
  findings/                   The chain of custody, one file per batch
  schema/                     The findings JSON schema + a worked example
  manifests/                  Parcel lists produced here, seeded by the script
  tools/check.py              Research consistency checks (stdlib only)
news/
  AGENTS.md                   News rulebook: cursors, the screen, privacy
  feeds.json                  Register of every feed, and how each misbehaves
  state/cursors.json          What each feed has been considered up to
  queue/<date>.json           One poll run: what to read, what was skipped, why
  items/<feed>/*.json         Findings files — research schema, research resolver
  tools/poll.py               Fetch, screen, queue, advance the cursors
  tools/read.py               Read queued articles; report the addresses in them
scripts/
  seed_pages.py               Writes the first draft of pages that don't
                              exist yet, from the DataSF APIs
  permit_redactions.json      Names stripped from permit text before it's saved
  validate.py                 CI contract checks (stdlib only)
  build_sitemap.py            Regenerates sitemap.xml
  build_map_index.py          Regenerates shared/addresses.geojson
.github/
  ISSUE_TEMPLATE/page-feedback.yml
  workflows/{feedback-agent,refresh,validate}.yml
```

## Setup checklist (Phase 0)

- [ ] Push to GitHub; confirm `repo_url` in [shared/site-config.json](shared/site-config.json)
- [ ] Settings → Pages → deploy from branch `main`, root; custom domain `knowthis.place`
- [ ] DNS: apex A/ALIAS records → GitHub Pages, per GitHub docs (CNAME file is committed)
- [ ] Add `ANTHROPIC_API_KEY` **Actions** secret; install the Claude GitHub App for this repo
- [ ] Settings → Actions → General → check **"Allow GitHub Actions to create and
      approve pull requests"** (off by default; without it the agent can't open PRs)
- [ ] **Create the `page-feedback` label** (Issues → Labels → New label). GitHub
      silently ignores labels an issue form references but that don't exist, which
      leaves feedback issues unlabeled and the agent workflow skipped.
- [ ] Branch protection on `main`: require PR review (you)
- [ ] Create a Google Maps **Embed API** key, referrer-locked to `knowthis.place`,
      and put it in `shared/site-config.json`
- [ ] Create a Mapbox **public token** (`pk.…`) for the homepage map and the
      per-page locator maps, URL-restricted to `knowthis.place` and
      `http://localhost:8517`, and put it in `shared/site-config.json` as
      `mapbox_token`. Address pages request one Static Images call per view, so
      watch the account's monthly request count as coverage grows
- [ ] Verify each endpoint in [DATA-SOURCES.md](DATA-SOURCES.md) with a live
      query and fill in its `Verified:` date
- [ ] Create the two labels the research module files issues against:
      `research` and `needs-human` (same trap as `page-feedback` — GitHub
      silently drops labels that don't exist). Older issues also carry
      per-stage labels (`research:extract` and friends) from when a stage was
      the unit of work; the module no longer files them.

## Seeding a neighborhood

```bash
python3 scripts/seed_pages.py plan --neighborhood "Castro/Upper Market"
python3 scripts/seed_pages.py seed --neighborhood "Castro/Upper Market" \
                                   --city san-francisco --area castro
python3 scripts/build_sitemap.py
python3 scripts/build_map_index.py
python3 scripts/validate.py
```

`plan` reports what would be written and why parcels are skipped; `seed` writes
the new pages and rebuilds the street hubs. `seed` only ever creates — it skips
any address that already has a page, so re-running it is safe and is a no-op
unless new parcels have appeared. Raw dataset rows are cached in
`.cache/` (gitignored) and each fetch resumes where it left off, so an
interrupted run is cheap to restart. `--neighborhood` takes the SF Planning
analysis-neighborhood name as it appears in the datasets.

## Researching

```bash
python3 research/tools/check.py --stats
```

The [research module](research/README.md) is where sources are found, mined and
turned into citable facts. It runs on files rather than conversations — a
register, a dossier per source, structured findings, and GitHub issues — so a
scan that takes six sessions across three agents doesn't lose its place. Start
at [research/AGENTS.md](research/AGENTS.md).

The bias is toward sources search engines can't see: newspaper OCR, out-of-print
books, neighborhood newsletters, PDF survey reports. A pass that reads a whole
book and yields four citable facts is a good pass.

## Watching the news

```bash
python3 news/tools/poll.py poll                 # every open feed
python3 news/tools/poll.py status               # where the cursors stand
python3 news/tools/read.py news/queue/<date>.json
```

The [news module](news/README.md) runs daily in CI
([.github/workflows/news.yml](.github/workflows/news.yml)) and asks a different
question from research: not *what has never been written about this address*,
but *what was written about it this week*. Nine feeds, a cursor apiece, a cheap
screen that throws out the Oakland stories and the ones that could not be about
a building, and a reader's judgement on the rest. A handful of buildings a day
survive that, and most of them have no page yet — 10,828 pages is a small slice
of the city — so the module seeds the parcel and puts the story on the page it
just made. Start at [news/AGENTS.md](news/AGENTS.md).

## Running the agent locally

Any Claude Code session in this repo picks up `AGENTS.md` automatically. Use an
agent for the work a script can't do — verifying a reader's feedback,
researching a building's history, writing the prose for a page that has a story
— not for seeding pages from city data.
