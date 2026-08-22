#!/usr/bin/env python3
"""Turn one DigitalSF archival collection into a findings file.

    python3 research/tools/digitalsf_extract.py "SFP 23" sfp-23
    python3 research/tools/digitalsf_extract.py "SFP 23" sfp-23 --report

The first argument matches against `524$a`, which is the preferred citation and
also the batch unit for this source — see research/sources/digitalsf.md. The
second names the output file, `research/findings/digitalsf/<batch>.json`.
`--report` prints the coverage counts and the address strings it kept and
dropped, without writing anything; that is the pass you read before committing.

What it reads out of each MARC record, and why:

  245$a   the catalogued title, which is where an exact street number appears
  500$a   the archivist's own `Address. Box N; <street>, <number>.` note, and
          the `Block. Box N; Block <n>.` note that gives an assessor block
  260$c   the date — **not** 269$a. 269$a collapses "between 1946 and 1951"
          to 1946, so reading it promotes an archivist's range to a firm year.
  907$a   `fuzzy date`, which flags only some of those ranges (see below)
  540$f   rights, machine-readable
  524$a   the citation a page prints
  852$c   the physical box and bundle
  610/650 controlled corporate and topical headings

Two things this deliberately does not do. It does not invent a `street_type`
the source never stated — "1377 Fulton" yields a street name and no type, and
the resolver decides. And it takes named firms out of a title but leaves bare
personal names behind, per "Privacy — hard limits" in the root AGENTS.md;
`--report` prints both lists so the filter can be checked by eye.

Stdlib only.
"""
from __future__ import annotations

import collections
import datetime
import glob
import json
import pathlib
import re
import sys
import xml.etree.ElementTree as ET

ROOT = pathlib.Path(__file__).resolve().parents[1]
CORPUS = ROOT / "corpora" / "digitalsf"
M = "{http://www.loc.gov/MARC21/slim}"
O = "{http://www.openarchives.org/OAI/2.0/}"

RECORD_URL = "https://digitalsf.org/record/{}"

# --------------------------------------------------------------------------- #
# Reading the corpus
# --------------------------------------------------------------------------- #

def records(collection: str):
    """Yield {id, oai, page, fields} for each unique record in one collection.

    Deduplicates on the OAI identifier: the sets overlap, so a record reached
    through `Photographs` is usually also in `city` and `sfhistory`.
    """
    seen: set[str] = set()
    for page in sorted(glob.glob(str(CORPUS / "*" / "page-*.xml"))):
        try:
            root = ET.parse(page).getroot()
        except ET.ParseError as exc:
            print(f"  ! unparseable: {page}: {exc}", file=sys.stderr)
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
            fields: dict[str, list[list[tuple[str, str]]]] = {}
            for f in mrc.iter(M + "datafield"):
                fields.setdefault(f.get("tag"), []).append(
                    [(s.get("code"), (s.text or "").strip()) for s in f])
            if collection not in first(fields, "524", "a"):
                continue
            cf = mrc.find(f"{M}controlfield[@tag='001']")
            yield {"id": (cf.text or "") if cf is not None else "",
                   "oai": oai,
                   "page": str(pathlib.Path(page).relative_to(ROOT.parent)),
                   "fields": fields}


def first(fields, tag, code) -> str:
    for f in fields.get(tag, []):
        for c, v in f:
            if c == code:
                return v
    return ""


def every(fields, tag, code) -> list[str]:
    return [v for f in fields.get(tag, []) for c, v in f if c == code]


# --------------------------------------------------------------------------- #
# Dates
#
# 269$a is a single year and 260$c is what the archivist actually wrote. Where
# 260$c reads "between 1946 and 1951", 269$a reads 1946 — so a pass that trusts
# 269$a records an estimate as a firm year. 907$a `fuzzy date` catches only
# some of those; in SFP 23 it flags 115 of the 298 imprecise dates.
# --------------------------------------------------------------------------- #

ISO_DAY = re.compile(r"^\d{4}-\d{2}-\d{2}$")
ISO_MONTH = re.compile(r"^\d{4}-\d{2}$")
ISO_YEAR = re.compile(r"^\d{4}$")
BETWEEN = re.compile(r"^(?:between\s+)?(\d{4})\s*(?:and|to|-)\s*(\d{4})$", re.I)
YEAR_IN = re.compile(r"\b(1[89]\d\d|20[0-2]\d)\b")


