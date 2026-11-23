#!/usr/bin/env python3
"""Put a list of merchants on their buildings' pages, from the city's register.

    python3 merchants/tools/register.py run  merchants/lists/<date>-<slug>.tsv
    python3 merchants/tools/register.py read merchants/lists/<date>-<slug>.tsv
    python3 merchants/tools/register.py apply merchants/sf-registered-businesses/<date>.json

The list is a tab-separated file with a header row: `name` (the trading name
as the register spells it, which is how the list is usually made), `address`
(the merchant's own door, as written anywhere: "3251 20th Ave 250K",
"180 Howard St Ste G2") and, optionally, `page` (the page someone expects it
on, checked against the resolver and never trusted over it).

`read` asks the register (DataSF g8m3-pdis, DATA-SOURCES.md →
sf-registered-businesses) for every registration at each address, picks the
one trading under the listed name, follows that storefront's run of the same
name back through earlier registrants, and writes a findings-shaped file,
`merchants/sf-registered-businesses/<date>.json`, that
`research/tools/resolve_eas.py` reads unchanged. Each entry's `extra` holds
what the page takes: `name`, `name_as_listed`, `kind`, `opened`,
`ownership_changed`. Registrants' names are read to tell one owner from the
next and are never written anywhere.

`apply` writes each resolved entry into its page's `businesses` (one entry
per trading name, replaced if already there) with a `sources` row for the
register, and stamps `publish` on the finding.

`run` is the whole pipeline in the one order that works: read, resolve
(`resolve_eas.py apply`), seed the parcels with no page (`manifest`, then
`seed_pages.py seed-list`), resolve again so the new pages are found, then
apply. Build and validate afterwards (merchants/AGENTS.md → A run).
"""
from __future__ import annotations

import argparse
import csv
import difflib
import json
import re
import subprocess
import sys
import urllib.parse
from datetime import date, datetime
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO / "research" / "tools"))
from resolve_eas import api_get, parse_address, street_display  # noqa: E402

REGISTER = "g8m3-pdis"
SOURCE_ID = "sf-registered-businesses"
SOURCE_NAME = ("SF Office of the Treasurer & Tax Collector, Registered Business "
               "Locations via DataSF")
SOURCE_LABEL = "SF Treasurer & Tax Collector, business registrations"
OUT_DIR = REPO / "merchants" / SOURCE_ID

# Words a registration appends to a trading name that are the registrant's
# legal form, not the name a customer knows.
CORPORATE = re.compile(
    r"[\s,]+(llc|l\.l\.c\.?|inc\.?|incorporated|corp\.?|corporation|co\.?|ltd\.?)$", re.I)

# What the business is. The business's own name says it first where it says it
# plainly ("Fancy Wheatfield Bakery" holds a restaurant licence and is a
# bakery); otherwise the health licence the register carries does. Checked in
# order: "J & M A-1 Cafe Restaurant" is a restaurant.
NAME_KIND = (
    (r"\brestaurant\b|\bresturant\b", "Restaurant"),
    (r"\bbakery\b|\bpastry\b|\bdonuts?\b", "Bakery"),
    (r"\bdeli\b", "Deli"),
    (r"\bmarket\b|\bgrocery\b", "Market"),
    (r"\bjuices?\b", "Juice bar"),
    (r"\bcaf[eé]\b|\bcaffe\b|\bcoffee\b|\blatte\b", "Café"),
)
LICENCE_KIND = (
    ("RESTAURANT", "Restaurant"),
    ("BAKER", "Bakery"),
    ("TAKE-OUT", "Take-out"),
    ("BARS/TAVERNS", "Bar"),
)

# Two registrations with names this alike at one door are one business that
# re-registered — "St Francis Fountain" then "Saint Francis Fountain", "Barbary
# Coast Pastry & Cafe" then "Barbary Coast Pastry And Coffee".
SAME_NAME = 0.8
# A gap longer than this between one registration ending and the next starting
# is a storefront that closed and later reopened under the old name: the page
# dates the business from the reopening.
REOPENED_AFTER_DAYS = 365
# Registrations starting this close together are one handover, however many
# filings it took (a person, then their company, days apart).
ONE_HANDOVER_DAYS = 90


def name_key(name: str) -> str:
    n = (name or "").lower().replace("&", "and")
    n = re.sub(r"^the\s+", "", n)
    n = re.sub(r"\bst\.?\s", "saint ", n)
    n = re.sub(r"\bresturant\b", "restaurant", n)
    return re.sub(r"[^a-z0-9]", "", n)


