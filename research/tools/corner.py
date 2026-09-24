#!/usr/bin/env python3
"""List the parcels at a street corner, for placing a record that gives no number.

Building news in period newspapers locates new construction by corner ("the
southeast corner of Bush and Mason") or by offset ("137:6 feet south of
Market"), never by street number, so `resolve_eas.py` has nothing to join on.
This prints every parcel with an EAS address within about 60 m of where the two
streets meet, with what decides the match: the roll's build year, storeys and
lot area, SF Planning's building name, and the page the site already has.

    python3 research/tools/corner.py BUSH MASON
    python3 research/tools/corner.py "GOLDEN GATE" JONES --year 1912
    python3 research/tools/corner.py CALIFORNIA HYDE --to LEAVENWORTH --year 1911

`--to` lists a whole block face instead: every parcel addressed on the first
street between its crossings with the other two, for a record that says "south
side of California between Hyde and Leavenworth", or gives an offset further
along the block than the corner radius reaches.

`--batch FILE` does a whole findings batch's corners at once. FILE is JSON
lines, one entry per record:

    {"id": "...-0012", "a": "BUSH", "b": "MASON", "lot": "46x137:6", "year": 1910}
    {"id": "...-0013", "a": "CALIFORNIA", "b": "HYDE", "to": "LEAVENWORTH",
     "lot": "27:6x100", "offset": 110}

and it prints, per entry, only the parcels whose roll `lot_area` is within 4%
of the record's lot (feet:inches, "25x137:6" is 25 by 137 ft 6 in), with the
build year, storeys, name, page, and each parcel's distance along street `a`
from its crossing with `b`. With `to`, that distance is measured on the
sf-parcels shapes, so it is the lot's front: "front 183-229 ft" is the span of
frontage from the corner, measured from the edge of the assessor block the lot
is in — the check a record's "183 feet west of Powell" is made against. Without
`to` it is the EAS point's distance, a rough middle. Streets are fetched once
each, so a hundred entries take a minute rather than an hour.

It deliberately does not pick a corner. Which parcel is "southeast" depends on
which side of the street carries the odd numbers, and that is a reading of the
addresses printed here, not something a centroid gets right. The match is the
lot area the record gives against the roll's `lot_area`, and the record's year
against `year_property_built`; write the reasoning into `resolution.method`
with `"by_hand": true`. See RUNBOOK.md step 3, "A corner, not a number".
"""
import argparse
import glob
import json
import math
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import resolve_eas as r  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
RADIUS_DEG = 0.00055  # about 60 m of latitude


def eas_rows(street: str) -> list:
    rows = r.api_get(r.EAS, {"street_name": street.upper(), "$limit": 50000,
                             "$select": "address,parcel_number,latitude,longitude"})
    return [x for x in rows if x.get("parcel_number") and x.get("latitude")]


def roll_row(apn: str) -> dict:
    rows = r.api_get(r.ROLL, {"parcel_number": apn, "$order": "closed_roll_year DESC",
                              "$limit": 1})
    return rows[0] if rows else {}


def planning_names(apns: list) -> dict:
    out = {}
    for i in range(0, len(apns), 80):
        rows = r.api_get("3tsw-4idn", {"$select": "apn,name",
                                       "$where": f"apn in({r._quoted(apns[i:i + 80])}) "
                                                 "and name is not null"})
        out.update({x["apn"]: x["name"] for x in rows})
    return out


def pages_by_apn() -> dict:
    out = {}
    for p in glob.glob(os.path.join(ROOT, "san-francisco/*/*/*/data.json")):
        try:
            apn = json.load(open(p)).get("apn")
        except (OSError, ValueError):
            continue
        out.setdefault(apn, []).append(os.path.relpath(os.path.dirname(p), ROOT))
    return out


def crossing(A: list, B: list):
    """Where two streets' EAS rows come closest, or None if they don't meet."""
    pa = [(float(x["latitude"]), float(x["longitude"])) for x in A]
    best = min(((p[0] - q[0]) ** 2 + (p[1] - q[1]) ** 2, p, q)
               for p in pa for q in ((float(y["latitude"]), float(y["longitude"])) for y in B))
    if best[0] > 0.0012 ** 2:
        return None
    return ((best[1][0] + best[2][0]) / 2, (best[1][1] + best[2][1]) / 2)


def block_face(A: list, p: tuple, q: tuple) -> dict:
    """Parcels addressed on street A between crossings p and q, either side."""
    k = math.cos(math.radians(p[0]))
    vx, vy = (q[1] - p[1]) * k, q[0] - p[0]
    n = math.hypot(vx, vy)
    out = {}
    for x in A:
        wx, wy = (float(x["longitude"]) - p[1]) * k, float(x["latitude"]) - p[0]
        if 0 <= (wx * vx + wy * vy) / (n * n) <= 1 and abs(wx * vy - wy * vx) / n < RADIUS_DEG:
            out.setdefault(x["parcel_number"], []).append(x["address"])
    return out


