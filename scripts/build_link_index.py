#!/usr/bin/env python3
"""Regenerate shared/nearby.json from the content tree. Stdlib only.

`seed_pages.render_html` is a pure function of one page's `data.json`, so it
can never know what stands next door. Lateral links between address pages
therefore need a derived index, the way the homepage map needs
`shared/addresses.geojson`. This builds it: for every documented address, up to
eight nearby pages in three relationship classes.

- **street** — the nearest documented lower and higher number on the same
  street, in `num_key` order rather than string order (so 9 precedes 10). Not
  distance-limited: where coverage is sparse the next documented number really
  is the next one up the street, and this is the class that keeps an isolated
  page from having no neighbors at all.
- **block** — other documented pages on the same assessor block, nearest first,
  as long as they are close enough for that to mean anything. Sharing a block
  code is not always sharing a block: 9900 is the assessor's catch-all for
  state tidelands, and it puts The Embarcadero 2.8 km from Terry A Francois
  Boulevard. A 500 m bound rejects those, and is deliberately generous — the
  widest block link that survives it still spans 473 m, across one of the
  Bayview's industrial superblocks. The script names every block it rejected a
  pair from, so a bound set wrongly shows up in the run rather than as links
  that quietly stopped appearing.
- **corner** — the nearest pages within 120 m that are on a different street
  *and* a different block: what you'd see turning the corner.

**The index deliberately carries no `hook`.** It stores each page's path and
title and nothing else. If it carried hooks, editing any page's `data.json`
would change its neighbors' rendered HTML and every content edit anywhere would
ripple through the tree; with titles only, a page's HTML changes when a page is
added or removed nearby, and not otherwise. The relationship label the renderer
prints supplies the context a hook would have given.

Output is parallel arrays — paths and titles stored once, `near[i]` holding
`[index, class]` pairs for page `i` — one page per line so a diff is readable.
Note that indices are positional: inserting a page renumbers every entry after
it, which churns this file but not, by design, anyone's HTML.

Once the renderer consumes this file, it must run *before* `render` in any
sequence that adds pages:

    seed → hubs → build_link_index → render <neighborhood>
         → build_map_index → build_sitemap → validate

Run from anywhere: python3 scripts/build_link_index.py
"""
import json
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from seed_pages import ADDRESS_DIR, num_key, page_title  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent

RADIUS_M = 120.0        # "around the corner", and the radius the coverage
                        # measurements in issue #232 were taken at
BLOCK_RADIUS_M = 500.0  # longer than any real assessor block, so it rejects
                        # only the catch-all block codes — see the module
                        # docstring
MAX_BLOCK = 4
MAX_CORNER = 3
MAX_TOTAL = 8

# Equirectangular metres per degree at San Francisco's latitude. The city is
# 12 km across; over that span the error against a great-circle distance is
# centimetres, and every use here is a comparison against 120 m.
M_PER_DEG_LAT = 111320.0
M_PER_DEG_LNG = 111320.0 * math.cos(math.radians(37.76))


