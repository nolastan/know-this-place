# Findings

The handoff between pipeline stages. One file per **batch** of one source:

```
research/findings/<source-id>/<batch>.json
```

The directory name must be a registered source id from
[../SOURCES.md](../SOURCES.md); the batch name should be the citable unit that
was read (`sn85066387-1895.json`, `japantown-hcs.json`, `vol-31-no-2.json`).

Shape and every field: [../schema/finding.schema.json](../schema/finding.schema.json).
A worked example: [../schema/example-findings.json](../schema/example-findings.json).
Validate with `python3 research/tools/check.py`.

## Why the file exists

Three different agents touch the same entries, usually in three different
sessions:

| stage | writes |
|---|---|
| [extractor](../roles/extractor.md) | the entry: date, address as written, kind, description, citation, `raw` evidence |
| [resolver](../roles/resolver.md) | `resolution` — a parcel and the method that proved it, or why it can't be resolved |
| [publisher](../roles/publisher.md) | `publish` — the PR that put it on a page, or why it was declined |

Nobody has to re-read the corpus to continue. That is the whole point, and it
is why an entry is never deleted once written: an `unresolved` or `rejected`
finding is a record that the haystack was searched *there*, which is worth
almost as much as a hit.

## Rules

- **`coverage` is filled in even when nothing was found.** "Read 1,200 pages,
  found none" is a result, and it stops the next agent re-reading them.
- **Never edit an entry to make it look better.** Correct a mistake, yes —
  and say so in the entry's `note`. Softening a hedge or sharpening a date is
  how a chain of custody dies.
- **`raw.text` never reaches a page.** It is evidence for the resolver and the
  auditor: the shortest span that justifies the extraction, not a quotation to
  publish.
- **Findings are committed; corpora are not.** If a fact only exists in
  `research/corpora/`, it isn't a fact yet.
- **The site is the publication, this is the workshop.** No findings JSON
  under `san-francisco/`, and nothing here is linked from a page.

## Naming ids

`<batch>-<nnnn>`, zero-padded, in the order found: `sn85066387-1895-0001`.
Unique within the file; `check.py` enforces it. Ids are referenced from issues
and PR bodies, so don't renumber a file after it has been handed off.
