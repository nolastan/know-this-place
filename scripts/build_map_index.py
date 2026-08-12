#!/usr/bin/env python3
"""Regenerate shared/addresses.geojson from the content tree. Stdlib only.

One Point feature per documented address, carrying only what the homepage map
needs: the label it shows on hover ("t") and the page it opens on click ("p").
Coordinates come from each page's data.json, which is the single source of
truth; this file is a derived index and is never edited by hand.

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


def main() -> None:
    content = ROOT / "san-francisco"
    features = []
    skipped = []

    for data_path in sorted(content.rglob("data.json")) if content.exists() else []:
        page_dir = data_path.parent
        if not ADDRESS_DIR.match(page_dir.name):
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
        label = LOCALITY.sub("", data.get("address") or "").strip()
        features.append((path, {
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [round(lng, 5), round(lat, 5)]},
            "properties": {"t": label, "p": path},
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
    print(f"shared/addresses.geojson written with {len(features)} address(es)")
    for note in skipped:
        print(f"  skipped — {note}")


if __name__ == "__main__":
    main()
