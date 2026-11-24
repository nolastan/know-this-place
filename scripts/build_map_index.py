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
import math
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
from seed_pages import (forwarding_parcel, forwards, hero_lines, page_photo,  # noqa: E402
                        place_sub, read_lot_cache, polygons_contain, BOUNDARY_SOURCE,
                        _pack, _polys_bbox, _unpack, unpack_polygons,
                        DS_ANALYSIS_NEIGHBORHOODS, MAP_DIR)

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
    place_parcels = {}
    place_part_of = {}

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

        # A parcel that is wholly one park forwards to the park's page, and
        # the park has its own dot.
        if not is_place and forwards(data):
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
        # A park whose parcel forwards to it shows the parcel's photo.
        parcel = forwarding_parcel(data) if is_place else None
        if parcel and not data.get("photo") and page_photo(parcel):
            data, path_for_photo = parcel, parcel["path"]
        else:
            path_for_photo = path
        photo = page_photo({**data, "path": path_for_photo})
        if photo:
            props["ph"] = path_for_photo + photo["file"]
        if is_place:
            place_paths.add(path)
            place_parcels[path] = [m.replace("-", "") for m in data.get("parcels") or []]
            part_of = data.get("part_of") or {}
            if part_of.get("path") and part_of.get("name"):
                place_part_of[path] = (part_of["path"], part_of["name"])
        features.append((path, {
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [round(lng, 5), round(lat, 5)]},
            "properties": props,
        }))

    features.sort(key=lambda f: f[0])
    write_page_lots(features, place_parcels, place_part_of)

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


def write_page_lots(features: list, place_parcels: dict, place_part_of: dict) -> None:
    """The homepage map's second index: which lot each page stands on, one file
    per neighborhood, so a reader who picks a neighborhood fetches only its own.

    shared/map/pages/<slug>.json  [{"l": lot, "t", "s", "p", "r"?}, …]
    shared/map/index.json         [{"slug", "name", "pages", "hub"?}, …]

    A page's lot is its APN's where that is a lot in shared/map/ (the lot cache
    `seed_pages.py lots` writes); otherwise — a condominium building, a place,
    an APN since retired — the lot its point falls in. A place stands on every
    lot of the parcels it covers: its point is often in the street between two
    of them (Mission Dolores Park's lies on the line between its two parcels),
    and a park drawn as one lot of several reads as a park with no page. A
    place drawn by its parcels follows every other record in each file, so
    that on a lot it covers it is drawn on top and takes the click — over the
    parcel's own address page. A place with no parcel of its own stands on
    the lot its point falls in only when no other page stands there by its
    own record: Golden Gate Park's gardens and lakes are all inside its one
    parcel, and the last of them drawn would otherwise answer for the whole
    park (Strybing Arboretum did). Such a place names the park it is part of,
    and that park's own page — Golden Gate Park's is its neighborhood hub —
    goes on the lot instead, on top, so a tap anywhere in the park opens the
    park. Both files are derived and gitignored."""
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
    def covered(f):
        return [m for m in place_parcels.get(f[0], ()) if m in lots]
    # Stable: address pages keep their order, then the places drawn by parcel.
    ordered = sorted(features, key=lambda f: bool(covered(f)))
    # Lots a page stands on by its own record: an address page's APN, a
    # place's parcels. A place with no parcel of its own never lands on one of
    # these by its point — it stands inside a larger parcel that has its page.
    claimed = {apns[p] for p, _ in features if apns.get(p) in lots}
    claimed.update(m for f in features for m in covered(f))
    parks = {}      # lot → (path, name) of the park its unplaced places are part of
    for path, f in ordered:
        on = covered((path, f))
        if not on:
            m = apns.get(path)
            if m not in lots:
                lng, lat = f["geometry"]["coordinates"]
                m = lot_at(lng, lat)
                if path in place_parcels and m in claimed:
                    if path in place_part_of:
                        parks.setdefault(m, place_part_of[path])
                    m = None
            on = [m] if m else []
        if not on:
            unplaced += 1
            continue
        placed += 1
        p = f["properties"]
        for m in on:
            rec = {"l": m, "t": p["t"], "s": p["s"], "p": p["p"]}
            if p.get("r"):
                rec["r"] = 1
            by_area[lots[m]["area"]].append(rec)
    for m, (path, name) in sorted(parks.items()):
        by_area[lots[m]["area"]].append({"l": m, "t": name, "s": "", "p": path})
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
    photos = {p: f["properties"]["ph"] for p, f in features if f["properties"].get("ph")}
    write_near_tiles(areas, by_area, photos)


# The address page's map is a fixed view of the blocks around the building,
# so it fetches only the few cells of this grid that view covers. ~440 m on a
# side at San Francisco's latitude: a wide desktop band takes three or four
# across, a phone one or two.
NEAR_CELL = (0.005, 0.004)      # degrees of longitude, latitude


def _near_cells(bbox: tuple):
    """Every grid cell a (minx, miny, maxx, maxy) box touches."""
    w, h = NEAR_CELL
    for i in range(math.floor(bbox[0] / w), math.floor(bbox[2] / w) + 1):
        for j in range(math.floor(bbox[1] / h), math.floor(bbox[3] / h) + 1):
            yield i, j


