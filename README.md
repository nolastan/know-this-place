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
  ([shared/site.js](shared/site.js): web components for click-to-load Street
  View and chart tooltips). The JS only *enhances* — every page renders
  completely from its HTML alone, so pages stay static and crawlable.
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
  the tree; available data APIs are cataloged in [DATA-SOURCES.md](DATA-SOURCES.md).

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
DATA-SOURCES.md               Catalog of APIs agents draw from
index.html                    Site homepage
san-francisco/
  castro/
    AGENTS.md                 Neighborhood-specific guidance
    <street-slug>/<number>/   One directory per building (see AGENTS.md)
shared/
  AGENTS.md                   The HTML page contract + design system
  site.css                    The only stylesheet (component library)
  site.js                     Enhancement layer (progressive web components)
  site-config.json            Site URL, repo URL, Maps embed key
scripts/
  seed_pages.py               Writes the first draft of pages that don't
                              exist yet, from the DataSF APIs
  permit_redactions.json      Names stripped from permit text before it's saved
  validate.py                 CI contract checks (stdlib only)
  build_sitemap.py            Regenerates sitemap.xml
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
- [ ] Verify each endpoint in [DATA-SOURCES.md](DATA-SOURCES.md) with a live
      query and fill in its `Verified:` date

## Seeding a neighborhood

```bash
python3 scripts/seed_pages.py plan --neighborhood "Castro/Upper Market"
python3 scripts/seed_pages.py seed --neighborhood "Castro/Upper Market" \
                                   --city san-francisco --area castro
python3 scripts/build_sitemap.py
python3 scripts/validate.py
```

`plan` reports what would be written and why parcels are skipped; `seed` writes
the new pages and rebuilds the street hubs. `seed` only ever creates — it skips
any address that already has a page, so re-running it is safe and is a no-op
unless new parcels have appeared. Raw dataset rows are cached in
`.cache/` (gitignored) and each fetch resumes where it left off, so an
interrupted run is cheap to restart. `--neighborhood` takes the SF Planning
analysis-neighborhood name as it appears in the datasets.

## Running the agent locally

Any Claude Code session in this repo picks up `AGENTS.md` automatically. Use an
agent for the work a script can't do — verifying a reader's feedback,
researching a building's history, writing the prose for a page that has a story
— not for seeding pages from city data.
