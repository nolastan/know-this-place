#!/usr/bin/env python3
"""Turn one or more DigitalSF archival collections into a findings file.

    python3 research/tools/digitalsf_extract.py "SFP 23" sfp-23
    python3 research/tools/digitalsf_extract.py "SFP 23" sfp-23 --report
    python3 research/tools/digitalsf_extract.py "(SFH 61),(SFP 83)" tail

The first argument matches against `524$a`, which is the preferred citation and
also the batch unit for this source — see research/sources/digitalsf.md. The
second names the output file, `research/findings/digitalsf/<batch>.json`.
`--key 982` matches the digital series in `982$a` instead, which is the only
way to reach the 1,678 records that carry no `524$a` at all.
`--report` prints the coverage counts and the address strings it kept and
dropped, without writing anything; that is the pass you read before committing.

**A batch may be several collections.** Comma-separate the selectors and every
per-collection setting below — the description template, the name policy, the
unnumbered policy — is resolved per record from the collection that record
matched, not once for the run. That is what makes the long tail readable: 36
of DigitalSF's collections hold between one and nineteen addressed records
each, and one findings file per collection would be 36 files, 36 register
lines and 36 dossier entries for 188 candidate addresses.

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

def records(selectors: list[str], key: str = "524"):
    """Yield {id, oai, page, fields, collection} per unique record selected.

    `selectors` are matched as substrings of the record's `key$a`; a record is
    yielded once, tagged with the first selector that matched it, so a batch
    spanning several collections still knows which one each record came from.

    Deduplicates on the OAI identifier: the sets overlap, so a record reached
    through `Photographs` is usually also in `city` and `sfhistory`.

    `key` is the MARC tag whose `$a` names the batch. It is `524` — the
    preferred citation — for every catalogued collection, and that is the batch
    unit this source is organised on. **1,678 records carry no `524$a` at
    all**, so a run keyed on the citation string can never reach them; those
    are selected on `982$a`, which names the digital series instead. See the
    Coverage note in research/sources/digitalsf.md.
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
            cited = first(fields, key, "a")
            matched = next((sel for sel in selectors if sel in cited), None)
            if matched is None:
                continue
            cf = mrc.find(f"{M}controlfield[@tag='001']")
            yield {"id": (cf.text or "") if cf is not None else "",
                   "oai": oai,
                   "page": str(pathlib.Path(page).relative_to(ROOT.parent)),
                   "collection": matched,
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
# A decade's trailing "s" is a word character, so `\b1920\b` does not match
# inside "1920s" and every decade date fell through to the 269$a fallback
# below — as a *firm year*. The decade is matched in its own right.
YEAR_IN = re.compile(r"\b(1[89]\d\d|20[0-2]\d)s?\b")
DECADE_PHRASE = re.compile(
    r"^(circa|probably|possibly|about)?\s*"
    r"(\d{4}s(?:\s*[-–]\s*\d{4}s)?)$", re.I)


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
        elif raw:
            # `260$c` said something and it names no year: "19--", "18--",
            # "undated", "n.d.". 269$a still carries a four-digit number for
            # these — 1900 for "19--", on 731 records — and it is the
            # catalogue's own floor value for an unspecified century, not a
            # date anybody recorded. Taking it writes a year the archivist
            # never claimed, and 1900 is the one year this project is least
            # able to tell from a real one. See the `269$a` caution in
            # research/sources/digitalsf.md.
            out.update(date=raw, precision="unknown")
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
    # EAS files Clinton Park as street_name CLINTON, street_type PARK, and
    # `seed_pages.STREET_TYPE_WORD` — which this map was copied from — has
    # carried "PARK" all along. Without it "2 Clinton Park" comes back as a
    # street the city does not have.
    "park": "PARK",
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
# Abbreviations that belong to a street's name rather than ending a sentence.
NAME_ABBREV = {"st", "mt", "ft", "dr", "mrs", "mr", "ms", "ave", "av", "blvd",
               "ln", "ct", "pl", "rd", "ter", "cir", "hwy", "aly"}
# The spelled-out type words, as opposed to the abbreviations in the same map.
FULL_TYPE_WORD = {
    "street", "avenue", "boulevard", "way", "court", "terrace", "place",
    "drive", "lane", "alley", "road", "highway", "stairway", "walk", "circle",
    "plaza", "row", "path", "steps", "park",
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
# A run of buildings is printed with a word between the two numbers — "610 to
# 624 Anza Street", "648 thru 622 Jerrold Avenue", "Piers 21 through 17". A
# pattern that only knows the hyphen matches the *second* number and files the
# photograph on it, silently losing the first: three Cook Street findings came
# back on 94 and 73, which are the abbreviated high ends of 194 and 173. It is
# matched here so both numbers are seen; `build` then writes one finding each,
# per "A row of buildings is not a range" in research/LESSONS.md.
TITLE_RUN = r"(?:\s+(?:to|thru|through)\s+\d{1,5}[A-Za-z]?)?"
TITLE_ADDR = re.compile(
    rf"\b(\d{{1,5}}[A-Za-z]?(?:\s*-\s*\d{{1,5}}[A-Za-z]?)?{TITLE_RUN})\s+"
    rf"({NAME_TOKEN}(?:\s+{NAME_TOKEN}){{0,3}}\b(?:\s+{LOWER_TYPE}\b\.?)?)")
RUN_SPLIT = re.compile(r"^(\d{1,5}[A-Za-z]?)\s+(?:to|thru|through)\s+"
                       r"(\d{1,5}[A-Za-z]?)$", re.I)

# A number introduced by "No." or "#" is the thing's own serial, not a street
# number: "Pumping Station No. 2", "Chinese San Francisco No. 9", "Ridgepoint
# No. 2 Elementary School", "Lantern Slide No. 55 A". 140 titles corpus-wide.
SERIAL_BEFORE = re.compile(r"(?:\bNos?\.?|#)\s*$", re.I)

# `Address. Box 3; Mission, 3232-3234.`  `Address. Box 1, Cortland 415.`
# `Address. Fulton, 1377.`               `Address. Box 4; 2900-2904, 24th st.`
ADDR_NOTE = re.compile(r"^\s*(?:SFP\s*\d+\.?\s*)?Address\.?\s*(.*?)\s*\.?\s*$", re.I)
BLOCK_NOTE = re.compile(
    r"^\s*(?:SFP\s*\d+\.?\s*)?Block\.?\s*(?:Box\s*#?\s*([\w]+)\s*[;,])?\s*"
    r"Block\s*#?\s*(\d+)", re.I)
BOX_PREFIX = re.compile(r"^\s*Box\s*#?\s*([\w]+)\s*[;,]\s*", re.I)
DONOR_NOTE = re.compile(r"^\s*Donor's metadata notes:\s*(.*)$", re.I)
# The tail the donor appended: a street address, then optionally a city, a
# state and a ZIP, each in its own comma-separated slot. Peeled off from the
# end rather than matched in one pattern, because the slots are optional in
# every combination and the street itself can be numbered ("2500 16th St"),
# which is what a `\d+\s+[A-Z]` shape misses.
DONOR_TAIL_ZIP = re.compile(r"^\d{5}(?:-\d{4})?$")
DONOR_TAIL_PLACE = re.compile(r"^(?:CA|California|[A-Z][A-Za-z' .]{2,30})$")
DONOR_TAIL_ADDRESS = re.compile(
    rf"^\d{{1,5}}[A-Za-z]?(?:\s*-\s*\d{{1,5}}[A-Za-z]?)?\s+"
    rf"{NAME_TOKEN}(?:\s+{NAME_TOKEN}){{0,3}}\.?$")
NUMBERISH = r"\d{1,5}[A-Za-z]?(?:\s*-\s*\d{1,5}[A-Za-z]?)?"
NOTE_STREET_FIRST = re.compile(rf"^(.*?)[;,]?\s*({NUMBERISH})$")
NOTE_NUMBER_FIRST = re.compile(rf"^({NUMBERISH})\s*[;,]\s*(.+)$")

BLOCK_PHRASE = re.compile(r"\b\d{1,5}\s+block\b", re.I)
# "South of 500 Bayshore Boulevard" and "Rear of 1069 Market Street" name a
# number without being at it. The number still locates the photograph, so the
# finding is worth keeping — but it does not get a `street_number`.
QUALIFIED = re.compile(
    r"((?:south|north|east|west|rear|front|corner|opposite|near)\s+of|near|"
    r"opposite|(?:taken|photographed|shot|seen|view)\s+from|"
    r"towards?|across\s+from)\s+$", re.I)
# The same thing said after the number instead of before it. The BART
# construction slides are photographs of Market Street with a tower named for
# scale — "a construction crane with auger in the middle of the street. 555
# Market in background" — and the building is not what the record shows.
QUALIFIED_AFTER = re.compile(
    r"^\s*,?\s*(?:in\s+(?:the\s+)?(?:background|distance)|"
    r"in\s+the\s+rear|behind)\b", re.I)


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
    if out:
        out[-1] = out[-1].rstrip(".")
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
    # "4 Mile House Restaurant at 3rd and Yosemite" — the restaurant is named
    # for its distance from the city, and the distance parses as a number.
    "MILE HOUSE RESTAURANT", "MILE HOUSE",
    # Aircraft and machinery in a photograph carry a model number and a name,
    # and the pair reads exactly like an address: "Beechcraft 35 Bonanza",
    # "John Deere 93 Series A crawler tractor". The hyphenated designations
    # are caught by their hyphen; these are not hyphenated.
    "BONANZA", "SERIES A", "SERIES", "ALBATROSS", "HERCULES", "SEAGUARD",
}


def address_from_title(title: str, year_guard: bool = False,
                      plate_numbers: bool = False) -> dict | None:
    """The first exact street number in a title. A block is not an address.

    Parentheses hold a second address rather than this one — "4001-4005, Judah
    (1411 45th Ave.)" is on Judah — so they come out before the match.
    """
    title = QUOTED_SPAN.sub(" ", PARENTHETICAL.sub(" ", title))
    if BLOCK_PHRASE.search(title):
        return None
    # A collection that numbers its plates prints that number where an address
    # would go. All 14 of SFP 84's title-initial numbers are stereograph
    # numbers — "877 A view of San Francisco Bay", "1704 Mission Church,
    # Mission Dolores", "3022 Ferry-boat entering Oakland slip" — and none of
    # its real addresses is title-initial; they are all mid-caption ("Caswell
    # and Company building at 412 Sacramento Street"). It is a per-collection
    # switch because 779 titles corpus-wide open with a genuine street number.
    if plate_numbers:
        title = re.sub(r"^\s*\d{1,5}\.?\s+", " ", title)
    for m in TITLE_ADDR.finditer(title):
        # "Sikorsky HH-52A Seaguard", "Coast Guard HC-130B Hercules",
        # "Grumman HU-16 Albatross": the number is the tail of a hyphenated
        # model designation, and the word after it is the model's name. The
        # word boundary the pattern anchors on sits inside the designation.
        #
        # A colon before it is a clock time, and the minutes read as a number
        # over a street: "at 1:00 P. M." yields *00 P. M*, and the meridiem is
        # on NOT_A_STREET_NAME in a spelling that a caption writing "P. M."
        # does not match.
        if m.start() and title[m.start() - 1] in "-:":
            continue
        if SERIAL_BEFORE.search(title[:m.start()]):
            continue
        break
    else:
        return None
    if m is None:
        return None
    number, rest = m.group(1), m.group(2)
    second = ""
    run = RUN_SPLIT.match(number)
    if run:
        number, second = run.group(1), complete_high_end(run.group(1),
                                                         run.group(2))
    qualifier = (QUALIFIED.search(title[:m.start()])
                 or QUALIFIED_AFTER.match(title[m.end():]))
    # Trim trailing words that belong to the next clause rather than the street
    # name: "800 Irving Street at 9th Avenue" and "1231 9th Avenue, B&E Deli".
    tokens = rest.split()
    # A full stop inside the matched span ends the catalogue's sentence, and
    # the capitalized word after it starts a new one: "949 Grant Avenue. Signs
    # for various products in the window" and "520 Montgomery. Fire apparatus
    # parked in the street" are each an address followed by prose. What a
    # sentence-ending stop is not is a name's own abbreviation — "St. Francis
    # Way", "Mt. Vernon Avenue", "Mayor Edwin M. Lee Avenue" — so those, and
    # bare initials, carry on.
    for i, tok in enumerate(tokens):
        stem = tok[:-1]
        if (tok.endswith(".") and len(stem) > 1
                and stem.lower() not in NAME_ABBREV):
            tokens = tokens[:i + 1]
            break
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
    # "1958 Bell 47G-2 N977B Helicopter" is a year and a make, not an address.
    # The standing guard only catches a number equal to *this* record's year,
    # and a caption is free to date something else. But the same shape is a
    # real address about as often — "House of Prime Rib, 1906 Van Ness" — so
    # refusing it outright costs more than it saves. It is refused only where
    # the text is a donor's or photographer's free prose rather than a
    # catalogued "<name>, <address>" title, which is where the equipment
    # captions live.
    if year_guard and not stype and re.fullmatch(r"1[89]\d\d|20[0-2]\d", number):
        return None
    # "429 Montgomery street." keeps a full stop that is the end of the
    # catalogue's sentence, not part of the address, and it reaches the page in
    # the middle of one. An abbreviation's own period ("16th st.") stays.
    if (tokens[-1].endswith(".")
            and tokens[-1].rstrip(".").lower() not in NAME_ABBREV):
        tokens[-1] = tokens[-1].rstrip(".")
    as_written = f"{number} {' '.join(tokens)}"
    if qualifier:
        phrase = qualifier.group(0).strip(" ,")
        as_written = (f"{as_written} {phrase}" if QUALIFIED_AFTER.match(phrase)
                      else f"{phrase} {as_written}")
    out = {"as_written": as_written, "number": number, "street_name": name,
           "street_type": stype, "qualified": bool(qualifier)}
    if second:
        out["second_number"] = second
        out["printed_as"] = f"{run.group(1)} {m.group(0)[len(run.group(1)):].strip()}"
    return out


def complete_high_end(low: str, high: str) -> str:
    """('183', '94') -> '194'. A survey drops the digits that do not change.

    Same rule `resolve_eas.py` applies to a hyphenated range: "1843-47" means
    1843 to 1847. Here it is the Bureau of Engineering writing "183 to 94 Cook
    Street" for 183 to 194, and reading 94 literally files the photograph on a
    number a block away — or on nothing at all.
    """
    lo, hi = re.sub(r"\D", "", low), re.sub(r"\D", "", high)
    if not lo or not hi or len(hi) >= len(lo):
        return high
    filled = lo[:len(lo) - len(hi)] + hi
    return filled if int(filled) >= int(lo) else high


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


def split_donor_note(note: str) -> tuple[str, str]:
    """(the descriptive half, the geocode the donor appended).

    The geocode is peeled off the end: a ZIP, then a state or city, then the
    street address itself, each optional. Anything left is what the donor said
    about the photograph.
    """
    slots = [c.strip() for c in re.split(r"\s*[.,]\s*", note) if c.strip()]
    tail: list[str] = []
    while slots and (DONOR_TAIL_ZIP.match(slots[-1])
                     or DONOR_TAIL_PLACE.match(slots[-1])):
        tail.insert(0, slots.pop())
    if not (slots and DONOR_TAIL_ADDRESS.match(slots[-1])):
        return note, ""
    tail.insert(0, slots.pop())
    # Everything before the address slot, in the note's own words. Rebuilt from
    # the note rather than from `slots` so the descriptive half keeps its
    # punctuation for address_from_title to read.
    cut = note.rfind(tail[0])
    return note[:cut].rstrip(" .,"), ", ".join(tail)


def address_from_donor_note(note: str) -> tuple[dict | None, str]:
    """(the address the donor states in the descriptive half, the geocode).

    When no geocode can be peeled off the end, the note is **not** parsed for
    an address at all: without the split there is no way to tell the donor
    naming what the photograph shows from the donor geocoding where it was
    taken, and COLLECTION_DONOR_ADDRESS says why the second is not an address.
    """
    descriptive, geocode = split_donor_note(note)
    if not geocode:
        return None, ""
    return address_from_title(descriptive, year_guard=True), geocode


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
    out = {"address_note": "", "block": "", "box": "", "donor_note": "",
           "other": []}
    for note in every(fields, "500", "a"):
        m = DONOR_NOTE.match(note)
        if m:
            out["donor_note"] = m.group(1).strip()
            continue
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
# The title of the work, in quotes, in front of what it is on: `"200 Years of
# Resistance" on Uganda Liquors exterior`. Without this the quoted half is
# split off at the comma and the rest reads as a firm called " of Resistance".
QUOTED_WORK = re.compile(r'^"[^"]*"\s*(?:on|at|in)?\s*', re.I)
# "Phoenix Imports building mural", "French-American International School
# mural" — the caption saying what is on the building, not part of its name.
MURAL_TAIL = re.compile(r"\s+(?:building\s+)?murals?$", re.I)
# Who is standing in the frame, in front of the building the caption is about:
# "Two people outside of Bernal Heights Branch Library". The people are barred
# anyway; what this rescues is the building behind them.
PEOPLE_FRAME = re.compile(
    r"^(?:\w+\s+){0,3}?(?:people|persons?|man|men|woman|women|child|children|"
    r"crowd|customers|shoppers|pedestrians)\b[^,]*?\s+(?:of|from)\s+(?:the\s+)?",
    re.I)

# A fragment can only be a location once it starts this way, whatever follows.
LOCATIONAL_JOIN = re.compile(
    r"^(?:near|corner\s+of|[NSEW]{1,2}\s+corner\s+of|"
    r"(?:north|south|east|west|northwest|northeast|southwest|southeast)"
    r"\s+(?:corner\s+)?of)\s+", re.I)
LEADING_JOIN = re.compile(
    r"^(?:at|and|on|in|of|to|near|the\s+rear\s+of|rear\s+of|south\s+of|north\s+of|"
    r"east\s+of|west\s+of|corner\s+of|[NSEW]{1,2}\s+corner\s+of)\s+"
    # The article after the join word goes with it. On its own the article
    # stays: a firm's "The" is part of its name — "The Knittery".
    r"(?:the\s+)?", re.I)
# The same words at the end, once the address they introduced has been removed:
# "Residence at 531 College Avenue" leaves "Residence at".
TRAILING_JOIN = re.compile(r"\s+(?:at|and|on|in|of|to|now)$", re.I)
# "Bank of Canton located at 743 Washington street" and "Cadillac Hotel located
# at 380 Eddy street" leave the participle behind once the address goes. It is
# the caption placing the building, not part of what the building is called —
# and left on, it fails the all-capitalized test and takes the name with it.
TRAILING_LOCATIVE = re.compile(
    r"\s+(?:located|situated|shown|pictured|seen)$", re.I)
CAPTION_PART = (
    r"entrances?|courtyard|lobby|lobbies|views?|facades?|doors?|doorway|"
    r"floors?|porch|steps|stairway|staircase|details?|signs?|roof|windows?|"
    r"yard|garden|driveway|corridor|hallway|basement|interiors?|exteriors?")
CAPTION_PART_QUALIFIER = (
    r"Main|Front|Rear|Side|Back|Aerial|Exterior|Interior|Modern|Upper|Lower|"
    r"First|Second|Third|Fourth|Ground|Top|Close|Partial|Corner|Original|"
    r"New|Old|North|South|East|West|Northwest|Northeast|Southwest|Southeast")

# What the caption says happened to the building, left stranded when the
# address between it and the name is removed: "Gump's at 250 Post Street closed"
# becomes "Gump's at closed". Trimmed here, the join word behind it goes too.
TRAILING_STATE = re.compile(
    r"\s+(?:closed|vacant|demolished|razed|burned|remodeled|"
    r"(?:being\s+|prior\s+to\s+|before\s+)?demolition|under\s+construction)$", re.I)
# The part of the building the caption framed, at the end instead of the front:
# "Grand Theater entrance", "Hillsdale Hotel front windows". CAPTION_PART holds
# no building noun, so this can never take a name's own head word.
TRAILING_PART = re.compile(rf"\s+(?:{CAPTION_PART_QUALIFIER}\s+)?(?:{CAPTION_PART})$", re.I)
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
    # Left behind by a caption rather than naming anything: a common noun for
    # the structure, or a phrase describing the frame.
    "garage", "mural", "murals", "street view", "building corner", "and",
    "exterior", "interior", "hotel", "hotels", "building", "buildings",
    "storefront", "storefronts", "sign", "signs", "contact sheet",
    "mural on medical building", "medical building",
}


