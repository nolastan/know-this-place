# Know This Place

A map-less (for now), crowd-editable encyclopedia of the built environment —
one rich, Wikipedia-style page per building, starting with the Castro / Eureka
Valley neighborhood of San Francisco. Live at **https://knowthis.place**.

## How it works

There is deliberately **no CMS, no database, no build framework**:

- Content is a geographic tree of directories. Each address holds `index.md`
  (human-readable source), `data.json` (structured facts with citations),
  `assets/` (openly licensed media), and `index.html` (the generated page).
- `index.html` is a **build artifact authored by an AI agent**, not rendered
  from a template. Every page can have a bespoke structure suited to what is
  actually interesting about that place, composed from a shared **design
  system** — a CSS component library ([shared/site.css](shared/site.css)) of
  stat tiles, a visual timeline, charts, and icons, plus a tiny
  progressive-enhancement layer ([shared/site.js](shared/site.js): web
  components for click-to-load Street View and chart tooltips). The JS only
  *enhances* — every page renders completely from its HTML alone, so pages stay
  static and crawlable. Consistency is enforced by a small contract checked in
  CI — see [shared/AGENTS.md](shared/AGENTS.md) and [scripts/validate.py](scripts/validate.py).
- **Agents do the work a CMS would.** Rules live in `AGENTS.md` files through
  the tree; available data APIs are cataloged in [DATA-SOURCES.md](DATA-SOURCES.md).

## The editing loop

1. Every page footer links to a prefilled **GitHub issue form**
   ([.github/ISSUE_TEMPLATE/page-feedback.yml](.github/ISSUE_TEMPLATE/page-feedback.yml)).
   Readers describe a change in plain words; the form carries the page path.
2. The issue triggers **Claude Code in GitHub Actions**
   ([.github/workflows/feedback-agent.yml](.github/workflows/feedback-agent.yml)),
   which verifies the claim against sources, updates `index.md` / `data.json` /
   `assets/`, regenerates `index.html`, and opens a **pull request** that
   closes the issue.
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
- [ ] Add `ANTHROPIC_API_KEY` repo secret; install the Claude GitHub App for this repo
- [ ] Branch protection on `main`: require PR review (you)
- [ ] Create a Google Maps **Embed API** key, referrer-locked to `knowthis.place`,
      and put it in `shared/site-config.json`
- [ ] Verify each endpoint in [DATA-SOURCES.md](DATA-SOURCES.md) with a live
      query and fill in its `Verified:` date

## Running the agent locally

Any Claude Code session in this repo picks up `AGENTS.md` automatically. For a
seeding pass: "Create the page for <address> following AGENTS.md", then
`python3 scripts/validate.py` and `python3 scripts/build_sitemap.py` before
opening a PR.