def read_date(fields) -> dict:
    """Return {date, precision, as_recorded, range?} from 260$c, 269$a, 907$a."""
    raw = first(fields, "260", "c").strip()
    fallback = first(fields, "269", "a").strip()
    fuzzy = any("fuzzy" in v.lower() for v in every(fields, "907", "a"))
    out = {"as_recorded": raw or fallback, "fuzzy_flag": fuzzy}

    if ISO_DAY.match(raw):
        out.update(date=raw, precision="day")
    elif ISO_MONTH.match(raw):
        out.update(date=raw, precision="month")
    elif ISO_YEAR.match(raw):
        out.update(date=raw, precision="year")
    else:
        m = BETWEEN.match(raw)
        if m:
            out.update(date=raw, precision="circa",
                       range=[int(m.group(1)), int(m.group(2))])
        elif YEAR_IN.search(raw):
            out.update(date=raw, precision="circa")
        elif ISO_YEAR.match(fallback):
            out.update(date=fallback, precision="year")
        else:
            out.update(date=raw or fallback, precision="unknown")
    return out


# --------------------------------------------------------------------------- #
# Addresses
# --------------------------------------------------------------------------- #

# EAS abbreviations, from scripts/seed_pages.py's STREET_TYPE_WORD.
TYPE_ABBR = {
    "street": "ST", "st": "ST", "avenue": "AVE", "ave": "AVE", "av": "AVE",
    "boulevard": "BLVD", "blvd": "BLVD", "way": "WAY", "court": "CT",
    "ct": "CT", "terrace": "TER", "ter": "TER", "place": "PL", "pl": "PL",
    "drive": "DR", "dr": "DR", "lane": "LN", "ln": "LN", "alley": "ALY",
    "road": "RD", "rd": "RD", "highway": "HWY", "hwy": "HWY",
    "stairway": "STWY", "walk": "WALK", "circle": "CIR", "plaza": "PLZ",
    "row": "ROW", "path": "PATH", "steps": "STPS",
}
WORD_ORDINAL = {
    "first": 1, "second": 2, "third": 3, "fourth": 4, "fifth": 5, "sixth": 6,
    "seventh": 7, "eighth": 8, "ninth": 9, "tenth": 10, "eleventh": 11,
    "twelfth": 12, "thirteenth": 13, "fourteenth": 14, "fifteenth": 15,
    "sixteenth": 16, "seventeenth": 17, "eighteenth": 18, "nineteenth": 19,
    "twentieth": 20, "twenty-first": 21, "twenty-second": 22,
    "twenty-third": 23, "twenty-fourth": 24, "twenty-fifth": 25,
}
SUFFIX = {1: "ST", 2: "ND", 3: "RD"}

# "1377 Fulton", "2929-2931 24th Street", "547-547A Castro Street", "7 7th Ave".
# Four name tokens, because "415 El Camino Del Mar" needs them, and the
# lowercase particles because the same street is also filed "El Camino del Mar".
NAME_TOKEN = r"(?:[A-Z][A-Za-z'./]*|\d{1,2}(?:st|nd|rd|th)|del|de|la|van|von)"
TITLE_ADDR = re.compile(
    rf"\b(\d{{1,5}}[A-Za-z]?(?:\s*-\s*\d{{1,5}}[A-Za-z]?)?)\s+"
    rf"({NAME_TOKEN}(?:\s+{NAME_TOKEN}){{0,3}})\b")

# `Address. Box 3; Mission, 3232-3234.`  `Address. Box 1, Cortland 415.`
# `Address. Fulton, 1377.`               `Address. Box 4; 2900-2904, 24th st.`
ADDR_NOTE = re.compile(r"^\s*(?:SFP\s*\d+\.?\s*)?Address\.?\s*(.*?)\s*\.?\s*$", re.I)
BLOCK_NOTE = re.compile(
    r"^\s*(?:SFP\s*\d+\.?\s*)?Block\.?\s*(?:Box\s*#?\s*([\w]+)\s*[;,])?\s*"
    r"Block\s*#?\s*(\d+)", re.I)
BOX_PREFIX = re.compile(r"^\s*Box\s*#?\s*([\w]+)\s*[;,]\s*", re.I)
NUMBERISH = r"\d{1,5}[A-Za-z]?(?:\s*-\s*\d{1,5}[A-Za-z]?)?"
NOTE_STREET_FIRST = re.compile(rf"^(.*?)[;,]?\s*({NUMBERISH})$")
NOTE_NUMBER_FIRST = re.compile(rf"^({NUMBERISH})\s*[;,]\s*(.+)$")

