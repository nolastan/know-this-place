#!/usr/bin/env python3
"""Seed and re-render address pages from the DataSF APIs. Stdlib only.

Two commands write address pages, and what separates them is the page that
already exists:

- **`seed` creates, and only creates.** It writes the first draft of a page
  that doesn't exist yet — nothing more. Every fact on a fresh address page
  comes from an API, so producing that draft is a data job, not a writing one.
  A directory that already holds a `data.json` is skipped, whether the page was
  seeded a minute ago or written by a person last year.
- **`render` re-renders, and only re-renders.** `data.json` is the source of
  truth for an address page and `index.html` is its build artifact, so `render`
  rewrites the artifact from the source in place: change a fact in `data.json`,
  run `render` on the path, and never open the HTML. It is idempotent — a
  second run over the same path changes nothing — and it reads nothing but the
  `data.json` files it is pointed at, so it needs no network and no cache.

A page whose HTML a person genuinely maintains by hand sets `"rendered": false`
in its `data.json`. `render` skips it and `validate.py` skips its parity check,
which also means it stops picking up site-wide design changes and goes stale
silently. That is a real cost, so `validate.py` prints how many pages have
taken the opt-out on every run.

`render` does not touch hub pages: a page's `hook` reaches its street hub
through `hubs`, which is a separate command for the separate reason that hubs
are assembled from many pages at once.

Usage:
  python3 scripts/seed_pages.py fetch --neighborhood "Castro/Upper Market"
  python3 scripts/seed_pages.py plan  --neighborhood "Castro/Upper Market"
  python3 scripts/seed_pages.py seed  --neighborhood "Castro/Upper Market" \
                                      --city san-francisco --area castro
  python3 scripts/seed_pages.py seed-list --manifest research/manifests/popos-public-art.json
  python3 scripts/seed_pages.py render san-francisco/castro/castro-street/744
  python3 scripts/seed_pages.py render san-francisco          # the whole city
  python3 scripts/seed_pages.py names --neighborhood "Castro/Upper Market"
  python3 scripts/seed_pages.py hubs  --city san-francisco --area castro
"""
from __future__ import annotations

import argparse
import collections
import functools
import html
import json
import math
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

# An address page's directory is its bare street number: `4127`, `4127a`. Hub
# directories (city, neighborhood, street) never match, which is what makes
# "walk this path and render the address pages under it" unambiguous.
# `validate.py` imports this rather than keeping a second copy.
ADDRESS_DIR = re.compile(r"^\d+[a-z]?$")

# Site icons. `shared/icon.svg` is the source of truth for the mark; the raster
# files are derived from it. Every page carries these, the way it carries the
# shared stylesheet — `validate.py` enforces it.
ICON_LINKS = """  <link rel="icon" href="/favicon.ico" sizes="32x32">
  <link rel="icon" href="/shared/icon.svg" type="image/svg+xml">
  <link rel="apple-touch-icon" href="/apple-touch-icon.png">
  <link rel="manifest" href="/shared/site.webmanifest">"""

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
    "block", "lot", "street_number", "street_name", "street_suffix", "location"))
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
    # `keys` can be empty — a neighborhood name that matches no EAS row, say —
    # in which case no batch ran and no `.partial` was ever written. Cleaning up
    # a file that was never created is not an error.
    part.unlink(missing_ok=True)
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
# DBI abbreviates street types differently from EAS — EAS writes AVE/CIR/TER/WAY,
# DBI writes Av/Cr/Tr/Wy — so the two can only be compared through a shared
# token. Mapping DBI's spelling onto the same words `STREET_TYPE_WORD` already
# uses for EAS gives that token without a second parallel vocabulary to keep in
# step. Both vocabularies were read off the live datasets; DBI's tail (Sq, Cg,
# So, No) has no EAS counterpart, and `type_key` leaves those as themselves.
PERMIT_TYPE_WORD = {
    "ST": "street", "AV": "avenue", "BL": "boulevard", "DR": "drive", "WY": "way",
    "TR": "terrace", "CT": "court", "PL": "place", "LN": "lane", "HY": "highway",
    "RD": "road", "PZ": "plaza", "CR": "circle", "PK": "park", "AL": "alley",
    "SW": "stairway", "RW": "row", "WK": "walk", "HL": "hill", "PG": "passage",
}
ORDINAL = re.compile(r"^\d+(ST|ND|RD|TH)$", re.I)
# EAS zero-pads the single-digit numbered streets — "03RD", "05TH" — so they
# sort as text. The city doesn't: the street is Third Street, and the directory
# contract wants "3rd-street". Padding survives into a slug and a page title
# unless it is stripped here, which is how "03rd Street" reached a first draft.
PADDED_ORDINAL = re.compile(r"^0+(\d(ST|ND|RD|TH))$", re.I)
# Single-digit numbered streets are spelled out in San Francisco addresses
# ("601 Third Street"); two-digit ones are not ("1010 14th Street").
ORDINAL_WORD = {"1ST": "First", "2ND": "Second", "3RD": "Third", "4TH": "Fourth",
                "5TH": "Fifth", "6TH": "Sixth", "7TH": "Seventh", "8TH": "Eighth",
                "9TH": "Ninth"}


def unpad(token: str) -> str:
    m = PADDED_ORDINAL.match(token or "")
    return m.group(1) if m else token


def type_key(stype: str, permit: bool = False) -> str:
    """One street type, in a spelling EAS and DBI can be compared in.

    Returns "" for a missing type. `attach_permits` treats that as a wildcard on
    the permit side — 15,982 DBI rows carry an address with no suffix at all,
    and a handful of streets (Broadway, The Embarcadero) genuinely have none —
    so an absent suffix must not be read as evidence of a *different* street.
    """
    raw = (stype or "").strip().upper()
    if not raw:
        return ""
    table = PERMIT_TYPE_WORD if permit else STREET_TYPE_WORD
    return table.get(raw, raw)


def street_slug(name: str, stype: str) -> str | None:
    # A few streets have no type at all — EAS files South Park with an empty
    # `street_type`, because the street is called South Park and nothing else.
    # An unrecognized type is still a reason to skip the row; a missing one is
    # not, and treating them the same drops every address on such a street.
    word = "" if not (stype or "").strip() else STREET_TYPE_WORD.get(stype.upper())
    if word is None:
        return None
    name = " ".join(unpad(t) for t in (name or "").split())
    base = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    if not base:
        return None
    return f"{base}-{word}" if word else base


def street_display(name: str, stype: str) -> str:
    word = STREET_TYPE_WORD.get((stype or "").upper(), (stype or "").lower())
    parts = []
    for token in (name or "").split():
        token = unpad(token)
        spelled = ORDINAL_WORD.get(token.upper())
        if spelled:
            parts.append(spelled)
        else:
            parts.append(token.lower() if ORDINAL.match(token) else token.capitalize())
    return (" ".join(parts) + " " + word.capitalize()).strip()


def alias_display(addr: str) -> str:
    """Render one `also_addressed` string the way the page renders its own street.

    EAS stores these whole — "2071 03RD ST" — so titlecasing them yields
    "2071 03Rd St". Split off the number and hand the rest to `street_display`,
    which unpads the ordinal and spells it: "2071 Third Street".

    A researcher who added an alias by hand wrote it in display form already
    ("216 Beale Street"); anything not in EAS's all-caps spelling is left as it
    stands rather than round-tripped through a parse it was never in.
    """
    number, _, rest = (addr or "").strip().partition(" ")
    if not rest or rest != rest.upper():
        return addr
    tokens = rest.split()
    stype = tokens[-1] if len(tokens) > 1 and tokens[-1] in STREET_TYPE_WORD else ""
    name = " ".join(tokens[:-1] if stype else tokens)
    return f"{number} {street_display(name, stype)}".strip()


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
    if "apartment" in c and "store" in c:
        return f"{u}-unit apartment building with a ground-floor store" if u else \
            "Apartment building with a ground-floor store"
    if "apartment" in c or "apt" in c:
        return f"{u}-unit apartment building" if u else "Apartment building"
    commercial = commercial_type(c)
    if commercial:
        return commercial
    # Unrecognized class code — say only what the unit count supports, since a
    # parcel here may be commercial as easily as residential.
    return f"{u}-unit building" if u > 1 else "Building"


def commercial_type(c: str) -> str | None:
    """The same phrase for the non-residential classes on the assessor's roll.

    Downtown parcels are offices, hotels, garages and department stores, and the
    residential ladder above has nothing to say about them — without this every
    office tower would be tagged "Residential building".
    """
    if "office" in c and "retail" in c:
        return "Office building with ground-floor retail"
    if "office" in c and "condominium" in c:
        return "Office condominium"
    if "office" in c:
        return "Office building"
    if "hotel" in c or "motel" in c:
        return "Hotel"
    if "shopping center" in c:
        return "Shopping center"
    if "department store" in c:
        return "Department store"
    if "bank" in c:
        return "Bank building"
    if "school" in c:
        return "School building"
    if "church" in c:
        return "Church"
    if "theater" in c or "theatre" in c:
        return "Theater"
    if "restaurant" in c:
        return "Restaurant building"
    if "warehouse" in c:
        return "Warehouse"
    if "garage" in c:
        return "Garage"
    # Say whose word this is. The roll classes a parcel carrying a park rather
    # than a building as a vacant lot — Redwood Park and Empire Park both read
    # that way — and an unqualified "Vacant lot" tag would tell a reader the
    # site is empty, which is the opposite of true.
    if "parking lot" in c:
        return "Assessor class: parking lot"
    if "vacant lot" in c:
        return "Assessor class: vacant lot"
    if "store" in c:
        return "Store building"
    if "industrial" in c or "light indust" in c:
        return "Industrial building"
    return None


ZONING = {"RH1": "RH-1", "RH2": "RH-2", "RH3": "RH-3", "RH4": "RH-4",
          "RM1": "RM-1", "RM2": "RM-2", "RM3": "RM-3", "RM4": "RM-4",
          "RC3": "RC-3", "RC4": "RC-4", "NC1": "NC-1", "NC2": "NC-2", "NC3": "NC-3",
          "RH2RH3": "RH-2 / RH-3", "RH1D": "RH-1(D)", "RH1S": "RH-1(S)"}

CEQA_LABEL = {"A": "historic resource", "A*": "historic resource in a district",
              "B": "unevaluated", "C": "not a historical resource"}

# Planning's `ceqacodereason` is a comma-separated list of findings, and it
# mixes two different subjects: the district a parcel sits in (which the
# district panel renders) and designations that attach to the building itself.
# Only the second kind belongs in the tags, and without it a landmarked
# building inherits its district's verdict — 573 Castro Street is an Article 10
# landmark inside a district that is only California Register-eligible, so the
# page said its local landmark protection was none.
INDIVIDUAL_DESIGNATION = {
    "Article 10 Individual Landmark": ("ic-check", "City landmark (Article 10)"),
    # Not a designation: the work program is the Historic Preservation
    # Commission's list of candidates. The data says so — a parcel whose only
    # local finding is the work program stays CEQA "A", never the "A*" that
    # every actually-designated Article 10 landmark carries — so name the
    # program rather than promoting it to a landmark.
    "Article 10 Individual Landmark Work Program":
        ("ic-clock", "Landmark designation work program (Article 10)"),
    "National Register Individual": ("ic-check", "Individually listed on the "
                                                 "National Register"),
    # "Article 11 Individual" is deliberately absent. It is the fourth
    # individual token in the field and it is not settled enough to state as a
    # tag: 78 of the 118 pages carrying it already render a concrete Article 11
    # rating in their survey panel, and 12 of those ratings are Category V
    # — unrated — which no wording of "individually rated" survives. Naming the
    # rating is a survey question, and `historic_survey` already answers it
    # where a survey has been read onto the page.
}


def individual_designations(rec: dict) -> list:
    """(icon, label) for each building-level designation in `historic_status`.

    Matched token by token, never as a substring: "Article 10 Individual
    Landmark Work Program" contains "Article 10 Individual Landmark" and means
    the opposite of it.
    """
    reason = ((rec.get("historic_status") or {}).get("reason") or "")
    return [INDIVIDUAL_DESIGNATION[t] for t in
            (x.strip() for x in reason.split(","))
            if t in INDIVIDUAL_DESIGNATION]


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


MONTH_NUM = {m.lower(): i + 1 for i, m in enumerate(MONTHS)}
MONTH_NUM.update({m.lower(): i + 1 for i, m in enumerate(MONTHS_LONG)})


def date_key(when: str | None) -> tuple:
    """Sort key for one timeline date, oldest first.

    A page's single timeline mixes city records, which carry an ISO date, with
    historical ones, which carry whatever the source knew: a bare year, a
    decade ("1930s"), a span ("1890–1900"), a hedge ("circa 1885", "pre-1906").
    So this reads a year, then a month and day if they're there, and orders on
    what it found: within a year, the vaguer entry comes first ("1906" before
    "Apr 1906"), and a "pre-"/"before" hedge comes before that. Anything with
    no year at all sorts last rather than silently landing in antiquity.
    """
    s = (when or "").strip()
    if not s:
        return (9999, 99, 99)
    m = re.match(r"(\d{4})-(\d{2})(?:-(\d{2}))?$", s)
    if m:
        return (int(m[1]), int(m[2]), int(m[3] or 0))
    year = re.search(r"\b(1[6-9]\d{2}|20\d{2})", s)
    if not year:
        return (9999, 99, 99)
    if re.search(r"\bpre-|\bbefore\b", s, re.I):
        return (int(year[1]), -1, -1)
    month = next((MONTH_NUM[w.lower()] for w in re.findall(r"[A-Za-z]{3,9}", s)
                  if w.lower() in MONTH_NUM), 0)
    day = re.search(r"\b(\d{1,2})(?:st|nd|rd|th)?,", s) or (
        month and re.search(r"\b(\d{1,2})\s+[A-Za-z]{3,9}", s))
    return (int(year[1]), month, int(day[1]) if day else 0)


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
# One numbered designator: "4", "12a", "502a", "1/2", "457 1/2".
_UNIT_NUM = r"\d+(?:\s*/\s*\d+)?[a-z]?(?:\s+\d+\s*/\s*\d+)?\b"
# DBI letters units as often as it numbers them ("unit a:", "apt #c"), and a
# bare letter is a far more dangerous thing to match than a digit — one-letter
# English words and DBI's slashed abbreviations wear the same shape. So the
# letter form is deliberately narrow, and every narrowing is something the
# corpus actually contains:
#   * only "a" through "h", the range these letters run in. Past it lie
#     "units w/ garage" (with), "unit. n/a", "unit. u factor", "unit #s: 143",
#     "unit r-3" (occupancy class) — all abbreviation, none a designator.
#   * never glued to the keyword, so "unite" and "unita" aren't read as
#     "unit e" and "unit a" (the lookbehind is what enforces the gap, since
#     the "#" and whitespace between keyword and designator are optional).
#   * never before "/", where a leading letter is half of an abbreviation
#     pair: "hvac units. f/s sep permit", "a/c". Deeper into a list that
#     ambiguity is gone, so "unit a & b/remove kitchen" keeps its "b".
_UNIT_LETTER = r"(?<![a-z])[a-h]\b(?!/)"
_UNIT_LETTER_MORE = r"(?<![a-z])[a-h]\b"
_UNIT_DESIG = r"(?:" + _UNIT_NUM + r"|" + _UNIT_LETTER_MORE + r")"
# DBI doubles its separators too ("units b,c,& e"), so the run absorbs a pair.
_SEP = r"\s*(?:,\s*&|,\s*and|,|&|and)\s*"
# A run of them after the keyword. The trailing \b matters: without it,
# "unit 2nd flr" matches as unit "2n" and the sentence gets mangled — with it,
# ordinals ("1st", "2nd") and street numbers ("4145 20th st") stay put.
# DBI also writes lists with the separators missing ("units 2, 3 5 & 6",
# "unit 2308 232"), so a bare space continues a numbered run — except before
# "." or "/", which mark a numbered list item ("unit 502a 1. rehabilitate") or
# a floor ("unit #2 3/f only") rather than another unit.
_NUM_RUN = (_UNIT_NUM + r"(?:" + _SEP + r"#?\s*" + _UNIT_NUM +
            r"|\s+#?" + _UNIT_NUM + r"(?![./]))*")
