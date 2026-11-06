#!/usr/bin/env python3
"""Know This Place as an MCP server. Stdlib only, read-only.

Gives an AI chat client tools to look up a building by address or name, find
what is near a point, read a building's page as structured data, browse a
neighborhood or street, and query the whole corpus. Every answer is read from
the files this repository already holds — `data.json`, `place.json`,
`corpus.jsonl`, and `shared/addresses.geojson` (built here if missing) — so
the server states nothing the site does not.

There is deliberately no lookup by a person's name: these pages describe
buildings, not the people in them (AGENTS.md → Privacy).

Run it two ways:

    python3 mcp/server.py                     # stdio, for Claude Desktop / Code
    python3 mcp/server.py --http 8765         # Streamable HTTP at /mcp

See mcp/AGENTS.md for wiring it into a client.
"""
import argparse
import json
import math
import re
import subprocess
import sys
from functools import lru_cache
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
from seed_pages import SITE, area_display, hero_lines, place_hook, place_sub  # noqa: E402

SERVER_INFO = {"name": "know-this-place", "title": "Know This Place",
               "version": "0.1.0"}
PROTOCOL_VERSIONS = ["2025-11-25", "2025-06-18", "2025-03-26", "2024-11-05"]
INSTRUCTIONS = (
    "Know This Place is a cited encyclopedia of San Francisco buildings, one "
    "page per address. Use find_building to turn an address or a building's "
    "name into a page, then get_building for its history. Always link the "
    "page URL when you repeat a fact, and keep the source the summary names. "
    "The site never names current residents or owners; don't infer them.")

STREET_SUFFIXES = {
    "st": "street", "str": "street", "ave": "avenue", "av": "avenue",
    "blvd": "boulevard", "dr": "drive", "rd": "road", "ln": "lane",
    "ct": "court", "pl": "place", "ter": "terrace", "terr": "terrace",
    "hwy": "highway", "pkwy": "parkway", "cir": "circle", "aly": "alley",
    "sq": "square", "wy": "way",
}
# Planning's labels that say nothing about the building.
UNINFORMATIVE_STATUS = {"Unevaluated", "Unknown Historic Resource status"}
TIMELINE_LIMIT = 30
RECENT_PERMITS = 5


def log(*args):
    print("know-this-place-mcp:", *args, file=sys.stderr, flush=True)


# --------------------------------------------------------------------------
# The indexes
# --------------------------------------------------------------------------
def slug_words(slug: str) -> str:
    return slug.replace("-", " ")


@lru_cache(maxsize=1)
def pages() -> dict:
    """Every page by path: heading, sub line, coordinates, and the corpus row."""
    geo = ROOT / "shared" / "addresses.geojson"
    if not geo.exists():
        log("building shared/addresses.geojson (a few seconds, once)")
        subprocess.run([sys.executable, str(ROOT / "scripts" / "build_map_index.py")],
                       check=True, stdout=subprocess.DEVNULL)
    out = {}
    for f in json.loads(geo.read_text(encoding="utf-8"))["features"]:
        p = f["properties"]
        lng, lat = f["geometry"]["coordinates"]
        parts = p["p"].strip("/").split("/")
        out[p["p"]] = {"path": p["p"], "heading": p["t"], "sub": p.get("s", ""),
                       "lat": lat, "lng": lng, "kind": "building" if len(parts) == 4 else "place",
                       "area": parts[1], "street": parts[2] if len(parts) == 4 else None,
                       "number": parts[3] if len(parts) == 4 else None}
    corpus = ROOT / "corpus.jsonl"
    for line in corpus.read_text(encoding="utf-8").splitlines():
        row = json.loads(line)
        if row["path"] in out:
            out[row["path"]]["corpus"] = row
    return out


def by_street() -> dict:
    idx = {}
    for p in pages().values():
        if p["street"]:
            idx.setdefault(p["street"], []).append(p)
    return idx


def brief(p: dict, **extra) -> dict:
    """One page as a search result: enough to choose it, plus its link."""
    c = p.get("corpus", {})
    row = {"name": p["heading"], "subtitle": p["sub"], "kind": p["kind"],
           "neighborhood": area_display(f"/san-francisco/{p['area']}/"),
           "url": f"{SITE}{p['path']}", "path": p["path"]}
    for k_out, k_in in (("year_built", "year"), ("use", "use"),
                        ("historic_district", "district"), ("summary", "hook")):
        if c.get(k_in):
            row[k_out] = c[k_in]
    row.update(extra)
    return row


