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

**SF neighborhood newspapers, 1956–2026.** The original lead named five papers
and pointed at each one's own website; that is the wrong access path. The right
one is a single Internet Archive collection, `sanfrancisconewspapers`, holding
**2,358 issues** contributed by a collaborative of neighborhood history groups,
each with a `_djvu.txt` OCR file. Titles include Noe Valley Voice (273 issues),
The Potrero View (190), Richmond ReView (228 across two title spellings),
Visitacion Valley Grapevine (116), New Mission News (111), OMI News (71), North
Mission News (68), New Bernal Journal and Bernal Journal (118), Tenderloin
Times (64), Park Bell (51), The Semaphore / Telegraph Hill Semaphore (75), Glen
Park News (33), The New Fillmore (23). **Sampled:** *The Potrero View*, June
1999 — the Victoria Theater at 2961 Sixteenth Street, the Potrero Hill Health
Center at 1050 Wisconsin Street, the Neighborhood House at 953 DeHaro Street.
OCR doubles its spaces, so match on `\d+\s+Street` rather than a single space.
Two cautions: no explicit license on the items (facts are free, the OCR text is
not ours to redistribute), and these papers are thick with residents, obituaries
and donors — the privacy limits bite harder here than anywhere else in the
register. Marina Times and Westside Observer, both named in the original lead,
are **not** in this collection.

**SF Redevelopment Agency property summaries.** 106 items on the Internet
Archive under `sanfranciscoredevelopmentagencyrecords`, from SFPL's SFH 371,
covering Western Addition A-1 and A-2 and Yerba Buena. **Public domain, CC0
marked**, with a requested credit line: "From the San Francisco History Center,
San Francisco Public Library." The payload is a per-parcel SFRA survey form
(FORM P-10, dated 8/10/62) carrying block and lot, parcel dimensions, number and
type of improvements, assessed land and improvement value, zoning, an exterior
and interior condition survey with dates, and a **recommendation for disposition
— retain, rehabilitate, move, or demolish**. For the neighborhoods the
redevelopment program erased, this is the record of what stood there, and it is
keyed to block and lot, which is the resolver's answer handed over directly.
**Sampled:** item `SFH371-5054_0`, "Western Addition Property Summary", blocks
1126 to 1130. **Two hard cautions.** The forms are handwritten on printed
stock and the OCR of them is close to unusable — dimensions come through as
`25! x [Ob` — so extraction here means a vision pass over page images, not a
text scan. And the collection includes items titled "Western Addition.
Community: Identified People" and "Identified people relocated" — files about
displaced residents by name. Those are exactly what the root
[AGENTS.md](../AGENTS.md) privacy limits forbid, the displacement makes them
more sensitive rather than less, and no amount of public-domain status changes
it. Take the buildings. Leave the people.

**HABS/HAER documentation.** 384 San Francisco items, 104 with a street number
in the title. 126 are military installations (Presidio, Treasure Island,
Alcatraz, Fort Mason), whose addresses will mostly not exist in EAS, and the
numbered civilian ones cluster heavily in a handful of projects — real distinct
coverage is perhaps 40–60 buildings. The payload is the "data pages": a written
historian's report, reachable at
`tile.loc.gov/storage-services/master/pnp/habshaer/ca/ca<NN00>/ca<NNNN>/data/ca<NNNN>data.pdf`
and carrying a text layer that `pdftotext` reads directly — no OCR step needed.
Public domain. **Sampled:** ca3559, North Beach Place Building 1 at 415 Bay
Street — designed 1941–42, built 1950–52, demolished 2001–03, with the
architect and the housing authority named.

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

**San Francisco City Planning Commission minutes.** 109 volumes in the same
SFPL collection, **1946–1984**, each with a `_djvu.txt`. The payload is the
case calendar: a case number, the address, the zoning, the request, the date
and the Commission's decision. **The address line carries a survey bearing**,
which is exactly what the resolver needs where a street number alone is
ambiguous. **Sampled:** `10minutesofsanfran1969san` — "CU67.13 960 Haight
Street, north line, east of Broderick Street; and Broderick Street, east line,
between 112.5 feet and 137.5 feet north of Haight Street. Request for 100-bed
convalescent hospital for long-term psychiatric care on property zoned R-3 and
R-4", carried over from the meeting of 7 August 1969. The same volume names 801
and 731 Grove, 751 and 725 Webster, 1280 Ellis and 6021 Geary. **Caution:** 100
Larkin Street is the top numbered token in every volume and it is the library's
and the Commission's own address, not a case — the same advertiser-address trap
the trade-journals note describes. Volumes are undated in the IA metadata; the
year is in the text.

**Period trade journals.** Two runs, mined identically, so they are one lead.
***Architect and Engineer of California***: 214 issues on the Internet Archive
under `usmodernist-AECA-*`. ***Building & Engineering News***: 35 volumes under
`buildingengineer*`, digitized with SFPL funding, roughly 9 MB of OCR text per
volume. Both are dense with architects, contractors, costs and dates, and both
carry the weekly contract-award column — a sampled 1928 entry gives a
three-storey 69-room apartment building, $80,000, with the owner, the heating
contractor and the architect's firm all named and addressed.

**The catch is the same one `loc-newspapers` already documents, twice over.**
First, the contract notices identify buildings by corner, not by number: the
1912 *Architect and Engineer* award for the Sharon building places it "on the
northeast corner of New Montgomery and Jessie streets" with a $375,000 price and
the architect named, and no street number anywhere. Second, the numbered
addresses that *are* dense in the text are mostly advertisers' and architects'
own offices — in one *Building & Engineering News* volume the 5,427 numbered
street tokens are topped by 354 Hobart (125 times) and 251 Kearny (102), which
are firms' addresses, not building facts. The usable material is in the long
tail. Expect a low resolve rate and a resolver-heavy pass, and note that a
sampled volume ran heavily to Oakland and the wider Bay Area, so a filtering
step for San Francisco comes before anything else.

**Bay Area Reporter archive.** 1,529 issues on the Internet Archive under
collection `bayareareporter`, contributed by the GLBT Historical Society,
identifiers of the form `BAR_YYYYMMDD`, each with OCR text. This is a much
cleaner path than CDNC, which also holds the paper but is walled. **Caution:**
the items carry an explicit "Copyright BAR Media, Inc." — facts extract freely
under the evidence bar, the text does not get committed or reproduced. Note the
register already lists Bay Area Reporter under `local-news` as a browse-only
reference; mining the archive is a different activity and wants its own id.

***East/West: The Chinese-American Journal.*** 1,125 issues on the Internet
Archive under collection `eastwestnews`, **1967–1989**, contributed through
SFPL, with OCR text on each. Chinatown, the Richmond and the Sunset in a
weekly that no address query will ever return. **Density is thin and it is
mostly commercial:** five issues sampled across the run (1967, 1972, 1978,
1984, 1989) carried roughly 5–15 numbered addresses each — 758 Commercial
Street, 900 and 857 Grant Avenue, 724 Pacific Avenue, 777 Stockton Street, 1119
Clement Street, 1127 Market Street. Over 1,125 issues that is a few thousand
mentions, which is a real harvest at this module's usual rate. **Three
cautions.** The OCR is mixed Chinese and English and the Latin text is mangled
(commas render as `，`, and `838 Grant Avenue` recurs across years as an
advertiser, not a fact). The masthead address (863 Stockton Street) will top
any frequency count. And the issues carry an explicit "Copyright 1967 by
EAST/WEST Publishing Company" — facts extract freely, the text does not get
committed.

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

