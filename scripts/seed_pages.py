#!/usr/bin/env python3
"""Seed new address pages from the DataSF APIs. Stdlib only.

This writes the **first draft of a page that doesn't exist yet** — nothing more.
Every fact on a fresh address page comes from an API, so producing that draft is
a data job, not a writing one.

**It never touches a page that already exists.** Once a page is on disk it
belongs to whoever edits it next, by hand, per shared/AGENTS.md. There is no
re-render and no refresh path: a directory that already holds a `data.json` is
skipped, whether the page was seeded a minute ago or written by a person last
year. That is the whole rule, and it is why pages need no marker distinguishing
"generated" from "hand-authored" — the only question is whether the page exists.

Usage:
  python3 scripts/seed_pages.py fetch --neighborhood "Castro/Upper Market"
  python3 scripts/seed_pages.py plan  --neighborhood "Castro/Upper Market"
  python3 scripts/seed_pages.py seed  --neighborhood "Castro/Upper Market" \
                                      --city san-francisco --area castro
  python3 scripts/seed_pages.py names --neighborhood "Castro/Upper Market"
  python3 scripts/seed_pages.py hubs  --city san-francisco --area castro
"""
from __future__ import annotations

import argparse
import collections
import html
import json
import re
import sys
import time
import urllib.parse
import urllib.request
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONFIG = json.loads((ROOT / "shared" / "site-config.json").read_text())
SITE = CONFIG["site_url"].rstrip("/")
REPO = CONFIG["repo_url"].rstrip("/")
CACHE = ROOT / ".cache"
UA = {"User-Agent": "know-this-place-seeder/1.0"}

# The `.sub` locality line, per neighborhood. The Castro's parenthetical is
# required by san-francisco/castro/AGENTS.md — it is what tells a reader that
# "Castro" and "Eureka Valley" name the same place.
AREA_SUB = {("san-francisco", "castro"): "Castro (Eureka Valley)"}

# An analysis neighborhood can contain streets this site files under a
# different neighborhood directory. Castro/Upper Market covers Corbett Heights,
# which san-francisco/corbett-heights/AGENTS.md keeps separate on the strength
# of local sources. Seeding those streets under castro/ would file them twice.
AREA_EXCLUDE_STREETS = {
    ("san-francisco", "castro"): {
        "corbett-avenue", "ord-street", "ord-court", "hattie-street",
        "danvers-street", "mars-street", "romain-street", "levant-street",
        "museum-way", "clayton-street", "ashbury-street",
    },
}

# Datasets, per DATA-SOURCES.md.
DS_EAS = "3mea-di5p"
DS_ROLL = "wv5m-vpq2"
DS_PERMITS = "i98e-djp9"
DS_HISTORIC = "3tsw-4idn"
DS_DISTRICTS = "63x5-g3m4"


# --------------------------------------------------------------------------
# Socrata
#
# These datasets are big and their text columns are unindexed, so a bulk export
# ("give me every 2025 roll row in this neighborhood") reliably times out. What
# works is many small queries keyed on an indexed column — parcel number, APN,
# block — so every request returns well under a megabyte. Results are cached
# under .cache/, and each keyed fetch checkpoints after every batch so an
# interrupted run resumes instead of starting over.
# --------------------------------------------------------------------------
ROLL_SELECT = ",".join((
    "parcel_number", "block", "lot", "closed_roll_year", "year_property_built",
    "use_definition", "property_class_code_definition", "number_of_units",
    "number_of_rooms", "number_of_stories", "number_of_bathrooms", "number_of_bedrooms",
    "construction_type", "lot_area", "property_area", "basement_area", "lot_depth",
    "lot_frontage", "zoning_code", "assessed_land_value", "assessed_improvement_value",
    "assessed_fixtures_value", "current_sales_date", "property_location",
    "assessor_neighborhood", "analysis_neighborhood", "supervisor_district"))
HISTORIC_SELECT = ",".join((
    "apn", "ceqacode", "ceqacodea10a11", "ceqacodereason", "yearbuilt", "name",
    "lowstnum", "highstnum"))
PERMIT_SELECT = ",".join((
    "permit_number", "permit_type_definition", "status", "status_date", "filed_date",
    "permit_creation_date", "estimated_cost", "revised_cost", "description",
    "block", "lot", "street_number", "street_name", "street_suffix"))
DISTRICT_SELECT = "name_1,cr,nr,a10,a11,pos_1,description,the_geom"


def api_get(dataset: str, params: dict, timeout: int = 120, budget: int = 300,
            tries: int = 6) -> list:
    """One query, with a *total* time budget.

    Socrata sometimes accepts a request and then dribbles the body out over many
    minutes. urllib's timeout is per-read, so it never fires on a trickle and the
    fetch hangs forever. Reading in chunks against a wall-clock deadline turns
    that into an ordinary retryable failure.
    """
    url = f"https://data.sfgov.org/resource/{dataset}.json?" + urllib.parse.urlencode(params)
    for attempt in range(tries):
        try:
            deadline = time.time() + budget
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA),
                                        timeout=timeout) as r:
                buf = bytearray()
                while True:
                    if time.time() > deadline:
                        raise TimeoutError(
                            f"response still arriving after {budget}s ({len(buf)} bytes)")
                    chunk = r.read(65536)
                    if not chunk:
                        break
                    buf.extend(chunk)
            return json.loads(bytes(buf))
        except Exception as exc:  # noqa: BLE001 — any transport error is worth a retry
            if attempt == tries - 1:
                raise
            # Repeated failures here mean the API is rate-limiting us, and the
            # only useful response is to slow down properly — a short retry just
            # spends the next slot on another rejection.
            wait = (10, 30, 60, 120, 180)[min(attempt, 4)]
            print(f"    retry {attempt + 1}/{tries - 1} in {wait}s: {exc}",
                  file=sys.stderr, flush=True)
            time.sleep(wait)
    return []


def _quote_list(keys) -> str:
    return ",".join("'" + str(k).replace("'", "''") + "'" for k in keys)


def fetch_paged(name: str, dataset: str, select: str = None, where: str = None,
                page: int = 2000, refresh: bool = False) -> list:
    """Page a small dataset front to back."""
    CACHE.mkdir(exist_ok=True)
    path = CACHE / name
    if path.exists() and not refresh:
        return json.loads(path.read_text())
    rows, offset = [], 0
    while True:
        p = {"$order": ":id", "$limit": page, "$offset": offset}
        if select:
            p["$select"] = select
        if where:
            p["$where"] = where
        got = api_get(dataset, p)
        rows.extend(got)
        print(f"  {name}: {len(rows)} rows", file=sys.stderr, flush=True)
        if len(got) < page:
            break
        offset += page
    path.write_text(json.dumps(rows))
    return rows


def fetch_keyed(name: str, dataset: str, field: str, keys, select: str = None,
                where: str = None, chunk: int = 200, page: int = None,
                refresh: bool = False) -> list:
    """Fetch rows for a list of key values, a chunk at a time, resumably.

    `page` additionally pages *within* a chunk, for keys whose result set is
    too big to come back in one response (a downtown block's permits).
    """
    CACHE.mkdir(exist_ok=True)
    path, part = CACHE / name, CACHE / (name + ".partial")
    if path.exists() and not refresh:
        return json.loads(path.read_text())
    done: set = set()
    rows: list = []
    if part.exists() and not refresh:
        state = json.loads(part.read_text())
        done, rows = set(state["done"]), state["rows"]
        print(f"  {name}: resuming — {len(done)} key(s) already fetched",
              file=sys.stderr, flush=True)
    todo = [k for k in keys if k not in done]
    batches = [todo[i:i + chunk] for i in range(0, len(todo), chunk)]
    for i, batch in enumerate(batches, 1):
        clause = f"{field} in ({_quote_list(batch)})"
        print(f"  {name}: batch {i}/{len(batches)} ({len(batch)} keys)…",
              file=sys.stderr, flush=True)
        started, offset = time.time(), 0
        while True:
            p = {"$where": f"{where} AND {clause}" if where else clause,
                 "$limit": page or 50000, "$offset": offset, "$order": ":id"}
            if select:
                p["$select"] = select
            got = api_get(dataset, p)
            rows.extend(got)
            if not page or len(got) < page:
                break
            offset += page
            print(f"    …{offset} rows for this key so far", file=sys.stderr, flush=True)
        done.update(batch)
        part.write_text(json.dumps({"done": sorted(done), "rows": rows}))
        print(f"  {name}: batch {i}/{len(batches)} done in {time.time() - started:.0f}s "
              f"— {len(rows)} rows total", file=sys.stderr, flush=True)
        time.sleep(3)  # be a polite client; the API throttles hard when pushed
    path.write_text(json.dumps(rows))
    part.unlink()
    return rows