# --------------------------------------------------------------------------
# Address and name matching
# --------------------------------------------------------------------------
ADDRESS = re.compile(r"^\s*(\d+)([a-z])?(?:\s*[-–]\s*\d+[a-z]?)?\s+(.+)$", re.I)
RANGE = re.compile(r"^(\d+)[a-z]?[–-](\d+)[a-z]?\s")


def normalize_street(text: str) -> list[str]:
    text = re.split(r",|\bsan francisco\b|\bsf\b|\bca\b|\b94\d{3}\b", text.lower())[0]
    words = re.sub(r"[^a-z0-9 ]", " ", text).split()
    words = [w for w in words if w not in {"unit", "apt", "suite", "#"}]
    if words and words[-1] in STREET_SUFFIXES:
        words[-1] = STREET_SUFFIXES[words[-1]]
    return words


def numbers_of(p: dict) -> set[int]:
    """The street numbers a page answers to: its own, and its heading's range."""
    nums = {int(re.match(r"\d+", p["number"]).group())}
    for text in (p["heading"], p["sub"]):
        m = RANGE.match(text)
        if m and int(m.group(2)) - int(m.group(1)) < 200:
            # One side of a street shares a parity: 429–431 is 429, 431.
            nums.update(range(int(m.group(1)), int(m.group(2)) + 1, 2))
    return nums


def match_address(query: str) -> list[dict]:
    m = ADDRESS.match(query)
    if not m:
        return []
    number, words = int(m.group(1)), normalize_street(m.group(3))
    if not words:
        return []
    joined = "-".join(words)
    streets = [s for s in by_street() if s == joined] or \
              [s for s in by_street() if s.startswith(joined + "-")] or \
              [s for s in by_street() if joined in s]
    hits = []
    for s in streets:
        for p in by_street()[s]:
            if number in numbers_of(p):
                hits.append(p)
    return hits


def match_name(query: str, limit: int) -> list[dict]:
    words = set(re.sub(r"[^a-z0-9 ]", " ", query.lower()).split()) - {"the", "of", "and"}
    if not words:
        return []
    scored = []
    for p in pages().values():
        head = set(re.sub(r"[^a-z0-9 ]", " ", p["heading"].lower()).split())
        hit = len(words & head)
        if hit:
            scored.append((hit / len(words), -len(head), p))
    scored.sort(key=lambda t: (-t[0], -t[1]))
    return [p for score, _, p in scored if score >= 0.5][:limit]


def resolve(ref: str) -> dict | None:
    """A path, a page URL, or an address, to its page."""
    ref = ref.strip()
    path = ref.replace(SITE, "").split("?")[0]
    if path.endswith(("data.json", "place.json")):
        path = path.rsplit("/", 1)[0] + "/"
    if path.startswith("/") and not path.endswith("/"):
        path += "/"
    if path in pages():
        return pages()[path]
    hits = match_address(ref)
    return hits[0] if hits else None


# --------------------------------------------------------------------------
# A building, as the page shows it
# --------------------------------------------------------------------------
def source_list(rec: dict) -> list[dict]:
    out = []
    for s in rec.get("sources") or []:
        row = {"id": s.get("id"), "name": s.get("name")}
        for k in ("cites", "query", "retrieved"):
            if s.get(k):
                row[k] = s[k]
        out.append(row)
    return out


