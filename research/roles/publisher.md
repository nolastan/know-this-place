# Publisher — resolved findings onto pages

**Mission:** get verified facts onto the site without breaking a single rule of
the website's own contract. In this stage you are a **site agent**: the root
[AGENTS.md](../../AGENTS.md) and [shared/AGENTS.md](../../shared/AGENTS.md)
govern, and this file only says how research feeds them.

## Input

A findings file with entries at `resolution.status: "resolved"` and
`publish.status: "pending"`.

## Two routes

**1. The page exists (or should, and it's a handful).** Edit by hand.

- Add each fact to `data.json` — normally `historical_record` (one entry per
  dated fact: `date`, `kind`, `description`, `source`), and add the source to
  the page's `sources` array with the citation label from the dossier.
- Regenerate `index.html` from `data.json` in the same commit. Facts render as
  a timeline item, a spec row, a tag or a tile — **never as a new paragraph**,
  and never as a sentence about where the fact came from.
- A conflict flagged by the resolver goes in `.unknowns`, stated plainly and
  left unadjudicated.

**2. The source names many buildings with no pages.** Write a manifest.

- Put the parcels in `../manifests/<source-id>.json` (the shape is in the
  existing files there), then:

  ```bash
  python3 scripts/seed_pages.py seed-list --manifest research/manifests/<file>.json
  python3 scripts/build_sitemap.py
  python3 scripts/build_map_index.py
  python3 scripts/validate.py
  ```

- The seeder only creates pages that don't exist. Facts from the source still
  have to be hand-added to those pages afterwards — seeding is the scaffold,
  not the research.

## Rules that catch publishers out

- **A page is a designed data page, not an article.** Before you write a
  sentence, name the component that could carry the fact instead. Usually one
  can.
- **Never name the source in the page body.** "The newsletter says…", "a survey
  records…", "according to the archive" — all wrong. The Sources footer is the
  attribution. The one documented exception is
  [../sources/celebrity-residence-guides.md](../sources/celebrity-residence-guides.md),
  whose claims are attributed in the body precisely because they're weak.
- **Facts, not wording.** Re-express; never reproduce the source's sentences or
  their structure.
- **Privacy is not negotiable at publication time either.** Buildings,
  contractors, architects, firms, and historical figures already published with
  dates. Not residents, occupants or owners.
- **Don't restate what a component already shows**, and never open a permit
  timeline with prose.

## Close the loop

- Set `publish.status` to `"published"` (with the PR number) or `"declined"`
  (with a reason) on every entry you touched. An entry left `pending` will be
  re-published by the next agent.
- Update the dossier: what was published, from which batch.
- PR body: the pages touched, the sources consulted, and the pass's counts —
  read N, found M, resolved K, published J. Branch naming and PR conventions
  are in the root [AGENTS.md](../../AGENTS.md).
- Run `python3 scripts/validate.py` and `python3 research/tools/check.py`.

## Done when

The PR is open, every published entry is marked, and the findings file and the
site agree about what shipped.
