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
# The spelled-out type words, as opposed to the abbreviations in the same map.
FULL_TYPE_WORD = {
    "street", "avenue", "boulevard", "way", "court", "terrace", "place",
    "drive", "lane", "alley", "road", "highway", "stairway", "walk", "circle",
    "plaza", "row", "path", "steps",
}

# "1377 Fulton", "2929-2931 24th Street", "547-547A Castro Street", "7 7th Ave".
# Four name tokens, because "415 El Camino Del Mar" needs them, and the
# lowercase particles because the same street is also filed "El Camino del Mar".
NAME_TOKEN = r"(?:[A-Z][A-Za-z'./]*|\d{1,2}(?:st|nd|rd|th)|del|de|la|van|von)"
# The catalogue writes the street type in lower case about as often as not —
# "743 Washington street", "3281 16th st." — and a name token keyed on a
# capital letter cannot see it. That costs twice over: the finding records
# `street_type_not_stated` about a record that stated it, and the orphaned
# "street" left behind in the title blocks the caption name filter, which
# requires every word of a fragment to be capitalized. So the type is matched
# in its own right, in lower case, as an optional last token.
LOWER_TYPE = "(?:%s)" % "|".join(
    sorted(TYPE_ABBR, key=len, reverse=True))
TITLE_ADDR = re.compile(
    rf"\b(\d{{1,5}}[A-Za-z]?(?:\s*-\s*\d{{1,5}}[A-Za-z]?)?)\s+"
    rf"({NAME_TOKEN}(?:\s+{NAME_TOKEN}){{0,3}}\b(?:\s+{LOWER_TYPE}\b\.?)?)")

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


# A caption's own words that parse as "<number> <street name>" and are not
# addresses. Curated from `--report` over SFP 162, where a subject file's prose
# supplies them by the dozen: a date ("23 April"), a fire company ("2 Engine",
# "1 Fire House"), a numbered vehicle ("32 Streetcar"), and a venue named for
# its street number ("365 Club" is the nightclub at 365 Market). The dossier's
# existing guard — a street number equal to the record's own year — catches a
# different half of the same problem; this is the half with no year in it.
NOT_A_STREET_NAME = {
    "JANUARY", "FEBRUARY", "MARCH", "APRIL", "MAY", "JUNE", "JULY", "AUGUST",
    "SEPTEMBER", "OCTOBER", "NOVEMBER", "DECEMBER",
    "ENGINE", "ENGINE COMPANY", "FIRE HOUSE", "FIREHOUSE", "TRUCK COMPANY",
    "STREETCAR", "STREET CAR", "CLUB", "RESTAURANT", "THEATRE RESTAURANT",
    "P.M", "A.M", "B.C", "STAR", "LINE",
    # "3 Residences 236 & 222 Moncada Way, 90 Cedro Avenue" counts the houses
    # in the frame before it gives any of their addresses.
    "RESIDENCE", "RESIDENCES", "HOUSES", "VIEWS",
}


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
    if not stype and name.upper() in NOT_A_STREET_NAME:
        return None
    # "429 Montgomery street." keeps a full stop that is the end of the
    # catalogue's sentence, not part of the address, and it reaches the page in
    # the middle of one. An abbreviation's own period ("16th st.") stays.
    if tokens[-1].endswith(".") and tokens[-1].rstrip(".").lower() in FULL_TYPE_WORD:
        tokens[-1] = tokens[-1].rstrip(".")
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
# "Bank of Canton located at 743 Washington street" and "Cadillac Hotel located
# at 380 Eddy street" leave the participle behind once the address goes. It is
# the caption placing the building, not part of what the building is called —
# and left on, it fails the all-capitalized test and takes the name with it.
TRAILING_LOCATIVE = re.compile(
    r"\s+(?:located|situated|shown|pictured|seen)$", re.I)
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