BLOCK_PHRASE = re.compile(r"\b\d{1,5}\s+block\b", re.I)
# "South of 500 Bayshore Boulevard" and "Rear of 1069 Market Street" name a
# number without being at it. The number still locates the photograph, so the
# finding is worth keeping — but it does not get a `street_number`.
QUALIFIED = re.compile(
    r"((?:south|north|east|west|rear|front|corner|opposite|near)\s+of|near|"
    r"opposite)\s+$", re.I)


def normalize_street(name: str) -> tuple[str, str]:
    """('24th Street') -> ('24TH', 'ST'). Type is '' when the source omits it.

    EAS zero-pads single-digit numbered streets ("03RD"), spells nothing out,
    and holds the name in upper case. A trailing word that is not a known type
    is part of the name, not a type we failed to recognize.
    """
    tokens = [t for t in re.split(r"\s+", (name or "").strip()) if t]
    if not tokens:
        return "", ""
    stype = ""
    if len(tokens) > 1 and TYPE_ABBR.get(tokens[-1].lower().rstrip(".")):
        stype = TYPE_ABBR[tokens.pop().lower().rstrip(".")]

    out = []
    for token in tokens:
        low = token.lower().rstrip(".")
        if low in WORD_ORDINAL:
            n = WORD_ORDINAL[low]
            out.append(f"{n:02d}{SUFFIX.get(n % 10 if n % 100 not in (11, 12, 13) else 0, 'TH')}")
            continue
        m = re.fullmatch(r"(\d{1,2})(st|nd|rd|th)", low)
        if m:
            out.append(f"{int(m.group(1)):02d}{m.group(2).upper()}")
            continue
        out.append(token.upper())
    return " ".join(out), stype


def split_number(number: str) -> tuple[str, str]:
    """('2929-2931') -> ('', '2929-2931'); ('2929') -> ('2929', '')."""
    n = re.sub(r"\s*-\s*", "-", (number or "").strip())
    return ("", n) if "-" in n else (n, "")


def address_from_title(title: str) -> dict | None:
    """The first exact street number in a title. A block is not an address.

    Parentheses hold a second address rather than this one — "4001-4005, Judah
    (1411 45th Ave.)" is on Judah — so they come out before the match.
    """
    title = PARENTHETICAL.sub(" ", title)
    if BLOCK_PHRASE.search(title):
        return None
    m = TITLE_ADDR.search(title)
    if not m:
        return None
    number, rest = m.group(1), m.group(2)
    qualifier = QUALIFIED.search(title[:m.start()])
    # Trim trailing words that belong to the next clause rather than the street
    # name: "800 Irving Street at 9th Avenue" and "1231 9th Avenue, B&E Deli".
    tokens = rest.split()
    while tokens and tokens[-1].lower() in ("at", "and", "on", "in", "rear", "the"):
        tokens.pop()
    if not tokens:
        return None
    # A name with no recognized type keeps at most two words ("El Camino Del
    # Mar" is the exception the third slot exists for, and it has no type).
    name, stype = normalize_street(" ".join(tokens))
    if not name:
        return None
    as_written = f"{number} {' '.join(tokens)}"
    if qualifier:
        as_written = f"{qualifier.group(0).strip()} {as_written}"
    return {"as_written": as_written, "number": number, "street_name": name,
            "street_type": stype, "qualified": bool(qualifier)}


def address_from_note(note: str) -> dict | None:
    """Parse the archivist's `Address.` note. Returns None when it has no number."""
    body = note.strip().rstrip(".")
    body = BOX_PREFIX.sub("", body)
    body = re.sub(r"^\s*Address\.?\s*", "", body, flags=re.I)  # "Address. 555 Golden Gate"
    if not body:
        return None

    m = NOTE_NUMBER_FIRST.match(body)          # "2900-2904, 24th st"
    if m and re.match(r"^\d", body):
        number, street = m.group(1), m.group(2)
    else:
        m = NOTE_STREET_FIRST.match(body)      # "Mission, 3232-3234" / "Cortland 415"
        if not m:
            return None
        street, number = m.group(1), m.group(2)
    street = street.strip().rstrip(",;")
    # "Bayshore, S. or 500" is "south of 500 Bayshore" abbreviated; the parse
    # reads "S. or" as the street name, which it plainly is not.
    if (not street or re.match(r"^\d+$", street)
            or re.match(r"^[NSEW]\.?\b", street) or len(street) < 3):
        return None
    name, stype = normalize_street(street)
    if not name:
        return None
    return {"as_written": f"{number} {street}", "number": number,
            "street_name": name, "street_type": stype, "qualified": False}


