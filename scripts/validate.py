#!/usr/bin/env python3
"""Contract checks for Know This Place pages.

Bespoke page bodies are the point of this site; this script only enforces the
minimal shared contract described in shared/AGENTS.md. Stdlib only.

The one check with teeth beyond that contract is **render parity**: an address
page's `index.html` must be exactly what `seed_pages.render_html` produces from
its `data.json`. `data.json` is the single source of truth and `index.html` is
its build artifact, so a hand edit to the HTML is a second source of truth by
definition — this check is what makes that impossible rather than something the
repo periodically discovers. A page opts out with `"rendered": false`, which is
counted and printed on every run.

Run from anywhere: python3 scripts/validate.py
                   python3 scripts/validate.py --prune-render-backlog
"""
import collections
import html
import json
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
# The renderer *is* the contract for an address page's index.html, so the
# checker has to be able to run it. Both scripts are stdlib-only siblings and
# seed_pages does no network on import. `scripts/__pycache__/` is tracked in
# git for now, so importing it would otherwise leave a modified file behind on
# every run.
sys.dont_write_bytecode = True
import seed_pages  # noqa: E402
from seed_pages import ADDRESS_DIR  # noqa: E402  — an address dir: 123, 123a

ROOT = Path(__file__).resolve().parent.parent
CONFIG = json.loads((ROOT / "shared" / "site-config.json").read_text())
SITE = CONFIG["site_url"].rstrip("/")
REPO = CONFIG["repo_url"].rstrip("/")

# Site icons, on every page for the same reason the stylesheet is: they are
# shared chrome, not page content. `shared/icon.svg` is the source of truth for
# the mark; favicon.ico and apple-touch-icon.png are derived from it.
ICON_LINKS = (
    '<link rel="icon" href="/favicon.ico" sizes="32x32">',
    '<link rel="icon" href="/shared/icon.svg" type="image/svg+xml">',
    '<link rel="apple-touch-icon" href="/apple-touch-icon.png">',
    '<link rel="manifest" href="/shared/site.webmanifest">',
)

errors: list[str] = []

# Counted, not errors. `opted_out` is pages whose data.json says
# `"rendered": false`; `backlogged` is pages the renderer can't yet reproduce
# that render-backlog.txt grandfathers; `backlog_stale` is entries in that file
# that no longer need to be there.
opted_out: list[str] = []
backlogged: list[str] = []
backlog_stale: list[str] = []

# Filled in as the address pages are read, and checked once at the end:
# district name -> the pages that say they stand inside it. Gathering it here
# rather than re-walking the tree costs nothing — every data.json is already
# parsed for the parity check.
district_pages: dict = collections.defaultdict(set)


def err(path: Path, msg: str) -> None:
    errors.append(f"{path.relative_to(ROOT)}: {msg}")


# See the file's own header for what it is and why it can only shrink. Read
# through seed_pages so the checker that excuses these pages from parity and
# the renderer that refuses to overwrite them agree on the list by construction.
BACKLOG_PATH = seed_pages.RENDER_BACKLOG_PATH
BACKLOG = seed_pages.load_render_backlog()