# A full stop separates two names ("Potrero Avenue. Nicholls Hardware") — but
# not when it is an initial or an abbreviation ("A.P. Guadagni", "Dr. P. Crudo",
# "Leary Bros. Morticians"), which is most of the periods in these titles.
ABBREV = re.compile(r"(?:\b[A-Z]|\b(?:Dr|Mr|Mrs|Mme|St|Jr|Sr|Co|No|Inc|Bros|"
                    r"Mfg|Ave|Blvd|Corp|Ltd|Chas|Wm|Geo|Thos|Jas))$")
PARENTHETICAL = re.compile(r"\s*\([^)]*\)")
# Quotation marks hold the title of the work in the photograph, not an address:
# `"200 Years of Resistance" on Uganda Liquors` yielded 200 Years Street.
QUOTED_SPAN = re.compile(r'\s*"[^"]*"')
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
        if LOCATIONAL_JOIN.match(part):
            continue
        while True:
            trimmed = part
            for pattern in (QUOTED_WORK, PEOPLE_FRAME, LEADING_JOIN,
                            CAPTION_PREFIX, TRAILING_CROSS, TRAILING_STATE,
                            MURAL_TAIL, TRAILING_PART, TRAILING_LOCATIVE,
                            TRAILING_JOIN):
                trimmed = pattern.sub("", trimmed)
            trimmed = trimmed.strip(" ,.-&")
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
    # One enthusiast's colour slides of the city's streets, 1955-1990, filed by
    # street on the photographer's own contact sheets. A slide is a dated
    # record that the building at the number was standing and looked a
    # particular way; the photographer is what the catalogue knows about who
    # made it.
    "SFP 42": ("Robert Durden photographed the property {at} {display} "
               "{when}."),
    # A single-subject collection: every record is a mural, photographed in
    # 1981-84 as street art was being surveyed. The address is where the mural
    # was, so the mural — not the building — is the fact the record carries,
    # and saying "photographed the property" would misdescribe every entry.
    "SFP 90": ("A mural {at} {display} was photographed {when}."),
    # One photographer's documentation of the South of Market residential
    # hotels during the Yerba Buena clearances. Most of what it shows was
    # demolished within a few years, so the date is the fact: it is often the
    # last picture of a building at that number.
    "SFP 125": ("Lee Sims photographed the property {at} {display} {when}."),
    # An amateur's colour slides of the city in 1965-67, given to the library
    # with the donor's own notes. Same shape as SFP 42 — see the donor-note
    # caution in research/sources/digitalsf.md before trusting those notes.
    "SFP 169": ("James A. Martin photographed the property {at} {display} "
                "{when}."),
    # The Bureau of Engineering's own record of the public works it built and
    # the streets it cut — a city department photographing its own projects,
    # so the department is the fact the catalogue carries about who made it.
    "SFP 26": ("The San Francisco Department of Public Works Bureau of "
               "Engineering photographed the property {at} {display} {when}."),
    # A dealer's assembled collection of historical San Francisco photographs,
    # 1860s-1910s, bought in from many photographers and studios. Blaisdell
    # collected it; she did not take it, so naming her as the photographer
    # would be false of every record. Same sentence as SFP 162, for the same
    # reason: what is true of every record is that a dated photograph of the
    # address survives.
    "SFP 84": ("Photographed {at} {display} {when}."),
    # One photographer's negatives of the Western Addition in 1964, made for
    # the neighbourhood's own block clubs in the year before redevelopment
    # reached those blocks.
    "SFP 103": ("Michael Brailove photographed the property {at} {display} "
                "{when}."),
    # The school district's own photographs of its schools. Like SFP 23 it is
    # an institution photographing its own property, so the district is what
    # the catalogue knows about who made the picture.
    "SFH 3": ("The San Francisco Unified School District photographed the "
              "property {at} {display} {when}."),
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
    # Three more photographer's collections of the same shape. Their unnumbered
    # majority is street views and intersections — "Steiner street near Alamo",
    # "Mural at Fillmore Street near Sutter Street", "View of Twin Peaks from
    # Forest Hill" — which locate a corner, not a building, and can never carry
    # a page. 218 of SFP 42's 288 records, 232 of SFP 90's 285 and 848 of SFP
    # 169's 918.
    "SFP 42": "skip-unnumbered",
    "SFP 90": "skip-unnumbered",
    "SFP 169": "skip-unnumbered",
    # SFP 26 and SFH 3 are institutional collections of the same shape as the
    # subject file: 968 of SFP 26's 984 records are sewer trenches, pump
    # houses and street grading located by intersection, and 1,582 of SFH 3's
    # 1,603 name a school and nothing else. Neither unnumbered majority can
    # carry a page, and together they would put 2,550 stubs in two files.
    "SFP 26": "skip-unnumbered",
    "SFH 3": "skip-unnumbered",
    # SFP 84 is a collector's miscellany — bay views, parades, cable cars,
    # Cliff House, the 1906 fire seen from a hill. 455 of 483 records give no
    # number and almost none of them is about a building.
    "SFP 84": "skip-unnumbered",
    # SFP 103 is 51 records of one 1964 assignment in the Western Addition.
    # Its unnumbered half is block-club meetings and street corners — "Laguna
    # and Redwood Street and Block Club putting up sign after clean up",
    # "Twin boys standing in front of door" — which locate no building and are
    # captions about children besides.
    "SFP 103": "skip-unnumbered",
    # SFP 125 keeps its unnumbered records: unlike the others it photographs
    # one clearance area over eight months, so "Buildings on the 700 block of
    # Howard before being demolished" is a real record of a block that no
    # longer exists — the SFH 371 case.
}

