# Findings

The chain of custody for every fact this module produces. One file per **batch**
of one source:

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

An entry records where a fact came from, which parcel it names, and which PR put
it on a page — so nobody ever has to re-read the corpus to know what happened to
it. **An entry is never deleted once written:** an `unresolved` or `rejected`
finding is a record that the haystack was searched *there*, which is worth almost
as much as a hit.

One run normally writes all of it in one pass. The three parts are still
separable, because a run that has to stop early stops between them:

| step | writes |
|---|---|
| read it | the entry: date, address as written, kind, description, citation, `raw` evidence |
| place it | `resolution` — a parcel and the method that proved it, or why it can't be resolved |
| publish it | `publish` — the PR that put it on a page, or why it was declined |

## Rules

- **`coverage` is filled in even when nothing was found.** "Read 1,200 pages,
  found none" is a result, and it stops the next run re-reading them.
- **Every resolved entry gets a `publish` decision, in the same commit that
  edits the pages.** An unmarked entry is indistinguishable from unstarted work
  and will be re-published by the next run. `check.py` fails the run if a file
  has published entries and resolved ones with nothing recorded — this rule
  exists because PR #114 skipped it and closing the loop cost a full
  verification pass over 425 entries.
- **There is no file-level status.** A file's state is what its entries say, and
  `check.py --stats` derives it. A duplicated status eventually disagrees with
  itself, which is exactly how PR #114 went unnoticed.
- **Never edit an entry to make it look better.** Correct a mistake, yes — and
  say so in the entry's `note`. Softening a hedge or sharpening a date is how a
  chain of custody dies.
- **`raw.text` never reaches a page.** It is evidence for placing and checking:
  the shortest span that justifies the extraction, not a quotation to publish.
- **Findings are committed; corpora are not.** If a fact only exists in
  `research/corpora/`, it isn't a fact yet.
- **The site is the publication, this is the workshop.** No findings JSON under
  `san-francisco/`, and nothing here is linked from a page.

## Naming ids

`<batch>-<nnnn>`, zero-padded, in the order found: `sn85066387-1895-0001`.
Unique within the file; `check.py` enforces it. Ids are referenced from issues
and PR bodies, so don't renumber a file after it has been handed off.