def business_names(title: str, address_span: str, streets: list[str],
                   policy: str = "", districts: list[str] | None = None
                   ) -> tuple[list[str], list[str]]:
    """Split a title's tail into (firm names kept, fragments dropped).

    Default is to keep: a fragment left over after the address is removed is
    usually the business whose sign is in the photograph, and that is the fact
    worth having. Drop on positive evidence — a credential, a curated personal
    name, another address, a cross street, a bare descriptor. `streets` is the
    record's own `Streets--<name>` headings, which is how a bare "Mission" or
    "Balboa" left behind by the address match gets recognized as a street;
    `districts` is its `Districts--<name>` headings, which does the same for a
    neighbourhood. Worden captions end "in Ingleside Terraces" on every plate,
    and `terrace` is a building noun, so without this the district is kept as
    the building's name on sixty pages.
    """
    tail = PARENTHETICAL.sub(" ", title)
    if address_span and address_span in tail:
        tail = tail.replace(address_span, " ")
    tail = re.sub(r"\s+", " ", tail).strip(" ,.-")
    bare_streets = {s.lower().rstrip(".") for s in streets if s}
    bare_places = {d.lower().rstrip(".") for d in (districts or []) if d}

    kept: list[str] = []
    dropped: list[str] = []
    for part in split_fragments(tail):
        # Removing the address can leave two joins stacked up — "Corner of
        # 16th Street and 3rd Street" minus "16th Street" is "Corner of and
        # 3rd Street" — so trim until the fragment stops shrinking.
        part = part.strip(" ,.-&")
        while True:
            trimmed = TRAILING_LOCATIVE.sub(
                "", TRAILING_JOIN.sub(
                    "", TRAILING_CROSS.sub(
                        "", LEADING_JOIN.sub("", part)))).strip(" ,.-&")
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
        # "Residence in Ingleside Terraces" minus the address is the district
        # the record is already indexed under, not a building.
        if bare_places and re.sub(r"^(?:\w+\s+)*?in\s+", "", low) in bare_places:
            continue
        if low in bare_places:
            continue
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
        if policy == "named-buildings-only":
            if not is_named_building(part):
                dropped.append(part)
                continue
            part = CAPTION_PREFIX.sub("", part).strip(" ,.&-")
        kept.append(part)
    return kept, dropped


# --------------------------------------------------------------------------- #
# What a photograph in a collection *is*
#
# The description has to say who made the record and why, because that is the
# fact the catalogue carries and it differs completely per collection: SFP 23
# is the Assessor-Recorder photographing a building in order to tax it, SFP 22
# is one commercial photographer's plate negatives, SFP 78 is a community
# collecting project. Getting this from a hardcoded sentence — which is what
# this tool did until the second collection was read — attributes every
# photograph in the archive to the Assessor-Recorder.
#
# So: one entry per collection, added when that collection is read, and an
# unknown collection is a hard stop rather than a default. A wrong attribution
# on a page is far more expensive than an error message here.
#
# `{at}` is "at" or "at the location it records as"; `{display}` the address as
# written; `{when}` the date phrase. Say what the record is, not where it is
# held — the Sources footer is the attribution (RUNBOOK.md, "Rules that catch
# publishers out").
# --------------------------------------------------------------------------- #

COLLECTION_VOICE = {
    "SFP 23": ("The San Francisco Office of the Assessor-Recorder photographed "
               "the property {at} {display} for tax assessment {when}."),
    # Agency photography of the redevelopment project areas. Much of what it
    # shows was cleared soon afterwards, so the date is doing real work here:
    # it is often the last record of a building at that number.
    "SFH 371": ("The San Francisco Redevelopment Agency photographed the "
                "property {at} {display} {when}."),
    # The History Center's own subject file: an artificial collection assembled
    # folder by folder from many photographers and donors, so there is no one
    # body that made these pictures and the sentence must not name one. What is
    # true of every record is that a dated photograph of the address survives.
    "SFP 162": ("Photographed {at} {display} {when}."),
    # One commercial photographer's glass plates. Worden was hired to
    # photograph the Ingleside Terraces and Jordan Park residence parks as they
    # were built, so the collection is a dated, house-by-house record and the
    # photographer is the fact the catalogue carries about who made it.
    "SFP 22": ("Willard E. Worden photographed the property {at} {display} "
               "{when}."),
}


# How much of a title's tail is a business name at all.
#
# SFP 23 titles are "address, shop sign" and the default — keep the leftover
# fragment unless something says it is a person — is right for them. SFH 371's
# are narrative captions: "1249 Scott Street home on dolly being pulled by
# bulldozer". Run the default over those and 140 "firm names" come back, of
# which most are caption prose ("home on dolly", "under construction",
# "Adjacent") and four name individuals at public ceremonies, which the privacy
# limits bar outright.
#
# So a caption collection uses `named-buildings-only`: keep a fragment only if
# every word is capitalized, it carries no digits, and one of its capitalized
# words is a building noun. That keeps Miyako Hotel, Woolf House Apartments and
# St. Patrick's Catholic Church; it drops every person and every fragment of
# caption. It also drops real names buried in lowercase prose ("Japantown
# bakery Benkyodo Company"), and that trade is deliberate — under "The evidence
# bar" scarcity raises the bar, and a false keep here is a privacy failure.
# Whether a record that gives no street number is worth keeping as an
# unresolved finding.
#
# The default is to keep it: SFH 371 is 2,421 records photographing a handful of
# project areas, its unnumbered captions locate real buildings that were about
# to be cleared, and 170 stubs are a cheap record of a haystack already searched.
#
# SFP 162 is the opposite shape. It is the History Center's general subject file
# — 34,738 records of parades, ferries, wildflowers and mayors, of which 1,435
# carry a street number. Keeping the rest produces 9,000 findings that say "the
# record names no street number" about a photograph of Stow Lake, in a file the
# next agent has to read past. The coverage block already records that the whole
# collection was examined, which is the thing worth keeping. So: `skip-unnumbered`
# for a subject file, where the unnumbered majority is not about buildings at all.
COLLECTION_UNNUMBERED_POLICY = {
    "SFP 162": "skip-unnumbered",
    # Same shape as SFP 162 for the same reason: 330 of SFP 22's 433 records
    # give no street number, and they are the photographer's miscellany — Camp
    # McCoy, Y.M.C.A. portraits, views across Brisbane, "Ingleside Terraces
    # residence interior" with no way to know which house. Not buildings.
    "SFP 22": "skip-unnumbered",
}