def building_summary(p: dict) -> dict:
    rec = json.loads((ROOT / p["path"].strip("/") / "data.json").read_text(encoding="utf-8"))
    heading, sub = hero_lines(rec)
    parcel = rec.get("parcel") or {}
    out = {"name": heading, "subtitle": sub, "address": rec["address"],
           "url": f"{SITE}{rec['path']}",
           "neighborhood": rec.get("sub_area") or area_display(f"/san-francisco/{p['area']}/"),
           "coordinates": rec.get("coordinates")}
    if p.get("corpus", {}).get("hook"):
        out["summary"] = p["corpus"]["hook"]
    facts = {k: parcel[k] for k in ("year_built", "stories", "units", "building_area_sqft",
                                    "lot_area_sqft", "use") if parcel.get(k)}
    if facts:
        out["building"] = facts
    b = rec.get("building") or {}
    for k in ("architect", "builder"):
        if b.get(k):
            out.setdefault("building", {})[k] = b[k]
    if rec.get("city_landmark"):
        cl = rec["city_landmark"]
        out["city_landmark"] = {k: cl[k] for k in ("name", "number") if cl.get(k)}
    label = (rec.get("historic_status") or {}).get("ceqa_status_label")
    if label and label not in UNINFORMATIVE_STATUS:
        out["historic_status"] = label
    d = rec.get("historic_district") or {}
    if d.get("name"):
        out["historic_district"] = {k: d[k] for k in ("name", "period_of_significance")
                                    if d.get(k)}
    if rec.get("notable_residents"):
        out["notable_past_residents"] = [
            {k: r[k] for k in ("name", "period", "detail", "source") if r.get(k)}
            for r in rec["notable_residents"]]
    if rec.get("occupants"):
        out["businesses_here"] = [
            {k: o[k] for k in ("name", "cuisines") if o.get(k)} for o in rec["occupants"]]
    for key in ("public_art", "public_open_space"):
        if rec.get(key):
            out[key] = [{k: v for k, v in x.items() if k in
                         ("title", "artist", "type", "name", "hours", "location")}
                        for x in rec[key]]
    n = rec.get("narrative") or {}
    if n.get("lead") or n.get("sections"):
        out["narrative"] = {k: n[k] for k in ("lead", "sections") if n.get(k)}
    history = rec.get("historical_record") or []
    if history:
        out["timeline"] = [
            {k: h[k] for k in ("date", "kind", "summary", "description", "source") if h.get(k)}
            for h in history[:TIMELINE_LIMIT]]
        if len(history) > TIMELINE_LIMIT:
            out["timeline_note"] = (f"{len(history) - TIMELINE_LIMIT} more dated entries "
                                    "are on the page.")
    permits = rec.get("permits") or []
    if permits:
        ps = rec.get("permit_summary") or {}
        recent = sorted(permits, key=lambda x: x.get("filed") or "", reverse=True)
        out["permits"] = {
            "on_file": ps.get("count_on_file", len(permits)),
            "range": ps.get("range"),
            "most_recent": [{"filed": x.get("filed"),
                             "work": x.get("description_edited") or x.get("description")}
                            for x in recent[:RECENT_PERMITS]]}
        if not out["permits"]["range"]:
            del out["permits"]["range"]
    photo = rec.get("photo") or {}
    if photo.get("file"):
        out["photo"] = {"url": f"{SITE}{rec['path']}{photo['file']}",
                        "credit": photo.get("author"), "license": photo.get("license")}
    out["sources"] = source_list(rec)
    return out


def place_summary(p: dict) -> dict:
    rec = json.loads((ROOT / p["path"].strip("/") / "place.json").read_text(encoding="utf-8"))
    out = {"name": rec["name"], "subtitle": place_sub(rec), "summary": place_hook(rec),
           "url": f"{SITE}{rec['path']}",
           "neighborhood": area_display(f"/san-francisco/{p['area']}/"),
           "coordinates": rec.get("coordinates")}
    for k in ("acres", "managed_by", "facilities", "part_of", "historical_record",
              "public_art"):
        if rec.get(k):
            out[k] = rec[k]
    out["sources"] = source_list(rec)
    return out


# --------------------------------------------------------------------------
# Tools
# --------------------------------------------------------------------------
def meters(lat1, lng1, lat2, lng2) -> float:
    r = 6371000
    a = (math.sin(math.radians(lat2 - lat1) / 2) ** 2
         + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2))
         * math.sin(math.radians(lng2 - lng1) / 2) ** 2)
    return 2 * r * math.asin(math.sqrt(a))


