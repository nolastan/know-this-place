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
    if not apns:
        return {}
    rows = r.api_get("3tsw-4idn", {"$select": "apn,name",
                                   "$where": f"apn in({r._quoted(apns)}) and name is not null"})
    return {x["apn"]: x["name"] for x in rows}


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


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("street_a")
    ap.add_argument("street_b")
    ap.add_argument("--to", metavar="STREET_C",
                    help="list street_a's block face from street_b to this street instead")
    ap.add_argument("--year", type=int, help="mark parcels built within two years of this")
    a = ap.parse_args()
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
