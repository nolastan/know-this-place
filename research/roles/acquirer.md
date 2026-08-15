# Acquirer — get the material readable

**Mission:** turn a registered lead into something an extractor can actually
read, and write down how you did it so nobody repeats the archaeology.

## Input

A `research:acquire` issue naming a source id, or a dossier with status `lead`.

## Output

- Material under `../corpora/<source-id>/` (gitignored — never committed).
- A `state.json` in that directory recording what has been fetched.
- The dossier's **access** section, rewritten from guesswork into fact: the
  exact URL that serves the file, the tool that worked, the quirks.
- Status moved to `mining` in [../SOURCES.md](../SOURCES.md).
- A `research:extract` issue naming the first batch.

## Procedure

1. Read the dossier. Assume its access notes are a hypothesis.
2. Fetch a single item first and confirm it is what you think it is. Then plan
   batches — by year, by issue, by volume, by block — and record the plan.
3. Fetch politely: rate-limit, back off on failure (tens of seconds, not five),
   resume from `state.json` rather than restarting, and stop if you are being
   throttled. Honour `robots.txt` and terms of use.
4. Normalize just enough for the next stage: PDFs to text, one file per
   logical unit (issue, page, section), predictable filenames that map back to
   a citation. A file the extractor can't cite is a file it can't use.
5. Update the dossier — including everything that *didn't* work, which is
   usually the more valuable half.

## Traps this project has already hit

- **`WebFetch` returns nothing usable for many PDFs.** Fetch the bytes and
  extract text (`pdftotext`, `pypdf`); this is documented per source in the
  dossiers.
- **SF Planning serves some documents from an M-Files vault**, where the
  `SharedLinks.aspx` URL returns an HTML shell, not the PDF. The real file is
  at the REST path the page's own script names. Worked examples for the
  Dogpatch survey and the Glen Park evaluation are in
  [../sources/sf-context-statements.md](../sources/sf-context-statements.md).
- **Cite the form a reader can use, fetch the form that works.** Where those
  differ, the dossier records both and says which is which.
- **Drafts and finals coexist**, and the final sometimes still says DRAFT in
  its page headers. Take the file the adopting body listed; say in the dossier
  which file that is.
- **A per-read timeout never fires on a slow trickle.** Read against a
  wall-clock deadline. (The same lesson as the DataSF notes in
  [../../DATA-SOURCES.md](../../DATA-SOURCES.md).)

## Licensing

Downloading for analysis is not publishing. What may be published is **facts,
re-expressed** — never the source's sentences, never a scanned page committed
into `assets/`, never imagery whose licence doesn't permit redistribution. If
the terms are unclear, mine the facts and file a `needs-human` issue before
anything of the source's *expression* reaches the site.

## Done when

A batch is on disk, the dossier's access section would let a stranger repeat
it, and an extract issue names the first batch to read.