SINGLE_STREET = re.compile(
    rf"^{NAME_TOKEN}(?:\s+{NAME_TOKEN}){{0,3}}$")


def location_without_number(title: str, notes: dict) -> dict:
    """What a record locates when it gives no street number.

    An intersection, a block face, an assessor block, or a named place. None of
    these clears the evidence bar, but each is a real location and the record
    is a real photograph, so it becomes an unresolved finding rather than
    nothing — that is what stops the next pass re-reading the same haystack.
    """
    note = BOX_PREFIX.sub("", (notes["address_note"] or "").strip()).strip(" .,;")
    if note:
        as_written, why = note, "The record locates the photograph but gives no street number."
    elif notes["block"]:
        as_written = f"Block {notes['block']}"
        why = "The record gives an assessor block and no street number."
    else:
        as_written, why = title.strip(), "The record names no street number."

    if BLOCK_PHRASE.search(title):
        as_written = title.strip()
        why = "A block, not an address — see research/sources/digitalsf.md."

    out = {"as_written": as_written, "why": why, "street_name": "",
           "street_type": ""}
    if SINGLE_STREET.match(as_written) and not re.search(r"\d", as_written):
        name, stype = normalize_street(as_written)
        if stype:                       # only when the type is stated
            out["street_name"], out["street_type"] = name, stype
    return out


def read_notes(fields) -> dict:
    """Pull the address note, the assessor block and the box out of 500$a."""
    out = {"address_note": "", "block": "", "box": "", "other": []}
    for note in every(fields, "500", "a"):
        m = BLOCK_NOTE.match(note)
        if m:
            out["box"] = out["box"] or (m.group(1) or "")
            out["block"] = m.group(2)
            continue
        if re.match(r"^\s*(?:SFP\s*\d+\.?\s*)?Address", note, re.I):
            body = ADDR_NOTE.match(note).group(1)
            b = BOX_PREFIX.match(body)
            if b:
                out["box"] = out["box"] or b.group(1)
            out["address_note"] = body
            continue
        out["other"].append(note)
    return out


# --------------------------------------------------------------------------- #
# Names
#
# "Take buildings, contractors, architects and named firms. Leave residents,
# occupants and owners out — at extraction time, not later." A 1951 storefront
# title lists both: "Vermont Cleaners" is a firm, "F. Justin McCarthy, M.D."
# is a person who happened to rent an office. Keep the first, drop the second,
# and drop anything the test can't call.
# --------------------------------------------------------------------------- #

# A professional credential marks the fragment as a person renting an office,
# not a firm: "F. Justin McCarthy, M.D." on a 1951 building directory.
CREDENTIAL = re.compile(
    r"\b(M\.?\s?D\.?|D\.?\s?D\.?S\.?|Dentist|Physician|Surgeon|"
    r"Attorney(\s+at\s+Law)?)\b\.?$|^\s*(Dr|Mme|Mr|Mrs|Miss)\.\s", re.I)
# ...but an honorific inside a trading name is part of the name, so
# "Mrs. Biggs Bakery" and "Mme. Plegat & Co. French Laundry" stay.
TRADING_TAIL = re.compile(
    r"\b(co|company|inc|corp|corporation|bros|brothers|shop|store|stores|"
    r"market|cafe|restaurant|tavern|grill|club|hotel|theater|church|school|"
    r"laundry|cleaners|pharmacy|drugs?|bakery|delicatessen|grocery|"
    r"groceteria|grocers|creamery|dairy|liquors?|hardware|furniture|"
    r"appliances?|realty|insurance|bank|savings|press|printing|works|mfg|"
    r"supply|supplies|services?|station|garage|motors|lumber|foundry|"
    r"machine|equipment|products|studio|salon|barber|tailors|clothiers|"
    r"apparel|jewelry|antiques|pastry|meats?|foods?|diner|billiards|bowl|"
    r"center|agency|homes|contractor|convent|florist|morticians)\b\.?$", re.I)

