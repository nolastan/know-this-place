#!/usr/bin/env python3
"""Contract checks for Know This Place pages.

Bespoke page bodies are the point of this site; this script only enforces the
minimal shared contract described in shared/AGENTS.md. Stdlib only.

Run from anywhere: python3 scripts/validate.py
"""
import html
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONFIG = json.loads((ROOT / "shared" / "site-config.json").read_text())
SITE = CONFIG["site_url"].rstrip("/")
REPO = CONFIG["repo_url"].rstrip("/")

ADDRESS_DIR = re.compile(r"^\d+[a-z]?$")  # 123, 123a
errors: list[str] = []


def err(path: Path, msg: str) -> None:
    errors.append(f"{path.relative_to(ROOT)}: {msg}")


def check_html(html_path: Path, is_address: bool) -> None:
    html = html_path.read_text(encoding="utf-8")
    rel_dir = "/" + html_path.parent.relative_to(ROOT).as_posix() + "/"
    if html_path.parent == ROOT:
        rel_dir = "/"

    if '<link rel="stylesheet" href="/shared/site.css">' not in html:
        err(html_path, "missing the shared stylesheet link")
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
        if "application/ld+json" not in html:
            err(html_path, "address page missing JSON-LD structured data")
        if f"{REPO}/issues/new" not in html or "page=" not in html:
            err(html_path, "address page missing prefilled feedback link")
        if "google.com/maps/embed" in html and "streetview?key=&" in html:
            err(html_path, "street view iframe has an empty API key")


def check_address_dir(page_dir: Path) -> None:
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

    check_narrative(data_path, data)


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
        is_address = bool(ADDRESS_DIR.match(html_path.parent.name))
        check_html(html_path, is_address)
        if is_address:
            check_address_dir(html_path.parent)
        elif html_path.parent != content:
            # The city-level index (san-francisco/index.md) has no generator
            # counterpart — write_neighborhood_hub/write_street_hub only cover
            # neighborhood and street hubs — so there is no "regenerate
            # index.html from index.md" fix to point someone at here. It's
            # hand-authored prose in both files; keeping them in sync is a
            # content edit, not a build-contract check.
            check_hub_sync(html_path.parent)

    # Every page should be reachable through the sitemap once one exists.
    sitemap = ROOT / "sitemap.xml"
    if sitemap.exists():
        sitemap_text = sitemap.read_text(encoding="utf-8")
        for html_path in html_pages:
            rel_dir = "/" + html_path.parent.relative_to(ROOT).as_posix() + "/"
            if html_path.parent == ROOT:
                rel_dir = "/"
            if f"<loc>{SITE}{rel_dir}</loc>" not in sitemap_text:
                err(html_path, "not in sitemap.xml — run scripts/build_sitemap.py")

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

    if errors:
        print(f"FAIL — {len(errors)} problem(s):")
        for e in errors:
            print(f"  - {e}")
        return 1
    print(f"OK — {len(html_pages)} page(s) pass the contract")
    return 0


if __name__ == "__main__":
    sys.exit(main())
