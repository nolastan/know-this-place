# Issue templates

An issue is how a run hands off what it couldn't finish, and how it asks a
human for the one thing it can't do itself. **Prefer finishing over filing** —
the point of a run is to leave less behind, not to fan work out. Full rules:
[../AGENTS.md](../AGENTS.md) → "Filing work".

- **Title:** `research(<source-id>): <specific thing>`
- **Labels:** `research`, plus `needs-human` when it is blocked on a person.
  That is the whole label set. Older issues carry per-stage labels
  (`research:extract` and friends) from when a stage was the unit of work —
  they're harmless; read the title, not the label.
- **Body:** always states the source id, the input, and the definition of done.
  Search open issues for the source id before filing.
- End any comment or issue body you post on GitHub with the attribution footer
  your harness requires.

---

## A run someone can finish

```markdown
**Source id:** `<id>` · **Dossier:** research/sources/<id>.md
**Batch:** <the citable unit: one report, a year of a paper, a volume, a decade>
**Input:** <corpus path, or the URL and how to fetch it>
**Known traps:** <renumbering, OCR digits, metes and bounds, advertiser addresses>
**Expect:** a low hit rate. Read the whole batch; report the yield as counts.

**Definition of done:** the batch taken end to end —
`research/findings/<id>/<batch>.json` written and resolved, the resolved facts
published (by hand or via a manifest) with every entry marked `published` with
its PR or `declined` with a reason, the dossier's coverage note and `Verified:`
line updated, and `python3 research/tools/check.py` plus `python3
scripts/validate.py` clean.

Runbook: `research/RUNBOOK.md`
```

Trim it where a step doesn't apply — a source read live off the web has nothing
to fetch, a lead has no findings file yet. Don't split it into one issue per
step; that is the pattern this module moved away from.

## `needs-human` — blocked on a person

```markdown
**Source id:** `<id>`
**Blocked on:** <paywall | login | licensing terms | a library visit | a schema
or presentation decision>
**What was tried:** <specifics>
**What would unblock it:** <the smallest thing a person could do>

Nothing here is a workaround to route around — a source that forbids automated
access stays blocked until a person decides.
```
