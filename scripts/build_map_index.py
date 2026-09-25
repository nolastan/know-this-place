#!/usr/bin/env python3
"""Regenerate shared/addresses.geojson from the content tree. Stdlib only.

One Point feature per documented address and per place page (a park, plaza
or place in a park — see REFERENCE.md → Place pages), carrying only what the
homepage map needs: the label it shows on hover ("t"), the page it opens on
click ("p"), and "r": 1 when the research module has published a finding onto
that page — the map draws those in the brick hue and the rest, pages that are
permit history and little else, in grey. Coordinates and labels come from each
page's data.json, or a place's place.json, which is the single source of truth;
a place is labelled by its name, since most have no street number. "r" comes
from research/findings, whose published entries each name the page they went
onto. This file is a derived index and is never edited by hand.

Run from anywhere: python3 scripts/build_map_index.py
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ADDRESS_DIR = re.compile(r"^\d+[a-z]?$")  # 123, 123a — same as validate.py
# "227 Dorland Street, San Francisco, CA 94114" → "227 Dorland Street". The
# city is the whole map; repeating it on every dot is noise.
LOCALITY = re.compile(r",\s*San Francisco.*$", re.I)


def researched_paths() -> set[str]:
    """Every page a research finding has been published onto. The publish
    record says only that it shipped; the page is the resolution's path."""
    paths = set()
    for path in sorted((ROOT / "research" / "findings").rglob("*.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        if not isinstance(data, dict):
            continue
        for finding in data.get("findings") or []:
            if (finding.get("publish") or {}).get("status") != "published":
                continue
            page = (finding.get("resolution") or {}).get("path")
            if page:
                paths.add(page)
    return paths


def main() -> None:
    content = ROOT / "san-francisco"
    features = []
    skipped = []
    researched = researched_paths()
    place_paths = set()

    pages = sorted(content.rglob("data.json")) if content.exists() else []
    places = sorted(content.rglob("place.json")) if content.exists() else []
    for data_path in pages + places:
        page_dir = data_path.parent
        is_place = data_path.name == "place.json"
        if not is_place and not ADDRESS_DIR.match(page_dir.name):
            continue
        try:
            data = json.loads(data_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            skipped.append(f"{data_path.relative_to(ROOT)}: invalid JSON")
            continue

        coords = data.get("coordinates") or {}
        lat, lng = coords.get("lat"), coords.get("lng")
        if not isinstance(lat, (int, float)) or not isinstance(lng, (int, float)):
            # No point guessing — a dot in the wrong place is worse than none.
            skipped.append(f"{data_path.relative_to(ROOT)}: no coordinates")
            continue

        path = data.get("path") or "/" + page_dir.relative_to(ROOT).as_posix() + "/"
        label = (data.get("name") if is_place else
                 LOCALITY.sub("", data.get("address") or "")).strip()
        props = {"t": label, "p": path}
        # Only on the pages that have it: absent is the common case, and this
        # file is fetched whole by every homepage visit.
        if path in researched:
            props["r"] = 1
        if is_place:
            place_paths.add(path)
        features.append((path, {
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [round(lng, 5), round(lat, 5)]},
            "properties": props,
        }))

    features.sort(key=lambda f: f[0])

    # One feature per line: a 1.4 MB single-line JSON blob is unreviewable in a
    # diff, and pages are added a handful at a time.
    lines = ['{"type":"FeatureCollection","features":[']
    body = [json.dumps(f, separators=(",", ":"), ensure_ascii=False) for _, f in features]
    lines.append(",\n".join(body))
    lines.append("]}")

    out = ROOT / "shared" / "addresses.geojson"
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    flagged = sum(1 for _, f in features if "r" in f["properties"])
    mapped_places = sum(1 for p, _ in features if p in place_paths)
    print(f"shared/addresses.geojson written with {len(features) - mapped_places} "
          f"address(es) and {mapped_places} place(s), {flagged} with published research")
    for note in skipped:
        print(f"  skipped — {note}")


if __name__ == "__main__":
    main()