def lot_sqft(lot: str):
    """ "46x137:6" or "62:6 by 106:3" -> square feet, or None."""
    m = re.match(r"\s*(\d+)(?::(\d+))?\s*(?:x|by)\s*(\d+)(?::(\d+))?\s*$", lot or "", re.I)
    if not m:
        return None
    w = int(m[1]) + int(m[2] or 0) / 12
    d = int(m[3]) + int(m[4] or 0) / 12
    return w * d


def along_ft(x: dict, p: tuple, q: tuple) -> float:
    """Distance in feet from crossing p to the EAS point x, measured toward q."""
    k = math.cos(math.radians(p[0]))
    vx, vy = (q[1] - p[1]) * k, q[0] - p[0]
    n = math.hypot(vx, vy) or 1
    wx, wy = (float(x["longitude"]) - p[1]) * k, float(x["latitude"]) - p[0]
    return (wx * vx + wy * vy) / n * 364000  # a degree of latitude, in feet


def block_shapes(blocks: list) -> dict:
    """Every active parcel's outline on these assessor blocks, by APN."""
    out = {}
    for i in range(0, len(blocks), 40):
        chunk = blocks[i:i + 40]
        for x in r.api_get(r.PARCELS, {"$select": "blklot,block_num,shape", "$limit": 50000,
                                       "$where": f"active=true and block_num in({r._quoted(chunk)})"}):
            shape = x.get("shape") or {}
            if isinstance(shape, str):
                continue
            pts = [pt for poly in shape.get("coordinates", []) for ring in poly for pt in ring]
            if pts:
                out[x["blklot"]] = (x["block_num"], pts)
    return out


def front_span(apn: str, shapes: dict, p: tuple, q: tuple):
    """Feet from the block's end at p to where this lot's frontage starts and stops.

    The direction p->q comes from EAS points and can be skewed by 20 degrees,
    enough to add the lot's depth to its frontage, so the axis is the lot's own
    edge most nearly parallel to it.
    """
    if apn not in shapes:
        return None
    k = math.cos(math.radians(p[0]))
    vx, vy = (q[1] - p[1]) * k, q[0] - p[0]
    n = math.hypot(vx, vy) or 1
    vx, vy = vx / n, vy / n
    pts = shapes[apn][1]
    best = (0, vx, vy)
    for a, b in zip(pts, pts[1:]):
        ex, ey = (b[0] - a[0]) * k, b[1] - a[1]
        m = math.hypot(ex, ey)
        if m * 364000 < 5:
            continue
        ex, ey = ex / m, ey / m
        if ex * vx + ey * vy < 0:
            ex, ey = -ex, -ey
        c = ex * vx + ey * vy
        if c > best[0]:
            best = (c, ex, ey)
    _, ux, uy = best

    def proj(pt):
        return ((pt[0] - p[1]) * k * ux + (pt[1] - p[0]) * uy) * 364000

    block = shapes[apn][0]
    origin = min(proj(pt) for b, ps in shapes.values() if b == block for pt in ps)
    mine = [proj(pt) for pt in pts]
    return min(mine) - origin, max(mine) - origin


def roll_rows(apns: list) -> dict:
    out = {}
    for i in range(0, len(apns), 80):
        chunk = apns[i:i + 80]
        for x in r.api_get(r.ROLL, {"$where": f"parcel_number in({r._quoted(chunk)})",
                                    "$order": "closed_roll_year DESC", "$limit": 50000}):
            out.setdefault(x["parcel_number"], x)
    return out