# Curated by eye from `--report` over the whole batch — the fragments that name
# an individual rather than a firm. An explicit list beats a heuristic here:
# the set is small, a false keep is a privacy failure, and a false drop throws
# away a fact. Re-run `--report` on a new collection and extend this.
PERSONAL_NAMES = {
    "a.p. guadagni", "beverly simpson", "chas. boegershausen", "don budge",
    "dr. f.s. crudo", "dr. p. crudo", "elsa margo", "f. justin mccarthy",
    "g.e. welles", "j.r. mount", "louis bulasky", "j. r. mount",
    "mme. ferran", "moses", "roselli", "schwartz", "schwartz - moses",
}
# Signage and vehicles caught in a photograph are not tenants of the building.
NOT_A_TENANT = re.compile(r"\b(advertisement|sign|truck)$", re.I)
# A cross street, a compass corner, or a bare descriptor.
CROSS_STREET = re.compile(
    r"^(?:\d{1,3}(?:st|nd|rd|th)\s+)?(?:[A-Z][A-Za-z'.]+\s+){0,2}"
    r"(?:Street|St\.?|Avenue|Ave\.?|Boulevard|Blvd\.?|Way|Drive|Terrace|"
    r"Alley|Place|Road|Highway|Corner)\.?$", re.I)
# "Seventh Street on northwest corner at Stevenson" describes where the camera
# stood, not a tenant. A firm called "Cozy Corner" has no compass point.
COMPASS_CORNER = re.compile(
    r"\b(?:north|south|east|west|northwest|northeast|southwest|southeast)"
    r"\s+corner\b", re.I)
LEADING_JOIN = re.compile(
    r"^(?:at|and|on|in|of|to|the\s+rear\s+of|rear\s+of|south\s+of|north\s+of|"
    r"east\s+of|west\s+of|corner\s+of|[NSEW]{1,2}\s+corner\s+of)\s+", re.I)
# The same words at the end, once the address they introduced has been removed:
# "Residence at 531 College Avenue" leaves "Residence at".
TRAILING_JOIN = re.compile(r"\s+(?:at|and|on|in|of|to|now)$", re.I)
CORP_SUFFIX = re.compile(r"^(?:inc|inc\.|ltd|ltd\.|co|co\.|corp|corp\.)$", re.I)
GENERIC = {
    "business", "businesses", "residence", "residences", "apartments",
    "church", "gas station", "gas service", "parking lot",
    "parking lot on roof", "laundry", "cafe", "restaurant", "grocery store",
    "grocery", "smoke shop", "rear", "front", "d.c.", "auto supplies",
    "delicatessen", "medical and dental", "parcel", "self-service laundry",
    "shoe hospital", "jewelry watch repairing", "general contractor",
    "liqour store", "liquor store", "variety store", "sheet metal works",
    "automotive service", "automotive electricians", "industrial surgery",
    "ballet school", "shopping center", "station j", "d.c", "apartments at",
}


# A full stop separates two names ("Potrero Avenue. Nicholls Hardware") — but
# not when it is an initial or an abbreviation ("A.P. Guadagni", "Dr. P. Crudo",
# "Leary Bros. Morticians"), which is most of the periods in these titles.
ABBREV = re.compile(r"(?:\b[A-Z]|\b(?:Dr|Mr|Mrs|Mme|St|Jr|Sr|Co|No|Inc|Bros|"
                    r"Mfg|Ave|Blvd|Corp|Ltd|Chas|Wm|Geo|Thos|Jas))$")
PARENTHETICAL = re.compile(r"\s*\([^)]*\)")
TRAILING_CROSS = re.compile(
    r"\s+(?:at|and|on)\s+(?:\d{1,3}(?:st|nd|rd|th)\s+)?"
    r"(?:[A-Z][A-Za-z'.]+\s+){0,2}"
    r"(?:Street|St\.?|Avenue|Ave\.?|Boulevard|Blvd\.?|Way|Drive|Terrace|"
    r"Alley|Place|Road|Highway)\.?$")


def split_fragments(tail: str) -> list[str]:
    """Comma-separated, plus a full stop or a spaced dash between two names.

    The dash split has to spare "Bruce & Griffin 5 - 10 Cent Stores", so it
    only fires when the left side does not end in a digit.
    """
    chunks: list[str] = []
    for comma_part in tail.split(","):
        cursor = 0
        for m in re.finditer(r"\.\s+(?=[A-Z])", comma_part):
            if ABBREV.search(comma_part[cursor:m.start()]):
                continue
            chunks.append(comma_part[cursor:m.start()])
            cursor = m.end()
        chunks.append(comma_part[cursor:])

    parts: list[str] = []
    for chunk in chunks:
        pieces = re.split(r"\s+-\s+", chunk)
        if len(pieces) > 1 and not re.search(r"\d$", pieces[0].strip()):
            parts += pieces
        else:
            parts.append(chunk)
    return parts