def tool_find_building(args):
    query, limit = str(args["query"]), min(int(args.get("limit", 5)), 25)
    hits = match_address(query)
    how = "address"
    if not hits:
        hits, how = match_name(query, limit), "name"
    q = query.strip().lower()
    hoods = [a for a in {p["area"] for p in pages().values()}
             if q in (a.replace("-", " "), area_display(f"/san-francisco/{a}/").lower())]
    if hoods:
        a = hoods[0]
        hood = {"name": area_display(f"/san-francisco/{a}/"), "kind": "neighborhood",
                "url": f"{SITE}/san-francisco/{a}/",
                "note": "A neighborhood. Call browse with this neighborhood to list it."}
        return {"matched_by": "neighborhood",
                "matches": [hood] + [brief(p) for p in hits[:limit - 1]]}
    if not hits:
        return {"matches": [], "note": "No page for that address or name. The site "
                "covers San Francisco only, and not yet every address in it."}
    return {"matched_by": how, "matches": [brief(p) for p in hits[:limit]]}


def tool_get_building(args):
    p = resolve(str(args["page"]))
    if not p:
        raise ToolError("No page found. Pass a page URL or path from find_building, "
                        "or a street address.")
    return building_summary(p) if p["kind"] == "building" else place_summary(p)


def tool_nearby(args):
    if args.get("lat") is not None and args.get("lng") is not None:
        lat, lng, origin = float(args["lat"]), float(args["lng"]), None
    elif args.get("page"):
        origin = resolve(str(args["page"]))
        if not origin:
            raise ToolError("No page found for that address or URL.")
        lat, lng = origin["lat"], origin["lng"]
    else:
        raise ToolError("Pass lat and lng, or page (an address or page URL).")
    radius = min(float(args.get("radius_m", 250)), 2000)
    limit = min(int(args.get("limit", 10)), 50)
    near = []
    for p in pages().values():
        if origin and p["path"] == origin["path"]:
            continue
        d = meters(lat, lng, p["lat"], p["lng"])
        if d <= radius:
            near.append((d, p))
    near.sort(key=lambda t: t[0])
    if args.get("only_researched"):
        near = [t for t in near if len(t[1].get("corpus", {}).get("sources", [])) > 3]
    return {"center": {"lat": lat, "lng": lng}, "radius_m": radius,
            "results": [brief(p, distance_m=round(d)) for d, p in near[:limit]]}


def tool_browse(args):
    area = (args.get("neighborhood") or "").strip().lower()
    street = (args.get("street") or "").strip()
    everything = pages().values()
    if not area and not street:
        counts = {}
        for p in everything:
            counts[p["area"]] = counts.get(p["area"], 0) + 1
        return {"neighborhoods": [
            {"name": area_display(f"/san-francisco/{a}/"), "slug": a, "pages": n,
             "url": f"{SITE}/san-francisco/{a}/"} for a, n in sorted(counts.items())]}
    if area:
        slug = re.sub(r"[^a-z0-9]+", "-", area).strip("-")
        known = {p["area"] for p in everything}
        if slug not in known:
            names = {area_display(f"/san-francisco/{a}/").lower(): a for a in known}
            slug = names.get(area) or next((a for n, a in names.items() if area in n), slug)
        everything = [p for p in everything if p["area"] == slug]
        if not everything:
            raise ToolError("No such neighborhood. Call browse with no arguments to list them.")
    if street:
        slug = "-".join(normalize_street(street))
        rows = [p for p in everything if p["street"] and
                (p["street"] == slug or p["street"].startswith(slug + "-"))]
        if not rows:
            raise ToolError("No pages on that street.")
        rows.sort(key=lambda p: (p["street"], int(re.match(r"\d+", p["number"]).group())))
        return {"street": slug_words(rows[0]["street"]).title(), "pages": len(rows),
                "addresses": [brief(p) for p in rows[:200]],
                **({"note": "First 200 shown."} if len(rows) > 200 else {})}
    streets, places = {}, []
    for p in everything:
        if p["street"]:
            streets[p["street"]] = streets.get(p["street"], 0) + 1
        else:
            places.append(brief(p))
    a = everything[0]["area"]
    return {"neighborhood": area_display(f"/san-francisco/{a}/"),
            "url": f"{SITE}/san-francisco/{a}/",
            "streets": [{"name": slug_words(s).title(), "pages": n,
                         "url": f"{SITE}/san-francisco/{a}/{s}/"}
                        for s, n in sorted(streets.items())],
            "places": places}