def load_pages():
    """Every address page in the tree, in path order. Skips nothing: a page
    that has opted out of rendering is still a page a neighbor can link to."""
    content = ROOT / "san-francisco"
    pages, skipped = [], []

    for data_path in sorted(content.rglob("data.json")) if content.exists() else []:
        page_dir = data_path.parent
        if not ADDRESS_DIR.match(page_dir.name):
            continue
        try:
            data = json.loads(data_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            skipped.append(f"{data_path.relative_to(ROOT)}: invalid JSON")
            continue

        # The directory, not data.json's `path`: on a static site the
        # directory is the URL, it is what `validate.py` checks this index
        # against, and street and number are read off it just below.
        path = "/" + page_dir.relative_to(ROOT).as_posix() + "/"
        if not data.get("address"):
            # page_title reads `address`; without it there is no anchor text,
            # and a link labelled with a slug is worse than no link.
            skipped.append(f"{data_path.relative_to(ROOT)}: no address")
            continue

        segments = path.strip("/").split("/")
        coords = data.get("coordinates") or {}
        lat, lng = coords.get("lat"), coords.get("lng")
        if not isinstance(lat, (int, float)) or not isinstance(lng, (int, float)):
            # Still an index entry, so its street siblings can link to it — it
            # just can't be placed, so it gets and gives no distance-ranked
            # neighbors.
            lat = lng = None
            skipped.append(f"{data_path.relative_to(ROOT)}: no coordinates "
                           f"— street neighbors only")

        pages.append({
            "path": path,
            "title": page_title(data),
            # The street slug, not the street directory: address numbers are
            # unique per street citywide (verified — no slug/number collides),
            # so Mission Street is one street even where it crosses four
            # neighborhood directories, and its numbering runs through them.
            "street": segments[2] if len(segments) > 2 else "",
            "number": page_dir.name,
            "block": str(data.get("block") or ""),
            "lat": lat,
            "lng": lng,
        })

    pages.sort(key=lambda p: p["path"])
    return pages, skipped


def metres(a, b) -> float:
    return math.hypot((a["lat"] - b["lat"]) * M_PER_DEG_LAT,
                      (a["lng"] - b["lng"]) * M_PER_DEG_LNG)


def build_near(pages):
    """The [index, class] list for each page, ordered street → block → corner.
    Returns it alongside the block-code pairs the 500 m bound rejected."""
    street_groups, block_groups, grid = {}, {}, {}
    for i, p in enumerate(pages):
        street_groups.setdefault(p["street"], []).append(i)
        if p["block"]:
            block_groups.setdefault(p["block"], []).append(i)
        if p["lat"] is not None:
            grid.setdefault(cell(p), []).append(i)

    position = {}
    for members in street_groups.values():
        # num_key, so 1200 follows 999 and 218A follows 218.
        members.sort(key=lambda i: (num_key(pages[i]["number"]), pages[i]["path"]))
        for at, i in enumerate(members):
            position[i] = at

    near, far = [], {}
    for i, p in enumerate(pages):
        # The lower number then the higher one — reading order, and at most
        # two of them by construction.
        siblings = street_groups[p["street"]]
        at = position[i]
        out = [[siblings[j], "street"]
               for j in (at - 1, at + 1) if 0 <= j < len(siblings)]
        picked = {i} | {e[0] for e in out}

        if p["lat"] is not None:
            block = []
            for j in block_groups.get(p["block"], []):
                if j in picked or pages[j]["lat"] is None:
                    continue
                if metres(p, pages[j]) > BLOCK_RADIUS_M:
                    far.setdefault(p["block"], set()).add(
                        (min(i, j), max(i, j), round(metres(p, pages[j]))))
                    continue
                block.append(j)
            for j in rank(pages, p, block)[:MAX_BLOCK]:
                picked.add(j)
                out.append([j, "block"])

            corner = [j for j in candidates(grid, p)
                      if j not in picked
                      and pages[j]["street"] != p["street"]
                      and pages[j]["block"] != p["block"]
                      and metres(p, pages[j]) <= RADIUS_M]
            for j in rank(pages, p, corner)[:MAX_CORNER]:
                picked.add(j)
                out.append([j, "corner"])

        near.append(out[:MAX_TOTAL])
    return near, far


def cell(p):
    return (int(p["lat"] * M_PER_DEG_LAT // RADIUS_M),
            int(p["lng"] * M_PER_DEG_LNG // RADIUS_M))


def candidates(grid, p):
    """Everything in the nine 120 m cells around p — the smallest neighborhood
    of cells that can't miss a page within 120 m. The median page has 49
    documented neighbors that close, so an all-pairs scan is not an option."""
    cy, cx = cell(p)
    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            yield from grid.get((cy + dy, cx + dx), ())


def rank(pages, p, indices):
    """Nearest first; path breaks ties so a rerun produces the same file."""
    return sorted(indices, key=lambda j: (metres(p, pages[j]), pages[j]["path"]))


def main() -> None:
    pages, skipped = load_pages()
    near, far = build_near(pages)

    # One page per line, and the three arrays in the same order, so entry N of
    # each lines up and a diff shows which page changed.
    def rows(values):
        return ",\n".join(json.dumps(v, separators=(",", ":"), ensure_ascii=False)
                          for v in values)

    text = ('{"paths":[\n' + rows([p["path"] for p in pages])
            + '\n],\n"titles":[\n' + rows([p["title"] for p in pages])
            + '\n],\n"near":[\n' + rows(near) + '\n]}\n')

    out = ROOT / "shared" / "nearby.json"
    out.write_text(text, encoding="utf-8")

    links = sum(len(n) for n in near)
    isolated = sum(1 for n in near if not n)
    print(f"shared/nearby.json written with {len(pages)} address(es), "
          f"{links} link(s)")
    if isolated:
        print(f"  {isolated} page(s) have no neighbor to link to")
    for code, pairs in sorted(far.items()):
        print(f"  block {code}: {len(pairs)} pair(s) up to "
              f"{max(d for _, _, d in pairs)} m "
              f"apart — too far to call neighbors, not linked")
    for note in skipped:
        print(f"  skipped — {note}")


if __name__ == "__main__":
    main()