def business_names(title: str, address_span: str,
                   streets: list[str]) -> tuple[list[str], list[str]]:
    """Split a title's tail into (firm names kept, fragments dropped).

    Default is to keep: a fragment left over after the address is removed is
    usually the business whose sign is in the photograph, and that is the fact
    worth having. Drop on positive evidence — a credential, a curated personal
    name, another address, a cross street, a bare descriptor. `streets` is the
    record's own `Streets--<name>` headings, which is how a bare "Mission" or
    "Balboa" left behind by the address match gets recognized as a street.
    """
    tail = PARENTHETICAL.sub(" ", title)
    if address_span and address_span in tail:
        tail = tail.replace(address_span, " ")
    tail = re.sub(r"\s+", " ", tail).strip(" ,.-")
    bare_streets = {s.lower().rstrip(".") for s in streets if s}

    kept: list[str] = []
    dropped: list[str] = []
    for part in split_fragments(tail):
        # Removing the address can leave two joins stacked up — "Corner of
        # 16th Street and 3rd Street" minus "16th Street" is "Corner of and
        # 3rd Street" — so trim until the fragment stops shrinking.
        part = part.strip(" ,.-")
        while True:
            trimmed = TRAILING_JOIN.sub(
                "", TRAILING_CROSS.sub(
                    "", LEADING_JOIN.sub("", part))).strip(" ,.-")
            if trimmed == part:
                break
            part = trimmed
        if not part or len(part) < 3 or re.match(r"^parcel\b", part, re.I):
            continue
        # "Floor Styles, Inc." splits into two; put it back together.
        if CORP_SUFFIX.match(part):
            if kept:
                kept[-1] = f"{kept[-1]}, {part}"
            continue
        low = part.lower().rstrip(".")
        # "Washington & Montgomery" is a corner, not a firm — every side of it
        # is one of the streets this record is indexed under.
        sides = [s.strip() for s in re.split(r"\s*&\s*|\s+and\s+", part) if s.strip()]
        if len(sides) > 1 and all(s.lower().rstrip(".") in bare_streets
                                  or CROSS_STREET.match(s) for s in sides):
            continue
        if (low in GENERIC or low in bare_streets or CROSS_STREET.match(part)
                or COMPASS_CORNER.search(part)
                or re.fullmatch(r"[\d\W]+", part) or re.match(r"^\(", part)
                or TITLE_ADDR.match(part) or re.match(r"^\d", part)
                or NOT_A_TENANT.search(part) or YEAR_IN.fullmatch(low)):
            continue
        if low in PERSONAL_NAMES or (CREDENTIAL.search(part)
                                     and not TRADING_TAIL.search(part)):
            dropped.append(part)
            continue
        kept.append(part)
    return kept, dropped


# --------------------------------------------------------------------------- #
# Building the findings
# --------------------------------------------------------------------------- #