COLLECTION_NAME_POLICY = {
    "SFH 371": "named-buildings-only",
    # Subject-file titles are narrative captions in the same way SFH 371's are
    # — "Man standing in front of Malvina Coffee Shop in North Beach" — so the
    # same policy applies for the same reason.
    "SFP 162": "named-buildings-only",
    # "Residence of Mrs. Henrietta Lehe, 15 Cerritos Avenue" — the tail of a
    # Worden caption is the owner about as often as it is anything, and owners
    # are barred outright.
    "SFP 22": "named-buildings-only",
}

BUILDING_NOUN = {
    "hotel", "apartment", "apartments", "house", "church", "school", "market",
    "garage", "company", "galleria", "ywca", "ymca", "theatre", "theater",
    "hall", "club", "restaurant", "cafe", "bakery", "hardware", "store",
    "stores", "center", "centre", "building", "buildings", "tower", "inn",
    "library", "temple", "mission", "bank", "works", "plant", "factory",
    "warehouse", "terrace", "court", "plaza", "commons", "mall", "cathedral",
    "corporation",
    "synagogue", "hospital", "laundry", "cleaners", "pharmacy", "tavern",
    # Each of these completes a family already in the list rather than opening
    # a new one: institute and society sit with library and temple, brewery
    # with plant and factory, bar and saloon with tavern, cafeteria with cafe,
    # mortuary with cleaners, bookstore with store.
    "institute", "society", "brewery", "saloon", "bar", "mortuary",
    "cafeteria", "bookstore",
}
SMALL_WORD = {"of", "the", "at", "and", "in", "on", "for", "de", "la", "du",
              "des", "von", "van", "&", "-"}


# A record whose subject is a person, with no street number in it, is a
# photograph of people rather than of a place. It can never become a page fact
# — no number, no page — so keeping it buys nothing and carries named
# individuals into the repository, which "Privacy — hard limits" in the root
# AGENTS.md bars at extraction time, not at publication. Detected by a MARC 600
# personal-name subject or a personal title in the caption. Records that *do*
# carry a street number are unaffected: their address is the fact, and the
# name filter already keeps people out of `named_in_record`.
PERSON_MARKER = re.compile(
    r"\b(?:Mayor|Supervisor|Commissioner|Reverend|Rev\.|Miss|Mr\.|Mrs\.|Ms\.|"
    r"Dr\.)\s+[A-Z]", re.I)


def people_not_a_place(title: str, fields) -> bool:
    return bool(every(fields, "600", "a")) or bool(PERSON_MARKER.search(title))


# An event at a building is not the building's name.
EVENT_TAIL = re.compile(r"\b(?:ceremony|opening|meeting|dedication|groundbreaking)$", re.I)

# What a subject-file caption puts in front of the name. "Exterior of Ernie's
# Restaurant" and "Former North Beach Branch Library" are the caption's framing,
# not part of what the building is called; left on, they reach the page as the
# archive describing its own photograph.
# The second shape is the same framing with a *part of the building* in front
# of it — "Main entrance to the Marines' Memorial Club", "Courtyard at the San
# Francisco Art Institute", "Lobby of the Hotel Turpin". None of these words is
# a BUILDING_NOUN, so stripping them can never take a name's own head noun.
CAPTION_PART = (
    r"entrances?|courtyard|lobby|lobbies|views?|facades?|doors?|doorway|"
    r"floors?|porch|steps|stairway|staircase|details?|signs?|roof|windows?|"
    r"yard|garden|driveway|corridor|hallway|basement|interiors?|exteriors?")
CAPTION_PART_QUALIFIER = (
    r"Main|Front|Rear|Side|Back|Aerial|Exterior|Interior|Modern|Upper|Lower|"
    r"First|Second|Third|Fourth|Ground|Top|Close|Partial|Corner|Original|"
    r"New|Old|North|South|East|West|Northwest|Northeast|Southwest|Southeast")