def tool_search(args):
    area = (args.get("neighborhood") or "").strip().lower()
    area_slug = re.sub(r"[^a-z0-9]+", "-", area).strip("-")
    use = (args.get("use") or "").lower()
    district = (args.get("historic_district") or "").lower()
    text = (args.get("text") or "").lower()
    before, after = args.get("built_before"), args.get("built_after")
    history_before = args.get("history_before")
    limit = min(int(args.get("limit", 20)), 100)
    hits = []
    for p in pages().values():
        c = p.get("corpus")
        if not c:
            continue
        if area and area_slug != p["area"] and \
                area not in area_display(f"/san-francisco/{p['area']}/").lower():
            continue
        year = c.get("year")
        if before is not None and not (year and year < int(before)):
            continue
        if after is not None and not (year and year > int(after)):
            continue
        if history_before is not None and not (
                c.get("earliest") and int(c["earliest"]) < int(history_before)):
            continue
        if use and use not in (c.get("use") or "").lower():
            continue
        if district and district not in (c.get("district") or "").lower():
            continue
        if text and text not in ((c.get("hook") or "") + " " + p["heading"]).lower():
            continue
        hits.append(p)
    hits.sort(key=lambda p: (p["corpus"].get("year") or 9999, p["path"]))
    return {"total": len(hits), "results": [brief(p) for p in hits[:limit]],
            **({"note": f"First {limit} of {len(hits)}, oldest first."}
               if len(hits) > limit else {})}


class ToolError(Exception):
    pass


TOOLS = {
    "find_building": (tool_find_building, {
        "description": "Find Know This Place pages for a San Francisco street address "
                       "(\"429 Castro St\") or a building or park's name (\"Castro "
                       "Theatre\"). Returns matching pages with their URL.",
        "inputSchema": {"type": "object", "required": ["query"], "properties": {
            "query": {"type": "string", "description": "A street address or a building's name."},
            "limit": {"type": "integer", "default": 5}}}}),
    "get_building": (tool_get_building, {
        "description": "Read one building's or place's page as structured data: what "
                       "it is, when it was built, its historic status, notable past "
                       "residents, its dated history, recent permits, and the source "
                       "for every fact.",
        "inputSchema": {"type": "object", "required": ["page"], "properties": {
            "page": {"type": "string",
                     "description": "A page URL or path from another tool, or a street address."}}}}),
    "nearby": (tool_nearby, {
        "description": "List pages near a point or near another page, nearest first.",
        "inputSchema": {"type": "object", "properties": {
            "lat": {"type": "number"}, "lng": {"type": "number"},
            "page": {"type": "string", "description": "An address or page URL to search around."},
            "radius_m": {"type": "number", "default": 250, "maximum": 2000},
            "only_researched": {"type": "boolean", "default": False,
                                "description": "Only pages citing more than the standard city datasets."},
            "limit": {"type": "integer", "default": 10}}}}),
    "browse": (tool_browse, {
        "description": "With no arguments, list the neighborhoods. With a neighborhood, "
                       "list its streets and parks. With a street, list its addresses "
                       "and a one-line summary of each.",
        "inputSchema": {"type": "object", "properties": {
            "neighborhood": {"type": "string"}, "street": {"type": "string"}}}}),
    "search": (tool_search, {
        "description": "Query every building page at once, for example the oldest "
                       "buildings in North Beach, or Mission pages whose history goes "
                       "back before 1900. Results are oldest first.",
        "inputSchema": {"type": "object", "properties": {
            "neighborhood": {"type": "string"},
            "built_before": {"type": "integer", "description": "Year built is before this year."},
            "built_after": {"type": "integer", "description": "Year built is after this year."},
            "history_before": {"type": "integer",
                               "description": "The page's timeline reaches back before this year."},
            "use": {"type": "string", "description": "Part of the assessor's use, e.g. \"Industrial\"."},
            "historic_district": {"type": "string", "description": "Part of a historic district's name."},
            "text": {"type": "string", "description": "Words in the building's name or summary."},
            "limit": {"type": "integer", "default": 20}}}}),
}
for _name, (_fn, _spec) in TOOLS.items():
    _spec["annotations"] = {"readOnlyHint": True, "openWorldHint": False}


