# <source-id> — <Short title> (<primary|secondary|tertiary>)

> **Research dossier.** Rules: [../AGENTS.md](../AGENTS.md) · traps:
> [../LESSONS.md](../LESSONS.md) · register:
> [../SOURCES.md](../SOURCES.md) · cited on pages by the source id `<source-id>`.
>
> - **Kind:** <newspaper OCR | book | journal | newsletter | PDF report | directory | photo archive> · **Tier:** <secondary> · **Status:** <open|done|blocked|reference>
> - **Search-invisibility:** <high|medium|low> — see the register for what that rates.
> - **Coverage:** <one honest phrase, in counts>
> - **Local corpus:** `research/corpora/<source-id>/`
>
> Update this dossier at the end of every pass — the `Verified:` line, the
> coverage note, and anything the pass learned about getting at the source.

- **What:** What this is, who published it, what years it covers, and what kind
  of address-level fact it carries. Be specific about the columns, sections or
  series that actually name street numbers.
- **Where:** The stable public URL a page cites. If the URL that *serves* the
  file differs from the URL a reader should be given, record both and say which
  is which.
- **How to get at it:** The tool and the sequence that worked. Batch structure.
  Rate limits. Anything that returned an HTML shell instead of a PDF.
- **What is actually usable:** The parts worth reading, and the parts that look
  promising and aren't. One quoted example of a real entry, so the next agent
  knows the shape.
- **Cautions:** Renumbered or renamed streets. OCR quality. Dates that
  contradict the assessor. Claims the source hedges. Places it is known wrong.
  Every one of these is a lesson someone paid for — write it down.
- **People:** What this source names, and what of that may be used. Default:
  buildings, contractors, architects, firms; never residents, occupants or
  owners. See "Privacy — hard limits" in the root [AGENTS.md](../../AGENTS.md).
- **Citation label:** Exactly what a page's Sources footer should print, with a
  worked example.
- **Coverage:** What has been read, in counts, and what has not — named
  precisely enough that the next pass resumes instead of restarting.
- **Verified:** YYYY-MM-DD (what was checked, the yield — read N, found M,
  resolved K, published J — and **what the run learned**. A trap you hit and
  didn't write down gets paid for again by the next run.)