CAPTION_PREFIX = re.compile(
    r"^(?:Exterior|Interior|Front|Rear|Side|View|Views|Construction|"
    r"Demolition|Remodeling|Renovation|Warehouse|Site)\s+of\s+(?:the\s+)?"
    rf"|^(?:(?:{CAPTION_PART_QUALIFIER})\s+)?(?:{CAPTION_PART})\s+"
    r"(?:on\s+top\s+of|in\s+front\s+of|of|at|to|on|in|inside|outside)"
    r"\s+(?:the\s+)?"
    r"|^(?:Former|Old|New)\s+(?=[A-Z])", re.I)


def is_named_building(part: str) -> bool:
    """A proper name for a building, not a scrap of caption and not a person."""
    part = CAPTION_PREFIX.sub("", part).strip(" ,.&-")
    tokens = part.replace("&", " & ").split()
    if not tokens or any(any(c.isdigit() for c in tok) for tok in tokens):
        return False
    if EVENT_TAIL.search(part.strip().rstrip(".")):
        return False
    # Removing the address from the middle of a fragment leaves two joining
    # words back to back — "Building at 3rd and Howard" becomes "Building at
    # and Howard" — which is a cross street, not a name.
    lowered = [w.strip(".,").lower() for w in tokens]
    if any(a in SMALL_WORD and b in SMALL_WORD
           for a, b in zip(lowered, lowered[1:])):
        return False
    has_noun = False
    distinguishing = False
    for tok in tokens:
        word = tok.strip(".,")
        if not word:
            continue
        if word.lower() in SMALL_WORD:
            continue
        if not word[0].isupper():
            return False
        if word.lower().rstrip("'s") in BUILDING_NOUN or word.lower() in BUILDING_NOUN:
            has_noun = True
        else:
            distinguishing = True
    # "Building", "House", "Public Library" name no particular one. A fragment
    # with nothing but the noun in it is the caption's common noun, and on a
    # page it says only that the address had a building on it.
    return has_noun and distinguishing


def voice_for(collection: str) -> str:
    try:
        return COLLECTION_VOICE[collection]
    except KeyError:
        sys.exit(
            f"no description template for {collection!r}.\n"
            "Add one to COLLECTION_VOICE in this file first: it says what a\n"
            "photograph in this collection is and who made it, and there is no\n"
            "safe default — falling back on another collection's sentence\n"
            "attributes the whole batch to the wrong body. Known collections:\n"
            + "".join(f"  {k}\n" for k in sorted(COLLECTION_VOICE)))


# --------------------------------------------------------------------------- #
# Building the findings
# --------------------------------------------------------------------------- #

def build(collection: str, batch: str):
    voice = voice_for(collection)
    policy = COLLECTION_NAME_POLICY.get(collection, "")
    skip_unnumbered = (COLLECTION_UNNUMBERED_POLICY.get(collection)
                       == "skip-unnumbered")
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
        # "Miss Chinatown 1967 Marilyn Lew" parses as number 1967 on a street
        # called Marilyn Lew. The dossier's rule for this is that a street
        # number equal to the record's own year is not an address; with no
        # street type stated there is nothing else holding it up.
        if (from_title and not from_title["street_type"]
                and from_title["number"] == year_of(date)):
            tally["street number is the record's year, not an address"] += 1
            from_title = None
        addr = from_title or from_note
        unnumbered = ""
        if not addr and people_not_a_place(title, f):
            tally["people, not a place — skipped"] += 1
            continue
        if not addr:
            tally["no street number"] += 1
            if notes["block"]:
                tally["  ...but an assessor block"] += 1
            if skip_unnumbered and not notes["block"]:
                tally["  ...and skipped, per COLLECTION_UNNUMBERED_POLICY"] += 1
                continue
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
        districts = [re.sub(r"\.$", "", v[len("Districts--"):])
                     for v in every(f, "650", "a") if v.startswith("Districts--")]
        kept, dropped = business_names(title, addr["as_written"], streets, policy,
                                       districts)
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
        if first(f, "490", "a"):
            extra["archival_series"] = first(f, "490", "a")
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
        elif date["precision"] == "unknown":
            # "at a date the archivist gives as 'undated'" says nothing, and it
            # says it in the archive's voice. `date_precision` carries this.
            when = ""
        else:
            # The catalogue's own hedge reads as plain English on its own —
            # "circa 1862", "between 1943 and 1958", "not before 1968" — so use
            # it as the phrase rather than framing it as something a cataloguer
            # said. A page body never names where a fact came from.
            when = date["as_recorded"]
        at = "at" if not unnumbered else "at the location it records as"
        description = re.sub(r"\s+([.,])", r"\1",
                             voice.format(at=at, display=display, when=when))
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
        # A record skipped as a photograph of people never reached the address
        # test, so it is not a mention either.
        "mentions": (tally["records"] - tally["no street number"]
                     - tally["people, not a place — skipped"]),
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