# Whether the leftover `500$a` notes go into the finding as `record_notes`.
#
# For most collections they are archival housekeeping — "Sheet: S.F.
# Streets-Steiner", "See SFP22-0125", a landmark designation — and worth
# keeping for the auditor. For two of them they are a photographer's or a
# donor's free prose about who is in the frame: "214, Lee Wash room Daton
# Hot.", "Doris Martin & son", "Reverend Fumio Matsui (in white robes)". None
# of that can ever become a page fact, the record page is one click from
# `citation.url` if an auditor wants it, and "Privacy — hard limits" in the
# root AGENTS.md binds at extraction time — so it does not enter the
# repository at all.
COLLECTION_NOTE_POLICY = {
    "SFP 125": "drop",
    "SFP 169": "drop",
}

# Collections whose `500$a` note carries a second address worth reading, and
# how to read it. SFP 169's donor wrote a note per slide ending in a modern,
# geocoded street address — "SPCA - Animal Shelter, 16th & Alabama, front
# lobby. 2500 16th St, 94103" — and that trailing address is **where the
# camera was or roughly what the frame shows**, not a statement about a
# building. Measured over the collection: 411 of 918 records end that way, and
# on the ones where the donor also named a number in the descriptive half the
# two disagree about as often as they agree — 2324 against 2330 Chestnut, 230
# against 250 Brannan, 581 against 553 Buckingham. Several of the rest are
# plainly a viewpoint: "SF Opera House from Franklin. 406 Franklin St".
#
# So the geocode is never the address. What is read is the number the donor
# states in the descriptive half — the donor saying what the photograph is of
# — with the geocode kept beside it and a conflict recorded when they differ.
COLLECTION_DONOR_ADDRESS = {"SFP 169"}

