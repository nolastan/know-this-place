#!/usr/bin/env python3
"""Regenerate shared/addresses.geojson from the content tree. Stdlib only.

One Point feature per documented address and per place page (a park, plaza
or place in a park — see REFERENCE.md → Place pages), carrying only what the
homepage map needs: the heading its card shows ("t") and the line under it
("s") — the page's own <h1> and .sub, less the neighborhood — the page the
card links to ("p"), and "r": 1 when the research module has published a finding onto
that page — the map draws those in the brick hue and the rest, pages that are
permit history and little else, in grey — and "ph", the page's own photo where
it has one, which the card shows in Street View's place. Coordinates and labels come from each
page's data.json, or a place's place.json, which is the single source of truth,
through the same seed_pages functions that write the page's hero. "r" comes
from research/findings, whose published entries each name the page they went
onto. This file is a derived index and is never edited by hand.

It also writes the homepage map's page lots: shared/map/pages/<slug>.json, the
documented pages of each neighborhood keyed by the lot they stand on, and
shared/map/index.json (see write_page_lots). They need the committed lot cache
in shared/map/, which `seed_pages.py lots` refreshes from DataSF.

Run from anywhere: python3 scripts/build_map_index.py
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
from seed_pages import (hero_lines, page_photo, place_sub, read_lot_cache,  # noqa: E402
                        polygons_contain, BOUNDARY_SOURCE, DS_ANALYSIS_NEIGHBORHOODS, MAP_DIR)

ADDRESS_DIR = re.compile(r"^\d+[a-z]?$")  # 123, 123a — same as validate.py


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
        if is_place:
            heading, sub = data.get("name") or "", place_sub(data)
        else:
            heading, sub = hero_lines(data)
        props = {"t": heading.strip(), "s": sub, "p": path}
        # Only on the pages that have it: absent is the common case, and this
        # file is fetched whole by every homepage visit.
        if path in researched:
            props["r"] = 1
        photo = page_photo({**data, "path": path})
        if photo:
            props["ph"] = path + photo["file"]
        if is_place:
            place_paths.add(path)
        features.append((path, {
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [round(lng, 5), round(lat, 5)]},
            "properties": props,
        }))

    features.sort(key=lambda f: f[0])
    write_page_lots(features)

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


def write_page_lots(features: list) -> None:
    """The homepage map's second index: which lot each page stands on, one file
    per neighborhood, so a reader who picks a neighborhood fetches only its own.

    shared/map/pages/<slug>.json  [{"l": lot, "t", "s", "p", "r"?}, …]
    shared/map/index.json         [{"slug", "name", "pages", "hub"?}, …]

    A page's lot is its APN's where that is a lot in shared/map/ (the lot cache
    `seed_pages.py lots` writes); otherwise — a condominium building, a place,
    an APN since retired — the lot its point falls in. Both files are derived
    and gitignored."""
    areas, lots = read_lot_cache()
    if not areas:
        print("  no lot cache in shared/map/ — run `seed_pages.py lots`; page lots skipped")
        return
    # A coarse grid over the lots' bbox centres, for the point lookups.
    def cell(x, y):
        return int(x * 200), int(y * 200)      # ~450 m
    grid = {}
    for m, lot in lots.items():
        b = lot["bbox"]
        grid.setdefault(cell((b[0] + b[2]) / 2, (b[1] + b[3]) / 2), []).append(m)

    def lot_at(x, y):
        cx, cy = cell(x, y)
        for i in (cx - 1, cx, cx + 1):
            for j in (cy - 1, cy, cy + 1):
                for m in grid.get((i, j), ()):
                    b = lots[m]["bbox"]
                    if (b[0] <= x <= b[2] and b[1] <= y <= b[3]
                            and polygons_contain(lots[m]["polys"], x, y)):
                        return m
        return None

    apns = {}
    for data_path in (ROOT / "san-francisco").rglob("data.json"):
        if ADDRESS_DIR.match(data_path.parent.name):
            try:
                rec = json.loads(data_path.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                continue
            apn = (rec.get("apn") or "").replace("-", "")
            if apn:
                apns[rec.get("path") or "/" + data_path.parent.relative_to(ROOT).as_posix() + "/"] = apn
    by_area = {slug: [] for slug in areas}
    placed = unplaced = 0
    for path, f in features:
        m = apns.get(path)
        if m not in lots:
            lng, lat = f["geometry"]["coordinates"]
            m = lot_at(lng, lat)
        if not m:
            unplaced += 1
            continue
        placed += 1
        p = f["properties"]
        rec = {"l": m, "t": p["t"], "s": p["s"], "p": p["p"]}
        if p.get("r"):
            rec["r"] = 1
        by_area[lots[m]["area"]].append(rec)
    out = MAP_DIR / "pages"
    out.mkdir(parents=True, exist_ok=True)
    for slug, recs in by_area.items():
        (out / f"{slug}.json").write_text(
            json.dumps(recs, separators=(",", ":"), ensure_ascii=False) + "\n", encoding="utf-8")
    hub = {name: f"/san-francisco/{d}/" for d, (ds, name) in BOUNDARY_SOURCE.items()
           if ds == DS_ANALYSIS_NEIGHBORHOODS}
    index = []
    for slug, a in areas.items():
        row = {"slug": slug, "name": a["name"], "pages": len(by_area[slug])}
        if a["name"] in hub:
            row["hub"] = hub[a["name"]]
        index.append(row)
    (MAP_DIR / "index.json").write_text(
        json.dumps(index, separators=(",", ":")) + "\n", encoding="utf-8")
    print(f"shared/map/pages/ written: {placed} page(s) on their lots, {unplaced} with no lot")


if __name__ == "__main__":
    main()
