#!/usr/bin/env python3
"""Consistency checks for the events module. Stdlib only.

    python3 events/tools/check.py          # check everything
    python3 events/tools/check.py --stats  # ...and print what's listed

What it checks:
  * sources.json is well formed — unique ids, a known kind, an access flag,
    and the `feeds` list an ical-multi source needs;
  * venues.json — every venue has a name, coordinates come in pairs inside
    the San Francisco bounding box, matchers are non-empty, and a `path`
    points at a page that actually exists (the file holding the parcel the
    venue claims to be);
  * events.json — every event has the fields the renderers consume, its
    source is registered, its id is unique, its times parse and are ordered,
    its coordinates come in pairs inside the bounding box, its `path` names
    a real page, and nothing listed is already over relative to `fetched`.
"""
from __future__ import annotations

import argparse
import json
import sys
import zoneinfo
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent           # events/
REPO = ROOT.parent
PACIFIC = zoneinfo.ZoneInfo("America/Los_Angeles")
SF_BBOX = (37.70, 37.84, -122.55, -122.34)

KINDS = {"ical", "ical-multi", "squarespace", "html"}
ACCESS = {"open", "needs-human", "blocked"}

errors = []


def err(where, msg):
    errors.append(f"{where}: {msg}")


def in_sf(lat, lng):
    return SF_BBOX[0] <= lat <= SF_BBOX[1] and SF_BBOX[2] <= lng <= SF_BBOX[3]


def check_sources():
    if not (ROOT / "sources.json").exists():
        err("events/sources.json", "the register is missing")
        return {}
    data = json.loads((ROOT / "sources.json").read_text(encoding="utf-8"))
    sources = {}
    for s in data.get("sources", []):
        sid = s.get("id")
        if not sid:
            err("events/sources.json", "a source has no id")
            continue
        if sid in sources:
            err("events/sources.json", f"duplicate source id {sid!r}")
        for key in ("name", "url", "kind", "access", "note"):
            if not s.get(key):
                err("events/sources.json", f"{sid}: missing {key!r}")
        if s.get("kind") not in KINDS:
            err("events/sources.json", f"{sid}: kind {s.get('kind')!r} "
                                       f"is not one of {sorted(KINDS)}")
        if s.get("access") not in ACCESS:
            err("events/sources.json", f"{sid}: access {s.get('access')!r} "
                                       f"is not one of {sorted(ACCESS)}")
        if s.get("kind") == "ical-multi" and not s.get("feeds"):
            err("events/sources.json", f"{sid}: an ical-multi source needs a "
                                       "'feeds' list")
        sources[sid] = s
    return sources


def check_venues():
    path = ROOT / "venues.json"
    if not path.exists():
        err("events/venues.json", "the register is missing")
        return
    data = json.loads(path.read_text(encoding="utf-8"))
    for key, v in (data.get("venues") or {}).items():
        where = f"events/venues.json [{key}]"
        if not key.strip():
            err(where, "empty matcher")
        if not v.get("name"):
            err(where, "no name")
        for m in v.get("match") or []:
            if not m.strip():
                err(where, "an empty alternate matcher")
        lat, lng = v.get("lat"), v.get("lng")
        if (lat is None) != (lng is None):
            err(where, "lat and lng must come as a pair")
        elif lat is not None and not in_sf(lat, lng):
            err(where, f"({lat}, {lng}) is outside San Francisco")
        if v.get("path"):
            data_json = REPO / v["path"].strip("/") / "data.json"
            if not data_json.exists():
                err(where, f"path {v['path']} names no page")
        if (lat is None or not v.get("path")) and not v.get("note"):
            err(where, "no note — say where the coordinates came from, or "
                       "why there are none")


def check_events(sources):
    path = ROOT / "events.json"
    if not path.exists():
        err("events/events.json", "not fetched yet — run tools/fetch.py")
        return []
    doc = json.loads(path.read_text(encoding="utf-8"))
    try:
        fetched = datetime.fromisoformat(doc["fetched"])
    except (KeyError, ValueError):
        err("events/events.json", "missing or bad 'fetched' timestamp")
        return []

    seen_ids, seen_starts, prev_start = set(), set(), ""
    for i, ev in enumerate(doc.get("events") or []):
        where = f"events.json event {i} ({ev.get('title', '?')!r})"
        for key in ("id", "source", "title", "start", "url"):
            if not ev.get(key):
                err(where, f"missing {key!r}")
        if ev.get("id") in seen_ids:
            err(where, f"duplicate id {ev.get('id')!r}")
        seen_ids.add(ev.get("id"))
        if ev.get("source") not in sources:
            err(where, f"source {ev.get('source')!r} is not registered")
        if not str(ev.get("url", "")).startswith("http"):
            err(where, "url must be a link back to the listing")
        try:
            start = datetime.fromisoformat(ev["start"])
            end = datetime.fromisoformat(ev["end"]) if ev.get("end") else None
        except (KeyError, ValueError):
            err(where, "bad start/end timestamp")
            continue
        if end and end < start:
            err(where, "ends before it starts")
        over = end < fetched if end else start.date() < fetched.date()
        if over:
            err(where, "already over when fetched — resolve() should drop it")
        if ev["start"] < prev_start:
            err(where, "events are not sorted by start")
        prev_start = ev["start"]
        key = (start, ev.get("title"))
        if key in seen_starts:
            err(where, "two events share a title and start — dedup miss?")
        seen_starts.add(key)
        lat, lng = ev.get("lat"), ev.get("lng")
        if (lat is None) != (lng is None):
            err(where, "lat and lng must come as a pair")
        elif lat is not None and not in_sf(lat, lng):
            err(where, f"({lat}, {lng}) is outside San Francisco")
        if ev.get("path"):
            data_json = REPO / ev["path"].strip("/") / "data.json"
            if not data_json.exists():
                err(where, f"path {ev['path']} names no page")
    return doc.get("events") or []


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--stats", action="store_true")
    args = ap.parse_args()

    sources = check_sources()
    check_venues()
    events = check_events(sources)

    if args.stats and events:
        by_source = {}
        for e in events:
            by_source[e["source"]] = by_source.get(e["source"], 0) + 1
        mapped = sum(1 for e in events if e.get("lat"))
        paged = sum(1 for e in events if e.get("path"))
        print(f"{len(events)} events: " +
              ", ".join(f"{k} {v}" for k, v in sorted(by_source.items())))
        print(f"{mapped} with coordinates, {paged} on a page's parcel")

    if errors:
        print(f"\n{len(errors)} problem(s):")
        for e in errors:
            print("  " + e)
        return 1
    print("events module: all checks pass")
    return 0


if __name__ == "__main__":
    sys.exit(main())