# Collections that number their own plates, where a title-initial number is
# that serial and never a street number. See the comment in
# `address_from_title`; SFP 84's fourteen are all stereograph numbers and its
# genuine addresses are all mid-caption.
COLLECTION_PLATE_NUMBERS = {"SFP 84"}

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
    # SFP 125's addressed titles are "<building>, <number> <street>, <what the
    # frame shows>" — the SFP 23 shape — but its unnumbered ones are narrative
    # captions full of people at meetings and in their own rooms. The strict
    # policy is what keeps those out.
    "SFP 125": "named-buildings-only",
    # SFP 169's are captions too: "Person in SF SPCA doorway holding dog on
    # leash", "Martin family in courtyard of Legion of Honor".
    "SFP 169": "named-buildings-only",
    # SFP 42 and SFP 90 are deliberately *not* here. Their titles are a name
    # and an address — "Vanessi's, 498 Broadway", "Star Classics, 425 Hayes" —
    # and almost none of those names contains a building noun, so the strict
    # policy would throw away the whole point of the collection.
    #
    # SFP 84's captions are narrative and its people are the ones the privacy
    # limits are hardest about: "Ezra Winchell sitting on sidewalk taking
    # hammer to can at 747 Baker Street", "Led Winchell residence at 747 Baker
    # Street" — householders photographed outside their own homes after the
    # fire, and only three records in the collection carry a `600$a` heading
    # for redaction to work from.
    "SFP 84": "named-buildings-only",
    # SFP 103's are the same shape from 1964: "Children playing at 1884 Sutter
    # Street", "Two people sitting at voter registration table". Its buildings
    # are named — Freedom House, the Temple Theater, the Paradise Inn — and
    # the strict policy keeps exactly those.
    "SFP 103": "named-buildings-only",
    # SFH 3's captions describe classrooms: "Two children playing hopscotch in
    # the playground at Gough School for the Deaf", "Dr. V. A. Becker,
    # Supervisor of the Physically Handicapped". The schools are the buildings
    # and `school` is a building noun, so the strict policy keeps the school
    # and drops the staff and the children.
    "SFH 3": "named-buildings-only",
    # SFP 26's are a survey clerk's: "1458 Kirkwood Avenue and Mendell Street
    # southeast corner". Nothing in an addressed title is a firm name, and the
    # unaddressed ones photograph men at work in a trench.
    "SFP 26": "named-buildings-only",
}