def display_name(dba: str) -> str:
    """The trading name a page prints: the registrant's legal form dropped,
    "X Dba Y" read as Y, and an all-capitals name put in title case."""
    n = re.sub(r"\s+", " ", dba or "").strip()
    m = re.search(r"\bdba\b\.?\s+(.*)$", n, re.I)
    if m:
        n = m.group(1)
    prev = None
    while prev != n:
        prev, n = n, CORPORATE.sub("", n).strip(" ,")
    n = re.sub(r"(\w)&(\w)", r"\1 & \2", n)
    n = re.sub(r"#\s+(\d)", r"#\1", n)
    if n.isupper():
        n = n.title()
    return n


def kind_for(name: str, row: dict) -> str | None:
    low = (name or "").lower()
    for pat, kind in NAME_KIND:
        if re.search(pat, low):
            return kind
    lic = " ".join(filter(None, (row.get("lic_code_description"),
                                 row.get("lic_code_descriptions_list")))).upper()
    for word, kind in LICENCE_KIND:
        if word in lic:
            return kind
    return None


def day(iso: str | None) -> date | None:
    return datetime.fromisoformat(iso[:10]).date() if iso else None


def register_date(iso: str) -> str:
    """A start date as a page keeps it: a day, or a bare year where the register
    stamped 1 January (DATA-SOURCES.md → sf-registered-businesses)."""
    return iso[:4] if iso[5:10] == "01-01" else iso[:10]


def owner_key(owner: str) -> set:
    words = re.findall(r"[a-z0-9]+", CORPORATE.sub("", (owner or "").lower()))
    return {w for w in words if len(w) > 1 and w not in {"and", "the", "of"}}


def same_owner(a: dict, b: dict) -> bool:
    """Whether two registrations are one owner. A registrant re-filing as a
    company named for the business, or sharing a name with the last one
    ("Chan Fu", then "A.C.A. Fu Group"), is the same owner incorporating."""
    ka, kb = owner_key(a.get("ownership_name")), owner_key(b.get("ownership_name"))
    if not ka or not kb or ka & kb:
        return True
    dba = owner_key(b.get("dba_name"))
    return bool(dba) and (kb <= dba or dba <= kb)


def street_of(addr: str) -> tuple[str, str, str | None] | None:
    """The listing's own address → (number, EAS street name, EAS type), with a
    unit or suite dropped: "3251 20th Ave 250K" → ("3251", "20TH", "AVE")."""
    t = re.sub(r"\s+(ste|suite|unit|apt|#)\s*\S+$", "", addr.strip(), flags=re.I)
    t = re.sub(r"\s+#?\d+[A-Za-z]?$", "", t) if re.search(
        r"\b(st|ave|blvd|way|ct|ter|pl|dr|ln|rd|street|avenue|boulevard)\s+#?\d+[A-Za-z]?$",
        t, re.I) else t
    t = re.sub(r"\s+[A-Z]\d+$", "", t)                       # "Ste G2" already gone; "G2"
    p = parse_address(t)
    if not p:
        return None
    num = re.match(r"\d+", p["numbers"][0]).group(0)
    return num, p["street_name"], p["street_type"]


def same_street(row: dict, num: str, street: str) -> bool:
    got = street_of(row.get("full_business_address") or "")
    if not got or got[0] != num:
        return False
    a, b = got[1].lstrip("0"), street.lstrip("0")
    return a == b


def register_query(addresses: list[tuple[str, str]]) -> str:
    """The register URL a page cites: every registration at its merchants'
    doors."""
    parts = [f"upper(full_business_address) like '{n} {s.lstrip('0')}%'"
             for n, s in sorted(set(addresses))]
    return (f"https://data.sf.gov/resource/{REGISTER}.json?"
            + urllib.parse.urlencode({"$where": " or ".join(parts)}, quote_via=urllib.parse.quote))


def fetch_rows(num: str, street: str) -> list:
    first = street.split()[0].lstrip("0")
    rows = api_get(REGISTER, {
        "$where": f"upper(full_business_address) like '{num} {first}%'",
        "$limit": 1000})
    return [r for r in rows
            if (r.get("city") or "").upper().startswith("SAN FRAN")
            and same_street(r, num, street)
            # A registration opened and closed the same day is a filing
            # correction, not a tenancy.
            and not (r.get("location_end_date")
                     and r["location_end_date"][:10] == r["location_start_date"][:10])]


def similarity(a: str, b: str) -> float:
    return difflib.SequenceMatcher(None, name_key(a), name_key(b)).ratio()