def check_html(html_path: Path, html: str, is_address: bool) -> None:
    rel_dir = "/" + html_path.parent.relative_to(ROOT).as_posix() + "/"
    if html_path.parent == ROOT:
        rel_dir = "/"

    if '<link rel="stylesheet" href="/shared/site.css">' not in html:
        err(html_path, "missing the shared stylesheet link")
    for link in ICON_LINKS:
        if link not in html:
            err(html_path, f"missing a shared icon link: {link}")
    if '<script type="module" src="/shared/site.js"></script>' not in html:
        err(html_path, "missing the shared enhancement script (/shared/site.js)")
    # Enhancement layer only: no page-level or inline scripts beyond the shared
    # module and the JSON-LD data block. Guards the content-stays-in-HTML rule.
    #
    # The homepage is the one deliberate exception: it is a map, not a content
    # page, so it carries Mapbox GL JS and its own init script. Nothing under
    # san-francisco/ may do this — a page whose facts render only in JS is
    # invisible to search, which is the whole point of the rule.
    if rel_dir != "/":
        for m in re.finditer(r"<script\b([^>]*)>", html):
            attrs = m.group(1)
            is_shared = 'src="/shared/site.js"' in attrs
            is_jsonld = 'type="application/ld+json"' in attrs
            if not (is_shared or is_jsonld):
                err(html_path, "unexpected <script> — JS lives only in /shared/site.js "
                               "(content must stay in the HTML)")
    if f'<link rel="canonical" href="{SITE}{rel_dir}">' not in html:
        err(html_path, f'canonical link missing or wrong (expected {SITE}{rel_dir})')
    if '<meta name="description"' not in html:
        err(html_path, "missing meta description")
    if "<title>" not in html or "<title></title>" in html:
        err(html_path, "missing or empty <title>")
    if rel_dir != "/" and 'class="breadcrumb"' not in html:
        err(html_path, "missing breadcrumb nav")
    if 'class="site-footer"' not in html:
        err(html_path, "missing site footer")

    if is_address:
        # One page, one timeline. Splitting the permits off from the historical
        # record gave a reader two rails that each restarted the clock; they are
        # one sequence of things that happened here, so they share one `.vtl`.
        rails = len(re.findall(r'<ol class="vtl"', html))
        if rails > 1:
            err(html_path, f"{rails} timelines — an address page has one `.vtl` "
                           "holding every dated entry, oldest first (AGENTS.md)")
        if "application/ld+json" not in html:
            err(html_path, "address page missing JSON-LD structured data")
        if f"{REPO}/issues/new" not in html or "page=" not in html:
            err(html_path, "address page missing prefilled feedback link")
        if "google.com/maps/embed" in html and "streetview?key=&" in html:
            err(html_path, "street view iframe has an empty API key")


# Cache for check_internal_links: a resolved target path -> does it exist.
# The sweep resolves ~185,000 hrefs across the site and they collapse onto far
# fewer targets (every street hub links the same neighborhood, every address
# page the same stylesheet), so the stat calls are the part worth not repeating.
_link_targets: dict = {}


def check_internal_links(html_path: Path, html_text: str) -> None:
    """Every internal href on a page must resolve to a file on disk.

    The one failure mode of generated cross-linking: a hub lists a building
    whose page was never created, or a page moves and the index that points at
    it isn't rebuilt. Both render as a live link to a 404, which nothing else
    here would notice. Same contract as the sitemap and addresses.geojson
    checks above — these lists are derived, so a failure means re-running the
    script that builds the index (`seed_pages.py hubs` for a hub's list), not
    hand-editing the HTML.

    Both href forms on the site are resolved: absolute ("/san-francisco/…/",
    what a breadcrumb and a cross-reference use) and relative ("2262/", what a
    hub's list of children uses). A directory href must hold an index.html; an
    href naming a file must be that file.
    """
    for raw in re.findall(r'href="([^"]*)"', html_text):
        href = html.unescape(raw).split("#")[0].split("?")[0]
        # Off-site (http:, mailto:, //cdn…) and pure fragments aren't ours.
        if not href or href.startswith("//") or ":" in href.split("/")[0]:
            continue
        base = ROOT if href.startswith("/") else html_path.parent
        target = Path(os.path.normpath(base / href.lstrip("/")))
        if not target.suffix:
            target = target / "index.html"
        rel = os.path.relpath(target, ROOT)
        if rel.startswith(".."):
            # Enough "../" to climb past the repo root. Whatever it finds on
            # this disk, the deployed site has nothing above ROOT to serve.
            err(html_path, f"internal link '{raw}' resolves outside the site root")
            continue
        if target not in _link_targets:
            _link_targets[target] = target.exists()
        if not _link_targets[target]:
            err(html_path, f"dangling internal link '{raw}' — nothing at {rel}")


