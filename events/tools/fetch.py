#!/usr/bin/env python3
"""Fetch upcoming events from the registered calendars → events/events.json.

Stdlib only. The calendars are registered in events/sources.json; the venues
they name are resolved through events/venues.json. What this writes is the
module's one data file: /events renders from it, the homepage map's event dots
come from the geojson built out of it, and a page's "Upcoming events" panel
reads it through the venue's `path`.

    python3 events/tools/fetch.py            # fetch every source, write events.json
    python3 events/tools/fetch.py --source sfrecpark
    python3 events/tools/fetch.py venues     # print the venues seen and unmapped

Six shapes of calendar, one parser each — see events/AGENTS.md:

    ical          one iCalendar feed per source (illuminate.org)
    ical-multi    the same feed once per CivicPlus calendar id (sfrecpark.org)
    squarespace   <collection>?format=json `upcoming` array (natureinthecity,
                  sunsetdunes)
    html          a hand-maintained page with no feed (alemanyfarm.org)
    tribe         The Events Calendar's list view, paged by path
                  (ybgfestival.org)
    pdf-table     a page linking a spreadsheet exported to PDF (sfrecpark.org's
                  tentative calendars of special events — one row per permit
                  and day, dates but no times, so every event is all-day)

Good citizenship: the user agent says who we are, requests are rate-limited,
and robots.txt is honoured — a source that forbids automated access is
`access: needs-human` in sources.json and is never fetched.
"""
from __future__ import annotations

import argparse
import html.parser
import html as html_lib
import json
import re
import sys
import time
import unicodedata
import urllib.parse
import zlib
import urllib.request
import zoneinfo
from datetime import date, datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SOURCES = ROOT / "sources.json"
VENUES = ROOT / "venues.json"
OUT = ROOT / "events.json"

PACIFIC = zoneinfo.ZoneInfo("America/Los_Angeles")
UA = "know-this-place-events/1.0 (+https://knowthis.place)"
# One polite pause between requests to the same run. Alemany Farm's robots.txt
# asks for a crawl-delay of 20s — we make exactly one request there per run,
# but the floor applies everywhere so a new source inherits it.
DELAY_S = 2.0
# Calendars announce events months out; the site only shows the near term, and
# a longer file only means diffs nobody reads.
HORIZON_DAYS = 120

# Squarespace leaves the venue pin at the platform default (its own NYC
# office) when the editor never set one — a coordinate that says nothing.
SQ_DEFAULT_COORDS = (40.7207559, -74.0007613)