# A lettered run is stricter on both counts. It needs a separator throughout —
# "unit a b" appears nowhere, while "unit a only" appears everywhere — and a
# number may join it only wearing a "#" ("apts a,b,c,d and #1087"), because
# without one the number after the list is an address: "units a & b, 743 green
# st" is two units on Green Street, not three units.
_LETTER_RUN = (_UNIT_LETTER + r"(?:" + _SEP + r"#?\s*" + _UNIT_LETTER_MORE +
               r"|" + _SEP + r"#\s*" + _UNIT_NUM + r")*")
# DBI also punctuates the "#" itself ("unit #:233", "apt#: 3"), and the colon
# is allowed only there — never straight after the keyword, where "one unit: 1.
# rehabilitate ..." would read its list marker as a designator.
UNIT_REF = re.compile(
    r"\b(?:apt|apartment|unit)s?\.?\s*(?:#\s*:?\s*)?(?:" + _NUM_RUN + r"|" + _LETTER_RUN + r")",
    re.I)
COUNT_WORD = {1: "one", 2: "two", 3: "three", 4: "four", 5: "five",
              6: "six", 7: "seven", 8: "eight", 9: "nine", 10: "ten"}


def _generic_unit(m) -> str:
    # Count designators, not digits — "unit 457 1/2" is one unit, not three.
    rest = re.sub(r"^(?:apt|apartment|unit)s?\.?\s*", "", m.group(0), flags=re.I)
    n = len(re.findall(_UNIT_DESIG, rest, re.I))
    return "one unit" if n <= 1 else f"{COUNT_WORD.get(n, n)} units"


def generalize_units(text: str | None) -> str | None:
    return UNIT_REF.sub(_generic_unit, text) if text else text


# In a hotel — and above all in a residential hotel or SRO, where the room is
# the home — a room number is a dwelling identifier exactly as an apartment
# number is, and AGENTS.md bars both. DBI writes them constantly: "repair fire
# damage to room #227 & 204" (240 Jones, the Roosevelt).
#
# The rewrite is confined to parcels the assessor's roll files as a hotel,
# because that gate is what separates a dwelling identifier from a room named
# by its function. Measured over every published data.json, a "room <number>"
# pattern matches 111 pages; on the 55 that are not hotels it is almost
# always a building description a page should keep — "storage room #1 (aka
# media room)" in a Castro house, "exam room #3" in a clinic, "operating rooms
# 1,2,3,4,6" in a hospital, "living room #1 - #3" in a flat. Widening past the
# roll's own classification would rewrite those, so it isn't done here; the
# apartment buildings whose "room #63" really is a dwelling are left for a
# person to decide, one page at a time.
HOTEL_USE = "Commercial Hotel"
# The narrowings, each one something the hotel corpus actually contains:
#   * a room type named right before the keyword is a room, not a home. Every
#     word here precedes a numbered room somewhere in the DBI export; "bath"
#     is deliberately absent, because inside a hotel "bth rms 201-205" and
#     "bathrms in & adj to rms 120, 220 & 320" number the guest rooms.
ROOM_TYPE_WORD = {
    "bed", "boiler", "break", "breakout", "class", "computer", "conference",
    "dining", "display", "elec", "electrical", "engine", "exam", "fam",
    "family", "furnace", "game", "jacuzzi", "laundry", "liv", "living",
    "locker", "machine", "massage", "mech", "mechanical", "media", "meeting",
    "mud", "music", "office", "operating", "piano", "powder", "pump",
    "purpose", "rest", "sauna", "server", "service", "shower", "steam",
    "stock", "storage", "storge", "study", "studio", "sun", "supply", "tool",
    "training", "treatment", "utility", "wash",
}
#   * a qualifier that says "dwelling" is absorbed into the replacement rather
#     than left in front of it, so "hotel rooms 806 and 807" becomes "two
#     hotel rooms" and not "hotel two rooms".
DWELLING_WORD = {"guest", "guess", "hotel", "sleeping"}
#   * a number that measures is not a number that identifies: "tool room 69 sq
#     ft" is an area, "room 12' x 15'" is a dimension, and a list can run
#     straight into one ("rms 113,114,115,116,117,118, 720 sq ft").
_NOT_MEASURE = (r"(?!\s*(?:sqft|sq|sf|s\.\s?f|feet|ft|square)\b)"
                r"(?!\s*['\"])")
#   * DBI hyphenates room numbers, as a range ("rooms 100-121") and as a list
#     ("bth rms 201-205-302-303-304-305"), a shape it never uses for units.
#     The hyphen must join two numbers: before a word it is a dash ("room
#     #248-close partition wall"), and before "/f" it marks a floor ("room
#     6-2/f", which is room 6 on the second floor, not rooms 6 through 2).
_ROOM_NUM = (_UNIT_NUM + _NOT_MEASURE +
             r"(?:\s*-\s*" + _UNIT_NUM + _NOT_MEASURE + r"(?!/))*")
_ROOM_RUN = (_ROOM_NUM + r"(?:" + _SEP + r"#?\s*" + _ROOM_NUM +
             r"|\s+#?" + _ROOM_NUM + r"(?![./]))*")
# No lettered branch, unlike UNIT_REF: the hotel corpus holds no "room a", and
# a bare letter after "room" is likelier one of DBI's abbreviations. The
# abbreviation may carry its own period ("rm. 248-close partition wall",
# "rm.#206"); the spelled-out word may not, except in front of "#", because
# "room." otherwise ends a sentence and the number after it opens the next one
# ("powder room. 338 sq ft of new habitable space") — the mistake that makes
# generalize_units non-idempotent (#250).
ROOM_REF = re.compile(
    r"(?:\b(?P<qual>[a-z]+)\s+)?\b(?:rms?\.?|rooms?(?:\.(?=\s*#))?)"
    r"\s*(?:#\s*:?\s*)?(?P<desig>" + _ROOM_RUN + r")", re.I)
# Counts are spelled out, never written as digits, so that the rewrite can
# never produce text it would rewrite again: "toilet rooms guest room 501,505,
# ..." ends "... rooms sixteen guest rooms", where a digit would have left a
# fresh "rooms 16" for the next pass to eat. A run longer than this table
# drops to the bare plural for the same reason; the longest in the corpus is
# 19, so that branch is unreached today.
ROOM_COUNT_WORD = COUNT_WORD | {
    11: "eleven", 12: "twelve", 13: "thirteen", 14: "fourteen",
    15: "fifteen", 16: "sixteen", 17: "seventeen", 18: "eighteen",
    19: "nineteen", 20: "twenty"}


def _generic_room(m) -> str:
    qual = m.group("qual") or ""
    if qual.lower() in ROOM_TYPE_WORD:
        return m.group(0)
    if qual.lower() in DWELLING_WORD:
        lead, kind = "", f"{qual.lower()} room"
    else:
        lead, kind = (f"{qual} " if qual else ""), "room"
    desig = m.group("desig")
    n = 0 if "-" in desig else len(re.findall(_UNIT_NUM, desig))
    if n == 0 or n not in ROOM_COUNT_WORD:
        return f"{lead}{kind}s"
    return lead + (f"one {kind}" if n == 1 else f"{ROOM_COUNT_WORD[n]} {kind}s")


def generalize_rooms(text: str | None, *, hotel: bool) -> str | None:
    """Genericize room numbers, but only on a hotel parcel — see HOTEL_USE."""
    return ROOM_REF.sub(_generic_room, text) if text and hotel else text


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
    # A connective whose object was the name now points at nothing — either at
    # the end of the clause, or at a second connective that led the rest of the
    # sentence ("notice by john sims on 12-12-2001" leaves "notice by on …").
    out = re.sub(r"\b(?:by|per|from|of|for|with|at|and|in|as)\b\s*(?=[.,;:]|$)", "", out,
                 flags=re.I)
    out = re.sub(r"\b(?:by|per|from|of|for|with|as)\s+(?=(?:by|per|from|of|for|with|at|in|on|as|and|to)\b)",
                 "", out, flags=re.I)
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
PERMIT_TIMELINE_MAX = 24


def _permit_cost(p: dict) -> float:
    return max(float(p.get("estimated_cost") or 0), float(p.get("revised_cost") or 0))


def trim_permits(permits: list) -> tuple:
    """Reduce a parcel's permit record to a timeline a person can read.

    A house files a permit every few years; a downtown office tower files one
    per tenant per floor, and DBI holds 3,102 of them for 1 Market Street. Every
    one is a real record, but a 3,102-item timeline is not a page — and the
    figures a reader wants (what was built, what it cost) are drowned by fit-out
    after fit-out. So the page carries the largest filings by stated cost plus
    the earliest on file, and `permit_summary` states how many exist and by what
    rule these were chosen. The DBI query in `sources` returns all of them.

    Nominal $1 street-space and sidewalk-occupancy permits are counted here
    rather than shown, which is what the hand-authored pages do.
    """
    nominal, rest = [], []
    for p in permits:
        desc = (p.get("description") or "").lower()
        (nominal if _permit_cost(p) <= 1 and re.search(r"street space|sidewalk", desc)
         else rest).append(p)
    filed = sorted(x["filed"][:4] for x in permits if x.get("filed"))
    span = (f"{filed[0]}–{filed[-1]}" if filed and filed[0] != filed[-1]
            else (filed[0] if filed else None))

    if len(rest) <= PERMIT_TIMELINE_MAX:
        if not nominal:
            return rest, None
        word = "permit is" if len(nominal) == 1 else "permits are"
        return rest, {k: v for k, v in {
            "count_on_file": len(permits), "range": span,
            "shown_on_page": len(rest),
            "note": (f"{len(nominal)} nominal $1 street-space or sidewalk "
                     f"{word} omitted from the timeline."),
        }.items() if v is not None}

    ranked = sorted(rest, key=_permit_cost, reverse=True)[:PERMIT_TIMELINE_MAX]
    keep = {p["number"] for p in ranked}
    oldest = min((p for p in rest if p.get("filed")),
                 key=lambda p: p["filed"], default=None)
    if oldest and oldest["number"] not in keep:
        ranked.append(oldest)
        keep.add(oldest["number"])
    ranked.sort(key=lambda x: (x.get("filed") or ""), reverse=True)
    note = (f"DBI holds {len(permits):,} permits for this parcel, most of them "
            f"tenant improvements on individual floors. The timeline shows the "
            f"{PERMIT_TIMELINE_MAX} largest by stated cost"
            + (", plus the earliest on file" if oldest and oldest in ranked else "")
            + f"; the DBI query in the sources below returns all {len(permits):,}.")
    if nominal:
        note += (f" {len(nominal):,} of them are nominal $1 street-space or "
                 f"sidewalk permits.")
    return ranked, {k: v for k, v in {
        "count_on_file": len(permits), "range": span,
        "shown_on_page": len(ranked), "note": note,
    }.items() if v is not None}


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
    is_hotel = p.get("use") == HOTEL_USE
    for r in parcel["permits"]:
        entry = {
            "number": r.get("permit_number"),
            "type": r.get("permit_type_definition"),
            "status": (r.get("status") or "").lower(),
            "filed": ymd(r.get("filed_date") or r.get("permit_creation_date")),
            "status_date": ymd(r.get("status_date")),
            "estimated_cost": num(r.get("estimated_cost")),
            "revised_cost": num(r.get("revised_cost")),
            "description": redact(generalize_rooms(
                generalize_units(r.get("description")), hotel=is_hotel)),
            "source": "sf-building-permits",
        }
        permits.append({k: v for k, v in entry.items() if v not in (None, "")})
    permits.sort(key=lambda x: (x.get("filed") or ""), reverse=True)
    rec["permits"], summary = trim_permits(permits)
    if summary:
        rec["permit_summary"] = summary

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
    # No year built here: it is a dated fact, so it opens the timeline instead
    # (see `built_item`).
    out.append(("ic-home", building_type(p.get("property_class"), p.get("units"))))
    if p.get("stories"):
        s = p["stories"]
        out.append(("ic-layers", f"{s} stor{'y' if s == 1 else 'ies'}"))
    if p.get("zoning"):
        out.append(("ic-plan", f"Zoned {p['zoning']}"))
    if p.get("supervisor_district"):
        out.append(("ic-pin", f"District {p['supervisor_district']}"))
    if rec.get("public_open_space"):
        n = len(rec["public_open_space"])
        out.append(("ic-pin", "Privately owned public open space"
                    + (f" ×{n}" if n > 1 else "")))
    hs = rec.get("historic_status") or {}
    label = CEQA_LABEL.get((hs.get("ceqa_status_code") or "").strip())
    if label:
        out.append(("ic-permit", f"Historic status: {label}"))
    # After the CEQA classification, which is the general finding: a
    # designation is the specific one, and it is the building's own.
    out.extend(individual_designations(rec))
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


def permit_items(rec: dict, indent: str) -> tuple:
    """(items, disclosure) — the permit half of the timeline.

    Each item is a `(date_key, html)` pair so it can be interleaved with the
    historical entries; `disclosure` is the line about filings deliberately
    left out, which belongs under the finished rail.
    """
    permits = rec.get("permits", [])
    # Pages written before `permit_summary` existed still carry their nominal
    # $1 street-space filings in `permits`; drop those here as before.
    note = (rec.get("permit_summary") or {}).get("note")
    shown, omitted = [], 0
    for p in permits:
        cost = p.get("estimated_cost") or p.get("revised_cost") or 0
        desc = (p.get("description") or "").lower()
        if not note and cost <= 1 and re.search(r"street space|sidewalk", desc):
            omitted += 1
            continue
        shown.append(p)
    disclosure = ""
    if note:
        disclosure = f'{indent}<p class="prose"><small>{esc(note)}</small></p>\n'
    elif omitted:
        word = "permit is" if omitted == 1 else "permits are"
        disclosure = (f'{indent}<p class="prose"><small>{omitted} nominal $1 '
                      f'street-space {word} omitted.</small></p>\n')
    if not shown:
        return [], ""
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
        items.append((date_key(p.get("filed")),
            f'{indent}  <li class="vtl-item{" is-muted" if muted else ""}">\n'
            f'{indent}    <div class="vtl-date">{month_year(p.get("filed"))}</div>\n'
            f'{indent}    <p class="vtl-desc">{esc(desc)}</p>\n'
            f'{indent}    <div class="vtl-meta">\n' + "\n".join(meta) + "\n"
            f'{indent}    </div>\n'
            f'{indent}  </li>'))
    return items, disclosure


DEMOLITION = re.compile(r"\bdemoli", re.I)
# Work inside or beside a building that stayed up: "interior demolition",
# "demolish non-bearing partitions", "demolish storage shed".
PARTIAL_DEMOLITION = re.compile(r"interior|non-? ?structural|partition|\bshed\b|partial", re.I)


def built_item(rec: dict, indent: str) -> list:
    """The assessor's year built, as the entry the rest of the timeline hangs off.

    It was a "Built 1896" tag in the hero until issue #132: a dated fact
    standing outside the one sequence a reader reads dates in, which left every
    rail starting at whichever permit DBI happened to keep.

    "Current structure built" only where the record shows the parcel was
    cleared first — a whole building demolished on a permit filed before the
    assessor's year and not cancelled, withdrawn or expired. That is the sole
    signal this reads, deliberately: 1,484 pages carry something dated earlier
    than their build year, and on all but a fraction of them it is this
    building's own design or construction, attributed a few years before the
    roll's rounded year ("Designed by Ernest Coxhead", 1895, under a build year
    of 1900). Calling that a previous structure would be a claim no source
    made. 162 pages meet the demolition test.
    """
    year = (rec.get("parcel") or {}).get("year_built")
    if not year:
        return []
    replaced = any(
        date_key(p.get("filed"))[0] < int(year)
        and DEMOLITION.search(p.get("description") or "")
        and not PARTIAL_DEMOLITION.search(p.get("description") or "")
        # A demolition that was cancelled, withdrawn or expired is a plan, not
        # a cleared lot — the rail mutes those items for the same reason.
        and not PILL.get(p.get("status", ""), ("", "", "", False))[3]
        for p in rec.get("permits") or [])
    return [((int(year), 0, 0),
             f'{indent}  <li class="vtl-item">\n'
             f'{indent}    <div class="vtl-date">{year}</div>\n'
             f'{indent}    <p class="vtl-desc">'
             f'{"Current structure built." if replaced else "Built."}</p>\n'
             f'{indent}  </li>')]