def check_render_parity(page_dir: Path, data: dict, on_disk: str) -> None:
    """`index.html` must be exactly what the renderer produces from `data.json`.

    This is the check that makes the two files structurally incapable of
    drifting. `data.json` is the single source of truth (AGENTS.md ground rule
    1) and `index.html` is its build artifact, so there is exactly one correct
    HTML for a given `data.json` and `seed_pages.py render` writes it. A page
    edited by hand fails here, and the fix is always the same: put the change
    in `data.json` and re-render.

    Two pages are exempt, for two different reasons:

    - `"rendered": false` — a deliberate, permanent opt-out for a page whose
      HTML a person maintains. Counted and reported on every run, because an
      opted-out page silently stops tracking site-wide design changes.
    - a page listed in `render-backlog.txt` — drift that predates this check,
      grandfathered until the sweep reaches it. That list only shrinks.
    """
    rel = page_dir.relative_to(ROOT).as_posix()
    rendered = data.get("rendered")
    if rendered is not None and not isinstance(rendered, bool):
        err(page_dir / "data.json",
            '"rendered" must be a boolean — only `false` opts a page out of '
            "rendering; leave the key out otherwise")
        return
    if not seed_pages.renders(data):
        opted_out.append(rel)
        if rel in BACKLOG:
            backlog_stale.append(rel)
        return

    try:
        expected = seed_pages.render_html(data)
    except Exception as e:
        if rel in BACKLOG:
            backlogged.append(rel)
            return
        err(page_dir / "data.json",
            f"the renderer cannot produce this page ({type(e).__name__}: {e}) "
            f"— fix seed_pages.py, or the data it chokes on")
        return

    if on_disk == expected:
        if rel in BACKLOG:
            backlog_stale.append(rel)
        return
    if rel in BACKLOG:
        backlogged.append(rel)
        return
    err(page_dir / "index.html",
        "does not match what the renderer produces from data.json — index.html "
        "is a build artifact, not a source file. Put the change in data.json "
        f"and run: python3 scripts/seed_pages.py render {rel}")