# The kind of record, where it is not a photograph. Free-form in the schema;
# only two collections in the archive need it.
COLLECTION_KIND = {
    "SFP 21": "postcard",
    "SFH 730": "poster",
}


# --------------------------------------------------------------------------- #
# The tail — 36 collections of one to nineteen addressed records each
#
# Everything left in the archive after the twelve collections read on their
# own, minus the three #217 held back. Each is far too small to be a batch,
# and together they are one: 188 candidate addresses over 12,657 records.
#
# All 36 take the same two policies, and both are the conservative choice:
#
#   `skip-unnumbered`, because the unnumbered majority of every one of them is
#   portraits, parades, streetcars and street corners rather than buildings.
#   Keeping it would put 12,000 stubs in one file.
#
#   `named-buildings-only`, because these are caption collections and their
#   captions are almost entirely about people — bar customers, marchers,
#   volunteers, a mayor at a party, a photographer's own household. "A false
#   keep here is a privacy failure", and at this size a name the strict filter
#   drops can be judged by hand at publication instead. That trade is only
#   affordable *because* the batch is small; do not carry it to a big one.
#
# What differs per collection is the sentence, which has to say what the
# record is and who made it. Where the catalogue names one photographer the
# sentence names them; where the collection is an assembled or donated one
# with no single maker it says only that a dated photograph survives — the
# SFP 162 sentence, for the SFP 162 reason.
# --------------------------------------------------------------------------- #

_ANONYMOUS = "Photographed {at} {display} {when}."

TAIL_VOICE = {
    # The Police Department's own photography: glass plates of the 1906 ruins,
    # traffic collisions, and the Bureau of Special Services' surveillance of
    # bars and bookstores in the 1960s.
    "SFH 61": ("The San Francisco Police Department photographed the property "
               "{at} {display} {when}."),
    # Shades of San Francisco is a community collecting project — six
    # neighbourhood sets, every picture lent by a resident and copied. No one
    # body made them, so the sentence must not name one.
    "SFP 78": _ANONYMOUS,
    "SFP 155": ("Judi Iranyi photographed the property {at} {display} "
                "{when}."),
    "GLC 78": _ANONYMOUS,
    # The Board of Health's 1903 survey of Chinatown facades, made during the
    # plague campaign that demolished 160 buildings between March and October
    # of that year. The department is the fact the catalogue carries.
    "SFP 83": ("The San Francisco Board of Health photographed the building "
               "{at} {display} {when}."),
    "GLC 131": _ANONYMOUS,
    # The Junior League's Historic Sites Committee photographed buildings
    # across the city in 1964-65 while compiling its architectural survey. Ten
    # of ten records are one building at one number, which is the densest
    # addressed collection in the archive.
    "SFH 611": ("The Junior League of San Francisco's Historic Sites "
                "Committee photographed the property {at} {display} {when}."),
    "SFP 160": ("Robert Dawson photographed the property {at} {display} "
                "{when}."),
    "SFP 148": ("Leslie Sheraton photographed the property {at} {display} "
                "{when}."),
    # Published picture postcards, not somebody's photograph, and the date is
    # the card's.
    "SFP 21": "A picture postcard pictured {display} {when}.",
    # A newspaper's photo morgue: the file the paper kept of its own pictures.
    "SFP 39": ("The San Francisco News-Call Bulletin photographed {display} "
               "{when}."),
    "SFP 38": _ANONYMOUS,
    "SFH 78": _ANONYMOUS,
    "SFH 36": _ANONYMOUS,
    "GLC 35": _ANONYMOUS,
    "SFP 159": ("The United States Naval Station at Treasure Island "
                "photographed the property {at} {display} {when}."),
    "SFH 79": ("The San Francisco Sheriff's Department photographed the "
               "property {at} {display} {when}."),
    "GLC 174": _ANONYMOUS,
    "SFH 59": _ANONYMOUS,
    "GLC 203": _ANONYMOUS,
    "GLC 94": _ANONYMOUS,
    "SFP 164": ("Claudio Beagarie photographed the property {at} {display} "
                "{when}."),
    "GLC 118": _ANONYMOUS,
    "SFH 675": _ANONYMOUS,
    "GLC 66": _ANONYMOUS,
    # The society collected these shacks' pictures; it did not take them.
    "SFH 9": _ANONYMOUS,
    "SFP 40": ("D. H. Wulzen photographed the property {at} {display} "
               "{when}."),
    "SFP 55": ("Edward Stanton photographed the property {at} {display} "
               "{when}."),
    "SFP 131": _ANONYMOUS,
    "SFP 135": _ANONYMOUS,
    "SFH 75": ("The San Francisco Society for the Prevention of Cruelty to "
               "Animals photographed the property {at} {display} {when}."),
    "SFP 100": ("Ray M. Mann, Jr. photographed the property {at} {display} "
                "{when}."),
    "SFP 157": ("Darius Aidala photographed the property {at} {display} "
                "{when}."),
    "SFP 166": ("Phiz Mezey photographed the property {at} {display} "
                "{when}."),
    "GLC 76": _ANONYMOUS,
    "SFH 730": "A poster pictured {display} {when}.",
}

COLLECTION_VOICE.update(TAIL_VOICE)
for _collection in TAIL_VOICE:
    COLLECTION_NAME_POLICY.setdefault(_collection, "named-buildings-only")
    COLLECTION_UNNUMBERED_POLICY.setdefault(_collection, "skip-unnumbered")
    # And a third, added after reading the batch's `record_notes` by eye. In
    # these collections the archivist's `500$a` is not housekeeping: it is a
    # donor's memoir of their own family, a police case note, or a newspaper's
    # copy, and every kind of it names people. A crime victim with her home
    # apartment number ("EVELYN POWERS… Victim. 1900 Vallejo St. apt. #204"),
    # the children at a blackboard, a donor's parents and their hotel, the
    # party to a 1941 collision and his street address. "Privacy — hard
    # limits" binds at extraction time, none of it can ever become a page
    # fact, and `citation.url` is one click from the record for an auditor —
    # so it does not enter the repository at all. Same rule as SFP 125 and
    # SFP 169 above, applied to the whole tail because the donor-description
    # shape is what these collections are made of.
    COLLECTION_NOTE_POLICY.setdefault(_collection, "drop")

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
CAPTION_PREFIX = re.compile(
    # "Ruins" belongs with the rest of them: the 1906 caption shape is "Ruins
    # of the Orpheum Theatre at 119 O'Farrell Street", and without it the
    # theatre's name is thrown away with the caption. Measured over every
    # findings file: it recovers six building names in SFP 162 — the Dana
    # Building, the El Monterey and Warren Apartments, the Orpheum Theatre and
    # the Schloss Crockery Company — and removes none anywhere.
    r"^(?:Exterior|Interior|Front|Rear|Side|View|Views|Construction|"
    r"Demolition|Remodeling|Renovation|Warehouse|Site|Ruins)\s+of\s+(?:the\s+)?"
    rf"|^(?:(?:{CAPTION_PART_QUALIFIER})\s+)?(?:{CAPTION_PART})\s+"
    r"(?:on\s+top\s+of|in\s+front\s+of|of|at|to|on|in|inside|outside)"
    r"\s+(?:the\s+)?"
    r"|^(?:Former|Formerly|Old|Vacant|Abandoned)\s+(?=[A-Z])", re.I)