def build(collection: str, batch: str):
    rows = list(records(collection))
    if not rows:
        sys.exit(f"no records matching {collection!r} under {CORPUS} — "
                 "run digitalsf_harvest.py first")

    tally = collections.Counter()
    dropped_names: list[str] = []
    kept_names: list[str] = []
    entries: dict[tuple, dict] = {}
    order: list[tuple] = []

    for rec in sorted(rows, key=lambda r: int(r["id"] or 0)):
        f = rec["fields"]
        title = " ".join(v for v in (first(f, "245", "a"), first(f, "245", "b")) if v)
        notes = read_notes(f)
        date = read_date(f)
        tally["records"] += 1
        tally[f"precision:{date['precision']}"] += 1
        if date["fuzzy_flag"]:
            tally["fuzzy flag"] += 1
        if date["precision"] == "circa" and not date["fuzzy_flag"]:
            tally["imprecise but unflagged"] += 1

        from_title = address_from_title(title)
        from_note = address_from_note(notes["address_note"]) if notes["address_note"] else None
        addr = from_title or from_note
        unnumbered = ""
        if not addr:
            tally["no street number"] += 1
            if notes["block"]:
                tally["  ...but an assessor block"] += 1
            fallback = location_without_number(title, notes)
            unnumbered = fallback["why"]
            addr = {"as_written": fallback["as_written"], "number": "",
                    "street_name": fallback["street_name"],
                    "street_type": fallback["street_type"], "qualified": False}

        conflict = ""
        if unnumbered:
            pass
        elif from_title and from_note:
            same_street = from_title["street_name"] == from_note["street_name"]
            same_number = (from_title["number"].split("-")[0]
                           == from_note["number"].split("-")[0])
            if not (same_street and same_number):
                # Recorded, not adjudicated: some of these are the archivist's
                # typo ("Byrant"), some are a corner property filed under the
                # other street, some are a range against one of its numbers.
                conflict = (f"The catalogue title reads "
                            f"{from_title['as_written']!r}; the archivist's "
                            f"address note reads {from_note['as_written']!r}. "
                            f"The two do not agree.")
            tally["title and note both"] += 1
        elif from_title:
            tally["title only"] += 1
        else:
            tally["address note only"] += 1
        if conflict:
            tally["title/note disagree"] += 1

        streets = [re.sub(r"\.$", "", v[len("Streets--"):])
                   for v in every(f, "650", "a") if v.startswith("Streets--")]
        streets.append(addr["street_name"])
        if from_note:
            streets.append(from_note["street_name"])
        kept, dropped = business_names(title, addr["as_written"], streets)
        kept_names += kept
        dropped_names += dropped

        number, number_range = split_number(addr["number"])
        if addr.get("qualified"):
            number = ""
            tally["number qualified, not an address"] += 1
        key = (addr["street_name"], addr["street_type"], addr["number"], date["date"])
        if key in entries:
            e = entries[key]
            e["_records"].append(rec)
            for name in kept:
                if name not in e["extra"].get("named_in_record", []):
                    e["extra"].setdefault("named_in_record", []).append(name)
            tally["duplicate records folded in"] += 1
            continue

        extra: dict = {}
        if number_range:
            extra["address_range_as_recorded"] = number_range
        if addr["street_name"] and not addr["street_type"]:
            extra["street_type_not_stated"] = True
        extra["date_as_recorded"] = date["as_recorded"]
        if date.get("range"):
            extra["date_range"] = date["range"]
        if date["fuzzy_flag"]:
            extra["fuzzy_date_flag"] = True
        if notes["block"]:
            extra["assessor_block_as_recorded"] = notes["block"]
        if notes["box"]:
            extra["archive_box"] = notes["box"]
        if first(f, "852", "c"):
            extra["shelf"] = first(f, "852", "c")
        if first(f, "300", "a"):
            extra["medium"] = first(f, "300", "a")
        if kept:
            extra["named_in_record"] = list(dict.fromkeys(kept))
        corporate = [v for v in every(f, "610", "a")
                     if "Assessor-Recorder" not in v]
        if corporate:
            extra["corporate_subject_headings"] = sorted(set(corporate))
        topical = [v for v in every(f, "650", "a")
                   if not v.startswith("Streets--")
                   and not v.startswith("Tax assessment")]
        if topical:
            extra["subject_headings"] = sorted(set(topical))
        if notes["other"]:
            extra["record_notes"] = notes["other"]
        # Only worth recording when it says something the title didn't.
        if (from_note and from_title
                and from_note["as_written"] != from_title["as_written"]):
            extra["address_note_as_recorded"] = from_note["as_written"]

        display = addr["as_written"]
        if date["precision"] == "day":
            when = f"on {date['date']}"
        elif date["precision"] in ("month", "year"):
            when = f"in {date['date']}"
        else:
            when = f"at a date the archivist gives as {date['as_recorded']!r}"
        subject = "at" if not unnumbered else "at the location it records as"
        description = (f"The San Francisco Office of the Assessor-Recorder "
                       f"photographed the property {subject} {display} for tax "
                       f"assessment {when}.")
        if kept:
            description += (" The record names " + oxford(kept)
                            + " at the address.")

        entry = {
            "id": "",  # numbered after the whole batch is grouped
            "date": date["date"],
            "date_precision": date["precision"],
            "kind": "photograph",
            "address_as_written": display,
            "description": description,
            "extra": extra,
            "citation": {
                "label": (f"{display}, {year_of(date)}. "
                          + first(f, "524", "a").replace("[Identification of item], ", "")),
                "url": RECORD_URL.format(rec["id"]),
                "corpus_path": rec["page"],
                "locator": locator(rec, notes, first(f, "852", "c")),
            },
            "raw": {"text": raw_span(title, notes)},
            "confidence": ("low" if unnumbered
                           else confidence(date, conflict, from_title, from_note)),
            "resolution": {
                "status": "unresolved",
                "note": (unnumbered + " No street number means no page, per "
                         "'The evidence bar' in research/AGENTS.md."
                         if unnumbered else
                         "Extracted from the catalogue record only; not yet "
                         "checked against sf-eas-addresses."),
            },
            "publish": {"status": "pending"},
            "_records": [rec],
        }
        if conflict:
            entry["conflict"] = conflict
        if number:
            entry["street_number"] = number
        if addr["street_name"]:
            entry["street_name"] = addr["street_name"]
        if addr["street_type"]:
            entry["street_type"] = addr["street_type"]
        entries[key] = entry
        order.append(key)

    findings = []
    for i, key in enumerate(order, 1):
        e = entries[key]
        recs = e.pop("_records")
        e["id"] = f"{batch}-{i:04d}"
        if len(recs) > 1:
            e["extra"]["additional_records"] = [RECORD_URL.format(r["id"])
                                                for r in recs[1:]]
        findings.append(reorder(e))

    tally["findings"] = len(findings)
    tally["distinct addresses"] = len({(k[0], k[1], k[2]) for k in order})
    return rows, findings, tally, kept_names, dropped_names