def storefront_run(rows: list, listed: str) -> tuple[dict | None, list, str]:
    """The open registration trading under `listed`, and the run of
    registrations of the same name at the door that leads to it, oldest first.
    Returns (current, run, why-not)."""
    named = [r for r in rows if similarity(r["dba_name"], listed) >= SAME_NAME]
    open_ = [r for r in named if not r.get("location_end_date")]
    if not named:
        return None, [], "the register holds no registration under this name at this address"
    if not open_:
        last = max(r["location_end_date"][:10] for r in named)
        return None, [], f"every registration under this name here has ended (last {last})"
    current = max(open_, key=lambda r: (similarity(r["dba_name"], listed),
                                        r["location_start_date"]))
    # Walk back from the current registration through the earlier ones of the
    # same name, stopping at a long gap: a shop that closed and later reopened
    # under the old name is dated from the reopening.
    named.sort(key=lambda r: r["location_start_date"])
    run = [current]
    for r in reversed([r for r in named if r["location_start_date"] < current["location_start_date"]]):
        if similarity(r["dba_name"], current["dba_name"]) < SAME_NAME:
            continue
        head = run[0]
        end = day(r.get("location_end_date")) or day(head["location_start_date"])
        if (day(head["location_start_date"]) - end).days > REOPENED_AFTER_DAYS:
            break
        run.insert(0, r)
    # The same-name registrations that started after the run began and are
    # not in it (overlapping filings of one handover) still count as filings.
    return current, run, ""


def ownership_changes(run: list) -> list:
    changes, last_owner = [], run[0]
    for r in run[1:]:
        if same_owner(last_owner, r):
            last_owner = r
            continue
        when = r["location_start_date"]
        if changes and (day(when) - day(changes[-1])).days <= ONE_HANDOVER_DAYS:
            last_owner = r
            continue
        changes.append(when)
        last_owner = r
    return [register_date(c) for c in changes]