# --------------------------------------------------------------------------
# JSON-RPC
# --------------------------------------------------------------------------
def handle(msg: dict) -> dict | None:
    """One JSON-RPC message in, its response out (None for a notification)."""
    mid, method, params = msg.get("id"), msg.get("method"), msg.get("params") or {}
    if mid is None:
        return None

    def ok(result):
        return {"jsonrpc": "2.0", "id": mid, "result": result}

    def fail(code, message):
        return {"jsonrpc": "2.0", "id": mid, "error": {"code": code, "message": message}}

    if method == "initialize":
        asked = params.get("protocolVersion")
        return ok({"protocolVersion": asked if asked in PROTOCOL_VERSIONS else PROTOCOL_VERSIONS[0],
                   "capabilities": {"tools": {"listChanged": False}},
                   "serverInfo": SERVER_INFO, "instructions": INSTRUCTIONS})
    if method == "ping":
        return ok({})
    if method == "tools/list":
        return ok({"tools": [{"name": n, "title": n.replace("_", " ").capitalize(), **spec}
                             for n, (_, spec) in TOOLS.items()]})
    if method == "tools/call":
        entry = TOOLS.get(params.get("name"))
        if not entry:
            return fail(-32602, f"Unknown tool: {params.get('name')}")
        try:
            result = entry[0](params.get("arguments") or {})
        except (ToolError, KeyError, ValueError, TypeError) as e:
            text = str(e) if isinstance(e, ToolError) else f"Bad arguments: {e}"
            return ok({"content": [{"type": "text", "text": text}], "isError": True})
        return ok({"content": [{"type": "text",
                                "text": json.dumps(result, ensure_ascii=False, indent=1)}],
                   "structuredContent": result})
    return fail(-32601, f"Method not found: {method}")


def handle_body(body):
    if isinstance(body, list):
        out = [r for r in (handle(m) for m in body) if r]
        return out or None
    return handle(body)


def serve_stdio():
    log(f"serving over stdio from {ROOT}")
    for line in sys.stdin:
        if not line.strip():
            continue
        try:
            reply = handle_body(json.loads(line))
        except json.JSONDecodeError:
            reply = {"jsonrpc": "2.0", "id": None,
                     "error": {"code": -32700, "message": "Parse error"}}
        if reply:
            sys.stdout.write(json.dumps(reply, ensure_ascii=False) + "\n")
            sys.stdout.flush()


def serve_http(host: str, port: int, allowed_origins: set[str]):
    class Handler(BaseHTTPRequestHandler):
        def _send(self, code, body=None):
            data = json.dumps(body, ensure_ascii=False).encode() if body is not None else b""
            self.send_response(code)
            if body is not None:
                self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        def do_POST(self):
            if self.path.split("?")[0] != "/mcp":
                return self._send(404, {"error": "POST to /mcp"})
            # A browser page on another site must not reach a local server
            # (DNS rebinding); MCP clients send no Origin at all.
            origin = self.headers.get("Origin")
            if origin and origin not in allowed_origins:
                return self._send(403, {"error": "origin not allowed"})
            try:
                body = json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0))))
            except (json.JSONDecodeError, ValueError):
                return self._send(400, {"jsonrpc": "2.0", "id": None,
                                        "error": {"code": -32700, "message": "Parse error"}})
            reply = handle_body(body)
            self._send(200, reply) if reply else self._send(202)

        def do_GET(self):
            if self.path.split("?")[0] == "/mcp":
                self.send_response(405)
                self.send_header("Allow", "POST")
                self.end_headers()
            else:
                self._send(200, {"server": SERVER_INFO, "endpoint": "/mcp"})

        def do_DELETE(self):
            self._send(405)

        def log_message(self, fmt, *args):
            log(fmt % args)

    log(f"serving Streamable HTTP on http://{host}:{port}/mcp from {ROOT}")
    ThreadingHTTPServer((host, port), Handler).serve_forever()


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--http", type=int, metavar="PORT",
                    help="serve Streamable HTTP on this port instead of stdio")
    ap.add_argument("--host", default="127.0.0.1",
                    help="interface for --http (default 127.0.0.1; 0.0.0.0 when hosted)")
    ap.add_argument("--allow-origin", action="append", default=[],
                    help="a browser Origin allowed to call --http (repeatable)")
    args = ap.parse_args()
    pages()  # load the indexes before the first request, not during it
    if args.http:
        serve_http(args.host, args.http, set(args.allow_origin))
    else:
        serve_stdio()


if __name__ == "__main__":
    main()