def oxford(items: list[str]) -> str:
    if len(items) == 1:
        return items[0]
    if len(items) == 2:
        return f"{items[0]} and {items[1]}"
    return ", ".join(items[:-1]) + f" and {items[-1]}"


def year_of(date: dict) -> str:
    """What the citation prints for the date. A range prints as a range."""
    if date["precision"] in ("day", "month", "year"):
        m = YEAR_IN.search(date["date"] or "")
        if m:
            return m.group(1)
    return date["as_recorded"] or "undated"


def locator(rec, notes, shelf) -> str:
    bits = [f"record {rec['id']}"]
    if notes["box"]:
        bits.append(f"Box {notes['box']}")
    if shelf:
        bits.append(shelf)
    if notes["block"]:
        bits.append(f"assessor block {notes['block']}")
    return ", ".join(bits)


def raw_span(title: str, notes: dict) -> str:
    span = title
    if notes["address_note"]:
        span += f" | 500$a: Address. {notes['address_note']}"
    if notes["block"]:
        span += f" | 500$a: Block {notes['block']}"
    return span


def confidence(date, conflict, from_title, from_note) -> str:
    if conflict:
        return "low"
    if date["precision"] in ("day", "month") and from_title and from_note:
        return "high"
    if date["precision"] == "unknown":
        return "low"
    return "medium"


ORDER = ["id", "date", "date_precision", "kind", "address_as_written",
         "street_number", "street_name", "street_type", "description", "extra",
         "citation", "raw", "confidence", "conflict", "resolution", "publish"]


def reorder(entry: dict) -> dict:
    return {k: entry[k] for k in ORDER if k in entry}


# --------------------------------------------------------------------------- #

def main(argv: list[str]) -> int:
    if len(argv) < 2:
        sys.exit(__doc__.split("\n\n")[1].strip())
    collection, batch = argv[0], argv[1]
    report = "--report" in argv
    read_on = next((a for a in argv if re.fullmatch(r"\d{4}-\d{2}-\d{2}", a)),
                   datetime.date.today().isoformat())

    rows, findings, tally, kept, dropped = build(collection, batch)

    if report:
        for k, v in tally.most_common():
            print(f"{v:6}  {k}")
        print(f"\nkept {len(set(kept))} distinct firm names:")
        for n in sorted(set(kept)):
            print(f"  + {n}")
        print(f"\ndropped {len(set(dropped))} distinct fragments "
              f"(personal names, or nothing that reads as a firm):")
        for n in sorted(set(dropped)):
            print(f"  - {n}")
        return 0

    out = ROOT / "findings" / "digitalsf" / f"{batch}.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    existing = json.loads(out.read_text(encoding="utf-8")) if out.exists() else {}
    coverage = {
        "unit": "catalogue records",
        "examined": tally["records"],
        "mentions": tally["records"] - tally["no street number"],
        "remaining": existing.get("coverage", {}).get("remaining", ""),
        "note": existing.get("coverage", {}).get("note", ""),
    }
    out.write_text(json.dumps({
        "source_id": "digitalsf",
        "batch": batch,
        "read_on": read_on,
        "notes": existing.get("notes", ""),
        "coverage": coverage,
        "findings": findings,
    }, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"wrote {out.relative_to(ROOT.parent)} — {len(findings)} findings "
          f"from {len(rows)} records")
    print("`notes`, `coverage.note` and `coverage.remaining` are prose: they "
          "are carried over from the existing file, not generated.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