def check_address_dir(page_dir: Path, on_disk: str) -> None:
    for required in ("index.html", "data.json"):
        if not (page_dir / required).exists():
            err(page_dir / required, "required file missing")

    # data.json is the single source of truth for an address page; prose lives
    # in its "narrative" field. A stray index.md is the old duplicate surface
    # and must not come back.
    if (page_dir / "index.md").exists():
        err(page_dir / "index.md",
            "address pages have no index.md — put prose in data.json's "
            '"narrative" field (see AGENTS.md)')

    data_path = page_dir / "data.json"
    if not data_path.exists():
        return
    try:
        data = json.loads(data_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        err(data_path, f"invalid JSON: {e}")
        return

    if not data.get("address"):
        err(data_path, 'missing "address"')
    sources = data.get("sources")
    if not isinstance(sources, list) or not sources:
        err(data_path, '"sources" must be a non-empty list — every page cites its data')
    else:
        for i, s in enumerate(sources):
            for key in ("id", "retrieved"):
                if not isinstance(s, dict) or not s.get(key):
                    err(data_path, f'sources[{i}] missing "{key}"')

    for name in seed_pages.districts_named(data):
        district_pages[name].add("/" + page_dir.relative_to(ROOT).as_posix() + "/")

    check_narrative(data_path, data)
    check_render_parity(page_dir, data, on_disk)


def hub_md_items(text: str) -> dict:
    """href -> hook text for each '- [label](href) — hook' bullet in a hub's index.md.

    A bullet's hook may wrap onto indented continuation lines; those are
    folded back into one string so they compare against index.html's
    single-line rendering of the same hook.
    """
    items: dict = {}
    lines = text.splitlines()
    i = 0
    while i < len(lines):
        m = re.match(r"^- \[[^\]]+\]\(([^)]+)\)\s+—\s+(.+)$", lines[i])
        if not m:
            i += 1
            continue
        href, hook = m.group(1), [m.group(2).strip()]
        i += 1
        while i < len(lines) and lines[i].strip() and not re.match(r"^(#|- )", lines[i]):
            hook.append(lines[i].strip())
            i += 1
        items[href] = " ".join(hook)
    return items


def hub_html_items(text: str) -> dict:
    """href -> hook text for each hub list <li> in index.html."""
    return {m.group(1): html.unescape(re.sub(r"\s+", " ", m.group(2))).strip()
            for m in re.finditer(
                r'<a href="([^"]+)">[^<]*</a><br>\s*<span class="hook">(.+?)</span>',
                text, re.S)}


def street_hub_hook_overrides(dir_path: Path) -> dict:
    """slug -> data.json["hook"], for each child address page that has one set by hand.

    Only *explicit* overrides are collected — `hook_for`'s computed default
    (used when a page has no "hook" key) is deliberately not reproduced here.
    That default has changed before as `building_type` grew new cases (see its
    "residential" fallback history) and will again; a hub snapshot made before
    such a change is expected to read differently from a fresh one — that's
    the same "fixed by hand on affected pages, not retroactively" rule
    AGENTS.md states for address pages, applied to hubs. An explicit hook
    override is different: a human wrote it as this building's one true line,
    so every rendering of it must agree.

    A directory with at least one data.json child is a street hub; one with
    none (a neighborhood or city hub, whose children are street/neighborhood
    dirs with no data.json of their own) is not.
    """
    out = {}
    for d in sorted(dir_path.iterdir()):
        data_path = d / "data.json"
        if not (d.is_dir() and data_path.exists()):
            continue
        try:
            rec = json.loads(data_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue  # invalid JSON is reported by the page's own checks
        if rec.get("hook"):
            out[d.name] = rec["hook"]
    return out


def check_hub_covers_children(dir_path: Path) -> None:
    """Every page beneath a street hub must be listed in that hub's index.md.

    `check_hub_sync` is the same contract read the other way: it compares the
    hub's two files against each other, which catches a list that drifted in
    one of them but not a list that is stale in both. That is the case here —
    a page seeded under a street after the hub was last built is in the
    sitemap and reachable by URL, yet a reader browsing the street never sees
    it. AGENTS.md's directory contract makes the hub the way in ("Hub pages
    ... list and link what's beneath them. Keep them current when adding
    pages"), so an unlisted page is a broken site, not a cosmetic gap — the
    mirror of a hub link that points at a page which isn't there.

    Only street hubs are checked: a directory with at least one data.json
    child, per `street_hub_hook_overrides`. A hub whose own index.md carries
    hand-written sections is one `write_street_hub` refuses to rebuild, but
    the requirement is the same either way — the list is then updated by hand.
    """
    md_path = dir_path / "index.md"
    if not md_path.exists():
        return
    children = sorted(d.name for d in dir_path.iterdir()
                      if d.is_dir() and (d / "data.json").exists())
    if not children:
        return  # a neighborhood or city hub; its children are hubs, not pages
    listed = {href.rstrip("/") for href in hub_md_items(md_path.read_text(encoding="utf-8"))}
    missing = [c for c in children if c not in listed]
    if missing:
        err(md_path, f"{len(missing)} page(s) beneath this hub are not in its "
                     f"list ({', '.join(missing)}) — a reader browsing the "
                     f"street can't reach them; rebuild with "
                     f"scripts/seed_pages.py hubs")


def check_hub_sync(dir_path: Path) -> None:
    """A hub page's index.md and index.html must show the same list.

    `write_street_hub` / `write_neighborhood_hub` generate both files from the
    same data in one pass, so a fresh rebuild always agrees — divergence means
    a hand edit landed in only one file. index.md is the source of truth
    (AGENTS.md: a hub's "prose lives in its index.md"); the fix is always to
    edit index.md and regenerate index.html from it (`seed_pages.py hubs`),
    never the reverse.

    A street hub's list has one deeper anchor beyond that: AGENTS.md also
    says the list "is generated from those pages' data.json, each
    contributing its own hook line", and a hand-written data.json["hook"]
    "always wins over a generated one" (`seed_pages.hook_for`). So where a
    child page has an explicit hook override, both files must match *that*,
    not just each other — see `street_hub_hook_overrides`.
    """
    md_path, html_path = dir_path / "index.md", dir_path / "index.html"
    if not (md_path.exists() and html_path.exists()):
        return
    md_items = hub_md_items(md_path.read_text(encoding="utf-8"))
    html_items = hub_html_items(html_path.read_text(encoding="utf-8"))
    if not md_items and not html_items:
        return

    overrides = street_hub_hook_overrides(dir_path)
    for href in sorted(set(md_items) | set(html_items)):
        md_hook, html_hook = md_items.get(href), html_items.get(href)
        override = overrides.get(href.rstrip("/"))
        if md_hook is None:
            err(html_path, f"'{href}' appears in index.html but not index.md — "
                           f"index.md is the source of truth; add it there")
        elif html_hook is None:
            err(html_path, f"'{href}' is in index.md but missing from index.html — "
                           f"regenerate with scripts/seed_pages.py hubs")
        elif md_hook != html_hook:
            err(html_path, f"'{href}' hook differs between index.md and index.html "
                           f"— index.md is the source of truth; fix it there and "
                           f"regenerate index.html with scripts/seed_pages.py hubs")
        elif override and md_hook != override:
            err(md_path, f"'{href}' hook (\"{md_hook}\") doesn't match "
                         f"{href}data.json's hand-written \"hook\" (\"{override}\") — "
                         f"that override is the source of truth for this entry; "
                         f"regenerate with scripts/seed_pages.py hubs")


def check_district_hubs() -> None:
    """Every district hub lists every page inside it, and no hub outlives its district.

    `check_hub_covers_children` read one level up. A district hub is derived
    from the pages that name the district, exactly as the sitemap and the map
    index are derived from the tree — so a hub whose list has gone stale in
    both its files is invisible to everything else here, and the fix is always
    to re-run the generator rather than to edit a list by hand.

    A district under `DISTRICT_MIN_PAGES` has no hub by design and is not
    checked; see `seed_pages.DISTRICT_MIN_PAGES` for why that floor exists.
    """
    hubs = ROOT / "san-francisco" / seed_pages.DISTRICTS_DIR
    if not hubs.exists():
        return
    earned = {seed_pages.district_slug(name): (name, paths)
              for name, paths in district_pages.items()
              if len(paths) >= seed_pages.DISTRICT_MIN_PAGES}

    for slug, (name, paths) in sorted(earned.items()):
        md = hubs / slug / "index.md"
        if not md.exists():
            err(md, f"{len(paths)} page(s) stand in the {name}, which has no hub "
                    f"— run scripts/seed_pages.py districts")
            continue
        listed = set(hub_md_items(md.read_text(encoding="utf-8")))
        missing = sorted(paths - listed)
        if missing:
            err(md, f"{len(missing)} page(s) in this district are not in its list "
                    f"(starting {missing[0]}) — a reader browsing the district "
                    f"can't reach them; run scripts/seed_pages.py districts")

    for hub_dir in sorted(hubs.iterdir()):
        if hub_dir.is_dir() and hub_dir.name not in earned:
            err(hub_dir / "index.md",
                f"no district with {seed_pages.DISTRICT_MIN_PAGES} or more "
                f"documented buildings maps here any more — delete the directory")

    index_md = hubs / "index.md"
    if index_md.exists():
        listed = {h.rstrip("/") for h in hub_md_items(index_md.read_text(encoding="utf-8"))}
        absent = sorted(set(earned) - listed)
        if absent:
            err(index_md, f"{len(absent)} district(s) with a hub are not on this "
                          f"index ({', '.join(absent[:5])}) — run "
                          f"scripts/seed_pages.py districts")


def check_narrative(data_path: Path, data: dict) -> None:
    """Light shape check for the narrative field (all prose lives here)."""
    narrative = data.get("narrative")
    if narrative is None:
        return  # optional — a page may be all data and no prose
    if not isinstance(narrative, dict):
        err(data_path, '"narrative" must be an object')
        return
    if "lead" in narrative and not isinstance(narrative["lead"], str):
        err(data_path, '"narrative.lead" must be a string')
    sections = narrative.get("sections")
    if sections is not None:
        if not isinstance(sections, list):
            err(data_path, '"narrative.sections" must be a list')
        else:
            for i, s in enumerate(sections):
                if not isinstance(s, dict) or not s.get("heading") or not s.get("body"):
                    err(data_path, f'narrative.sections[{i}] needs "heading" and "body"')


def main() -> int:
    content = ROOT / "san-francisco"
    html_pages = [ROOT / "index.html"] if (ROOT / "index.html").exists() else []
    html_pages += sorted(content.rglob("index.html")) if content.exists() else []

    for html_path in html_pages:
        text = html_path.read_text(encoding="utf-8")
        is_address = bool(ADDRESS_DIR.match(html_path.parent.name))
        check_html(html_path, text, is_address)
        check_internal_links(html_path, text)
        if is_address:
            check_address_dir(html_path.parent, text)
        elif html_path.parent != content:
            # The city-level index (san-francisco/index.md) has no generator
            # counterpart — write_neighborhood_hub/write_street_hub only cover
            # neighborhood and street hubs — so there is no "regenerate
            # index.html from index.md" fix to point someone at here. It's
            # hand-authored prose in both files; keeping them in sync is a
            # content edit, not a build-contract check.
            check_hub_sync(html_path.parent)
            check_hub_covers_children(html_path.parent)

    check_district_hubs()

    # The icon links every page carries have to resolve to something.
    for icon in ("favicon.ico", "apple-touch-icon.png", "shared/icon.svg",
                 "shared/icon-192.png", "shared/icon-512.png",
                 "shared/site.webmanifest"):
        if not (ROOT / icon).exists():
            err(ROOT / icon, "site icon missing — every page links to it")

    # Every page should be reachable through the sitemap once one exists.
    # sitemap.xml is an index now, so the URLs live one level down, in the
    # per-neighborhood children it points at; a page missing from all of them
    # is a page Google is never told about.
    sitemap = ROOT / "sitemap.xml"
    if sitemap.exists():
        index_text = sitemap.read_text(encoding="utf-8")
        children = [ROOT / rel.lstrip("/") for rel in
                    re.findall(rf"<loc>{re.escape(SITE)}(/\S+?\.xml)</loc>", index_text)]
        listed = set()
        for child in children:
            if not child.exists():
                err(child, "listed in sitemap.xml but missing — "
                           "run scripts/build_sitemap.py")
                continue
            listed |= set(re.findall(rf"<loc>{re.escape(SITE)}(\S*?)</loc>",
                                     child.read_text(encoding="utf-8")))
        for html_path in html_pages:
            rel_dir = "/" + html_path.parent.relative_to(ROOT).as_posix() + "/"
            if html_path.parent == ROOT:
                rel_dir = "/"
            if rel_dir not in listed:
                err(html_path, "not in the sitemap — run scripts/build_sitemap.py")
        # And nothing in the sitemap that has stopped existing: a submitted
        # URL that 404s is a crawl error Search Console reports against the
        # sitemap it came from, which is the report this split exists to make
        # readable. One error, not one per URL — the fix is the same command.
        gone = sorted(u for u in listed
                      if u != "/" and not (ROOT / u.strip("/") / "index.html").exists())
        if gone:
            err(sitemap, f"{len(gone)} sitemap URL(s) no longer exist, starting "
                         f"{gone[0]} — run scripts/build_sitemap.py")

    # And every address should be a dot on the homepage map. Same contract as
    # the sitemap: the index is derived, so a new page just means re-running
    # the script that builds it.
    geojson = ROOT / "shared" / "addresses.geojson"
    if geojson.exists():
        try:
            mapped = {
                f.get("properties", {}).get("p")
                for f in json.loads(geojson.read_text(encoding="utf-8"))["features"]
            }
        except (json.JSONDecodeError, KeyError, TypeError) as e:
            err(geojson, f"invalid GeoJSON — run scripts/build_map_index.py ({e})")
            mapped = None
        if mapped is not None:
            for html_path in html_pages:
                if not ADDRESS_DIR.match(html_path.parent.name):
                    continue
                rel_dir = "/" + html_path.parent.relative_to(ROOT).as_posix() + "/"
                if rel_dir not in mapped:
                    err(html_path, "not in shared/addresses.geojson — "
                                   "run scripts/build_map_index.py")

    # And every address should have its neighbors in the link index. Same
    # contract again — but this one is checked in both directions, because a
    # path in the index that no longer exists becomes a dangling link the
    # moment the renderer starts printing them.
    nearby = ROOT / "shared" / "nearby.json"
    if nearby.exists():
        try:
            indexed = json.loads(nearby.read_text(encoding="utf-8"))["paths"]
        except (json.JSONDecodeError, KeyError, TypeError) as e:
            err(nearby, f"invalid link index — run scripts/build_link_index.py ({e})")
            indexed = None
        if indexed is not None:
            known = set(indexed)
            for html_path in html_pages:
                if not ADDRESS_DIR.match(html_path.parent.name):
                    continue
                rel_dir = "/" + html_path.parent.relative_to(ROOT).as_posix() + "/"
                if rel_dir not in known:
                    err(html_path, "not in shared/nearby.json — "
                                   "run scripts/build_link_index.py")
            # Reported as one error, not one per stale entry: a neighborhood
            # moved or removed would otherwise print hundreds of lines that all
            # have the same one-command fix.
            gone = [q for q in indexed
                    if not (ROOT / q.strip("/") / "index.html").exists()]
            if gone:
                err(nearby, f"{len(gone)} indexed page(s) no longer exist, "
                            f"starting {gone[0]} — run scripts/build_link_index.py")

    # Entries in the backlog that no longer belong there. Reported as one
    # error, not one per page: the file is 1,010 lines long today and the sweep
    # that empties it would otherwise print a thousand identical complaints.
    if backlog_stale:
        err(BACKLOG_PATH,
            f"{len(backlog_stale)} listed page(s) no longer need grandfathering "
            f"— they render cleanly now, or have opted out. Drop them: "
            f"python3 scripts/validate.py --prune-render-backlog")

    if errors:
        print(f"FAIL — {len(errors)} problem(s):")
        for e in errors:
            print(f"  - {e}")
    else:
        print(f"OK — {len(html_pages)} page(s) pass the contract")

    # Always, pass or fail. An opt-out is a page that has stopped tracking
    # site-wide design changes, and a backlogged page is one whose HTML nothing
    # is checking; both are invisible unless something says them out loud.
    print(f'     {len(opted_out)} page(s) opted out of rendering ("rendered": false)')
    if backlogged:
        print(f"     {len(backlogged)} page(s) awaiting the render sweep "
              f"(scripts/render-backlog.txt)")
    return 1 if errors else 0


def prune_backlog() -> int:
    """Drop the entries in render-backlog.txt that no longer need to be there.

    Removal only, never addition — that is what keeps the file a ratchet. A
    page that starts failing the parity check cannot be silenced by running
    this; it has to be re-rendered.
    """
    if not BACKLOG_PATH.exists():
        print("no scripts/render-backlog.txt — nothing to prune")
        return 0
    lines = BACKLOG_PATH.read_text(encoding="utf-8").splitlines()
    still: set = set()
    for rel in sorted(BACKLOG):
        page_dir = ROOT / rel
        data_path = page_dir / "data.json"
        html_path = page_dir / "index.html"
        if not (data_path.exists() and html_path.exists()):
            continue
        try:
            data = json.loads(data_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            still.add(rel)   # the page's own checks will report the bad JSON
            continue
        if not seed_pages.renders(data):
            continue
        try:
            expected = seed_pages.render_html(data)
        except Exception:
            still.add(rel)
            continue
        if html_path.read_text(encoding="utf-8") != expected:
            still.add(rel)

    kept = [ln for ln in lines
            if not ln.strip() or ln.lstrip().startswith("#") or ln.strip() in still]
    if len(kept) == len(lines):
        print(f"scripts/render-backlog.txt: {len(still)} entr(ies), nothing to prune")
        return 0
    if still:
        BACKLOG_PATH.write_text("\n".join(kept) + "\n", encoding="utf-8")
    else:
        BACKLOG_PATH.unlink()   # the sweep is done; the file has no reason to exist
    print(f"scripts/render-backlog.txt: dropped {len(BACKLOG) - len(still)} entr(ies), "
          + (f"{len(still)} left" if still else "backlog empty — file removed"))
    return 0


if __name__ == "__main__":
    if "--prune-render-backlog" in sys.argv[1:]:
        sys.exit(prune_backlog())
    sys.exit(main())
