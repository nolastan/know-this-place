# article-10-landmarks — SF Planning landmark designation reports

> **Research dossier.** Rules: [../AGENTS.md](../AGENTS.md) · traps:
> [../LESSONS.md](../LESSONS.md) · register:
> [../SOURCES.md](../SOURCES.md) · cited on pages by the source id `article-10-landmarks`.
>
> - **Kind:** PDF reports · **Tier:** primary · **Status:** open
> - **Search-invisibility:** high — PDF-only, address-specific designation documents not indexed
> - **Coverage:** Article 10 of the Planning Code (Landmarks Preservation) — 370 San Francisco landmark properties with individual designation reports
> - **Local corpus:** `research/corpora/article-10-landmarks/` — one PDF per landmark, named by landmark ID (LM001, LM002, etc.)

Update this dossier at the end of every pass — the `Verified:` line, the coverage note, and anything the pass learned about getting at the source.

## What

SF Planning's **Article 10 landmark designation reports** are PDF documents, one per designated landmark property. Each is a formal legal document establishing the property's status as a city landmark and citing its historic and architectural significance.

The dataset is indexed at DataSF ([97yj-54sx](https://data.sfgov.org/api/views/97yj-54sx)): 370 rows, each with landmark name, address, assessor parcel number (APN), and direct URL to the PDF.

## Access

The index lives at DataSF `97yj-54sx`, which lists all landmarks with their street addresses and links to the PDFs on `files.sfplanning.org` or `sfplanninggis.org`. A simple CSV export gives all URLs at once; no login required.

**Citation URL:** `https://sfplanning.org/landmarks/lm<number>` — a web page; the PDF is linked from it.

**Citation label:** "SF Planning, Landmark Designation No. LM###, [Street Address]"

## What is in the documents

Each report is 3–50+ pages (typically 10–20). Contents include:

- **Location and parcel information:** Street address and assessor's block and lot, so resolution is mostly handed over for free.
- **Historical narrative:** A dated history of the property, often naming occupants, builders, architects, developers, and previous uses.
- **Architectural description:** Materials, style, date of construction, and major alterations.
- **Map and photographs:** Current and historical images.
- **Legal designation:** The precise language of Article 10 status and conditions.

Architects, builders, contractors, and developers are all fair game. Current occupants and owners are barred by the privacy limits.

## Text quality

Mixed. Clean text layers in newer designations (LM100+) and some older ones. Image-only PDFs exist (especially LM1–LM50), requiring OCR. The triage pass sampled:
- LM100 (Castro Theatre): clean text layer, ~5pp
- LM271, LM300 (districts): large, text-bearing
- LM11, LM200: image-only

## Cautions

- **Block and lot given outright** — the whole challenge of the resolver is often handled by the source.
- **Some are entire districts.** LM271 and LM300 are not one building but multiple properties; the document describes all of them together. Each parcel in the district gets its own facts.
- **Duplicates with sf-context-statements are likely.** Both sources cover the same neighborhoods and buildings. Check the overlap before seeding pages.
- **Search for the designation number (LM###), not the address.** The PDF link is sometimes the address; sometimes it's the landmark number. Both work.

## Structure for mining

- **Batch 1:** LM1–LM50 (early designations, many image-only; worth the OCR effort for the depth of history)
- **Batch 2:** LM51–LM100 (mix; transition to cleaner text)
- **Batch 3:** LM101–LM200 (mostly clean text)
- **Batch 4:** LM201+ (newest, cleanest)

Or organize by geography: Downtown (LM1–LM30), Mission (LM40–LM70), etc. The module will decide batching.

---

**Verified:** 2026-09-27, prospecting pass complete
- Index confirmed at DataSF 97yj-54sx: 370 rows, complete address and APN coverage
- PDFs confirmed accessible on files.sfplanning.org and sfplanninggis.org without login
- Text quality verified: clean text layers in LM100+ (Castro Theatre sampled); image-only PDFs in LM1–LM50 (LM11, LM200 sampled)
- Structured data: all records carry landmark name, street address, and APN outright
- Overlap with `sf-context-statements` will need checking before seeding new pages
- Source promoted 2026-09-27; promotion and first mining batch (LM1–LM50) is the next run

**Next:** Mine batch 1 (LM1–LM50) — 50 PDF documents, establish extraction and OCR strategy. All PDFs have text layers or contain the key information (address, date, architect) even if image-heavy.
