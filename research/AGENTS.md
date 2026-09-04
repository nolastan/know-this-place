# The research module — the rulebook

This directory is where **finding** address-level information happens. The rest
of the repo is where the website gets **built and maintained**.

Two documents run this module:

- **This file** — why it exists, what a run is, the evidence bar, the statuses,
  and the lessons that have already cost something.
- **[RUNBOOK.md](RUNBOOK.md)** — the procedure. Read it when you are about to do
  a run.

Read the root [AGENTS.md](../AGENTS.md) too. Its privacy limits and evidence
rules bind here without exception.

## The goal, and what follows from it

**Know This Place intends to be the first search result for any San Francisco
street address.** A source that is already indexed and ranking does little for
that — a fact anyone can find in three seconds is a fact a reader had no need of
this site for. So the module has a bias, and it is not subtle:

> **Prefer sources that search engines cannot see.** Newspaper archives behind
> OCR, out-of-print books, neighborhood newsletters, association bulletins, PDF
> survey reports, microfilm finding aids, printed journals, oral-history
> transcripts, permit ledgers, city directories. The harder a source is to
> search from outside, the more a page built on it is worth.

Two corollaries agents get wrong often enough to be worth stating:

- **Low yield is fine and expected.** A scanned book that produces four citable
  facts about four addresses is a **win**. See "Mining a corpus" below.
- **A big, easy, already-indexed dataset is not automatically the better
  target.** It usually loses to a small obscure one on the only axis that
  matters here.

## The unit of work is a run, not a stage

**A run is one source taken as far as it goes in one session** — get the
material, read it, resolve the addresses, publish the pages, check the work,
close the books. Six steps, one session, one PR.

They were once six roles in six sessions with six handoffs. That split cost more
in bookkeeping than it bought in focus, and it is where the module's real
defects came from: findings resolved and never published, statuses that
disagreed with each other, and a human who couldn't tell finished work from
abandoned work. **Take the whole chain.** Size the run so the session is full —
if one batch would finish early, take the next one too.

A step may be **skipped** when it has nothing to do: a source read live off the
web needs no corpus, a source with ten addresses needs no manifest. Skipping is
a judgement recorded in the dossier, not a silent omission.

A run may still stop early — the material ran out, something needs a person, or
the batch was far bigger than it looked. Then finish what you read, close its
books completely, and say exactly where you stopped. What a run must never do is
stop at "resolved."

## The boundary with the website

| Research module | Website |
|---|---|
| Finds, acquires, mines, resolves, cites | Composes pages, keeps the design contract |
| Writes findings JSON, dossiers, manifests, issues | Writes `data.json` + `index.html` |
| Owns `research/**` and its source ids | Owns `san-francisco/**`, `shared/**`, `scripts/**` |
| Cares whether a fact is true and traceable | Cares how a true fact is presented |

Publishing is part of a run, so a research agent **does** write to
`san-francisco/**`. When it does it is wearing the site agent's hat and follows
the root [AGENTS.md](../AGENTS.md) and [shared/AGENTS.md](../shared/AGENTS.md)
exactly. What it must never do is let research conventions leak onto a page — no
findings JSON in the content tree, no dossier prose copied into a `narrative`,
no "the archive shows…" sentences.

## The artifacts a run leaves behind

- **[SOURCES.md](SOURCES.md)** — the register. One row per source. This is the
  module's index; **if a source isn't in it, it doesn't exist.** It also holds
  the leads table, which is the prospecting queue.
- **`sources/<id>.md`** — the dossier. How to get at the source, what it
  contains, every caution learned the hard way, what has been covered and what
  hasn't, and the `Verified:` line. **The dossier is the memory of the module.**
  A run that doesn't update its dossier has thrown away most of its value.
- **`findings/<id>/<batch>.json`** — the chain of custody for every fact, from
  the passage it came from to the page it landed on. Rules:
  [findings/README.md](findings/README.md) and
  [schema/finding.schema.json](schema/finding.schema.json).
- **`manifests/*.json`** — parcel lists for `scripts/seed_pages.py seed-list`,
  when a source names enough buildings with no pages to be worth seeding in
  bulk.
- **GitHub issues** — the queue between runs and between agents and humans.

## Statuses — the whole vocabulary

Deliberately short. If you find yourself wanting a new status value, you
probably want a sentence in the dossier instead.

**A source, in the register:**

| status | means |
|---|---|
| `open` | being mined; material remains. The dossier's coverage note says what's left. |
| `done` | exhausted for now. Nothing outstanding. |
| `blocked` | needs a person — a paywall, a licence, a library visit. The dossier says what would unblock it. |
| `reference` | consulted per address for cross-checking, never mined as a corpus. |

