#!/usr/bin/env python3
"""Build the events surfaces from events/events.json. Stdlib only.

Two derived artifacts, both gitignored like every other build output:

    shared/events.geojson   one Point feature per upcoming event that has a
                            coordinate and a page — the homepage map's event
                            layer, whose dots open that page. The
                            six-day window is applied in the browser, off the
                            "d" property, so a stale build fades rather than
                            being wrong.
    events/index.html       /events — every upcoming event the calendars
                            announced, grouped by day, each entry linking back
                            to the listing that published it. Static HTML, no
                            JavaScript — it has to be readable without it.

The data file itself is written by events/tools/fetch.py; this script only
reads it, the way build_map_index.py only reads data.json. Run from anywhere:

    python3 scripts/build_events.py
"""
import hashlib
import html
import json
import re
from collections import defaultdict
from datetime import date, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EVENTS = ROOT / "events" / "events.json"
SOURCES = ROOT / "events" / "sources.json"
GEOJSON = ROOT / "shared" / "events.geojson"
OUT = ROOT / "events" / "index.html"

CONFIG = json.loads((ROOT / "shared" / "site-config.json").read_text())
SITE = CONFIG["site_url"].rstrip("/")
REPO = CONFIG["repo_url"].rstrip("/")
_CSS_HASH = hashlib.md5((ROOT / "shared" / "site.css").read_bytes()).hexdigest()[:8]

MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
          "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
MONTHS_LONG = ["January", "February", "March", "April", "May", "June", "July",
               "August", "September", "October", "November", "December"]
WEEKDAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday",
            "Saturday", "Sunday"]


def esc(s) -> str:
    return html.escape(str(s or ""), quote=False)


def esca(s) -> str:
    return html.escape(str(s or ""), quote=True)


def clock(iso: str) -> str:
    """'2026-09-27T14:30:00-07:00' → '2:30 pm' (':00' drops to '2 pm')."""
    dt = datetime.fromisoformat(iso)
    h, m = dt.hour % 12 or 12, dt.minute
    ap = "am" if dt.hour < 12 else "pm"
    return f"{h}:{m:02d} {ap}" if m else f"{h} {ap}"


def time_range(ev: dict) -> str:
    """'10 am–1:30 pm', collapsing a shared am/pm: '10–11:30 am'."""
    a = clock(ev["start"])
    if not ev.get("end"):
        return a
    b = clock(ev["end"])
    if a[-2:] == b[-2:]:
        a = a[:-3]
    return f"{a}–{b}"


def day_label(d: date, today: date) -> str:
    base = f"{WEEKDAYS[d.weekday()]}, {MONTHS_LONG[d.month - 1]} {d.day}"
    if d == today:
        return f"Today · {base}"
    if d == date.fromordinal(today.toordinal() + 1):
        return f"Tomorrow · {base}"
    return base


