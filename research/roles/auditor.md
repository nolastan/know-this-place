# Auditor — check what shipped against what was found

**Mission:** make sure the chain from source to page survived every handoff.
Cheap to run, and the only thing standing between a long pipeline and a
confidently wrong encyclopedia.

## Input

A published batch: a findings file with `published` entries, and the pages the
publisher touched.

## What to check

1. **The fact on the page matches the finding**, and the finding matches
   `raw.text`. Drift usually appears as a date that gained precision it never
   had, or a hedge that got dropped.
2. **The citation resolves.** Open the URL, or confirm the issue/section
   reference is exact enough for a reader to find it. Broken or vague
   citations are the most common real defect.
3. **The address is still right.** Spot-check the resolver's `method` on a few
   entries, especially anything on a renumbered street.
4. **No people leaked** — residents, occupants or owners named in prose, a
   `hook`, a `narrative`, or a permit description.
5. **No source prose leaked** — sentences lifted or lightly paraphrased from
   the source, or a page body naming the archive it came from.
6. **The page still obeys the design contract** — facts in components, prose
   only where it earns its place, `python3 scripts/validate.py` clean.

## Output

- Corrections, as an ordinary site edit with a PR.
- The dossier's `Verified:` line updated with the date and what was checked.
- A `research:audit` issue for anything you can't fix in the session, or
  `needs-human` for a judgement call (a licensing question, a schema change, a
  conflict that needs a person to decide how to present).

## Sampling

Audit **every** entry for a source's first published batch — that is when
systematic errors are cheapest to catch. After that, a spot-check of a handful
per batch is enough, weighted toward resolved-by-inference addresses and
anything on a street the dossier flags as renumbered.