**A lead, in the leads table:** blank means nobody has looked; a date means it
was triaged, with the evidence in [Triage notes](SOURCES.md#triage-notes); a
struck-through row means it didn't pan out, with the reason in place. A lead
that gets promoted moves to the register and its row is deleted.

**A finding, in a findings file:** `resolution.status` is `unresolved`,
`resolved` or `rejected`. `publish.status` is `pending`, `published` or
`declined`. Every entry gets a `resolution`; every resolved entry gets a
`publish`. That is all of it — there is no file-level stage, because a file's
state is just what its entries say.

**The one dashboard** is `python3 research/tools/check.py --stats`. It prints
read / found / resolved / published per source, plus an `open` column of
resolved findings nobody has published or declined. A non-zero `open` column is
the module's to-do list.

## Mining a corpus for address-level facts

Much of the research here is **a deliberately low-yield scan of a large source**
— an OCR newspaper run, a period history, a bulk dataset export — for the
handful of passages that pin a fact to a street number. Needles in a haystack is
the design, not an accident, and the measured numbers say so: the Chronicling
America pass in [sources/loc-newspapers.md](sources/loc-newspapers.md) read
**58,620 OCR pages to find 8,437 numbered-address mentions across 2,025
addresses**, and Hittell's 1878 history is an entire book that names a modest
number of addresses, most of which don't resolve in EAS at all. A source that is
overwhelmingly irrelevant is still a good source when the remainder is dated,
numbered and citable.

So when you are handed a dataset, an archive dump, a scanned book or a batch of
OCR text and asked to find the address-level information in it:

- **Do the pass. Don't relitigate it.** A low hit rate is not evidence that the
  input is wrong, the request is confused, the file is truncated, or the effort
  is misspent. Do not stop to ask whether a different or richer dataset was
  meant, whether the scan is worth running given how little is in there, or
  whether the task should be narrowed — and don't open the results with a caveat
  about how thin the material was. Read the whole thing and report what you
  found.
- **A small harvest is a successful pass, and zero is a valid result.** Report
  the outcome as counts — "read N pages/rows, found M numbered-address mentions,
  K of them on streets that have pages here" — in the PR body, in the findings
  file's `coverage` block, and in the dossier's `Verified:` line. A pass that
  surfaces three usable facts out of ten thousand rows has done its job; a pass
  that surfaces none has also done its job, and says so in the same form.
  Neither is a failure to explain away.
- **Scarcity never lowers the evidence bar.** This is the one thing low yield
  genuinely changes, and it changes it in the opposite direction from the
  temptation: do not stretch a weak match to make the harvest look bigger. A
  metes-and-bounds entry with no street number stays unresolved; a mangled OCR
  digit stays unresolved; an 1878 number with no EAS record does not become a
  page; a South Van Ness conversion done by subtracting a constant is wrong.
  Discarding the large majority of candidate hits is the expected arithmetic.
- **Record the scan, not just the hits.** Update the dossier with what was
  covered and what wasn't, so the next run resumes instead of re-reading the
  same haystack.
- **Volume doesn't relax privacy.** These corpora are dense with people —
  householders in want-ads, tenants in fire reports, owners in transfer notices.
  Take buildings, contractors, architects and named firms; leave residents,
  occupants and owners, per "Privacy — hard limits" in the root
  [AGENTS.md](../AGENTS.md). The size of the input is not a reason to loosen
  that, and the low yield of a pass is never a reason to make up the difference
  with people.

## The evidence bar

Every fact that leaves this module carries three things: **a date, a street
number, and a citation precise enough for a reader to check.** A finding missing
any of them is `unresolved`, and unresolved findings stay in the findings file —
they never reach a page.

- **The address is the hard part, and it is where the mistakes are.** Street
  numbers were changed (1909 renumbering), streets were renamed, and one street
  was renumbered *when* it was renamed (Howard → South Van Ness). Resolve
  against `sf-eas-addresses`; where the source gives cross streets or lot
  dimensions, use them as the check. No EAS record means no page — record the
  fact against the surviving building or the street hub, or leave it unresolved.
  The full trap list is in [RUNBOOK.md](RUNBOOK.md#the-renumbering-traps).
- **Never reconcile a conflict silently.** A source that contradicts the
  assessor, or another source, is recorded as a conflict and named in the page's
  `.unknowns`. Adjudicating is not research; it is invention.
- **Cite what you actually read.** The issue, page and date of a newspaper; the
  section of a book; the volume, number and article of a journal; the page of a
  PDF report. "The archive" is not a citation.
- **Facts, not wording.** Extract discrete facts and re-express them through
  page components. Never reproduce a source's sentences or their structure —
  facts aren't copyrightable, expression is.

## What we've learned the hard way

Cross-cutting lessons that cost a session or a correction. Source-specific ones
live in the dossiers. **Add to this list** whenever a run discovers something a
future run would otherwise repeat — that is what makes this module improve
rather than just accumulate.

- **Identical extraction output across many files means you extracted a
  wrapper, not the documents.** 43 of SF Planning's 81 DPR 523 survey PDFs are
  **Adobe PDF Packages**: the outer PDF is a one-page "install Adobe Reader"
  notice and the real documents are *embedded files* inside it. `pdftotext`
  returned the same 621 characters for all 43, and a bulk pass that only counted
  bytes would have recorded 43 documents read and nothing found. `pdfdetach
  -list` / `-save` got 553 per-address forms out of them. The general rule is
  cheap and catches this whole family — a portfolio, a redirect page, a
  cookie wall, a "your download will begin shortly" shell: **after any bulk text
  extraction, count the distinct outputs.** If N files produced far fewer than N
  distinct texts, you have not read the corpus.

- **A finding's `date` is the date of the *fact*; the renumbering question is
  about the date of the *address*.** They are usually the same and for a modern
  survey of an old building they are a century apart. The Market & Octavia DPR
  forms were written in 2006, in 2006's street numbers, about buildings put up
  in the 1880s — and `resolve_eas.py`'s pre-1910 guard refused 200 of 473 of
  them for a renumbering that had already happened long before the surveyor
  wrote the address down. When a source's addresses are contemporary with the
  *reading* rather than the *event*, say so before resolving, and check the
  guard's exemption applies. The fix was to exempt records that print their own
  assessor block and lot, which is the guard's own stated condition.

- **A field shared by many records is about the batch, not the record.** The
  Lee Sims photographs carry a `500$a` "Photographer's notes" that reads like a
  per-item address — *160 October 1970, 700 block Howard Street, Jim's General
  Merchandise, 789 Howard; Imperial Hotel; Panama Hotel* — and **385 of its 431
  instances are on a note shared by more than one record**, because it describes
  a 36-frame roll and is attached to all 36 frames. Read per-record it puts every
  building on the roll at every other one's address. The same shape turns up as a
  folder title in an archive, a header row repeated down a scanned table, and a
  volume-level note in a finding aid. **Before using any metadata field as an
  address, count its distinct values against the record count.** Roughly one
  per record means someone wrote it about that item; far fewer means it belongs
  to the roll, the folder or the accession.

- **A modern geocode attached to an old record locates the camera, not the
  subject.** SFP 169's donor appended a street address to 549 of 918 slides —
  *"SF Opera House from Franklin. 406 Franklin St"*, *"Elevated View Opera House
  & War Memorial. 1390 Market St"* — and those name the viewpoint, not the
  building in the frame. Where the same note also states a number in its own
  prose the two disagree about as often as they agree: 2324 against 2330
  Chestnut, 230 against 250 Brannan, 581 against 553 Buckingham. It is the most
  seductive shape this module meets, because a geocode always resolves: it is
  well-formed, it is current, and EAS confirms it. **Treating it as the address
  would have produced about 300 confidently wrong findings in a collection whose
  honest yield is 21.** The rule that survives: a coordinate or address supplied
  *by the digitizer* is provenance about the scan, and only a number stated by
  the record's own describer is a claim about a building.

- **A quoted title, a model number and a background landmark all parse as street
  addresses.** `"200 Years of Resistance" on Uganda Liquors` yielded *200 Years
  Street*; *Sikorsky HH-52A Seaguard* yielded *52A Seaguard*; *"a construction
  crane in the middle of the street. 555 Market in background"* put a photograph
  of Market Street on a skyscraper's page. Each is the same failure as the
  footnote-marker trap already recorded below — **a number next to a capitalised
  word is not an address, it is a shape** — and each is cheap to guard once
  named: strip quoted spans the way parentheses are stripped, refuse a number
  whose left-hand neighbour is a hyphen, and check for a qualifier **after** the
  number as well as before it.

- **Privacy binds on `raw.text`, which is committed, not only on the page.** A
  collection can be a buildings source and a privacy problem at once: SFP 125's
  addressed half names South of Market hotels by street number, and one of the
  same captions reads *"[name withheld] room in Daton Hotel, 175 3rd Street,
  personal items atop dresser next to sink"*. The publication filters never see
  it, because it never reaches a page — and it is in the repository anyway.
  Redact the record's own personal-name subject headings out of the quoted span
  when the finding is written, and refuse to carry a free-text archival note
  into the findings file at all where that note is a donor's or a photographer's
  prose about who is in the frame. The citation URL is a better audit trail than
  a verbatim caption, and it carries nobody.

- **A pre-1909 address that resolves cleanly is the module's most convincing
  wrong answer.** The 1909 renumbering moved street numbers across much of the
  city, and an EAS join cannot see it: the number exists today, it sits on a
  parcel, and the resolver reports a clean match for a building that may be a
  block away or a century newer. SFP 162 published 42 such findings before the
  audit caught them, and **36 of the 42 sat on a parcel whose building the
  assessor dates after the photograph** — one by 122 years. The cheap test is
  the roll: a photograph older than the building under it is a resolution to
  distrust, whatever the join said. `resolve_eas.py` now refuses any address
  dated before 1910 and says what would unblock it — a cross street, a block
  face, a lot dimension — so the refusal is mechanical rather than a thing the
  next auditor has to think of.

- **An alias maps a street's name, never its direction.** `--alias
  DOUGLAS=DOUGLASS` is a spelling; `--alias 'BUENA VISTA WEST=BUENA VISTA'` is
  not. EAS keeps a post-direction in `address` rather than in `street_name`, so
  collapsing it files the finding on the wrong street and seeds a second page
  for a building that already has one. Check what EAS actually holds in each
  field before inventing an alias.

- **A report that reads the page cannot tell your work from the last run's.**
  `check.py --report` counted a page's current `unknowns` and
  `building.completed_conflict` as the batch's own, so a digitalsf batch that
  stated no conflicts at all opened its PR claiming five conflicts and four
  disputed dates — all of them written months earlier by the context-statement
  runs that had already documented those same buildings. The columns now
  subtract what the page held before this batch's commits touched it, the way
  *Pages created* and *Pages edited* already did. **Any per-batch count taken
  from a page's current state is wrong on a page two sources have touched**, and
  the more thoroughly the site is documented the more often that is every page.

- **A `description` warning is not a page defect until you check the page.** The
  source-voice sweep looked like 571 descriptions to rewrite and 571 pages to
  re-render. It was 571 descriptions and **69 pages**: the rest were either
  declined, or published into a *structured component* rather than prose — the
  1990 UMB batch put all 343 of its into `historic_survey`, so its wording never
  reached a page at all. **Size a description sweep by grepping the target pages
  for the offending sentence, not by counting the warnings.** The two numbers
  differed by eight-fold here, and the difference is the whole cost of the job.
- **A phrasing check only catches the shapes its author had in front of them.**
  `SOURCE_VOICE_PASSIVE` listed *illustrated, pictured, depicted, reproduced* and
  missed *photographed as an example of the neighbourhood's flats* — nine
  descriptions, published, that read exactly like the four it did catch. When you
  fix a new shape of a known slip, **add it to the pattern in the same commit**,
  or the next run rediscovers it by eye.

- **A parcel's page is not always at a number the finding names, and both the
  resolver and the publisher can get this wrong in opposite directions.** The
  site keeps one page per parcel, at the number the assessor files it under, so
  a corner building addressed on two streets has its page on whichever street
  the assessor chose. `resolve_eas.py` forms `resolution.path` from the
  finding's own number, which is right until the page turns out to live at the
  other address. **28 SFP 23 findings said `published` with a path no page has
  ever occupied** — every one had actually landed, on the parcel's page one
  street over — and **eight UMB findings were declined outright with "no page
  was seeded for it"** while that same page sat there the whole time. The
  question to ask is never "is there a page at this path" but "does this parcel
  have a page"; `check.py` now asks it, and fails a published finding whose
  path has no `data.json`, naming the page the APN does have.

- **A point-placed address is settled by the block's number line, not by the
  parcel's range field.** Where EAS carries no parcel for an address the
  resolver places it by point, and EAS points sit centimetres from a boundary.
  The available test used to be sf-parcels' `from_address_num`/`to_address_num`,
  which fires on 61 of 582 point placements and is wrong about 46 of them,
  because that field is routinely narrower than the numbers a parcel holds.
  Reading all 61 found the test that held every time: **another parcel holding
  a number between the address and the parcel the point chose.** Nothing in
  between, 35 of 35 correct; something in between, 13 of 13 the neighbour or
  further. It is blind on a stretch EAS joins no parcel to, and `report` says
  so rather than reporting a clean bill.

- **A wrong placement can seed a page under an address its parcel does not
  carry.** `seed_pages.py` takes the manifest's lowest number as the page's
  own, so a point that landed on the wrong parcel does not just misfile a fact
  — it can name a building. Parcel 0113023 is 287–289 Union Street to EAS and
  to the assessor, and had a page titled *265–289 Union Street* because one
  finding placed 265 there. **When you retract a placement, check whether the
  page it created is the parcel's own address**, and correct the page, not only
  the finding.

- **`seed_pages.py render <neighborhood>` sweeps the render backlog.** 969
  pages are grandfathered in `scripts/render-backlog.txt` because their HTML
  still carries hand-written prose the renderer would drop, and rendering a
  whole neighborhood to re-render your own two pages rewrites them too — this
  run silently replaced a hand-written description on 1640 Grant Avenue that
  way and caught it in `git status`, not in `validate.py`. **Render the page
  paths you edited, one by one.**

- **`--landed` reads `data.json`, and a page can hold a key the renderer does
  not know.** The Corbett Heights tree has a `building_history` object on eight
  Mars Street pages; those pages are hand-written HTML in
  `scripts/render-backlog.txt`, which is the only reason their events are
  visible. Writing that key onto a *rendered* page puts the fact in `data.json`,
  passes `--landed`, passes `validate.py`, and shows a reader nothing — six
  pages in one run. **After rendering, grep the rendered `index.html` for a
  phrase from each fact you wrote.** A key that is right on one page in a
  neighborhood is not thereby right on the next one.

- **A condominium hides behind a single EAS row.** The resolver defers a
  condominium stack, but it used to let one through when EAS carried the
  address on exactly one parcel — no siblings, therefore no stack. 655 Corbett
  Avenue is a 39-unit building of 1964 with one EAS row, and it seeded a page
  for flat 105. The roll knew all along: `property_location` ends in the unit
  designation, `AV0105`, where a whole parcel ends in `0000`. `resolve_eas.py`
  now reads that suffix and declines. **Twenty-nine published pages are still
  one flat rather than a building**, and whether those buildings can have a page
  at all is a directory-contract question for a person: #228.

- **An archive that paginates by recency has no stable batch unit.** The
  Corbett Heights Neighbors newsletter shows ten or eleven issues to a page,
  newest first, so an issue slides from page 1 to page 2 as new ones appear.
  One run recorded its coverage as "page 1 of 5"; two months later the run that
  took "page 2" re-read the January 2026 issue and had to decline four facts
  already on pages. **Record coverage as a range of the source's own dates, and
  name batches the same way.**

- **"Published" is a claim about a page, and it can be false silently.** A
  publisher that sets `building.architect` only if the field is empty does
  nothing when the page already names the same person under another spelling —
  "Chris McKeon" against "Christopher Dennis McKeon" — and the finding is marked
  published anyway. Four entries in one run said published and had changed
  nothing. **After writing the pages and before closing the books, run
  `python3 research/tools/check.py --landed <findings-file>`**: it reports every
  published finding whose page carries neither its description nor a spec row
  naming anyone it records. Each one is a decline, or a description trimmed to
  the part the page lacked with `publish.note` saying so.

- **`--overlap`'s wording percentage is not the signal — the page is.** The
  score compares content words, so a one-line credit scores about the same
  against a page that already says exactly that as against a page that says
  nothing of the kind: "Designed by architect Louis Mastropasqua" scored 50% in
  both cases. Sorting by score and reading the top of the list misses the 40%
  duplicates and wastes time on the 60% originals. Dump each flagged page's
  existing `historical_record`, `building` and `sources` in one pass and decide
  from that — on a citywide batch over a well-surveyed neighbourhood it is the
  difference between 98 correct declines and a page that says the same thing
  twice.

- **A PDF's thin text layer is not the document's yield.** `pdftotext` returned
  841 lines from the 2004 sexual-identity subcultures statement and none of them
  were its two densest pages: both appendices are scanned images, and between
  them they carried 160 of the document's 188 findings. Nothing warns you — the
  appendix heading extracts, the table under it does not. **Run `pdfimages
  -list` over any page whose extracted text looks like a heading with nothing
  after it**, and read the image with `pdftoppm -r 400 -png -x -y -W -H` to crop
  a column at a time. A thin extraction is a hypothesis about the document, not
  a fact about it.

- **A demolished building is `rejected`, not `resolved`.** Its street number
  usually still resolves to a live parcel, and publishing against that parcel
  hangs the fact on whatever was built afterwards. Where a source marks its own
  addresses — the counterculture statement marks nearly every one `(extant)` or
  `(demolished)` — that marking outranks the resolver, which knows only that the
  number exists today. 18 of that document's 100 addresses were rejected this
  way, and every one of them would otherwise have become a page.

- **Read the table of contents before planning the read.** A *strategy* is not a
  *survey*, whatever list it is published on. The LGBTQ+ Cultural Heritage
  Strategy sits on SF Planning's completed historic-context-statements page, ran
  56 pages, and contains exactly one street number — in a photo credit. Chapters
  named for goals and recommended actions mean a policy document and near-zero
  yield; chapters named for property types, periods or a study area mean a
  resource document. Two minutes on the contents page sizes the run correctly.

- **An undated finding needs a spec row, not a timeline entry.** A page's
  timeline is ordered by date, so an entry whose date is `unknown` renders a row
  reading *unknown* above the 1930s. `building.architect`, `.builder`,
  `.developer` and `.name` all carry a credit with no year; nothing carries an
  undated garden, storefront detail or occupancy. **Decide which spec row will
  take an undated finding before you publish it, and decline it if none will** —
  the renderer will not stop you writing it into the timeline. The Modern
  Architecture statement wrote 92 of these before a render caught them, and the
  same defect was live on two pages from an earlier batch. `check.py` now fails
  the run on it; the backlog it was raised against has been swept.

- **In a born-digital PDF, a footnote marker manufactures street addresses.**
  `pdftotext` renders a superscript reference number inline, so a marker that
  falls at the end of a sentence runs straight into the next one and reads as a
  street number: "…popular spot for gay sex.537 Fifth Street was popular for
  cruising" yields *537 Fifth Street*, which does not exist. The LGBTQ citywide
  statement produced **eleven** such phantoms in 710 mentions — 545 Turk Street,
  908 and 909 Polk Street, 1054 Eighteenth Street among them — and several would
  have resolved cleanly in EAS and become confidently wrong pages, because the
  street is real and the number is plausible. **On any source with numbered
  footnotes, check the character before the number**: a lower-case letter, a
  full stop or a closing quote means the "number" is a reference marker and the
  words after it are a new sentence. The same collision invents institutions —
  "Eighteenth Street Services" became *1054 Eighteenth Street*.
- **The overlap tool compares wording; duplicates hide behind different wording.**
  `--overlap` scores text similarity, so it catches a paraphrase and misses a
  restatement in another register. Volume D–F of the professionals biographies
  had **20** findings flagged that way and **35 more** that were flagged only by a
  second scan: match the practitioner's **surname plus a date within two years**
  against every historical-record entry already on the page from another source.
  Almost all 35 were a prolific builder's work — Henry Doelger's Sunset model
  homes, the North Beach flat builders — already documented, house by house, by
  the neighbourhood survey devoted to that builder. **A citywide source about a
  person overlaps a neighbourhood survey about the same person almost
  completely**, and the neighbourhood survey usually says more. Run both scans
  before publishing anything organised by practitioner.
- **A hedge in the extractor's voice is a page naming its source.** Every
  research document hedges — *gives no year*, *records it as demolished*, *dates
  it 1929 in the list and 1923 in a caption* — and carrying that hedge into a
  `description` produces "The volume records…", which the runbook forbids in a
  page body. It reached **50 descriptions** in one run before a grep caught it.
  State the fact instead ("Since demolished", "Dated 1929, though 1923 is also
  given"), or drop the hedge and let `date_precision` carry it. **Grep every
  published description for the source's own noun — volume, statement, survey,
  report, archive — before you commit.**
- **An undated credit is not automatically a decline.** `building.architect`,
  `building.builder` and `building.developer` are components that hold a credit
  with no year, and a page can say who built it without claiming when. Decline
  only where no spec row fits either. Runs before this one declined undated
  credits as a class and threw away facts the page could have carried.
- **Ask what the page already says before you write, not after.**
  `python3 research/tools/check.py --overlap <findings-file>` compares every
  resolved finding against the historical record, hook and narrative already on
  its target page and prints the ones that repeat it. Two statements routinely
  cover the same buildings, so a citywide batch lands on parcels a neighbouring
  survey has already documented: the LGBTQ citywide run wrote 18 findings that
  restated what the page already carried — the Harvey Milk camera shop, the
  Twin Peaks Tavern windows, the Full Moon Coffeehouse — and one of them
  contradicted the page on a date the older entry had right. All of it was
  caught by hand at audit time, after the pages had been written and rendered.
  **Run it between `resolve_eas.py apply` and publishing.** It flags candidates
  for a decision, not errors: decline the duplicate, or trim it to the part that
  is new.
- **A scanned fixed-column table is a 2-D object. Read it from the word boxes.**
  `pdftotext -layout` reconstructs a table by guessing at whitespace, and on a
  scan it guesses differently on every page — the 1990 UMB survey's appendix
  lost every Block on one page, every street number on two others, and half of
  each year on a fourth. Line-based extraction found 1,179 rows; rebuilding rows
  and columns from `pdftotext -bbox-layout` word coordinates found 1,902 in the
  same 51 pages. Cluster words into rows by y, assign them to columns by x
  against the page's own header line, and anchor the column template on whichever
  header word the scan preserves best. *Sixty per cent more yield for an hour's
  work, on any table this project will ever read.*
- **A parser that requires every column throws away good rows.** The same pass
  demanded a four-digit assessor block and silently dropped 200 rows on pages
  where that one column had not survived. Accept a row that still identifies a
  building, record each field's condition, and let the checks downstream decide
  what each column can be used for.
- **A street name that no longer exists reads exactly like bad OCR.** ARMY is
  Cesar Chavez Street and MONROE is Dashiell Hammett Street, and both look like
  scanner damage until the record's own assessor block is consulted — block 4324
  carries Cesar Chavez, and the parcel printed against "20 MONROE" is Dashiell
  Hammett 20–20. **On any pre-1995 source, resolve the street through the block
  before concluding the scan is at fault.**
- **A numbered street with no street type resolves to the Avenue.** San
  Francisco has both a Sixth Street and a Sixth Avenue, forty blocks apart, and
  a source that prints "665 6TH" has told you neither. The UMB ratings table
  sent seven South of Market buildings to the Richmond that way. Where the
  source states an assessor block, take the street type from that block's own
  parcels before resolving; it is the difference between a right answer and a
  confident wrong one, and nothing downstream catches it except the block check.
- **A run that regenerates HTML must check which pages were written by hand.**
  Re-rendering two bespoke pages in this run would have replaced a hand-written
  description, a sub-neighbourhood, a building type and two stat tiles with the
  seeder's defaults. The renderer is the default, not the authority: before a
  bulk re-render, diff one page of each kind, and hand-patch the ones that have
  drifted on purpose.
- **A run that stops at "resolved" leaves the worst possible state.** PR #114
  put 425 `sf-context-statements` findings onto pages and never marked the
  findings file. The next agent could not tell finished work from unstarted
  work, and closing the loop cost a full verification pass over 425 entries
  against 260 pages. *Mark the findings file in the same commit that edits the
  pages.* `check.py` now fails when a file has published entries and resolved
  ones with no decision recorded.
- **A duplicated status will eventually disagree with itself.** The findings
  schema used to carry a file-level `stage` alongside the per-entry statuses;
  PR #114's file said `stage: resolved` while its facts were on pages. Derived
  state belongs in the tool that derives it, not in the file.
- **Don't sample a corpus sequentially to estimate its density.** OAI-PMH and
  most archive APIs return records in accession order, so any prefix is one or
  two accessions rather than a cross-section. A `digitalsf` prospecting pass
  measured 1.2% on that basis and was wrong by more than threefold.
- **Read the field the archivist wrote in, not the one that is easy to parse.**
  `digitalsf`'s `269$a` collapses "between 1946 and 1951" to `1946`, and its
  `907$a` fuzzy-date flag catches only 115 of 298 imprecise dates. Trusting
  either promoted 183 estimates to firm years.
- **Check where a collection actually keeps its people before trusting a flag
  about them.** In `digitalsf` SFP 23 the `600`/`700` personal-name fields hold
  one corporate body and the actual people are in the titles.
- **A stale identifier loses records silently.** EAS carries retired APNs; a
  manifest built by looking EAS up on the active `blklot` drops those parcels
  with no error. Go via the number EAS actually carries.
- **Query coordinates at full precision.** EAS address points sit centimetres
  from their parcel boundary; rounding to six decimals moves enough of them
  across it to lose the parcel.
- **A frequency count over any commercial corpus surfaces the advertisers.** The
  top numbered address in a trade journal is a firm's own office; in Planning
  Commission minutes it is the Commission's own address. The usable material is
  in the long tail.
- **A recorded range is the whole range.** `resolve_eas.py` used to look up only
  a finding's `street_number` whenever it had one, ignoring the
  `address_range_as_recorded` beside it. Every building whose low number has
  since been retired came back "no EAS record" — 550–590 and 731–799 Van Ness
  Avenue among them, both extant and both surveyed. The tool now expands the
  range whenever one is recorded. *If a record states a range, look up every
  number in it.*
- **A record that names its own parcel has already done the placing.** Where a
  range spans several parcels today, the tool declined — correctly, because
  choosing would be adjudicating. But a survey that prints `647/13, 14` has
  identified the parcel itself, and following that is reading the record, not
  deciding for it. `resolve_eas.py` now takes the parcel a finding's
  `extra.assessor_block_as_recorded` **and** `assessor_lot_as_recorded` name
  when it is one of the candidates, and says so in the method.
- **The nearest published page cannot pick the neighbourhood directory on a
  street that has no pages.** The resolver files a new page under the area of
  the nearest existing page; on Van Ness Avenue, which had three pages in the
  whole city, that scattered one corridor across five directories and put 1765
  California Street in `financial-district`. Where a street is that thin, file
  on the **analysis neighbourhood** the assessor and EAS give the parcel, and
  put the reason in `resolution.method`.
- **A lesson nobody can act on gets paid for twice.** The Van Ness run wrote
  down that the nearest published page cannot pick the neighbourhood directory
  on a street the site hasn't settled — and then left `resolve_eas.py` doing
  exactly that, so North Beach came back scattered across six directories and
  the paths would have been hand-patched a second time. *When a run discovers a
  rule, give the tool the switch that applies it.* `--area-from-nhood` and the
  `manifest` subcommand both exist because the knowledge was already in the
  module and only the tooling was missing.
- **A `conflict` is not always a conflict about the address.** `resolve_eas.py`
  read every `conflict` as a disagreement between two recorded addresses and
  printed `"290 Lombard Street" against "None"` into eighteen resolution
  methods. Most conflicts are a source disagreeing with itself about a *date*
  or a *name*; those resolve normally and the disagreement is the page's
  `.unknowns` to carry. The branch now runs only when a second address is
  actually recorded.
- **A page the generator will not render is a hand-authored page.** Publishing
  in bulk means calling `seed_pages.render_html` over pages the run did not
  create, and some of them predate it — a source with no `query`, a field the
  renderer expects as a string. Writing `data.json` and letting the render blow
  up leaves the two files disagreeing, which the root AGENTS.md forbids
  outright. *Render first, write both files or neither, and list what has to be
  edited by hand.*
- **A condominium class code is not proof of a condominium.** `resolve_eas.py`
  and `seed_pages.py` both declined any parcel the roll class-codes
  `Condominium`, which is right for a unit stack and wrong for an old parcel
  that was condominium-mapped and never split. 11 Blackstone Court is one
  parcel, one EAS address, no sibling units and a roll build year of 1850 that
  corroborates the statement's circa 1851 — and it was refused a page twice, by
  two tools running the same weak test. Both now check the thing the rule is
  actually about: whether EAS puts the recorded numbers on more than one parcel.
  The Malloch Building's thirteen unit parcels and 2944 Jackson Street's two
  still decline. *Test the condition the rule exists to catch, not the field
  that usually accompanies it — and when two tools enforce the same rule, make
  the one holding the evidence decide and let the other honour it.*
- **A caption-versus-narrative date split has no fixed direction.** The
  Progressive Era styles pass established that where these statements print two
  years for one building, the caption is usually the assessor's roll leaking in.
  The Early Settlement Era statement reverses it: the Nightengale House is 1882
  in the landmark list and the caption, 1878 in the narrative, and the roll says
  **1878** — the narrative is the one agreeing with the roll. *Check the roll
  each time rather than carrying the previous document's direction forward; a
  pattern that held for one statement in a series is a hypothesis about the next
  one, not a rule.*
- **A series covers the same landmarks repeatedly, so a bad address has a
  second opinion.** The Early Settlement Era statement prints the Feusier
  Octagon House at 1607 Green Street; EAS has no such address. The department's
  own Victorian Era Styles statement prints 1067 Green Street for the same
  landmark number, and that page already carried the city's survey record for
  the house. Resolved on the landmark number and the building name. *Before
  calling a statement's address unresolvable, check the sibling statements this
  repo has already read — a transposed digit in one document is often correct in
  another, and matching on a landmark number is an identification where matching
  on a street number would be a guess.*
- **An abbreviated range is not a range.** Surveys print "1843-47" and
  "1761-65" for 1843–1847 and 1761–1765, dropping the digits that don't change.
  `resolve_eas.py` read the pair literally, expanded 47→1843, and reported the
  Japantown statement's Art Deco building at 1843-47 Fillmore Street as spanning
  eighty parcels. The tool now fills a short high end in from the low end.
  *A recorded range needs its high end spelled out before it is expanded.*
- **A parcel found by point can outvote three that were stated.** EAS leaves
  some address rows without a `parcel_number`, and the resolver places those by
  the point their coordinates fall in — which DATA-SOURCES.md already warns sits
  centimetres from a boundary. Inside a recorded range that turned one lot into
  two: 1944 Fillmore Street landed on the neighbour and declined 1940–1946
  Fillmore Street, an extant National Register building whose other three
  numbers all state the same parcel. The tool now takes the stated parcel and
  says so. *Weigh what the record states above what a coordinate implies.*
- **A permit name with no role label near it walks straight onto a page.**
  `seed_pages.py names` flags role words, firm suffixes and titles, so it never
  saw DBI's intake prefix: "one-stop:peter burns:revision to pa …" carries none
  of them. Two names were seeded onto a Japantown page, and a third had been
  sitting on a Mission page since whenever it was seeded. `NAME_HINT` now catches
  the prefix and all three names are on the redaction list. *A privacy filter
  built from role words misses every name that isn't introduced by one — test it
  against the raw text of the pages you just wrote, not only against its own
  flags.*
- **When a source prints both the historical and the current address, looking
  up the historical one resolves silently onto a neighbour.** The Russian Hill
  statement heads each demolished building with its pre-renumbering number and
  adds "site of today's #N". Every one of those old numbers — 2507, 2509, 2513,
  2517, 2519 Larkin, 2612 and 2614 Polk — is still a live EAS address on the
  same block, so `resolve_eas.py` placed six 1870s cottages on the parcels of
  buildings that are standing today, with a confident method sentence each. It
  showed up only because 2509 Larkin landed on the parcel of the extant 1888
  house next door. *A renumbering trap does not always look like a miss; the
  dangerous ones look like clean matches. When a record gives today's address
  for a site, place on that and say so.*
- **EAS holds the numbered streets as zero-padded ordinals**, so a source that
  spells one out — "285 Second Street" — failed at the *street*, not the number,
  and came back "not a street in the city's address registry" for one of the
  busiest streets downtown. `resolve_eas.py` now maps spelled-out ordinals to
  EAS's form (`SECOND` → `02ND`) and states the mapping in the method. *A
  lookup that fails on the street name rather than the number is a spelling
  problem, not a finding.* **The digits fail the same way and were not
  covered**: a survey that writes "20 2nd Street", which is how nearly every
  report writes it, lost 1st, 2nd and 3rd Streets whole — 130 findings in the
  middle of downtown — until the same mapping was taught to accept `2ND` as
  well as `SECOND`.
- **A survey of a redevelopment area is a record of buildings that were about to
  come down, and some did.** The Transit Center survey lists thirteen active
  projects that would demolish buildings it had just inventoried; three of its
  parcels now carry buildings the assessor dates after the survey was written.
  A construction date published on those pages would describe a building that is
  gone. *Compare the assessor's year built with the source's on every finding,
  and where the roll year postdates the source, state both years and let the
  page's `.unknowns` carry the disagreement — never assert a demolition the
  source does not record.*
- **Two surveys of the same buildings do not fit in one page.** The Transit
  Center survey area sits inside the Central SoMa survey area, which this repo
  had already published; 57 of the 123 pages the run reached already carried the
  other survey's `historic_survey` panel, and the renderer holds one. Their
  ratings could not be shown at all, and only the fact the other survey lacks —
  district-contributor status — reached those pages, as a timeline entry.
  *Before planning where a district statement's facts will go, check which of
  its parcels the repo has already documented from a neighbouring survey.*
- **A page-level fact still needs its finding marked published.** Writing a
  surveyed year into `building.completed_conflict` while declining the finding
  that supplied it left a page stating a disagreement with no entry in its
  `sources` — an unsourced sentence, which the root AGENTS.md forbids outright.
  *A finding that reached the page in any component is published, whatever
  component it reached, and the source entry goes with it.*
- **The resolver's path and its manifest disagreed about a parcel's lowest
  number**, because the path reaches EAS rows filed under a since-retired parcel
  and the manifest did not. The seeder put the page at 657 Mission Street while
  every resolution pointed at 655: one parcel, two places, and the facts landing
  on neither. `build_manifest` now carries the path's own number into the list
  it hands the seeder.
- **A parcel with no row on the assessor's secured roll cannot become a page,
  and on an architectural corpus that selects for exactly the best buildings.**
  Eight resolved Russian Hill parcels have `in_asr_secured_roll: false` and no
  roll row in any year, so `seed_pages.py` skipped them: 945 and 947 Green, 2555
  Larkin, 2500 Steiner, 2000 and 2006 Washington, 1925 Gough. They are the
  1910s–1920s apartment houses, several of them the "cooperative" buildings the
  report itself describes — the parcel is not assessed as one property. This is
  the condominium rule's cousin and it bites the same way: *the rule that keeps
  the site honest about parcels also holds back the most-documented buildings,
  so say which ones in the dossier rather than letting them vanish into a
  count.*
- **A project table without a date column is not a dated record.** The New Deal
  statement lists hundreds of WPA projects by facility, address and scope of
  work, with a project *number* where a year would go. Fifty-nine findings in
  that batch were first written with a year the document never states — 1935,
  because that is when the agency started — and every one had to be corrected to
  the agency's own span before publication. The evidence bar wants *a date, a
  street number and a citation*; a table that gives two of the three gives two of
  the three. **Before writing a year into a finding, find the sentence that says
  it.** Where only a span is defensible, record the span and say in `extra` why.
- **A privacy filter tuned to full names misses the initialled ones.**
  `NAME_HINT` learned DBI's `one-stop:` intake prefix after two names walked onto
  Japantown pages, but the redaction list only held the names in the form those
  permits printed them. This run's seeding surfaced `one-stop:p.burns` on the
  zoo's page, and a repo-wide sweep of the same prefix found `m.tjoe`, `mtjoe`,
  `m tjoe`, `susan leong`, `eric. omokaro` and `neil f.` already published across
  sixteen pages. *A name on the redaction list is one spelling of that name;
  after every bulk seed, grep the whole repo for the intake prefixes, not just
  the pages you wrote.*
- **A note that only exists in `data.json` is not on the page.** Findings runs
  have been writing conflicts into an `unknowns` key since Market & Octavia, and
  `seed_pages.py`'s renderer never read it — the disagreements reached the repo
  and stopped there. The renderer now states them above the "Not yet
  documented" line. *When you invent a key, check that something renders it.*
- **The natural way to write up an inventory finding is the one thing the design
  contract forbids.** A source that says nothing about a building except that it
  is on a list invites the sentence "Picked out by a 2007 walking survey as a
  house predating…" — which is exactly the `a survey records…` pattern the root
  AGENTS.md rules out of a page body. It went onto 129 pages across two batches
  before an audit caught it, because it reads like content rather than like
  attribution. The line: a listing or designation **event** may be stated as an
  event, the way the North Beach pages state a 1982 survey listing; an ordinary
  fact about a building must be stated as a fact, with the attribution left to
  the Sources footer. *Grep the descriptions you are about to publish for
  "survey", "statement", "report" and "according to" before rendering.*
- **A generic entry published beside a specific one is a duplicate, not a second
  finding.** Sources that carry both an inventory and a narrative name the same
  building twice, and the narrative always says more — a firm year, a builder, a
  style. Publish both and the page's one timeline shows two items at the same
  date, the second saying less. Four Parkside findings were declined for this.
  *Before publishing a source with both parts, group the resolved findings by
  parcel and read every page that gets more than one.*
- **A read whose resolve step is blocked must still land on `main`.** The South
  of Market statement was read cover to cover — 118 pages, 155 cited findings —
  in a session whose network policy blocked `data.sfgov.org`, so nothing could
  be resolved. The PR was opened, published nothing, and was closed unmerged
  an hour later; the whole read sat on an abandoned branch for a week, invisible
  to `check.py --stats`, which counts open loops only among findings files that
  are *on disk*. The next run found it only by reading a closed PR's comment.
  *A blocked run's findings file is the expensive half of the work. Merge it,
  even with every entry `unresolved` — a stranded branch is indistinguishable
  from work nobody has started.* And check `data.sfgov.org` answers before
  planning a run; one `curl` decides whether the run can finish.
- **The renumbering guard is a refusal, not a verdict, and the assessor usually
  settles it.** For a modern survey of old buildings the guard fires on the
  whole pre-1910 stock — 47 of the South of Market statement's findings — because
  its only exemption is a record that prints its own block and lot, and a
  narrative statement prints neither. The check it names but cannot make is
  already in the fetched roll: compare the record's date to
  `year_property_built` on the parcel the join chose. On that batch 22 agreed
  within three years, most of them exactly, and were resolved by hand; the rest
  were off by 10 to 124 years and stayed unresolved, including an 1854 mansion
  on a parcel the assessor dates to 1922 — the exact error the guard exists to
  catch. The guard now prints the comparison in its note. *When a tool refuses,
  ask what evidence would change its mind and whether you already have it.*
- **A resolution you make by hand needs `by_hand: true`, or `apply` eats it.**
  `resolve_eas.py apply` recomputes every entry that is not `rejected`, so a
  hand judgement the guard's own note invited would silently revert to
  `unresolved` on the next run — work that looks done and then isn't. `apply`
  now also preserves `resolution.by_hand`; set it whenever you overrule or
  supplement the tool.
- **`seed_pages.py names` goes quiet once the pages exist.** It only inspects
  parcels still marked seedable, so running it after `seed-list` — which is when
  the root AGENTS.md's instruction reads most naturally — reports zero
  descriptions and zero flags, which looks like a clean privacy pass and is not
  one. It also wants the EAS neighborhood name (`"Sunset/Parkside"`), not the
  directory slug. *Do the privacy pass by reading the `data.json` files the run
  just wrote, and test against the raw permit text rather than the tool's own
  flags.*

- **"Rejected, not resolved" for a demolished building cannot be automated, and
  trying it showed why.** The rule is right and the tooling gap was real, so a
  run taught `resolve_eas.py` to reject any finding whose record marks the
  building gone — then ran it over every findings file in the repo before
  trusting it. A regex over any `*_as_recorded` field would have rejected
  **fourteen correctly published findings**, because the thing that came down is
  usually not this building: the *first* St. Francis Hotel of 1904, one academic
  building of a campus, "demolished except for vertical sign", "largely destroyed
  in the Great 1906 Earthquake". Narrowing to a bare marker in
  `status_as_recorded` still rejected the **Swedenborgian Church**, which two
  volumes of the professionals biographies mark demolished and which stands,
  landmarked, at 3200 Washington Street. So the tool raises and the person
  decides: `report` now prints every demolition marking in its own section,
  split into stated-plainly and mentioned-in-passing, and `decide()` changes
  nothing. *Before wiring a rule into a tool, run it over every findings file in
  the repo and read what it would have changed — a rule that is right about the
  general case can be wrong about a source that is wrong about itself.*

- **A source can name a well-known institution and give the address of a
  different building of the same name.** A citywide biography credits Gilbert
  Stanley Underwood with "US Mint, 88 5th Street, 1935-1937". 88 Fifth Street is
  the **Old Mint of 1874** by Alfred B. Mullet — extant, landmarked, already a
  page here — and the Mint Underwood supervised in the 1930s is a different
  building elsewhere in the city. EAS matched, the parcel was live, the roll year
  agreed with nothing in particular, and no check in the pipeline objected: the
  address is real, it is simply not this building's. **When a finding names an
  institution rather than a street number alone, ask whether that institution was
  at that address on that date** — an institution that moved takes its name with
  it, and every downstream tool knows only that the number exists.

- **When a building has been moved, the fact belongs to the parcel it stands on
  now.** The Englander House was built at 807 Franklin Street in 1880 and rolled
  to 635 Fulton Street in February 2021; the source prints both addresses. The
  construction credit was published at 635 Fulton with the original address
  stated in the sentence, because publishing at 807 Franklin would hang an 1880
  house on whatever occupies that lot today. This is the Russian Hill
  "site of today's #N" rule inverted, and it has the same shape: *the parcel that
  carries the building wins over the parcel that carries the old number.*

- **A locator computed by searching a quoted span silently falls back to page 1.**
  A generator that finds each finding's page by looking its `raw.text` up in the
  extracted pages returns nothing when the quoted sentence wrapped a line break,
  and a naive `hits[0] if hits else 1` writes `p. 1` into the citation — ten of
  them in one run, on a source where page 1 is the cover. Nothing downstream
  checks a locator, and a wrong page is exactly the "citation resolves" defect
  step 5 exists to catch. *Normalize whitespace before the lookup, fall back to a
  short distinctive key such as the address rather than to a constant, and fail
  loudly when no page matches.*

- **A month-precision date printed raw on 68 pages, unnoticed.** The timeline
  formatted a full ISO date into "August 24, 1896" and left everything else
  alone, so a source that knows the month but not the day — a directory issue,
  a water-service record — wrote `1896-10` into `historical_record` and the
  page printed that string, next to a formatted date from the line above it.
  It had been doing so on 68 pages across nine neighbourhoods since the first
  run that used the form. Nothing failed: `validate.py` only asks that the HTML
  match the renderer, and it did. *A date precision the extractor can express is
  one the renderer has to be taught; write one of each precision and read the
  rendered rail before you publish a batch.* Twelve of the 68 are on
  `scripts/render-backlog.txt` and still print it raw until that sweep reaches
  them.

- **Putting a lost address on a street hub freezes that hub's list.**
  `seed_pages.py hubs` refuses to rebuild any street hub carrying a section
  beyond its generated lead-and-list template, so the "The lost corner"
  write-up on the Danvers Street hub is why that hub's four entries are now
  hand-maintained. The runbook offers the surviving building's page **or** the
  street hub for an address EAS no longer holds, and it reads as a free
  choice; it is not. Douglass Street has a hundred pages and gains more with
  every seeding run, and freezing that list to carry a demolished brewery
  would have cost far more than the story was worth — so the brewery went onto
  109 Douglass Street, the partner's house next door that survived it.
  *Count the pages under the hub before choosing the hub.*

- **A row of buildings is not a range, and the resolver cannot tell them
  apart.** `resolve_eas.py` expands a recorded range on the assumption it is
  one building with a two-number address, which is right for "1940–1946
  Fillmore Street" and wrong for "3253 through 3259 Baker Street" — a row of
  four houses on four parcels, which it then declines. The fix is at extraction
  time, not in the tool: record only the two numbers the source actually
  prints, one finding each. The buildings between them are real, but their
  numbers are an inference, and a source will tell you so if you let it — the
  PPIE statement calls 215-287 Avila Street *twelve* bungalows and 2122-2146
  Bay Street *five*, spacings that enumerating by parity would have got wrong
  both times.
- **A privacy filter built from role words also misses the bare preposition.**
  The `one-stop:` lesson above widened `NAME_HINT` to catch DBI's intake
  prefix; it still let "walk in cooler per jesus zapien" onto a Marina page,
  because "per" introduces a name with no label at all. The pattern now flags
  two lowercase words after `per` or `by`, which is noisy — "per field
  findings" flags too — and that is the right trade for a list a person
  reviews. *Every widening of this filter so far has come from a name that
  reached a page. Check the pages you just wrote, not the filter's own output.*
- **A roll build year of 1900 is a floor value, not a construction date.**
  Civic and institutional parcels come off the assessor's secured roll as built
  1900, and the PPIE statement says outright that 1900 on the roll may stand
  for something earlier. Publishing it as a source-versus-assessor
  disagreement invents a conflict that isn't there. Where the parcel holds
  several buildings of several dates, say that instead.
- **A parcel can resolve perfectly and still be unable to carry a page.**
  `sf-parcels` marks some active parcels `in_asr_secured_roll: false`, and
  those have no roll row in any year — so `seed_pages.py` has nothing to build
  a page from and skips them, silently, in a line among its output. This is not
  the condominium case and the resolver does not catch it: EAS matches, the
  parcel is active, `resolve_eas.py` says `resolved`. **After seeding, diff the
  manifest against the pages that now exist** — the gap is this. The findings
  are `resolved` with `publish: declined`, which is the "Resolved, no page"
  column of the PR table. Large multi-unit buildings are where it concentrates:
  the Large Apartment Buildings statement lost 11 parcels this way and 10 more
  to condominium APNs, 30 of 89 findings between them.
- **A multi-family theme loses a large, predictable slice to condominium
  conversion.** Small multiple-unit buildings are exactly the stock the city
  converted, so on a theme whose subject *is* multi-family housing the
  condominium rule bites hardest: 13 of 19 unresolved findings in the Flats and
  Small Apartment Buildings statement, and 49 of 161 across it and its companion
  volume once the secured-roll cases are counted too. Budget for roughly a
  quarter of such a batch never reaching a page, say so in the coverage note,
  and do not report it as a resolution failure — the addresses are right and the
  buildings are standing.
- **Check the resolver's neighborhood against the directories the site
  actually has.** `--area-from-nhood` files on the analysis neighborhood the
  assessor and EAS give the parcel, and that vocabulary is not this site's:
  "Twin Peaks" is a real analysis neighborhood and not one of the 40
  directories under `san-francisco/`. The manifest will name it anyway and the
  seeder will create it. `ls san-francisco/` before seeding.
- **Read the target page before writing the fact.** A citywide theme crosses
  every neighborhood statement this project has already mined, so a good share
  of its parcels arrive already documented. Nine of 53 pages in the Flats and
  Small Apartment Buildings run already carried research content, and it cost
  one declined finding, three rewordings and three stated disagreements to
  handle them honestly. What a citywide statement usually adds to a page a
  neighborhood statement reached first is the *type and style*, not the
  architect — the neighborhood survey nearly always had the architect already.
  Check `historic_survey.source` too: the renderer holds one survey panel per
  page, and a second statement's panel cannot go on.
- **Where a source names its own neighborhoods, they beat both filing rules.**
  Proximity and `--area-from-nhood` are both guesses about geography; a context
  statement saying "both located within Noe Valley" is not. On a scattered
  batch the two rules will disagree on a fifth of the findings and split about
  evenly on which is right, and the source's own attributions broke every tie
  correctly in the run that measured it.

- **A table that prints a build year in one column and a use in the next is
  not a dated record, and the giveaway is the assessor's roll.** The SoMa
  Filipino addendum's appendix survey prints YEAR BUILT beside an ASSET that is
  whatever the surveyor found there in 2011. On the rows before about 1960 that
  year is the assessor's own build year — it matched the 2025 roll on **twelve
  of the fifteen** rows where the roll carries one — so publishing the pair as
  one event put a child care centre at 1949, a Filipino cultural centre at 1908
  and a monument at 1900, five entries that had to be withdrawn a PR later. The
  test is cheap and it is now a tool: **compare every finding's date with the
  parcel's `year_built` before publishing**, and where they are equal and the
  fact is not the building going up, the date probably belongs to the building
  rather than to the fact. `check.py --overlap` prints these under *by the roll
  year*. A use that genuinely began the year the building opened is real — say
  so in the publish note rather than deleting the check.
- **On a theme study organised by an institution, what survives an overlap is
  the client.** The Clubs and Social Halls statement collided with the
  architect biographies on nearly every building the site already had: same
  address, same year, same architect, different sentence. What it alone
  carried was who the building was *for* — 609 Sutter Street was on the page as
  "Marines Memorial Club, designed by Bliss & Faville" and nowhere did it say
  the building went up in 1926 as the Western Women's Club. **Trim such a
  finding to the client and the original name rather than declining it**, and
  check `building` before you write: an architect the page already credits is a
  duplicate, an original client is not.
- **An address inside a parenthesis is invisible to a street-name grep when the
  street is a number.** The Clubs statement gives every building as
  *"(1620 Stockton Street, built in 1935, designed by John A. Porporato)"*, and
  a pattern keyed on a capitalised street name silently drops 2700 45th Avenue,
  3543 18th Street and 2850 19th Avenue. This is the same failure as the Early
  Residential study's ALL-CAPS captions, from the opposite direction. *Grep is
  for finding the seam, not for the extraction; a fifty-page statement gets
  read.*

- **A hyphenated `street_number` is a range the resolver cannot read.** It looks
  the number up literally, finds nothing, and reports "EAS has no address near it
  on this street" — which reads like a dead address and is really a mis-filled
  field. The range goes in `extra.address_range_as_recorded`; `street_number`
  holds the low number alone. The biographies A–C batch lost **40 resolutions**
  to this before anyone read a decline closely enough to notice that 809-811
  Pierce Street is an address EAS holds on one parcel. `check.py` now fails an
  unresolved finding with a hyphen in `street_number` and no recorded range.

- **The assessor's roll year is the cheapest test of whether a source's
  addresses are today's addresses.** Take every published finding older than
  1910, compare the source's year to `year_property_built`, and look at the
  distribution. A source printing modern addresses of surviving buildings
  clusters: the biographies A–C volume put 30 of 89 exactly on the roll year, 53
  within three years, 78 within ten. A source printing pre-1909 numbers would
  scatter instead. **Run it before trusting a secondary source's addresses, and
  run it in reverse afterwards** — findings whose roll year falls *long after*
  the source's date are the ones on a parcel that has since been rebuilt, where
  "Designed by X" is a claim about a building that is no longer there. State
  that disagreement in `.unknowns`; never adjudicate it, and never let it become
  a silent assertion about the standing building.

- **A publishing script is not idempotent unless you make it so.** A second run
  reads back its own first run's prose, decides the page already carries the
  fact, and declines findings it published an hour earlier — leaving pages with
  facts and a findings file that says they were declined, which is the exact
  "done but unrecorded" state this module pays most to avoid. Two rules make it
  safe: compute "does the page already say this?" from entries whose `source` is
  **not** this run's, and decide `published` from whether the page *carries* the
  fact after the edit, not from whether this invocation wrote it. If in doubt,
  strip every entry carrying your source id from the pages and re-apply from
  scratch — that is cheap and it is the only way to get a clean count.

- **A source cited in a page's footer with nothing on the page from it is a
  bug.** Declining a finding after the sources entry is written leaves the
  citation stranded. Sweep for it before committing: every page carrying your
  source id must have a published finding, and every published finding's page
  must carry the source id.

- **An undated fact has two homes on a page, not one.** A credit goes in a spec
  row (`building.architect`, `.builder`, `.developer`, `.name`); a survey's own
  observation — style, physical integrity, a listing, a character-defining
  feature — goes in the `historic_survey` block, which carries no year by
  design. Neither is the timeline, which orders by date and renders a dateless
  entry as a row reading *unknown*. Say in `publish.note` which of the two took
  it; `check.py` looks for the words *spec row* or *survey block*.

- **Before writing "nothing on the page could carry it", read the whole
  `data.json`.** Five findings were marked published with a note saying the page
  had nowhere to put them, when `building.architect` and `building.name` were
  holding them the whole time. The audit that wrote those notes looked at
  `historical_record` and `building` and never at `historic_survey`, where 25 of
  the same sweep's 40 findings turned out to live. A page component you forget
  to look at reads exactly like a page component that doesn't exist.

## Filing work

An issue is how a run hands off what it couldn't finish, and how it asks a human
for the one thing it can't do itself. **Prefer finishing over filing** — the
point of a run is to leave less behind, not to fan work out.

- **Labels:** `research` on every issue, plus `needs-human` when it is blocked
  on a person (a paywall, a library visit, a licensing call, a presentation
  decision). *That is the whole label set.* There used to be six per-stage
  labels; a run isn't a stage, so they're gone. Existing issues still carrying
  one are fine — read the title, not the label.
- **Title:** `research(<source-id>): <the specific thing>` — e.g.
  `research(loc-newspapers): mine batch sn85066387/1906`.
- **Body:** use [templates/issues.md](templates/issues.md). Every issue states
  the **source id**, the **input** (file paths, URLs, batch names), and the
  **definition of done** in one line. An issue another agent can't start without
  asking a question is a bad issue.
- **One issue per unit of work someone can actually finish.** "Read the 34
  remaining context statements" is a bad issue; "Add the Japantown Historic
  Context Statement (Revised 2011)" is a good one.
- **Don't file duplicates.** Search open issues for the source id first.

## Corpora on disk

Raw source material — PDFs, OCR dumps, scraped HTML, dataset exports — goes in
`research/corpora/<source-id>/`, which is **gitignored**. It is large,
re-downloadable, and often not ours to redistribute.

- Keep a `state.json` in each corpus directory recording what has been fetched,
  so a later run resumes rather than re-downloads.
- **What gets committed is the findings, not the corpus.** If a fact only exists
  in an uncommitted file, it isn't a fact yet.
- Never commit copyrighted source text into the repo. Quotations in a findings
  file are the minimum needed to justify the extraction (a clause, not a
  column), and never reach a page.
- Be a good citizen when fetching: rate-limit, back off on failure, identify the
  client, and honour `robots.txt` and terms of use. If a source forbids
  automated access, that is a `needs-human` issue, not a workaround.

## This module improves itself

**This module is a skill that is supposed to get better every time it is used.**
The runbook above is the current best guess at how the work goes, not a
constitution handed down. Every run is expected to leave the module smarter than
it found it, and there are three levels of that:

1. **Record what you learned.** Always. Source-specific in the dossier's
   cautions and `Verified:` line; cross-cutting in
   [What we've learned the hard way](#what-weve-learned-the-hard-way) above.
   A trap you hit and didn't write down will be paid for again by someone else.
2. **Fix the gap you tripped over.** A missing schema field, a check the tool
   should have caught, a dossier section that lied, a step in the runbook that
   doesn't match what runs actually do — fix it in the same PR as the work. Not
   an issue for later; the person with the context is you, now.
3. **Restructure when the structure is wrong.** Add or remove a step, a tool, an
   artifact, a status value, a whole document. Collapse two things that are
   really one. Delete what nobody reads. Leave the module easier to use than you
   found it, and **smaller where you can** — every rule, file and status here is
   a cost paid by every future run.

The mechanics:

- Update [RUNBOOK.md](RUNBOOK.md), this file and [README.md](README.md) **in the
  same commit** as any pipeline change. A change that leaves the docs describing
  the old shape is worse than no change.
- Record *why* in the commit message. The next agent inherits the structure
  without the conversation.
- **Two things need a human's say-so:** changing the meaning of an existing
  source id already cited on published pages (it breaks citations), and anything
  that changes what appears on a page under `san-francisco/**` (that is the root
  `AGENTS.md`'s territory, not this file's).
- Everything else is yours to change.

- **A source that prints its own parcel has handed over a test, not just a
  tiebreak.** `resolve_eas.py` used the recorded assessor block and lot to
  *choose* among the parcels a range spans, and never to *check* a resolution it
  had already made — so on a 724-page scan the only guard against an OCR digit
  was the street number, which is itself OCR. Running the comparison over the
  whole batch by hand found the shape immediately: 147 of 167 exact, 15
  re-lottings since 1990, and 5 on another block, of which two were a 3/5
  confusion in the scan (849–853 Valencia printed as block 5996 for 3596) and
  three the record's own error. *`report` now prints that comparison, splitting
  re-lottings from block disagreements; put the printed block and lot on every
  finding from a scanned source, and read every block disagreement before
  applying.*
- **A survey's own column may not be the survey's own claim.** The UMB
  survey's appendix table heads its YEAR column "the year of construction
  according to the Assessor's Records. It is not necessarily accurate."
  Published as a construction date it restates the roll; published as a
  `completed_conflict` it asserts a disagreement between the assessor and the
  assessor. The same document's inventory forms date the building from city
  directories and the trade press, and *those* are evidence. *Read the key
  before treating a column as something the source is claiming.*
- **A survey selected on a hazard is a survey of buildings that were about to
  be replaced.** The Transit Center lesson said to compare the roll year with
  the source's on every finding; the unreinforced-masonry survey says how to
  read the answer. A roll year a few years off is a dating disagreement and
  belongs in `.unknowns`. A roll year *decades* later — 1913 against 2022, 1907
  against 2001 — is not a disagreement at all: the building the source
  described is gone, and publishing its architect and date would describe
  something that does not exist. Seven of that survey's parcels were declined
  on that rule. *Set a threshold, decline above it, and say so in the publish
  note.*

- **An Excel-printed PDF table has no rows in its text layer.** The Showplace
  Square survey data is an `.xlsx` printed to PDF: cells wrap, and a row's
  parcel number, address and note sit on three different baselines, sometimes
  above one another's rows. `pdftotext -layout` and every y-clustering parse
  built on it mixed adjacent buildings' architects, styles and dates. The row
  boundaries are in the **content stream**, where each row starts with a `Td`
  that returns the pen to the first column's x; splitting there and taking each
  drawn string's column from its x rebuilt all 633 rows, and disagreed with the
  layout parse on 167 fields — correctly, every time. *Where a table's rows
  matter, read the content stream, not the rendered text; and parse it twice by
  different means and diff the two before trusting either.*
- **Two readers of the same field will eventually disagree, and the failure is
  silent.** `resolve_eas.py` parsed `address_range_as_recorded` in two places —
  once to decide which parcels to fetch, once to decide a finding — with two
  copies of the regex. A batch that wrote its ranges in a shape only one copy
  accepted had every ranged building's parcel left unfetched, and then declined
  those findings for "not an active parcel in sf-parcels", which is a sentence
  about the city rather than about the tool. 57 findings. *One reader per
  field; and when a lookup fails, check that what it looked up was ever
  fetched.*
- **In a storefront corpus, the date belongs to whatever the caption describes.** "A
  ceramic veneer storefront at 2215 Irving Street, constructed in 1936" dates the
  storefront; the roll dates the building to 1924. Recorded as a construction fact it
  becomes a `completed_conflict` asserting a disagreement that does not exist, and the
  resolver cannot catch it because the address is perfectly good. Two findings were
  corrected after the publication review for this. *Before writing a year into
  `building.completed` or `.unknowns`, ask what the sentence is dating.*
- **`--area-from-nhood` is a per-finding judgement, not a per-batch switch.**
  On a citywide theme the batch lands on six streets in six parts of the city,
  and the two rules disagree in both directions. The switch was right for
  Valley Street (Noe Valley, not the Glen Park of the nearest published page)
  and Peralta Avenue (Bernal Heights, not the Mission) — and wrong for 1227
  24th Avenue, where the site files the 1200 block under `inner-sunset` while
  the analysis neighborhood is Sunset/Parkside, so it would have separated the
  page from 1234 next door. *Run `report` both ways on a scattered batch, and
  where the site has already settled a block, follow the block.*
- **One existing page is not a settled block — and it may itself be misfiled.**
  Proximity files a new page under the area of the *nearest published page*, so
  where a street has exactly one, that page decides the whole corridor. Both
  singletons a citywide theme study landed next to were wrong: 202 Clipper
  Street sits under `castro` where the assessor says Noe Valley, and 279 Ney
  Street under `bernal-heights` where the assessor says Excelsior, and
  proximity would have copied each error onto three new pages. *Before letting
  proximity win, check the neighbour's own `analysis_neighborhood`.* The
  90-page corridor on 21st Street beat the assessor's slug on the same run;
  the single page did not.
- **A cultural statement's densest seam is a transcribed city directory, not a
  table.** The SoMa Filipino heritage addendum has an inventory table of 22
  addressed rows and a narrative that yields 98 more, because the narrative
  reads directories year by year and so prints a named organisation or business
  at a numbered address on a dated line over and over — sixteen Manilatown
  storefronts in one paragraph. *Before judging a statement with no appendix,
  grep the prose for a run of numbers on one street.*
- **On a statement about a demolished community, a low resolution rate is the
  subject showing through.** 26 of 33 unresolved findings there were addresses
  EAS no longer has, because Manilatown was razed for the Financial District
  and Japantown for redevelopment — which is what the document is about. Report
  it as coverage, never as a failure, and never reach for a nearby surviving
  number to rescue one.
- **A method sentence written for one corpus lies about every other one.**
  `resolve_eas.py`'s no-street-number branch said "No street number in the
  catalogue title or the archivist's address note" — true of `digitalsf`, false
  of a survey PDF, a newspaper or a book, and it went into the audit trail of
  two findings from a Planning theme document. The tool serves every source;
  its sentences have to as well.
- **A privacy filter built from digits misses the letter.**
  `seed_pages.py`'s `generalize_units` rewrites "unit #4" to "one unit" and
  leaves "unit a:" alone, because `_UNIT_NUM` requires a digit. 315 permit
  descriptions across the site carry a lettered designator, one of them on a
  page seeded by this run. Same shape as the `NAME_HINT` lessons above and the
  same moral: *every widening of a privacy filter here has come from something
  that already reached a page — so check the pages you just wrote.*
- **A filter built from suffixes takes the sentences too.** The survey's note
  column names the firm for most buildings and describes the architecture for
  the rest, and a name-detector keyed on "Co.", "&" and capitalisation read
  "Intact small-scale industrial building with finely executed brick cornice"
  as an occupant and put it on a page. The leading word is the tell: an
  adjective at the head of a note means the surveyor is describing, not naming.
- **A privacy filter built from role words misses the role it doesn't know.**
  `NAME_HINT` knew owner, applicant, architect, engineer, contractor, tenant,
  landlord and four honorifics, and did not know **inspector** — the one label
  DBI uses that no other pattern fires on, since "per inspector adwin lau" has
  no firm suffix, no "one-stop" prefix and no bare preposition. Two dozen named
  building inspectors were sitting on published pages when this run happened to
  grep for them. *A role-word list is a list of the roles somebody thought of;
  grep the corpus for the shape, not for the words you already have.*
- **And it misses the punctuation, not just the designator.**
  `generalize_units` handles "unit #4" and now "unit a", but died on
  **"unit #:233"** — a colon between the "#" and the number. Widening it is
  safe only there: a bare "unit:" would read the list marker in "one unit: 1.
  rehabilitate ..." as a designator. Third lesson in this family, same moral as
  the two above.
- **When a source prints two street numbers for one building, ask EAS before
  calling it a contradiction — and never let the resolver pick.** The
  Progressive Era statement does it three times. For the Palace of Fine Arts,
  3301 Lyon in the text and 3601 Lyon in the caption, EAS carries *both* numbers
  on the one parcel: there is nothing to state and nothing to adjudicate. For
  the Roos House, 3500 Jackson in the text and 2500 Jackson in the caption, EAS
  carries both as separate parcels, and `resolve_eas.py` silently took the one
  the finding happened to carry — the caption's — whose roll year is **1937**,
  decades after the 1909 building described. The unreinforced-masonry lesson
  below is what settles it: a roll year decades later means the building
  described is not on that parcel. Publishing without that check would have put
  a Maybeck attribution and a landmark number on the wrong building.
- **A hand-corrected resolution used to fall out of the manifest without a
  word.** `resolve_eas.py manifest` decided whether a page already existed by
  testing `resolution.note.startswith("No page at this path yet")` — a string
  the tool writes itself. Any resolution a publisher corrected by hand carried a
  different note, so it was skipped, no page was seeded, and the publish step
  then declined the finding for having no page. It happened twice in one run
  (the Roos House and 4676-4680 18th Street). **Fixed:** the manifest now asks
  the filesystem whether `data.json` exists at the path. *A tool that reads its
  own prose back is testing what it said, not what is true.*
- **Two findings for one page will silently lose one, if the page carries one
  panel per survey.** A publisher that appends a `historic_survey` entry only
  when no entry from that source id exists — the right rule, since two panels
  from one survey misattribute — drops the second finding's content while still
  marking it published. It happened here at 215 and 245 Market Street, two named
  buildings on one assessor parcel. *Before marking a batch published, compare
  the finding count with the page count; where they differ, open the page and
  check the collision reached it.*
- **An illustrated style guide dates its landmarks and copies the roll for
  everything else — and says so nowhere.** The Victorian Era Styles statement
  gives a specific, researched year for every building that is a designated
  landmark (1876, 1883, 1886, 1889, 1892, 1895, 1897, 1902, 1904, 1907) and the
  bare year **1900** for nine of the eleven that are not — including a row of
  *flat-front Italianate* dwellings, a style the same document says ended
  around 1885. No key, no footnote, no column heading admits it: unlike the UMB
  survey's YEAR column, nothing in the document tells you. The tell is the
  repetition — one year, exactly 1900, on every undesignated example — and the
  confirmation is one lookup: 725 Castro Street's roll `year_built` is 1900 too.
  *In a document with no inventory table, check the source's years against the
  roll before publishing any of them; where they are the roll's, publish the
  style and drop the date rather than restating the assessor to himself.*
- **A renderer that stops crashing has not started reproducing.** Fixing the
  `TypeError` that killed the "Street numbers" row on a hand-authored page did
  not make the renderer produce that page — it made it produce a *worse* one,
  quietly, dropping the hand-written description and printing an
  `address_range` dict raw into the breadcrumb. `scripts/render-backlog.txt` is
  what stands between that page and a bulk sweep. *After fixing a render crash,
  read the diff before you trust the page: a loud failure is safer than a silent
  rewrite, and the page may need `"rendered": false` rather than a fix.*
- **A multi-column key list reads correctly in `pdftotext`'s raw order and
  wrongly under `-layout`.** The Russian American statement's two appendix maps
  are keyed to three-column lists of numbered entries. `-layout` reconstructs
  the page line by line, so a wrapped entry in the first column runs straight
  into the second column's next line and two businesses merge into one; raw
  reading order emits each column as a contiguous block and is exact. That is
  the opposite of the advice for scanned tables above, and the two together are
  the real rule: *a PDF has three readings — `-layout`, raw order and the
  content stream — and which one is right is a property of the document, not of
  the project. Try all three on one page and diff them before reading the rest.*
- **An undated row in a dated table takes the table's date, not yours.** Sixty
  of the Russian American statement's appendix entries print a decade; the other
  sixty-nine print nothing, and the only date the document gives them is its own
  table heading — "1920s-1940s" for the interwar Fillmore, "ca 1940s-present"
  for the post-war Richmond. Every one of those sixty-nine was first written
  with a decade the run had supplied itself, which looks exactly like evidence
  and is not. This is the New Deal lesson's second half: that one said *find the
  sentence that says the year*; this one says *when there is no sentence, the
  table's own heading is the span, and `extra.date_basis` has to say so.*
- **A source that says an area was demolished has told you how its addresses
  will resolve.** The Russian American statement says twice that every building
  in the interwar "Russian center" came down in the Western Addition
  redevelopment — and 137 of its 164 unresolved findings came back "no EAS
  record", almost all in those blocks. The blanket statement is not colour, it
  is a prediction, and the useful consequence is the opposite of the obvious
  one: *the findings to look at hardest are the ones that resolve anyway*,
  because the city reissued those numbers on the buildings that replaced them.
  Comparing the roll's year built with the latest date the source gives caught
  22, one of them a 1920s shop landing on a 1974 superblock that carries 69
  numbers of that street on a single parcel.
- **`seed_pages.py render` does not respect `scripts/render-backlog.txt`.** The
  backlog grandfathers pages whose HTML the renderer cannot yet reproduce, and
  a bulk `render` over a batch's page list will quietly sweep any that happen to
  be in it — 2727 Pierce Street lost its "Casebolt House" tag, its hand-written
  meta description and a note about omitted permits, and `validate.py` then
  reported the page as ready to drop from the backlog. The renderer has no
  `data.json` key for any of the three, so the fix is to keep the hand-written
  file. *Before rendering a batch, intersect its page list with the backlog, and
  read `git diff` on every page in both.*
- **A privacy filter's tidy-up only handles the name at the end of a clause.**
  `redact()` dropped a dangling connective before punctuation, so "correct acc
  violation-repair by mr. mcabe instructions" became "…repair by instructions"
  and "notice by john sims on 12-12-2001" became "notice by on 12-12-2001" —
  the name gone, the sentence broken, and both shipped to a page. It now also
  drops a connective left pointing at a second connective. The neighbouring
  half of the fix is the redaction file's own `_order` rule: list "harold lewis
  and assc" before "harold lewis", or the firm's remnant is stranded the same
  way.

- **A document's own recommendation is a fact about the building, not about the
  document.** "The statement recommends the property for landmark designation"
  names the source in the page body, which the publishing rules forbid, and 47
  descriptions in one batch were written that way before anyone noticed —
  because when the source's judgement *is* the finding, attributing it feels
  like accuracy. It isn't: state it impersonally ("Identified in 2024 as
  eligible for local landmark, California Register or National Register
  designation") and let the Sources footer say who. The one place a source may
  be named is `.unknowns`, where a disagreement cannot be stated without saying
  who disagrees — and there it needs its full name, not "the statement".

- **The assessor's `year_built` of 1900 is a bucket, not a date, and a reverse
  date check that forgets this calls extant buildings demolished.** Volume A–C
  established a cheap and valuable check: a finding whose roll year falls *more
  than fifteen years after* the source's date is usually about a building that
  no longer stands, and thirteen pages carry that caution. Run mechanically over
  volume G–I it fired twenty times and was wrong seventeen of them — every
  Charles Hinkel house of 1883 on Broderick and Pine, and the Havens Mansion of
  1884, a designated city landmark, all of which the roll dates 1900. **1900 is
  21% of every roll year on this site** (3,090 of 14,505 pages) and 60% of all
  pre-1907 ones; 1910 is another 3%. They are where the assessor files
  "nineteenth century" and "before the fire". So: apply the check only where the
  roll year is a *specific* later year — 1986 for the 1907 Italian American Bank
  site, 2019 for the demolished Jack Tar Hotel, both of which it caught
  correctly — and treat a roll year of 1900 or 1910 as an ordinary
  construction-date disagreement instead.
- **The same check governs whether the credit may become a spec row.** Where the
  building really is a later one, writing the source's architect into
  `building.architect` misattributes the building standing there now: Hertzka &
  Knowles went onto 1101 Van Ness, whose building dates from 2019, and Lawrence
  Halprin onto 10–50 United Nations Plaza, a 1936 federal building whose plaza
  he laid out and whose architect the page already named. **Set the spec row only
  when the fact is about the building the parcel now carries**; otherwise keep
  the timeline entry, give it the kind `site history`, and leave the spec row
  alone.
- **A specific later roll year is still not proof, so the building's own name is
  the second half of the test.** Volume J–L refined the rule above: a major
  alteration re-dates a parcel, so 225 Bush Street — the Standard Oil Building of
  1922, extant and well known — carries a roll year of 1948 and tripped the
  demolition caution anyway. **State the caution only where the record gives a
  bare address**; where the source names the building (a hotel, a theatre, a
  named office block), the name is evidence that the building described is the
  one standing, and an ordinary construction-date disagreement is the honest
  form. Two of that volume's four candidates moved that way.
- **Size a batch on what its addressed half is *about*, not on how many rows
  it has.** DigitalSF's dossier ordered its 44 collections by addressed-record
  count and named the largest untouched one as the next batch. Its 184
  addressed captions turned out to be a neighbourhood newspaper's photographs of
  the people of the Tenderloin — **177 of 184 carry a personal-name shape, 82
  name someone in a role**, most of them tenants in rent strikes and evictions,
  and most of them alive. The name filter keeps all of that off a page, but
  `raw.text` carries the caption verbatim into a committed findings file, which
  is naming an occupant in the repository — the thing the privacy limits bar *at
  extraction time*. **A collection can be the largest, the best documented and
  the wrong one to read.** Check what the addressed captions say before
  budgeting a session on the count, and where the answer is people, that is a
  decision for a person and not a batch.

- **A caption's own district heading reads as a building name.** Every Worden
  plate ends "in Ingleside Terraces", `terrace` is a building noun, and the
  named-buildings filter kept the *district* as the building's name on sixty
  pages. The fix was not a stop-list: the record already carries its
  `650$a Districts--Ingleside Terraces` heading, exactly as it carries the
  `Streets--` headings the filter was already given to recognise a bare street
  name. *When a filter needs to know that a phrase is a place, ask the record
  before writing the phrase down — a catalogue that indexes by place has already
  told you.*

- **A tool that builds a page's identity from the finding rather than from the
  resolution breaks on every readdressed building.** `resolve_eas.py manifest`
  took `street_name` and `street_type` from the finding — the address as
  recorded — while taking the slug from `resolution.path`. For the Worden plate
  headed "299 Moncada Way" whose note says the address is now 101 Paloma Avenue,
  that produced a manifest entry reading `street_slug: paloma-avenue` with
  `street_name: MONCADA`, which matches no EAS row on the parcel, so the entry
  got no coordinates and `seed_pages.py` died on a bare `KeyError: 'lat'`. The
  resolution's `eas_address` is the address that was actually placed. *Anything
  downstream of a resolution should read the resolution, not the finding it came
  from — they agree on every ordinary record and disagree on exactly the ones
  the module has a rule about.*

- **A duplicate check that recognises your own writes by their wording will not
  recognise them.** `check.py --overlap` excluded a page entry when its text
  matched a finding's `description` — but a publisher trims the address and the
  date out of that sentence before it goes on the page, so "Willard E. Worden
  photographed the property at 710 Victoria Street in 1912" is stored as
  "…photographed the house." and **all sixty** of a batch's own entries came
  back as duplicates of themselves, burying the four real flags underneath. The
  reliable key is the source id: where a source cites per item, the page's id is
  the register id with the item appended (`digitalsf-8325`), so the prefix test
  works. *Same shape as the idempotency lesson above, in the checking tool
  rather than the publishing one — anything that asks "did the page already say
  this?" has to be able to tell your own writes apart, and text is not how.*

- **A pattern keyed on capitalization is a claim about the source's house
  style, and sources do not keep to one.** The DigitalSF extractor matched a
  street name as capitalized tokens, so "743 Washington street" — which is how
  that catalogue writes an address about a third of the time — parsed as *743
  Washington*. It cost three different things at once, which is why it went
  unnoticed through a whole published batch: the finding recorded
  `street_type_not_stated` about a record that stated it, the orphaned "street"
  left in the caption failed the name filter's all-capitalized test and took the
  building's name down with it, and the resolution method said "the record
  states no street type" — which sent a 12th Street address to the
  Street-or-Avenue tie-break for want of a word the record had printed.
  *Before trusting a case-sensitive pattern, grep the corpus for the lower-case
  form of what it is looking for and count.*

- **A filter that drops on positive evidence still has to be told what the
  evidence looks like from both ends.** The same extractor's
  `named-buildings-only` policy — every word capitalized, one of them a building
  noun — is the right trade for a caption collection, because a false keep is a
  privacy failure. What it lost was names the caption *frames*: "Main entrance
  to the Marines' Memorial Club", "Courtyard at the San Francisco Art
  Institute", "Bank of Canton located at …". Widening the prefix list at the
  front, stripping the trailing participle at the back, and completing eight
  noun families recovered 42 names on 53 findings with nothing lost — because
  none of those edits touched the policy, only what reaches it. **The one
  proposed widening that was rejected is the shape to remember:** "home" would
  have kept fourteen funeral homes and also "Home of Charles Berta" and "Home of
  Katherine Modesti". *A head noun that reads as a building in a firm's name and
  as a dwelling in a resident's is not safe as a bare noun, whatever the ratio —
  and the ratio is what makes it tempting.*

- **A word boundary is not a decade boundary, and the field you avoided is
  still the one you fall back to.** The DigitalSF extractor was written to read
  `260$c` precisely because `269$a` collapses a range to its first year — and
  it then failed on `\b(19\d\d)\b` against "1920s", where the trailing "s" is a
  word character and kills the boundary. Every decade date therefore fell
  through to the `269$a` fallback and was written as `date_precision: year`.
  The worst case is the one with no digits at all: `260$c` "19--" means "some
  time in the twentieth century" and `269$a` answers **1900**, which is also
  the assessor's bucket for "nineteenth century" — so the fabricated year is
  the single year this project is least equipped to recognise as fabricated.
  731 records read "19--"; over 2,100 carried a decade; **24 had reached
  published pages** before anyone looked. *A fallback is only as safe as the
  test that decides not to use it — write one input of every shape the source
  actually prints through the parser and read the output, rather than trusting
  the branch you were careful about.*

- **A creator credit does not make a name in a caption something other than a
  person in the frame.** DigitalSF's redactor read `600$a`, which is where a
  catalogue is supposed to put the people a photograph is *about*. SFP 84
  leaves `600` empty and files "Winchell, Ezra & Winchell, Led F." under
  `700$a` with `$e Photographer` — the family photographed their own house in
  the weeks after the 1906 fire — so seven captions naming a household at 747
  Baker Street went into a committed findings file untouched. The module's rule
  that a photographer may be credited is about *crediting the maker*; it says
  nothing about a caption that puts a name at a street number, which is the
  resident information the privacy limits bar outright. *Read every field the
  record files a person in, not the field the standard says it should use* —
  14,535 of that corpus's 22,360 `700` fields carry no role at all. The guard
  that stops the widening eating the evidence is worth copying: **a bare
  surname is left alone when the next word says it is a place**, which keeps
  "Canterbury Hotel" against a `700$a` of "Canterbury, Alan J." and keeps a
  street named for someone.

- **Measure a rule over the whole repo before wiring it in — and be willing to
  leave it out.** A point-placed resolution put 1458 Kirkwood Avenue on a
  parcel that states its own range as 1470–1498 Kirkwood: the address has no
  parcel number in EAS, and EAS points sit centimetres from a boundary, so the
  point landed in the neighbour. The obvious fix is to refuse any point
  placement whose parcel's stated range excludes the number. Run over every
  findings file in the repo that rule fires on **61 of 582** point-placed
  resolutions and **most of them are correct**, because `sf-parcels`'
  `from_address_num`/`to_address_num` is routinely narrower than the EAS
  numbers the parcel actually holds — "2861 24th Street" on a parcel stated
  2863–2869, "243-245 8th Avenue" on one stated 245–245. So the tool raises and
  prints how far outside the number falls, and a person decides: a parcel
  stating a single number is an incomplete field, one stating a wide span that
  excludes the number is usually next door. *Same shape as the demolition rule
  above, reached the same way — by running it before trusting it.*

- **A batch that can yield nothing is still worth defining precisely, and the
  definition is usually not the one the symptom suggests.** DigitalSF's batch
  unit is the citation string in `524$a`, so 1,678 records carrying none were
  invisible to every run — filed as one open question about "the records with
  no citation field". They are not a collection: `982$a` splits all 1,678 into
  six digital series, five of which are not photograph catalogues at all
  (newspaper *issues*, Sanborn atlas plates, five Book Arts items), and the
  whole set states no address in any field. All 37 of the candidates that made
  it an issue are false positives — 23 of them the atlas's own publisher
  imprint, "115 Broadway, New York". *When a group is defined by a missing
  field, find the field that is present before planning the read; the answer to
  "what are these?" is usually a different question's answer.*

- **A second architect on a building the page already credits is an addition,
  not a duplicate — and neither overlap scan will tell you so.** The name-and-date
  scan compares the *same* name, so a different collaborator never matches; the
  wording scan scores these low because the sentences share only the building.
  Temple Emanu-El's page credited John Bakewell Jr. and the professionals
  biographies credit G. Albert Lansburgh for the same 1926 building; both are
  right, because he was the associate. Publish alongside and let neither credit
  adjudicate the other.
