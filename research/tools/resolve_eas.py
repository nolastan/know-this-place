#!/usr/bin/env python3
"""Resolve a findings file's addresses against EAS, the parcel map and the roll.

    python3 research/tools/resolve_eas.py fetch  research/findings/<id>/<batch>.json
    python3 research/tools/resolve_eas.py report research/findings/<id>/<batch>.json
    python3 research/tools/resolve_eas.py apply  research/findings/<id>/<batch>.json

Stdlib only. `fetch` fills a resumable cache under `.cache/resolve-eas/` (three
DataSF datasets, see DATA-SOURCES.md); `report` prints what each finding would
become and why; `apply` writes the decisions into the findings file.

This is the mechanical half of RUNBOOK.md step 3, "Place it" — the
EAS join, the parcel confirmation, the lowest-number rule for a parcel that
spans several street numbers, and the conflict comparison. **It never adjudicates
a conflict**: where a finding's two recorded addresses land on different parcels
it declines and says so, and where a decision needs a human's judgement the
entry is left for one, in the words of its `resolution.note`. Read every
`conflict` entry it emits before committing.

What it will not do:

  * resolve an address with no EAS record (that is the evidence bar in
    research/AGENTS.md, and the miss is the finding);
  * pick one of several parcels a recorded address range spans today — unless
    the record names its own assessor block *and* lot, in which case it takes
    the parcel the record itself states and says so in the method;
  * touch `date`, `description`, `extra` or anything else the extractor wrote.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import time
import urllib.parse
import urllib.request
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
CACHE = REPO / ".cache" / "resolve-eas"
UA = {"User-Agent": "know-this-place-research/1.0 (+https://knowthis.place)"}

EAS = "3mea-di5p"          # sf-eas-addresses
PARCELS = "acdm-wktn"      # sf-parcels (active and retired)
ROLL = "wv5m-vpq2"         # sf-assessor-roll

EAS_SELECT = ("address_number,street_name,street_type,parcel_number,latitude,"
              "longitude,nhood,zip_code,address,eas_baseid")
PARCEL_SELECT = ("blklot,mapblklot,block_num,lot_num,from_address_num,to_address_num,"
                 "street_name,street_type,active,in_asr_secured_roll,"
                 "analysis_neighborhood,centroid_latitude,centroid_longitude")
ROLL_SELECT = ("parcel_number,closed_roll_year,property_location,year_property_built,"
               "use_definition,property_class_code_definition,number_of_units,"
               "number_of_stories,lot_area,analysis_neighborhood")

# Street types EAS abbreviates, spelled out for a directory name. Same table as
# scripts/seed_pages.py — the site's directory contract, not this module's.
STREET_TYPE_WORD = {
    "ST": "street", "AVE": "avenue", "BLVD": "boulevard", "WAY": "way", "CT": "court",
    "TER": "terrace", "PL": "place", "DR": "drive", "LN": "lane", "ALY": "alley",
    "RD": "road", "HWY": "highway", "STWY": "stairway", "WALK": "walk", "PARK": "park",
    "CIR": "circle", "PLZ": "plaza", "ROW": "row", "PATH": "path", "STPS": "steps",
}
PADDED_ORDINAL = re.compile(r"^0+(\d(ST|ND|RD|TH))$", re.I)
NUMBER = re.compile(r"^(\d+)([A-Za-z]?)$")

# Sources write "Second Street" and "Twenty-fourth Avenue"; EAS holds the
# numbered streets and avenues as zero-padded ordinals — 02ND, 24TH. Without
# this the lookup fails at the street, not the number, and the finding dies
# with "no such street" when the street is one of the busiest in the city.
_ONES = ["", "FIRST", "SECOND", "THIRD", "FOURTH", "FIFTH", "SIXTH", "SEVENTH",
         "EIGHTH", "NINTH", "TENTH", "ELEVENTH", "TWELFTH", "THIRTEENTH",
         "FOURTEENTH", "FIFTEENTH", "SIXTEENTH", "SEVENTEENTH", "EIGHTEENTH",
         "NINETEENTH"]
_TENS = {20: "TWENTY", 30: "THIRTY", 40: "FORTY", 50: "FIFTY"}
_CARDINAL = {1: "ONE", 2: "TWO", 3: "THREE", 4: "FOUR", 5: "FIVE", 6: "SIX",
             7: "SEVEN", 8: "EIGHT", 9: "NINE"}


def _ordinal_suffix(n: int) -> str:
    if 10 <= n % 100 <= 20:
        return "TH"
    return {1: "ST", 2: "ND", 3: "RD"}.get(n % 10, "TH")


def _ordinal_words() -> dict:
    """Squashed spelled-out ordinal -> EAS's padded form ("SECOND" -> "02ND")."""
    out = {}
    for n in range(1, 60):
        if n < 20:
            word = _ONES[n]
        else:
            tens, unit = (n // 10) * 10, n % 10
            if unit == 0:
                word = _TENS[tens][:-1] + "IETH" if _TENS[tens].endswith("Y") else _TENS[tens] + "TH"
            else:
                word = _TENS[tens] + _ONES[unit]
        eas = f"{n:02d}{_ordinal_suffix(n)}"
        out[word] = eas
        if n >= 20 and n % 10:
            out[_TENS[(n // 10) * 10] + _CARDINAL[n % 10]] = eas  # "TWENTYFOUR" typos
    return out


ORDINAL_WORDS = _ordinal_words()


# --------------------------------------------------------------------------- #
# Fetching
# --------------------------------------------------------------------------- #

def api_get(dataset: str, params: dict, timeout: int = 120, budget: int = 300,
            tries: int = 6) -> list:
    """One query against a total time budget — see DATA-SOURCES.md's caution.

    urllib's timeout is per-read, so a response that trickles never fires it and
    the process hangs. Read in chunks against a wall clock instead.
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
                        raise TimeoutError(f"response still arriving after {budget}s")
                    chunk = r.read(65536)
                    if not chunk:
                        break
                    buf.extend(chunk)
            return json.loads(bytes(buf))
        except Exception as exc:  # noqa: BLE001 — any transport error is retryable
            if attempt == tries - 1:
                raise
            wait = (10, 30, 60, 120, 180)[min(attempt, 4)]
            print(f"    retry {attempt + 1}/{tries - 1} in {wait}s: {exc}",
                  file=sys.stderr, flush=True)
            time.sleep(wait)
    return []


def _quoted(keys) -> str:
    return ",".join("'" + str(k).replace("'", "''") + "'" for k in keys)


def fetch_keyed(name: str, dataset: str, field: str, keys, select: str,
                where: str = None, chunk: int = 100, refresh: bool = False) -> list:
    """Rows for a list of key values, a chunk at a time, resumable.

    The cache keeps the keys it has already fetched, so a later run that adds a
    few keys — a street this batch spells differently, say — fetches only those.
    """
    CACHE.mkdir(parents=True, exist_ok=True)
    path = CACHE / f"{name}.json"
    rows, done = [], set()
    if path.exists() and not refresh:
        state = json.loads(path.read_text())
        if isinstance(state, list):      # cache written before keys were recorded
            rows, done = state, {r.get(field) for r in state if r.get(field)}
        elif state.get("where") == where and state.get("select") == select:
            rows, done = state["rows"], set(state["done"])
    todo = [k for k in keys if k not in done]
    if not todo:
        return rows
    batches = [todo[i:i + chunk] for i in range(0, len(todo), chunk)]
    for i, batch in enumerate(batches, 1):
        clause = f"{field} in ({_quoted(batch)})"
        offset = 0
        while True:
            got = api_get(dataset, {"$select": select, "$order": ":id", "$limit": 5000,
                                    "$offset": offset,
                                    "$where": f"{where} AND {clause}" if where else clause})
            rows.extend(got)
            if len(got) < 5000:
                break
            offset += 5000
        done.update(batch)
        path.write_text(json.dumps({"rows": rows, "done": sorted(done),
                                    "where": where, "select": select}))
        print(f"  {name}: batch {i}/{len(batches)} — {len(rows)} rows",
              file=sys.stderr, flush=True)
        time.sleep(2)  # be a polite client
    return rows


def point_key(lat, lng) -> str:
    """An EAS point, at the precision EAS states it.

    Not rounded: an address point often sits within centimetres of its parcel's
    boundary, and trimming to six decimals moves enough of them across it to
    lose the parcel entirely.
    """
    if lat in (None, "") or lng in (None, ""):
        return ""
    try:
        float(lat), float(lng)
    except (TypeError, ValueError):
        return ""
    return f"{lat},{lng}"


def fetch_points(points: list, refresh: bool = False) -> dict:
    """The active parcel each point falls in — one spatial query per point.

    Used only where the EAS join has failed or gone stale, which is a few dozen
    addresses in a batch of a thousand, so a query apiece is affordable. Doing it
    for every address would not be.
    """
    path = CACHE / "points.json"
    known = {} if refresh or not path.exists() else json.loads(path.read_text())
    todo = [p for p in points if p and p not in known]
    for i, key in enumerate(todo, 1):
        lat, lng = key.split(",")
        known[key] = api_get(PARCELS, {
            "$select": "blklot,mapblklot,block_num,lot_num,active,street_name,street_type,"
                       "from_address_num,to_address_num,centroid_latitude,centroid_longitude",
            "$where": f"active=true AND intersects(shape, 'POINT({lng} {lat})')", "$limit": 20})
        if i % 10 == 0 or i == len(todo):
            path.write_text(json.dumps(known))
            print(f"  points: {i}/{len(todo)}", file=sys.stderr, flush=True)
        time.sleep(1)
    path.write_text(json.dumps(known))
    return known


def street_names(refresh: bool = False) -> list:
    """Every street name EAS holds, with its type. Small, and worth having.

    A source spells streets its own way — "Bayshore Boulevard", "O'Farrell",
    "Sea Cliff Avenue" — where EAS holds BAY SHORE, OFARRELL and SEACLIFF. Left
    unmapped those read as addresses that no longer exist, which is the wrong
    answer for the wrong reason: the street is there, the spelling isn't.
    """
    path = CACHE / "street-names.json"
    if path.exists() and not refresh:
        return json.loads(path.read_text())
    CACHE.mkdir(parents=True, exist_ok=True)
    rows = api_get(EAS, {"$select": "street_name,street_type,count(1) as n",
                         "$group": "street_name,street_type", "$limit": 50000})
    path.write_text(json.dumps(rows))
    return rows


DIGIT_ORDINAL = re.compile(r"^(\d+)(st|nd|rd|th)$", re.I)


def squash(name: str) -> str:
    return re.sub(r"[^A-Z0-9]+", "", (name or "").upper())


class StreetIndex:
    """The source's street spellings mapped onto EAS's."""

    def __init__(self, rows: list, extra_aliases: dict = None):
        self.types: dict = defaultdict(set)      # EAS name -> types
        self.squashed: dict = {}                 # squashed EAS name -> EAS name
        for r in rows:
            name = r.get("street_name") or ""
            self.types[name].add(r.get("street_type") or "")
            self.squashed.setdefault(squash(name), name)
        self.aliases = dict(extra_aliases or {})

    def eas_name(self, name: str) -> tuple:
        """(EAS street name or None, how it was matched)."""
        if not name:
            return None, ""
        if name in self.types:
            return name, "exact"
        if name in self.aliases:
            target = self.aliases[name]
            return (target, "alias") if target in self.types else (None, "")
        key = squash(name)
        for candidate in (key, "THE" + key):
            hit = self.squashed.get(candidate)
            if hit:
                return hit, "spelling"
        padded = ORDINAL_WORDS.get(key)
        if padded and padded in self.types:
            return padded, "ordinal"
        # "2ND STREET" is the ordinary way a report writes it and the one EAS
        # will not answer to: the city holds the numbered streets zero-padded to
        # four characters. Spelling it out ("SECOND") is handled above; this is
        # the same trap wearing digits, and it fails at the street rather than
        # the number, so it reads as a missing street rather than a bad address.
        digits = DIGIT_ORDINAL.match(key)
        if digits and len(digits.group(1)) == 1:
            padded = (digits.group(1) + digits.group(2)).upper().rjust(4, "0")
            if padded in self.types:
                return padded, "digit-ordinal"
        return None, ""

    def eas_type(self, name: str, stype: str | None) -> tuple:
        """(street type EAS uses, whether the record's type was overridden)."""
        types = self.types.get(name) or set()
        if stype and stype in types:
            return stype, False
        if len(types) == 1:                      # THE EMBARCADERO has no type at all
            only = next(iter(types))
            return only, bool(stype) and only != stype
        return stype, False


# --------------------------------------------------------------------------- #
# Naming — the site's directory contract
# --------------------------------------------------------------------------- #

def unpad(token: str) -> str:
    m = PADDED_ORDINAL.match(token or "")
    return m.group(1) if m else token


def street_slug(name: str, stype: str) -> str | None:
    word = "" if not (stype or "").strip() else STREET_TYPE_WORD.get((stype or "").upper())
    if word is None:
        return None
    name = " ".join(unpad(t) for t in (name or "").split())
    base = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    if not base:
        return None
    return f"{base}-{word}" if word else base


def area_slug(nhood: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", (nhood or "").lower()).strip("-")


def num_key(n: str):
    m = NUMBER.match(n or "")
    return (int(m.group(1)), m.group(2)) if m else (10 ** 9, n or "")


# --------------------------------------------------------------------------- #
# The address index
# --------------------------------------------------------------------------- #

def between_on_street(city: "City", name: str, stype: str, num: int,
                      apn: str, stated: tuple = ()) -> list:
    """[(number, parcel)] another parcel holds between `num` and `apn`'s own numbers.

    The block's number line is the only evidence that tells a boundary slip from
    a genuine misplacement, and EAS carries it: every number on the street with
    the parcel it belongs to. Same parity only — the two sides of a street
    interleave in the sort and not on the ground.
    """
    held = sorted(num_key(r["address_number"])[0]
                  for r in city.by_parcel.get(apn, [])
                  if (r.get("street_name") or "") == name
                  and (r.get("street_type") or "") == stype
                  and re.fullmatch(r"\d+", r.get("address_number") or ""))
    if not held:
        # A parcel EAS joins no number to is known only by its range field, and
        # that field is then the only edge there is. 1458 Kirkwood — the case
        # this check was raised for — is exactly this shape.
        held = sorted(x for x in stated if x is not None)
    if not held:
        return []
    edge = held[0] if num < held[0] else held[-1]
    span = (num, edge) if num < edge else (edge, num)
    out, nearby = [], 0
    for r in city.eas:
        if (r.get("street_name") or "") != name or (r.get("street_type") or "") != stype:
            continue
        if not r.get("parcel_number") or r["parcel_number"] == apn:
            continue
        if not re.fullmatch(r"\d+", r.get("address_number") or ""):
            continue
        n = int(r["address_number"])
        if n % 2 != num % 2:
            continue
        if abs(n - num) <= 40:
            nearby += 1
        if span[0] < n < span[1]:
            out.append((n, r["parcel_number"]))
    # Whole stretches of the city carry no parcel join in EAS at all — the
    # Kirkwood Avenue case this check was raised for is one — and there the
    # number line is blind rather than clear. Saying which is which is the
    # difference between "confirmed" and "still unchecked".
    return sorted(set(out)), nearby


class City:
    """EAS, parcels and roll, indexed for the joins a resolver makes."""

    def __init__(self, eas: list, pages: list, streets: "StreetIndex" = None,
                 area_from_nhood: bool = False):
        self.eas = eas
        self.streets = streets or StreetIndex([])
        # When the site has not settled a street, the nearest published page is
        # the wrong authority for the directory — see area_for.
        self.area_from_nhood = area_from_nhood
        # The directories the site actually uses. An analysis neighborhood does
        # not always slug to one of them: the site splits "Financial District/
        # South Beach" into two and joins "Oceanview/Merced Heights/Ingleside"
        # into one, and no dataset records either choice.
        self.areas = {p["area"] for p in pages if p.get("area")}
        self.parcels: dict = {}
        self.roll: dict = {}
        self.spatial: dict = {}
        self.by_effective: dict = defaultdict(list)
        self.by_addr: dict = defaultdict(list)     # (NAME, TYPE, NUM) -> rows
        self.by_name_num: dict = defaultdict(list)  # (NAME, NUM) -> rows
        self.on_street: dict = defaultdict(list)   # (NAME, TYPE) -> numbers
        self.by_parcel: dict = defaultdict(list)   # parcel -> rows
        for r in eas:
            num = (r.get("address_number") or "").upper()
            name, stype = r.get("street_name") or "", r.get("street_type") or ""
            self.by_addr[(name, stype, num)].append(r)
            self.by_name_num[(name, num)].append(r)
            self.on_street[(name, stype)].append(num)
            if r.get("parcel_number"):
                self.by_parcel[r["parcel_number"]].append(r)
        self.pages = {p["apn"]: p for p in pages if p.get("apn")}
        self.page_area: dict = defaultdict(Counter)   # (nhood, street_slug) -> areas
        self.nhood_area: dict = defaultdict(Counter)  # nhood -> areas
        self.by_street: dict = defaultdict(list)      # street_slug -> located pages
        self.located: list = []                       # pages with coordinates
        for p in pages:
            if p.get("nhood"):
                self.page_area[(p["nhood"], p["street_dir"])][p["area"]] += 1
                self.nhood_area[p["nhood"]][p["area"]] += 1
            if p.get("lat") and p.get("lng"):
                self.by_street[p["street_dir"]].append(p)
                self.located.append(p)

    def attach_spatial(self, points: dict, rows: list = None) -> None:
        """Active parcels found by point, for addresses whose EAS APN is retired.

        `rows` are the address rows that needed one. Indexing their *effective*
        parcels matters for the lowest-number rule: two numbers on one building
        can reach the same parcel by different routes — one through a retired
        APN, one through no APN at all — and unless both are counted the parcel
        looks like two, and the batch proposes two pages for one building.
        """
        self.spatial = points
        for row in rows or []:
            apn, _, _ = self.active_parcel(row)
            if apn:
                self.by_effective[apn].append(row)

    def active_parcel(self, row: dict) -> tuple:
        """(APN to record, EAS parcel key, clause) for one EAS address row.

        EAS's `parcel_number` is the APN as of whenever the address record was
        written, and DATA-SOURCES.md → sf-parcels says plainly that downtown it
        is often a retired one. Where sf-parcels does not have it active, the
        parcel that exists now is the one the address's own coordinates fall in.
        """
        apn = row.get("parcel_number")
        parcel = self.parcels.get(apn) if apn else None
        if parcel and str(parcel.get("active")).lower() in ("true", "1"):
            return apn, apn, ""
        key = point_key(row.get("latitude"), row.get("longitude"))
        found = (self.spatial or {}).get(key) or []
        if len(found) > 1:
            # Several active parcels share the point — a condominium split, or
            # two lots that meet there. The one whose own address range holds
            # this number on this street is the building; anything else is a
            # coin toss, and a coin toss is not a resolution.
            number = num_key(row.get("address_number") or "")
            same = [p for p in found
                    if (p.get("street_name") or "") == (row.get("street_name") or "")
                    and p.get("from_address_num") and p.get("to_address_num")
                    and num_key(p["from_address_num"]) <= number <= num_key(p["to_address_num"])]
            if len(same) == 1:
                found = same
            else:
                # Dozens of active parcels on one point is the condominium
                # signal in DATA-SOURCES.md → sf-parcels. Units, not buildings.
                shown = ", ".join(p["blklot"] for p in found[:4])
                return None, None, (
                    f" {row.get('address') or 'The address'}'s coordinates fall in "
                    f"{len(found)} active parcels "
                    f"({shown}{'…' if len(found) > 4 else ''}), which is what a condominium "
                    f"looks like in sf-parcels: one parcel per unit, none of them the building.")
        if len(found) == 1:
            new = found[0]["blklot"]
            if apn and new != apn:
                return new, apn, (f" EAS files the address under parcel {apn}, which sf-parcels "
                                  f"reports {'retired' if parcel else 'unmapped'}; the active "
                                  f"parcel its coordinates fall in is {new}.")
            return new, new, (" The address carries no parcel number in EAS; the active parcel "
                              f"its coordinates fall in is {new}." if not apn else "")
        if apn:
            return apn, apn, ""
        return None, None, ""

    def attach(self, parcels: list, roll: list) -> None:
        """Add the parcel map and the roll, fetched only for the APNs in play."""
        self.parcels = {p["blklot"]: p for p in parcels if p.get("blklot")}
        for r in roll:
            key = r.get("parcel_number")
            prev = self.roll.get(key)
            if not prev or (r.get("closed_roll_year") or "") > (prev.get("closed_roll_year") or ""):
                self.roll[key] = r

    # -- lookups ---------------------------------------------------------- #

    def normalize(self, name: str, stype: str | None) -> tuple:
        """(EAS name, EAS type, a clause for the method) for a recorded street."""
        eas_name, how = self.streets.eas_name(name)
        if not eas_name:
            return None, stype, ""
        eas_type, retyped = self.streets.eas_type(eas_name, stype)
        clause = ""
        if how == "spelling" or (how == "alias" and eas_name != name):
            clause = f" The record spells the street {name}; EAS holds it as {eas_name}."
        if how == "ordinal":
            clause = (f" The record spells the street out as {name}; EAS holds the numbered "
                      f"streets as zero-padded ordinals, so this is {eas_name}.")
        if how == "digit-ordinal":
            clause = (f" The record writes the street {name}; EAS holds the numbered streets "
                      f"zero-padded to four characters, so this is {eas_name}.")
        if retyped:
            clause += (f" EAS files this street as {eas_name} "
                       f"{eas_type or 'with no street type'}, not {stype}.")
        return eas_name, eas_type, clause

    def rows_for(self, name: str, stype: str | None, number: str) -> list:
        number = (number or "").upper()
        if stype:
            return self.by_addr[(name, stype, number)]
        return self.by_name_num[(name, number)]

    def parcel_numbers(self, parcel: str, name: str, stype: str, key: str = None) -> list:
        """Every street number that lands on this parcel, on this street."""
        rows = list(self.by_parcel.get(key or parcel, [])) + list(self.by_effective.get(parcel, []))
        nums = {(r.get("address_number") or "").upper()
                for r in rows
                if (r.get("street_name") or "") == name
                and (not stype or (r.get("street_type") or "") == stype)}
        return sorted(nums, key=num_key)

    def neighbours(self, name: str, stype: str, number: str, span: int = 20) -> list:
        """Surviving EAS numbers either side — where a lost address's fact can live."""
        m = NUMBER.match((number or "").upper())
        if not m:
            return []
        target = int(m.group(1))
        pool = (set(self.on_street.get((name, stype), [])) if stype else
                {n for (nm, _), nums in self.on_street.items() if nm == name for n in nums})
        near = []
        for n in pool:
            mm = NUMBER.match(n)
            if mm and abs(int(mm.group(1)) - target) <= span:
                near.append(n)
        return sorted(near, key=num_key)

    def area_for(self, slug: str, nhood: str, lat: float = None, lng: float = None) -> str | None:
        """Which neighborhood directory the site files this address under.

        The site's directories are not the assessor's analysis neighborhoods —
        it splits Castro/Upper Market into `castro` and `corbett-heights`, and
        files part of Financial District/South Beach as `east-cut`. The pages
        already published are the only record of where the line falls, so ask
        them: the nearest page on the same street, then the nearest page at all,
        then the neighborhood's usual directory.
        """
        if self.area_from_nhood:
            # Asked for explicitly, because the site has not settled these
            # streets: the analysis neighborhood the assessor and EAS give the
            # parcel decides, and the nearest published page does not get a say.
            return area_slug(nhood) if nhood else None
        if lat is not None and lng is not None:
            for pool, radius in ((self.by_street.get(slug, []), 1.2), (self.located, 0.6)):
                best, dist = None, radius
                for p in pool:
                    d = (((p["lat"] - lat) * 111.0) ** 2 + ((p["lng"] - lng) * 88.0) ** 2) ** 0.5
                    if d < dist:
                        best, dist = p["area"], d
                if best:
                    return best
        if nhood:
            if self.page_area.get((nhood, slug)):
                return self.page_area[(nhood, slug)].most_common(1)[0][0]
            # A neighborhood the site has really settled says where its addresses
            # go; a handful of pages does not — 29 West of Twin Peaks pages are
            # all in Ingleside Terraces and Glen Park, and Taraval Street is in
            # neither. Below that, name the analysis neighborhood and let the
            # publisher place it.
            counted = self.nhood_area.get(nhood)
            if counted and sum(counted.values()) >= 100:
                return counted.most_common(1)[0][0]
            return area_slug(nhood)
        return None

    def path_for(self, parcel: str, name: str, stype: str, number: str) -> tuple:
        """(path, note) — an existing page's path, or the one that would exist."""
        page = self.pages.get(parcel)
        if page:
            return page["path"], "existing page"
        slug = street_slug(name, stype)
        if not slug:
            return None, f"no directory name for street type {stype!r}"
        rows = self.by_parcel.get(parcel) or self.rows_for(name, stype, number)
        nhood = next((r.get("nhood") for r in rows if r.get("nhood")), None)
        lat = next((float(r["latitude"]) for r in rows if r.get("latitude")), None)
        lng = next((float(r["longitude"]) for r in rows if r.get("longitude")), None)
        if not nhood:
            nhood = (self.roll.get(parcel) or {}).get("analysis_neighborhood")
        area = self.area_for(slug, nhood, lat, lng)
        if not area:
            return None, "no analysis neighborhood for the parcel"
        why = "no page yet"
        if self.area_from_nhood:
            why = ("no page yet, area from nhood, new directory"
                   if area not in self.areas else "no page yet, area from nhood")
        return f"/san-francisco/{area}/{slug}/{number.lower()}/", why


# --------------------------------------------------------------------------- #
# Deciding one finding
# --------------------------------------------------------------------------- #

def assessor_location(city: City, parcel: str, name: str) -> str:
    """The assessor's own `property_location`, when it names another street.

    A corner parcel's frontage street is arbitrary — DATA-SOURCES.md → sf-parcels
    — so 120 Perry Street and 735–755 Harrison Street can be one parcel. Saying
    which is which is the difference between a check and a surprise.
    """
    raw = (city.roll.get(parcel) or {}).get("property_location") or ""
    if len(raw) < 11:
        return ""
    # Fixed width: two five-character street-number fields, then the street,
    # then four trailing digits. Same layout scripts/seed_pages.py reads.
    numbers = []
    for i in (0, 5):
        m = re.fullmatch(r"(\d{4})([A-Z ])", raw[i:i + 5])
        if m and int(m.group(1)):
            numbers.append(f"{int(m.group(1))}{m.group(2).strip()}")
    street = " ".join(re.sub(r"0{4}$", "", raw[10:]).split())
    if not street or squash(name) in squash(street):
        return ""
    numbers = sorted(set(numbers), key=num_key)
    stated = ("–".join((numbers[0], numbers[-1])) if len(numbers) > 1
              else (numbers[0] if numbers else ""))
    return f" The assessor files the parcel as {stated} {street}.".replace("  ", " ")


def parcel_note(city: City, parcel: str) -> str:
    """One clause on what the parcel map and the roll say about this parcel."""
    p = city.parcels.get(parcel)
    roll = city.roll.get(parcel)
    bits = []
    if p:
        state = "active" if str(p.get("active")).lower() in ("true", "1") else "retired"
        rng = ""
        if p.get("from_address_num") and p.get("to_address_num"):
            rng = f", {p['from_address_num']}–{p['to_address_num']} {p.get('street_name','')}".rstrip()
        bits.append(f"sf-parcels has blklot {parcel} {state}{rng}")
    else:
        bits.append(f"sf-parcels has no row for blklot {parcel}")
    if roll:
        built = roll.get("year_property_built")
        use = roll.get("use_definition")
        bits.append(f"the {roll.get('closed_roll_year')} roll records it as "
                    f"{(use or 'an unclassified property').lower()}"
                    + (f", built {built}" if built and built != "0" else ""))
    else:
        bits.append("no row on the secured roll")
    return "; ".join(bits)


def condo_warning(city: City, parcel: str, name: str = "", stype: str = "",
                  matched: list = None) -> str | None:
    """A condominium APN is a unit, not a building — the directory contract's trap.

    The trap is a *stack*: many unit APNs on one point, so a page per APN would be
    a page per unit. The roll's class code alone does not prove one, because it
    also lands on old single-address parcels that were condominium-mapped at some
    point and never split. Where EAS holds the recorded numbers on exactly this
    one parcel, there is no stack to defer and the parcel is the building.
    """
    roll = city.roll.get(parcel) or {}
    if "condominium" not in (roll.get("property_class_code_definition") or "").lower():
        return None
    if name and matched:
        siblings = set()
        for n in matched:
            for r in city.rows_for(name, stype, n):
                apn, key, _ = city.active_parcel(r)
                if apn:
                    siblings.add(apn)
        if siblings and siblings <= {parcel}:
            return None
    area = (roll.get("lot_area") or "").strip()
    return ("the 2025 roll classes this parcel as a Condominium"
            + (" with zero lot area" if area in ("0", "0.0") else "")
            + ", which is a unit and not a building — the root AGENTS.md "
              "directory contract defers these until the building's own parcels "
              "are established")


def resolve_numbers(city: City, name: str, stype: str | None,
                    numbers: list) -> dict:
    """Join a set of recorded street numbers to parcels. Pure lookup, no judgement."""
    hits, misses, types, unparcelled, notes = {}, [], set(), [], []
    keys: dict = {}
    stated: dict = {}          # parcels an EAS row names itself, not ones found by point
    for n in numbers:
        rows = city.rows_for(name, stype, n)
        if not rows:
            misses.append(n)
            continue
        placed = False
        for r in rows:
            types.add(r.get("street_type") or "")
            apn, key, clause = city.active_parcel(r)
            if clause and clause not in notes:
                notes.append(clause)
            if apn:
                hits.setdefault(apn, []).append(n)
                keys.setdefault(apn, key)
                if r.get("parcel_number"):
                    stated.setdefault(apn, []).append(n)
                placed = True
        if not placed:
            unparcelled.append(n)
    return {"parcels": hits, "misses": misses, "types": types,
            "unparcelled": unparcelled, "keys": keys, "notes": notes, "stated": stated}


def complete_high(low: str, high: str) -> str:
    """The high end of a printed range, spelled out from the low end.

    Surveys print "1843-47" and "1761-65" for 1843-1847 and 1761-1765 — the high
    end carries only the digits that changed. Taken literally the pair reads as
    47-1843, which is the whole street: the Japantown statement's "1843-47
    Fillmore Street" came back spanning eighty parcels. Where the high end is
    shorter than the low, fill it in from the low end's leading digits and use it
    only if it really is higher.
    """
    if len(high) >= len(low):
        return high
    filled = low[:len(low) - len(high)] + high
    return filled if int(filled) >= int(low) else high


RANGE = re.compile(r"(\d+)\s*([A-Za-z]?)\s*[-\u2013]\s*(\d+)\s*([A-Za-z]?)"
                   r"(?:\s+[A-Za-z0-9'. ]+)?")


def parse_range(recorded: str) -> tuple | None:
    """The two street numbers a recorded range states, or None.

    A range is a pair of street numbers. Surveys print them with spaces around
    the dash ("541 -543") and often repeat the street after them ("541-543 8TH
    ST"); both say the same thing, and rejecting either loses every ranged
    building in a batch. One reader, so `fetch` and `decide` cannot disagree
    about what a range is — when they did, the parcels of every ranged building
    went unfetched and the findings came back "not an active parcel".
    """
    m = RANGE.fullmatch((recorded or "").strip())
    return (m.group(1), m.group(3)) if m else None


def expand_range(low: str, high: str) -> list:
    """Every number a recorded range covers, low end first, parity kept.

    A street-number range on one building runs up one side of the street, so the
    numbers between the ends share the ends' parity when the ends do.
    """
    a, b = int(low), int(complete_high(low, high))
    if a > b:
        a, b = b, a
    step = 2 if a % 2 == b % 2 else 1
    return [str(n) for n in range(a, b + 1, step)]


# --------------------------------------------------------------------------- #
# Reading the archivist's second address
# --------------------------------------------------------------------------- #

WORD_TYPE = {word: abbr for abbr, word in STREET_TYPE_WORD.items()}
ORDINAL_WORD = {
    "first": "01ST", "second": "02ND", "third": "03RD", "fourth": "04TH",
    "fifth": "05TH", "sixth": "06TH", "seventh": "07TH", "eighth": "08TH",
    "ninth": "09TH", "tenth": "10TH", "eleventh": "11TH", "twelfth": "12TH",
    "thirteenth": "13TH", "fourteenth": "14TH", "fifteenth": "15TH",
    "sixteenth": "16TH", "seventeenth": "17TH", "eighteenth": "18TH",
    "nineteenth": "19TH", "twentieth": "20TH",
}
# The archivist writes cross-street numbers out in full — "Nineteenth Street",
# "Twenty-Second Street" — where EAS holds 19TH and 22ND.
for _tens, _prefix in ((20, "twenty"), (30, "thirty"), (40, "forty")):
    for _unit, _word in enumerate(("first", "second", "third", "fourth", "fifth",
                                   "sixth", "seventh", "eighth", "ninth"), start=1):
        _n = _tens + _unit
        ORDINAL_WORD[f"{_prefix}-{_word}"] = f"{_n}{ORDINAL_WORD[_word][-2:]}"
        ORDINAL_WORD[f"{_prefix}{_word}"] = f"{_n}{ORDINAL_WORD[_word][-2:]}"
def parse_address(text: str) -> dict | None:
    """A recorded address string → numbers, EAS street name, EAS street type.

    Handles the shapes the archivist's `500$a` note uses — "1724 Byrant",
    "3608-3612 Nineteenth Street", "110-114 Embarcadero". Returns None when the
    string is not a numbered address ("500 Bayshore, S. or"), which is itself a
    result: an unparsable second address is not evidence of anything.
    """
    if not text:
        return None
    t = text.strip().rstrip(".").replace(",", " ")
    m = re.match(r"^(\d+)([A-Za-z]?)\s*-\s*(\d+)([A-Za-z]?)\s+(.*)$", t)
    if m:
        numbers, rest = [m.group(1), m.group(3)], m.group(5)
    else:
        m = re.match(r"^(\d+)([A-Za-z]?)\s+(.*)$", t)
        if not m:
            return None
        numbers, rest = [m.group(1) + m.group(2)], m.group(3)
    tokens = [tok for tok in rest.split() if tok]
    if not tokens:
        return None
    if tokens[0].lower() == "the":       # "The Embarcadero"
        tokens = tokens[1:]
    stype = None
    if tokens and tokens[-1].lower() in WORD_TYPE:
        stype = WORD_TYPE[tokens.pop().lower()]
    elif tokens and tokens[-1].upper() in STREET_TYPE_WORD:
        stype = tokens.pop().upper()
    if not tokens:
        return None
    name = []
    for tok in tokens:
        low = tok.lower()
        if low in ORDINAL_WORD:
            name.append(ORDINAL_WORD[low])
        elif DIGIT_ORDINAL.match(tok):
            d = DIGIT_ORDINAL.match(tok)
            name.append((d.group(1) + d.group(2)).upper().rjust(4, "0")
                        if len(d.group(1)) == 1 else (d.group(1) + d.group(2)).upper())
        else:
            name.append(tok.upper())
    return {"numbers": numbers, "street_name": " ".join(name), "street_type": stype,
            "as_written": text}


# --------------------------------------------------------------------------- #
# Deciding one finding
# --------------------------------------------------------------------------- #

def eas_label(name: str, stype: str | None, number: str) -> str:
    return " ".join(x for x in (number, name, stype) if x)


def place(city: City, parcel: str, name: str, stype: str, matched: list,
          method_head: str, today: str, numbers_key: str = None) -> dict:
    """Turn a parcel the address landed on into a resolution, or decline."""
    method = f"{method_head} → parcel {parcel}; {parcel_note(city, parcel)}."
    live = city.parcels.get(parcel)
    if not live or str(live.get("active")).lower() not in ("true", "1"):
        return {"status": "unresolved", "checked_on": today, "method": method,
                "note": ("The parcel EAS gives for this address is not an active parcel in "
                         "sf-parcels and no active parcel contains the address's coordinates, "
                         "so there is no parcel today to hang the fact on. The block has been "
                         "re-parcelized since; a later pass with the assessor's own "
                         "property_location could still place it.")}
    condo = condo_warning(city, parcel, name, stype, matched)
    if condo:
        return {"status": "unresolved", "checked_on": today, "method": method,
                "note": f"Not placed: {condo}."}
    numbers_key = numbers_key or parcel
    stype = stype or next((r.get("street_type") for r in
                           city.by_parcel.get(numbers_key, []) + city.by_effective.get(parcel, [])
                           if (r.get("street_name") or "") == name), "")
    numbers = sorted(set(city.parcel_numbers(parcel, name, stype, numbers_key)) | set(matched),
                     key=num_key)
    lead = numbers[0] if numbers else (matched[0] if matched else "")
    path, why = city.path_for(parcel, name, stype, lead)
    method += assessor_location(city, parcel, name)
    if len(numbers) > 1:
        method += (f" EAS puts {', '.join(numbers)} {name} {stype} on that parcel, so per the "
                   f"directory contract the fact belongs on one page at the lowest, {lead}.")
    if not path:
        return {"status": "unresolved", "checked_on": today, "method": method,
                "note": f"Parcel identified but no page path could be formed: {why}."}
    if why.startswith("no page yet, area from nhood"):
        method += (" The neighborhood directory is the analysis neighborhood the assessor and "
                   "EAS give the parcel, not the area of the nearest published page: the site "
                   "has too few pages on these streets for proximity to say where the line falls.")
        if why.endswith("new directory"):
            method += (" No page on the site is filed under that directory yet, so the analysis "
                       "neighborhood's own name is used and the publisher should confirm it "
                       "against the directory contract before seeding.")
    res = {"status": "resolved", "apn": parcel, "path": path,
           "eas_address": eas_label(name, stype, lead), "method": method,
           "checked_on": today}
    if why.startswith("no page yet"):
        res["note"] = "No page at this path yet; the parcel is the publisher's to seed."
    return res


def recorded_parcels(f: dict) -> list:
    """The APNs a record names outright, from its own assessor block and lot.

    A survey that prints "647/13, 14" has identified the parcel itself; that is
    stronger evidence than a street number, and it is the one thing that can
    choose between the parcels a recorded range spans today without the tool
    doing any adjudicating of its own. Returns [] when the record names no lot.
    """
    extra = f.get("extra") or {}
    block, lots = extra.get("assessor_block_as_recorded"), extra.get("assessor_lot_as_recorded")
    if not block or not lots:
        return []
    m = re.fullmatch(r"(\d{1,4})([A-Z]?)", str(block).strip().upper())
    if not m:
        return []
    blk = m.group(1).zfill(4) + m.group(2)
    out = []
    for lot in re.split(r"[,\s]+", str(lots).strip().upper()):
        m = re.fullmatch(r"(\d{1,3})([A-Z]?)", lot)
        if m:
            out.append(blk + m.group(1).zfill(3) + m.group(2))
    return out


def recorded_parcel_check(f: dict, parcel: str) -> str:
    """How the parcel a record printed compares with the one it resolved to.

    A source that states its own assessor block and lot has handed over a test,
    not just a tiebreak: run it on every resolved finding and the OCR of a
    scanned survey stops being taken on trust. Three outcomes matter and they
    mean different things, which is why they are counted separately —

    * ``match``  — the record's block and lot are the parcel's. Nothing to do.
    * ``relot``  — same block, different lot: the assessor has re-lotted since
      the record was written, which is ordinary and expected.
    * ``block``  — a different block. Usually a digit the scan lost (a 3/5
      confusion put 849-853 Valencia Street on "5996" for 3596), sometimes a
      real error in the record. **Read every one of these.**

    Returns "" when the record names no parcel, so it can be counted apart from
    a check that ran and passed.
    """
    recorded = recorded_parcels(f)
    if not recorded or not parcel:
        return ""
    if parcel.upper() in recorded:
        return "match"
    blk = re.match(r"^(\d{3,4}[A-Z]?)", parcel.upper())
    blk = blk.group(1) if blk else ""
    return "relot" if any(r.startswith(blk) for r in recorded) else "block"


def block_check(city: City, f: dict, parcel: str) -> tuple:
    """(clause, agrees) — the archivist's assessor block against the parcel's."""
    recorded = (f.get("extra") or {}).get("assessor_block_as_recorded")
    if not recorded:
        return "", True
    block = re.sub(r"^0+", "", str(recorded).strip().upper())
    # The parcel map states the block; slicing the APN gets lettered blocks
    # (2526B) and lettered lots (021A) wrong in opposite directions.
    mapped = (city.parcels.get(parcel) or {}).get("block_num")
    if not mapped:
        m = re.match(r"^(\d{3,4}[A-Z]?)(\d{3}[A-Z]?)$", parcel or "")
        mapped = m.group(1) if m else ""
    parcel_block = re.sub(r"^0+", "", (mapped or "").upper())
    if block == parcel_block:
        return f" The record's assessor block {recorded} matches the parcel's block.", True
    if re.fullmatch(re.escape(block) + r"[A-Z]", parcel_block):
        # 1000 Sloat sits on 2526B; the archivist wrote 2526. A lettered
        # sub-block is inside the block it is lettered from, not another one.
        return (f" The record's assessor block {recorded} is the block the parcel's "
                f"lettered sub-block {parcel_block} sits in.", True)
    return (f" The record's assessor block {recorded} is not the parcel's block "
            f"({parcel_block}).", False)


# A source that marks its own building demolished outranks the resolver, which
# knows only that the number exists today — see AGENTS.md, "A demolished building
# is `rejected`, not `resolved`." The tool raises these; it does not decide them.
# Two passes over every findings file in the repo settled that. A regex over any
# field mentioning demolition would have rejected fourteen correctly published
# findings, because the demolished thing is often not this building: the *first*
# St. Francis Hotel of 1904, one academic building of a campus, "demolished
# except for vertical sign", "largely destroyed in the Great 1906 Earthquake".
# Narrowing to a bare marker in `status_as_recorded` still gets the Swedenborgian
# Church wrong — two volumes mark it demolished and it stands, landmarked, at
# 3200 Washington Street. A source can be mistaken about its own building, and
# only a person can tell. So `report` prints these loudly and the judgement stays
# where the runbook puts it.
BARE_DEMOLITION = re.compile(
    r"^\s*(?:demolished|destroyed|razed|not extant|no longer extant)"
    r"(?:\s+(?:in\s+)?\d{4})?\s*$", re.I)
DEMOLITION_MENTIONED = re.compile(
    r"\b(?:demolish|destroyed|razed|no longer stand|not extant|since gone)", re.I)


def demolished_as_recorded(f: dict) -> str | None:
    """The source's own bare marking that this building is gone, or None.

    Only `extra.status_as_recorded` counts, and only when it is the marker and
    nothing else. A sentence that merely mentions demolition is a judgement call,
    not a fact the tool may act on; `demolition_mentioned` surfaces those.
    """
    status = (f.get("extra") or {}).get("status_as_recorded")
    if isinstance(status, str) and BARE_DEMOLITION.match(status):
        return status.strip()
    return None


def demolition_mentioned(f: dict) -> tuple[str, str] | None:
    """A field recording that something here came down, for `report` to raise."""
    if demolished_as_recorded(f):
        return None
    for key, value in (f.get("extra") or {}).items():
        if key.endswith("_as_recorded") and isinstance(value, str) \
                and DEMOLITION_MENTIONED.search(value):
            return key, value
    return None


# The 1909 renumbering changed street numbers across much of the city, and a
# plain EAS join cannot see it: the number exists today, on a parcel, and the
# join reports a clean resolution for a building that may be a block away or a
# century newer. RUNBOOK.md's rule is that a pre-1909 number is not today's
# number until EAS *and a cross-street check* agree, and this tool only does the
# first. So it declines, and says what would unblock it — a cross street, a
# block face, a lot dimension — which a publisher can act on by resolving the
# entry by hand.
#
# Measured on SFP 162, where 42 findings dated before 1910 resolved on the join
# alone: 36 of them landed on a parcel whose building the assessor dates *after*
# the photograph, by as much as 122 years (760 Mission Street, 1867, on a
# parcel built in 1989). The check that caught it is not in this tool; the
# refusal is.
RENUMBERING_YEAR = 1910
YEAR_IN_DATE = re.compile(r"(1[6-9]\d\d|20\d\d)")


def renumbering_guard(f: dict, res: dict) -> dict:
    """Refuse a pre-1910 address resolved on the EAS join alone."""
    if res.get("status") != "resolved":
        return res
    m = YEAR_IN_DATE.search(f.get("date") or "")
    if not m or int(m.group(1)) >= RENUMBERING_YEAR:
        return res
    return {"status": "unresolved", "checked_on": res.get("checked_on"),
            "method": res.get("method", ""),
            "note": (f"Dated {f.get('date')}, before the 1909 renumbering, and the record "
                     f"gives no cross street, block face or lot dimension to check the "
                     f"number against. EAS holds "
                     f"{f.get('street_number')} {f.get('street_name')} today, but a "
                     f"pre-1909 number is not today's number until a cross-street check "
                     f"says so — see 'The renumbering traps' in research/RUNBOOK.md. "
                     f"Resolve it by hand if the source supplies the check material.")}


def decide(city: City, f: dict, today: str) -> dict:
    """One finding → one resolution. No adjudication: ties go unresolved."""
    extra = f.get("extra") or {}

    recorded_name, recorded_type = f.get("street_name"), f.get("street_type")
    number, recorded_range = f.get("street_number"), extra.get("address_range_as_recorded")
    note_addr = parse_address(extra.get("address_note_as_recorded"))
    name, stype, spelling = city.normalize(recorded_name, recorded_type)

    # ---- nothing to look up ------------------------------------------------ #
    if not recorded_name or (not number and not recorded_range):
        name, stype = recorded_name, recorded_type
        bits = []
        if extra.get("assessor_block_as_recorded"):
            bits.append(f"assessor block {extra['assessor_block_as_recorded']}, which places the "
                        f"record on a city block but not on a parcel")
        if name:
            bits.append(f"the street ({name} {stype or ''})".strip())
        what = f.get("address_as_written")
        return {"status": "unresolved", "checked_on": today,
                # Source-neutral: this branch runs for every corpus, and a
                # sentence about catalogue titles and archivists' notes is
                # false on a survey report, a newspaper or a book.
                "method": "The record states no street number, so there is nothing to look up "
                          "in sf-eas-addresses.",
                "note": (f"The record locates it only as \"{what}\""
                         + (f" — {'; '.join(bits)}" if bits else "")
                         + ". Kept so the record is not read again; per the evidence bar in "
                           "research/AGENTS.md it cannot become a page.")}

    if not name:
        second = ""
        if note_addr:
            n_name, n_type, _ = city.normalize(note_addr["street_name"], note_addr["street_type"])
            hit = (resolve_numbers(city, n_name, n_type, note_addr["numbers"])
                   if n_name else {"parcels": {}})
            second = (f" The archivist's second address "
                      f"(\"{extra.get('address_note_as_recorded')}\") "
                      + (f"resolves to parcel(s) {', '.join(sorted(hit['parcels']))}, but it is "
                         f"the address the record disagrees with itself about, so resolving on it "
                         f"would be adjudicating the conflict."
                         if hit["parcels"] else "has no EAS record either."))
        return {"status": "unresolved", "checked_on": today,
                "method": (f"sf-eas-addresses holds no street named {recorded_name}"
                           f"{' ' + recorded_type if recorded_type else ''}, under that spelling "
                           f"or any spelling of it, so the address cannot be looked up." + second),
                "note": "The street the record names is not a street in the city's address "
                        "registry today; the record may name a private way, a renamed street "
                        "or a spelling this pass could not match."}

    # ---- what the title says ----------------------------------------------- #
    # A record that states a range states every number in it. Where it also
    # carries the low number on its own, the range is still what was recorded —
    # looking up only the low end loses a building whose low number has since
    # been retired but whose high numbers survive.
    if number and not recorded_range:
        title_numbers, title_kind = [number], "number"
    else:
        pair = parse_range(recorded_range)
        if not pair:
            return {"status": "unresolved", "checked_on": today,
                    "method": f"Recorded address range {recorded_range!r} is not a pair of "
                              f"street numbers, so it cannot be expanded and looked up.",
                    "note": "Range not machine-readable; a hand check could still place it."}
        title_numbers, title_kind = expand_range(*pair), "range"
    title = resolve_numbers(city, name, stype, title_numbers)

    # ---- the archivist's second address, where the two disagree ------------ #
    # A `conflict` is only this branch's business when the record states a
    # second address to compare. Findings whose conflict is a date or a name —
    # a survey that dates the same building twice — resolve normally; the
    # disagreement is the page's `.unknowns` to carry, not the resolver's.
    address_conflict = bool(f.get("conflict")) and note_addr is not None
    note_hit = None
    if address_conflict:
        n_name, n_type, _ = city.normalize(note_addr["street_name"], note_addr["street_type"])
        n_numbers = note_addr["numbers"]
        if len(n_numbers) == 2 and all(x.isdigit() for x in n_numbers):
            n_numbers = expand_range(*n_numbers)
        if n_name:
            note_hit = resolve_numbers(city, n_name, n_type, n_numbers)

    label = (f"the recorded range {recorded_range} on {name} {stype or ''}".strip()
             if title_kind == "range" else eas_label(name, stype, number))

    if address_conflict:
        t_parcels = set(title["parcels"])
        n_parcels = set(note_hit["parcels"]) if note_hit else set()
        same_number = bool(note_addr) and set(note_addr["numbers"]) & set(title_numbers)
        if t_parcels and n_parcels:
            if t_parcels == n_parcels and len(t_parcels) == 1:
                parcel = next(iter(t_parcels))
                head = (f"Catalogue title and archivist's note disagree; both were checked in "
                        f"sf-eas-addresses — \"{f['address_as_written']}\" and "
                        f"\"{extra.get('address_note_as_recorded')}\" — and both land on the same "
                        f"parcel, so the disagreement does not move the building. EAS match")
                res = place(city, parcel, name, stype, title["parcels"][parcel], head, today,
                            title["keys"].get(parcel))
                res["method"] += "".join(title["notes"]) + block_check(city, f, parcel)[0] + spelling
                res["note"] = ((res.get("note", "") + " ") if res.get("note") else "") + \
                    "The conflict stays on the finding for the page's unknowns; it was not reconciled."
                return res
            return {"status": "unresolved", "checked_on": today,
                    "method": (f"Catalogue title \"{f['address_as_written']}\" resolves to parcel(s) "
                               f"{', '.join(sorted(t_parcels))}; the archivist's note "
                               f"\"{extra.get('address_note_as_recorded')}\" resolves to "
                               f"{', '.join(sorted(n_parcels))}. Both are real addresses today."),
                    "note": "The two recorded addresses are different parcels. Adjudicating between "
                            "them is invention, not research, so the finding stays unresolved."}
        if len(t_parcels) == 1 and not n_parcels:
            # The title is the catalogue's own identification of the photograph and
            # EAS corroborates it; the note's address does not exist. That is the
            # title winning on evidence, and the method says so — not a silent fix.
            parcel = next(iter(t_parcels))
            note_street = (note_addr or {}).get("street_name")
            known, _ = city.streets.eas_name(note_street) if note_street else (None, "")
            if same_number and note_street and squash(note_street) != squash(name) and not known:
                why = f"spells the street a way sf-eas-addresses has no street under ({note_street})"
            elif same_number and known and squash(known) != squash(name):
                why = f"puts the same number on {known}, which sf-eas-addresses does not"
            elif same_number:
                why = "writes the same address in a form sf-eas-addresses does not hold"
            else:
                why = "states a street number sf-eas-addresses does not have"
            head = (f"Catalogue title and archivist's note disagree — "
                    f"\"{f['address_as_written']}\" against "
                    f"\"{extra.get('address_note_as_recorded')}\". Both were checked: the title "
                    f"resolves in sf-eas-addresses and the note {why}, so the title won. "
                    f"EAS match on {label}")
            res = place(city, parcel, name, stype, title["parcels"][parcel], head, today,
                        title["keys"].get(parcel))
            res["method"] += "".join(title["notes"]) + block_check(city, f, parcel)[0] + spelling
            res["note"] = ((res.get("note", "") + " ") if res.get("note") else "") + \
                "The conflict stays on the finding for the page's unknowns; the note was not " \
                "silently corrected."
            return res
        if n_parcels and not t_parcels:
            return {"status": "unresolved", "checked_on": today,
                    "method": (f"Catalogue title \"{f['address_as_written']}\" has no EAS record; "
                               f"the archivist's note \"{extra.get('address_note_as_recorded')}\" "
                               f"resolves to {', '.join(sorted(n_parcels))}."),
                    "note": "Only the disputed second address survives in EAS; resolving on it "
                            "would be adjudicating the conflict."}
        return {"status": "unresolved", "checked_on": today,
                "method": (f"Neither recorded address has a record in sf-eas-addresses: "
                           f"\"{f['address_as_written']}\" and "
                           f"\"{extra.get('address_note_as_recorded')}\"."),
                "note": "No surviving address either way — a street-hub fact at best."}

    # ---- the ordinary cases ------------------------------------------------ #
    if not title["parcels"]:
        near = city.neighbours(name, stype or "", title_numbers[0])
        where = (f" The nearest surviving numbers on the street are "
                 f"{', '.join(near[:6])}." if near else
                 " EAS has no address near it on this street either.")
        block = extra.get("assessor_block_as_recorded")
        blk = (f" The record's assessor block {block} still places it on that "
               f"city block." if block else "")
        if title["unparcelled"]:
            # The address is in EAS but cannot be joined to one parcel — either
            # the EAS record carries no parcel number, or its point falls in a
            # condominium's worth of them.
            condo = any("condominium" in n for n in title["notes"])
            return {"status": "unresolved", "checked_on": today,
                    "method": (f"sf-eas-addresses has {', '.join(title['unparcelled'])} "
                               f"{name} {stype or ''}".rstrip() + " but it does not join to one "
                               "parcel." + "".join(title["notes"]) + spelling),
                    "note": (("The address is a condominium today, and the directory contract in "
                              "the root AGENTS.md defers those: each unit has its own parcel and "
                              "none of them is the building the record names."
                              if condo else
                              "The address exists but cannot be joined to a parcel, so there is no "
                              "page to put it on. EAS leaves addresses unparcelled for rear units, "
                              "vacated lots and addresses in flux; a later pass may find one.")
                             + blk)}
        return {"status": "unresolved", "checked_on": today,
                "method": (f"No record in sf-eas-addresses for {label}"
                           + (f" (checked {', '.join(title_numbers[:8])}"
                              f"{'…' if len(title_numbers) > 8 else ''})"
                              if title_kind == "range" else "") + "." + spelling),
                "note": ("The address does not exist today, so there is no page it can go on."
                         + where + blk +
                         " Per \"The evidence bar\" in research/AGENTS.md this is a street-hub "
                         "fact: a dated record of a building at a number the city no longer has.")}

    if not stype and len(title["types"]) > 1:
        return {"status": "unresolved", "checked_on": today,
                "method": (f"The record gives no street type. EAS has {label} on "
                           f"{', '.join(sorted(t for t in title['types'] if t))}, "
                           f"and the record says nothing that chooses between them." + spelling),
                "note": "Ambiguous street type; a cross street or the assessor block would settle it."}

    named = ""
    if len(title["parcels"]) > 1:
        listed = ", ".join(f"{p} ({', '.join(ns)})" for p, ns in sorted(title["parcels"].items()))
        # The record's own assessor lot is allowed to choose here — following the
        # parcel a survey states is reading the record, not adjudicating it.
        own = [p for p in recorded_parcels(f) if p in title["parcels"]]
        if len(set(own)) == 1:
            keep = own[0]
            named = (f" The recorded numbers span {len(title['parcels'])} parcels today "
                     f"({listed}); the record names assessor block "
                     f"{f['extra']['assessor_block_as_recorded']} lot "
                     f"{f['extra']['assessor_lot_as_recorded']} itself, which is {keep}, so that "
                     f"is the parcel taken.")
            title["parcels"] = {keep: title["parcels"][keep]}
        elif len(title.get("stated") or {}) == 1:
            # The odd parcel out here came from a number whose EAS row carries no
            # parcel of its own, so it was placed by the point its coordinates
            # fall in — and DATA-SOURCES.md's caution is that those points sit
            # centimetres from a parcel boundary. Where every number that states
            # a parcel agrees on one, the point-placed neighbour is that caution
            # firing, not a second parcel. 1940-1946 Fillmore Street, an extant
            # National Register building on one lot, declined on 1944 alone.
            keep = next(iter(title["stated"]))
            by_point = ", ".join(n for p, ns in sorted(title["parcels"].items())
                                 for n in ns if p != keep)
            named = (f" The recorded numbers span {len(title['parcels'])} parcels today "
                     f"({listed}), but only {keep} is a parcel EAS states: {by_point} carries no "
                     f"parcel number of its own and was placed by the point its coordinates fall "
                     f"in, which sf-parcels puts on a neighbouring lot. The stated parcel is "
                     f"taken.")
            title["parcels"] = {keep: title["parcels"][keep]}
        else:
            return {"status": "unresolved", "checked_on": today,
                    "method": (f"{label} spans more than one parcel in sf-eas-addresses today: "
                               f"{listed}." + spelling),
                    "note": ("The numbers the record gives are on different parcels now, so the "
                             "record cannot be placed on one page without deciding which — "
                             "which the record does not say.")}

    parcel, matched = next(iter(title["parcels"].items()))
    if title_kind == "range":
        head = (f"Recorded range {recorded_range} {name} {stype or ''}".rstrip()
                + f"; EAS matches {', '.join(matched)} on this street")
    else:
        head = f"EAS exact match on {label}"
        if not recorded_type:
            types = sorted(t for t in title["types"] if t)
            head += (f" (the record states no street type; EAS has this number on "
                     f"{', '.join(types)} only)" if types else
                     " (neither the record nor EAS gives this street a type)")
    res = place(city, parcel, name, stype, matched, head, today,
                title["keys"].get(parcel))
    res["method"] += named + "".join(title["notes"])
    if title_kind == "range" and (title["misses"] or title["unparcelled"]):
        gone = ", ".join(title["misses"][:6])
        loose = ", ".join(title["unparcelled"][:6])
        res["method"] = res["method"].rstrip(".") + "." + (
            f" EAS has no record for {gone} on this street." if gone else "") + (
            f" {loose} is in EAS on this street but carries no parcel number."
            if loose else "")
    clause, agrees = block_check(city, f, parcel)
    res["method"] += clause + spelling
    res = renumbering_guard(f, res)
    if not agrees and res["status"] == "resolved" and not f.get("conflict"):
        # An address EAS matches exactly, against a block number that says
        # somewhere else. Per RUNBOOK.md a contradiction like this is not
        # a resolution problem: resolve the address, keep both claims, and hand
        # the disagreement to the publisher as a conflict.
        res["note"] = ((res.get("note", "") + " ") if res.get("note") else "") + \
            "The record's assessor block contradicts the parcel; both claims are kept."
        res["_set_conflict"] = (
            f"The record is filed under assessor block "
            f"{f['extra']['assessor_block_as_recorded']}, but the address it states resolves in "
            f"sf-eas-addresses to parcel {parcel}, on another block. Recorded, not reconciled.")
    return res


# --------------------------------------------------------------------------- #
# The site's own pages — the other half of "which page does this belong on"
# --------------------------------------------------------------------------- #

def page_index() -> list:
    """Every published address page: its apn, path, street directory, neighborhood.

    A parcel that already has a page settles `resolution.path` outright; the rest
    supply the mapping from an analysis neighborhood to the directory the site
    files it under, which is not derivable from any dataset.
    """
    out = []
    for p in sorted((REPO / "san-francisco").glob("*/*/*/data.json")):
        try:
            d = json.loads(p.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        rel = p.relative_to(REPO).parent
        coords = d.get("coordinates") or {}
        out.append({"path": d.get("path") or "/" + str(rel) + "/",
                    "apn": d.get("apn"), "area": rel.parts[1], "street_dir": rel.parts[2],
                    "nhood": (d.get("parcel") or {}).get("analysis_neighborhood"),
                    "lat": coords.get("lat"), "lng": coords.get("lng")})
    return out


def candidate_parcels(city: City, findings: dict) -> list:
    """The APNs the findings actually land on — nothing else is worth fetching.

    Keying the parcel map and the roll off every APN on every street in the file
    is tens of thousands of parcels for a batch that touches a thousand.
    """
    apns: set = set()
    for f in findings["findings"]:
        for name, stype, numbers in recorded_addresses(f, city):
            for n in numbers:
                for r in city.rows_for(name, stype, n):
                    if r.get("parcel_number"):
                        apns.add(r["parcel_number"])
                        # A parcel's other numbers decide which one the page takes.
                        for sib in city.by_parcel.get(r["parcel_number"], []):
                            if sib.get("parcel_number"):
                                apns.add(sib["parcel_number"])
    return sorted(apns)


def recorded_addresses(f: dict, city: City = None) -> list:
    """Every (street name, type, numbers) the record states — title and note."""
    out = []
    extra = f.get("extra") or {}
    name, stype = f.get("street_name"), f.get("street_type")
    if city and name:
        eas_name, eas_type, _ = city.normalize(name, stype)
        name, stype = eas_name or name, eas_type
    if name:
        # Same precedence as decide(): a recorded range is the whole range, even
        # when the finding also carries its low number.
        pair = parse_range(extra.get("address_range_as_recorded"))
        if pair:
            out.append((name, stype, expand_range(*pair)))
        elif f.get("street_number"):
            # An unreadable range still has its low number, and dropping the
            # finding here means `fetch` never asks for its parcel at all.
            out.append((name, stype, [f["street_number"]]))
    parsed = parse_address(extra.get("address_note_as_recorded"))
    if parsed:
        numbers = parsed["numbers"]
        if len(numbers) == 2 and numbers[0].isdigit() and numbers[1].isdigit():
            numbers = expand_range(numbers[0], numbers[1])
        p_name, p_type = parsed["street_name"], parsed["street_type"]
        if city:
            eas_name, eas_type, _ = city.normalize(p_name, p_type)
            p_name, p_type = eas_name or p_name, eas_type
        out.append((p_name, p_type, numbers))
    return out



# --------------------------------------------------------------------------- #
# The manifest the seeder consumes
# --------------------------------------------------------------------------- #

CODE_WORD = {code: word for word, code in ORDINAL_WORD.items()
             if "-" not in word and len(code) == 4}


def street_display(name: str, stype: str) -> str:
    """"GRANT", "AVE" -> "Grant Avenue". Matches scripts/seed_pages.py."""
    word = STREET_TYPE_WORD.get((stype or "").upper(), (stype or "").lower())
    parts = []
    for token in (name or "").split():
        token = unpad(token)
        if re.fullmatch(r"\d+(ST|ND|RD|TH)", token.upper()):
            parts.append(token.lower())
        elif token.lower() == "the":
            parts.append("The")
        else:
            parts.append(token.capitalize())
    return (" ".join(parts) + " " + word.capitalize()).strip()


def build_manifest(city: City, data: dict) -> list:
    """The resolved parcels that have no page yet, in the seeder's entry shape.

    Every run that publishes in bulk needs this list and every run used to build
    it by hand from the report. The resolutions already name the parcel, the
    path and the street; EAS supplies the rest.
    """
    by_parcel: dict = {}
    for f in data["findings"]:
        res = f.get("resolution") or {}
        if res.get("status") != "resolved" or not res.get("apn"):
            continue
        m = re.match(r"^/([a-z\-]+)/([a-z\-]+)/([a-z0-9\-]+)/([^/]+)/$", res["path"] or "")
        if not m:
            continue
        # Ask the filesystem whether the page exists, not the note. This used to
        # test `note.startswith("No page at this path yet")`, which is a string
        # this tool writes itself — so a resolution corrected by hand, which
        # carries whatever note the publisher wrote, dropped out of the manifest
        # without a word and its page was never seeded. Twice in one run.
        if (REPO / res["path"].strip("/") / "data.json").exists():
            continue                       # the page exists; the seeder skips it anyway
        city_slug, area, slug, number = m.groups()
        apn = res["apn"]
        if apn in by_parcel:
            continue
        name = f.get("street_name") or ""
        eas_name, stype, _ = city.normalize(name, f.get("street_type"))
        eas_name = eas_name or name
        rows = [r for r in city.by_parcel.get(apn, []) + city.by_effective.get(apn, [])]
        # A building that has been readdressed resolves onto a street the
        # finding never names — the Worden plate headed "299 Moncada Way" whose
        # own note says the address is now 101 Paloma Avenue, and every other
        # "site of today's #N" record. The path already carries the new street;
        # taking the name from the finding leaves the entry's `street_name`
        # disagreeing with its `street_slug`, which matches no EAS row on the
        # parcel, so the entry gets no coordinates and the seeder dies on a
        # KeyError. The resolution's own `eas_address` is the address that was
        # actually placed, so ask the parcel's rows which one it is.
        landed = next((r for r in rows
                       if eas_label(r.get("street_name") or "",
                                    r.get("street_type"),
                                    (r.get("address_number") or "").upper())
                       == (res.get("eas_address") or "")), None)
        if landed and (landed.get("street_name") or "") != eas_name:
            eas_name = landed.get("street_name") or eas_name
            stype = landed.get("street_type") or ""
        same = [r for r in rows if (r.get("street_name") or "") == eas_name]
        stype = stype or next((r.get("street_type") for r in same), "") or ""
        # The path already carries the parcel's lowest number, and it is worked
        # out from a wider set of EAS rows than this one: an address filed under
        # a since-retired parcel reaches the path through that parcel's key and
        # would be missed here. Leave it out and the seeder puts the page in a
        # different directory from the one every resolution points at — one
        # parcel, two places, and the facts land on neither.
        numbers = sorted({(r.get("address_number") or "").upper() for r in same
                          if r.get("address_number")} | {number.upper()}, key=num_key)
        others = sorted({eas_label(r.get("street_name") or "", r.get("street_type"),
                                   (r.get("address_number") or "").upper())
                         for r in rows if (r.get("street_name") or "") != eas_name})
        pick = next((r for r in same if r.get("latitude")), None) or (same[0] if same else None)
        entry = {"apn": apn, "city": city_slug, "area": area, "street_slug": slug,
                 "street_name": eas_name, "street_type": stype,
                 "street_display": street_display(eas_name, stype),
                 "numbers": numbers, "other_street_addresses": others}
        # The seeder runs its own condominium check on the roll's class code
        # alone, which is right for a unit stack and wrong for an old parcel
        # that was condominium-mapped and never split. This resolution only
        # exists because condo_warning already tested the stronger thing — that
        # EAS puts these numbers on this parcel and no other — so say so, and
        # let the seeder honour the check that had the evidence.
        roll_row = city.roll.get(apn) or {}
        if "condominium" in (roll_row.get("property_class_code_definition") or "").lower():
            entry["sole_parcel_for_address"] = True
        if pick:
            if pick.get("latitude"):
                entry["lat"] = float(pick["latitude"])
                entry["lng"] = float(pick["longitude"])
            if pick.get("zip_code"):
                entry["zip"] = str(pick["zip_code"])
            if pick.get("eas_baseid"):
                entry["eas_baseid"] = str(pick["eas_baseid"])
        by_parcel[apn] = entry
    return [by_parcel[k] for k in sorted(by_parcel)]


def load_city(findings: dict, refresh: bool = False, aliases: dict = None,
              area_from_nhood: bool = False) -> City:
    streets = StreetIndex(street_names(refresh=refresh), aliases)
    recorded = {f["street_name"] for f in findings["findings"] if f.get("street_name")}
    for f in findings["findings"]:
        parsed = parse_address((f.get("extra") or {}).get("address_note_as_recorded"))
        if parsed:
            recorded.add(parsed["street_name"])
    names, unknown = set(), []
    for n in sorted(recorded):
        eas_name, _ = streets.eas_name(n)
        (names.add(eas_name) if eas_name else unknown.append(n))
    if unknown:
        print(f"  no EAS street for: {', '.join(unknown)}", file=sys.stderr, flush=True)
    eas = fetch_keyed("eas", EAS, "street_name", sorted(names), EAS_SELECT,
                      chunk=12, refresh=refresh)
    city = City(eas, page_index(), streets, area_from_nhood=area_from_nhood)
    apns = candidate_parcels(city, findings)
    print(f"  {len(apns)} candidate parcels", file=sys.stderr, flush=True)
    parcels = fetch_keyed("parcels", PARCELS, "blklot", apns, PARCEL_SELECT,
                          chunk=100, refresh=refresh)
    roll = fetch_keyed("roll", ROLL, "parcel_number", apns, ROLL_SELECT,
                       where="closed_roll_year='2025'", chunk=100, refresh=refresh)
    city.attach(parcels, roll)

    # Only now can we see which addresses EAS files under a parcel that is gone
    # (or under none at all). Those, and only those, get a spatial lookup.
    stale, stale_rows = set(), []
    for f in findings["findings"]:
        for name, stype, numbers in recorded_addresses(f, city):
            for n in numbers:
                for r in city.rows_for(name, stype, n):
                    parcel = city.parcels.get(r.get("parcel_number") or "")
                    if not parcel or str(parcel.get("active")).lower() not in ("true", "1"):
                        stale.add(point_key(r.get("latitude"), r.get("longitude")))
                        stale_rows.append(r)
    stale.discard("")
    if stale:
        print(f"  {len(stale)} address(es) need an active parcel by point",
              file=sys.stderr, flush=True)
    points = fetch_points(sorted(stale), refresh=refresh)
    city.attach_spatial(points, stale_rows)
    found = sorted({row["blklot"] for rows in points.values() for row in rows
                    if row.get("blklot") and row["blklot"] not in city.parcels})
    if found:
        print(f"  {len(found)} parcel(s) found by point need their roll rows",
              file=sys.stderr, flush=True)
        parcels += fetch_keyed("parcels", PARCELS, "blklot", apns + found, PARCEL_SELECT,
                               chunk=100, refresh=refresh)
        roll += fetch_keyed("roll", ROLL, "parcel_number", apns + found, ROLL_SELECT,
                            where="closed_roll_year='2025'", chunk=100, refresh=refresh)
        city.attach(parcels, roll)
    return city


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("command", choices=("fetch", "report", "apply", "manifest"))
    ap.add_argument("findings", type=Path)
    ap.add_argument("--refresh", action="store_true", help="ignore the cache and re-fetch")
    ap.add_argument("--on", default=date.today().isoformat(), help="checked_on date")
    ap.add_argument("--out", type=Path,
                    help="manifest: where to write the parcel list "
                         "(default research/manifests/<batch>.json)")
    ap.add_argument("--area-from-nhood", action="store_true",
                    help="file new pages under the analysis neighborhood the assessor and EAS "
                         "give the parcel, instead of the area of the nearest published page. "
                         "Use it where the site has too few pages on a street for proximity to "
                         "mean anything — a whole corridor otherwise scatters across the "
                         "directories of whichever handful of pages happen to exist. Every "
                         "resolution says which rule chose its directory.")
    ap.add_argument("--alias", action="append", default=[], metavar="RECORDED=EAS",
                    help="map a street name the source spells its own way onto EAS's "
                         "(e.g. --alias DOUGLAS=DOUGLASS). Every use is stated in the "
                         "resolution method, so it stays auditable.")
    args = ap.parse_args()

    aliases = dict(a.split("=", 1) for a in args.alias)
    data = json.loads(args.findings.read_text(encoding="utf-8"))
    city = load_city(data, refresh=args.refresh, aliases=aliases,
                     area_from_nhood=args.area_from_nhood)
    if args.command == "fetch":
        print(f"{len(city.eas)} EAS addresses, {len(city.parcels)} parcels, "
              f"{len(city.roll)} roll rows, {len(city.pages)} pages cached.")
        return 0

    if args.command == "manifest":
        entries = build_manifest(city, data)
        out = args.out or (REPO / "research" / "manifests" / f"{data['batch']}.json")
        # --out is whatever the caller typed, so it may be relative, and a
        # relative path is not "in the subpath of" REPO — relative_to raises
        # rather than returning it. Resolve first, and fall back to the path as
        # given for an --out that genuinely points outside the repo.
        out = out.resolve()
        out.write_text(json.dumps(entries, indent=1, ensure_ascii=False) + "\n",
                       encoding="utf-8")
        areas = Counter(e["area"] for e in entries)
        try:
            shown = out.relative_to(REPO)
        except ValueError:
            shown = out
        print(f"{len(entries)} parcels with no page yet → {shown}")
        for area, n in areas.most_common():
            print(f"  {area}: {n}")
        return 0

    tally, decisions, conflicts = Counter(), {}, {}
    for f in data["findings"]:
        res = decide(city, f, args.on)
        # A contradiction the resolver found rather than inherited — the block
        # the archivist filed the photograph under against the parcel the
        # address resolves to. RUNBOOK.md says record it on the finding.
        if "_set_conflict" in res:
            conflicts[f["id"]] = res.pop("_set_conflict")
        decisions[f["id"]] = res
        tally[res["status"]] += 1

    # One parcel, two paths: a corner building the source addresses on both its
    # streets. One page per parcel is the directory contract, so say so here
    # rather than leaving the publisher to notice.
    by_apn: dict = defaultdict(set)
    for res in decisions.values():
        if res.get("apn") and res.get("path"):
            by_apn[res["apn"]].add(res["path"])
    for res in decisions.values():
        others = sorted(by_apn.get(res.get("apn"), set()) - {res.get("path")})
        if others:
            res["note"] = ((res.get("note", "") + " ") if res.get("note") else "") + (
                f"This batch also resolves parcel {res['apn']} from another street "
                f"({', '.join(others)}) — a corner building. One page per parcel: the other "
                f"address belongs on it as an alias, not as a second page.")

    if args.command == "report":
        for f in data["findings"]:
            r = decisions[f["id"]]
            print(f"{f['id']}  {r['status']:<10} {f['address_as_written'][:48]:<50}"
                  f"{r.get('path') or r.get('note', '')[:70]}")
        print()
        # The record's own parcel against the one it resolved to. This is the
        # only check in the tool that tests a finished resolution rather than
        # producing one, and on a scanned source it is the thing that catches
        # an OCR digit before it reaches a page.
        checks = Counter()
        disagree = []
        for f in data["findings"]:
            r = decisions[f["id"]]
            if r["status"] != "resolved":
                continue
            verdict = recorded_parcel_check(f, r.get("apn") or "")
            checks[verdict or "not stated"] += 1
            if verdict in ("relot", "block"):
                e = f.get("extra") or {}
                disagree.append((verdict, f["id"], f["address_as_written"][:34],
                                 f"{e.get('assessor_block_as_recorded')}/"
                                 f"{e.get('assessor_lot_as_recorded')}", r["apn"]))
        if checks["match"] or disagree:
            print(f"Recorded parcel vs resolved parcel: {checks['match']} exact, "
                  f"{checks['relot']} re-lotted since, {checks['block']} on another block, "
                  f"{checks['not stated']} not stated by the record.")
            for verdict, fid, addr, printed, apn in disagree:
                label = "another block" if verdict == "block" else "re-lotted"
                print(f"  {label:<13} {fid}  {addr:<36} printed {printed:<12} → {apn}")
            if checks["block"]:
                print("  Read every 'another block' line before applying: on a scanned "
                      "source most are a lost digit, and the rest are the record's own error.")
            print()

        # A resolution the point made, on a parcel that says it does not carry
        # the number. Raised, never decided — but ranked by the thing that
        # actually settles it, which is not the stated range.
        #
        # Measured over every findings file in the repo, the stated-range test
        # alone fires on 61 of 582 point-placed resolutions and 46 of those are
        # right: sf-parcels' `from_address_num` / `to_address_num` is routinely
        # narrower than the numbers a parcel holds ("2861 24th Street" on a
        # parcel stated 2863–2869), and EAS sometimes still files the number
        # under a parcel sf-parcels reports retired while the point found its
        # active successor. Reading all 61 by hand found one signal that
        # separated right from wrong every time: **another parcel holding a
        # number between the address and the parcel the point chose.** With
        # nothing in between the resolution was correct in all 35 such cases;
        # with something in between it was the neighbour, or several doors
        # past it, in all 13.
        outside = []
        for f in data["findings"]:
            r = decisions[f["id"]]
            if r["status"] != "resolved" or "coordinates fall in is" not in \
                    (r.get("method") or ""):
                continue
            parcel = (city.parcels or {}).get(r.get("apn") or "") or {}
            lo, hi = parcel.get("from_address_num"), parcel.get("to_address_num")
            m = re.match(r"\d+", f.get("street_number") or "")
            num = num_key(m.group(0)) if m else None
            if not (lo and hi and num is not None):
                continue
            name, stype = f.get("street_name") or "", f.get("street_type") or ""
            if (parcel.get("street_name") or "") != name:
                continue
            if num_key(lo) <= num <= num_key(hi):
                continue
            gap = min(abs(num[0] - num_key(lo)[0]), abs(num[0] - num_key(hi)[0]))
            outside.append((f["id"], f["address_as_written"][:34], r["apn"],
                            f"{lo}\u2013{hi} {parcel.get('street_name','')}", gap,
                            between_on_street(city, name, stype, num[0], r["apn"],
                                              (num_key(lo)[0], num_key(hi)[0]))))
        if outside:
            crowded = [o for o in outside if o[5][0]]
            print(f"Placed by point, on a parcel whose own range excludes the "
                  f"number: {len(outside)}, {len(crowded)} with another parcel in between.")
            for fid, addr, apn, rng, gap, between in sorted(
                    outside, key=lambda x: (-len(x[5][0]), -x[4])):
                hits, nearby = between
            if hits:
                where = (", ".join(f"{n} on {p}" for n, p in hits[:3])
                         + (" …" if len(hits) > 3 else "") + " — in between")
            elif nearby:
                where = "nothing in between"
            else:
                where = "EAS joins no parcel to any number near this one — unchecked"
                print(f"  {gap:>4} off      {fid}  {addr:<36} {apn} states {rng}")
                print(f"                  {where}")
            print("  EAS address points sit centimetres from a boundary, so a point can land in "
                  "the neighbour.\n  The line under each one is the block's own number line. "
                  "Another parcel holding a number\n  between the address and the one the point "
                  "chose means the point is short of it; nothing\n  in between is the immediate "
                  "neighbour and an incomplete range field, which is what the\n  great majority "
                  "of these are; and a stretch EAS joins no parcel to says only that the\n  "
                  "number line cannot see this one.")
            print()

        # The record saying its own building is gone. Not decided here: two
        # passes over the repo's findings showed the marking is wrong or
        # about a different building often enough that only a person can call
        # it. See the note above BARE_DEMOLITION.
        gone, mentioned = [], []
        for f in data["findings"]:
            r = decisions[f["id"]]
            if r["status"] == "rejected":
                continue
            marker = demolished_as_recorded(f)
            if marker:
                gone.append((f["id"], f["address_as_written"][:40], marker, r["status"]))
            else:
                hit = demolition_mentioned(f)
                if hit:
                    mentioned.append((f["id"], f["address_as_written"][:40], hit[1][:60]))
        if gone or mentioned:
            print(f"The record marks a building gone: {len(gone)} stated plainly, "
                  f"{len(mentioned)} mentioned in passing.")
            for fid, addr, marker, status in gone:
                print(f"  marked        {fid}  {addr:<42} \u201c{marker}\u201d  ({status})")
            for fid, addr, text in mentioned:
                print(f"  mentioned     {fid}  {addr:<42} \u201c{text}\u201d")
            print("  A demolished building is rejected, not resolved: its number usually still "
                  "resolves to a\n  live parcel, and publishing there hangs the fact on whatever "
                  "stands now. But check each one\n  \u2014 the thing that came down is often a "
                  "predecessor or one building of a group, and a source\n  can simply be wrong "
                  "(two volumes mark the Swedenborgian Church demolished; it stands).")
            print()
    print(f"{sum(tally.values())} findings: " +
          ", ".join(f"{n} {s}" for s, n in tally.most_common())
          + (f"; {len(conflicts)} new conflict(s) recorded" if conflicts else ""))

    if args.command == "apply":
        # A finding the reader has already rejected is not the tool's to
        # reconsider. The reasons a run rejects by hand are ones the joins
        # cannot see — the source itself says the building is demolished, the
        # address is outside San Francisco, the record names no number at all —
        # and overwriting them with "unresolved" loses the reason and invites
        # the next run to try again. Every other status is recomputed.
        kept = 0
        for f in data["findings"]:
            if (f.get("resolution") or {}).get("status") == "rejected":
                kept += 1
                continue
            f["resolution"] = decisions[f["id"]]
            if f["id"] in conflicts and not f.get("conflict"):
                f["conflict"] = conflicts[f["id"]]
        if kept:
            print(f"  left {kept} finding(s) already marked rejected untouched")
        args.findings.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n",
                                 encoding="utf-8")
        print(f"wrote {args.findings}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
