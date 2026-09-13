#!/usr/bin/env python3
"""Regenerate corpus.jsonl from the content tree. Stdlib only.

One line per address page — path, year built, use, historic district, the
earliest date on its timeline, its source ids and its hub hook — so a
corpus-wide question ("which Mission pages cite a non-sf-* source", "what's
the earliest year documented in the Tenderloin") is a grep over ~1.7 MB of
JSON Lines instead of a walk through 11,305 directories. `data.json` is the
source of truth; this file is a derived index and is never edited by hand.

Run from anywhere: python3 scripts/build_corpus_index.py
"""
# `str | None` in an annotation is a runtime expression before Python 3.10, and
# macOS still ships 3.9 — without this the local build stops here.
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))
# Stdlib-only sibling; importing it would otherwise write
# scripts/__pycache__/ into the working tree (see validate.py's note).
sys.dont_write_bytecode = True
import seed_pages  # noqa: E402
from seed_pages import ADDRESS_DIR, district_of, hook_for  # noqa: E402

# A bare 4-digit year, wherever it turns up in a historical_record date's free
# text ("circa 1930", "between 1947 and 1951") or a permit's ISO "filed" date.
# Good enough for a lookup index; it does not need to parse every date shape
# validate.py or the renderer cares about, only find the smallest year in one.
YEAR = re.compile(r"\b(1[5-9]\d{2}|20\d{2})\b")


def earliest_year(data: dict) -> str | None:
    years = [int(y) for h in (data.get("historical_record") or [])
             for y in YEAR.findall(h.get("date") or "")]
    years += [int(y) for p in (data.get("permits") or [])
              for y in YEAR.findall(p.get("filed") or "")]
    return str(min(years)) if years else None


def source_ids(data: dict) -> list:
    seen = []
    for s in data.get("sources") or []:
        sid = s.get("id")
        if sid and sid not in seen:
            seen.append(sid)
    return seen


def main() -> None:
    content = ROOT / "san-francisco"
    lines = []
    skipped = []

    for data_path in sorted(content.rglob("data.json")) if content.exists() else []:
        page_dir = data_path.parent
        if not ADDRESS_DIR.match(page_dir.name):
            continue
        try:
            data = json.loads(data_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            skipped.append(f"{data_path.relative_to(ROOT)}: invalid JSON")
            continue

        path = data.get("path") or "/" + page_dir.relative_to(ROOT).as_posix() + "/"
        rec = {"path": path}

        year = (data.get("parcel") or {}).get("year_built")
        if year:
            rec["year"] = year
        use = (data.get("parcel") or {}).get("use")
        if use:
            rec["use"] = use
        district = district_of(data).get("name")
        if district:
            rec["district"] = district
        earliest = earliest_year(data)
        if earliest:
            rec["earliest"] = earliest
        ids = source_ids(data)
        if ids:
            rec["sources"] = ids
        rec["hook"] = hook_for(data)

        lines.append((path, json.dumps(rec, separators=(",", ":"), ensure_ascii=False)))

    lines.sort(key=lambda pair: pair[0])
    out = ROOT / "corpus.jsonl"
    body = "\n".join(line for _, line in lines)
    out.write_text(body + "\n" if body else "", encoding="utf-8")
    print(f"corpus.jsonl written with {len(lines)} page(s)")
    for note in skipped:
        print(f"  skipped — {note}")


if __name__ == "__main__":
    main()