def fetch(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read()


def norm(s: str) -> str:
    """Lowercase, alphanumeric-only — the dedup and venue-match surface."""
    return re.sub(r"[^a-z0-9]+", " ", s.lower()).strip()


def strip_tags(s: str) -> str:
    return html_lib.unescape(re.sub(r"<[^>]+>", "", s))


def clean_location(s: str) -> str:
    """The source's location text, displayable: tags and entities gone, and
    RecPark's nameless ' - 698 Connecticut Street' shape loses its dash."""
    s = strip_tags(s)
    s = re.sub(r"\s+", " ", s).strip()
    return s.lstrip("-–— ").strip()


# A trailing date on a title — Illuminate's "Midweek Melodies | September 30"
# — repeats what the listing already shows beside it, and splits one series
# into as many names as it has dates.
TITLE_DATE = re.compile(
    r"\s+[|–—-]\s+(?:(?:Mon|Tues?|Wed(?:nes)?|Thu(?:rs)?|Fri|Sat(?:ur)?|Sun)"
    r"[a-z]*,?\s+)?(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?"
    r"\s+\d{1,2}(?:st|nd|rd|th)?(?:,?\s+\d{4})?\s*$", re.I)


def clean_title(title: str) -> str:
    return TITLE_DATE.sub("", title).strip() or title


def drop_venue_prefix(title: str, venue: str) -> str:
    """'Union Square Daily Programming: Friday Chess Lessons' at Union Square
    → 'Friday Chess Lessons'. RecPark leads with the venue, which every
    surface already shows beside the title; a prefix that doesn't name the
    venue ('Partner Spotlight: …') is part of the title and stays."""
    head, sep, rest = title.partition(": ")
    v = norm(venue or "")
    return rest.strip() if sep and rest.strip() and v and v in norm(head) else title


def venue_label(location: str) -> str:
    """What to call a venue the register doesn't know. RecPark writes
    '<Venue> - <address>  San Francisco CA 94122'; the venue half is the name
    a reader knows it by, and the city and ZIP say nothing on a San Francisco
    site. Anything else is shown as the source wrote it."""
    s = re.sub(r",?\s*San Francisco,?\s*CA\s*\d{5}(-\d{4})?\s*$", "",
               location, flags=re.I).strip()
    m = re.match(r"^(.+?)\s+[-–]\s+\d+\s+\S.*$", s)
    return (m.group(1) if m else s).strip() or location


def ical_unescape(s: str) -> str:
    return (s.replace("\\n", " ").replace("\\,", ",").replace("\\;", ";")
             .replace("\\N", " ").replace("\\\\", "\\"))


# --------------------------------------------------------------------------
# iCalendar
# --------------------------------------------------------------------------

def parse_ical(text: str) -> list:
    """Minimal VEVENT reader: unfold, split properties, keep the fields used."""
    lines = []
    for raw in text.replace("\r\n", "\n").split("\n"):
        if raw[:1] in (" ", "\t") and lines:
            lines[-1] += raw[1:]
        else:
            lines.append(raw)
    events, cur = [], None
    for line in lines:
        if line == "BEGIN:VEVENT":
            cur = {}
        elif line == "END:VEVENT" and cur is not None:
            events.append(cur)
            cur = None
        elif cur is not None and ":" in line:
            head, _, value = line.partition(":")
            name, _, params = head.partition(";")
            cur[name] = (ical_unescape(value), params)
    return events


def parse_ical_dt(prop) -> datetime | None:
    """DTSTART/DTEND → an aware Pacific datetime. All-day dates are midnight."""
    value, params = prop
    value = value.strip()
    m = re.search(r"TZID=([^;:]+)", params or "")
    tz = zoneinfo.ZoneInfo(m[1]) if m else None
    try:
        if re.fullmatch(r"\d{8}", value):            # all-day
            return datetime.strptime(value, "%Y%m%d").replace(tzinfo=tz or PACIFIC)
        if value.endswith("Z"):
            return (datetime.strptime(value, "%Y%m%dT%H%M%SZ")
                    .replace(tzinfo=zoneinfo.ZoneInfo("UTC")).astimezone(PACIFIC))
        return datetime.strptime(value, "%Y%m%dT%H%M%S").replace(tzinfo=tz or PACIFIC)
    except (ValueError, KeyError):
        return None


def fetch_ical_feed(url: str, source_id: str, url_for_uid) -> list:
    out = []
    for ev in parse_ical(fetch(url).decode("utf-8", "replace")):
        start = parse_ical_dt(ev.get("DTSTART", ("", "")))
        if not start:
            continue
        end = parse_ical_dt(ev.get("DTEND", ("", "")))
        title = html_lib.unescape(ev.get("SUMMARY", ("", ""))[0]).strip()
        location = clean_location(ev.get("LOCATION", ("", ""))[0])
        uid = ev.get("UID", ("", ""))[0].strip()
        link = ev.get("URL", ("", ""))[0].strip()
        url = link if link.startswith("http") else (url_for_uid(uid) if uid else "")
        if not title:
            continue
        out.append({
            "id": f"{source_id}:{uid}" if uid else f"{source_id}:{norm(title)}:{start.isoformat()}",
            "source": source_id,
            "title": title,
            "url": url,
            "start": start.isoformat(timespec="seconds"),
            "end": end.isoformat(timespec="seconds") if end else None,
            "location": location,
        })
    return out


def fetch_illuminate(source: dict) -> list:
    # The feed's VEVENTs carry no URL of their own, but every event is a
    # WordPress post, and the REST API lists each one's link with its title
    # and start (a UTC epoch). Slugs can't be derived from titles — reused
    # names get "-2", "-3" — so match on start time and title, and fall back
    # to the public listing page only for an event the API doesn't return.
    events = fetch_ical_feed(source["url"], source["id"],
                             lambda uid: source.get("page") or source["url"])
    links = source.get("links")
    if not links or not events:
        return events
    by_start, wanted = {}, {int(datetime.fromisoformat(e["start"]).timestamp())
                            for e in events}
    # Posts come newest first, and an event is posted before it happens, so
    # the upcoming slate is in the first pages; stop once every start is seen.
    for page in range(1, 6):
        sep = "&" if "?" in links else "?"
        try:
            posts = json.loads(fetch(f"{links}{sep}page={page}"))
        except Exception:
            break   # a missing link falls back to the listing page, not a failure
        for post in posts:
            try:
                start = int((post.get("meta") or {}).get("se_event_date_start"))
            except (TypeError, ValueError):
                continue
            title = norm(html_lib.unescape((post.get("title") or {}).get("rendered", "")))
            if post.get("link", "").startswith("http"):
                by_start.setdefault(start, []).append((title, post["link"]))
        if len(posts) < 100 or wanted <= by_start.keys():
            break
        time.sleep(DELAY_S)
    for ev in events:
        cands = by_start.get(int(datetime.fromisoformat(ev["start"]).timestamp()), [])
        match = ([link for t, link in cands if t == norm(ev["title"])]
                 or ([cands[0][1]] if len(cands) == 1 else []))
        if match:
            ev["url"] = match[0]
    return events


def fetch_sfrecpark(source: dict) -> list:
    out = []
    for url in source["feeds"]:
        out += fetch_ical_feed(
            url, source["id"],
            lambda uid: f"https://sfrecpark.org/calendar.aspx?EID={uid}")
        time.sleep(DELAY_S)
    return out


# --------------------------------------------------------------------------
# Squarespace — <collection>?format=json, the `upcoming` array
# --------------------------------------------------------------------------

def fetch_squarespace(source: dict) -> list:
    url = source["url"] + ("&" if "?" in source["url"] else "?") + "format=json"
    data = json.loads(fetch(url).decode("utf-8", "replace"))
    base = source["url"].split("/")[0] + "//" + source["url"].split("/")[2]
    out = []
    for item in data.get("upcoming") or []:
        title = (item.get("title") or "").strip()
        start = item.get("startDate")
        if not title or not start:
            continue
        loc = item.get("location") or {}
        lat, lng = loc.get("mapLat"), loc.get("mapLng")
        coords = None
        if isinstance(lat, (int, float)) and isinstance(lng, (int, float)):
            if (round(lat, 6), round(lng, 6)) != (round(SQ_DEFAULT_COORDS[0], 6),
                                                  round(SQ_DEFAULT_COORDS[1], 6)):
                coords = (lat, lng)
        venue = clean_location(loc.get("addressTitle") or "")
        full = item.get("fullUrl") or ""
        event = {
            "id": f"{source['id']}:{item.get('id') or item.get('urlId') or norm(title)}",
            "source": source["id"],
            "title": html_lib.unescape(title),
            "url": base + full if full else source["url"],
            "start": datetime.fromtimestamp(start / 1000, PACIFIC).isoformat(timespec="seconds"),
            "end": (datetime.fromtimestamp(item["endDate"] / 1000, PACIFIC).isoformat(timespec="seconds")
                    if item.get("endDate") else None),
            "location": venue,
        }
        if coords:
            event["coords"] = coords
            event["src_coords"] = True
        out.append(event)
    return out


# --------------------------------------------------------------------------
# alemanyfarm.org — a hand-maintained page, no feed
# --------------------------------------------------------------------------

WORKSHOP_DATE = re.compile(
    r"(?:Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday),?\s+"
    r"(January|February|March|April|May|June|July|August|September|October|"
    r"November|December)\s+(\d{1,2}),?\s+(\d{4})", re.I)
WORKSHOP_TIME = re.compile(
    r"(\d{1,2})(?::(\d{2}))?\s*([ap])\.?m\.?\s*(?:to|–|—|-)\s*"
    r"(\d{1,2})(?::(\d{2}))?\s*([ap])\.?m\.?", re.I)


class WorkshopParser(html.parser.HTMLParser):
    """Walk the page's block stream; each <h3> opens a candidate workshop and
    the first date-shaped <strong> plus first Eventbrite link finish it."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.blocks = []          # [{title, text, link}]
        self.cur = None
        self._h3 = self._strong = False
        self._strong_text = []

    def handle_starttag(self, tag, attrs):
        if tag == "h3":
            if self.cur:
                self.blocks.append(self.cur)
            self.cur = {"title": "", "text": "", "link": ""}
            self._h3 = True
        elif tag == "strong" and self.cur is not None:
            self._strong = True
            self._strong_text = []
        elif tag == "a" and self.cur is not None:
            href = dict(attrs).get("href", "")
            if "eventbrite.com" in href and not self.cur["link"]:
                self.cur["link"] = href.split("?")[0]

    def handle_endtag(self, tag):
        if tag == "h3":
            self._h3 = False
        elif tag == "strong" and self._strong:
            self._strong = False
            if self.cur is not None:
                self.cur["text"] += " " + " ".join(self._strong_text)
        elif tag in ("hr",) and self.cur is not None:
            self.blocks.append(self.cur)
            self.cur = None

    def handle_data(self, data):
        if self._h3 and self.cur is not None:
            self.cur["title"] += data
        if self._strong:
            self._strong_text.append(data)


def fetch_alemany(source: dict) -> list:
    parser = WorkshopParser()
    parser.feed(fetch(source["url"]).decode("utf-8", "replace"))
    if parser.cur:
        parser.blocks.append(parser.cur)
    out = []
    for block in parser.blocks:
        title = re.sub(r"\s+", " ", block["title"]).strip()
        text = re.sub(r"\s+", " ", block["text"])
        d = WORKSHOP_DATE.search(text)
        t = WORKSHOP_TIME.search(text)
        if not title or not d:
            continue
        day = datetime.strptime(f"{d[2]} {d[1]} {d[3]}", "%d %B %Y").date()

        def clock(groups):
            h, m, ap = int(groups[0]), groups[1] or "0", groups[2].lower()
            return int(h) % 12 + (12 if ap == "p" else 0), int(m)

        if t:
            sh, sm = clock(t.groups()[:3])
            eh, em = clock(t.groups()[3:])
        else:
            sh, sm, eh, em = 0, 0, 0, 0
        start = datetime(day.year, day.month, day.day, sh, sm, tzinfo=PACIFIC)
        end = datetime(day.year, day.month, day.day, eh, em, tzinfo=PACIFIC) if t else None
        slug = norm(title).replace(" ", "-")
        out.append({
            "id": f"{source['id']}:{slug}:{day.isoformat()}",
            "source": source["id"],
            "title": title,
            "url": block["link"] or source["url"],
            "start": start.isoformat(timespec="seconds"),
            "end": end.isoformat(timespec="seconds") if end else None,
            "location": "Alemany Farm",
        })
    return out


# --------------------------------------------------------------------------
# The Events Calendar (WordPress "tribe") — the public list view, paged by path
# --------------------------------------------------------------------------
# ybgfestival.org runs The Events Calendar. Its iCal export (?ical=1) and its
# REST API's paging (?page=2) both need a query string, and the site's
# robots.txt disallows every URL with one (`Disallow: /*?`). The list view
# pages by path instead — /events/, then /events/list/page/2/ — so that is
# what is read. Each event is an <article class="tribe-events-calendar-list__event …
# post-<id> …"> with a <time datetime="YYYY-MM-DD"> holding the human date and
# hours, a title link to the event's own page, and an <address> naming the
# venue and street. The "latest past" block the page shows out of season has
# the same shape under another prefix; resolve() drops what has passed.

TRIBE_ARTICLE = re.compile(
    r'<article\b[^>]*class="[^"]*tribe-events-calendar-(?:list|latest-past)__event\b'
    r'([^"]*)"[^>]*>(.*?)</article>', re.S)
TRIBE_TIME = re.compile(r'<time\b[^>]*datetime="(\d{4}-\d{2}-\d{2})"[^>]*>(.*?)</time>', re.S)
TRIBE_TITLE = re.compile(
    r'<a\b[^>]*href="([^"]+)"[^>]*class="[^"]*__event-title-link[^"]*"[^>]*>(.*?)</a>', re.S)
TRIBE_VENUE = re.compile(r'class="[^"]*__event-venue-title[^"]*"[^>]*>(.*?)</span>', re.S)
TRIBE_ADDRESS = re.compile(r'class="[^"]*__event-venue-address[^"]*"[^>]*>(.*?)</span>', re.S)
TRIBE_NEXT = re.compile(r'<a\b[^>]*\brel="next"[^>]*>|<a\b[^>]*class="[^"]*tribe-events-c-nav__next[^"]*"[^>]*>', re.S)
TRIBE_CLOCK = re.compile(r"(\d{1,2})(?::(\d{2}))?\s*([ap])\.?m\.?", re.I)
TRIBE_MONTHDAY = re.compile(
    r"\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+(\d{1,2})\b", re.I)
MONTHS = ["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"]
TRIBE_MAX_PAGES = 12


def _text(fragment: str) -> str:
    return re.sub(r"\s+", " ", strip_tags(fragment)).strip()


def parse_tribe_list(page: str, source_id: str) -> list:
    out = []
    for classes, body in TRIBE_ARTICLE.findall(page):
        t, a = TRIBE_TIME.search(body), TRIBE_TITLE.search(body)
        if not t or not a:
            continue
        day = date.fromisoformat(t[1])
        when = _text(t[2])
        clocks = [(int(h) % 12 + (12 if ap.lower() == "p" else 0), int(m or 0))
                  for h, m, ap in TRIBE_CLOCK.findall(when)]
        # A second month-day in the range is the end date of a multi-day event.
        days = TRIBE_MONTHDAY.findall(when)
        end_day = day
        if len(days) > 1:
            mon, dd = MONTHS.index(days[-1][0][:3].lower()) + 1, int(days[-1][1])
            end_day = date(day.year + (1 if mon < day.month else 0), mon, dd)
        sh, sm = clocks[0] if clocks else (0, 0)
        start = datetime(day.year, day.month, day.day, sh, sm, tzinfo=PACIFIC)
        end = None
        if len(clocks) > 1:
            eh, em = clocks[-1]
            end = datetime(end_day.year, end_day.month, end_day.day, eh, em, tzinfo=PACIFIC)
        elif end_day != day:
            end = datetime(end_day.year, end_day.month, end_day.day, 23, 59, tzinfo=PACIFIC)
        title = _text(a[2])
        if not title:
            continue
        venue = TRIBE_VENUE.search(body)
        address = TRIBE_ADDRESS.search(body)
        location = ", ".join(x for x in (_text(venue[1]) if venue else "",
                                         _text(address[1]) if address else "") if x)
        post = re.search(r"\bpost-(\d+)\b", classes)
        out.append({
            "id": (f"{source_id}:{post[1]}" if post
                   else f"{source_id}:{norm(title)}:{start.isoformat()}"),
            "source": source_id,
            "title": title,
            "url": html_lib.unescape(a[1]),
            "start": start.isoformat(timespec="seconds"),
            "end": end.isoformat(timespec="seconds") if end else None,
            "location": clean_location(location),
        })
    return out


# --------------------------------------------------------------------------
# PDF table — Rec & Park's tentative calendars of special events
# --------------------------------------------------------------------------
#
# The permits office publishes its special-event master spreadsheet as PDFs
# linked from one page, and replaces the files (new DocumentCenter ids) as the
# year fills in, so the page is read first for the current links. Excel's PDF
# export is plain enough for the stdlib: Flate-compressed content streams of
# literal strings in WinAnsi, one TJ array per row with a wide gap between
# cells. Rows are grouped by their position on the page, because a cell that
# overflows its column is clipped and the rest of the row continues in a
# separate text object on the same line.

PDF_TOKEN = re.compile(rb"\((?:\\.|[^\\)])*\)|\[|\]|[-+]?\d*\.?\d+|/[^\s/\[\]()<>]+"
                       rb"|[A-Za-z*'\"]+", re.S)
PDF_NUMBER = re.compile(rb"[-+]?\d*\.?\d+$")
# A TJ adjustment this wide (thousandths of the font size) is a column gap,
# not kerning.
PDF_CELL_GAP = 400


def pdf_literal(b: bytes) -> str:
    out, i, b = bytearray(), 1, b[:-1]
    while i < len(b):
        if b[i] == 0x5C:   # backslash
            m = re.match(rb"[0-7]{1,3}", b[i + 1:])
            if m:
                out.append(int(m.group(), 8) & 0xFF)
                i += 1 + len(m.group())
                continue
            n = b[i + 1:i + 2]
            out += {b"n": b"\n", b"r": b"\r", b"t": b"\t"}.get(n, n)
            i += 2
            continue
        out.append(b[i])
        i += 1
    return out.decode("cp1252", "replace")


def pdf_rows(pdf: bytes):
    """Every text row of every page, as a list of cell strings left to right."""
    for m in re.finditer(rb"stream\r?\n", pdf):
        end = pdf.find(b"endstream", m.end())
        try:
            content = zlib.decompress(pdf[m.end():end])
        except zlib.error:
            continue
        if b"BT" not in content:
            continue
        lm, lead, depth, stack, arr, page = [1, 0, 0, 1, 0, 0], 0.0, 0, [], None, {}

        def put(cells):
            # The page is landscape, so with a rotated text matrix the row is
            # e and the column is f; either way the row is the coordinate the
            # line moves (TD, T*) change.
            page.setdefault(round(lm[4], 1), []).append((lm[5], cells))

        for t in PDF_TOKEN.findall(content):
            if t == b"[":
                arr = []
                continue
            if t == b"]":
                stack.append(arr)
                arr = None
                continue
            num = bool(PDF_NUMBER.match(t))
            if arr is not None:
                arr.append(pdf_literal(t) if t[:1] == b"(" else float(t) if num else t)
                continue
            if t[:1] == b"(":
                stack.append(pdf_literal(t))
                continue
            if num:
                stack.append(float(t))
                continue
            a, b, c, d, e, f = lm
            if t == b"q":
                depth += 1
            elif t == b"Q":
                depth -= 1
            elif t == b"BT":
                lm = [1, 0, 0, 1, 0, 0]
            elif t == b"Tm" and len(stack) >= 6:
                lm = stack[-6:]
            elif t in (b"TD", b"Td") and len(stack) >= 2:
                tx, ty = stack[-2:]
                if t == b"TD":
                    lead = -ty
                lm = [a, b, c, d, tx * a + ty * c + e, tx * b + ty * d + f]
            elif t == b"TL" and stack:
                lead = stack[-1]
            elif t == b"T*":
                lm = [a, b, c, d, -lead * c + e, -lead * d + f]
            elif t == b"Tj" and stack and isinstance(stack[-1], str):
                # A lone glyph inside a clip is the visible sliver of a cell
                # that overflowed its column — its text is truncated anyway.
                if not (depth > 0 and len(stack[-1]) == 1):
                    put([stack[-1]])
            elif t == b"TJ" and stack and isinstance(stack[-1], list):
                cells = [""]
                for part in stack[-1]:
                    if isinstance(part, str):
                        cells[-1] += part
                    elif isinstance(part, float) and part < -PDF_CELL_GAP:
                        cells.append("")
                put(cells)
            stack = []
        for row in page.values():
            cells = [c.strip() for _, cs in sorted(row, key=lambda r: r[0])
                     for c in cs]
            yield [c for c in cells if c]


MONTH_ABBR = {m: i for i, m in enumerate(
    "jan feb mar apr may jun jul aug sep oct nov dec".split(), 1)}
WEEKDAYS = {"monday", "tuesday", "wednesday", "thursday", "friday",
            "saturday", "sunday"}
# Between the date and the site: set-up and take-down dates (sometimes an
# Excel serial, sometimes a time), attendance, amplified sound.
RPD_OPTIONAL = re.compile(
    r"^(\d{1,2}-[a-z]{3}|\d{1,2}(:\d\d)?\s*[ap]m|\d{5}|[<>]?[\d,]+\+?(/day)?"
    r"|na|n/a|tbd|yes|no)$", re.I)
# Titles that name a private person, or a person's own occasion, never list
# (events/AGENTS.md): a permit calendar carries weddings and memorials by
# name. A campaign event names its candidate, so it is held back too.
RPD_PRIVATE = re.compile(
    r"wedding|memorial(?! day)|funeral|celebration of life|birthday|quincea"
    r"|baby shower|bridal|family gathering|reunion|priv(i)?ate|campaign"
    r"|for supervisor|for mayor", re.I)
# Rows that are logistics, not a gathering: festival fencing going up and
# coming down, a club run the sheet marks as off Rec & Park property.
RPD_NOT_EVENT = re.compile(r"\bfencing (starts|clears)\b|no sfr&?p impact", re.I)


def rpd_location(site: str) -> str:
    """'GGP-Robin Williams Meadow' → 'Robin Williams Meadow, Golden Gate
    Park'; accents folded so 'Parque Niños Unidos' matches its register
    entry (norm() keeps ASCII only)."""
    site = unicodedata.normalize("NFKD", site).encode("ascii", "ignore").decode()
    site = re.sub(r"\s+", " ", site).strip(" -")
    m = re.match(r"GGP\s*-\s*(.+)$", site)
    return f"{m.group(1)}, Golden Gate Park" if m else site


def rpd_events(rows, year: int, source: dict) -> list:
    out = []
    for r in rows:
        # Status, then permit number: only a P or an I is approved ("Not
        # Approved Until P or I Appears in First Column"); a HOLIDAY, HOLD
        # or ADVISORY row has no permit number and is not an event.
        if len(r) < 6 or r[0] not in ("P", "I") or not re.fullmatch(r"R\d+", r[1]):
            continue
        if r[2].lower() not in WEEKDAYS:
            continue
        m = re.fullmatch(r"(\d{1,2})-([A-Za-z]{3})", r[3])
        if not m or m.group(2).lower() not in MONTH_ABBR:
            continue
        try:
            day = date(year, MONTH_ABBR[m.group(2).lower()], int(m.group(1)))
        except ValueError:
            continue
        rest = r[4:]
        while rest and RPD_OPTIONAL.match(rest[0]):
            rest = rest[1:]
        if len(rest) < 2:
            continue
        site, title = rest[0], rest[-1]
        title = re.sub(r"\s+tentative$", "", re.sub(r"\s+", " ", title),
                       flags=re.I).strip()
        if not title or RPD_PRIVATE.search(title) or RPD_NOT_EVENT.search(title):
            continue
        location = rpd_location(site)
        start = datetime(day.year, day.month, day.day, tzinfo=PACIFIC)
        out.append({
            # One permit can cover several sites on one day — a run through
            # three squares — and each is its own listing on its own page.
            "id": f"{source['id']}:{r[1]}:{day.isoformat()}:{norm(location).replace(' ', '-')}",
            "source": source["id"],
            "title": title,
            # The PDFs are replaced as the year fills in, so link the page
            # that lists them, which stays put.
            "url": source["url"],
            "start": start.isoformat(timespec="seconds"),
            "end": None,
            "all_day": True,
            "location": location,
        })
    return out


def fetch_tribe(source: dict) -> list:
    url, out, seen = source["url"], [], set()
    host = urllib.parse.urlsplit(source["url"]).netloc
    horizon = datetime.now(PACIFIC).date() + timedelta(days=HORIZON_DAYS)
    for _ in range(TRIBE_MAX_PAGES):
        seen.add(url)
        page = fetch(url).decode("utf-8", "replace")
        got = parse_tribe_list(page, source["id"])
        out += got
        if got and max(date.fromisoformat(e["start"][:10]) for e in got) > horizon:
            break
        nxt = None
        for tag in TRIBE_NEXT.findall(page):
            href = re.search(r'href="([^"]+)"', tag)
            if href:
                nxt = html_lib.unescape(href[1])
                break
        # Never follow a query-string URL (robots.txt) or leave the site.
        if (not nxt or "?" in nxt or nxt in seen
                or urllib.parse.urlsplit(nxt).netloc != host):
            break
        url = nxt
        time.sleep(max(DELAY_S, source.get("crawl_delay", 0)))
    return out


def fetch_rpd_master(source: dict) -> list:
    page = fetch(source["url"]).decode("utf-8", "replace")
    base = "https://" + source["url"].split("/")[2]
    # The page links one spreadsheet per area and one with every area; read
    # the one with every area, for each year the page lists.
    links = re.findall(
        r'href="([^"]*/DocumentCenter/View/\d+[^"]*)"[^>]*>\s*(?:<[^>]+>\s*)*'
        r"(\d{4}) RPD Special Event Master ALL", page, re.I)
    if not links:
        raise RuntimeError("no 'Special Event Master ALL' link on the page — "
                           "has its layout changed?")
    out = []
    by_year = {year: href for href, year in links}
    for year, href in sorted(by_year.items()):
        time.sleep(DELAY_S)
        pdf = fetch(urllib.parse.urljoin(base, href))
        if not pdf.startswith(b"%PDF"):
            raise RuntimeError(f"{href} is not a PDF")
        got = rpd_events(pdf_rows(pdf), int(year), source)
        if not got and int(year) >= datetime.now(PACIFIC).year:
            raise RuntimeError(f"{href}: no rows parsed — has the sheet changed?")
        out += got
    return out


KIND = {"ical": fetch_illuminate, "ical-multi": fetch_sfrecpark,
        "squarespace": fetch_squarespace, "html": fetch_alemany,
        "tribe": fetch_tribe, "pdf-table": fetch_rpd_master}


# --------------------------------------------------------------------------
# Venues
# --------------------------------------------------------------------------

def load_venues() -> list:
    """The register as a match list, longest matcher first."""
    try:
        data = json.loads(VENUES.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return []
    rows = []
    for key, v in (data.get("venues") or {}).items():
        for matcher in [key] + list(v.get("match") or []):
            rows.append((norm(matcher), v))
    rows.sort(key=lambda r: -len(r[0]))
    return rows


def match_venue(rows: list, location: str):
    """First venue whose matcher appears in the normalized location."""
    loc = norm(location)
    if not loc:
        return None
    for matcher, venue in rows:
        if matcher and matcher in loc:
            return venue
    return None


# Coordinates outside San Francisco aren't publishable — the Squarespace
# default is handled at the source, this box catches every other miss.
SF_BBOX = (37.70, 37.84, -122.55, -122.34)   # lat_min, lat_max, lng_min, lng_max


def in_sf(lat, lng) -> bool:
    return SF_BBOX[0] <= lat <= SF_BBOX[1] and SF_BBOX[2] <= lng <= SF_BBOX[3]


def resolve(events: list, today: date) -> tuple:
    """Attach venue name, coordinates and page path; drop what is past or far
    beyond the horizon."""
    venues = load_venues()
    horizon = today + timedelta(days=HORIZON_DAYS)
    unlocated, kept = {}, []

    for ev in events:
        ev["title"] = clean_title(ev["title"])
        start = datetime.fromisoformat(ev["start"])
        if start.date() > horizon or (ev.get("end")
                and datetime.fromisoformat(ev["end"]) < datetime.now(PACIFIC)):
            continue
        if not ev.get("end") and start.date() < today:
            continue  # a started all-day/no-end event is over for our purposes
        venue = match_venue(venues, ev.get("location") or "")
        if venue:
            ev["venue"] = venue["name"]
            if venue.get("path"):
                ev["path"] = venue["path"]
            if not ev.get("coords") and venue.get("lat") and venue.get("lng"):
                ev["coords"] = (venue["lat"], venue["lng"])
        else:
            ev["venue"] = venue_label(ev.get("location") or "")
        ev["title"] = drop_venue_prefix(ev["title"], ev["venue"])
        if ev.get("coords") and in_sf(*ev["coords"]):
            ev["lat"], ev["lng"] = ev["coords"]
        elif ev.get("location"):
            unlocated[norm(ev["location"])] = ev["location"]
        ev.pop("coords", None)
        ev.pop("location", None)
        kept.append(ev)
    return kept, unlocated


SHADOW_STOP = {"the", "and", "park", "square", "plaza", "with", "from",
               "golden", "gate", "francisco", "annual", "event", "events"}


def drop_shadowed(events: list) -> list:
    """An all-day row — Rec & Park's permit sheet, which has dates but no
    times — gives way to a timed listing of the same event on the venue's own
    calendar: same day, same venue, and a word of the title in common (or the
    other calendar's own name in it — the permit for Illuminate's concerts is
    'Illuminate Concert', whatever each night is called)."""
    def words(ev):
        return {w for w in norm(ev["title"]).split()
                if len(w) >= 4 and w not in SHADOW_STOP}

    timed = {}
    for ev in events:
        if not ev.get("all_day"):
            timed.setdefault(ev["start"][:10], []).append(ev)
    kept = []
    for ev in events:
        if ev.get("all_day"):
            here = ev.get("path") or ev.get("venue")
            mine = words(ev)
            if any((o.get("path") or o.get("venue")) == here
                   and o["source"] != ev["source"]
                   and (mine & words(o) or o["source"] in norm(ev["title"]).split())
                   for o in timed.get(ev["start"][:10], [])):
                continue
        kept.append(ev)
    return kept


def dedupe(events: list) -> list:
    # Two calendars can list one event — SF Rec & Park hosts the Sunset Dunes
    # series the Friends of Sunset Dunes also post. Same normalized title and
    # start time is the same event; a pin the source set on the event beats a
    # venue centroid from the register.
    events = drop_shadowed(events)
    merged = {}
    for ev in events:
        key = (norm(ev["title"]), ev["start"])
        if ev.get("all_day"):
            # A permit row per site: the same run at three squares is three
            # listings, each on its own square's page.
            key += (ev.get("path") or ev.get("venue") or "",)
        prev = merged.get(key)
        if prev is None:
            merged[key] = ev
            continue
        if ev.get("src_coords") and not prev.get("src_coords"):
            prev, ev = ev, prev
            merged[key] = prev
        for field in ("url", "lat", "lng", "end", "venue", "path"):
            if not prev.get(field) and ev.get(field):
                prev[field] = ev[field]
        prev["also_listed_by"] = sorted(set(
            prev.get("also_listed_by", [prev["source"]]) + [ev["source"]]))
    for ev in merged.values():
        ev.pop("src_coords", None)

    return sorted(merged.values(), key=lambda e: (e["start"], e["title"]))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("command", nargs="?", default="fetch",
                    choices=["fetch", "venues"])
    ap.add_argument("--source", help="fetch only this source id")
    ap.add_argument("--dry-run", action="store_true",
                    help="print what would be written; don't touch events.json")
    args = ap.parse_args()

    sources = json.loads(SOURCES.read_text(encoding="utf-8"))["sources"]
    if args.source:
        sources = [s for s in sources if s["id"] == args.source]
        if not sources:
            print(f"no source '{args.source}' in sources.json")
            return 1

    raw, errors, fetched_ids = [], [], set()
    for source in sources:
        if source.get("access") != "open":
            print(f"  {source['id']}: skipped — access {source.get('access')}")
            continue
        try:
            got = KIND[source["kind"]](source)
            raw += got
            fetched_ids.add(source["id"])
            print(f"  {source['id']}: {len(got)} events listed")
        except Exception as e:   # one dead calendar must not lose the rest
            errors.append(f"{source['id']}: {e}")
            print(f"  {source['id']}: FAILED — {e}")
        time.sleep(DELAY_S)

    today = datetime.now(PACIFIC).date()
    events, unlocated = resolve(raw, today)

    # Only the sources read this run are replaced. A calendar that was not
    # asked for (--source) or failed to answer keeps the slice the file
    # already holds, less what has since passed — a half-fetched events.json
    # is a worse state than a stale one, and a publisher's bad morning should
    # not empty its venues' panels.
    if OUT.exists():
        try:
            old_doc = json.loads(OUT.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            old_doc = {}
        now = datetime.now(PACIFIC)
        kept = [e for e in old_doc.get("events", [])
                if e.get("source") not in fetched_ids
                and datetime.fromisoformat(e.get("end") or e["start"]) >= (
                    now if e.get("end") else
                    datetime.combine(today, datetime.min.time(), PACIFIC))]
        # The register may have moved on since the kept slice was resolved —
        # a venue given a page, or a page moved — so re-match on the venue
        # name the slice carries and follow the register's current path.
        venues = load_venues()
        for ev in kept:
            ev["title"] = clean_title(ev["title"])
            venue = match_venue(venues, ev.get("venue") or "")
            if venue:
                ev["venue"] = venue["name"]
                if venue.get("path"):
                    ev["path"] = venue["path"]
                else:
                    ev.pop("path", None)
            ev["title"] = drop_venue_prefix(ev["title"], ev.get("venue"))
        if kept:
            events += kept
            print(f"  (kept {len(kept)} events from sources not read this run)")
    events = dedupe(events)

    if args.command == "venues":
        seen = sorted({(ev.get("venue") or "(none)") for ev in events})
        print("\nvenues seen:")
        # A venue needs a page for a dot (the dot opens it) and for a panel.
        for v in seen:
            flag = "no page " if not any(
                e.get("path") for e in events if e.get("venue") == v) else ""
            print(f"  {flag}{v}")
        return 0

    doc = {
        "fetched": datetime.now(PACIFIC).isoformat(timespec="seconds"),
        "horizon_days": HORIZON_DAYS,
        "events": events,
    }
    if unlocated:
        doc["unlocated_venues"] = sorted(unlocated.values())

    if args.dry_run:
        print(json.dumps(doc, indent=2, ensure_ascii=False)[:4000])
        print(f"\n{len(events)} events")
        return 0

    old = OUT.read_text(encoding="utf-8") if OUT.exists() else ""
    new = json.dumps(doc, indent=2, ensure_ascii=False) + "\n"
    if new == old:
        print("events.json unchanged")
    else:
        OUT.write_text(new, encoding="utf-8")
        print(f"events.json written: {len(events)} events"
              + (f", {len(unlocated)} unlocated venue(s)" if unlocated else ""))
    if errors:
        print("errors: " + "; ".join(errors))
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
