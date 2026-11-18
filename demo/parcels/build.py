#!/usr/bin/env python3
"""DEMO ONLY — parcel-outline map prototypes. Stdlib only.

Builds the data the three prototypes under demo/parcels/ read:

  data/pages.geojson   one polygon per documented page's lot (the dots, as lots)
  data/lots/I_J.json   every active lot in the city, cut into ~1 km cells
  data/lots/index.json the cells and their bounding boxes
  data/streets.geojson street centerlines, named and classed (for labels)
  data/land.geojson    the city's land (Analysis Neighborhoods), so water reads
                       as water when there is no basemap
  locator/<slug>/      copies of a few built address pages whose Mapbox locator
                       band is replaced by inline SVG drawn from the lots

Sources (DataSF, retrieved by this script into .cache/parcels/):
  acdm-wktn  Parcels — Active and Retired (shape, mapblklot, zoning_code)
  3psu-pn9h  Streets — Active and Retired (line, streetname, classcode)
  j2bu-swwd  Analysis Neighborhoods (the_geom)

Run after `python3 scripts/build_site.py` (the locator copies start from the
built pages):  python3 demo/parcels/build.py
"""
import html
import json
import math
import re
import sys
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
CACHE = ROOT / ".cache" / "parcels"
OUT = HERE / "data"
sys.path.insert(0, str(ROOT / "scripts"))
from seed_pages import hero_lines, place_sub  # noqa: E402
from build_map_index import researched_paths, ADDRESS_DIR  # noqa: E402

API = "https://data.sf.gov/resource/"
KX = 111320 * math.cos(math.radians(37.76))   # metres per degree of longitude
KY = 110540                                   # metres per degree of latitude
CELL = (0.012, 0.009)                         # degrees: about 1 km square


# --- fetching -------------------------------------------------------------
def fetch(dataset: str, select: str, where: str, name: str, page=50000) -> list:
    path = CACHE / f"{name}.json"
    if path.exists():
        return json.loads(path.read_text())
    CACHE.mkdir(parents=True, exist_ok=True)
    rows, offset = [], 0
    while True:
        q = urllib.parse.urlencode({"$select": select, "$where": where,
                                    "$order": ":id", "$limit": page, "$offset": offset})
        with urllib.request.urlopen(f"{API}{dataset}.json?{q}", timeout=600) as r:
            chunk = json.load(r)
        rows += chunk
        print(f"  {dataset}: {len(rows)} rows", flush=True)
        if len(chunk) < page:
            break
        offset += page
    path.write_text(json.dumps(rows))
    return rows


# --- geometry -------------------------------------------------------------
def dp(pts: list, eps_m: float) -> list:
    """Douglas–Peucker in local metres, endpoints kept."""
    if len(pts) < 3:
        return pts
    keep = {0, len(pts) - 1}
    stack = [(0, len(pts) - 1)]
    while stack:
        i, j = stack.pop()
        ax, ay = pts[i][0] * KX, pts[i][1] * KY
        bx, by = pts[j][0] * KX, pts[j][1] * KY
        dx, dy = bx - ax, by - ay
        L = dx * dx + dy * dy
        far, far_d = None, eps_m
        for q in range(i + 1, j):
            px, py = pts[q][0] * KX, pts[q][1] * KY
            t = 0 if L == 0 else max(0, min(1, ((px - ax) * dx + (py - ay) * dy) / L))
            d = math.hypot(px - ax - t * dx, py - ay - t * dy)
            if d > far_d:
                far, far_d = q, d
        if far is not None:
            keep.add(far)
            stack += [(i, far), (far, j)]
    return [pts[k] for k in sorted(keep)]


def polys_of(geom: dict) -> list:
    if not geom:
        return []
    return geom["coordinates"] if geom["type"] == "MultiPolygon" else [geom["coordinates"]]


def simplify_polys(polys: list, eps: float, nd=6) -> list:
    out = []
    for poly in polys:
        rings = []
        for ring in poly:
            r = [[round(x, nd), round(y, nd)] for x, y in dp(ring, eps)]
            if len(r) >= 4:
                rings.append(r)
        if rings:
            out.append(rings)
    return out


def bbox(polys: list) -> tuple:
    xs = [p[0] for poly in polys for ring in poly for p in ring]
    ys = [p[1] for poly in polys for ring in poly for p in ring]
    return min(xs), min(ys), max(xs), max(ys)