def cmd_read(args) -> Path:
    today = args.on
    rows = list(csv.DictReader(open(args.list, encoding="utf-8"), delimiter="\t"))
    findings = []
    for i, m in enumerate(rows, 1):
        name, addr = m["name"].strip(), m["address"].strip()
        parsed = street_of(addr)
        f = {"id": f"{today}-{i:04d}", "date": today, "date_precision": "day",
             "kind": "occupancy", "address_as_written": addr,
             "extra": {"name_as_listed": name}}
        if m.get("page"):
            f["extra"]["page_expected"] = urllib.parse.urlparse(m["page"].strip()).path
        if not parsed:
            f["resolution"] = {"status": "unresolved", "note": "address does not parse",
                               "checked_on": today}
            findings.append(f)
            continue
        num, street, stype = parsed
        f.update(street_number=num, street_name=street, street_type=stype)
        reg = fetch_rows(num, street)
        current, run, why = storefront_run(reg, name)
        f["citation"] = {"label": SOURCE_LABEL, "url": register_query([(num, street)]),
                         "locator": "full_business_address, dba_name"}
        f["confidence"] = "high"
        if not current:
            f["description"] = f"The city's register of business locations: {why}."
            f["publish"] = {"status": "declined", "reason": why}
            f["resolution"] = {"status": "unresolved", "note": why, "checked_on": today}
            print(f"  -  {name} — {why}", file=sys.stderr)
            findings.append(f)
            continue
        shown = display_name(current["dba_name"])
        opened = register_date(run[0]["location_start_date"])
        f["description"] = (f"The city's register of business locations lists {shown} at "
                            f"this address, open since {opened[:4]}.")
        f["extra"].update({
            "name": shown,
            "register_dba": current["dba_name"],
            "kind": kind_for(shown, current),
            "opened": opened,
            "ownership_changed": ownership_changes(run),
            "registrations": len(run),
        })
        print(f"  ✓  {shown} — {f['extra']['kind']}, since {opened}"
              + (f", changed hands {', '.join(f['extra']['ownership_changed'])}"
                 if f["extra"]["ownership_changed"] else ""), file=sys.stderr)
        findings.append(f)
    out = Path(args.out) if args.out else OUT_DIR / f"{today}.json"
    doc = {"source_id": SOURCE_ID, "batch": f"{SOURCE_ID}-{today}", "read_on": today,
           "notes": f"Read from {args.list} by merchants/tools/register.py.",
           "coverage": f"{len(rows)} listed merchants", "findings": findings}
    if out.exists() and not args.force:
        sys.exit(f"{out} exists; pass --force to replace it, or --out")
    out.write_text(json.dumps(doc, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"{sum(1 for f in findings if f['extra'].get('name'))} of {len(findings)} "
          f"trading under the listed name → {out.relative_to(REPO)}")
    return out


def page_file(path: str) -> Path:
    return REPO / path.strip("/") / "data.json"


def dump_like(original: str, data: dict) -> str:
    m = re.search(r"\n( +)\"", original)
    return json.dumps(data, indent=len(m.group(1)) if m else 2, ensure_ascii=False) + "\n"


def cmd_apply(args) -> int:
    fpath = Path(args.findings)
    doc = json.loads(fpath.read_text(encoding="utf-8"))
    by_page: dict = {}
    for f in doc["findings"]:
        res, ex = f.get("resolution") or {}, f.get("extra") or {}
        if not ex.get("name"):
            continue
        if res.get("status") != "resolved" or not res.get("path"):
            f["publish"] = {"status": "pending",
                            "reason": "not resolved: " + (res.get("note") or res.get("status", ""))}
            continue
        if not page_file(res["path"]).exists():
            f["publish"] = {"status": "pending", "reason": f"no page at {res['path']} yet"}
            continue
        by_page.setdefault(res["path"], []).append(f)
    changed = []
    for path, fs in sorted(by_page.items()):
        fp = page_file(path)
        raw = fp.read_text(encoding="utf-8")
        data = json.loads(raw)
        biz = data.get("businesses") or []
        for f in fs:
            ex = f["extra"]
            # The door on the city's spelling of the street: the register's
            # "2668 San Bruno St" is EAS's 2668 San Bruno Avenue.
            # Only where it is the same street: a corner building's lead
            # address is on the other one.
            eas = street_of(f["resolution"].get("eas_address") or "")
            if not eas or eas[1] != f["street_name"]:
                eas = (f["street_number"], f["street_name"], f["street_type"])
            door = f"{f['street_number']} {street_display(eas[1], eas[2])}"
            entry = {"name": ex["name"]}
            if ex.get("kind"):
                entry["kind"] = ex["kind"]
            entry["opened"] = ex["opened"]
            if ex.get("ownership_changed"):
                entry["ownership_changed"] = ex["ownership_changed"]
            entry["address"] = door
            entry["source"] = SOURCE_ID
            keep = [b for b in biz if name_key(b.get("name")) != name_key(ex["name"])]
            old = next((b for b in biz if name_key(b.get("name")) == name_key(ex["name"])), None)
            if old and old.get("source") != SOURCE_ID:
                print(f"  !  {path}: {ex['name']} already there from {old.get('source')}; left it",
                      file=sys.stderr)
                continue
            biz = keep + [entry]
            f["publish"] = {"status": "published", "path": path, "on": doc["read_on"]}
        biz.sort(key=lambda b: (str(b.get("opened") or ""), b.get("name", "")))
        data["businesses"] = biz
        # One register row per page, its query covering every door the page's
        # businesses from the register trade from.
        doors = []
        for b in biz:
            if b.get("source") == SOURCE_ID and b.get("address"):
                p = street_of(b["address"])
                if p:
                    doors.append((p[0], p[1]))
        row = {"id": SOURCE_ID, "name": SOURCE_NAME, "label": SOURCE_LABEL,
               "query": register_query(doors), "supports": "Businesses",
               "retrieved": doc["read_on"]}
        srcs = [s for s in data.get("sources") or [] if s.get("id") != SOURCE_ID]
        data["sources"] = srcs + [row]
        fp.write_text(dump_like(raw, data), encoding="utf-8")
        changed.append(path)
        print(f"  ✓  {path}: {', '.join(f['extra']['name'] for f in fs)}", file=sys.stderr)
    fpath.write_text(json.dumps(doc, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"{len(changed)} page(s) updated")
    return 0


def sh(*cmd) -> None:
    print("$ " + " ".join(str(c) for c in cmd), file=sys.stderr, flush=True)
    subprocess.run([str(c) for c in cmd], cwd=REPO, check=True)


def cmd_run(args) -> int:
    out = cmd_read(args)
    rel = out.relative_to(REPO)
    manifest = REPO / "research" / "manifests" / f"{out.parent.name}-{out.stem}.json"
    py = sys.executable
    resolver = ["research/tools/resolve_eas.py"]
    extra = ["--area-from-nhood"] if args.area_from_nhood else []
    sh(py, *resolver, "apply", rel, *extra)
    sh(py, *resolver, "manifest", rel, "--out", manifest.relative_to(REPO), *extra)
    if json.loads(manifest.read_text()):
        sh(py, "scripts/seed_pages.py", "seed-list", "--manifest", manifest.relative_to(REPO))
        sh(py, *resolver, "apply", rel, *extra)
    else:
        manifest.unlink()
    args.findings = out
    return cmd_apply(args)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("read", "run"):
        p = sub.add_parser(name)
        p.add_argument("list", help="tab-separated: name, address[, page]")
        p.add_argument("--on", default=date.today().isoformat(), help="the read's date")
        p.add_argument("--out", help="findings file (default merchants/sf-registered-businesses/<date>.json)")
        p.add_argument("--force", action="store_true", help="replace an existing findings file")
        p.add_argument("--area-from-nhood", action="store_true",
                       help="passed to resolve_eas.py for new pages")
    p = sub.add_parser("apply")
    p.add_argument("findings")
    args = ap.parse_args()
    if args.cmd == "read":
        cmd_read(args)
        return 0
    if args.cmd == "apply":
        return cmd_apply(args)
    return cmd_run(args)


if __name__ == "__main__":
    sys.exit(main())