# A word that is capitalized only because the caption begins with it, and that
# describes the building rather than naming it. Kept as a closed list, not a
# part-of-speech test: measured over every findings file in the repository,
# 234 candidate names are a bare adjective plus a BUILDING_NOUN and 232 of them
# are real — "Grand Theater", "Ideal Bar", "Imperial Hotel", "Sunset Market",
# "White Cleaners". Only "Large house" and "Residencial building" are the
# caption describing what it photographed, and only a closed list separates
# them. See "measure a rule before wiring it" in research/LESSONS.md.
GENERIC_QUALIFIER = {
    "large", "small", "residential", "residencial", "commercial",
    "industrial", "vacant", "abandoned", "empty", "unidentified", "unnamed",
}


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
        if word.lower().rstrip("'s") in BUILDING_NOUN or word.lower() in BUILDING_NOUN:
            has_noun = True
            continue
        if not word[0].isupper():
            return False
        if word.lower() not in GENERIC_QUALIFIER:
            distinguishing = True
    # "Building", "House", "Public Library" name no particular one. A fragment
    # with nothing but the noun in it is the caption's common noun, and on a
    # page it says only that the address had a building on it. Neither does one
    # with nothing but a GENERIC_QUALIFIER in front of the noun: "Large house"
    # is the archivist describing the photograph, not the house's name.
    return has_noun and distinguishing


def settings_key(collection: str) -> str:
    """The key the per-collection tables are filed under.

    A collection id appears in `524$a` inside parentheses — "…records (SFH 3),
    San Francisco History Center…" — and a bare `SFH 3` also matches SFH 371
    and SFH 391 as a substring, so selecting that collection means passing
    `"(SFH 3)"`. The tables below are keyed on the id itself, so the
    parentheses come off before they are read.
    """
    return collection.strip("() ")


def voice_for(collection: str) -> str:
    collection = settings_key(collection)
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

def expand_runs(rows, plate_numbers_for):
    """Yield (record, forced_number) — twice for a record printing a run.

    "610 to 624 Anza Street" is a Bureau of Engineering photograph of a stretch
    of street, not one building with a two-number address, so it becomes two
    findings on the two numbers the caption actually prints. The buildings
    between them are real and their numbers are an inference; see "A row of
    buildings is not a range" in research/LESSONS.md.

    `plate_numbers_for` is called with the record's own collection, because a
    batch may span collections that answer that question differently.
    """
    for rec in rows:
        f = rec["fields"]
        title = " ".join(v for v in (first(f, "245", "a"),
                                     first(f, "245", "b")) if v)
        addr = address_from_title(title,
                                  plate_numbers=plate_numbers_for(rec))
        second = (addr or {}).get("second_number")
        if second and second != addr["number"]:
            yield rec, addr["number"]
            yield rec, second
        else:
            yield rec, ""