def in_ring(x, y, ring) -> bool:
    inside = False
    for (x1, y1), (x2, y2) in zip(ring, ring[1:]):
        if (y1 > y) != (y2 > y) and x < (x2 - x1) * (y - y1) / (y2 - y1) + x1:
            inside = not inside
    return inside


def contains(polys, x, y) -> bool:
    return any(in_ring(x, y, poly[0]) and not any(in_ring(x, y, h) for h in poly[1:])
               for poly in polys)


def geom(polys: list) -> dict:
    if len(polys) == 1:
        return {"type": "Polygon", "coordinates": polys[0]}
    return {"type": "MultiPolygon", "coordinates": polys}


def dump(path: Path, obj) -> int:
    path.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(obj, separators=(",", ":"), ensure_ascii=False)
    path.write_text(text, encoding="utf-8")
    return len(text.encode())


# --- build ----------------------------------------------------------------
def main() -> None:
    print("==> fetching (cached in .cache/parcels/)")
    parcels = fetch("acdm-wktn", "blklot,mapblklot,zoning_code,shape",
                    "active=true", "parcels")
    streets = fetch("3psu-pn9h", "cnn,streetname,layer,classcode,line",
                    "active=true", "streets")
    nhoods = fetch("j2bu-swwd", "nhood,the_geom", "1=1", "nhoods")

    print("==> lots")
    blk2map, lots, public = {}, {}, set()
    for r in parcels:
        b = r.get("blklot")
        m = r.get("mapblklot") or b
        blk2map[b] = m
        if (r.get("zoning_code") or "").startswith("P"):
            public.add(m)
        if m not in lots and r.get("shape"):
            s = simplify_polys(polys_of(r["shape"]), 0.4)
            if s:
                lots[m] = (s, bbox(s))
    print(f"    {len(parcels)} parcels → {len(lots)} lots")

    # Spatial index: lot ids per cell, by each lot's bbox centre.
    x0, y0 = -122.52, 37.70
    cell_of = lambda x, y: (int((x - x0) // CELL[0]), int((y - y0) // CELL[1]))
    cells: dict[tuple, list] = {}
    for m, (s, bb) in lots.items():
        cells.setdefault(cell_of((bb[0] + bb[2]) / 2, (bb[1] + bb[3]) / 2), []).append(m)

    def lots_near(x, y, r=1):
        cx, cy = cell_of(x, y)
        for i in range(cx - r, cx + r + 1):
            for j in range(cy - r, cy + r + 1):
                yield from cells.get((i, j), ())

    def lot_at(x, y):
        for m in lots_near(x, y):
            s, bb = lots[m]
            if bb[0] <= x <= bb[2] and bb[1] <= y <= bb[3] and contains(s, x, y):
                return m
        return None

    print("==> pages")
    researched = researched_paths()
    content = ROOT / "san-francisco"
    feats, how = [], {"apn": 0, "point": 0, "none": 0}
    sources = sorted(content.rglob("data.json")) + sorted(content.rglob("place.json"))
    for f in sources:
        is_place = f.name == "place.json"
        if not is_place and not ADDRESS_DIR.match(f.parent.name):
            continue
        rec = json.loads(f.read_text(encoding="utf-8"))
        c = rec.get("coordinates") or {}
        lat, lng = c.get("lat"), c.get("lng")
        if not isinstance(lat, (int, float)):
            continue
        path = rec.get("path") or "/" + f.parent.relative_to(ROOT).as_posix() + "/"
        m = None
        if not is_place:
            apn = (rec.get("apn") or "").replace("-", "")
            m = blk2map.get(apn) if apn else None
            if m in lots:
                how["apn"] += 1
            else:
                m = None
        if m is None:
            m = lot_at(lng, lat)
            how["point" if m else "none"] += 1
        if m is None:
            continue
        if is_place:
            t, s = rec.get("name") or "", place_sub(rec)
        else:
            t, s = hero_lines(rec)
        props = {"t": t.strip(), "s": s, "p": path, "l": m}
        if path in researched:
            props["r"] = 1
        if is_place:
            props["k"] = "place"
        feats.append({"type": "Feature", "geometry": geom(lots[m][0]), "properties": props})
    # The largest lots first, so a small lot inside a park draws on top.
    feats.sort(key=lambda f: -(lambda b: (b[2] - b[0]) * (b[3] - b[1]))(lots[f["properties"]["l"]][1]))
    n = dump(OUT / "pages.geojson", {"type": "FeatureCollection", "features": feats})
    print(f"    {len(feats)} page lots (by APN {how['apn']}, by point {how['point']}, "
          f"unplaced {how['none']}) — {n/1e6:.1f} MB")
    page_lots = {f["properties"]["l"] for f in feats}

    print("==> lot cells")
    index, total = [], 0
    for (i, j), ids in sorted(cells.items()):
        fc = {"type": "FeatureCollection", "features": [
            {"type": "Feature", "geometry": geom(lots[m][0]),
             "properties": {k: 1 for k, v in (("z", m in public), ("pg", m in page_lots)) if v}}
            for m in ids]}
        total += dump(OUT / "lots" / f"{i}_{j}.json", fc)
        bb = [x0 + i * CELL[0], y0 + j * CELL[1], x0 + (i + 1) * CELL[0], y0 + (j + 1) * CELL[1]]
        index.append({"id": f"{i}_{j}", "bbox": [round(v, 4) for v in bb], "n": len(ids)})
    dump(OUT / "lots" / "index.json", index)
    print(f"    {len(index)} cells, {total/1e6:.1f} MB")

    print("==> streets")
    skip = {"PAPER", "PAPER_FWYS", "PAPER_WATER", "PSEUDO"}
    sfeats = []
    for r in streets:
        if r.get("layer") in skip or not r.get("line"):
            continue
        g = r["line"]
        lines = g["coordinates"] if g["type"] == "MultiLineString" else [g["coordinates"]]
        lines = [[[round(x, 6), round(y, 6)] for x, y in dp(l, 1.0)] for l in lines]
        name = (r.get("streetname") or "").title()
        name = re.sub(r"\b(\d+)(St|Nd|Rd|Th)\b", lambda m: m[1] + m[2].lower(), name)
        sfeats.append({"type": "Feature",
                       "geometry": {"type": "MultiLineString", "coordinates": lines}
                       if len(lines) > 1 else {"type": "LineString", "coordinates": lines[0]},
                       "properties": {"n": name, "c": int(r.get("classcode") or 5)}})
    n = dump(OUT / "streets.geojson", {"type": "FeatureCollection", "features": sfeats})
    print(f"    {len(sfeats)} segments, {n/1e6:.1f} MB")

    print("==> land")
    land = []
    for r in nhoods:
        s = simplify_polys(polys_of(r["the_geom"]), 3.0, nd=5)
        land.append({"type": "Feature", "geometry": geom(s), "properties": {"n": r["nhood"]}})
    n = dump(OUT / "land.geojson", {"type": "FeatureCollection", "features": land})
    print(f"    {len(land)} neighborhoods, {n/1e6:.2f} MB")

    print("==> neighborhoods (prototype D)")
    by_neighborhood(lots, public, page_lots, feats, land)

    print("==> prototype D page")
    neighborhood_page()

    print("==> SVG locators")
    locators(lots, lots_near, page_lots, public, sfeats, land, feats)


# --- prototype D: one file per neighborhood --------------------------------
def by_neighborhood(lots, public, page_lots, page_feats, land):
    """data/nhoods/index.geojson: the 41 Analysis Neighborhoods, each with its
    slug, its hub page where the site has one, and how many pages it holds.
    data/nhoods/<slug>.json: every lot in it, and its documented pages' lots,
    so a click fetches one file. A lot belongs to the neighborhood its bbox
    centre falls in."""
    from seed_pages import BOUNDARY_SOURCE, DS_ANALYSIS_NEIGHBORHOODS
    hub = {name: f"/san-francisco/{d}/" for d, (ds, name) in BOUNDARY_SOURCE.items()
           if ds == DS_ANALYSIS_NEIGHBORHOODS}
    areas = []
    for f in land:
        polys = f["geometry"]["coordinates"] if f["geometry"]["type"] == "MultiPolygon" \
            else [f["geometry"]["coordinates"]]
        name = f["properties"]["n"]
        slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
        areas.append((slug, name, polys, bbox(polys)))

    def area_of(x, y):
        for slug, _, polys, bb in areas:
            if bb[0] <= x <= bb[2] and bb[1] <= y <= bb[3] and contains(polys, x, y):
                return slug
        return None

    where = {}
    for m, (s, bb) in lots.items():
        a = area_of((bb[0] + bb[2]) / 2, (bb[1] + bb[3]) / 2)
        if a:
            where[m] = a
    out = {slug: {"lots": [], "pages": []} for slug, *_ in areas}
    for m, a in where.items():
        props = {k: 1 for k, v in (("z", m in public), ("pg", m in page_lots)) if v}
        out[a]["lots"].append({"type": "Feature", "geometry": geom(lots[m][0]), "properties": props})
    for f in page_feats:
        a = where.get(f["properties"]["l"])
        if a:
            out[a]["pages"].append(f)
    index, total = [], 0
    for slug, name, polys, bb in areas:
        o = out[slug]
        total += dump(OUT / "nhoods" / f"{slug}.json", {
            "lots": {"type": "FeatureCollection", "features": o["lots"]},
            "pages": {"type": "FeatureCollection", "features": o["pages"]}})
        props = {"n": name, "slug": slug, "pages": len(o["pages"]),
                 "bbox": [round(v, 5) for v in bb]}
        if name in hub:
            props["hub"] = hub[name]
        index.append({"type": "Feature", "geometry": geom(polys), "properties": props})
    dump(OUT / "nhoods" / "index.geojson", {"type": "FeatureCollection", "features": index})
    print(f"    {len(areas)} neighborhoods, {total/1e6:.1f} MB in all")


def neighborhood_page():
    """demo/parcels/neighborhoods/index.html, made from the homepage itself so
    the cards below the fold are the homepage's own: the map is swapped for D's,
    and a Neighborhoods grid goes in above the news, one card per hub in the
    city index's order, its photo from hub.json and its hook from the index."""
    home = (ROOT / "index.html").read_text(encoding="utf-8")
    city = (ROOT / "san-francisco" / "index.html").read_text(encoding="utf-8")
    items = re.findall(r'<li><a href="([a-z0-9-]+)/">(.*?)</a><br>\s*<span class="hook">(.*?)</span></li>',
                       city, flags=re.S)
    cards = []
    for slug, name, hook in items:
        hub = ROOT / "san-francisco" / slug / "hub.json"
        if not hub.exists():
            continue
        photo = json.loads(hub.read_text(encoding="utf-8")).get("photo")
        if photo:
            pic = (f'<img src="/san-francisco/{slug}/{photo["file"]}" width="{photo["width"]}" '
                   f'height="{photo["height"]}" alt="{html.escape(photo.get("alt") or "")}" '
                   f'loading="lazy" decoding="async">')
        else:
            pic = '<div class="media-empty"><span class="ic ic-pin"></span></div>'
        cards.append(f"""    <li>
      <a href="/san-francisco/{slug}/">
        <figure class="media hub-card-media">{pic}</figure>
        <span class="card-label">{name}</span>
      </a>
      <p class="card-news">{hook}</p></li>""")
    section = ('<main id="neighborhoods">\n'
               '  <div class="section-head"><span class="ic ic-pin"></span><h1>Neighborhoods</h1></div>\n'
               '  <ul class="place-cards news-cards hub-cards">\n' + "\n".join(cards) + "\n  </ul>\n\n"
               '  <div class="section-head" id="news"><span class="ic ic-permit"></span><h2>In the news</h2></div>')
    page = home
    # Head: MapLibre and D's script in place of Mapbox GL.
    page = re.sub(r'  <link rel="preconnect" href="https://api.mapbox.com".*?defer></script>\n',
                  '  <meta name="robots" content="noindex">\n'
                  '  <link rel="stylesheet" href="https://unpkg.com/maplibre-gl@4.7.1/dist/maplibre-gl.css">\n'
                  '  <link rel="stylesheet" href="/demo/parcels/demo.css">\n'
                  '  <script src="https://unpkg.com/maplibre-gl@4.7.1/dist/maplibre-gl.js" defer></script>\n'
                  '  <script src="/demo/parcels/neighborhoods.js" defer></script>\n', page, count=1, flags=re.S)
    page = re.sub(r"<title>.*?</title>", "<title>Demo — Pick a neighborhood</title>", page, count=1)
    page = page.replace("</style>", """
    /* DEMO: hub cards wear the news cards' frame at 3:2, the photos' own crop. */
    .hub-cards .media { aspect-ratio: 3 / 2; overflow: hidden; }
    .hub-cards .media img { width: 100%; height: 100%; object-fit: cover; display: block; }
    .hub-cards .card-news { color: var(--muted); font-size: 0.9rem; }
    .map-shell .demo-note { bottom: 4.5rem; }
  </style>""", 1)
    # The map: D's, with its panel; the cue now points at the neighborhoods.
    page = re.sub(r'<div id="map" .*?></div>',
                  '<div id="map" role="region" aria-label="Map of San Francisco neighborhoods; pick one to see its lots"></div>',
                  page, count=1, flags=re.S)
    page = page.replace('<p class="map-brand">Know This Place</p>',
                        '<a class="map-brand" href="/demo/parcels/">Know This Place</a>\n'
                        '  <aside class="demo-note" id="panel" aria-live="polite"></aside>', 1)
    page = page.replace('<a class="map-cue" href="#news">In the news',
                        '<a class="map-cue" href="#neighborhoods">Neighborhoods', 1)
    page = page.replace('<main id="news">\n  <div class="section-head"><span class="ic ic-permit"></span><h1>In the news</h1></div>',
                        section, 1)
    # The homepage's own map script goes; D's replaces it.
    page = re.sub(r'<script type="module">.*?</script>\s*(?=</body>)', "", page, count=1, flags=re.S)
    out = HERE / "neighborhoods" / "index.html"
    out.write_text(page, encoding="utf-8")
    print(f"    {len(cards)} hub cards above the news")


# --- prototype C: inline SVG locator ---------------------------------------
LOCATOR_PAGES = [
    "/san-francisco/chinatown/montgomery-street/600/",
    "/san-francisco/castro/18th-street/4548/",
    "/san-francisco/nob-hill/green-street/999/",
    "/san-francisco/castro/boynton-court/3/",
    "/san-francisco/mission/valencia-street/1000/",
    "/san-francisco/marina/bay-street/3640/",
]
W, H = 1200, 400          # the band's 3:1 frame; a phone crops the sides to 4:3
HALF_W_M = 210            # metres from the centre to the frame's side edges


def merc(lng, lat):
    return (lng + 180) / 360, (1 - math.log(math.tan(math.radians(lat)) +
                                            1 / math.cos(math.radians(lat))) / math.pi) / 2


def locators(lots, lots_near, page_lots, public, streets, land, page_feats):
    by_path = {f["properties"]["p"]: f for f in page_feats}
    gallery = []
    for path in LOCATOR_PAGES:
        src = ROOT / path.strip("/") / "index.html"
        f = by_path.get(path)
        if not src.exists() or not f:
            print(f"    skip {path} (not built or not placed)")
            continue
        page = src.read_text(encoding="utf-8")
        m = re.search(r'<ktp-map location="([-\d.]+),([-\d.]+)"', page)
        lat, lng = float(m[1]), float(m[2])
        lot_page = {}
        for g in page_feats:
            lot_page.setdefault(g["properties"]["l"], (g["properties"]["p"], g["properties"]["t"]))
        svg = locator_svg(lat, lng, f["properties"]["l"], lots, lots_near, lot_page,
                          public, streets, by_path)
        new = re.sub(r"<ktp-map .*?</ktp-map>", lambda _: (
            '<figure class="media media-map media-parcels">' + svg + "</figure>"),
            page, count=1, flags=re.S)
        new = new.replace("</head>", LOCATOR_CSS + "</head>", 1)
        new = new.replace("<body", '<body data-demo="parcel-locator"', 1)
        slug = path.strip("/").split("/", 2)[-1].replace("/", "-")
        out = HERE / "locator" / slug / "index.html"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(new, encoding="utf-8")
        gallery.append((slug, f["properties"]["t"], len(svg.encode())))
        print(f"    {slug}: {len(svg.encode())/1024:.0f} KB of SVG")
    (OUT / "locators.json").write_text(json.dumps(gallery))


def locator_svg(lat, lng, here, lots, lots_near, page_lots, public, streets, by_path):
    cx, cy = merc(lng, lat)
    # Web Mercator units per metre at this latitude, and the frame's half sizes.
    upm = 1 / (40075016.686 * math.cos(math.radians(lat)))
    hw, hh = HALF_W_M * upm, HALF_W_M * upm * H / W
    sx = W / (2 * hw)

    def pt(x, y):
        mx, my = merc(x, y)
        return (mx - cx + hw) * sx, (my - cy + hh) * sx

    def d_of(polys):
        out = []
        for poly in polys:
            for ring in poly:
                p = [pt(*q) for q in ring]
                out.append("M" + "L".join(f"{x:.1f} {y:.1f}" for x, y in p) + "Z")
        return "".join(out)

    def visible(bb):
        (x1, y1), (x2, y2) = pt(bb[0], bb[3]), pt(bb[2], bb[1])
        return x2 > -20 and x1 < W + 20 and y2 > -20 and y1 < H + 20

    plain, pages, parks = [], [], []
    for m in lots_near(lng, lat, 1):
        s, bb = lots[m]
        if m == here or not visible(bb):
            continue
        if m in page_lots:
            # A documented neighbour is a link to its page — no JS needed.
            p, t = page_lots[m]
            pages.append(f'<a href="{html.escape(p)}"><title>{html.escape(t)}</title>'
                         f'<path d="{d_of(s)}"/></a>')
        else:
            (parks if m in public else plain).append(d_of(s))
    # Street names along the centreline, once per name, on the longest segment
    # in the frame, reading left to right.
    best = {}
    for f in streets:
        g = f["geometry"]
        for line in g["coordinates"] if g["type"] == "MultiLineString" else [g["coordinates"]]:
            p = [pt(*q) for q in line]
            p = [q for q in p if -50 < q[0] < W + 50 and -50 < q[1] < H + 50]
            if len(p) < 2:
                continue
            length = sum(math.dist(a, b) for a, b in zip(p, p[1:]))
            name = f["properties"]["n"]
            if length > 140 and length > best.get(name, (0,))[0]:
                if p[-1][0] < p[0][0]:
                    p = p[::-1]
                best[name] = (length, p)
    defs, labels = [], []
    for k, (name, (length, p)) in enumerate(sorted(best.items())):
        defs.append(f'<path id="st{k}" d="M' + "L".join(f"{x:.1f} {y:.1f}" for x, y in p) + '"/>')
        labels.append(f'<text><textPath href="#st{k}" startOffset="50%">'
                      f'{html.escape(name)}</textPath></text>')
    here_d = d_of(lots[here][0])
    return (f'<svg class="parcel-map" viewBox="0 0 {W} {H}" preserveAspectRatio="xMidYMid slice" '
            f'role="img" aria-label="Lot lines around this building">'
            f'<defs>{"".join(defs)}</defs>'
            f'<rect class="pm-ground" width="{W}" height="{H}"/>'
            f'<path class="pm-lot" d="{"".join(plain)}"/>'
            f'<path class="pm-lot pm-park" d="{"".join(parks)}"/>'
            f'<g class="pm-lot pm-page">{"".join(pages)}</g>'
            f'<path class="pm-here" d="{here_d}"/>'
            f'<g class="pm-labels">{"".join(labels)}</g></svg>')


LOCATOR_CSS = """<style>
/* DEMO: the locator band drawn from lot lines, no Mapbox. */
.media-parcels { margin: 0; }
.parcel-map { display: block; width: 100%; height: 100%; }
.pm-ground { fill: color-mix(in oklab, var(--rule) 70%, var(--paper)); }
.pm-lot { fill: var(--paper); stroke: color-mix(in oklab, var(--rule) 85%, var(--ink)); stroke-width: .6; }
.pm-park { fill: color-mix(in oklab, #6f9a62 18%, var(--paper)); }
.pm-page { fill: color-mix(in oklab, var(--muted) 14%, var(--paper)); }
.pm-page a:hover path { fill: var(--warm-soft, var(--warm)); }
.pm-here { fill: var(--warm); stroke: var(--paper); stroke-width: 1.5; }
.pm-labels { font: 500 11px/1 var(--sans), sans-serif; fill: var(--muted);
  letter-spacing: .04em; paint-order: stroke; stroke: color-mix(in oklab, var(--rule) 70%, var(--paper)); stroke-width: 3px; }
@media (max-width: 720px) {
  .map-shell .media-parcels { height: auto; aspect-ratio: 4 / 3; border-bottom: 1px solid var(--rule); }
}
.pm-labels { pointer-events: none; }
.pm-labels text { dominant-baseline: central; text-anchor: middle; }
</style>
"""

if __name__ == "__main__":
    main()