def timeline_html(rec: dict, indent: str) -> str:
    """The page's one timeline: every dated entry on a single rail, oldest first.

    The year the building went up, its permits and its historical records are
    the same kind of thing to a reader — something that happened here on a date
    — so they share one `.vtl` and interleave by date rather than sitting in
    two rails that each restart the clock.

    No heading. The rail carried a "Permit history" one while it could hold
    nothing else, and it is neither true now (every page with a build year
    opens with it) nor needed: a timeline is self-evident on sight. The name
    stays for screen readers, on `aria-label`.
    """
    built = built_item(rec, indent)
    permits, disclosure = permit_items(rec, indent)
    earlier = historical_items(rec, indent)
    if not (built or permits or earlier):
        return ""
    # `sorted` is stable and `built` leads the list, so the building's own year
    # comes before anything else the same year — a permit filed in the month it
    # was finished, a photograph dated to the year.
    items = [html for _, html in sorted(built + permits + earlier, key=lambda e: e[0])]
    return (f'{indent}<ol class="vtl" aria-label="Timeline">\n' + "\n".join(items)
            + f"\n{indent}</ol>\n" + disclosure)


def value_panel_html(rec: dict, indent: str) -> str:
    a = rec.get("assessment", {})
    land = a.get("assessed_land_value")
    improv = a.get("assessed_improvement_value")
    if not land or not improv:
        return ""
    total = land + improv
    lp = round(land / total * 100, 1)
    ip = round(100 - lp, 1)
    # No panel chrome and no heading: the legend already names land,
    # improvements and the total, and the Sources footer names the roll, so a
    # "Assessed value · 2025 roll" heading above them says nothing the figure
    # doesn't. The bare section reads better than a boxed one.
    return (
        f'{indent}<section>\n'
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


def narrative_html(rec: dict, indent: str) -> tuple:
    """(lead, sections) — the page's prose, rendered verbatim from `narrative`.

    Returned as two pieces because they belong in different places: the lead sits
    under the hero, the sections after the timeline.
    """
    n = rec.get("narrative") or {}
    lead = ""
    if n.get("lead"):
        paras = "\n".join(f'  <p class="lead">{esc(p)}</p>'
                          for p in n["lead"].split("\n") if p.strip())
        lead = paras + "\n"
    out = []
    for s in n.get("sections") or []:
        body = "\n".join(f'{indent}<p class="prose">{esc(p)}</p>'
                         for p in (s.get("body") or "").split("\n") if p.strip())
        out.append(f'{indent}<div class="section-head"><span class="ic ic-link"></span>'
                   f'<h2>{esc(s["heading"])}</h2></div>\n{body}\n')
    if n.get("community_note"):
        out.append(f'{indent}<div class="community-note">'
                   f'<p>{esc(n["community_note"])}</p></div>\n')
    return lead, "\n".join(out)


def historical_items(rec: dict, indent: str) -> list:
    """`historical_record` as `(date_key, html)` items for the page's timeline.

    One dated fact per entry, from a historical source rather than a city
    dataset. It is a timeline entry, not prose, so a page that gains three of
    these gains no paragraphs — and no second rail either: they take their
    place among the permits in date order.

    An entry's `source` may be a list where one dated event left several
    records — the assessor shot four negatives of a corner parcel on the same
    afternoon, one per street number. That is one thing that happened here, so
    it is one item; the records are cited side by side on it, each labelled
    with the address it was filed under. Never one item per record: a reader
    scanning the rail should not meet the same date twice.
    """
    entries = rec.get("historical_record") or []
    if not entries:
        return []
    # `label` is the short form a timeline entry cites; the full citation is in
    # the Sources footer, and repeating it under every item would swamp them.
    labels = {s["id"]: s.get("label") or s.get("name", s["id"])
              for s in rec.get("sources", [])}
    # A photograph is an item the reader can go and look at, so its meta links
    # to the record the way a permit's links to the permit. Other historical
    # entries cite a document *about* the building; that is attribution, and
    # attribution lives in the Sources footer.
    urls = {s["id"]: s["query"] for s in rec.get("sources", []) if s.get("query")}
    # `title` distinguishes co-dated records of one event — the street number
    # each negative was filed under.
    titles = {s["id"]: s["title"] for s in rec.get("sources", []) if s.get("title")}
    items = []
    for e in entries:
        cited = e.get("source")
        cited = [s for s in (cited if isinstance(cited, list) else [cited]) if s]
        meta = labels.get(cited[0], cited[0]) if cited else ""
        # An item-level record in an image catalogue: the citation is one
        # record with its own URL, so the label is a link to it. A
        # postcard is the same shape as a photograph here — a catalogued
        # item, not a document a page cites a passage of.
        photo = e.get("kind") in ("photograph", "postcard")
        if len(cited) > 1:
            # Shared label once, then one link per record — the shape a permit
            # item already uses, a span of context followed by its links.
            links = "".join(
                f'{indent}      <a href="{esca(urls[s])}">'
                f'{esc(titles.get(s) or labels.get(s, s))}</a>\n'
                for s in cited if s in urls)
            row = f'{indent}      <span>{esc(meta)}</span>\n' + links
        else:
            href = urls.get(cited[0]) if (photo and cited) else None
            row = (f'{indent}      <a href="{esca(href)}">{esc(meta)}</a>\n' if href
                   else f'{indent}      <span>{esc(meta)}</span>\n')
        desc = esc(e.get("description", ""))
        # A news entry is the article's headline, the outlet and the date, and
        # nothing else: we never restate a living outlet's reporting in our own
        # words, so it carries `headline`/`outlet`/`url` in place of a
        # `description`, and the outlet's name is the link. That leaves nothing
        # for a meta row to say — the citation is already the whole entry — so
        # the row is dropped rather than repeating the label underneath it.
        if e.get("headline"):
            desc = f'<em>{esc(e["headline"])}</em>'
            if e.get("outlet") and e.get("url"):
                desc += f' — <a href="{esca(e["url"])}">{esc(e["outlet"])}</a>'
            meta = ""
        summary = (f'{indent}    <p class="vtl-desc"><b>{esc(e["summary"])}</b></p>\n'
                   if e.get("summary") else "")
        when = e.get("date", "")
        key = date_key(when)
        if re.fullmatch(r"\d{4}-\d{2}-\d{2}", when or ""):
            when = long_date(when)
        # A source that knows the month but not the day — a directory issue, a
        # water-service record read to the month — writes `1896-10`, and until
        # this branch existed the rail printed that string raw beside a
        # "August 24, 1896" formatted from the line above it.
        elif re.fullmatch(r"\d{4}-\d{2}", when or ""):
            when = MONTHS_LONG[int(when[5:7]) - 1] + " " + when[:4]
        items.append((key,
            f'{indent}  <li class="vtl-item">\n'
            f'{indent}    <div class="vtl-date">{esc(when)}</div>\n'
            f'{summary}'
            f'{indent}    <p class="vtl-desc">{desc}</p>\n'
            + (f'{indent}    <div class="vtl-meta">\n' + row
               + f'{indent}    </div>\n' if meta else "")
            + f'{indent}  </li>'))
    return items


def survey_panel_html(rec: dict, indent: str) -> str:
    """`historic_survey` — what the historic resources surveys found here.

    One panel per survey, in the order the page lists them, because a heading
    names one survey and its rows are that survey's findings. Two surveys reach
    the same building often enough to plan for it — the Transit Center area sits
    inside Central SoMa, and the 1990 unreinforced-masonry survey crosses nearly
    all of them — and while this held a single object, the second survey to
    arrive either overwrote the first or was written into its panel under the
    first's name. Both lose the fact.

    Spec rows, not prose: a status code, a rating, the earlier surveys that
    looked at the building. Where a survey's own address or APN disagrees
    with the city's, both are shown and neither is adjudicated.
    """
    surveys = rec.get("historic_survey") or []
    if isinstance(surveys, dict):
        surveys = [surveys]
    return "".join(one_survey_panel_html(s, indent) for s in surveys if s)


def one_survey_panel_html(s: dict, indent: str) -> str:
    rows = []
    for icon, key, val in (
            # Not every survey assigns a status code. A CEQA-era evaluation
            # states an eligibility finding in words instead, and that finding
            # is the point of the page's citation — it belongs in a row, not
            # buried in the note under it.
            ("ic-permit", "Survey finding", s.get("finding")),
            ("ic-permit", "Status code", s.get("proposed_status_code")),
            ("ic-permit", "Prior status code", s.get("prior_status_code")),
            ("ic-plan", "Article 11 rating", s.get("proposed_article11_rating")),
            ("ic-plan", "Current Article 11 rating", s.get("current_article11_rating")),
            ("ic-pin", "Eligible district", s.get("eligible_district")),
            ("ic-pin", "Within district", s.get("existing_district")),
            ("ic-ruler", "Style", s.get("style")),
            # A survey that attributes the building to an architect or a builder
            # is stating a finding, not repeating `building.architect` — 32 pages
            # carried the builder key with nowhere to render it before the row
            # existed, and 15 more were written with the `_as_surveyed` spellings
            # that no row read at all.
            ("ic-ruler", "Architect as surveyed",
             s.get("architect_as_surveyed") or s.get("architect")),
            ("ic-ruler", "Builder as surveyed",
             s.get("builder") or s.get("builder_as_surveyed")),
            ("ic-plan", "Construction", s.get("frame")),
            ("ic-layers", "Integrity", s.get("physical_integrity")),
            ("ic-calendar", "Year built as surveyed", s.get("year_built_as_surveyed")),
            ("ic-home", "Address as surveyed", s.get("address_as_surveyed")),
            ("ic-pin", "Parcel as surveyed", s.get("apn_as_surveyed"))):
        if val:
            rows.append((icon, key, str(val)))
    for key, val in (("Here Today (1968)", s.get("here_today_page")),
                     ("1976 architectural survey", s.get("dcp_1976_survey")),
                     ("Unreinforced masonry survey", s.get("umb_survey")),
                     ("Heritage rating", s.get("heritage_rating")),
                     ("Earlier survey", s.get("prior_survey"))):
        if val:
            rows.append(("ic-check", key, "Listed" if val is True else str(val)))
    # A status code is opaque on its own, so the code key the survey prints
    # alongside its findings is carried under the list.
    meaning = s.get("status_code_meaning")
    if meaning and not meaning.endswith("."):
        meaning += "."
    footnote = " ".join(x for x in (meaning, s.get("note")) if x)
    # Some surveys record nothing codeable about a building and still say
    # something worth keeping — that its address was numbered differently when
    # it went up, or that the report contradicts itself about which building
    # this is. A note on its own is a finding; dropping the panel loses it.
    if not (rows or footnote):
        return ""
    body = "\n".join(
        f'{indent}    <div class="spec"><span class="ic {i}"></span>'
        f'<span class="spec-k">{esc(k)}</span>'
        f'<span class="spec-v">{esc(v)}</span></div>' for i, k, v in rows)
    specs = f'{indent}  <dl class="speclist">\n{body}\n{indent}  </dl>\n' if rows else ""
    note = (f'{indent}  <p class="prose"><small>{esc(footnote)}</small></p>\n'
            if footnote else "")
    return (f'{indent}<section class="panel">\n'
            f'{indent}  <h3>{esc(s.get("survey", "Historic resources survey"))}</h3>\n'
            f'{specs}'
            f'{note}'
            f'{indent}</section>\n')


def open_space_panel_html(rec: dict, indent: str) -> str:
    """The city's privately-owned-public-open-space record, as a sidebar panel.

    Each space is its own panel: 345 California has three, and a reader needs to
    know that the plaza is open at all times while the snippets are not.
    """
    out = []
    for s in rec.get("public_open_space") or []:
        rows = []
        for icon, key, val in (
                ("ic-home", "Type", s.get("type")),
                ("ic-clock", "Hours", s.get("hours")),
                ("ic-pin", "Where", s.get("location")),
                ("ic-home", "Seating", s.get("seating")),
                ("ic-value", "Food service", s.get("food_service")),
                ("ic-help", "Restrooms", s.get("restrooms")),
                ("ic-ruler", "Step-free access", s.get("accessibility")),
                ("ic-plan", "Landscaping", s.get("landscaping")),
                ("ic-check", "Signage", s.get("signage")),
                ("ic-link", "Amenities", s.get("amenities")),
                ("ic-ruler", "Designer", s.get("designer")),
                ("ic-calendar", "Required from", s.get("established"))):
            if val not in (None, ""):
                rows.append((icon, key, val))
        if not rows:
            continue
        body = "\n".join(
            f'{indent}    <div class="spec"><span class="ic {i}"></span>'
            f'<span class="spec-k">{esc(k)}</span>'
            f'<span class="spec-v">{esc(v)}</span></div>' for i, k, v in rows)
        heading = s.get("name") or "Public open space"
        out.append(f'{indent}<section class="panel">\n'
                   f'{indent}  <h3>{esc(heading)}</h3>\n'
                   f'{indent}  <dl class="speclist">\n{body}\n{indent}  </dl>\n'
                   f'{indent}</section>\n')
    return "".join(out)


def public_art_html(rec: dict, indent: str) -> str:
    """The works the 1% art requirement put on this parcel, one list item each."""
    works = rec.get("public_art") or []
    if not works:
        return ""
    items = []
    for w in works:
        title = w.get("title") or f"Untitled {(w.get('type') or 'work').lower()}"
        label = f"{title} — {w['artist']}" if w.get("artist") else title
        link = w.get("artist_link")
        head = (f'<a href="{esca(link)}">{esc(label)}</a>' if link else esc(label))
        # The inventory's own phrasing, joined; a trailing "p.m." already ends
        # the sentence, so don't add a second full stop after it.
        bits = [b for b in (w.get("medium"), w.get("location"), w.get("access")) if b]
        hook = "; ".join(b.rstrip() for b in bits)
        if hook:
            hook = hook[0].upper() + hook[1:] + ("" if hook.endswith(".") else ".")
        # A researched installation date and description go on their own line —
        # the inventory's spec line and the work's own story read as two things.
        second = " ".join(x for x in (
            f"Installed {w['installed']}." if w.get("installed") else "",
            w.get("detail") or "",
            # Where a source and the city's inventory disagree about a title or
            # a credit, say so — don't quietly pick one.
            w.get("title_note") or "", w.get("artist_note") or "") if x).strip()
        tail = (f'<br>\n{indent}    <span class="hook">{esc(second)}</span>'
                if second else "")
        items.append(f'{indent}  <li>{head}<br>\n'
                     f'{indent}    <span class="hook">{esc(hook)}</span>{tail}</li>')
    return (f'{indent}<div class="section-head"><span class="ic ic-plan"></span>'
            f'<h2>Public art</h2></div>\n'
            f'{indent}<ul class="place-list">\n' + "\n".join(items)
            + f'\n{indent}</ul>\n')


def glance_panel_html(rec: dict, indent: str) -> str:
    p = rec.get("parcel", {})
    a = rec.get("assessment", {})
    b = rec.get("building") or {}
    rows = []
    # Researched identity: the name the building goes by, who designed it, who
    # built it. Single facts, so spec rows — never a paragraph each.
    # A published completion year that matches the assessor's is the same fact
    # twice — the timeline's "Built" entry already carries it. Show the row only
    # when the two disagree, and `unknowns` says so alongside.
    completed = b.get("completed")
    if completed and str(completed) == str(p.get("year_built")):
        completed = None
    for icon, key, val in (("ic-home", "Known as", b.get("name")),
                           ("ic-home", "Formerly", b.get("former_name")),
                           ("ic-ruler", "Architect", b.get("architect")),
                           # A named builder with no named architect is the
                           # normal case for a 19th-century workers' cottage —
                           # the carpenter who put it up is who the record has.
                           ("ic-ruler", "Builder", b.get("builder")),
                           ("ic-plan", "Developer", b.get("developer")),
                           ("ic-calendar", "Completed", completed)):
        if val:
            rows.append((icon, key, val))
    ctype = CONSTRUCTION.get(p.get("construction_type_code"))
    if ctype:
        rows.append(("ic-plan", "Construction", ctype))
    if rec.get("block") and rec.get("lot"):
        rows.append(("ic-pin", "Parcel", f"Block {rec['block']}, Lot {rec['lot']}"))
    if rec.get("street_numbers_on_parcel"):
        # Hand-authored pages sometimes hold these as numbers rather than
        # strings, and a bare join dies on the first int.
        rows.append(("ic-home", "Street numbers",
                     ", ".join(str(n) for n in rec["street_numbers_on_parcel"])))
    if rec.get("also_addressed"):
        rows.append(("ic-pin", "Also addressed",
                     ", ".join(alias_display(x) for x in rec["also_addressed"])))
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


# The district panel is the one block whose subject is the district and not the
# building. Its most interesting fact is the plainest — this address stands
# inside a named historic district — and the old layout set that fact in label
# type above four undifferentiated rows. These helpers put the name in the
# headline and reduce the rows to standing: what the district is on, and what
# it is not.

DISTRICT_KIND = re.compile(
    r"\s+(Historic|Conservation|Early Residential|Neighborhood Commercial|"
    r"Industrial|Cultural Landscape)\s+District"
    r"(\s+Extension|\s+Addition|\s+\(Discontiguous\))?$")


def split_district_name(name: str) -> tuple:
    """("Panhandle Historic District") -> ("Panhandle", "Historic district").

    The type moves to the panel's eyebrow so the headline can be the district
    itself. 110 of the 113 district names in the data end in a type phrase;
    the three that don't — "Auxiliary Water Supply System (Discontiguous)" and
    its like — keep their whole name and take the generic eyebrow, which is
    what the fallback is for. Trailing qualifiers ("Extension",
    "(Discontiguous)") ride up with the type rather than dangling off a
    headline that no longer says what they qualify.
    """
    m = DISTRICT_KIND.search(name)
    if not m:
        return name, "Historic district"
    kind = f"{m.group(1)} district{m.group(2) or ''}".strip()
    return name[:m.start()].strip(), kind.capitalize()


def district_eyebrow(d: dict, kind: str) -> str:
    """The panel's eyebrow label.

    A designation outranks the name's own type, because being a city landmark
    district is the strongest thing the panel has to say and it is identity,
    not consequence — so it belongs beside the name rather than in the list
    below. The article number rides in line with the label: it is a citation,
    and it means nothing to a reader on its own.
    """
    a = (d.get("article_10_11_status") or "")
    if a.startswith("Article 10"):
        return "Article 10 city landmark district"
    if a.startswith("Article 11"):
        return "Article 11 conservation district"
    return kind


# listed > eligible > neither. The icon carries the step, never the subject:
# the label already says which register it is, so a glyph per register would
# distinguish rows their own words distinguish.
STANDING_ICON = {"listed": "ic-check", "eligible": "ic-eligible", "none": "ic-none"}
STANDING_RANK = {"listed": 0, "eligible": 1, "none": 2}
STANDING_PHRASE = {"listed": "Listed on the {}",
                   "eligible": "Eligible for the {}",
                   "none": "Not on the {}"}


def standing_tier(status: str) -> str:
    s = (status or "").strip().lower()
    if s == "listed":
        return "listed"
    if s.startswith("eligible"):
        return "eligible"
    return "none"


def standing_rows(d: dict) -> list:
    """(tier, sentence) per line, affirmative first."""
    rows = []
    ca, nr = d.get("california_register_status"), d.get("national_register_status")
    ca_t = standing_tier(ca) if ca else None
    nr_t = standing_tier(nr) if nr else None
    # Two registers at the same standing are one fact, not two rows.
    if ca_t and ca_t == nr_t:
        rows.append((ca_t, STANDING_PHRASE[ca_t].format(
            "California and National Registers")))
    else:
        if ca_t:
            rows.append((ca_t, STANDING_PHRASE[ca_t].format("California Register")))
        if nr_t:
            rows.append((nr_t, STANDING_PHRASE[nr_t].format("National Register")))
    # Local designation appears here only in the negative: when the district
    # carries it, the eyebrow has already said so. "Not a city landmark
    # district" and not "no local landmark protection" — the row is about the
    # district, and a building can be an Article 10 landmark in its own right
    # inside a district that holds nothing (573 Castro Street is exactly that),
    # so an unqualified line would contradict the tag beside it.
    a = d.get("article_10_11_status") or ""
    if a and not a.startswith(("Article 10", "Article 11")):
        rows.append(("none", "Not a city landmark district"))
    rows.sort(key=lambda r: STANDING_RANK[r[0]])
    return rows


LEGACY_REGISTER = {"listed": "Listed", "eligible": "Eligible (not listed)",
                   "no": "Not listed", "not listed": "Not listed"}


def district_record(rec: dict) -> dict:
    """The district in the shape the panel renders, whichever shape it is stored in.

    Pages seeded from DataSF carry `california_register_status` and
    `article_10_11_status`. Sixteen pages written by hand before the seeder
    existed carry `california_register: "Eligible"` and `article_10: "Listed"`
    instead. Normalising here keeps one renderer for both rather than two
    renderers that will drift.

    Returns {} when the record names no district: eight parcels carry a
    `historic_district` block whose only job is to record that a spatial query
    found nothing, and those pages must render no panel at all.
    """
    d = district_of(rec)
    if not d or not d.get("name"):
        return {}
    if d.get("california_register_status") or d.get("national_register_status"):
        return d
    out = dict(d)
    for legacy, key in (("california_register", "california_register_status"),
                        ("national_register", "national_register_status")):
        raw = str(d.get(legacy) or "").strip()
        if raw:
            out[key] = LEGACY_REGISTER.get(raw.lower(), raw)
    if str(d.get("article_10") or "").strip().lower() == "listed":
        out["article_10_11_status"] = "Article 10 historic district"
    elif str(d.get("article_11") or "").strip().lower() == "listed":
        out["article_10_11_status"] = "Article 11 conservation district"
    elif ("article_10" in d or "article_11" in d
          or "article_10_local_landmark_district" in d):
        # Only claim the absence where the record actually speaks to it.
        out["article_10_11_status"] = "No local landmark protection"
    return out


@functools.lru_cache(maxsize=None)
def _district_hubs(city_slug: str) -> frozenset:
    """The district slugs that have a hub page in this city, read off the tree.

    Which districts earned a hub is a fact about the whole city — the
    threshold is `DISTRICT_MIN_PAGES` documented buildings — so it cannot be
    computed from one page's `data.json`. Reading the built directory back is
    how the renderer stays incapable of emitting a link to a district hub that
    was held back, which `validate.check_internal_links` would fail on anyway.
    `seed_pages.py districts` writes these; this only ever reads them.
    """
    d = ROOT / city_slug / DISTRICTS_DIR
    if not d.is_dir():
        return frozenset()
    return frozenset(x.name for x in d.iterdir() if (x / "index.html").is_file())


def district_hub_href(city_slug: str, name: str) -> str | None:
    """The hub for this district, or None where the district has no hub.

    A district under the threshold keeps its panel and simply has nowhere to
    link — the panel states the standing either way, and only the name stops
    being a link.

    Takes the city slug rather than a record so hub pages, which have no
    `data.json` of their own, can resolve the same link an address page does.
    """
    slug = district_slug(name)
    return (f"/{city_slug}/{DISTRICTS_DIR}/{slug}/"
            if slug in _district_hubs(city_slug) else None)


def district_href(rec: dict, name: str) -> str | None:
    """`district_hub_href` for the city this page sits in."""
    return district_hub_href(rec["path"].strip("/").split("/")[0], name)


def district_hub_link(city_slug: str, name: str, text: str) -> str:
    """`text` as a link to the district's hub, or as plain text without one."""
    href = district_hub_href(city_slug, name)
    return f'<a href="{esca(href)}">{esc(text)}</a>' if href else esc(text)


def district_link(rec: dict, name: str, text: str) -> str:
    """`district_hub_link` for the city this page sits in."""
    return district_hub_link(rec["path"].strip("/").split("/")[0], name, text)


def district_panel_html(rec: dict, indent: str) -> str:
    d = district_record(rec)
    if not d:
        return ""
    name, kind = split_district_name(d["name"])
    out = [f'{indent}<section class="panel panel-district">',
           f'{indent}  <p class="district-kind">'
           f'{esc(district_eyebrow(d, kind))}</p>',
           f'{indent}  <h3>{district_link(rec, d["name"], name)}</h3>']
    # The survey records a literal "N/A" for districts it never dated. A
    # dateline reading "Significant N/A" is worse than no dateline.
    pos = (d.get("period_of_significance") or "").strip()
    if pos and pos.upper() != "N/A":
        out.append(f'{indent}  <p class="district-dateline">'
                   f'Significant {esc(pos)}</p>')
    rows = standing_rows(d)
    if rows:
        out.append(f'{indent}  <ul class="standing">')
        for tier, sentence in rows:
            cls = ' class="is-none"' if tier == "none" else ""
            out.append(f'{indent}    <li{cls}><span class="ic '
                       f'{STANDING_ICON[tier]}"></span>{esc(sentence)}</li>')
        out.append(f'{indent}  </ul>')
    # Overlapping districts have no home in the headline — a second district
    # would want a second name at the same size. They trail the panel as a
    # note until the layout has an answer for them.
    for other in rec.get("also_in_districts", []):
        out.append(f'{indent}  <p class="district-also">Also within '
                   f'{district_link(rec, other["name"], other["name"])}</p>')
    out.append(f'{indent}</section>')
    return "\n".join(out) + "\n"


# --------------------------------------------------------------------------
# Nearby
# --------------------------------------------------------------------------
# `render_html` is a pure function of one page's `data.json`, so it cannot know
# what stands next door. `scripts/build_link_index.py` works that out for the
# whole city ahead of time and this reads it back — the same arrangement the
# homepage map has with `shared/addresses.geojson`.
#
# The index carries paths and titles and deliberately no hooks, so a page's
# HTML changes when a page is added or removed nearby and not every time a
# neighbor's prose is edited. See that script's docstring for the rest.
NEARBY_INDEX = ROOT / "shared" / "nearby.json"

# The relationship in the reader's terms. This is the context a hook would have
# supplied, and the reason the index doesn't have to carry one.
NEARBY_LABEL = {"street": "Same street",
                "block": "Same block",
                "corner": "Around the corner"}


@functools.lru_cache(maxsize=1)
def _nearby_index() -> dict:
    """page path -> ((href, title, relationship), ...), read once per process.

    A missing or unreadable index is not an error: the page renders without a
    Nearby block rather than failing. That is what lets a page seeded before
    `build_link_index.py` next runs still render — it simply has no neighbors
    to show until the index catches up with it.
    """
    try:
        raw = json.loads(NEARBY_INDEX.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    paths, titles = raw["paths"], raw["titles"]
    return {path: tuple((paths[j], titles[j], cls) for j, cls in near)
            for path, near in zip(paths, raw["near"]) if near}


def nearby_html(rec: dict, indent: str) -> str:
    """The lateral links: the places a reader standing here could walk to.

    Ordered as the index stores them — up and down the street first, then the
    rest of the block, then around the corner — which is widening circles from
    the doorstep rather than a ranking.

    Note what this markup is not: an `<a>` followed by `<br>` and a
    `span.hook`. That pairing is what `validate.hub_html_items` reads a hub's
    generated list back out of, and `check_hub_sync` then requires the same
    item in the hub's `index.md`. The check skips address directories, so this
    block would be safe either way; staying off the pattern means it cannot
    break that check even if the markup is later reused on a hub.
    """
    entries = _nearby_index().get(rec["path"])
    if not entries:
        return ""
    out = [f'{indent}<section class="nearby">',
           f'{indent}  <div class="section-head"><span class="ic ic-pin"></span>'
           f'<h2>Nearby</h2></div>',
           f'{indent}  <ul class="place-list">']
    for href, title, cls in entries:
        out.append(f'{indent}    <li><a href="{esca(href)}">{esc(title)}</a>\n'
                   f'{indent}      <span class="pill pill-muted">'
                   f'{esc(NEARBY_LABEL.get(cls, cls))}</span></li>')
    out += [f'{indent}  </ul>', f'{indent}</section>']
    return "\n".join(out) + "\n"


def unknowns_html(rec: dict) -> str:
    p = rec.get("parcel", {})
    a = rec.get("assessment", {})
    # "The early residents" is only a gap on a building that has residents, and
    # the architect is only a gap while the page doesn't name one.
    residential = (p.get("use") or "") in (
        "Single Family Residential", "Multi-Family Residential")
    b = rec.get("building") or {}
    missing = []
    if not b.get("architect"):
        # "and builder" only while the builder is genuinely undocumented — a
        # page that names the carpenter who built the house must not go on
        # listing the builder as a gap.
        missing.append("the architect" if b.get("builder")
                       else "the architect and builder")
    elif not b.get("developer"):
        missing.append("the developer")
    missing.append("the early residents" if residential else "the early tenants")
    if any(not w.get("installed") for w in rec.get("public_art") or []):
        missing.append("when each artwork was installed")
    if any(not s.get("designer") for s in rec.get("public_open_space") or []):
        missing.append("who designed the open space")
    if not a.get("last_sale_date"):
        missing.append("the date of the last recorded sale")
    # The roll leaves `year_built` empty on city-owned and exempt parcels. That
    # is a gap only while nothing else on the page dates the building — once a
    # source gives a completion year, listing it as undocumented contradicts the
    # "Completed" row two blocks up.
    if not p.get("year_built") and not b.get("completed"):
        missing.insert(0, "the year the building went up")
    # One gap left is the normal case on a well-documented page, and the
    # join above turns it into a dangling "Not yet documented: and the early
    # tenants." It stayed hidden while every page had at least two gaps —
    # "the architect and builder" was always one of them — and surfaced the
    # first time a run filled in both.
    listing = (missing[0] if len(missing) == 1
               else ", ".join(missing[:-1]) + f" and {missing[-1]}")
    note = ""
    hs = rec.get("historic_status") or {}
    hy, ry = hs.get("yearbuilt"), p.get("year_built")
    if hy and ry and str(hy) != str(ry):
        note = (f" The assessor dates the building to {ry}; Planning's historic "
                f"resource survey records {hy}.")
    if "vacant lot" in (p.get("property_class") or "").lower() and ry:
        note += (f" The roll classes this parcel as a vacant lot and also gives "
                 f"it a build year of {ry}.")
    conflict = (rec.get("building") or {}).get("completed_conflict")
    if conflict:
        note += f" {conflict}"
    # `unknowns` is where a run records a disagreement it must not adjudicate —
    # a source against the assessor, or a source against itself. It is written
    # into data.json, so it has to render from there; a note that lives only in
    # the JSON is a fact the page does not state. Both shapes in the repo are
    # read: a list of sentences, and a dict keyed by a slug.
    stated = rec.get("unknowns") or []
    if isinstance(stated, dict):
        stated = list(stated.values())
    said = " ".join(str(s).strip() for s in stated if str(s).strip())
    url = feedback_url(page_title(rec), rec["path"])
    return ('  <div class="unknowns">\n'
            '    <span class="ic ic-help"></span>\n'
            f'    <p>{said + " " if said else ""}Not yet documented: {listing}.{note}\n'
            f'    <a href="{url}">Submit an update</a></p>\n'
            '  </div>\n')


SOURCE_FOOTER_NAME = {
    "sf-assessor-roll": lambda n: n.replace(" (", ", ").replace(")", ""),
}


def sources_html(rec: dict) -> str:
    """The footer's source list.

    A source need not have a URL. Two pages cite a printed journal article read
    off paper, and a citation with nowhere to link is still a citation — it just
    prints without the link rather than crashing the render.
    """
    items = []
    for s in rec.get("sources", []):
        name = SOURCE_FOOTER_NAME.get(s["id"], lambda n: n)(s["name"]).replace(" — ", ", ")
        retrieved = s.get("retrieved")
        if s.get("query") and retrieved:
            tail = (f'\n        <a href="{esca(s["query"])}">'
                    f'retrieved {retrieved}</a>')
        elif retrieved:
            tail = f'\n        <span>read {retrieved}</span>'
        else:
            tail = ""
        items.append(f'      <li>{esc(name)}{" —" if tail else ""}{tail}</li>')
    return "\n".join(items)


# --------------------------------------------------------------------------
# Structured data
# --------------------------------------------------------------------------
# The site's whole shape is a containment hierarchy — city, neighborhood,
# street, building — and until these blocks landed none of it was declared. A
# `BreadcrumbList` is what puts the trail, rather than a bare URL, under a
# result for a page four levels deep, and it states the same values the
# breadcrumb `<nav>` already renders, in the form a crawler reads.
#
# `validate.check_html` permits any number of `application/ld+json` tags and
# rejects only other scripts, so a page may carry several of these.
def ld_block(obj, indent: str = "  ") -> str:
    """One `<script type="application/ld+json">`, indented into the page."""
    return (f'{indent}<script type="application/ld+json">\n'
            + indent_block(json.dumps(obj, indent=2, ensure_ascii=False), indent)
            + f'\n{indent}</script>')


def breadcrumb_ld(crumbs: list) -> dict:
    """`[(name, href or None), ...]` from the top down, current page last.

    The current page carries no `item`: it is where the reader already is, and
    schema.org treats the final crumb's URL as optional for exactly that
    reason. Every crumb above it is absolute, because the consumer is a
    crawler that may have the page out of its directory context.
    """
    items = []
    for i, (name, href) in enumerate(crumbs):
        item = {"@type": "ListItem", "position": i + 1, "name": name}
        if href:
            item["item"] = f"{SITE}{href}"
        items.append(item)
    return {"@context": "https://schema.org", "@type": "BreadcrumbList",
            "itemListElement": items}


def collection_ld(path: str, name: str, desc: str, items: list) -> dict:
    """A hub, as the collection it is: `CollectionPage` wrapping an `ItemList`.

    `items` is `[(name, href), ...]` in the order the page lists them, and the
    positions are that order — a hub's list is sorted (by number up a street,
    by street across a neighborhood), so the sequence is information rather
    than an accident of the walk. Only URLs go in the list: the hook beside
    each entry is this page's own summary of another page, and repeating it
    here would be the same sentence in a second place.
    """
    return {
        "@context": "https://schema.org",
        "@type": "CollectionPage",
        "url": f"{SITE}{path}",
        "name": name,
        "description": desc,
        "mainEntity": {
            "@type": "ItemList",
            "numberOfItems": len(items),
            "itemListOrder": "https://schema.org/ItemListOrderAscending",
            "itemListElement": [
                {"@type": "ListItem", "position": i + 1, "name": label,
                 "url": f"{SITE}{href}"}
                for i, (label, href) in enumerate(items)],
        },
    }


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
    street_addr_plain = title.replace("–", "-")

    # Panels belong beside the main column whenever there is a main column for
    # them to sit beside — the empty column a split risks is the left one, and a
    # page with any timeline entry, art or prose at all has something to put
    # there. Only a page that is nothing but panels stacks them full width.
    has_panels = bool(value_panel_html(rec, "") or glance_panel_html(rec, "")
                      or district_panel_html(rec, "") or open_space_panel_html(rec, "")
                      or survey_panel_html(rec, ""))
    # A rail holding nothing but the building's own year is not a column: it
    # would put one dot beside a full stack of panels. Those pages keep
    # stacking full width, as they did when the year was a tag in the hero.
    has_main = bool(public_art_html(rec, "") or narrative_html(rec, "")[1]
                    or timeline_html(rec, "").count('<li class="vtl-item"') > 1)
    use_cols = has_panels and has_main
    ind = "      " if use_cols else "  "
    panels = (open_space_panel_html(rec, ind) + value_panel_html(rec, ind)
              + glance_panel_html(rec, ind) + survey_panel_html(rec, ind)
              + district_panel_html(rec, ind))
    art = public_art_html(rec, ind)
    timeline = timeline_html(rec, ind)
    lead_html, sections = narrative_html(rec, ind)
    main_col = "\n".join(x for x in (art, timeline, sections) if x)

    if use_cols:
        body = ('  <div class="cols">\n    <div class="main">\n'
                + main_col
                + '    </div>\n\n    <aside class="aside">\n'
                + panels
                + '    </aside>\n  </div>\n')
    else:
        body = main_col + ("\n" if main_col and panels else "") + panels

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
    crumbs_ld = breadcrumb_ld([
        (city_name, f"/{city_slug}/"),
        (area_name, f"/{city_slug}/{area_slug}/"),
        (street_name, f"/{city_slug}/{area_slug}/{street_slug_}/"),
        (crumb_number, None),
    ])

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{esc(title)} — Know This Place</title>
  <meta name="description" content="{esca(desc)}">
  <link rel="canonical" href="{SITE}{rec['path']}">
{ICON_LINKS}
  <link rel="stylesheet" href="/shared/site.css">
  <script type="module" src="/shared/site.js"></script>
{ld_block(ld)}
{ld_block(crumbs_ld)}
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
  <ktp-map location="{lat},{lng}" label="{esca(title)}">
    <figure class="media media-map">
      <div class="media-empty">
        <span class="ic ic-pin"></span>
        <span>{lat:.4f}, {'−' if lng < 0 else ''}{abs(lng):.4f}</span>
        <small>A locator map appears here once a Mapbox token is configured.</small>
      </div>
    </figure>
  </ktp-map>

  <section class="hero">
    <div>
      <h1>{esc(title)}</h1>
      <p class="sub">{esc(sub_line)} · {esc(city_name)}, CA {zip_code}</p>
      <ul class="tags">
{tags_html(rec)}
      </ul>
    </div>
    <ktp-streetview location="{lat},{lng}" label="{esca(title)}">
      <figure class="media media-lift">
        <div class="media-empty">
          <span class="ic ic-pin"></span>
          <span>{lat:.4f}, {'−' if lng < 0 else ''}{abs(lng):.4f}</span>
          <small>Street View appears here once a Google Maps embed key is configured.</small>
        </div>
      </figure>
    </ktp-streetview>
  </section>

{lead_html}{stats_html(rec)}
{body}
{nearby_html(rec, "  ")}{unknowns_html(rec)}</main>

<footer class="site-footer">
  <section class="sources">
    <h2>Sources</h2>
    <ul>
{sources_html(rec)}
    </ul>
  </section>
  <p class="feedback-cta">
    <a href="{feedback_url(title, rec['path'])}">Request an edit</a>
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
        # A few streets have no type at all in EAS — Broadway, The Embarcadero,
        # Via Bufano — so the key has to tolerate a missing one.
        by_street: dict = collections.defaultdict(list)
        for a in addrs:
            by_street[(a["street_name"], a.get("street_type", ""))].append(a)
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
            "other_street_addresses": [
                " ".join(x for x in (a["address_number"], a["street_name"],
                                     a.get("street_type", "")) if x)
                for a in addrs
                if (a["street_name"], a.get("street_type", "")) != (sname, stype)],
            "lat": float(lead["latitude"]),
            "lng": float(lead["longitude"]),
            # Every address point on the parcel, not just the lead one, so
            # `attach_permits` can measure a permit against the parcel's real
            # extent. Most parcels are one building and these points sit on top
            # of each other; APN 1300001 is the whole Presidio and has 741 of
            # them spread over two kilometres.
            "points": [(float(a["latitude"]), float(a["longitude"])) for a in addrs],
            "zip": lead.get("zip_code"),
            "eas_baseid": lead.get("eas_baseid"),
            "supervisor": lead.get("supervisor"),
            "roll": roll_by_parcel.get(pn),
            "permits": [],
        }
        row["status"] = classify(row)
        rows.append(row)
    return rows


# How far a permit's own geocode may sit from the parcel's address points
# before it is treated as belonging to some other building. Generous on
# purpose: DBI's point and EAS's point for the same address routinely differ by
# a hundred metres or so, and the failure this guards against — a permit filed
# on a *different street of the same name* — misses by kilometres, not by
# blocks. Measured against block 1300 (the Presidio) the legitimate permits sit
# at most 107m out while the foreign ones land at 3.3km and 4.0km.
PERMIT_MAX_DRIFT_M = 250.0


def _metres(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """Flat-earth distance. Fine over the few kilometres that separate two SF parcels."""
    return math.hypot((lat1 - lat2) * 111320.0,
                      (lng1 - lng2) * 111320.0 * math.cos(math.radians(lat1)))


def permit_near(p: dict, points: list) -> bool:
    """Is this permit's own geocode consistent with the parcel's address points?

    DBI's block and lot are not trustworthy on their own. San Francisco has
    several streets of the same name — the Presidio keeps its own Montgomery
    Street, Lincoln Boulevard and Mason Street alongside the downtown ones, and
    Treasure Island repeats names too — and DBI resolves an address to a parcel
    with the same ambiguity this seeder has to avoid. Thirteen permits for 101
    Montgomery Street in the Financial District are stamped block 1300 lot 001,
    which is the Presidio; four for 640 Mason Street on Nob Hill are stamped the
    same way. Nothing in the permit row's block, lot, street name or number
    separates those from the real thing. Its coordinates do.

    A permit with no point cannot be judged and is kept: 3,286 of DBI's 1.29m
    rows have no `location`, and dropping an old permit for being old is a worse
    error than the one this is preventing.
    """
    loc = (p.get("location") or {}).get("coordinates")
    if not loc or not points:
        return True
    lng, lat = loc[0], loc[1]
    return any(_metres(lat, lng, a, b) <= PERMIT_MAX_DRIFT_M for a, b in points)


def attach_permits(inv: list, permits: list) -> None:
    """Join permits onto parcels by block+lot, and by street address as a fallback.

    The fallback is not, as it once claimed, for records that carry an address
    but no block/lot: every one of DBI's 1.29m permit rows has both, and the
    corpus is fetched with `block in (...)` anyway, so a block-less row could
    never reach here. What it actually recovers is a permit filed against a
    *different* lot for the same street address — a retired lot number from
    before a block was re-parcelized, or a neighbouring lot in the same
    development. That is worth keeping, but it has to be matched on the whole
    street identity: keyed on name and number alone, "101 MONTGOMERY" matches
    two streets on opposite sides of the city, and Kirkwood Avenue's numbers
    recur across twenty lots.

    Both joins are then filtered through `permit_near`, because the block+lot
    join is no safer than the fallback — DBI mis-resolves duplicated street
    names into the block field itself.
    """
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
        points = row.get("points") or [(row["lat"], row["lng"])]
        want_type = type_key(row.get("street_type"))
        cands = list(by_bl.get((roll.get("block"), (roll.get("lot") or "").lstrip("0")), []))
        for n in row["numbers"]:
            for p in by_addr.get((row["street_name"].upper(), n.lstrip("0")), []):
                got = type_key(p.get("street_suffix"), permit=True)
                # "" is DBI declining to record a suffix, not a claim that the
                # street has none, so it matches whatever the parcel is on.
                if got and got != want_type:
                    continue
                cands.append(p)
        seen, plist = set(), []
        for p in cands:
            pn = p.get("permit_number")
            if not pn or pn in seen or not permit_near(p, points):
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
    #
    # The class code alone does not prove a unit stack: it also sits on old
    # single-address parcels that were condominium-mapped and never split, and
    # those are buildings. A research manifest may therefore carry
    # `sole_parcel_for_address`, set only where the resolver checked the
    # stronger thing — that EAS puts the recorded numbers on this parcel and no
    # other, so there is no stack of units to defer. Nothing else may set it.
    if roll.get("property_class_code_definition") == "Condominium":
        if not row.get("sole_parcel_for_address"):
            return "condo-unit"
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


def range_label(address_range) -> str:
    """Render an `address_range` value as hub link text, whatever shape it's in.

    `build_record` always writes a ready-to-use string ("100–102"), but a
    hand-edited page's data.json may instead carry a {low, high, ...} object
    (AGENTS.md only says to "record the range... under address_range", not
    which shape). Without this, a dict's Python repr leaks straight into the
    rendered Markdown link text.
    """
    if isinstance(address_range, dict):
        low, high = address_range.get("low"), address_range.get("high")
        if low is not None and high is not None and low != high:
            return f"{low}–{high}"
        return str(low if low is not None else address_range)
    return address_range


# Matched case-insensitively against each H2 heading. "documented so far" is
# a suffix match rather than an exact string because plenty of street hubs
# predate a wording change in `write_street_hub` and still read "Buildings
# documented so far" — that's a stale label on an otherwise plain generated
# list, not hand-written content, and must not block a routine rebuild.
KNOWN_STREET_HUB_SECTIONS = (re.compile(r"documented so far$", re.I),
                             re.compile(r"^not yet covered$", re.I))


def hub_extra_sections(hub_dir: Path, known) -> list:
    """H2 section headings in an existing hub that its generator didn't write.

    A hand-edited hub can grow sections a plain lead+list template has no room
    for — "The street itself", "Sources" — see `AGENTS.md`'s note that an
    existing page "is only ever edited by hand." A hub writer has no way to
    merge those back in, so it must detect them and refuse to overwrite rather
    than silently deleting them.
    """
    md = hub_dir / "index.md"
    if not md.exists():
        return []
    headings = re.findall(r"^## (.+)$", md.read_text(encoding="utf-8"), re.M)
    return [h for h in headings if not any(pat.search(h) for pat in known)]


def street_hub_extra_sections(street_dir: Path) -> list:
    return hub_extra_sections(street_dir, KNOWN_STREET_HUB_SECTIONS)


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
        # A hub written in an older format opens with its list and no lead
        # paragraph. Reading the first list item as the lead splices the whole
        # list into one line and leaves a duplicate list below it.
        if stripped.startswith(("- ", "* ", "1. ")):
            break
        if not stripped:
            if para:
                break
            continue
        para.append(stripped)
    return " ".join(para) if para else fallback


def hook_for(rec: dict, with_district: bool = True) -> str:
    """The page's one-line description for a hub's list.

    `with_district` is off on a historic-district hub, where naming the
    district on every line would repeat the page's own headline — and would
    name the *wrong* district for a building that stands in two.
    """
    # A hand-written hook in data.json always wins over a generated one.
    if rec.get("hook"):
        return rec["hook"]
    p = rec.get("parcel", {})
    year = p.get("year_built")
    btype = building_type(p.get("property_class"), p.get("units")).lower()
    article = article_for(year, btype).capitalize()
    head = f"{article} {year} {btype}" if year else f"{article} {btype}"
    dist = district_of(rec).get("name") if with_district else None
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


# --------------------------------------------------------------------------
# Nearby streets
# --------------------------------------------------------------------------
# The street-hub counterpart to `nearby_html`. Address pages get their lateral
# links from `shared/nearby.json` because `render_html` sees one `data.json`
# and nothing else; a street hub is already built from the whole directory
# beneath it, and its neighbors are one level up, so this reads the
# neighborhood off the tree instead of needing a committed index.
NEARBY_STREET_MAX = 6


@functools.lru_cache(maxsize=8)
def _street_geometry(area_dir: str) -> dict:
    """slug -> (display, count, (lat, lng) centroid, ((lat, lng), ...)).

    One pass over a neighborhood, cached, because `write_street_hub` is called
    once per street and every call wants the same answer. Streets with no
    documented building, and buildings with no coordinates, are left out —
    a street that contributes nothing to the geometry can't be ranked against
    and can't be ranked.
    """
    out = {}
    for street_dir in sorted(Path(area_dir).iterdir()):
        if not street_dir.is_dir():
            continue
        recs = []
        for d in sorted(street_dir.iterdir(), key=lambda x: num_key(x.name)):
            f = d / "data.json"
            if d.is_dir() and f.exists():
                recs.append(json.loads(f.read_text(encoding="utf-8")))
        if not recs:
            continue
        pts = tuple((c["lat"], c["lng"]) for c in
                    (r.get("coordinates") or {} for r in recs)
                    if c.get("lat") is not None and c.get("lng") is not None)
        if not pts:
            continue
        # The display name comes off an address on the street, not off the
        # slug — the same choice `write_street_hub` makes for its own <h1>, so
        # a link's text matches the page it lands on.
        disp = page_title(recs[0]).split(" ", 1)[1]
        centroid = (sum(p[0] for p in pts) / len(pts),
                    sum(p[1] for p in pts) / len(pts))
        out[street_dir.name] = (disp, len(recs), centroid, pts)
    return out


@functools.lru_cache(maxsize=8)
def _nearby_streets(area_dir: str) -> dict:
    """slug -> ((slug, display, count), ...), nearest first, capped.

    Distance between two streets is the shorter of "how far is A's centre from
    the nearest building on B" and the same measured the other way. Centre to
    centre would be cheaper but reads badly on a long street: Mission Street's
    centroid sits in the middle of the neighborhood, so a centre-to-centre
    ranking would hide it from every street near the edges that it in fact
    runs straight past. Taking the nearer of the two measurements keeps the
    *distance* symmetric while letting a long street be near everything it
    actually passes; the cap is still one-sided, so a street on a crowded
    corner can appear on a quiet street's list without returning the favour.

    Cost is streets x buildings per neighborhood, about 1.2M distance
    calculations for the whole city, all of it inside one cached pass.
    """
    geom = _street_geometry(area_dir)
    slugs = sorted(geom)
    reach = {}  # (a, b) -> distance from a's centroid to b's nearest building
    for a in slugs:
        lat, lng = geom[a][2]
        for b in slugs:
            if b != a:
                reach[(a, b)] = min(_metres(lat, lng, y, x) for y, x in geom[b][3])
    out = {}
    for a in slugs:
        ranked = sorted(((min(reach[(a, b)], reach[(b, a)]), b) for b in slugs
                         if b != a))[:NEARBY_STREET_MAX]
        if ranked:
            out[a] = tuple((b, geom[b][0], geom[b][1]) for _d, b in ranked)
    return out


def nearby_streets_html(street_dir: Path, ctx: dict, indent: str) -> str:
    """The streets a reader standing on this one could walk to.

    Deliberately not the `<a>…</a><br><span class="hook">` pairing:
    `validate.hub_html_items` reads a hub's generated list back out of exactly
    that markup and `check_hub_sync` then demands the same item in the hub's
    `index.md`. Street hubs *are* hub-synced, so a nearby list written that way
    would either fail the check or force generated content into the file that
    exists to hold a person's prose. Staying off the pattern keeps `index.md`
    for prose — the same choice `nearby_html` makes on address pages.
    """
    entries = _nearby_streets(str(street_dir.parent)).get(street_dir.name)
    if not entries:
        return ""
    out = [f'{indent}<section class="nearby">',
           f'{indent}  <div class="section-head"><span class="ic ic-pin"></span>'
           f'<h2>Nearby streets</h2></div>',
           f'{indent}  <ul class="place-list">']
    for slug, disp, count in entries:
        out.append(
            f'{indent}    <li><a href="/{ctx["city"]}/{ctx["area"]}/{slug}/">'
            f'{esc(disp)}</a>\n{indent}      <span class="pill pill-muted">'
            f'{count:,} {"building" if count == 1 else "buildings"}'
            f'</span></li>')
    out += [f'{indent}  </ul>', f'{indent}</section>']
    return "\n".join(out) + "\n"


def write_street_hub(street_dir: Path, ctx: dict, skipped: dict = None) -> bool:
    """Rebuild a street's index.md + index.html from the pages beneath it.

    Returns False (and leaves both files untouched) if the existing index.md
    has hand-written sections the generator doesn't know how to preserve —
    see `street_hub_extra_sections`.

    The "Nearby streets" list is a fact about the whole neighborhood, so
    rebuilding one street hub after seeding leaves its neighbors' lists a page
    behind — `hubs` over the neighborhood is what brings them level, the same
    way `build_link_index.py` catches `shared/nearby.json` up to new pages.
    """
    extra = street_hub_extra_sections(street_dir)
    if extra:
        print(f"  {street_dir}: skipping — hand-written section(s) "
              f"{', '.join(extra)} beyond the generated template; "
              f"update the list by hand instead", file=sys.stderr)
        return False
    recs = []
    for d in sorted(street_dir.iterdir(), key=lambda x: num_key(x.name)):
        f = d / "data.json"
        if d.is_dir() and f.exists():
            recs.append(json.loads(f.read_text()))
    if not recs:
        return True
    slug = street_dir.name
    disp = page_title(recs[0]).split(" ", 1)[1]  # off the address, not the slug
    path = f"/{ctx['city']}/{ctx['area']}/{slug}/"
    area_name = " ".join(w.capitalize() for w in ctx["area"].split("-"))
    city_name = " ".join(w.capitalize() for w in ctx["city"].split("-"))

    years = sorted(r["parcel"]["year_built"] for r in recs if r.get("parcel", {}).get("year_built"))
    in_district = sum(1 for r in recs if district_of(r).get("name"))
    districts = collections.Counter(district_of(r)["name"]
                                    for r in recs if district_of(r).get("name"))
    # What DBI holds, not what each page shows — a tower's page carries the
    # largest filings and states the full count in its `permit_summary`.
    n_permits = sum((r.get("permit_summary") or {}).get("count_on_file")
                    or len(r.get("permits", [])) for r in recs)

    entries = []
    for r in recs:
        addr_range = r.get("address_range")
        number = range_label(addr_range) if addr_range else r["path"].strip("/").split("/")[-1]
        entries.append((number, r["path"].strip("/").split("/")[-1], page_title(r), hook_for(r)))

    tiles = [("ic-home", f"{len(recs):,}", "Buildings documented")]
    if years:
        span = (f"{years[0]}<small>–{years[-1]}</small>" if years[0] != years[-1]
                else f"{years[0]}")
        tiles.append(("ic-calendar", span, "Construction dates"))
    tiles.append(("ic-permit", f"{n_permits:,}", "Permit records"))
    if in_district:
        tiles.append(("ic-plan", f"{in_district:,}", "In a historic district"))

    # The fallback never claims completeness: a street seeded from a *thematic*
    # list — the buildings named in a city inventory, say — holds a handful of
    # its parcels, not all of them, and "every parcel on Howard Street" is then
    # false. Say what is here instead.
    lead = hub_lead(street_dir, f"The parcels on {disp} documented here so far, "
                                f"from the city's address, assessor and permit "
                                f"records.")

    # What this street has that isn't a page, and why — replaces the hand-kept
    # "not yet covered" note with counts straight from the classifier.
    SKIP_WORDS = {
        "condo-unit": "condominium parcels, which are individual units rather than "
                      "buildings and are held back until the building each belongs to "
                      "can be established",
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
            f'<span class="spec-k">'
            f'{district_hub_link(ctx["city"], name, name)}</span>'
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
            f"{'parcel' if len(recs) == 1 else 'parcels'} with permits, "
            f"assessments and historic status, fully cited.")
    cols_open, cols_close = "", ""
    if aside:
        cols_open = '  <div class="cols">\n    <div class="main">\n'
        cols_close = f'    </div>\n\n    <aside class="aside">\n{aside}    </aside>\n  </div>\n'
    nearby = nearby_streets_html(street_dir, ctx, "  ")

    html_out = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{esc(disp)}, {esc(city_name)} — Know This Place</title>
  <meta name="description" content="{esca(desc)}">
  <link rel="canonical" href="{SITE}{path}">
{ICON_LINKS}
  <link rel="stylesheet" href="/shared/site.css">
  <script type="module" src="/shared/site.js"></script>
{ld_block(breadcrumb_ld([(city_name, f"/{ctx['city']}/"),
                         (area_name, f"/{ctx['city']}/{ctx['area']}/"),
                         (disp, None)]))}
{ld_block(collection_ld(path, disp, desc,
                        [(title, f"{path}{href}/")
                         for _n, href, title, _hook in entries]))}
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
{cols_close}{nearby}</main>

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
    return True


NEIGHBORHOOD_SECTION = "Streets documented so far"


def existing_street_hooks(area_dir: Path) -> dict:
    """slug -> the hook a neighborhood hub already shows for that street.

    A street's line on the neighborhood hub is generated ("3 buildings, built
    1901–1986"), but a person will often have replaced it with something worth
    reading ("The Crocker Bank Building of 1908, and two buildings on the block
    where Samuel Brannan built in 1853"). Rebuilding the list to add one street
    must not throw the rest of them away — this is the same courtesy `hub_lead`
    pays a street hub's own intro paragraph.

    index.md is the source of truth for a hub page's hand-written content —
    index.html is a rendering of it, never edited independently (see
    AGENTS.md's "Hub pages" note and `scripts/validate.py`'s
    `check_hub_sync`, which fails the build if the two disagree). So only
    index.md is read here.
    """
    md = area_dir / "index.md"
    if not md.exists():
        return {}
    return {m.group(1): m.group(2).strip() for m in re.finditer(
        r"^- \[[^\]]+\]\(([^/)]+)/\)\s+—\s+(.+)$", md.read_text(encoding="utf-8"),
        re.M)}


def street_summary(street_dir: Path, kept: dict = None) -> tuple:
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
    return disp, len(recs), (kept or {}).get(street_dir.name) or hook + "."


def write_neighborhood_hub(area_dir: Path, ctx: dict) -> int:
    """Rewrite only the street list on a neighborhood hub.

    The rest of the page — the lead, the naming explanation, the closing note —
    is a human's prose and is left exactly as it is, and so is any hook a person
    has written for a street already on the list.
    """
    kept = existing_street_hooks(area_dir)
    streets = []
    for street_dir in sorted(area_dir.iterdir()):
        if not street_dir.is_dir():
            continue
        summary = street_summary(street_dir, kept)
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
        html_path.write_text(neighborhood_ld(new, area_dir, streets),
                             encoding="utf-8")
    return len(streets)


# Everything from the shared enhancement script to the end of the head. A
# neighborhood hub is otherwise a human's prose that this file only patches, so
# its structured data is rewritten wholesale in the one region no hand-written
# content occupies — replacing the region rather than inserting into it is what
# makes a second `hubs` run leave the page alone.
HUB_HEAD_LD = re.compile(
    r'(<script type="module" src="/shared/site\.js"></script>)'
    r'.*?(\n</head>)', re.S)


def neighborhood_ld(text: str, area_dir: Path, streets: list) -> str:
    """Put the hub's `BreadcrumbList` and `ItemList` in its `<head>`."""
    city_slug, area_slug = area_dir.parent.name, area_dir.name
    path = f"/{city_slug}/{area_slug}/"
    city_name = " ".join(w.capitalize() for w in city_slug.split("-"))
    disp = area_display(path)
    m = re.search(r'<meta name="description" content="([^"]*)"', text)
    desc = html.unescape(m.group(1)) if m else disp
    blocks = "\n".join(ld_block(obj) for obj in (
        breadcrumb_ld([(city_name, f"/{city_slug}/"), (disp, None)]),
        collection_ld(path, disp, desc,
                      [(street_disp, f"{path}{slug}/")
                       for slug, street_disp, _n, _hook in streets])))
    out, n = HUB_HEAD_LD.subn(lambda m: f"{m.group(1)}\n{blocks}{m.group(2)}", text)
    if not n:
        raise SystemExit(f"{area_dir / 'index.html'}: no <head> to put "
                         f"structured data in")
    return out


# --------------------------------------------------------------------------
# Historic-district hubs
# --------------------------------------------------------------------------
# The fourth page type, and the only aggregation on this site that isn't the
# containment tree. A historic district is a real subject with a record of its
# own — the city's surveys drew its boundary, dated its period of significance
# and set down its standing on the registers — which is what separates it from
# a facet. Decade, zoning and property-class lists have no such record behind
# them and are deliberately not built.
#
# They sit at city level rather than under a neighborhood because a district is
# not contained by one: the Chinatown Historic District runs through five
# neighborhood directories and Kearny-Market-Mason-Sutter through six.
DISTRICTS_DIR = "historic-districts"
DISTRICTS_TITLE = "Historic districts"

# Below this a district's list says nothing the one or two pages carrying it
# don't already say, and a list that thin is a doorway page rather than an
# encyclopedia entry. Those pages keep their district panel; it just has
# nowhere to link.
DISTRICT_MIN_PAGES = 5

DISTRICT_DATASET_URL = "https://data.sfgov.org/resource/63x5-g3m4.json"

# Read off the *name*, not off `split_district_name`'s lifted type phrase,
# which lowercases it. Six districts in the data are an Extension sharing a
# base name with the district they extend, so dropping the qualifier would put
# two districts at one URL.
DISTRICT_QUALIFIER = re.compile(r"\s+(Extension|Addition|\(Discontiguous\))$")


def slugify(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower().replace("&", " and ")).strip("-")


def district_short_name(name: str) -> str:
    """"Duboce Triangle Historic District Extension" -> "Duboce Triangle Extension".

    The parent directory already says these are historic districts, so the slug
    and the breadcrumb drop the type phrase and keep the qualifier.
    """
    base, _kind = split_district_name(name)
    if base == name:
        return name          # no type phrase to lift; the name is all there is
    m = DISTRICT_QUALIFIER.search(name)
    return f"{base} {m.group(1)}" if m else base


def district_slug(name: str) -> str:
    return slugify(district_short_name(name))


DISTRICT_FIELDS = ("california_register_status", "national_register_status",
                   "article_10_11_status", "local_landmark_protection",
                   "period_of_significance")


def merge_district_records(name: str, records: list) -> dict:
    """One district record out of the many copies of it the pages carry.

    Three districts disagree with themselves. The survey holds two rows over
    the same ground under one name — one carrying an Article 10 designation,
    the other a register listing — and only some parcels fall inside the second
    row's boundary. `merge_districts` already takes the stronger status where
    both rows cover one parcel, so what is left here is a real split in the
    data rather than a merge bug.

    The hub reports what the pages beneath it report: the majority value, ties
    broken toward the stronger standing and then alphabetically so a rebuild is
    deterministic. Taking the strongest value outright would put the hub in
    contradiction with twenty-three of the twenty-four pages it lists.
    """
    out = {"name": name}
    for key in DISTRICT_FIELDS:
        vals = [r[key] for r in records if r.get(key) not in (None, "")]
        if not vals:
            continue
        counts = collections.Counter(vals)
        out[key] = max(counts, key=lambda v: (counts[v],
                                              -STANDING_RANK[standing_tier(str(v))],
                                              str(v)))
    return out


def districts_named(rec: dict) -> dict:
    """Every district this page stands in: name -> the record it carries for it.

    Both memberships count. A parcel inside overlapping districts headlines one
    under `historic_district` and records the rest under `also_in_districts`;
    to a district those are the same fact, and reading only the headline would
    lose seven districts outright — every one of the forty buildings in the
    Liberty Street Historic District headlines Liberty Hill instead.

    `validate.py` calls this too, so the hub and the check that the hub is
    current read membership by one rule rather than two.
    """
    found: dict = {}
    primary = district_record(rec)
    if primary.get("name"):
        found[primary["name"]] = primary
    for other in rec.get("also_in_districts") or []:
        if other.get("name") and other["name"] not in found:
            found[other["name"]] = other
    return found


def district_memberships(city_dir: Path) -> dict:
    """district name -> [(page_dir, rec, its district record)] across the city."""
    out: dict = collections.defaultdict(list)
    for data_path in sorted(city_dir.rglob("data.json")):
        page_dir = data_path.parent
        if not ADDRESS_DIR.match(page_dir.name):
            continue
        try:
            rec = json.loads(data_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            print(f"  {data_path}: invalid JSON — skipped", file=sys.stderr)
            continue
        for name, d in districts_named(rec).items():
            out[name].append((page_dir, rec, d))
    return out


def district_members(pages: list) -> list:
    """One row per building on a district hub, in the order the page lists them.

    Grouped by street and then by number, which is how a reader walks a
    district; ordering by number alone would interleave four streets.
    """
    rows = []
    for page_dir, rec, d in pages:
        street_dir = page_dir.parent
        rows.append({
            "path": "/" + page_dir.relative_to(ROOT).as_posix() + "/",
            "title": page_title(rec),
            # The district is the whole page here, so the hook doesn't repeat
            # it — and a building in two districts would otherwise name the
            # other one on this hub's list.
            "hook": hook_for(rec, with_district=False),
            "street_path": "/" + street_dir.relative_to(ROOT).as_posix() + "/",
            "street": page_title(rec).split(" ", 1)[-1],
            "area_path": "/" + street_dir.parent.relative_to(ROOT).as_posix() + "/",
            "number": page_dir.name,
            "year_built": (rec.get("parcel") or {}).get("year_built"),
            # What DBI holds, not what the page shows — same rule as a street
            # hub's permit tile.
            "permits": ((rec.get("permit_summary") or {}).get("count_on_file")
                        or len(rec.get("permits", []))),
            "sources": rec.get("sources", []),
            "record": d,
        })
    rows.sort(key=lambda r: (r["street"], r["street_path"], num_key(r["number"])))
    return rows


def area_display(area_path: str) -> str:
    """A neighborhood's own name for itself, off the h1 of its hub.

    The slug can't be reversed into it — "castro" is filed as "Castro / Eureka
    Valley" and "lone-mountain" as "Lone Mountain / USF".
    """
    md = ROOT / area_path.strip("/") / "index.md"
    if md.exists():
        for line in md.read_text(encoding="utf-8").splitlines():
            if line.startswith("# "):
                return line[2:].strip()
    return " ".join(w.capitalize()
                    for w in area_path.strip("/").split("/")[-1].split("-"))


def district_standing_clause(d: dict) -> str:
    """The one thing about a district's paperwork worth putting on a hub line.

    A local designation outranks a register for the same reason it outranks the
    name's own type in the panel eyebrow: it is what the district *is*.
    """
    a = d.get("article_10_11_status") or ""
    if a.startswith("Article 10"):
        return "An Article 10 city landmark district"
    if a.startswith("Article 11"):
        return "An Article 11 conservation district"
    rows = standing_rows(d)
    return rows[0][1] if rows else ""


def district_hook(d: dict, n_pages: int, n_streets: int) -> str:
    """A district's line on the index — standing, dates, and how much is here.

    Deliberately not where the district is: naming neighborhoods would put an
    article in front of half of them and not the other half ("in the Mission",
    "in Hayes Valley"), and the district's own page carries that list.
    """
    streets = "one street" if n_streets == 1 else f"{n_streets:,} streets"
    where = f"{n_pages:,} buildings documented on {streets}"
    clause = district_standing_clause(d)
    pos = (d.get("period_of_significance") or "").strip()
    if clause and pos and pos.upper() != "N/A":
        return f"{clause}, significant {pos}; {where}."
    if clause:
        return f"{clause}; {where}."
    return f"{where.capitalize()}."


def hub_shell(path: str, title: str, desc: str, crumbs: str, main_html: str,
              sources: str, feedback_title: str, ld: list = None) -> str:
    """The shared page chrome for the two historic-district page types.

    The skeleton in shared/BLOCKS.md, written once because these two writers
    produce it identically. The street and neighborhood hubs predate this and
    keep their own copy — routing them through here would re-render every hub
    on the site for no change a reader could see.
    """
    ld_blocks = "".join("\n" + ld_block(obj) for obj in ld or ())
    sources_block = ""
    if sources:
        sources_block = ('  <section class="sources">\n    <h2>Sources</h2>\n'
                         f'    <ul>\n{sources}\n    </ul>\n  </section>\n')
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{esc(title)} — Know This Place</title>
  <meta name="description" content="{esca(desc)}">
  <link rel="canonical" href="{SITE}{path}">
{ICON_LINKS}
  <link rel="stylesheet" href="/shared/site.css">
  <script type="module" src="/shared/site.js"></script>{ld_blocks}
</head>
<body>
<header class="site-header">
  <a class="wordmark" href="/">Know This Place</a>
  <nav class="breadcrumb" aria-label="Breadcrumb">
{crumbs}
  </nav>
</header>

<main>
{main_html}</main>

<footer class="site-footer">
{sources_block}  <p class="feedback-cta">
    <a href="{feedback_url(feedback_title, path)}">Request an edit</a>
  </p>
  <p class="colophon">Part of <a href="/">Know This Place</a>, a community
  encyclopedia of the built environment. Facts are cited; pages are reviewed
  by people. <a href="{REPO}">Source</a>.</p>
</footer>
</body>
</html>
"""


def stat_tiles_html(tiles: list, indent: str) -> str:
    return "\n".join(
        f'{indent}<div class="stat"><span class="ic {i}"></span>'
        f'<span class="stat-val">{v}</span>'
        f'<span class="stat-label">{esc(label)}</span></div>'
        for i, v, label in tiles)


def place_list_html(items: list, indent: str) -> str:
    """The list markup every hub uses — and the markup `validate.check_hub_sync`
    reads back, so each line written here has a matching bullet in index.md."""
    return "\n".join(
        f'{indent}<li><a href="{esca(href)}">{esc(label)}</a><br>\n'
        f'{indent}  <span class="hook">{esc(hook)}</span></li>'
        for href, label, hook in items)


def district_sources_html(name: str, members: list) -> str:
    """The footer for a district hub: the survey the district record comes from.

    The counts and the date span are read off the pages listed on the page,
    each of which carries its own footer — the same way a street hub cites
    nothing of its own. What this page states that they don't is the district's
    record, and that is this one dataset. The query is the district's own row
    by name rather than the point-intersect query a parcel page ran; the
    retrieval date is the most recent one across the pages listed here.
    """
    seen = collections.Counter()
    names: dict = {}
    retrieved: dict = collections.defaultdict(list)
    for m in members:
        for s in m["sources"]:
            if s.get("id") in ("sf-historic-districts", "sf-planning"):
                seen[s["id"]] += 1
                names.setdefault(s["id"], s.get("name") or s["id"])
                if s.get("retrieved"):
                    retrieved[s["id"]].append(s["retrieved"])
    if "sf-historic-districts" in seen:
        sid = "sf-historic-districts"
    elif seen:
        sid = seen.most_common(1)[0][0]
    else:
        return ""
    query = f"{DISTRICT_DATASET_URL}?name_1={urllib.parse.quote(name, safe='')}"
    rec = {"sources": [{"id": sid, "name": names[sid], "query": query,
                        "retrieved": max(retrieved[sid]) if retrieved[sid] else None}]}
    return sources_html(rec)


KNOWN_DISTRICT_HUB_SECTIONS = (re.compile(r"^streets$", re.I),
                               re.compile(r"^buildings$", re.I))
KNOWN_DISTRICT_INDEX_SECTIONS = (re.compile(r"^districts documented so far$", re.I),)


def write_district_hub(dist_dir: Path, name: str, members: list) -> bool:
    """Write one district's index.md + index.html. False if it refused to.

    It refuses for the reason `write_street_hub` does: a hub that has grown
    sections this template has no room for is a person's page from then on, and
    the generator has no way to merge them back in.
    """
    extra = hub_extra_sections(dist_dir, KNOWN_DISTRICT_HUB_SECTIONS)
    if extra:
        print(f"  {dist_dir}: skipping — hand-written section(s) "
              f"{', '.join(extra)} beyond the generated template; "
              f"update the lists by hand instead", file=sys.stderr)
        return False

    d = merge_district_records(name, [m["record"] for m in members])
    short = district_short_name(name)
    path = f"/san-francisco/{DISTRICTS_DIR}/{district_slug(name)}/"

    streets: dict = {}
    for m in members:
        s = streets.setdefault(m["street_path"], {"name": m["street"], "n": 0,
                                                  "area": m["area_path"]})
        s["n"] += 1
    areas = collections.Counter(m["area_path"] for m in members)

    years = sorted(m["year_built"] for m in members if m["year_built"])
    n_permits = sum(m["permits"] for m in members)

    tiles = [("ic-home", f"{len(members):,}", "Buildings documented")]
    if years:
        span = (f"{years[0]}<small>–{years[-1]}</small>" if years[0] != years[-1]
                else f"{years[0]}")
        tiles.append(("ic-calendar", span, "Construction dates"))
    tiles.append(("ic-pin", f"{len(streets):,}", "Streets"))
    tiles.append(("ic-permit", f"{n_permits:,}", "Permit records"))

    lead = hub_lead(dist_dir,
                    f"The buildings documented here so far inside the {name}, "
                    f"and the streets it runs through.")

    # A street name is not unique across the city: a district spanning two
    # neighborhoods can hold two different Market Streets. Say which, but only
    # where it is actually ambiguous.
    repeated = {n for n, c in collections.Counter(
        s["name"] for s in streets.values()).items() if c > 1}
    street_items = []
    for href in sorted(streets, key=lambda h: (streets[h]["name"], h)):
        s = streets[href]
        label = (f"{s['name']}, {area_display(s['area'])}"
                 if s["name"] in repeated else s["name"])
        street_items.append((href, label,
                             f"{s['n']:,} documented building"
                             f"{'' if s['n'] == 1 else 's'} inside the district."))
    building_items = [(m["path"], m["title"], m["hook"]) for m in members]

    md = [f"# {name}", "", lead, "", "## Streets", ""]
    md += [f"- [{label}]({href}) — {hook}" for href, label, hook in street_items]
    md += ["", "## Buildings", ""]
    md += [f"- [{label}]({href}) — {hook}" for href, label, hook in building_items]
    md += ["", "The district record is the city's; the buildings beneath it are",
           "generated from the DataSF datasets listed in each page's Sources",
           "footer, and are corrected by hand as readers write in.", ""]
    (dist_dir / "index.md").write_text("\n".join(md), encoding="utf-8")

    # Identity, so tags rather than tiles (shared/AGENTS.md): what kind of
    # district it is, and when it mattered. Its standing on the registers is a
    # separate question and takes the `.standing` list below.
    tags = [("ic-plan", district_eyebrow(d, split_district_name(name)[1]))]
    pos = (d.get("period_of_significance") or "").strip()
    if pos and pos.upper() != "N/A":
        tags.append(("ic-calendar", f"Significant {pos}"))
    tags_block = "\n".join(f'    <li class="tag"><span class="ic {i}"></span>'
                           f'{esc(label)}</li>' for i, label in tags)

    aside = ""
    rows = standing_rows(d)
    if rows:
        lines = []
        for tier, sentence in rows:
            cls = ' class="is-none"' if tier == "none" else ""
            lines.append(f'          <li{cls}><span class="ic '
                         f'{STANDING_ICON[tier]}"></span>{esc(sentence)}</li>')
        aside += ('      <section class="panel">\n'
                  '        <h3>Designation</h3>\n'
                  '        <ul class="standing">\n'
                  + "\n".join(lines) + '\n        </ul>\n'
                  '      </section>\n')
    area_rows = "\n".join(
        f'          <div class="spec"><span class="ic ic-pin"></span>'
        f'<span class="spec-k"><a href="{esca(href)}">{esc(area_display(href))}</a>'
        f'</span><span class="spec-v">{n:,}</span></div>'
        for href, n in sorted(areas.items(), key=lambda kv: (-kv[1], kv[0])))
    aside += ('      <section class="panel">\n'
              '        <h3>Neighborhoods</h3>\n'
              f'        <dl class="speclist">\n{area_rows}\n        </dl>\n'
              '      </section>\n')

    main_html = f"""  <h1>{esc(name)}</h1>
  <ul class="tags">
{tags_block}
  </ul>

  <p class="lead">{esc(lead)}</p>

  <div class="stats">
{stat_tiles_html(tiles, "    ")}
  </div>

  <div class="cols">
    <div class="main">
      <div class="section-head"><span class="ic ic-pin"></span><h2>Streets</h2></div>
      <ul class="place-list">
{place_list_html(street_items, "        ")}
      </ul>

      <div class="section-head"><span class="ic ic-home"></span><h2>Buildings</h2></div>
      <ul class="place-list">
{place_list_html(building_items, "        ")}
      </ul>
    </div>

    <aside class="aside">
{aside}    </aside>
  </div>
"""

    n_streets = len(streets)
    desc = (f"{name}, San Francisco: {len(members):,} documented building"
            f"{'' if len(members) == 1 else 's'} on "
            f"{'one street' if n_streets == 1 else f'{n_streets:,} streets'}, "
            f"with construction dates, permits and the district's register "
            f"standing, fully cited.")
    crumbs = ('    <a href="/san-francisco/">San Francisco</a>\n'
              f'    <a href="/san-francisco/{DISTRICTS_DIR}/">{DISTRICTS_TITLE}</a>\n'
              f'    <span aria-current="page">{esc(short)}</span>')
    (dist_dir / "index.html").write_text(
        hub_shell(path, f"{name}, San Francisco", desc, crumbs, main_html,
                  district_sources_html(name, members), name,
                  ld=[breadcrumb_ld([
                          ("San Francisco", "/san-francisco/"),
                          (DISTRICTS_TITLE, f"/san-francisco/{DISTRICTS_DIR}/"),
                          (short, None)]),
                      # The buildings, not the streets: the streets list above
                      # them is a way into the same set, and declaring both
                      # would state one collection twice.
                      collection_ld(path, name, desc,
                                    [(m["title"], m["path"]) for m in members])]),
        encoding="utf-8")
    return True


def write_districts_index(index_dir: Path, listed: list, held_back: int) -> bool:
    """The index at /san-francisco/historic-districts/.

    `listed` is (name, merged record, buildings, streets, area paths) per
    district that earned a page, in the order the index shows them.
    """
    extra = hub_extra_sections(index_dir, KNOWN_DISTRICT_INDEX_SECTIONS)
    if extra:
        print(f"  {index_dir}: skipping — hand-written section(s) "
              f"{', '.join(extra)} beyond the generated template; "
              f"update the list by hand instead", file=sys.stderr)
        return False

    items = [(f"{district_slug(name)}/", name, district_hook(d, n_pages, n_streets))
             for name, d, n_pages, n_streets, _areas in listed]
    n_buildings = sum(n for _name, _d, n, _s, _a in listed)
    n_areas = len({a for *_head, areas in listed for a in areas})

    lead = hub_lead(index_dir,
                    "The historic districts San Francisco's surveys have drawn, "
                    "and the buildings documented inside each one. A district "
                    "page lists every building here that stands within it, and "
                    "the streets it runs through.")
    held = (f"{held_back:,} further district{'' if held_back == 1 else 's'} named "
            f"on the pages here hold fewer than {DISTRICT_MIN_PAGES} documented "
            f"buildings, and have no page yet.")

    md = [f"# {DISTRICTS_TITLE}", "", lead, "", "## Districts documented so far", ""]
    md += [f"- [{label}]({href}) — {hook}" for href, label, hook in items]
    md += ["", held, ""]
    (index_dir / "index.md").write_text("\n".join(md), encoding="utf-8")

    tiles = [("ic-plan", f"{len(items):,}", "Districts"),
             ("ic-home", f"{n_buildings:,}", "Buildings documented"),
             ("ic-pin", f"{n_areas:,}", "Neighborhoods")]
    main_html = f"""  <h1>{DISTRICTS_TITLE}</h1>
  <p class="lead">{esc(lead)}</p>

  <div class="stats">
{stat_tiles_html(tiles, "    ")}
  </div>

  <div class="section-head"><span class="ic ic-plan"></span><h2>Districts documented so far</h2></div>
  <ul class="place-list">
{place_list_html(items, "    ")}
  </ul>

  <p>{esc(held)}</p>
"""
    desc = (f"The {len(items):,} San Francisco historic districts with buildings "
            f"documented on Know This Place: {n_buildings:,} buildings across "
            f"{n_areas:,} neighborhoods, with register standing and periods of "
            f"significance, fully cited.")
    crumbs = ('    <a href="/san-francisco/">San Francisco</a>\n'
              f'    <span aria-current="page">{DISTRICTS_TITLE}</span>')
    (index_dir / "index.html").write_text(
        hub_shell(f"/san-francisco/{DISTRICTS_DIR}/",
                  f"{DISTRICTS_TITLE}, San Francisco", desc, crumbs, main_html,
                  "", f"{DISTRICTS_TITLE}, San Francisco",
                  ld=[breadcrumb_ld([("San Francisco", "/san-francisco/"),
                                     (DISTRICTS_TITLE, None)]),
                      collection_ld(f"/san-francisco/{DISTRICTS_DIR}/",
                                    DISTRICTS_TITLE, desc,
                                    [(label, f"/san-francisco/{DISTRICTS_DIR}/{href}")
                                     for href, label, _hook in items])]),
        encoding="utf-8")
    return True


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

    rebuilt_hubs = sum(1 for street_dir in sorted(touched_streets)
                       if write_street_hub(street_dir, ctx, not_covered.get(street_dir.name)))
    n_streets = write_neighborhood_hub(ROOT / args.city / args.area, ctx)
    print(f"neighborhood hub lists {n_streets} street(s)")
    print(f"created {written} new page(s); left {skipped} existing page(s) "
          f"untouched; skipped {elsewhere} parcel(s) already documented under "
          f"another neighborhood; rebuilt {rebuilt_hubs} street hub(s)"
          + (f"; left {len(touched_streets) - rebuilt_hubs} street hub(s) untouched "
             f"(hand-written sections)" if rebuilt_hubs < len(touched_streets) else ""))
    if excluded:
        print(f"excluded streets (filed under another neighborhood): "
              f"{', '.join(sorted(excluded))}")
    if deferred:
        print(f"deferred for a human — {len(deferred)} parcel(s) share a street "
              f"number with another parcel:")
        for note in sorted(deferred.values()):
            print(f"  {note}")
    return 0


# --------------------------------------------------------------------------
# Render
#
# `seed` creates; `render` re-renders. The two never overlap: `seed` refuses to
# write into a directory that has a page, and `render` refuses to invent one
# where there is no `data.json`.
# --------------------------------------------------------------------------
RENDER_BACKLOG_PATH = ROOT / "scripts" / "render-backlog.txt"


def load_render_backlog() -> set:
    """The page directories `scripts/render-backlog.txt` grandfathers.

    That file lists pages whose committed `index.html` predates the parity
    check and is not what the renderer produces — hand-written prose, mostly,
    including the site's only address-to-address links written before there
    was an index to generate them from. `validate.py` reads it to excuse those
    pages from parity; `cmd_render` reads it to refuse to overwrite them,
    which is the half that was missing. Rendering one is how the drift gets
    destroyed rather than resolved, so it takes `--include-backlogged` and a
    person who has looked at the diff (issue #147's sweep).

    Returns paths relative to the repo root, as the file stores them.
    """
    if not RENDER_BACKLOG_PATH.exists():
        return set()
    return {ln.strip()
            for ln in RENDER_BACKLOG_PATH.read_text(encoding="utf-8").splitlines()
            if ln.strip() and not ln.lstrip().startswith("#")}


def renders(rec: dict) -> bool:
    """Whether this page's `index.html` is generated from its `data.json`.

    Every page is, unless its `data.json` says `"rendered": false`. The opt-out
    exists for a page whose HTML a person genuinely maintains by hand, and it
    is deliberately narrow, because it is not free: an opted-out page no longer
    tracks site-wide design changes, so the next time the stylesheet or a block
    changes it quietly falls behind. `validate.py` prints the opt-out count on
    every run for exactly that reason.

    Only an explicit `false` opts out. A missing key — the normal case, and
    what `seed` writes — means the page renders.
    """
    return rec.get("rendered") is not False


def page_dirs(paths) -> list:
    """Every address page directory under the given paths, sorted, deduplicated.

    A path may name one page, a street, a neighborhood, or the whole city; the
    walk is the same either way, which is what lets one command serve a
    one-line fix and a corpus-wide re-render. A `data.json` file is accepted in
    place of the directory holding it.
    """
    out = set()
    for raw in paths:
        p = Path(raw)
        if not p.is_absolute():
            p = Path.cwd() / p
        p = p.resolve()
        if p.is_file() and p.name == "data.json":
            p = p.parent
        if not p.exists():
            raise SystemExit(f"render: no such path: {raw}")
        if p != ROOT and ROOT not in p.parents:
            raise SystemExit(f"render: {raw} is outside the repo")
        if (p / "data.json").is_file():
            out.add(p)
        else:
            out.update(f.parent for f in p.rglob("data.json")
                       if ADDRESS_DIR.match(f.parent.name))
    return sorted(out)


def cmd_render(args) -> int:
    """Rewrite `index.html` from `data.json` for every page under a path."""
    dirs = page_dirs(args.path)
    if not dirs:
        print(f"no address pages under {', '.join(args.path)}", file=sys.stderr)
        return 1

    backlog = set() if args.include_backlogged else load_render_backlog()
    rewritten, current, opted_out, failed = 0, 0, 0, 0
    held_back = []
    for page_dir in dirs:
        rel = page_dir.relative_to(ROOT).as_posix()
        if rel in backlog:
            held_back.append(rel)
            continue
        try:
            rec = json.loads((page_dir / "data.json").read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            print(f"  {rel}: invalid JSON: {e}", file=sys.stderr)
            failed += 1
            continue
        if not renders(rec):
            opted_out += 1
            continue
        try:
            out = render_html(rec)
        except Exception as e:
            # One page the renderer can't produce must not abandon the rest of
            # the sweep. Report it, keep going, and fail the run at the end.
            print(f"  {rel}: {type(e).__name__}: {e}", file=sys.stderr)
            failed += 1
            continue
        html_path = page_dir / "index.html"
        if html_path.exists() and html_path.read_text(encoding="utf-8") == out:
            current += 1
            continue
        if args.dry_run:
            print(f"  {rel}")
        else:
            html_path.write_text(out, encoding="utf-8")
        rewritten += 1

    verb = "would rewrite" if args.dry_run else "rewrote"
    print(f"{len(dirs)} page(s): {verb} {rewritten}, left {current} already "
          f"current, skipped {opted_out} opted out of rendering"
          + (f", held back {len(held_back)} backlogged" if held_back else "")
          + (f", FAILED on {failed}" if failed else ""))
    if held_back:
        print(f"{len(held_back)} page(s) held back — scripts/render-backlog.txt "
              f"grandfathers HTML the renderer cannot reproduce, and rendering "
              f"one overwrites prose no data.json holds. Read the diff first, "
              f"then re-run with --include-backlogged:")
        for rel in held_back[:10]:
            print(f"  {rel}")
        if len(held_back) > 10:
            print(f"  … and {len(held_back) - 10} more")
    if opted_out:
        print(f'{opted_out} page(s) carry "rendered": false and no longer track '
              f"site-wide design changes")
    return 1 if failed else 0


# Deliberately over-broad: it is cheap to review a false positive and costly to
# publish a real name, so this catches role labels, firm suffixes and titles and
# leaves the judgement to a reviewer.
NAME_HINT = re.compile(
    # DBI's intake prefixes name a person with no role label anywhere near them
    # — "one-stop:peter burns:" carries none of the words below, so the Japantown
    # run seeded two pages with a name on them before this line existed.
    r"\b(one-?stop|onestop)\b\s*[:.]?\s*[a-z]"
    r"|\b(owner|owners|attn|attention|applicant|contact|c/o|architect|architects|"
    r"engineer|engineering|contractor|contracting|tenant|landlord|purchaser|"
    # "per inspector adwin lau" and two dozen like it sat on published
    # pages because the DBI inspector is the one role this list did not
    # know, and no other pattern fires on a bare first-and-last name.
    r"inspector|inspectors|"
    r"mr|mrs|ms|dr)\b[.:]?\s+\S"
    r"|\b(inc|llc|l\.l\.c|corp|corporation|company|associates|assoc|builders|"
    r"construction|develop(ment|ers)|partners|group|realty|properties)\b"
    # A name can also arrive with no role label at all, introduced by a bare
    # preposition — "walk in cooler per jesus zapien" reached a Marina page
    # because every pattern above looks for a label the sentence never uses.
    # Two lowercase words after "per"/"by" is noisy ("per field findings") and
    # that is the right trade: this list is reviewed by a person, and a miss is
    # a name on a page.
    r"|\b(per|by)\b\s+[a-z]{2,}\s+[a-z]{2,}\b"
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


def cmd_seed_list(args) -> int:
    """Seed the parcels named in a manifest file, rather than a whole neighborhood.

    `seed` walks an analysis neighborhood and takes the residential parcels in
    it. That is the right default and the wrong tool for a *thematic* set — the
    buildings named in the city's public-art and privately-owned-public-open-
    space inventories are downtown offices, hotels and garages scattered across
    seven neighborhood directories. It is also the wrong tool for downtown for a
    second reason: those blocks have been re-parcelized repeatedly, so EAS often
    still carries a retired APN and the address→parcel join `seed` relies on
    silently misses. So the manifest states the parcel outright, and this
    command joins the datasets onto it.

    The manifest is a JSON array; each entry is one page:

        {"apn": "3721120", "city": "san-francisco", "area": "east-cut",
         "street_slug": "mission-street", "street_name": "MISSION",
         "street_type": "ST", "street_display": "Mission Street",
         "numbers": ["555"], "other_street_addresses": [],
         "lat": 37.7884, "lng": -122.3989, "zip": "94105",
         "eas_baseid": "…", "supervisor": "6"}

    Everything else about the split holds: a directory that already has a page
    is left alone, and the draft it writes is edited only by hand afterwards.
    """
    entries = json.loads(Path(args.manifest).read_text())
    roll_year = int(api_get(DS_ROLL, {"$select": "max(closed_roll_year)"})[0]
                    ["max_closed_roll_year"])
    apns = sorted({e["apn"] for e in entries})
    tag = re.sub(r"[^a-z0-9]+", "-", Path(args.manifest).stem.lower()).strip("-")
    roll = fetch_keyed(f"roll{roll_year}__{tag}.json", DS_ROLL, "parcel_number", apns,
                       select=ROLL_SELECT, where=f"closed_roll_year={roll_year}",
                       chunk=100, refresh=args.refresh)
    historic = fetch_keyed(f"historic__{tag}.json", DS_HISTORIC, "apn", apns,
                           select=HISTORIC_SELECT, chunk=200, refresh=args.refresh)
    districts = fetch_paged("districts.json", DS_DISTRICTS, select=DISTRICT_SELECT,
                            page=25, refresh=args.refresh)
    roll_by_apn = {r["parcel_number"]: r for r in roll}
    blocks = sorted({r["block"] for r in roll if r.get("block")})
    permits = fetch_keyed(f"permits__{tag}.json", DS_PERMITS, "block", blocks,
                          select=PERMIT_SELECT, chunk=1, page=1500, refresh=args.refresh)

    inv = []
    for e in entries:
        r = roll_by_apn.get(e["apn"])
        if not r:
            print(f"  no {roll_year} roll row for {e['apn']} "
                  f"({e['numbers'][0]} {e['street_display']}) — skipped", file=sys.stderr)
            continue
        row = {**e, "roll": r, "permits": []}
        # A manifest states the parcel outright, which is the point of this
        # command — but stating it is not evidence that it is a building. The
        # same verdict `seed` applies has to run here too, or a condominium
        # unit named in a report gets a page of its own, which AGENTS.md
        # forbids.
        row["status"] = classify(row)
        if row["status"] != "seedable":
            print(f"  {row['status']} for {e['apn']} "
                  f"({e['numbers'][0]} {e['street_display']}) — skipped",
                  file=sys.stderr)
            continue
        inv.append(row)
    attach_permits(inv, permits)

    written, skipped, elsewhere = 0, 0, 0
    touched: dict = collections.defaultdict(set)
    covered = existing_pages_by_apn()
    for row in inv:
        ctx = make_ctx(argparse.Namespace(
            city=row["city"], area=row["area"], retrieved=args.retrieved),
            {"roll_year": roll_year, "historic": historic, "districts": districts})
        rec = build_record(row, ctx)
        prior = covered.get(row["apn"])
        if prior and prior != rec["path"]:
            print(f"  {rec['path']}: parcel {row['apn']} is already documented "
                  f"at {prior} — skipped", file=sys.stderr)
            elsewhere += 1
            continue
        page_dir = ROOT / rec["path"].strip("/")
        touched[(row["city"], row["area"])].add(page_dir.parent)
        if (page_dir / "data.json").exists() or (page_dir / "index.html").exists():
            skipped += 1          # the page exists; it is a human's to edit
            continue
        page_dir.mkdir(parents=True, exist_ok=True)
        (page_dir / "data.json").write_text(
            json.dumps(rec, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        (page_dir / "index.html").write_text(render_html(rec), encoding="utf-8")
        written += 1

    n_streets = 0
    for (city, area), street_dirs in sorted(touched.items()):
        ctx = make_ctx(argparse.Namespace(city=city, area=area, retrieved=args.retrieved),
                       {"roll_year": roll_year, "historic": historic,
                        "districts": districts})
        for street_dir in sorted(street_dirs):
            if write_street_hub(street_dir, ctx):
                n_streets += 1
        area_dir = ROOT / city / area
        if (area_dir / "index.html").exists():
            write_neighborhood_hub(area_dir, ctx)
        else:
            print(f"  {area_dir}: no neighborhood hub yet — write one by hand",
                  file=sys.stderr)
    print(f"created {written} new page(s); left {skipped} existing page(s) untouched; "
          f"skipped {elsewhere} parcel(s) documented elsewhere; "
          f"rebuilt {n_streets} street hub(s) across {len(touched)} neighborhood(s)")
    return 0


def cmd_districts(args) -> int:
    """Rebuild the historic-district hubs from the pages that name a district.

    A derived index, like the sitemap and the map: it holds nothing of its own
    beyond a hand-written lead, so re-running it after pages are added or
    removed is always safe and always the fix when it has gone stale.
    """
    city_dir = ROOT / args.city
    memberships = district_memberships(city_dir)
    index_dir = city_dir / DISTRICTS_DIR
    index_dir.mkdir(parents=True, exist_ok=True)

    earned, held_back, by_slug = [], 0, {}
    for name in sorted(memberships):
        if len(memberships[name]) < args.min_pages:
            held_back += 1
            continue
        slug = district_slug(name)
        if slug in by_slug:
            raise SystemExit(f"two districts share the slug '{slug}': "
                             f"{by_slug[slug]!r} and {name!r} — "
                             f"district_short_name needs to tell them apart")
        by_slug[slug] = name
        earned.append(name)

    written, skipped, listed = 0, 0, []
    for name in earned:
        members = district_members(memberships[name])
        dist_dir = index_dir / district_slug(name)
        dist_dir.mkdir(parents=True, exist_ok=True)
        if write_district_hub(dist_dir, name, members):
            written += 1
        else:
            skipped += 1
        # A hub the writer refused to touch is still a district with a page,
        # so it keeps its line on the index.
        listed.append((name,
                       merge_district_records(name, [m["record"] for m in members]),
                       len(members),
                       len({m["street_path"] for m in members}),
                       {m["area_path"] for m in members}))
    write_districts_index(index_dir, listed, held_back)

    for stale in sorted(index_dir.iterdir()):
        if stale.is_dir() and stale.name not in by_slug:
            print(f"  {stale}: no district with {args.min_pages} or more "
                  f"documented buildings maps here any more — remove it by hand",
                  file=sys.stderr)
    print(f"wrote {written} district hub(s); left {skipped} untouched "
          f"(hand-written sections); held back {held_back} district(s) under "
          f"{args.min_pages} documented building(s)")
    return 0


def cmd_hubs(args) -> int:
    ctx = make_ctx(args, {"roll_year": args.roll_year, "historic": [], "districts": []})
    area_dir = ROOT / args.city / args.area
    n, n_skipped = 0, 0
    for street_dir in sorted(area_dir.iterdir()):
        if street_dir.is_dir():
            if write_street_hub(street_dir, ctx):
                n += 1
            else:
                n_skipped += 1
    n_streets = write_neighborhood_hub(area_dir, ctx)
    print(f"rebuilt {n} street hub(s); left {n_skipped} untouched (hand-written "
          f"sections); neighborhood hub lists {n_streets} street(s)")
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

    p = sub.add_parser("seed-list",
                       help="write pages for the parcels named in a manifest file")
    p.add_argument("--manifest", required=True,
                   help="JSON array of parcel entries; see cmd_seed_list")
    p.add_argument("--retrieved", default=None,
                   help="retrieval date to record in sources (default: today)")
    p.add_argument("--refresh", action="store_true")
    p.set_defaults(fn=cmd_seed_list)

    p = sub.add_parser("render",
                       help="re-render index.html from data.json, in place")
    p.add_argument("path", nargs="+",
                   help="a page, a street, a neighborhood, or the whole city — "
                        "every address page beneath it is re-rendered")
    p.add_argument("--dry-run", action="store_true",
                   help="list the pages that would change without writing them")
    p.add_argument("--include-backlogged", action="store_true",
                   help="also render the pages scripts/render-backlog.txt "
                        "grandfathers, overwriting hand-written HTML the "
                        "renderer cannot reproduce (issue #147's sweep)")
    p.set_defaults(fn=cmd_render)

    p = sub.add_parser("names", help="list permit descriptions that may name a person or firm")
    common(p)
    p.add_argument("--refresh", action="store_true")
    p.set_defaults(fn=cmd_names)

    p = sub.add_parser("hubs", help="rebuild street hub pages from the pages beneath them")
    common(p, neighborhood_required=False)
    p.add_argument("--roll-year", type=int, default=2025)
    p.set_defaults(fn=cmd_hubs)

    p = sub.add_parser("districts",
                       help="rebuild the historic-district hub pages from the "
                            "address pages that name a district")
    p.add_argument("--city", default="san-francisco")
    p.add_argument("--min-pages", type=int, default=DISTRICT_MIN_PAGES,
                   help="a district with fewer documented buildings gets no page")
    p.set_defaults(fn=cmd_districts)

    args = ap.parse_args()
    return args.fn(args)


if __name__ == "__main__":
    sys.exit(main())