def source_names() -> dict:
    try:
        data = json.loads(SOURCES.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return {s["id"]: s["name"] for s in data.get("sources") or []}


def load() -> tuple:
    try:
        doc = json.loads(EVENTS.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return "", []
    return doc.get("fetched", ""), doc.get("events") or []


def anchor(ev: dict) -> str:
    """The event's row id on /events — 'sfrecpark:10515' → 'e-sfrecpark-10515'."""
    return "e-" + re.sub(r"[^a-z0-9]+", "-",
                         str(ev.get("id") or "").lower()).strip("-")


# ---------------------------------------------------------------- geojson

def build_geojson(events: list, names: dict) -> int:
    features = []
    for ev in events:
        # A dot opens the venue's page, so an event with no page gets no dot —
        # it still lists on /events, which links the calendar that posted it.
        lat, lng = ev.get("lat"), ev.get("lng")
        if (not ev.get("path") or not isinstance(lat, (int, float))
                or not isinstance(lng, (int, float))):
            continue
        props = {
            "t": ev["title"],
            "v": ev.get("venue") or "",
            "d": ev["start"],
            "tm": time_range(ev),
            "s": names.get(ev.get("source"), ev.get("source") or ""),
            "p": ev["path"],
        }
        features.append({
            "type": "Feature",
            "geometry": {"type": "Point",
                         "coordinates": [round(lng, 5), round(lat, 5)]},
            "properties": props,
        })
    body = [json.dumps(f, separators=(",", ":"), ensure_ascii=False)
            for f in features]
    out = ('{"type":"FeatureCollection","features":[\n'
           + ",\n".join(body) + "\n]}\n")
    GEOJSON.write_text(out, encoding="utf-8")
    return len(features)


# ---------------------------------------------------------------- the page

def event_row(ev: dict, names: dict) -> str:
    title = (f'<a class="event-title" href="{esca(ev["url"])}">'
             f'{esc(ev["title"])}</a>' if ev.get("url")
             else f'<span class="event-title">{esc(ev["title"])}</span>')
    venue = ev.get("venue") or ""
    if ev.get("path") and venue:
        where = f'<a class="event-where" href="{esca(ev["path"])}">{esc(venue)}</a>'
    elif venue:
        where = f'<span class="event-where">{esc(venue)}</span>'
    else:
        where = ""
    src = names.get(ev.get("source"), ev.get("source") or "")
    return (f'    <li class="event-row" id="{esca(anchor(ev))}">'
            f'<span class="event-when">{esc(time_range(ev))}</span>'
            f'{title}{where}'
            f'<span class="event-src">{esc(src)}</span></li>')


def render(fetched: str, events: list, names: dict) -> str:
    today = date.today()
    fetched_date = fetched[:10]
    fetched_long = (f"{MONTHS_LONG[int(fetched_date[5:7]) - 1]} "
                    f"{int(fetched_date[8:10])}, {fetched_date[:4]}"
                    if fetched_date else "an earlier date")

    by_day = defaultdict(list)
    for ev in events:
        by_day[datetime.fromisoformat(ev["start"]).date()].append(ev)

    sections = []
    for d in sorted(by_day):
        rows = "\n".join(event_row(ev, names) for ev in by_day[d])
        sections.append(
            f'  <div class="section-head"><span class="ic ic-calendar"></span>'
            f'<h2>{esc(day_label(d, today))}</h2></div>\n'
            f'  <ul class="event-rows">\n{rows}\n  </ul>')

    if not sections:
        sections.append('  <p class="lead">Nothing is listed — the calendars '
                        'have not announced an upcoming event.</p>')

    try:
        sources = json.loads(SOURCES.read_text(encoding="utf-8")).get("sources", [])
        sources_note = ", ".join(
            f'<a href="{esca(s.get("page") or s["url"])}">{esc(s["name"])}</a>'
            for s in sources if s.get("access") == "open")
    except (OSError, json.JSONDecodeError):
        sources_note = "the registered calendars"

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Upcoming events — Know This Place</title>
  <meta name="description" content="{len(events)} upcoming events in San Francisco's public spaces, read from the venues' own calendars on {fetched_long}.">
  <link rel="canonical" href="{SITE}/events/">
  <link rel="icon" href="/favicon.ico" sizes="32x32">
  <link rel="icon" href="/shared/icon.svg" type="image/svg+xml">
  <link rel="apple-touch-icon" href="/apple-touch-icon.png">
  <link rel="manifest" href="/shared/site.webmanifest">
  <link rel="stylesheet" href="/shared/site.css?v={_CSS_HASH}">
  <script type="module" src="/shared/site.js"></script>
</head>
<body>
<header class="site-header">
  <a class="wordmark" href="/">Know This Place</a>
  <nav class="breadcrumb" aria-label="Breadcrumb">
    <a href="/">Home</a>
    <span aria-current="page">Upcoming events</span>
  </nav>
</header>

<main>
  <h1>Upcoming events</h1>
  <p class="lead">What San Francisco's public-space calendars have announced,
  read {fetched_long} from {sources_note}. Each entry links the listing that
  published it; a venue the site documents links its page. Events within six
  days also appear as dots on the homepage map, and events at a park, a plaza
  or a building the site documents appear on its page for thirty.</p>

{chr(10).join(sections)}
</main>

<footer class="site-footer">
  <p class="feedback-cta">This page is generated. Run
  <a href="{REPO}/blob/main/scripts/build_events.py">scripts/build_events.py</a>
  to rebuild it from <code>events/events.json</code>.</p>
  <p class="colophon">Part of <a href="/">Know This Place</a>, a community
  encyclopedia of the built environment. Facts are cited; pages are reviewed
  by people. <a href="{REPO}">Source</a>.</p>
</footer>
</body>
</html>
"""


def main() -> int:
    fetched, events = load()
    names = source_names()
    n_geo = build_geojson(events, names)
    OUT.write_text(render(fetched, events, names), encoding="utf-8")
    print(f"events/index.html: {len(events)} events listed; "
          f"shared/events.geojson: {n_geo} dots")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