def nkey(neighborhood: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", neighborhood.lower()).strip("-")


def load_base(neighborhood: str, refresh: bool = False) -> dict:
    """Addresses, assessor roll, historic status and district polygons."""
    key = nkey(neighborhood)
    eas = fetch_paged(f"eas__{key}.json", DS_EAS, where=f"nhood='{neighborhood}'",
                      page=2000, refresh=refresh)
    parcels = sorted({r["parcel_number"] for r in eas if r.get("parcel_number")})
    roll_year = int(api_get(DS_ROLL, {"$select": "max(closed_roll_year)"})[0]
                    ["max_closed_roll_year"])
    roll = fetch_keyed(f"roll{roll_year}__{key}.json", DS_ROLL, "parcel_number", parcels,
                       select=ROLL_SELECT, where=f"closed_roll_year={roll_year}",
                       chunk=200, refresh=refresh)
    historic = fetch_keyed(f"historic__{key}.json", DS_HISTORIC, "apn", parcels,
                           select=HISTORIC_SELECT, chunk=400, refresh=refresh)
    districts = fetch_paged("districts.json", DS_DISTRICTS, select=DISTRICT_SELECT,
                            page=25, refresh=refresh)
    return {"eas": eas, "roll": roll, "roll_year": roll_year,
            "historic": historic, "districts": districts}


def load_permits(neighborhood: str, blocks, refresh: bool = False) -> list:
    """Permits for the given blocks, one block per request.

    Permit volume per block varies by an order of magnitude — a quiet
    residential block has a few hundred, a Market Street block has thousands —
    so batching blocks makes the worst request unpredictably large and it times
    out. One block at a time is more requests but every one of them lands.
    """
    return fetch_keyed(f"permits__{nkey(neighborhood)}.json", DS_PERMITS, "block",
                       sorted(blocks), select=PERMIT_SELECT, chunk=1, page=1500,
                       refresh=refresh)


# --------------------------------------------------------------------------
# Geometry — point in polygon, for naming the historic district
# --------------------------------------------------------------------------
def _in_ring(x: float, y: float, ring: list) -> bool:
    inside = False
    n = len(ring)
    for i in range(n):
        x1, y1 = ring[i][0], ring[i][1]
        x2, y2 = ring[(i + 1) % n][0], ring[(i + 1) % n][1]
        if (y1 > y) != (y2 > y):
            if x < (x2 - x1) * (y - y1) / (y2 - y1) + x1:
                inside = not inside
    return inside


def _in_geom(x: float, y: float, geom: dict = None) -> bool:
    if not geom:
        return False
    polys = geom["coordinates"] if geom.get("type") == "MultiPolygon" else [geom["coordinates"]]
    for poly in polys:
        if poly and _in_ring(x, y, poly[0]) and not any(_in_ring(x, y, h) for h in poly[1:]):
            return True
    return False


def _bbox(geom: dict = None):
    """Cheap reject box for a district — every parcel is tested against every
    district, and almost all of them miss."""
    if not geom:
        return None
    polys = geom["coordinates"] if geom.get("type") == "MultiPolygon" else [geom["coordinates"]]
    xs, ys = [], []
    for poly in polys:
        for ring in poly:
            for pt in ring:
                xs.append(pt[0])
                ys.append(pt[1])
    return (min(xs), min(ys), max(xs), max(ys)) if xs else None


def districts_at(lng: float, lat: float, districts: list) -> list:
    hits = []
    for d in districts:
        if "_bbox" not in d:
            d["_bbox"] = _bbox(d.get("the_geom"))
        box = d["_bbox"]
        if not box or not (box[0] <= lng <= box[2] and box[1] <= lat <= box[3]):
            continue
        if _in_geom(lng, lat, d.get("the_geom")):
            hits.append(d)
    return hits


REGISTER_RANK = {"Listed": 2, "Eligible": 1}


def _stronger(a: str = None, b: str = None) -> str:
    return a if REGISTER_RANK.get(a, 0) >= REGISTER_RANK.get(b, 0) else b


def merge_districts(hits: list) -> list:
    """Collapse a point's district hits into one entry per district name.

    The dataset holds several rows for some districts — Duboce Park has one row
    carrying its Article 10 designation and another carrying its California
    Register eligibility, over the same ground. Reading whichever came first
    would report "no local landmark protection" for a parcel that is in fact in
    an Article 10 district, so take the strongest status across the rows.
    """
    merged: dict = {}
    for h in hits:
        name = h.get("name_1")
        if not name:
            continue
        e = merged.setdefault(name, {"name": name, "cr": None, "nr": None,
                                     "a10": False, "a11": False, "pos": None})
        e["cr"] = _stronger(e["cr"], h.get("cr"))
        e["nr"] = _stronger(e["nr"], h.get("nr"))
        e["a10"] = e["a10"] or h.get("a10") == "Listed"
        e["a11"] = e["a11"] or h.get("a11") == "Listed"
        e["pos"] = e["pos"] or h.get("pos_1")
    # A district that confers local landmark protection leads.
    return sorted(merged.values(), key=lambda e: not (e["a10"] or e["a11"]))


# --------------------------------------------------------------------------
# Naming
# --------------------------------------------------------------------------
STREET_TYPE_WORD = {
    "ST": "street", "AVE": "avenue", "BLVD": "boulevard", "WAY": "way", "CT": "court",
    "TER": "terrace", "PL": "place", "DR": "drive", "LN": "lane", "ALY": "alley",
    "RD": "road", "HWY": "highway", "STWY": "stairway", "WALK": "walk", "PARK": "park",
    "CIR": "circle", "PLZ": "plaza", "ROW": "row", "PATH": "path", "STPS": "steps",
}
ORDINAL = re.compile(r"^\d+(ST|ND|RD|TH)$", re.I)


def street_slug(name: str, stype: str) -> str | None:
    word = STREET_TYPE_WORD.get((stype or "").upper())
    if not word:
        return None
    base = re.sub(r"[^a-z0-9]+", "-", (name or "").lower()).strip("-")
    return f"{base}-{word}" if base else None


def street_display(name: str, stype: str) -> str:
    word = STREET_TYPE_WORD.get((stype or "").upper(), (stype or "").lower())
    parts = []
    for token in (name or "").split():
        parts.append(token.lower() if ORDINAL.match(token) else token.capitalize())
    return " ".join(parts) + " " + word.capitalize()


def num_key(n: str):
    m = re.match(r"^(\d+)([A-Za-z]?)$", n or "")
    return (int(m.group(1)), m.group(2)) if m else (10 ** 9, n or "")


# --------------------------------------------------------------------------
# Value mapping — roll codes to the words a page shows
# --------------------------------------------------------------------------
def num(v, default=None):
    if v in (None, ""):
        return default
    try:
        f = float(v)
    except (TypeError, ValueError):
        return default
    return int(f) if f == int(f) else f


UNIT_WORD = {2: "Two", 3: "Three", 4: "Four"}


def article_for(year, phrase: str) -> str:
    """"an 1897 house" but "a 1901 house" — the article follows how the year is
    said aloud, and only the 1800s begin with a vowel sound."""
    if year:
        return "an" if str(year).startswith("18") else "a"
    return "an" if phrase[:1].lower() in "aeiou" else "a"


def building_type(pclass: str, units: int | None) -> str:
    """A short building-type phrase for the identity tag."""
    c = (pclass or "").lower()
    u = units or 0
    if "dwelling" in c and "2 dwellings" not in c and "apt" not in c:
        return "Single-family house"
    if "2 dwellings on 1 parcel" in c:
        return "Two dwellings on one parcel"
    if "town house" in c:
        return "Town house"
    if "flat & store" in c:
        return f"{u}-unit building with a ground-floor store" if u else \
            "Building with a ground-floor store"
    if "1 flat & 1 apt" in c:
        return "Flat and apartment building on one parcel"
    if "flats & duplex" in c:
        return f"{UNIT_WORD[u]}-flat" if u in UNIT_WORD else (
            f"{u}-unit flats building" if u else "Flats building")
    if "tic" in c:
        return f"{u}-unit TIC building" if u else "TIC building"
    if "apartment" in c or "apt" in c:
        return f"{u}-unit apartment building" if u else "Apartment building"
    return f"{u}-unit building" if u > 1 else "Residential building"


ZONING = {"RH1": "RH-1", "RH2": "RH-2", "RH3": "RH-3", "RH4": "RH-4",
          "RM1": "RM-1", "RM2": "RM-2", "RM3": "RM-3", "RM4": "RM-4",
          "RC3": "RC-3", "RC4": "RC-4", "NC1": "NC-1", "NC2": "NC-2", "NC3": "NC-3",
          "RH2RH3": "RH-2 / RH-3", "RH1D": "RH-1(D)", "RH1S": "RH-1(S)"}

CEQA_LABEL = {"A": "historic resource", "A*": "historic resource in a district",
              "B": "unevaluated", "C": "not a historical resource"}


def register_status(v: str = None) -> str:
    """State register status precisely — "eligible" is not "listed"."""
    return {"Listed": "Listed", "Eligible": "Eligible (not listed)"}.get(v, "Not listed")

CONSTRUCTION = {"D": "Wood frame", "WOO": "Wood frame"}

PILL = {  # DBI status -> (css class, icon, word, muted item?)
    "complete": ("pill-ok", "ic-check", "Complete", False),
    "issued": ("pill-warn", "ic-clock", "Issued", False),
    "filed": ("pill-warn", "ic-clock", "Filed", False),
    "filing": ("pill-warn", "ic-clock", "Filing", False),
    "approved": ("pill-warn", "ic-clock", "Approved", False),
    "reinstated": ("pill-warn", "ic-clock", "Reinstated", False),
    "expired": ("pill-muted", "ic-help", "Expired", True),
    "cancelled": ("pill-muted", "ic-help", "Cancelled", True),
    "withdrawn": ("pill-muted", "ic-help", "Withdrawn", True),
    "suspend": ("pill-muted", "ic-help", "Suspended", True),
    "disapproved": ("pill-muted", "ic-help", "Disapproved", True),
    "revoked": ("pill-muted", "ic-help", "Revoked", True),
}
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
          "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
MONTHS_LONG = ["January", "February", "March", "April", "May", "June", "July",
               "August", "September", "October", "November", "December"]


def ymd(v: str | None) -> str | None:
    return v[:10] if v else None


def month_year(iso: str | None) -> str:
    if not iso:
        return ""
    y, m = int(iso[:4]), int(iso[5:7])
    return f"{MONTHS[m - 1]} {y}"


def long_date(iso: str | None) -> str:
    if not iso:
        return ""
    y, m, d = int(iso[:4]), int(iso[5:7]), int(iso[8:10])
    return f"{MONTHS_LONG[m - 1]} {d}, {y}"


def cost_tier(amount: float) -> int:
    return 1 if amount < 5000 else (2 if amount <= 25000 else 3)


TIER_LABEL = {1: "Estimated cost under $5,000",
              2: "Estimated cost $5,000 to $25,000",
              3: "Estimated cost over $25,000"}


# --------------------------------------------------------------------------
# Permit descriptions
# --------------------------------------------------------------------------
# Only unambiguous, high-frequency DBI shorthand is expanded. The raw string
# stays in data.json, so a term left un-expanded is a readability miss, never a
# factual error — whereas guessing at an ambiguous abbreviation would be one.
ABBREV = [
    (r"\(n\)", "new"), (r"\(e\)", "existing"),
    (r"\bw/o\b", "without"), (r"\bw/", "with "),
    (r"\bextg\b|\bexstg\b|\bexst\b|\bexstng\b|\bexising\b", "existing"),
    (r"\bbldgs\b", "buildings"), (r"\bbldg\b", "building"),
    (r"\brepl\b|\breplc\b|\brplc\b", "replace"),
    (r"\brenov\b", "renovate"), (r"\baddn\b|\baddtn\b", "addition"),
    (r"\bfnd\b|\bfndn\b|\bfoundtn\b", "foundation"),
    (r"\bkitch\b|\bktchn\b", "kitchen"),
    (r"\bbthrm\b|\bbthrms\b|\bbthrmn\b", "bathroom"),
    (r"\belec\b|\belect\b|\belectr\b", "electrical"),
    (r"\bplmb\b|\bplbg\b|\bplmbg\b", "plumbing"),
    (r"\bmech\b", "mechanical"), (r"\bstrl\b|\bstructl\b", "structural"),
    (r"\bfxtrs\b", "fixtures"), (r"\bfxtr\b", "fixture"),
    (r"\blght\b|\blgt\b", "light"),
    (r"\bwndw\b|\bwdw\b", "window"), (r"\bwndws\b|\bwdws\b", "windows"),
    (r"\bflr\b", "floor"), (r"\bflrs\b", "floors"),
    (r"\bextr\b", "exterior"), (r"\bdemo\b", "demolition"),
    (r"\bre-?\s?roof(ing)?\b", "reroofing"),
    (r"\bsq\.?\s?ft\.?\b|\bsf\b", "sq ft"),
    (r"\bpa\s*#\s*", "permit application "),
    (r"\bpa\s+(?=\d{6,})", "permit application "),
    (r"\bdryrot\b", "dry rot"),
]


# DBI permit text sometimes names the owner, applicant, architect or contractor.
# The privacy rules in AGENTS.md bar all of those from a page, so the names are
# stripped before anything is written — they never reach data.json. The list
# lives in scripts/permit_redactions.json so it is reviewable in a diff.
REDACTIONS_PATH = ROOT / "scripts" / "permit_redactions.json"


def _load_redactions() -> list:
    if not REDACTIONS_PATH.exists():
        return []
    out = []
    for name in json.loads(REDACTIONS_PATH.read_text()).get("names", []):
        name = name.strip()
        if not name:
            continue
        body = re.escape(name).replace(r"\ ", r"\s+")
        # `\b` only means anything next to a word character. A name ending in a
        # period ("clear channel outdoor inc.") would never match with one.
        left = r"\b" if name[0].isalnum() else ""
        right = r"\b" if name[-1].isalnum() else ""
        out.append(re.compile(left + body + right, re.I))
    return out


REDACTIONS = _load_redactions()


# Permit text often pins work to a specific apartment ("apt 2:", "unit #3",
# "units 149, 151 and 153"). AGENTS.md bars apartment-level detail that points
# at who lives where, and the hand-authored pages genericize it, so the seeder
# does too: the number of units survives, the identifiers don't.
# One unit designator: "4", "12a", "502a", "1/2", "457 1/2".
_UNIT_NUM = r"\d+(?:\s*/\s*\d+)?[a-z]?(?:\s+\d+\s*/\s*\d+)?\b"
# A run of them after the keyword. The trailing \b matters: without it,
# "unit 2nd flr" matches as unit "2n" and the sentence gets mangled — with it,
# ordinals ("1st", "2nd") and street numbers ("4145 20th st") stay put.
# DBI also writes lists with the separators missing ("units 2, 3 5 & 6",
# "unit 2308 232"), so a bare space continues the run — except before "." or
# "/", which mark a numbered list item ("unit 502a 1. rehabilitate") or a floor
# ("unit #2 3/f only") rather than another unit.
UNIT_REF = re.compile(
    r"\b(?:apt|apartment|unit)s?\.?\s*#?\s*" + _UNIT_NUM +
    r"(?:\s*(?:,|&|and)\s*#?\s*" + _UNIT_NUM + r"|\s+#?" + _UNIT_NUM + r"(?![./]))*",
    re.I)
COUNT_WORD = {1: "one", 2: "two", 3: "three", 4: "four", 5: "five",
              6: "six", 7: "seven", 8: "eight", 9: "nine", 10: "ten"}


def _generic_unit(m) -> str:
    # Count designators, not digits — "unit 457 1/2" is one unit, not three.
    rest = re.sub(r"^(?:apt|apartment|unit)s?\.?\s*", "", m.group(0), flags=re.I)
    n = len(re.findall(_UNIT_NUM, rest, re.I))
    return "one unit" if n <= 1 else f"{COUNT_WORD.get(n, n)} units"


def generalize_units(text: str | None) -> str | None:
    return UNIT_REF.sub(_generic_unit, text) if text else text


def redact(text: str | None) -> str | None:
    """Remove any name on the redaction list, then tidy the wreckage.

    Cutting a name out mid-sentence leaves debris — a dangling "per", an empty
    pair of quotes, an unclosed bracket, doubled punctuation. Tidying only runs
    when a name was actually removed, so untouched text is never rewritten.
    """
    if not text:
        return text
    out = text
    for pattern in REDACTIONS:
        out = pattern.sub(" ", out)
    if out == text:
        return text

    out = re.sub(r"[\"“]\s*[\"”]", " ", out)     # emptied quotes
    out = re.sub(r"\(\s*\)|\[\s*\]", " ", out)             # emptied brackets
    if out.count("(") != out.count(")"):                   # now-unbalanced
        out = out.replace("(", " ").replace(")", " ")
    out = re.sub(r"\s{2,}", " ", out)
    # A connective whose object was the name now points at nothing.
    out = re.sub(r"\b(?:by|per|from|of|for|with|at|and|in)\b\s*(?=[.,;:]|$)", "", out,
                 flags=re.I)
    out = re.sub(r"\s+([,;.:])", r"\1", out)
    out = re.sub(r"([.,;:])\s*[.,;:]+", r"\1", out)        # doubled punctuation
    out = re.sub(r"(^|\.\s)\s*[,;:.]+\s*", r"\1", out)     # punctuation opening a clause
    out = re.sub(r"\s{2,}", " ", out)
    return out.strip(" ,;:-") or None


def clean_description(raw: str | None) -> str | None:
    """Turn DBI's abbreviated, uncased text into one plain sentence."""
    if not raw:
        return None
    s = " ".join(raw.split()).lower()
    for pattern, repl in ABBREV:
        s = re.sub(pattern, repl, s)
    s = re.sub(r"\s+([,;.:])", r"\1", s)
    s = re.sub(r"([,;:])(?=\S)", r"\1 ", s)
    s = re.sub(r"\s{2,}", " ", s).strip(" .,;:-")
    if not s:
        return None
    s = s[0].upper() + s[1:]
    return s + "."


WORK_PATTERNS = [
    (r"soft.?stor(y|ey)|seismic|retrofit", "a seismic retrofit"),
    (r"\bfoundation\b|underpin", "foundation work"),
    (r"\bhorizontal (addition|extension)\b|\brear addition\b|\badd(ition)? (at |to )?(the )?rear\b",
     "a rear addition"),
    (r"\bvertical addition\b|\badd (a )?(third|3rd|fourth|4th) (floor|story)\b",
     "a vertical addition"),
    (r"\baddition\b", "an addition"),
    (r"\bdormer\b", "a dormer"),
    (r"\badu\b|accessory dwelling", "an accessory dwelling unit"),
    (r"\bgarage\b", "garage work"),
    (r"\broof deck\b|\bdeck\b", "deck work"),
    (r"\bfire damage\b|\bfire repair\b", "fire repair"),
    (r"\breroofing\b|\broof\b", "reroofing"),
    (r"\bkitchen\b.*\bbath|bath.*\bkitchen\b", "a kitchen and bathroom remodel"),
    (r"\bkitchen\b", "a kitchen remodel"),
    (r"\bbathroom\b", "a bathroom remodel"),
    (r"\bdry rot\b", "dry-rot repair"),
    (r"\bfacade\b|\bsiding\b|\bstucco\b", "facade work"),
    (r"\bwindow", "window replacement"),
    (r"\bchimney\b", "chimney work"),
    (r"\bstair", "stair work"),
    (r"\bsewer\b|\bplumbing\b", "plumbing work"),
    (r"\belectrical\b", "electrical work"),
]


def work_phrase(permits: list) -> tuple[str, str] | None:
    """Pick the costliest substantive permit and describe it in a few words."""
    best = None
    for p in permits:
        cost = float(p.get("estimated_cost") or 0)
        desc = (p.get("description") or "").lower()
        if not desc:
            continue
        for pattern, phrase in WORK_PATTERNS:
            if re.search(pattern, desc):
                if best is None or cost > best[0]:
                    best = (cost, phrase, (p.get("filed") or "")[:4])
                break
    if not best or not best[2]:
        return None
    return best[1], best[2]


# --------------------------------------------------------------------------
# Building data.json
# --------------------------------------------------------------------------
def build_record(parcel: dict, ctx: dict) -> dict:
    """Assemble one page's data.json from the joined dataset rows."""
    roll = parcel["roll"]
    nums = parcel["numbers"]
    lead = nums[0]
    slug = parcel["street_slug"]
    disp = parcel["street_display"]
    addr_range = f"{nums[0]}–{nums[-1]}" if len(nums) > 1 and nums[0] != nums[-1] else None
    title = f"{addr_range or lead} {disp}"
    path = f"/{ctx['city']}/{ctx['area']}/{slug}/{lead.lower()}/"
    lat, lng = parcel["lat"], parcel["lng"]
    block, lot = roll.get("block"), roll.get("lot")
    apn = parcel["apn"]

    rec: dict = {
        "address": f"{title}, {ctx['city_display']}, {ctx['state']} {parcel['zip']}",
        "path": path,
        "apn": apn,
        "block": block,
        "lot": lot,
        "eas_baseid": parcel.get("eas_baseid"),
        "coordinates": {"lat": round(lat, 6), "lng": round(lng, 6)},
    }
    if addr_range:
        rec["address_range"] = addr_range
        rec["street_numbers_on_parcel"] = nums
    if parcel.get("other_street_addresses"):
        rec["also_addressed"] = parcel["other_street_addresses"]

    p: dict = {}
    for key, field in (("year_built", "year_property_built"), ("units", "number_of_units"),
                       ("stories", "number_of_stories"), ("rooms", "number_of_rooms"),
                       ("bathrooms", "number_of_bathrooms"), ("bedrooms", "number_of_bedrooms"),
                       ("lot_area_sqft", "lot_area"), ("building_area_sqft", "property_area"),
                       ("basement_area_sqft", "basement_area"), ("lot_depth_ft", "lot_depth"),
                       ("lot_frontage_ft", "lot_frontage")):
        v = num(roll.get(field))
        if v:
            p[key] = v
    p["use"] = roll.get("use_definition")
    p["property_class"] = roll.get("property_class_code_definition")
    if roll.get("construction_type"):
        p["construction_type_code"] = roll["construction_type"]
    if roll.get("zoning_code") and roll["zoning_code"] != "NA":
        p["zoning"] = ZONING.get(roll["zoning_code"], roll["zoning_code"])
    p["supervisor_district"] = num(roll.get("supervisor_district")) or num(parcel.get("supervisor"))
    p["assessor_neighborhood"] = roll.get("assessor_neighborhood")
    p["analysis_neighborhood"] = roll.get("analysis_neighborhood")
    if roll.get("property_location"):
        p["property_location_raw"] = roll["property_location"]
    rec["parcel"] = {k: v for k, v in p.items() if v not in (None, "")}

    a: dict = {"roll_year": ctx["roll_year"]}
    for key, field in (("assessed_land_value", "assessed_land_value"),
                       ("assessed_improvement_value", "assessed_improvement_value"),
                       ("assessed_fixtures_value", "assessed_fixtures_value")):
        v = num(roll.get(field))
        if v:
            a[key] = v
    if roll.get("current_sales_date"):
        a["last_sale_date"] = ymd(roll["current_sales_date"])
    rec["assessment"] = a

    h = ctx["historic"].get(apn)
    if h:
        code = (h.get("ceqacodea10a11") or h.get("ceqacode") or "").strip()
        base = (h.get("ceqacode") or "").strip()
        rec["historic_status"] = {k: v for k, v in {
            "ceqa_status_code": base or None,
            "ceqa_status_code_article_10_11": code or None,
            "ceqa_status_label": (CEQA_LABEL.get(base) or "").capitalize() or None,
            "reason": h.get("ceqacodereason") or None,
            "yearbuilt": h.get("yearbuilt") or None,
            "survey_name": h.get("name") or None,
            "in_article_10_11_historic_district": code == "A*",
            "source": "sf-planning",
        }.items() if v is not None}

    hits = merge_districts(districts_at(lng, lat, ctx["districts"]))
    if hits:
        def as_record(e):
            return {k: v for k, v in {
                "name": e["name"],
                "california_register_status": register_status(e["cr"]),
                "national_register_status": register_status(e["nr"]),
                "article_10_11_status": ("Article 10 historic district" if e["a10"] else
                                         "Article 11 conservation district" if e["a11"] else
                                         "No local landmark protection"),
                "local_landmark_protection": e["a10"] or e["a11"],
                "period_of_significance": (e["pos"] or "").replace("-", "–").replace(
                    " – ", "–") or None,
                "source": "sf-historic-districts",
            }.items() if v is not None}

        rec["historic_district"] = as_record(hits[0])
        if len(hits) > 1:
            rec["also_in_districts"] = [as_record(e) for e in hits[1:]]

    permits = []
    for r in parcel["permits"]:
        entry = {
            "number": r.get("permit_number"),
            "type": r.get("permit_type_definition"),
            "status": (r.get("status") or "").lower(),
            "filed": ymd(r.get("filed_date") or r.get("permit_creation_date")),
            "status_date": ymd(r.get("status_date")),
            "estimated_cost": num(r.get("estimated_cost")),
            "revised_cost": num(r.get("revised_cost")),
            "description": redact(generalize_units(r.get("description"))),
            "source": "sf-building-permits",
        }
        permits.append({k: v for k, v in entry.items() if v not in (None, "")})
    permits.sort(key=lambda x: (x.get("filed") or ""), reverse=True)
    rec["permits"] = permits

    q = urllib.parse.quote
    rec["sources"] = [
        {"id": "sf-eas-addresses",
         "name": "SF Enterprise Addressing System via DataSF",
         "query": (f"https://data.sfgov.org/resource/{DS_EAS}.json?street_name="
                   f"{q(parcel['street_name'])}&street_type={parcel['street_type']}"
                   f"&address_number={lead}"),
         "retrieved": ctx["retrieved"]},
        {"id": "sf-assessor-roll",
         "name": (f"SF Office of the Assessor-Recorder via DataSF "
                  f"({ctx['roll_year']} secured roll)"),
         "query": (f"https://data.sfgov.org/resource/{DS_ROLL}.json?parcel_number={apn}"
                   f"&$order=closed_roll_year%20DESC&$limit=1"),
         "retrieved": ctx["retrieved"]},
        {"id": "sf-building-permits",
         "name": "SF Dept. of Building Inspection via DataSF",
         "query": (f"https://data.sfgov.org/resource/{DS_PERMITS}.json?"
                   f"block={block}&lot={lot}"),
         "retrieved": ctx["retrieved"]},
    ]
    if h:
        rec["sources"].append(
            {"id": "sf-planning",
             "name": "SF Planning Department — Historic Resource Status by Parcel via DataSF",
             "query": f"https://data.sfgov.org/resource/{DS_HISTORIC}.json?apn={apn}",
             "retrieved": ctx["retrieved"]})
    if hits:
        rec["sources"].append(
            {"id": "sf-historic-districts",
             "name": "SF Planning Department — Historic Districts via DataSF",
             "query": (f"https://data.sfgov.org/resource/{DS_DISTRICTS}.json?$where="
                       f"intersects(the_geom,%20%27POINT({lng}%20{lat})%27)"),
             "retrieved": ctx["retrieved"]})

    return rec


# --------------------------------------------------------------------------
# Rendering index.html from data.json
# --------------------------------------------------------------------------
def esc(s) -> str:
    """Escape for text content — apostrophes stay readable in the source."""
    return html.escape(str(s), quote=False)


def esca(s) -> str:
    """Escape for an attribute value."""
    return html.escape(str(s), quote=True)


def indent_block(text: str, pad: str) -> str:
    return "\n".join(pad + line if line else line for line in text.split("\n"))


def feedback_url(title: str, path: str) -> str:
    return (f"{REPO}/issues/new?template=page-feedback.yml"
            f"&amp;title={urllib.parse.quote_plus('Feedback: ' + title)}"
            f"&amp;page={urllib.parse.quote(path, safe='')}")


def page_title(rec: dict) -> str:
    return rec["address"].split(",")[0]


def meta_description(rec: dict) -> str:
    p = rec.get("parcel", {})
    bits = [f"{page_title(rec)}, San Francisco:"]
    year = p.get("year_built")
    btype = building_type(p.get("property_class"), p.get("units")).lower()
    article = article_for(year, btype)
    bits.append(f"{article} {year} {btype}" if year else f"{article} {btype}")
    dist = district_of(rec).get("name")
    if dist:
        bits.append(f"in the {dist}")
    tail = "permits, " if rec.get("permits") else ""
    bits.append(f"— {tail}assessment and historic status from city records, fully cited.")
    return " ".join(bits)


def tags_html(rec: dict) -> str:
    p = rec.get("parcel", {})
    out = []
    if p.get("year_built"):
        out.append(("ic-calendar", f"Built {p['year_built']}"))
    out.append(("ic-home", building_type(p.get("property_class"), p.get("units"))))
    if p.get("stories"):
        s = p["stories"]
        out.append(("ic-layers", f"{s} stor{'y' if s == 1 else 'ies'}"))
    if p.get("zoning"):
        out.append(("ic-plan", f"Zoned {p['zoning']}"))
    if p.get("supervisor_district"):
        out.append(("ic-pin", f"District {p['supervisor_district']}"))
    hs = rec.get("historic_status") or {}
    label = CEQA_LABEL.get((hs.get("ceqa_status_code") or "").strip())
    if label:
        out.append(("ic-permit", f"Historic status: {label}"))
    return "\n".join(f'        <li class="tag"><span class="ic {i}"></span>{esc(t)}</li>'
                     for i, t in out)


def stats_html(rec: dict) -> str:
    p = rec.get("parcel", {})
    tiles = []
    if p.get("building_area_sqft"):
        tiles.append(("ic-plan", f"{p['building_area_sqft']:,}<small> sq ft</small>",
                      "Building area"))
    if p.get("lot_area_sqft"):
        tiles.append(("ic-lot", f"{p['lot_area_sqft']:,}<small> sq ft</small>", "Lot area"))
    rooms, bath, bed = p.get("rooms"), p.get("bathrooms"), p.get("bedrooms")
    if rooms:
        if bed and bath:
            label = f"Rooms · {bed} bed, {bath} bath"
        elif bath:
            label = f"Rooms · {bath} bath{'' if bath == 1 else 's'}"
        else:
            label = "Rooms"
        tiles.append(("ic-home", f"{rooms:,}", label))
    elif p.get("units") and p["units"] > 1:
        tiles.append(("ic-home", f"{p['units']:,}", "Residential units"))
    if not tiles:
        return ""
    body = "\n".join(
        f'    <div class="stat"><span class="ic {i}"></span>'
        f'<span class="stat-val">{v}</span>'
        f'<span class="stat-label">{esc(l)}</span></div>' for i, v, l in tiles)
    return f'  <div class="stats">\n{body}\n  </div>\n'


def timeline_html(rec: dict, indent: str) -> str:
    permits = rec.get("permits", [])
    shown, omitted = [], 0
    for p in permits:
        cost = p.get("estimated_cost") or p.get("revised_cost") or 0
        desc = (p.get("description") or "").lower()
        if cost <= 1 and re.search(r"street space|sidewalk", desc):
            omitted += 1
            continue
        shown.append(p)
    if not shown:
        return ""
    items = []
    for p in shown:
        css, icon, word, muted = PILL.get(p.get("status", ""),
                                          ("pill-warn", "ic-clock",
                                           (p.get("status") or "Filed").capitalize(), False))
        desc = clean_description(p.get("description")) or \
            f"{(p.get('type') or 'Permit').capitalize()}."
        cost = p.get("estimated_cost")
        if cost in (None, ""):
            cost = p.get("revised_cost")
        meta = [f'{indent}      <span class="pill {css}">'
                f'<span class="ic {icon}"></span>{esc(word)}</span>',
                f'{indent}      <a href="https://dbiweb02.sfgov.org/dbipts/default.aspx'
                f'?page=Permit&amp;PermitNumber={esca(p["number"])}">'
                f'Permit {esc(p["number"])}</a>']
        if cost:
            tier = cost_tier(float(cost))
            meta.append(f'{indent}      <span class="cost" data-tier="{tier}" '
                        f'aria-label="{TIER_LABEL[tier]}"><b>$</b><b>$</b><b>$</b></span>')
            meta.append(f'{indent}      <span class="cost-amt">${int(float(cost)):,}</span>')
        items.append(
            f'{indent}  <li class="vtl-item{" is-muted" if muted else ""}">\n'
            f'{indent}    <div class="vtl-date">{month_year(p.get("filed"))}</div>\n'
            f'{indent}    <p class="vtl-desc">{esc(desc)}</p>\n'
            f'{indent}    <div class="vtl-meta">\n' + "\n".join(meta) + "\n"
            f'{indent}    </div>\n'
            f'{indent}  </li>')
    out = (f'{indent}<div class="section-head"><span class="ic ic-clock"></span>'
           f'<h2>Permit history</h2></div>\n'
           f'{indent}<ol class="vtl">\n' + "\n".join(items) + f"\n{indent}</ol>\n")
    if omitted:
        word = "permit is" if omitted == 1 else "permits are"
        out += (f'{indent}<p class="prose"><small>{omitted} nominal $1 street-space '
                f'{word} omitted.</small></p>\n')
    return out


def value_panel_html(rec: dict, indent: str) -> str:
    a = rec.get("assessment", {})
    land = a.get("assessed_land_value")
    improv = a.get("assessed_improvement_value")
    if not land or not improv:
        return ""
    total = land + improv
    lp = round(land / total * 100, 1)
    ip = round(100 - lp, 1)
    return (
        f'{indent}<section class="panel">\n'
        f'{indent}  <h3>Assessed value · {a["roll_year"]} roll</h3>\n'
        f'{indent}  <ktp-figure>\n'
        f'{indent}    <div class="stack" role="group" aria-label="Assessed value breakdown">\n'
        f'{indent}      <div class="stack-seg seg-cool" style="width:{lp}%" tabindex="0" '
        f'data-tip="Land · ${land:,} · {lp}%" aria-label="Land, ${land:,}, {lp} percent"></div>\n'
        f'{indent}      <div class="stack-seg seg-warm" style="width:{ip}%" tabindex="0" '
        f'data-tip="Improvements · ${improv:,} · {ip}%" '
        f'aria-label="Improvements, ${improv:,}, {ip} percent"></div>\n'
        f'{indent}    </div>\n'
        f'{indent}    <div class="legend">\n'
        f'{indent}      <span class="legend-item"><span class="swatch seg-cool"></span>'
        f'<span>Land</span>&nbsp;<b>${land:,}</b></span>\n'
        f'{indent}      <span class="legend-item"><span class="swatch seg-warm"></span>'
        f'<span>Improvements</span>&nbsp;<b>${improv:,}</b></span>\n'
        f'{indent}    </div>\n'
        f'{indent}    <div class="legend" style="margin-top:.5rem"><span class="legend-item">'
        f'<span>Total assessed</span>&nbsp;<b>${total:,}</b></span></div>\n'
        f'{indent}  </ktp-figure>\n'
        f'{indent}</section>\n')


def glance_panel_html(rec: dict, indent: str) -> str:
    p = rec.get("parcel", {})
    a = rec.get("assessment", {})
    rows = []
    ctype = CONSTRUCTION.get(p.get("construction_type_code"))
    if ctype:
        rows.append(("ic-plan", "Construction", ctype))
    if rec.get("block") and rec.get("lot"):
        rows.append(("ic-pin", "Parcel", f"Block {rec['block']}, Lot {rec['lot']}"))
    if rec.get("street_numbers_on_parcel"):
        rows.append(("ic-home", "Street numbers", ", ".join(rec["street_numbers_on_parcel"])))
    if rec.get("also_addressed"):
        rows.append(("ic-pin", "Also addressed",
                     ", ".join(a.title() for a in rec["also_addressed"])))
    # Only when the building-type tag doesn't already carry the count
    # ("12-unit apartment building", "Two-flat") — never state a fact twice.
    units = p.get("units")
    if units and units > 1 and not re.search(
            r"\d|\bTwo\b|\bThree\b|\bFour\b", building_type(p.get("property_class"), units)):
        rows.append(("ic-layers", "Residential units", f"{units:,}"))
    if a.get("assessed_fixtures_value"):
        rows.append(("ic-value", "Assessed fixtures", f"${a['assessed_fixtures_value']:,}"))
    if a.get("last_sale_date"):
        rows.append(("ic-value", "Last sale", long_date(a["last_sale_date"])))
    hs = rec.get("historic_status") or {}
    code = (hs.get("ceqa_status_code") or "").strip()
    if code:
        rows.append(("ic-permit", "Historic status", f"CEQA {code} — {CEQA_LABEL.get(code, '')}"))
    if not rec.get("permits"):
        rows.append(("ic-clock", "Permits on file", "None"))
    if not rows:
        return ""
    body = "\n".join(
        f'{indent}    <div class="spec"><span class="ic {i}"></span>'
        f'<span class="spec-k">{esc(k)}</span>'
        f'<span class="spec-v">{esc(v)}</span></div>' for i, k, v in rows)
    return (f'{indent}<section class="panel">\n'
            f'{indent}  <h3>At a glance</h3>\n'
            f'{indent}  <dl class="speclist">\n{body}\n{indent}  </dl>\n'
            f'{indent}</section>\n')


def district_panel_html(rec: dict, indent: str) -> str:
    d = district_of(rec)
    if not d:
        return ""
    rows = []
    if d.get("california_register_status"):
        rows.append(("ic-permit", "California Register", d["california_register_status"]))
    if d.get("national_register_status"):
        rows.append(("ic-check", "National Register", d["national_register_status"]))
    if d.get("article_10_11_status"):
        rows.append(("ic-plan", "Local landmark protection",
                     "None" if d["article_10_11_status"].startswith("No local")
                     else d["article_10_11_status"]))
    if d.get("period_of_significance"):
        rows.append(("ic-calendar", "Period of significance", d["period_of_significance"]))
    for other in rec.get("also_in_districts", []):
        rows.append(("ic-pin", "Also within", other["name"]))
    body = "\n".join(
        f'{indent}    <div class="spec"><span class="ic {i}"></span>'
        f'<span class="spec-k">{esc(k)}</span>'
        f'<span class="spec-v">{esc(v)}</span></div>' for i, k, v in rows)
    return (f'{indent}<section class="panel">\n'
            f'{indent}  <h3>{esc(d["name"])}</h3>\n'
            f'{indent}  <dl class="speclist">\n{body}\n{indent}  </dl>\n'
            f'{indent}</section>\n')


def unknowns_html(rec: dict) -> str:
    p = rec.get("parcel", {})
    a = rec.get("assessment", {})
    missing = ["the architect and builder", "the early residents"]
    if not a.get("last_sale_date"):
        missing.append("the date of the last recorded sale")
    if not p.get("year_built"):
        missing.insert(0, "the year the building went up")
    listing = ", ".join(missing[:-1]) + f" and {missing[-1]}"
    note = ""
    hs = rec.get("historic_status") or {}
    hy, ry = hs.get("yearbuilt"), p.get("year_built")
    if hy and ry and str(hy) != str(ry):
        note = (f" The assessor dates the building to {ry}; Planning's historic "
                f"resource survey records {hy}.")
    url = feedback_url(page_title(rec), rec["path"])
    return ('  <div class="unknowns">\n'
            '    <span class="ic ic-help"></span>\n'
            f'    <p>Not yet documented: {listing}.{note}\n'
            f'    <a href="{url}">Know\n'
            '    any of it? Tell us — just describe it in plain words.</a></p>\n'
            '  </div>\n')


SOURCE_FOOTER_NAME = {
    "sf-assessor-roll": lambda n: n.replace(" (", ", ").replace(")", ""),
}


def sources_html(rec: dict) -> str:
    items = []
    for s in rec.get("sources", []):
        name = SOURCE_FOOTER_NAME.get(s["id"], lambda n: n)(s["name"]).replace(" — ", ", ")
        items.append(f'      <li>{esc(name)} —\n'
                     f'        <a href="{esca(s["query"])}">'
                     f'retrieved {s["retrieved"]}</a></li>')
    return "\n".join(items)


def render_html(rec: dict) -> str:
    title = page_title(rec)
    desc = meta_description(rec)
    lat, lng = rec["coordinates"]["lat"], rec["coordinates"]["lng"]
    zip_code = rec["address"].rsplit(" ", 1)[-1]
    parts = rec["path"].strip("/").split("/")
    city_slug, area_slug, street_slug_, number = parts
    city_name = " ".join(w.capitalize() for w in city_slug.split("-"))
    area_name = " ".join(w.capitalize() for w in area_slug.split("-"))
    # The street name comes off the address itself, so rendering never has to
    # reverse-engineer a slug.
    street_name = title.split(" ", 1)[1]
    sub_line = AREA_SUB.get((city_slug, area_slug), area_name)
    crumb_number = rec.get("address_range") or number
    permits = rec.get("permits", [])
    n_shown = len([p for p in permits
                   if not ((p.get("estimated_cost") or p.get("revised_cost") or 0) <= 1
                           and re.search(r"street space|sidewalk",
                                         (p.get("description") or "").lower()))])
    street_addr_plain = title.replace("–", "-")

    # Enough of a permit record to fill a column? Then split the region. A short
    # record runs full width, so a short page looks short rather than like a wide
    # page with an empty column.
    has_panels = bool(value_panel_html(rec, "") or glance_panel_html(rec, "")
                      or district_panel_html(rec, ""))
    use_cols = n_shown >= 4 and has_panels
    ind = "      " if use_cols else "  "
    panels = (value_panel_html(rec, ind) + glance_panel_html(rec, ind)
              + district_panel_html(rec, ind))
    timeline = timeline_html(rec, ind)

    if use_cols:
        body = ('  <div class="cols">\n    <div class="main">\n'
                + timeline
                + '    </div>\n\n    <aside class="aside">\n'
                + panels
                + '    </aside>\n  </div>\n')
    else:
        body = timeline + ("\n" if timeline and panels else "") + panels

    ld = {
        "@context": "https://schema.org",
        "@type": "Place",
        "name": title,
        "url": f"{SITE}{rec['path']}",
        "address": {"@type": "PostalAddress", "streetAddress": street_addr_plain,
                    "addressLocality": city_name, "addressRegion": "CA",
                    "postalCode": zip_code, "addressCountry": "US"},
        "geo": {"@type": "GeoCoordinates", "latitude": lat, "longitude": lng},
        "description": desc,
    }

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{esc(title)} — Know This Place</title>
  <meta name="description" content="{esca(desc)}">
  <link rel="canonical" href="{SITE}{rec['path']}">
  <link rel="stylesheet" href="/shared/site.css">
  <script type="module" src="/shared/site.js"></script>
  <script type="application/ld+json">
{indent_block(json.dumps(ld, indent=2, ensure_ascii=False), "  ")}
  </script>
</head>
<body>
<header class="site-header">
  <a class="wordmark" href="/">Know This Place</a>
  <nav class="breadcrumb" aria-label="Breadcrumb">
    <a href="/{city_slug}/">{esc(city_name)}</a>
    <a href="/{city_slug}/{area_slug}/">{esc(area_name)}</a>
    <a href="/{city_slug}/{area_slug}/{street_slug_}/">{esc(street_name)}</a>
    <span aria-current="page">{esc(crumb_number)}</span>
  </nav>
</header>

<main>
  <section class="hero">
    <div>
      <h1>{esc(title)}</h1>
      <p class="sub">{esc(sub_line)} · {esc(city_name)}, CA {zip_code}</p>
      <ul class="tags">
{tags_html(rec)}
      </ul>
    </div>
    <ktp-streetview location="{lat},{lng}" label="{esca(title)}">
      <figure class="media">
        <div class="media-empty">
          <span class="ic ic-pin"></span>
          <span>{lat:.4f}, {'−' if lng < 0 else ''}{abs(lng):.4f}</span>
          <small>Street View appears here once a Google Maps embed key is configured.</small>
        </div>
      </figure>
    </ktp-streetview>
  </section>

{stats_html(rec)}
{body}
{unknowns_html(rec)}</main>

<footer class="site-footer">
  <section class="sources">
    <h2>Sources</h2>
    <ul>
{sources_html(rec)}
    </ul>
  </section>
  <p class="feedback-cta">
    Know something about this place?
    <a href="{feedback_url(title, rec['path'])}">Tell us — just describe it in plain words.</a>
  </p>
  <p class="colophon">Part of <a href="/">Know This Place</a>, a community
  encyclopedia of the built environment. Facts are cited; pages are reviewed
  by people. <a href="{REPO}">Source</a>.</p>
</footer>
</body>
</html>
"""


# --------------------------------------------------------------------------
# Inventory
# --------------------------------------------------------------------------
RESIDENTIAL_USES = {"Single Family Residential", "Multi-Family Residential"}


def build_inventory(data: dict) -> list:
    """One row per parcel: its addresses, its roll record, and a verdict."""
    roll_by_parcel = {r["parcel_number"]: r for r in data["roll"] if r.get("parcel_number")}
    groups: dict = collections.defaultdict(list)
    for r in data["eas"]:
        pn = r.get("parcel_number")
        if pn and street_slug(r.get("street_name"), r.get("street_type")) \
                and r.get("latitude") and r.get("longitude"):
            groups[pn].append(r)

    rows = []
    for pn, addrs in groups.items():
        # EAS can hold two records for the same street number with marginally
        # different geocodes; break the tie on base ID so a re-run picks the
        # same one and coordinates don't drift between runs.
        addrs.sort(key=lambda a: (num_key(a.get("address_number", "")),
                                  a.get("eas_baseid", "")))
        # A corner parcel carries addresses on two streets. File it under the
        # street holding the most of them, and range only within that street —
        # otherwise "700–3999" would span two different roads.
        by_street: dict = collections.defaultdict(list)
        for a in addrs:
            by_street[(a["street_name"], a["street_type"])].append(a)
        (sname, stype), on_street = max(
            by_street.items(),
            key=lambda kv: (len(kv[1]), -num_key(kv[1][0].get("address_number", ""))[0]))
        lead = on_street[0]
        row = {
            "apn": pn,
            "street_slug": street_slug(sname, stype),
            "street_name": sname,
            "street_type": stype,
            "street_display": street_display(sname, stype),
            # EAS can hold more than one row for the same street number on a
            # parcel; dedupe or the range comes out as "3656–3656".
            "numbers": sorted({a.get("address_number", "") for a in on_street}, key=num_key),
            "other_street_addresses": [f"{a['address_number']} {a['street_name']} "
                                       f"{a['street_type']}" for a in addrs
                                       if (a["street_name"], a["street_type"]) != (sname, stype)],
            "lat": float(lead["latitude"]),
            "lng": float(lead["longitude"]),
            "zip": lead.get("zip_code"),
            "eas_baseid": lead.get("eas_baseid"),
            "supervisor": lead.get("supervisor"),
            "roll": roll_by_parcel.get(pn),
            "permits": [],
        }
        row["status"] = classify(row)
        rows.append(row)
    return rows


def attach_permits(inv: list, permits: list) -> None:
    """Join permits onto parcels by block+lot, and by street number for older
    records that carry an address but no block/lot."""
    by_bl: dict = collections.defaultdict(list)
    by_addr: dict = collections.defaultdict(list)
    for p in permits:
        by_bl[(p.get("block"), (p.get("lot") or "").lstrip("0"))].append(p)
        by_addr[((p.get("street_name") or "").upper().strip(),
                 (p.get("street_number") or "").lstrip("0"))].append(p)

    for row in inv:
        if row["status"] != "seedable":
            continue
        roll = row["roll"]
        cands = list(by_bl.get((roll.get("block"), (roll.get("lot") or "").lstrip("0")), []))
        for n in row["numbers"]:
            cands += by_addr.get((row["street_name"].upper(), n.lstrip("0")), [])
        seen, plist = set(), []
        for p in cands:
            pn = p.get("permit_number")
            if not pn or pn in seen:
                continue
            seen.add(pn)
            plist.append(p)
        row["permits"] = plist


def assessor_numbers(roll: dict) -> list:
    """Street numbers as the assessor writes them, e.g. ['30B', '30A'].

    `property_location` packs two street numbers into fixed five-character
    fields — "0030B0030AABBEY ST0000" is 30B and 30A. EAS gives both of those
    parcels the bare number 30, so this is the only field that tells them apart.
    """
    loc = roll.get("property_location") or ""
    out = []
    for i in (0, 5):
        field = loc[i:i + 5]
        m = re.fullmatch(r"(\d{4})([A-Z ])", field)
        if m and int(m.group(1)):
            out.append(f"{int(m.group(1))}{m.group(2).strip()}")
    return out


def classify(row: dict) -> str:
    roll = row["roll"]
    if roll is None:
        return "no-roll-record"
    # Condominium parcels are individual units with their own APN, not
    # buildings. AGENTS.md says skip them and flag for a human.
    if roll.get("property_class_code_definition") == "Condominium":
        return "condo-unit"
    if roll.get("use_definition") not in RESIDENTIAL_USES:
        return "non-residential"
    return "seedable"


# --------------------------------------------------------------------------
# Hub pages
# --------------------------------------------------------------------------
def district_of(rec: dict) -> dict:
    """The page's historic district, whichever shape it's recorded in.

    Generated pages put it at the top level; some earlier hand-authored pages
    nest it under `historic_status.district`.
    """
    return (rec.get("historic_district")
            or (rec.get("historic_status") or {}).get("district")
            or {})


def hub_lead(street_dir, fallback: str) -> str:
    """Reuse the hand-written intro from a street's existing index.md.

    A street hub's prose is a human's, and rebuilding the list of buildings
    beneath it must not throw that away. The first paragraph after the heading
    is the lead; if there isn't one, fall back to a plain generated sentence.
    """
    md = street_dir / "index.md"
    if not md.exists():
        return fallback
    para: list = []
    for line in md.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if stripped.startswith("#"):
            if para:
                break
            continue
        if not stripped:
            if para:
                break
            continue
        para.append(stripped)
    return " ".join(para) if para else fallback


def hook_for(rec: dict) -> str:
    # A hand-written hook in data.json always wins over a generated one.
    if rec.get("hook"):
        return rec["hook"]
    p = rec.get("parcel", {})
    year = p.get("year_built")
    btype = building_type(p.get("property_class"), p.get("units")).lower()
    article = article_for(year, btype).capitalize()
    head = f"{article} {year} {btype}" if year else f"{article} {btype}"
    dist = district_of(rec).get("name")
    if dist:
        head += f" in the {dist}"
    wp = work_phrase(rec.get("permits", []))
    if wp:
        phrase, yr = wp
        return f"{head}, with {phrase} permitted in {yr}."
    years = sorted((x.get("filed") or "")[:4] for x in rec.get("permits", []) if x.get("filed"))
    if len(years) > 1 and years[0] != years[-1]:
        return f"{head}, with permit records from {years[0]} to {years[-1]}."
    if years:
        return f"{head}, with one permit record from {years[0]}."
    # No permits: the page's own spec list says so. Repeating it on every line
    # of a hub would be noise, so the hook is just what the building is.
    return f"{head}."


def write_street_hub(street_dir: Path, ctx: dict, skipped: dict = None) -> None:
    """Rebuild a street's index.md + index.html from the pages beneath it."""
    recs = []
    for d in sorted(street_dir.iterdir(), key=lambda x: num_key(x.name)):
        f = d / "data.json"
        if d.is_dir() and f.exists():
            recs.append(json.loads(f.read_text()))
    if not recs:
        return
    slug = street_dir.name
    disp = page_title(recs[0]).split(" ", 1)[1]  # off the address, not the slug
    path = f"/{ctx['city']}/{ctx['area']}/{slug}/"
    area_name = " ".join(w.capitalize() for w in ctx["area"].split("-"))
    city_name = " ".join(w.capitalize() for w in ctx["city"].split("-"))

    years = sorted(r["parcel"]["year_built"] for r in recs if r.get("parcel", {}).get("year_built"))
    in_district = sum(1 for r in recs if district_of(r).get("name"))
    districts = collections.Counter(district_of(r)["name"]
                                    for r in recs if district_of(r).get("name"))
    n_permits = sum(len(r.get("permits", [])) for r in recs)

    entries = []
    for r in recs:
        number = r.get("address_range") or r["path"].strip("/").split("/")[-1]
        entries.append((number, r["path"].strip("/").split("/")[-1], page_title(r), hook_for(r)))

    tiles = [("ic-home", f"{len(recs):,}", "Buildings documented")]
    if years:
        span = (f"{years[0]}<small>–{years[-1]}</small>" if years[0] != years[-1]
                else f"{years[0]}")
        tiles.append(("ic-calendar", span, "Construction dates"))
    tiles.append(("ic-permit", f"{n_permits:,}", "Permit records"))
    if in_district:
        tiles.append(("ic-plan", f"{in_district:,}", "In a historic district"))

    lead = hub_lead(street_dir, f"Every residential parcel on {disp} that the city's "
                                f"address, assessor and permit records describe.")

    # What this street has that isn't a page, and why — replaces the hand-kept
    # "not yet covered" note with counts straight from the classifier.
    SKIP_WORDS = {
        "condo-unit": "condominium parcels, which are individual units rather than "
                      "buildings and are held back until the building each belongs to "
                      "can be established",
        "non-residential": "non-residential parcels",
        "no-roll-record": "parcels with no record in the assessor's roll",
    }
    uncovered = []
    for status, phrase in SKIP_WORDS.items():
        n = (skipped or {}).get(status, 0)
        if n:
            uncovered.append(f"{n} {phrase}")

    md = [f"# {disp}", "", lead, "", "## Documented so far", ""]
    for number, href, _title, hook in entries:
        md.append(f"- [{number}]({href}/) — {hook}")
    if uncovered:
        md += ["", "## Not yet covered", "",
               "Also on this street: " + "; ".join(uncovered) + "."]
    md += ["", "Pages are generated from the DataSF datasets listed in each page's",
           "Sources footer, and are corrected by hand as readers write in.", ""]
    (street_dir / "index.md").write_text("\n".join(md), encoding="utf-8")

    stat_html = "\n".join(
        f'    <div class="stat"><span class="ic {i}"></span><span class="stat-val">{v}</span>'
        f'<span class="stat-label">{esc(l)}</span></div>' for i, v, l in tiles)
    list_html = "\n".join(
        f'        <li><a href="{href}/">{esc(title)}</a><br>\n'
        f'          <span class="hook">{esc(hook)}</span></li>'
        for _n, href, title, hook in entries)
    aside = ""
    if districts:
        rows = "\n".join(
            f'          <div class="spec"><span class="ic ic-permit"></span>'
            f'<span class="spec-k">{esc(name)}</span>'
            f'<span class="spec-v">{count:,}</span></div>'
            for name, count in districts.most_common())
        aside += (f'      <section class="panel">\n'
                  f'        <h3>Historic districts on this street</h3>\n'
                  f'        <dl class="speclist">\n{rows}\n        </dl>\n'
                  f'      </section>\n')
    if uncovered:
        aside += (f'      <section class="panel">\n'
                  f'        <h3>Not yet covered</h3>\n'
                  f'        <p>Also on this street: {esc("; ".join(uncovered))}.</p>\n'
                  f'      </section>\n')
    desc = (f"Building-by-building pages for {disp} in {city_name}: {len(recs):,} "
            f"residential parcels with permits, assessments and historic status, "
            f"fully cited.")
    cols_open, cols_close = "", ""
    if aside:
        cols_open = '  <div class="cols">\n    <div class="main">\n'
        cols_close = f'    </div>\n\n    <aside class="aside">\n{aside}    </aside>\n  </div>\n'

    html_out = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{esc(disp)}, {esc(city_name)} — Know This Place</title>
  <meta name="description" content="{esca(desc)}">
  <link rel="canonical" href="{SITE}{path}">
  <link rel="stylesheet" href="/shared/site.css">
  <script type="module" src="/shared/site.js"></script>
</head>
<body>
<header class="site-header">
  <a class="wordmark" href="/">Know This Place</a>
  <nav class="breadcrumb" aria-label="Breadcrumb">
    <a href="/{ctx['city']}/">{esc(city_name)}</a>
    <a href="/{ctx['city']}/{ctx['area']}/">{esc(area_name)}</a>
    <span aria-current="page">{esc(disp)}</span>
  </nav>
</header>

<main>
  <h1>{esc(disp)}</h1>
  <p class="lead">{esc(lead)}</p>

  <div class="stats">
{stat_html}
  </div>

{cols_open}      <div class="section-head"><span class="ic ic-pin"></span><h2>Buildings</h2></div>
      <ul class="place-list">
{list_html}
      </ul>
{cols_close}</main>

<footer class="site-footer">
  <p class="feedback-cta">
    Live on {esc(disp)}, or know a building we should cover next?
    <a href="{feedback_url(disp, path)}">Tell us.</a>
  </p>
  <p class="colophon">Part of <a href="/">Know This Place</a>, a community
  encyclopedia of the built environment. Facts are cited; pages are reviewed
  by people. <a href="{REPO}">Source</a>.</p>
</footer>
</body>
</html>
"""
    (street_dir / "index.html").write_text(html_out, encoding="utf-8")


NEIGHBORHOOD_SECTION = "Streets documented so far"


def street_summary(street_dir: Path) -> tuple:
    """(display name, count, hook) for one street, read off its pages."""
    recs = [json.loads((d / "data.json").read_text())
            for d in street_dir.iterdir()
            if d.is_dir() and (d / "data.json").exists()]
    if not recs:
        return None
    disp = page_title(recs[0]).split(" ", 1)[1]
    years = sorted(r["parcel"]["year_built"] for r in recs
                   if r.get("parcel", {}).get("year_built"))
    hook = f"{len(recs):,} building{'' if len(recs) == 1 else 's'}"
    if years:
        hook += (f", built {years[0]}–{years[-1]}" if years[0] != years[-1]
                 else f", built {years[0]}")
    districts = collections.Counter(district_of(r)["name"]
                                    for r in recs if district_of(r).get("name"))
    if districts:
        name, count = districts.most_common(1)[0]
        hook += f"; {count:,} in the {name}"
    return disp, len(recs), hook + "."


def write_neighborhood_hub(area_dir: Path, ctx: dict) -> int:
    """Rewrite only the street list on a neighborhood hub.

    The rest of the page — the lead, the naming explanation, the closing note —
    is a human's prose and is left exactly as it is.
    """
    streets = []
    for street_dir in sorted(area_dir.iterdir()):
        if not street_dir.is_dir():
            continue
        summary = street_summary(street_dir)
        if summary:
            streets.append((street_dir.name, *summary))
    if not streets:
        return 0
    streets.sort(key=lambda s: s[1])

    md_path, html_path = area_dir / "index.md", area_dir / "index.html"
    if md_path.exists():
        text = md_path.read_text(encoding="utf-8")
        block = "\n".join(f"- [{disp}]({slug}/) — {hook}"
                          for slug, disp, _n, hook in streets)
        # A list item may wrap onto indented continuation lines — consume those
        # too, or the tail of the old entry survives the replacement.
        new, n = re.subn(
            rf"(## {re.escape(NEIGHBORHOOD_SECTION)}\n\n)"
            rf"(?:- .*\n(?:[ \t]+\S.*\n)*)+",
            lambda m: m.group(1) + block + "\n", text)
        if not n:
            raise SystemExit(f"{md_path}: no '## {NEIGHBORHOOD_SECTION}' list to replace")
        md_path.write_text(new, encoding="utf-8")

    if html_path.exists():
        text = html_path.read_text(encoding="utf-8")
        block = "\n".join(
            f'    <li><a href="{slug}/">{esc(disp)}</a><br>\n'
            f'      <span class="hook">{esc(hook)}</span></li>'
            for slug, disp, _n, hook in streets)
        new, n = re.subn(
            rf"(<h2>{re.escape(NEIGHBORHOOD_SECTION)}</h2></div>\s*"
            rf'<ul class="place-list">\n)(.*?)(\n  </ul>)',
            lambda m: m.group(1) + block + m.group(3), text, flags=re.S)
        if not n:
            raise SystemExit(f"{html_path}: no '{NEIGHBORHOOD_SECTION}' list to replace")
        html_path.write_text(new, encoding="utf-8")
    return len(streets)


# --------------------------------------------------------------------------
# Commands
# --------------------------------------------------------------------------
def make_ctx(args, data: dict) -> dict:
    return {
        "city": args.city, "area": args.area,
        "city_display": " ".join(w.capitalize() for w in args.city.split("-")),
        "state": "CA",
        "roll_year": data["roll_year"],
        "retrieved": args.retrieved or date.today().isoformat(),
        "historic": {h["apn"]: h for h in data["historic"] if h.get("apn")},
        "districts": data["districts"],
    }


def existing_pages_by_apn() -> dict:
    """APN -> page path, across the whole content tree.

    One building is one page, site-wide. A parcel already documented under
    another neighborhood directory must not be seeded a second time here.
    """
    index = {}
    for f in sorted(ROOT.rglob("san-francisco/**/data.json")):
        try:
            rec = json.loads(f.read_text())
        except json.JSONDecodeError:
            continue
        apn = (rec.get("apn") or "").replace("-", "")
        if apn:
            index[apn] = "/" + f.parent.relative_to(ROOT).as_posix() + "/"
    return index


def load_all(args, with_permits: bool = True):
    """Everything the seeder needs: base datasets, inventory, permits attached."""
    data = load_base(args.neighborhood, refresh=getattr(args, "refresh", False))
    inv = build_inventory(data)
    if with_permits:
        blocks = {r["roll"]["block"] for r in inv
                  if r["status"] == "seedable" and (r["roll"] or {}).get("block")}
        attach_permits(inv, load_permits(args.neighborhood, blocks,
                                         refresh=getattr(args, "refresh", False)))
    return data, inv


def cmd_fetch(args) -> int:
    load_all(args)
    print("cache ready in .cache/")
    return 0


def cmd_plan(args) -> int:
    data, inv = load_all(args, with_permits=False)
    counts = collections.Counter(r["status"] for r in inv)
    print(f"roll year: {data['roll_year']}")
    print(f"parcels: {len(inv)}")
    for k, v in counts.most_common():
        print(f"  {v:>6}  {k}")
    by_street = collections.Counter(r["street_slug"] for r in inv if r["status"] == "seedable")
    print("\nseedable by street:")
    for k, v in sorted(by_street.items(), key=lambda kv: -kv[1]):
        print(f"  {v:>6}  {k}")
    print(f"\nTOTAL seedable: {sum(by_street.values())}")
    return 0


def cmd_seed(args) -> int:
    data, inv = load_all(args)
    ctx = make_ctx(args, data)
    only = set(args.street or [])
    excluded = AREA_EXCLUDE_STREETS.get((args.city, args.area), set()) | set(args.skip_street or [])
    covered = existing_pages_by_apn()
    written, skipped, elsewhere, touched_streets = 0, 0, 0, set()
    # Per-street counts of what was deliberately not turned into a page.
    not_covered: dict = collections.defaultdict(collections.Counter)
    for row in inv:
        if row["status"] != "seedable" and row["street_slug"]:
            not_covered[row["street_slug"]][row["status"]] += 1

    # Two parcels can share a street number — EAS gives 229 Douglass to both a
    # 1907 house and the 2008 one the assessor calls 229A. Writing both to the
    # same directory silently loses one, and inventing "229a" would create an
    # address the canonical EAS list doesn't have. So the parcel the assessor
    # numbers plainly keeps the page and its lettered sibling is deferred for a
    # human, the same way condominium parcels are.
    targets: dict = collections.defaultdict(list)
    for row in inv:
        if row["status"] != "seedable" or row["street_slug"] in excluded:
            continue
        if only and row["street_slug"] not in only:
            continue
        lead = row["numbers"][0].lower()
        targets[(row["street_slug"], lead)].append(row)
    deferred: dict = {}
    for (slug, lead), rows in targets.items():
        if len(rows) < 2:
            continue
        plain = [r for r in rows if lead.upper() in assessor_numbers(r["roll"] or {})]
        keep = plain[0] if len(plain) == 1 else None
        for r in rows:
            if r is not keep:
                deferred[r["apn"]] = (
                    f"{lead} {r['street_display']} — parcel {r['apn']} shares this "
                    f"street number; the assessor calls it "
                    f"{'/'.join(assessor_numbers(r['roll'] or {})) or 'unnumbered'}")

    for row in inv:
        if row["status"] != "seedable":
            continue
        if only and row["street_slug"] not in only:
            continue
        if row["street_slug"] in excluded:
            continue
        if row["apn"] in deferred:
            continue
        rec = build_record(row, ctx)
        prior_path = covered.get(row["apn"])
        if prior_path and prior_path != rec["path"]:
            # Already documented under another neighborhood directory.
            elsewhere += 1
            continue
        page_dir = ROOT / rec["path"].strip("/")
        existing = page_dir / "data.json"
        if existing.exists() or (page_dir / "index.html").exists():
            # The page exists. It belongs to whoever edits it next, by hand.
            skipped += 1
            touched_streets.add(page_dir.parent)
            continue
        page_dir.mkdir(parents=True, exist_ok=True)
        existing.write_text(json.dumps(rec, indent=2, ensure_ascii=False) + "\n",
                            encoding="utf-8")
        (page_dir / "index.html").write_text(render_html(rec), encoding="utf-8")
        written += 1
        touched_streets.add(page_dir.parent)

    for street_dir in sorted(touched_streets):
        write_street_hub(street_dir, ctx, not_covered.get(street_dir.name))
    n_streets = write_neighborhood_hub(ROOT / args.city / args.area, ctx)
    print(f"neighborhood hub lists {n_streets} street(s)")
    print(f"created {written} new page(s); left {skipped} existing page(s) "
          f"untouched; skipped {elsewhere} parcel(s) already documented under "
          f"another neighborhood; rebuilt {len(touched_streets)} street hub(s)")
    if excluded:
        print(f"excluded streets (filed under another neighborhood): "
              f"{', '.join(sorted(excluded))}")
    if deferred:
        print(f"deferred for a human — {len(deferred)} parcel(s) share a street "
              f"number with another parcel:")
        for note in sorted(deferred.values()):
            print(f"  {note}")
    return 0


# Deliberately over-broad: it is cheap to review a false positive and costly to
# publish a real name, so this catches role labels, firm suffixes and titles and
# leaves the judgement to a reviewer.
NAME_HINT = re.compile(
    r"\b(owner|owners|attn|attention|applicant|contact|c/o|architect|architects|"
    r"engineer|engineering|contractor|contracting|tenant|landlord|purchaser|"
    r"mr|mrs|ms|dr)\b[.:]?\s+\S"
    r"|\b(inc|llc|l\.l\.c|corp|corporation|company|associates|assoc|builders|"
    r"construction|develop(ment|ers)|partners|group|realty|properties)\b"
    r"|\b[a-z]{3,}'s\b", re.I)


def cmd_names(args) -> int:
    """List distinct permit descriptions that may carry a person or firm name.

    Review the output and add real names to scripts/permit_redactions.json.
    """
    _, inv = load_all(args)
    seen = set()
    for row in inv:
        if row["status"] != "seedable":
            continue
        for p in row["permits"]:
            d = " ".join((p.get("description") or "").split())
            if d:
                seen.add(d)
    cands = sorted(d for d in seen if NAME_HINT.search(d))
    print(f"# {len(seen)} distinct descriptions, {len(cands)} flagged for review")
    for d in cands:
        print(d)
    return 0


def cmd_hubs(args) -> int:
    ctx = make_ctx(args, {"roll_year": args.roll_year, "historic": [], "districts": []})
    area_dir = ROOT / args.city / args.area
    n = 0
    for street_dir in sorted(area_dir.iterdir()):
        if street_dir.is_dir():
            write_street_hub(street_dir, ctx)
            n += 1
    n_streets = write_neighborhood_hub(area_dir, ctx)
    print(f"rebuilt {n} street hub(s); neighborhood hub lists {n_streets} street(s)")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    def common(p, neighborhood_required=True):
        p.add_argument("--neighborhood", required=neighborhood_required,
                       help="EAS/Planning analysis neighborhood, e.g. 'Castro/Upper Market'")
        p.add_argument("--city", default="san-francisco")
        p.add_argument("--area", default="castro")
        p.add_argument("--retrieved", default=None,
                       help="retrieval date to record in sources (default: today)")

    p = sub.add_parser("fetch", help="cache the DataSF datasets for a neighborhood")
    common(p)
    p.add_argument("--refresh", action="store_true")
    p.set_defaults(fn=cmd_fetch)

    p = sub.add_parser("plan", help="classify parcels without writing anything")
    common(p)
    p.add_argument("--refresh", action="store_true")
    p.set_defaults(fn=cmd_plan)

    p = sub.add_parser("seed", help="write data.json + index.html for every seedable parcel")
    common(p)
    p.add_argument("--refresh", action="store_true")
    p.add_argument("--street", action="append", help="limit to a street slug (repeatable)")
    p.add_argument("--skip-street", action="append",
                   help="exclude a street slug, e.g. one filed under another "
                        "neighborhood directory (repeatable)")
    p.set_defaults(fn=cmd_seed)

    p = sub.add_parser("names", help="list permit descriptions that may name a person or firm")
    common(p)
    p.add_argument("--refresh", action="store_true")
    p.set_defaults(fn=cmd_names)

    p = sub.add_parser("hubs", help="rebuild street hub pages from the pages beneath them")
    common(p, neighborhood_required=False)
    p.add_argument("--roll-year", type=int, default=2025)
    p.set_defaults(fn=cmd_hubs)

    args = ap.parse_args()
    return args.fn(args)


if __name__ == "__main__":
    sys.exit(main())
