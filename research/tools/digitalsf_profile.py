#!/usr/bin/env python3
"""Profile a harvested DigitalSF corpus, or list its candidate addresses.

    python3 research/tools/digitalsf_profile.py                 # profile every harvested set
    python3 research/tools/digitalsf_profile.py --candidates    # TSV of numbered, dated records
    python3 research/tools/digitalsf_profile.py --series        # record counts per archival series

Reads the MARCXML pages that research/tools/digitalsf_harvest.py wrote under
research/corpora/digitalsf/. Deduplicates on the OAI identifier, because the
sets overlap — an `lgbtq` record is also a `Photographs` record.

`--candidates` is the extractor's input: one row per record carrying BOTH an
exact street number in 245$a and a four-digit year, which is the class that can
clear the evidence bar. Everything it omits is omitted on purpose:
block-level locations ("900 block of Valencia Street") are not addresses.
See research/sources/digitalsf.md. Stdlib only.
"""
from __future__ import annotations

import collections
import glob
import pathlib
import re
import sys
import xml.etree.ElementTree as ET

CORPUS = pathlib.Path(__file__).resolve().parents[1] / "corpora" / "digitalsf"
M = "{http://www.loc.gov/MARC21/slim}"
O = "{http://www.openarchives.org/OAI/2.0/}"

STREET = (r"(?:Street|St\.?|Avenue|Ave\.?|Boulevard|Blvd\.?|Road|Rd\.?|Way|Place"
          r"|Pl\.?|Drive|Dr\.?|Terrace|Lane|Alley|Court|Circle|Park)")
EXACT = re.compile(rf"\b(\d{{1,5}})\s+((?:[A-Z][A-Za-z'.]*\s+){{1,3}}?){STREET}\b")
BLOCKY = re.compile(r"\b\d{1,5}\s+block\b", re.I)
YEAR = re.compile(r"\b(1[89]\d\d|20[0-2]\d)\b")


def _subs(field):
    return {s.get("code"): (s.text or "").strip() for s in field}


def records():
    """Yield one dict per unique OAI record across every harvested set."""
    seen = set()
    for page in sorted(glob.glob(str(CORPUS / "*" / "page-*.xml"))):
        try:
            root = ET.parse(page).getroot()
        except ET.ParseError as e:
            print(f"  ! unparseable: {page}: {e}", file=sys.stderr)
            continue
        for rec in root.iter(O + "record"):
            hdr = rec.find(O + "header")
            oai = hdr.findtext(O + "identifier", "") if hdr is not None else ""
            if oai in seen:
                continue
            seen.add(oai)
            mrc = rec.find(f".//{M}record")
            if mrc is None:
                continue
            out = {"oai": oai, "id": "", "title": "", "date": "", "fuzzy": False,
                   "rights": "", "cite": "", "series": "", "streets": [],
                   "notes": "", "person": False}
            cf = mrc.find(f"{M}controlfield[@tag='001']")
            out["id"] = (cf.text or "") if cf is not None else ""
            for f in mrc.iter(M + "datafield"):
                tag, s = f.get("tag"), _subs(f)
                if tag == "245":
                    out["title"] = " ".join(v for k, v in s.items() if k in "ab")
                elif tag in ("269", "260"):
                    out["date"] = out["date"] or s.get("a") or s.get("c") or ""
                elif tag == "907" and "fuzzy" in (s.get("a") or "").lower():
                    out["fuzzy"] = True
                elif tag == "540":
                    out["rights"] = s.get("f") or out["rights"]
                elif tag == "524":
                    out["cite"] = s.get("a") or out["cite"]
                elif tag == "490":
                    out["series"] = s.get("a") or out["series"]
                elif tag == "650":
                    m = re.match(r"Streets--(.+?)\.?$", s.get("a") or "")
                    if m:
                        out["streets"].append(m.group(1))
                elif tag == "500":
                    out["notes"] += " " + (s.get("a") or "")
                elif tag in ("600", "700"):
                    out["person"] = True
            yield out


def address_of(rec):
    """The exact street number in the title, or None. Blocks are not addresses."""
    if BLOCKY.search(rec["title"]):
        return None
    m = EXACT.search(rec["title"])
    return m.group(0).strip() if m else None


def main(argv):
    rows = list(records())
    if not rows:
        sys.exit(f"no harvested records under {CORPUS} — run digitalsf_harvest.py first")

    if "--series" in argv:
        c = collections.Counter(r["series"] or "(none)" for r in rows)
        print(f"{len(rows)} unique records, {len(c)} series\n")
        for k, v in c.most_common():
            print(f"  {v:6}  {k}")
        return

    if "--candidates" in argv:
        print("id\tyear\tfuzzy\taddress\trights\tperson\ttitle")
        n = 0
        for r in rows:
            addr = address_of(r)
            y = YEAR.search(r["date"] or "")
            if not (addr and y):
                continue
            n += 1
            print(f"{r['id']}\t{y.group(1)}\t{'fuzzy' if r['fuzzy'] else 'firm'}\t{addr}\t"
                  f"{r['rights']}\t{'named-person' if r['person'] else ''}\t{r['title'][:110]}")
        print(f"\n# {n} candidates of {len(rows)} records", file=sys.stderr)
        return

    dated = [r for r in rows if YEAR.search(r["date"] or "")]
    exact = [r for r in rows if address_of(r)]
    blocky = [r for r in rows if BLOCKY.search(r["title"])]
    both = [r for r in exact if YEAR.search(r["date"] or "")]
    streets = collections.Counter(s for r in rows for s in r["streets"])

    def pct(n):
        return f"{n:6} ({100 * n / len(rows):5.1f}%)"

    print(f"unique records: {len(rows)}\n")
    print(f"  exact street number in title      {pct(len(exact))}")
    print(f"  block-level only, not an address  {pct(len(blocky))}")
    print(f"  carries a four-digit year         {pct(len(dated))}")
    print(f"  year flagged 'fuzzy date'         {pct(sum(r['fuzzy'] for r in rows))}")
    print(f"  BOTH number and year (candidates) {pct(len(both))}")
    print(f"  carries a Streets--X heading      {pct(sum(1 for r in rows if r['streets']))}")
    print(f"  names a person (600/700)          {pct(sum(r['person'] for r in rows))}")
    print(f"\nrights (540$f):")
    for k, v in collections.Counter(r["rights"] or "(none)" for r in rows).most_common():
        print(f"  {v:6}  {k}")
    print(f"\ndistinct streets indexed: {len(streets)}")


if __name__ == "__main__":
    main(sys.argv[1:])