def batch(path: str, tol: float = 0.04) -> int:
    entries = [json.loads(line) for line in open(path) if line.strip()]
    streets, found = {}, []

    def rows(s):
        s = s.upper()
        if s not in streets:
            streets[s] = eas_rows(s)
        return streets[s]

    for e in entries:
        A, B = rows(e["a"]), rows(e["b"])
        ix = crossing(A, B) if A and B else None
        if ix is None:
            found.append((e, None, f"{e['a']} and {e['b']} do not meet in EAS"))
            continue
        if e.get("to"):
            C = rows(e["to"])
            iy = crossing(A, C) if C else None
            if iy is None:
                found.append((e, None, f"{e['a']} and {e['to']} do not meet in EAS"))
                continue
            near, toward = block_face(A, ix, iy), iy
        else:
            near, toward = {}, None
            for x in A + B:
                dy = float(x["latitude"]) - ix[0]
                dx = (float(x["longitude"]) - ix[1]) * math.cos(math.radians(ix[0]))
                if math.hypot(dy, dx) < RADIUS_DEG * 1.5:
                    near.setdefault(x["parcel_number"], []).append(x["address"])
        pts = {}
        for x in A:
            if x["parcel_number"] in near:
                pts.setdefault(x["parcel_number"], x)
        found.append((e, (near, ix, toward, pts), None))
    apns = sorted({a for _, hit, _ in found if hit for a in hit[0]})
    roll, names, pages = roll_rows(apns), planning_names(apns), pages_by_apn()
    shapes = block_shapes(sorted({a[:4] if not a[4].isalpha() else a[:5]
                                  for _, hit, _ in found if hit and hit[2] for a in hit[0]}))
    for e, hit, err in found:
        want = lot_sqft(e.get("lot", ""))
        head = f"{e['id']}: {e['a']} & {e['b']}" + (f" to {e['to']}" if e.get("to") else "")
        head += f"  lot {e.get('lot')} = {want:.0f} sq ft" if want else "  (no lot)"
        print(head)
        if err:
            print(f"    {err}")
            continue
        near, ix, toward, pts = hit
        n = 0
        for apn in sorted(near):
            ro = roll.get(apn, {})
            try:
                area = float(ro.get("lot_area") or 0)
            except ValueError:
                area = 0
            if not want or not area or abs(area - want) > tol * want:
                continue
            n += 1
            yr = ro.get("year_property_built") or "?"
            mark = ""
            if e.get("year") and yr.isdigit() and abs(int(yr) - int(e["year"])) <= 2:
                mark = "  <-- year"
            d = ""
            span = front_span(apn, shapes, ix, toward) if toward else None
            if span:
                d = f"  front {span[0]:.0f}-{span[1]:.0f} ft from {e['b']}"
            elif apn in pts:
                d = f"  ~{abs(along_ft(pts[apn], ix, toward or (ix[0], ix[1] + 1e-3))):.0f} ft along {e['a']}"
            print(f"    {apn}  built {yr}  {ro.get('number_of_stories', '?')} st  "
                  f"{area:g} sq ft  roll {ro.get('closed_roll_year')}{mark}{d}")
            print(f"        {', '.join(sorted(set(near[apn]))[:6])}"
                  + (f"  Planning: {names[apn]}" if apn in names else "")
                  + (f"  page: {', '.join(pages[apn])}" if apn in pages else ""))
        if not n:
            print(f"    no parcel of {len(near)} within {tol:.0%} of the lot")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("street_a", nargs="?")
    ap.add_argument("street_b", nargs="?")
    ap.add_argument("--batch", metavar="FILE",
                    help="JSON lines of corners with lots; print only the lot-area matches")
    ap.add_argument("--to", metavar="STREET_C",
                    help="list street_a's block face from street_b to this street instead")
    ap.add_argument("--year", type=int, help="mark parcels built within two years of this")
    a = ap.parse_args()
    if a.batch:
        return batch(a.batch)
    if not (a.street_a and a.street_b):
        ap.error("two streets, or --batch FILE")
    A, B = eas_rows(a.street_a), eas_rows(a.street_b)
    if not A or not B:
        print(f"no EAS rows for {a.street_a if not A else a.street_b} — "
              "use EAS's spelling (OFARRELL, 06TH, GOLDEN GATE)")
        return 1
    ix = crossing(A, B)
    if ix is None:
        print(f"{a.street_a} and {a.street_b} do not meet")
        return 1
    if a.to:
        C = eas_rows(a.to)
        iy = crossing(A, C) if C else None
        if iy is None:
            print(f"{a.street_a} and {a.to} do not meet")
            return 1
        near = block_face(A, ix, iy)
        head = f"{a.street_a} between {a.street_b} and {a.to}: {len(near)} parcel(s)"
    else:
        near = {}
        for x in A + B:
            dy = float(x["latitude"]) - ix[0]
            dx = (float(x["longitude"]) - ix[1]) * math.cos(math.radians(ix[0]))
            if math.hypot(dy, dx) < RADIUS_DEG:
                near.setdefault(x["parcel_number"], []).append(x["address"])
        head = (f"{a.street_a} & {a.street_b}: {len(near)} parcel(s) within ~60 m of "
                f"{ix[0]:.5f}, {ix[1]:.5f}")
    names, pages = planning_names(sorted(near)), pages_by_apn()
    print(head)
    for apn in sorted(near):
        ro = roll_row(apn)
        yr = ro.get("year_property_built") or "?"
        mark = ""
        if a.year and yr.isdigit() and abs(int(yr) - a.year) <= 2:
            mark = "  <-- year"
        stale = ro.get("closed_roll_year")
        print(f"  {apn}  built {yr}  {ro.get('number_of_stories', '?')} st  "
              f"{ro.get('lot_area', '?')} sq ft  roll {stale}{mark}")
        print(f"      {', '.join(sorted(set(near[apn]))[:10])}")
        extra = [f"Planning: {names[apn]}" if apn in names else "",
                 f"page: {', '.join(pages[apn])}" if apn in pages else ""]
        if any(extra):
            print("      " + "  ".join(e for e in extra if e))
    return 0


if __name__ == "__main__":
    sys.exit(main())