def build(selectors: list[str], batch: str, key: str = "524"):
    # Every collection in the batch must have a description template before a
    # single record is read: a run that dies half way through leaves nothing
    # behind, and the sentence is the thing there is no safe default for.
    for sel in selectors:
        voice_for(sel)
    rows = list(records(selectors, key))
    if not rows:
        sys.exit(f"no records matching {selectors!r} in {key}$a under "
                 f"{CORPUS} — run digitalsf_harvest.py first")
    unseen = sorted(set(selectors) - {r["collection"] for r in rows})
    if unseen:
        print(f"  ! no records matched: {', '.join(unseen)}", file=sys.stderr)

    def plate_numbers_for(rec):
        return settings_key(rec["collection"]) in COLLECTION_PLATE_NUMBERS

    tally = collections.Counter()
    dropped_names: list[str] = []
    kept_names: list[str] = []
    entries: dict[tuple, dict] = {}
    order: list[tuple] = []

    for rec, forced in expand_runs(sorted(rows, key=lambda r: int(r["id"] or 0)),
                                   plate_numbers_for):
        f = rec["fields"]
        settings = settings_key(rec["collection"])
        voice = COLLECTION_VOICE[settings]
        policy = COLLECTION_NAME_POLICY.get(settings, "")
        skip_unnumbered = (COLLECTION_UNNUMBERED_POLICY.get(settings)
                           == "skip-unnumbered")
        drop_notes = COLLECTION_NOTE_POLICY.get(settings) == "drop"
        read_donor = settings in COLLECTION_DONOR_ADDRESS
        plate_numbers = settings in COLLECTION_PLATE_NUMBERS
        title = " ".join(v for v in (first(f, "245", "a"), first(f, "245", "b")) if v)
        notes = read_notes(f)
        date = read_date(f)
        tally["records"] += 1
        if len(selectors) > 1:
            # A batch spanning collections is unreadable as one number: the
            # report has to say which collection each count came from.
            tally[f"records in {settings}"] += 1
        tally[f"precision:{date['precision']}"] += 1
        if date["fuzzy_flag"]:
            tally["fuzzy flag"] += 1
        if date["precision"] == "circa" and not date["fuzzy_flag"]:
            tally["imprecise but unflagged"] += 1

        citation = citation_of(f)
        if not citation:
            # No preferred citation and no series to build one from. The
            # evidence bar wants a citation precise enough for a reader to
            # check, so the record cannot produce a finding at all.
            tally["no citation the record can support — skipped"] += 1
            continue

        from_title = address_from_title(title, plate_numbers=plate_numbers)
        if forced and from_title:
            # This record prints a run of numbers and is being read once per
            # number — see expand_runs. `printed_as` keeps the source's own
            # words on both findings.
            from_title = dict(from_title, number=forced, as_written=re.sub(
                r"^\d[\dA-Za-z]*", forced, from_title["as_written"], count=1))
            tally["one of a run of street numbers"] += 1
        from_note = address_from_note(notes["address_note"]) if notes["address_note"] else None
        geocode = ""
        if read_donor and notes["donor_note"]:
            from_donor, geocode = address_from_donor_note(notes["donor_note"])
            if from_donor and not from_note:
                from_note = from_donor
                tally["address from the donor's own note"] += 1
            if geocode:
                tally["donor geocode present"] += 1
        # "Miss Chinatown 1967 Marilyn Lew" parses as number 1967 on a street
        # called Marilyn Lew. The dossier's rule for this is that a street
        # number equal to the record's own year is not an address; with no
        # street type stated there is nothing else holding it up.
        #
        # The comparison is against **every** four-digit year the date carries,
        # not the one `year_of` prints. `year_of` returns the archivist's whole
        # phrase for an imprecise date — "not before 1906", "between 1985 and
        # 1987" — which equals no street number ever, so the guard used to miss
        # exactly the records whose captions name the year in words: "Damage at
        # 1st Street and Harrison from 1906 Earthquake and Fire". Widening it
        # takes out 28 more candidates across the tail collections and changes
        # nothing in any findings file already committed.
        if (from_title and not from_title["street_type"]
                and from_title["number"] in years_of(date)):
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
        # The geocode is not an address (see COLLECTION_DONOR_ADDRESS), but a
        # geocode that names a different building from the address taken is
        # worth stating rather than silently dropping.
        if geocode and not unnumbered and addr.get("number"):
            geo_num = re.match(r"\s*(\d{1,5})", geocode)
            if geo_num and geo_num.group(1) != addr["number"].split("-")[0]:
                note = (f"The donor's note gives the address as "
                        f"{addr['as_written']!r} and geocodes the slide to "
                        f"{geocode!r}. The two are not the same building.")
                conflict = f"{conflict} {note}".strip()
                tally["donor geocode names another building"] += 1

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
        if from_title and from_title.get("printed_as"):
            extra["address_as_printed"] = from_title["printed_as"]
        if first(f, "852", "c"):
            extra["shelf"] = first(f, "852", "c")
        if first(f, "300", "a"):
            extra["medium"] = first(f, "300", "a")
        if kept:
            extra["named_in_record"] = list(dict.fromkeys(kept))
        # A `700 $e mural artist` is the catalogue crediting the person who
        # made the work at that address — the same class of fact as an
        # architect, and allowed by "Privacy — hard limits" in the root
        # AGENTS.md for exactly that reason. It is the only creator role this
        # archive states, so nothing else is read out of 700.
        artists = [d.get("a") for d in (dict(i) for i in f.get("700", []))
                   if (d.get("e") or "").lower().startswith("mural artist")
                   and d.get("a")]
        if artists:
            extra["mural_artist"] = sorted(set(artists))
        corporate = [v for v in every(f, "610", "a")
                     if "Assessor-Recorder" not in v]
        if corporate:
            extra["corporate_subject_headings"] = sorted(set(corporate))
        topical = [v for v in every(f, "650", "a")
                   if not v.startswith("Streets--")
                   and not v.startswith("Tax assessment")]
        if topical:
            extra["subject_headings"] = sorted(set(topical))
        if geocode:
            extra["donor_geocode_as_recorded"] = geocode
        if notes["other"] and not drop_notes:
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
            # A bare decade is the exception: "Photographed at 152 Church
            # Street 1930s" is not a sentence. `date_precision` carries the
            # hedge, so "circa" is dropped where "the 1950s" already says it.
            dec = DECADE_PHRASE.match(when)
            if dec:
                hedge = (dec.group(1) or "").lower()
                when = (f"in the {dec.group(2)}" if hedge in ("", "circa")
                        else f"{hedge} in the {dec.group(2)}")
        at = "at" if not unnumbered else "at the location it records as"
        description = re.sub(r"\s+([.,])", r"\1",
                             voice.format(at=at, display=display, when=when))
        if kept:
            description += (" The record names " + oxford(kept)
                            + " at the address.")
        if extra.get("mural_artist"):
            description += (" The mural is credited to "
                            + oxford([flip_name(a)
                                      for a in extra["mural_artist"]]) + ".")

        entry = {
            "id": "",  # numbered after the whole batch is grouped
            "date": date["date"],
            "date_precision": date["precision"],
            "kind": COLLECTION_KIND.get(settings, "photograph"),
            "address_as_written": display,
            "description": description,
            "extra": extra,
            "citation": {
                "label": f"{display}, {year_of(date)}. {citation}",
                "url": RECORD_URL.format(rec["id"]),
                "corpus_path": rec["page"],
                "locator": locator(rec, notes, first(f, "852", "c")),
            },
            "raw": {"text": raw_span(title, notes, personal_names(f),
                                     every(f, "610", "a") + every(f, "650", "a"))},
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
        if len(selectors) > 1:
            tally[f"findings in {settings_key(recs[0]['collection'])}"] += 1
        if len(recs) > 1:
            e["extra"]["additional_records"] = [RECORD_URL.format(r["id"])
                                                for r in recs[1:]]
        findings.append(reorder(e))

    tally["findings"] = len(findings)
    tally["distinct addresses"] = len({(k[0], k[1], k[2]) for k in order})
    return rows, findings, tally, kept_names, dropped_names


def flip_name(name: str) -> str:
    """'Weems, Jane' -> 'Jane Weems'. MARC files a name surname-first."""
    if "," not in name:
        return name.strip()
    last, first = name.split(",", 1)
    return f"{first.strip()} {last.strip()}".strip()


def oxford(items: list[str]) -> str:
    if len(items) == 1:
        return items[0]
    if len(items) == 2:
        return f"{items[0]} and {items[1]}"
    return ", ".join(items[:-1]) + f" and {items[-1]}"


def years_of(date: dict) -> set:
    """Every four-digit year the record's own date names, in any form."""
    return set(YEAR_IN.findall(f"{date.get('as_recorded', '')} "
                               f"{date.get('date', '')}"))


def year_of(date: dict) -> str:
    """What the citation prints for the date. A range prints as a range."""
    if date["precision"] in ("day", "month", "year"):
        m = YEAR_IN.search(date["date"] or "")
        if m:
            return m.group(1)
    return date["as_recorded"] or "undated"


def citation_of(f) -> str:
    """The archive's own citation for one record, or one built to the same shape.

    `524$a` is the preferred citation and is printed verbatim wherever it
    exists. 1,678 records carry none — the newspaper runs, the Sanborn atlas
    page images, the PUC water-system photographs — and for those the record
    still names its digital series in `982$a` (or `791$t`) and its holding
    centre in `692$a`, which is the same three-part shape the `524$a` strings
    use. A record naming neither gets no citation and `build` drops it, because
    "the archive" is not a citation.
    """
    preferred = first(f, "524", "a")
    if preferred:
        return preferred.replace("[Identification of item], ", "")
    series = first(f, "982", "a") or first(f, "791", "t")
    if not series:
        return ""
    centre = first(f, "692", "a")
    return ", ".join(x for x in (series, centre,
                                 "San Francisco Public Library") if x) + "."


def locator(rec, notes, shelf) -> str:
    bits = [f"record {rec['id']}"]
    if notes["box"]:
        bits.append(f"Box {notes['box']}")
    if shelf:
        bits.append(shelf)
    if notes["block"]:
        bits.append(f"assessor block {notes['block']}")
    return ", ".join(bits)


# A surname alone is also a street and a building: "747 Baker Street" with a
# `700$a` of "Baker, …" on the record, "Canterbury Hotel, 750 Sutter Street"
# with "Canterbury, Alan J.". Redacting those would take the address out of the
# evidence and the building's name off the page, so a bare surname is left
# alone wherever the next word says it is a place.
PLACE_AFTER = re.compile(
    r"^\W*(?:%s)\b" % "|".join(sorted(
        set(list(FULL_TYPE_WORD) + ["st", "ave", "av", "blvd", "dr", "ln",
                                    "ct", "pl", "rd", "ter", "cir", "hwy"])
        | {"hotel", "building", "house", "club", "school", "hall", "theatre",
           "theater", "company", "market", "church", "apartments", "tower",
           "park", "square", "center", "centre", "bar", "cafe", "inn"},
        key=len, reverse=True)), re.I)


def personal_names(fields) -> list[str]:
    """Every personal name the record files, from `600$a` and `700$a`.

    `600` is where a catalogue is *supposed* to put the people a photograph is
    about, and for SFP 23 and SFP 169 it is. SFP 84 leaves it empty and files
    the family whose house this is under `700$a` — "Winchell, Ezra & Winchell,
    Led F." — with `$e Photographer`, because they took the pictures of their
    own home after the fire. The role does not settle it: a name written into
    the caption is a person in the frame whatever the record credits them for
    elsewhere, and "Led Winchell home at 747 Baker Street" is a sentence about
    who lived at a street number. 14,535 of the corpus's 22,360 `700` fields
    carry no role at all.

    A corporate body has no comma — but its *qualifier* does: "San Francisco
    Redevelopment Agency (San Francisco, Calif.)" tested comma-first and had
    the agency's name struck out of a caption. The qualifier comes off before
    the test. Two people can share one subfield joined by an ampersand.
    """
    out = []
    for raw in every(fields, "600", "a") + every(fields, "700", "a"):
        for part in re.split(r"\s*&\s*", raw):
            if "," in re.sub(r"\s*\([^)]*\)\s*$", "", part):
                out.append(part.strip())
    return out


# A person the catalogue indexed nowhere. `redact` can only reach a name that
# is in the record's own 600/700 headings, and a caption often names someone
# the cataloguer never made a heading for — the chairs of a 1946 fundraising
# drive, the guest of honour at a 1947 party, a consul and his wife. This is
# the one shape that is narrow enough to act on: a courtesy title or a rank in
# front of a capitalised run. It cannot match a bare "Eagle Market", and the
# two exemptions below cover the firms that do wear one.
#
# Measured over every `raw.text` in every digitalsf findings file: 53 spans
# match, 49 are people — including "in the home of Mr. and Mrs. Ferdinand Smith
# at 825 Francisco Street", a resident named at their address in a *published*
# finding — and the other 4 are firms, all four exempted. Applied to the whole
# repository the same rule would be wrong: it fires on "Dr. Carlton B. Goodlett
# Place" (a street), "Miss Smith's Tea Room" and "Mr. S Leather" (businesses),
# and on the civic figures a context statement exists to document. `redact` is
# only ever called on this source, and that is what keeps it safe.
HONORIFIC = (r"Mr|Mrs|Ms|Miss|Dr|Capt|Sgt|Lt|Col|Gen|Rev|Reverend|Prof|Msgr|"
             r"Fr|Sister|Father|Judge|Monsignor")
# "Mr. and Mrs. Ferdinand Smith" is one name wearing two titles; without the
# bridge the first title is left stranded in front of the marker.
# `(?:[A-Z]\.){1,4}` is the unspaced initial run — the catalogue writes both
# "Dr. P. Crudo" and "Dr. F.S. Crudo" in one caption, and only one of them has
# a space to split on. The generational suffix keeps its full stop when a word
# runs straight into it ("Jr.discussing" is in the corpus verbatim), so the
# marker never swallows the start of the next word.
HONORIFIC_NAME = re.compile(
    rf"\b(?:{HONORIFIC})\.?\s+(?:and\s+(?:{HONORIFIC})\.?\s+)?"
    rf"(?:(?:(?:[A-Z]\.){{1,4}}|[A-Z][A-Za-z'’-]*\.?)\s+){{0,3}}"
    rf"(?!(?:Jr|Sr|II|III)\b)[A-Z][A-Za-z'’-]+"
    rf"(?:,?\s+(?:Jr|Sr|II|III)\b\.?(?!\w))?")
HONORIFIC_HEAD = re.compile(rf"^(?:{HONORIFIC})\.?\s+(?:and\s+(?:{HONORIFIC})\.?\s+)?")


def redact_honorifics(span: str, headings: list[str]) -> str:
    """Strike a courtesy title plus the name after it, unless it is a firm.

    Two exemptions, both measured: what follows the title reads as a firm name
    ("Dr. Pepper Bottling Company", "Mrs. Biggs Bakery"), or the record's own
    610/650 headings already file it as one — "Businesses--Andrews Diamond
    Palace." is the catalogue saying "Col. Andrews Diamond Palace" is a shop.
    """
    filed = " | ".join(headings).lower()

    def sub(m):
        name = HONORIFIC_HEAD.sub("", m.group(0))
        if is_named_building(name):
            return m.group(0)
        if name and name.lower() in filed:
            return m.group(0)
        return "[name withheld]"

    # One marker per person: a caption listing three people should still read
    # as three, so adjacent markers are not collapsed.
    return HONORIFIC_NAME.sub(sub, span)


def redact(span: str, subjects: list[str]) -> str:
    """Take the record's own personal names out of the quoted span.

    `raw.text` is the shortest passage that justifies the extraction, and it is
    committed. In a caption collection that passage is often "Lee Washington's
    room in Daton Hotel, 175 3rd Street" — the building is the finding, the
    resident is barred by "Privacy — hard limits" in the root AGENTS.md, and
    the bar applies when the finding is written, not when a page is. What is
    left still justifies the address, the date and the building's name.
    """
    for subject in subjects:
        # A heading carries the person's dates in parentheses or after a comma
        # — "Mancuso, Edward T. (1901-1985)" — and they are not part of any
        # name a caption will use.
        subject = re.sub(r"\s*\([^)]*\)\s*$", "", subject)
        subject = re.sub(r",\s*\d{4}\s*-\s*\d{0,4}\.?$", "", subject)
        parts = [p.strip(" .,") for p in subject.split(",")]
        forms = [subject.strip(" .")]
        if len(parts) == 2:
            # Surname and forenames both, and the flipped form: MARC files
            # "Mancuso, Edward T." and the caption writes "Public Defender
            # Edward T. Mancuso", so redacting only the whole string as filed
            # leaves the forename standing.
            forms += [f"{parts[1]} {parts[0]}", parts[0], parts[1]]
        for form in sorted(set(f for f in forms if len(f) > 2), key=len,
                           reverse=True):
            # `\b` cannot anchor a form that ends in an initial's full stop
            # ("Edward T."), so the boundary is a look-around on word
            # characters instead. Initials also vary in punctuation between
            # the heading and the caption, so a full stop matches an optional
            # one.
            pattern = re.escape(form).replace("\\.", r"\.?")
            bare = form == parts[0] if len(parts) == 2 else False
            span = re.sub(
                rf"(?<!\w){pattern}(?!\w)(?:'s)?",
                lambda m: (m.group(0) if bare and PLACE_AFTER.match(
                    span[m.end():]) else "[name withheld]"),
                span, flags=re.I)
    # Redacting a name in two passes ("Edward T", then "Mancuso") can leave an
    # orphaned initial's full stop between the two markers.
    span = re.sub(r"\[name withheld\](?:[\s.]*\[name withheld\])*\s*",
                  "[name withheld] ", span)
    # The marker replaces a name that ended a clause, so the space the
    # rejoining adds lands in front of the comma: "Officer [name withheld] ,".
    return re.sub(r"\s+([,.;])", r"\1", span).strip()


def raw_span(title: str, notes: dict, subjects: list[str] | None = None,
             headings: list[str] | None = None) -> str:
    span = redact_honorifics(redact(title, subjects or []), headings or [])
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
    selectors = [c.strip() for c in argv[0].split(",") if c.strip()]
    batch = argv[1]
    report = "--report" in argv
    key = "982" if "--key" in argv and argv[argv.index("--key") + 1] == "982" \
        else "524"
    read_on = next((a for a in argv if re.fullmatch(r"\d{4}-\d{2}-\d{2}", a)),
                   datetime.date.today().isoformat())

    rows, findings, tally, kept, dropped = build(selectors, batch, key)

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
