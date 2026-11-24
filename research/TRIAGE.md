# Triage notes — what a prospecting pass found

One entry per lead marked `hold` in [SOURCES.md → Leads](SOURCES.md#leads--candidates-not-yet-verified)
— what the triage pass actually found, with the sampled example that proves it
carries numbered addresses with dates.

**Delete an entry when its lead is promoted**; the dossier takes over from
there. A struck-through lead keeps its note, in place, with the reason it
didn't pan out.

This is a lookup, not a document to read. Search it for the source you are
about to triage — someone may already have paid for the answer.

---

**Sunnyside History Project** (`sunnysidehistory.org`). Real, and on the four
judgements it would rank high: a single-neighbourhood archive built by a local
historian, covering a district with almost no coverage on this site, and the
kind of per-house writing that carries a street number and a build year.

It is retired anyway, and not on its merits. The site operator has posted an
explicit opt-out for AI agents in both places an operator can post one:

- `robots.txt` carries an **AI Scrape Protect** block — 50-odd user agents under
  a single `Disallow: /`, including `anthropic-ai`, `ClaudeBot`,
  `ClaudeResearchBot`, `AnthropicBot`, `Claude-User` and `Claude-SearchBot`.
  General crawlers are still allowed, so this is a targeted refusal of exactly
  the use this module would be making, not a blanket no-crawl.
- Every page repeats it in markup: `<meta name="robots" content="noai,
  nosummary, DisallowAITraining">`, plus `gptbot: disallow` and `noimageai`.

Under "Corpora on disk" in [AGENTS.md](AGENTS.md) that is a limit to honour, and
it binds the news module as well as this one: polling the site's feed is the
same automated consumption by the same agent. **No corpus was fetched and no
feed was added.** Three requests were made in total — `robots.txt`, the
homepage, and the sitemap index — to establish the policy, which is what read
it.

What would unblock it is a person asking the operator for permission. That is
#203, kept open and labelled `needs-human`. Nothing here should be revisited by
an agent until that answer exists: the next pass will otherwise re-derive the
opt-out from scratch and, worse, may not notice it, because `robots.txt` says
`Allow: /` to `User-agent: *` sixty lines above the block that names us.


**Article 10 landmark designation reports.** DataSF's `97yj-54sx` carries 370
rows, each with the landmark name, address, **APN** and a direct URL to the
designation document — so this is the one lead where resolution is handed over
for free rather than being the hard part. The documents themselves live on
`files.sfplanning.org` or `sfplanninggis.org`, not DataSF. Text quality is
mixed: LM100 (the Castro Theatre) has a clean text layer naming "429-431 Castro
Street, Assessor's Parcel Block No. 3582, Lot No. 085", and the two district
documents sampled are large and text-bearing (LM271, 75pp; LM300, 235pp), but
LM11 and LM200 are image-only and would need OCR. Same publisher as
`sf-context-statements` but an entirely separate corpus.

**Crocker-Langley city directories.** 41 volumes on the Internet Archive with
full OCR. **The privacy limit removes most of the book.** A sampled slice of the
1900 volume is almost entirely residents, marked with `r.` for residence — all
of it off-limits under the root AGENTS.md. What survives is the business entry
sitting in the same alphabetical run: a contractors-and-builders firm at 667
Market, a laboratory director's office at 803 Sutter. An extractor here must
filter on the `r.` marker and keep only firms, which is a narrow slice of a
13 MB text file. OCR is also poor — words are space-broken mid-token. The lead
said "pre-1930"; the successor Polk's Crocker-Langley volumes are on the
Internet Archive too (`polkscrockerlang194849dire` and siblings), so the run
extends at least to 1949 if the business slice proves worth mining.

**SF Municipal Reports.** 68 volumes on the Internet Archive covering FY1859–60
through FY1913–14, plus a separate index volume to the appendices 1859–1901.
Not yet sampled for address density — that is the first thing an acquire pass
should measure.

***Here Today* and *Splendid Survivors*.** The two standard building-by-building
surveys of San Francisco's architecture, and the ones the city's own
environmental documents cite as authority — the 101 California EIR sampled
above refers to "the 1968 catalogue and description of architecturally
outstanding buildings built before 1920 (Olmsted, Roger, and T.H. Watkin, 1968,
*Here Today*)". All three editions are on the Internet Archive
(`heretodaysanfran00olms` 1968, `heretodaysanfran0000olms` 1978,
`splendidsurvivor00corb` 1979, the downtown survey). **All three are
lending-restricted**: `access-restricted-item: true`, collection `inlibrary`,
and a direct fetch of the `_djvu.txt` returns **401**. Per "Corpora on disk" in
[AGENTS.md](AGENTS.md) that makes this `needs-human`, not something to route
around — a person borrows the scan or reads the copy at SFPL. Worth the ask:
these are per-address entries with dates and architects, in books that have
been out of print for decades. Not yet sampled for content, because sampling it
is the thing that needs a person.

**Journal of Proceedings, Board of Supervisors.** 157 volumes in the SFPL
collection, **1906–1999**, roughly 4 MB of OCR each. **Sampled:**
`journalofproceed34sanfrich` (1939) — the assessment-appeal schedules put named
firms at numbered addresses on dated days: "Barron & Rossi, 998 Folsom St.
Assessment erroneous, excessive, reassessed. Tax paid to Assessor, Aug. 11,
1938"; the same run gives Crosley Radio Corporation, Lewittes & Sons and
Stakmore Co. all at 1355 Market St. That is a dated occupancy record for a
business at a street number, which is usable. **But it ranks low, for two
reasons.** The appeal schedules interleave firms with individuals — "Anna
Crljenko, 930 Fillmore St." on the next line — so an extractor needs the same
person-name filter the city-directories note describes, and most of a volume is
not about buildings at all. Street name changes and street acceptances are the
other seam here and have not been sampled.

**Western Neighborhoods Project *Outside Lands* magazine.** 36 issue PDFs listed
at outsidelands.org/publications/. **Access caution:** a plain `curl` for the
PDF returns 403; a browser-context fetch retrieves it fine. **Sampled:** volume
21 number 3 names Little Woman Variety & Foods at 2722 Clement Street with a
photo credit. The weakness is datedness — captions run to "circa 1980" as often
as to a year, and undated claims are nearly unusable under the evidence bar.
Same organization as OpenSFHistory, so reuse terms are one conversation, not
two.

**OpenSFHistory photo captions.** Same organization as WNP above. Terms are
explicit and workable: 1,000-pixel watermarked images are free for personal and
educational use, the watermark must not be cropped, WNP does not hold copyright
to everything in the collection, and the requested credit line is
`OpenSFHistory/<file number>` — for example `OpenSFHistory/wnp15.556` — linking
back to opensfhistory.org. That is the citation label a page would print. Facts
in a caption are free regardless. **Sampled:** a caption dating a single-family
residence at 1354 32nd Avenue, between Irving and Judah, to 1950.

**SFMTA Photo Archive.** Muni photography from 1903 to 1978, of which the
agency says over 95% is digitized, browsable on PhotoShelter. Copies up to 1,200
pixels are free on request for non-commercial use; they are not to be sold or
used in advertising, and there is no bulk download — every image is a request.
That request gate, plus the likelihood that transit photography is captioned to
the intersection rather than the street number, puts this well down the list.
Worth a pass only once the cheaper sources are exhausted, or when a specific
address needs a photograph and nothing else has one.

**San Francisco block books, 1894–1909.** Twelve volumes on the Internet
Archive (`handyblockbookof1894hick`, `sanfranciscobloc1901hick`,
`merysblockbookof1909bloc`, the 1906 volumes and others), digitized with SFPL
funding. **This is not a page source and should not be treated as one.** The
volumes are map plates: block outlines with lot lines, lot dimensions and owner
names lettered onto the drawing. The `_djvu.txt` is consequently noise — a
sampled page of the 1901 volume yields scattered surnames and fragments like
`S7-` where dimensions should be. Owner names are people and barred regardless.
What survives is genuinely useful but narrow: **pre-1906 lot geometry**, which
the resolver already uses as a corroborating check (see the cautions in
[sources/loc-newspapers.md](sources/loc-newspapers.md) on matching 25x125 against
a parcel's `lot_area`). Register it, if at all, as a resolver aid.

**Pacific Coast Architecture Database.** Per-building records of real quality —
the Crocker Building entry gives 600 Market Street, constructed 1890–1891,
demolished 1968, ten storeys, the architect, the building contractors, latitude
and longitude, and a narrative with its sources named. **And that is the
problem.** A plain web search for "600 Market Street San Francisco Crocker
Building history" returns the PCAD record as the **first result**. By the
standard set at the top of [AGENTS.md](AGENTS.md), a source already ranking for
address queries adds little to why this site exists. Keep it where `local-news`
sits — a cross-check for a fact found elsewhere, and a way to catch an
architect attribution that contradicts ours. Not a mining target.

**Sanborn fire insurance maps.** 40 San Francisco volumes at the Library of
Congress, 1886 onward, explicitly public domain and free to reuse. **But the
online format is `image` with no OCR and no text layer at all**, so every fact
has to be read off a map by eye or by vision model. Nothing else on this list
has that cost. There is also no obvious finishable batch unit yet — "one sheet"
is too small to be worth an issue and "one volume" may be hundreds of sheets.
Working out the batch unit is the precondition for this one, not the mining.

**California Digital Newspaper Collection.** The prize is real: CDNC holds 33
San Francisco titles, and the one that matters is ***Daily Alta California*,
1849–1891**, which covers the entire period before `loc-newspapers` begins in
1890. Also there: the Elevator (1865–1898) and Pacific Appeal (1862–1880), both
Black press; Organized Labor (1900–1988); Labor Clarion (1906–1947); Vestkusten
(1887–2007); Italia (1897–1919). **The search endpoint returns a Cloudflare
managed challenge to automated requests.** Under "Corpora on disk" in
[AGENTS.md](AGENTS.md) that makes it a `needs-human` matter, not something to
route around. Two things a person could do, in order: check whether Chronicling
America itself holds *Daily Alta California* — if it does, the existing
`loc-newspapers` tooling mines it with no wall to negotiate — and, failing that,
ask UCR whether they will grant API or bulk access.

**Rejected in the 2026-08-21 pass, with what was actually checked.**
*McCord's Edwards Abstract from Records* (37 volumes, 1900–1931, collection
`sfpl_mccords-edwards-abstract-from-records`) is the metes-and-bounds trap in
its purest form: a sampled 9 MB volume gives transfers as `N Haight 131-6 W
Gough W 27-6 x N 20` with no street number anywhere, the grantors and grantees
are individuals and barred, and the only numbered addresses in the whole file
are the abstract company's own offices at 318 Pine (126 times) and 210
Montgomery (54). *Tenant Times* (40 issues, `tenanttimes`) — a sampled 1981
issue contains no numbered street address at all, and the paper's subject is
the people in the buildings. *SF Weekly archive* (451 issues, `sfweeklyarchive`)
— the run starts in 2013 and the paper is fully indexed on the open web.

**Cultural Heritage Online, rejected 2026-11-05.**
<https://culturalheritageonline.com/place_city/san-francisco/> lists 16 San
Francisco places, all read whole through the site's WordPress API
(`/wp-json/wp/v2/place_card`). Every one is already a well-documented landmark:
the Golden Gate and Bay Bridges, Coit Tower, the Opera House, Alcatraz, the
Russ, Shell and PG&E buildings, 140 New Montgomery, 450 Sutter, Rincon Center,
the Pacific Coast Stock Exchange, the Doelger Building, the Aquatic Park
Bathhouse and the Treasure Island Administration Building. The text is
editorial summary credited to Wikipedia and Wikimedia Commons, with no
citations of its own. Where it can be checked, it is wrong. It gives the Shell
Building as San Francisco Landmark No. 184, but the Shell Building is an Article 11
downtown building and not an Article 10 landmark. It also lists the Shell
Building twice, once as 28 storeys and once as 29. No fact in it is new to the
pages, and its errors make it unsafe even as corroboration.

