# Extractor — messy source in, structured findings out

**Mission:** read the corpus and produce one **findings file** of dated,
numbered, citable facts. This is the stage the whole module exists for, and it
is the one where a low hit rate is normal.

## Input

A `research:extract` issue naming a source id and a batch, and material under
`../corpora/<source-id>/`.

## Output

`../findings/<source-id>/<batch>.json`, valid against
[../schema/finding.schema.json](../schema/finding.schema.json), with:

- `coverage` — what you read, counted. Pages, issues, rows, sections.
- one entry per candidate fact, each with `resolution.status: "unresolved"`.

Then: `python3 research/tools/check.py`, a dossier update, and a
`research:resolve` issue.

## Rules

- **Read the whole batch.** Not a sample, not until you have "enough."
  Report the yield as counts, in `coverage` and in the issue you close.
- **One entry per fact, not per passage.** A single classified ad that gives a
  number, a date and a room count is one finding with those fields — not three.
- **Address as written, always.** `address_as_written` keeps the source's own
  words ("1311 Alabama street", "Howard st. bet. 20th and 21st"). Parse into
  `street_number` / `street_name` / `street_type` only when the source is
  unambiguous, and never "fix" a number you think is an OCR error — record it
  as written and let the resolver judge.
- **Keep the check material.** Cross streets, lot dimensions, block faces,
  neighbouring numbers: these are what the resolver uses to confirm a match.
  Drop them and the finding usually dies at the next stage.
- **Every entry carries its citation locator** — the file path in the corpus
  *and* the public citation URL/label a page would print. A finding you can't
  cite is not a finding.
- **Quote sparingly.** `raw.text` holds the shortest span that justifies the
  extraction. It exists for the resolver and the auditor; it never reaches a
  page.
- **Don't resolve, don't publish, don't tidy history.** Not your stage. Leave
  `resolution` unresolved and `publish.status` pending.
- **People:** take buildings, contractors, architects and named firms. Leave
  residents, occupants and owners out — at extraction time, not later. See
  "Privacy — hard limits" in the root [AGENTS.md](../../AGENTS.md).
- **Zero findings is a valid outcome.** Write the file with an empty
  `findings` array and a truthful `coverage` block. That result stops the next
  agent from re-reading the same haystack, which is worth exactly as much as a
  hit.

## Batching

Pick a batch that fits one session and maps to a citable unit — a year of a
paper, a volume of a journal, one report, one block of a dataset. Name the file
after it (`sn85066387-1895.json`, `japantown-hcs.json`). If the batch turns out
too big, finish what you can, record it honestly in `coverage`, and file an
issue for the remainder naming exactly where you stopped.

## Done when

The findings file validates, the dossier's coverage note and `Verified:` line
name what was read, and a `research:resolve` issue points at the file.
