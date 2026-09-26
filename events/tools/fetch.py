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

Three shapes of calendar, one parser each — see events/AGENTS.md:

    ical          one iCalendar feed per source (illuminate.org)
    ical-multi    the same feed once per CivicPlus calendar id (sfrecpark.org)
    squarespace   <collection>?format=json `upcoming` array (natureinthecity,
                  sunsetdunes)
    html          a hand-maintained page with no feed (alemanyfarm.org)

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
import urllib.parse
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


KIND = {"ical": fetch_illuminate, "ical-multi": fetch_sfrecpark,
        "squarespace": fetch_squarespace, "html": fetch_alemany}


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


def dedupe(events: list) -> list:
    # Two calendars can list one event — SF Rec & Park hosts the Sunset Dunes
    # series the Friends of Sunset Dunes also post. Same normalized title and
    # start time is the same event; a pin the source set on the event beats a
    # venue centroid from the register.
    merged = {}
    for ev in events:
        key = (norm(ev["title"]), ev["start"])
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