def _clip_ring(ring: list, box: tuple) -> list:
    """Sutherland–Hodgman: a closed ring cut to an axis-aligned box. Fill
    only — the cut runs along the box's edge, where nothing is stroked."""
    x0, y0, x1, y1 = box
    pts = ring[:-1] if ring and ring[0] == ring[-1] else ring
    for inside, cut in (
            (lambda p: p[0] >= x0, lambda a, b: (x0, a[1] + (b[1] - a[1]) * (x0 - a[0]) / (b[0] - a[0]))),
            (lambda p: p[0] <= x1, lambda a, b: (x1, a[1] + (b[1] - a[1]) * (x1 - a[0]) / (b[0] - a[0]))),
            (lambda p: p[1] >= y0, lambda a, b: (a[0] + (b[0] - a[0]) * (y0 - a[1]) / (b[1] - a[1]), y0)),
            (lambda p: p[1] <= y1, lambda a, b: (a[0] + (b[0] - a[0]) * (y1 - a[1]) / (b[1] - a[1]), y1))):
        out = []
        for k, cur in enumerate(pts):
            prev = pts[k - 1]
            if inside(cur):
                if not inside(prev):
                    out.append(cut(prev, cur))
                out.append(cur)
            elif inside(prev):
                out.append(cut(prev, cur))
        pts = out
        if not pts:
            break
    return pts


def write_near_tiles(areas: dict, by_area: dict, photos: dict) -> None:
    """The address page map's data: shared/map/near/<i>_<j>.json, one file per
    NEAR_CELL of the grid, holding everything that touches the cell —

      "o"       the cell's south-west corner, whole microdegrees
      "land"    the city's land cut to the cell, packed off "o"
      "lots"    [[id, z, packed], …], each lot whose box touches the cell
      "streets" [[id, name, class, packed], …], likewise
      "pages"   [{"l", "t", "s", "p", "r"?, "ph"?}, …], the pages on those lots

    A lot or a street that crosses a cell edge is in every cell it touches;
    the page dedupes by id. Packing is the lot cache's (seed_pages.py → "The
    homepage map's lot cache"), rebased to the cell. Derived and gitignored."""
    out = MAP_DIR / "near"
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)
    w, h = NEAR_CELL
    cells = {}

    def cell(key):
        if key not in cells:
            i, j = key
            cells[key] = {"o": [round(i * w * 1e6), round(j * h * 1e6)],
                          "land": [], "lots": [], "streets": [], "pages": []}
        return cells[key]

    def rebase(flat, frm, to):
        return [flat[0] + frm[0] - to[0], flat[1] + frm[1] - to[1], *flat[2:]]

    pages_on = {}
    for recs in by_area.values():
        for rec in recs:
            rec = dict(rec)
            if rec["p"] in photos:
                rec["ph"] = photos[rec["p"]]
            pages_on.setdefault(rec["l"], []).append(rec)

    for a in areas.values():
        f = MAP_DIR / "lots" / f"{a['slug']}.json"
        if not f.exists():
            continue
        lf = json.loads(f.read_text(encoding="utf-8"))
        for m, z, packed in lf["lots"]:
            bbox = _polys_bbox(unpack_polygons(packed, tuple(lf["o"])))
            for key in _near_cells(bbox):
                c = cell(key)
                c["lots"].append([m, z, [[rebase(r, lf["o"], c["o"]) for r in poly] for poly in packed]])
                c["pages"].extend(pages_on.get(m, ()))

    streets = json.loads((MAP_DIR / "streets.json").read_text(encoding="utf-8"))
    so = streets["o"]
    for k, (n, c_, flat) in enumerate(streets["s"]):
        pts = _unpack(flat, tuple(so))
        xs, ys = [p[0] for p in pts], [p[1] for p in pts]
        for key in _near_cells((min(xs), min(ys), max(xs), max(ys))):
            if key in cells:      # a street through no lot's cell is in the bay
                cells[key]["streets"].append([k, streets["names"][n], c_, rebase(flat, so, cells[key]["o"])])

    # The land: every neighborhood, cut to the cell. A hair over the cell's
    # own edges, so neighbouring cells overlap rather than leave a seam.
    pad = 2e-6
    for (i, j), c in cells.items():
        box = (i * w - pad, j * h - pad, (i + 1) * w + pad, (j + 1) * h + pad)
        origin = tuple(c["o"])
        for a in areas.values():
            b = a["bbox"]
            if b[2] < box[0] or b[0] > box[2] or b[3] < box[1] or b[1] > box[3]:
                continue
            for poly in a["polys"]:
                rings = [r for r in (_clip_ring(ring, box) for ring in poly) if len(r) >= 3]
                if rings:
                    c["land"].append([_pack(r, origin) for r in rings])

    total = 0
    for (i, j), c in cells.items():
        text = json.dumps(c, separators=(",", ":"), ensure_ascii=False)
        total += len(text)
        (out / f"{i}_{j}.json").write_text(text + "\n", encoding="utf-8")
    print(f"shared/map/near/ written: {len(cells)} cell(s), {total / 1e6:.1f} MB")


if __name__ == "__main__":
    main()
