#!/usr/bin/env python3
"""Numbered-address mentions out of newspaper OCR, filtered for hand reading.

The mention pass every newspaper run does, kept here so it stops being lost
with the container it was written in. (The East/West 1967-1978 runs kept
theirs in a scratch directory; the 1979 run found it gone and rebuilt it.)

    python3 research/tools/ocr_mentions.py extract <corpus-dir> --items items.tsv \
        --from 1979-01-01 --to 1981-12-31 --out windows.jsonl [--keep-ads]

<corpus-dir>/raw/<identifier>.txt is one issue's djvu text; items.tsv is
`identifier<TAB>date[<TAB>volume<TAB>issue]`. A mention is a number followed by
a street name EAS holds (spelled-out and digit ordinals both mapped to EAS's
padded form), optionally a street type. Each mention keeps a window of text
around it, and the filter drops, in order:

  - another city just after the address (Oakland, Los Angeles, ...);
  - residences ("lives at", "Mr. and Mrs.", "son of", "home at");
  - advertisements (a phone number, a ZIP code, or opening hours in the window);
  - windows with no event or institution word;
  - any address printed in --advertiser (default 6) or more issues of the run
    — advertisers and mastheads.

What survives is printed one window per JSON line, for reading by hand. The
filter's counts go to stderr and belong in the findings file's coverage note.
Stdlib only; the EAS street list comes from resolve_eas's cache.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import resolve_eas  # noqa: E402

TYPE_WORDS = {
    "STREET": "ST", "ST": "ST", "AVENUE": "AVE", "AVE": "AVE", "AV": "AVE",
    "BOULEVARD": "BLVD", "BLVD": "BLVD", "PLACE": "PL", "PL": "PL",
    "ALLEY": "ALY", "WAY": "WAY", "TERRACE": "TER", "COURT": "CT", "CT": "CT",
    "DRIVE": "DR", "DR": "DR", "LANE": "LN", "ROAD": "RD", "RD": "RD",
    "PLAZA": "PLZ",
}

OTHER_CITY = re.compile(
    r"\b(Oakland|Berkeley|Alameda|Sacramento|Los Angeles|L\.A\.|San Jose|Daly City|"
    r"Palo Alto|Hayward|Fremont|Stockton, Calif|Richmond, Calif|San Mateo|Burlingame|"
    r"Millbrae|South San Francisco|Mountain View|Sunnyvale|Cupertino|Honolulu|"
    r"New York|Monterey Park|Pasadena|Fresno|Seattle|Chicago|Hong Kong|Taipei|"
    r"Walnut Creek|Concord|Vallejo|Redwood City|Santa Clara|Menlo Park|El Cerrito|"
    r"Pacifica|San Bruno|San Leandro|Castro Valley|Marin|Sausalito|Mill Valley)\b")
RESIDENCE = re.compile(
    r"\b(lives? at|living at|resides? at|residence at|resident of|home at|"
    r"his home|her home|their home|Mr\. and Mrs\.|son of|daughter of|survived by|"
    r"apartment|apt\.)", re.I)
PHONE = re.compile(r"\b\d{3}[-—.]\d{4}\b|\(\d{3}\)\s*\d{3}")
ZIP = re.compile(r"\b9\d{4}\b")
HOURS = re.compile(r"\b(open (daily|7 days|seven days)|hours:|daily \d|"
                   r"\d{1,2}(:\d\d)?\s*[ap]\.?m\.?\s*(-|to|—)\s*\d{1,2}(:\d\d)?\s*[ap]\.?m)", re.I)
EVENT = re.compile(
    r"\b(open(ed|s|ing)?|clos(ed|es|ing)|mov(ed|es|ing)|relocat\w*|fire|burn\w*|"
    r"demoli\w*|built|construct\w*|dedicat\w*|sold|sale|purchas\w*|bought|lease\w*|"
    r"headquarters|office|center|centre|clinic|school|church|temple|association|"
    r"society|benevolent|tong|club|theat(er|re)|restaurant|hotel|bank|branch|library|"
    r"building|project|housing|program|agency|council|committee|foundation|"
    r"museum|gallery|post|union|strike|picket\w*|protest\w*|meeting|held|"
    r"located|site|founded|established|renovat\w*|remodel\w*|expan\w*|"
    r"inaugurat\w*|ceremon\w*|celebrat\w*|anniversary|landmark|eviction|evict\w*)\b",
    re.I)

# Streets a paper prints without a type ("at 950 Stockton"). Any other street
# needs its type word: untyped, a number before MILES, DAY, PAGE, STATES or
# YOUNG is prose, and in East/West 1979-84 those were a third of the windows.
UNTYPED_OK = set("""GRANT STOCKTON CLAY SACRAMENTO WASHINGTON JACKSON PACIFIC BROADWAY
KEARNY POWELL MASON TAYLOR JONES LEAVENWORTH HYDE LARKIN POLK SUTTER BUSH PINE
CALIFORNIA MARKET MISSION HOWARD FOLSOM HARRISON BRYANT POST GEARY OFARRELL ELLIS
EDDY TURK MONTGOMERY SANSOME BATTERY FRONT DAVIS DRUMM COLUMBUS CLEMENT BALBOA
IRVING JUDAH TARAVAL NORIEGA ORTEGA VICENTE ULLOA VALLEJO GREEN FILBERT LOMBARD
COMMERCIAL WAVERLY BUCHANAN LAGUNA FILLMORE WEBSTER GOUGH FRANKLIN DIVISADERO
VALENCIA GUERRERO DOLORES FULTON HAIGHT HAYES OAK FELL MCALLISTER CHESTNUT
GOLDEN GATE MASONIC VAN NESS SOUTH VAN NESS STEINER SCOTT PIERCE""".split()) | {
    "GOLDEN GATE", "VAN NESS", "SOUTH VAN NESS"}

NUM = r"(?<![\d$.,/-])(\d{1,5}(?:[A-Z]|\s?1/2|½)?)"


def street_table() -> tuple[dict, re.Pattern]:
    """Squashed printed form -> set of EAS (name, type); and one regex of names."""
    rows = resolve_eas.street_names()
    names = defaultdict(set)
    for r in rows:
        n, t = r["street_name"], r.get("street_type") or ""
        if " TI" in n or len(n) < 3 and not n[0].isdigit():
            continue
        names[n].add(t)
    printed = {}
    for n in names:
        printed[n] = n
        m = re.match(r"^0*(\d+)(ST|ND|RD|TH)$", n)
        if m:
            printed[f"{int(m.group(1))}{m.group(2)}"] = n
    for word, eas in resolve_eas.ORDINAL_WORDS.items():
        if eas in names:
            printed[word] = eas
    for alias, eas in {"OFARRELL": "OFARRELL", "O'FARRELL": "OFARRELL",
                       "GRANT": "GRANT", "SOUTH VAN NESS": "SOUTH VAN NESS",
                       "VAN NESS": "VAN NESS"}.items():
        if eas in names:
            printed[alias] = eas
    alts = sorted(printed, key=len, reverse=True)
    pat = "|".join(re.escape(a).replace(r"\ ", r"\s+") for a in alts)
    rx = re.compile(NUM + r"\s+(" + pat + r")\b\.?(?:\s+(" + "|".join(TYPE_WORDS) + r")\b\.?)?",
                    re.I)
    return {k: (v, names[v]) for k, v in printed.items()}, rx


def normalise(text: str) -> str:
    text = re.sub(r"-\s*\n\s*", "", text)           # column line-end hyphens
    return re.sub(r"\s+", " ", text)


def extract(args) -> None:
    corpus = Path(args.corpus)
    items = []
    for line in Path(args.items).read_text().splitlines():
        parts = line.split("\t")
        if len(parts) >= 2 and args.date_from <= parts[1] <= args.date_to:
            items.append(parts + [""] * (4 - len(parts)))
    table, rx = street_table()
    found = []
    for ident, date, vol, no in items:
        p = corpus / "raw" / f"{ident}.txt"
        if not p.exists():
            print(f"missing {p}", file=sys.stderr)
            continue
        text = normalise(p.read_text(errors="replace"))
        for m in rx.finditer(text):
            key = re.sub(r"[\s']+", " ", m.group(2).upper()).replace(" ", "")
            hit = table.get(m.group(2).upper()) or table.get(key)
            if not hit:
                hit = next((v for k, v in table.items() if k.replace(" ", "") == key), None)
            if not hit:
                continue
            name, types = hit
            stype = TYPE_WORDS.get((m.group(3) or "").upper().rstrip("."), "")
            if stype and types and stype not in types:
                continue
            if not stype and (name not in UNTYPED_OK or not m.group(2)[0].isupper()):
                continue
            if not stype and len(types) == 1:
                stype = next(iter(types))
            a, b = max(0, m.start() - args.before), m.end() + args.after
            found.append({
                "issue": ident, "date": date, "volume": vol, "no": no,
                "number": m.group(1).replace(" ", ""), "street_name": name,
                "street_type": stype, "as_written": m.group(0).strip(),
                "offset": m.start(), "after": text[m.end():m.end() + 60],
                "window": text[a:b],
            })
    counts = Counter()
    counts["mentions"] = len(found)
    issues_per = defaultdict(set)
    for f in found:
        issues_per[(f["number"], f["street_name"])].add(f["issue"])
    kept, seen = [], set()
    for f in found:
        w = f["window"]
        if OTHER_CITY.search(f["after"]):
            counts["other city"] += 1
            continue
        if RESIDENCE.search(w):
            counts["residence"] += 1
            continue
        if not args.keep_ads and (PHONE.search(w) or ZIP.search(w) or HOURS.search(w)):
            counts["advertisement"] += 1
            continue
        if not EVENT.search(w):
            counts["no event word"] += 1
            continue
        if len(issues_per[(f["number"], f["street_name"])]) >= args.advertiser:
            counts["advertiser"] += 1
            continue
        k = (f["issue"], f["number"], f["street_name"])
        if k in seen:
            counts["same issue repeat"] += 1
            continue
        seen.add(k)
        kept.append(f)
    counts["kept"] = len(kept)
    out = open(args.out, "w") if args.out else sys.stdout
    for f in kept:
        f.pop("after")
        out.write(json.dumps(f, ensure_ascii=False) + "\n")
    print(f"{len(items)} issues; " + ", ".join(f"{k} {v}" for k, v in counts.items()),
          file=sys.stderr)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    e = sub.add_parser("extract")
    e.add_argument("corpus")
    e.add_argument("--items", required=True)
    e.add_argument("--from", dest="date_from", default="0000")
    e.add_argument("--to", dest="date_to", default="9999")
    e.add_argument("--out")
    e.add_argument("--before", type=int, default=300)
    e.add_argument("--after", type=int, default=300)
    e.add_argument("--advertiser", type=int, default=6)
    e.add_argument("--keep-ads", action="store_true")
    args = ap.parse_args()
    extract(args)
    return 0


if __name__ == "__main__":
    sys.exit(main())
