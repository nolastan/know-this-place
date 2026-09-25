# hittell-1878 — Hittell's *History of San Francisco* (secondary, period)

> **Research dossier.** Rules: [../AGENTS.md](../AGENTS.md) · traps:
> [../LESSONS.md](../LESSONS.md) · register:
> [../SOURCES.md](../SOURCES.md) · cited on pages by the source id `hittell-1878`.
>
> - **Kind:** book (period history) · **Tier:** secondary · **Status:** done
> - **Search-invisibility:** medium — see the register for what that rates.
> - **Coverage:** The whole book has been read. See the 2026-09-25 `Verified:` line.
> - **Local corpus:** `research/corpora/hittell-1878/`
>
> Update this dossier at the end of every pass — the `Verified:` line, the
> coverage note, and anything the pass learned about getting at the source.

- **What:** John S. Hittell, *A History of the City of San Francisco and
  Incidentally of the State of California* (San Francisco: A. L. Bancroft &
  Company, 1878). A Centennial-year history by the Society of California
  Pioneers' own historian, written from the city archives, the mission records
  and the recollections of surviving pioneers. Numbered sections (§1–§245) make
  citation precise — cite the section, not the page.
- **Item record:** <https://www.loc.gov/item/rc01000675/> (Library of Congress,
  call number F869.S3 H7; also available in digital form). Public domain.
- **Use for:** what stood on a site before the present building — Hittell names
  a modest number of addresses by street number (§231 lists the buildings and
  the fortunes that paid for them) and describes the missions, the presidio and
  the Yerba Buena village lots at length.
- **Cautions:**
  - **Street numbers are the binding problem.** Hittell writes in 1878; street
    numbers changed, streets were renamed (his Dupont Street is today's Grant
    Avenue), and nothing here establishes that an 1878 number is the same
    parcel as today's. Check EAS first — several of his addresses (811 Dupont,
    419 and 317 California, 228 Montgomery) have no modern EAS record at all,
    which is the end of the matter under the directory contract. Where a number
    does resolve, say on the page that the correspondence is unverified.
  - **The buildings are usually gone.** He is describing a city that burned in
    1906. Treat his claim as *site* history — record it under
    `historical_record` with `"kind": "site history"` and the source, and let
    the assessor's `year_property_built` show that the structure he saw is not
    the one standing.
  - **He editorializes, and he speculates.** He flags his own guesses ("presump-
    tively the same structure"), and elsewhere he does not. Take dates, names
    and events; leave the judgements, and never carry his characterizations of
    Indigenous people into a page.
  - **He is a source for the site, not for the present parcel.** Every
    structured fact on the page still comes from the city datasets.
  - **loc.gov's item page is Cloudflare-gated.** `curl` to
    `https://www.loc.gov/item/rc01000675/` returns a challenge page, not the
    text. The Internet Archive holds the same scan (`historyofcityofs00hitt`,
    and a second scan `historyofcityof00hitt`); its `_djvu.txt` is the
    readable full text, fetched via `archive.org/download/<id>/<id>_djvu.txt`
    (follow the redirect).
  - **A programmatic number-near-street-name scan finds everything numbered in
    a book this size.** The whole text (20,323 OCR lines) was joined into one
    string and searched for a 1–4 digit number within about 20–45 characters
    of a San Francisco street name, with page-footer noise ("23 HISTORY OF SAN
    FRANCISCO") stripped first — it turns "58,620 pages of OCR" into a
    five-minute pass for a single book, and turned up all five numbered
    addresses in the text, matching what the two partial 2026-08-04 reads had
    already found by eye.
  - **Most of the book is not about buildings at all.** Sections titled after
    likely-sounding topics — Millionaires (§238), Extravagance (§239) — turn
    out to be biography and social commentary with no address in them; Hotels
    (§237) is the one that pays off, with named, dated hotels by corner.
  - **A hotel "on the site of" a present-day landmark resolves the same way an
    argonaut-sfhs present-day building does** — Planning's historic-resource
    name index confirms APN 0239003 as "BANK OF CALIFORNIA," matching Hittell's
    "the present bank of California." But resolving the parcel isn't enough on
    its own: Hittell gives no date for the Tehama House that stood there
    first, so the finding stays declined rather than published with a guessed
    decade.
  - **"Common rumor tells us..." doesn't disqualify a fact that is otherwise
    concrete.** §231 opens with that hedge before listing which fortune paid
    for which building, but the entries that name a street number and a year
    (400/420 Montgomery, 1853) are exactly as citable as anything else in the
    book; the hedge only matters where nothing else pins the fact down, as with
    the seventeen corner-only anecdotes the rest of that section is really
    made of.
- **Citation label:** "John S. Hittell, *A History of the City of San Francisco
  and Incidentally of the State of California* (1878), §N"
- **Verified:** 2026-08-04 (§231 gives 400 and 420 Montgomery Street to Samuel
  Brannan, 1853; §12–14, 24 and 27 cover the founding and secularization of
  Mission San Francisco de Asís)
- **Verified:** 2026-09-25 (whole book read via the Internet Archive's OCR
  text: 245 sections, 20 candidate building-level facts. Nothing new to
  publish — the book's only five numbered addresses were already known from
  the first pass (811 Dupont, 419 and 317 California, 228 Montgomery: no EAS
  record; 400 and 420 Montgomery: already published, now recorded in
  `research/findings/hittell-1878/full-text.json` for the first time). The
  remaining yield is entirely corner-located: eight named, mostly-dated hotels
  in §237 with no resolvable parcel, one hotel site resolved to 400 California
  Street but declined for lacking a date, and seventeen further funding
  anecdotes in §231 that name a corner and a financier but no number, year, or
  lot dimension. §238 and §239 named no addresses at all. Source moves from
  `open` to `done` — the whole book has been read and nothing remains)
