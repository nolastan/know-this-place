#!/usr/bin/env python3
"""Regenerate sitemap.xml and sitemaps/ from the content tree. Stdlib only.

`sitemap.xml` is a <sitemapindex>, not a flat list of URLs. Its children are
one file per neighborhood, plus `sitemaps/hubs.xml` (the homepage, the city
index and the neighborhood hubs) and `sitemaps/historic-districts.xml` (the
district hubs). The split is not about the 50,000-URL limit — the whole site
fits in one file with room to spare — it is about getting an answer back:
Search Console reports coverage per submitted sitemap, so one sitemap per
neighborhood turns the coverage report into a per-neighborhood indexation
diagnostic. A single file can only say how many of seventeen thousand
near-identical pages are indexed, which is the one number that tells you
nothing about what to do next.

Every URL carries a <lastmod> sourced from the newest `sources[].retrieved`
date on the page's data.json. That field is the right one precisely because it
only moves when the page's facts do: a lastmod that advances on every rebuild
teaches crawlers to ignore it, which is worse than having none. Hub pages take
the newest lastmod among the pages below them, so a hub is "modified" exactly
when something it lists is. A page with no date to stand on gets no <lastmod>
rather than a guessed one.

No <changefreq> or <priority>: Google ignores both, and a field nothing reads
is a field that can only be wrong.

Run from anywhere: python3 scripts/build_sitemap.py
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = json.loads((ROOT / "shared" / "site-config.json").read_text())["site_url"].rstrip("/")
CONTENT = ROOT / "san-francisco"
SITEMAP_DIR = ROOT / "sitemaps"
DISTRICTS = "historic-districts"
ADDRESS_DIR = re.compile(r"^\d+[a-z]?$")  # 123, 123a — same as validate.py
DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
# "- [label](href) — hook" — the one line shape every hub list uses; same
# bullets validate.hub_md_items reads.
HUB_ITEM = re.compile(r"^- \[[^\]]+\]\(([^)]+)\)")


def page_dirs() -> list:
    """Every directory that publishes an index.html, deepest last."""
    dirs = [ROOT] if (ROOT / "index.html").exists() else []
    if CONTENT.exists():
        dirs += [p.parent for p in sorted(CONTENT.rglob("index.html"))]
    return dirs


def address_lastmods() -> dict:
    """Newest sources[].retrieved per address page — the only first-hand dates."""
    dates = {}
    for data_path in sorted(CONTENT.rglob("data.json")) if CONTENT.exists() else []:
        if not ADDRESS_DIR.match(data_path.parent.name):
            continue
        try:
            data = json.loads(data_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue  # validate.py is what complains about this
        retrieved = [s.get("retrieved") for s in data.get("sources") or []
                     if isinstance(s, dict) and DATE.match(str(s.get("retrieved")))]
        if retrieved:
            dates[data_path.parent] = max(retrieved)
    return dates


def listed_addresses(page_dir: Path) -> list:
    """The address pages a hub's index.md lists, resolved against the tree.

    Buildings only, not the streets a hub also links for navigation: a street
    hub would drag in every building on it, including the ones this hub does
    not list, and the date would then move for a page that did not change.
    """
    md = page_dir / "index.md"
    if not md.exists():
        return []
    out = []
    for line in md.read_text(encoding="utf-8").splitlines():
        m = HUB_ITEM.match(line)
        if not m or "://" in m.group(1) or m.group(1).startswith("#"):
            continue
        href = m.group(1)
        target = (ROOT / href.lstrip("/")) if href.startswith("/") else (page_dir / href)
        target = Path(target).resolve()
        if ADDRESS_DIR.match(target.name) and (target / "index.html").exists():
            out.append(target)
    return out


def resolve_lastmod(page_dir: Path, own: dict, below: dict, cache: dict):
    """A page's lastmod: its own date, or the newest among the pages below it.

    "Below it" is the page tree for every hub but one. A district hub has no
    directory of its own to hold pages — the buildings in a district live under
    their streets — so its content is the list of buildings it names, and its
    lastmod is the newest date among those.
    """
    if page_dir in cache:
        return cache[page_dir]
    dates = [own[page_dir]] if page_dir in own else []
    children = below.get(page_dir, [])
    if not dates and not children:
        dates = [own[p] for p in listed_addresses(page_dir) if p in own]
    dates += [d for d in (resolve_lastmod(c, own, below, cache) for c in children) if d]
    cache[page_dir] = max(dates) if dates else None
    return cache[page_dir]


def group_of(page_dir: Path) -> str:
    """Which child sitemap a page belongs in.

    The homepage, the city index and the neighborhood hubs go together in
    `hubs`: they are the handful of pages that have to be indexed, and a
    coverage report on 44 URLs is readable page by page. Everything under a
    neighborhood — its street hubs and its addresses — goes in that
    neighborhood's file, which is the number worth watching.
    """
    if page_dir == ROOT:
        return "hubs"
    parts = page_dir.relative_to(ROOT).parts[1:]  # drop "san-francisco"
    if not parts:
        return "hubs"
    if parts[0] == DISTRICTS:
        return DISTRICTS
    return parts[0] if len(parts) > 1 else "hubs"


def url_for(page_dir: Path) -> str:
    if page_dir == ROOT:
        return "/"
    return "/" + page_dir.relative_to(ROOT).as_posix() + "/"


def xml(root_tag: str, entries: list) -> str:
    lines = ['<?xml version="1.0" encoding="UTF-8"?>',
             f'<{root_tag} xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for tag, loc, lastmod in entries:
        mod = f"<lastmod>{lastmod}</lastmod>" if lastmod else ""
        lines.append(f"  <{tag}><loc>{SITE}{loc}</loc>{mod}</{tag}>")
    lines.append(f"</{root_tag}>")
    return "\n".join(lines) + "\n"


def main() -> None:
    dirs = page_dirs()
    own = address_lastmods()
    # The published tree, not the filesystem: a hub rolls up the pages the site
    # actually serves under it, and nothing else that happens to sit on disk.
    below = {}
    for d in dirs:
        below.setdefault(d.parent, []).append(d)
    cache = {}
    lastmod = {d: resolve_lastmod(d, own, below, cache) for d in dirs}

    groups = {}
    for d in dirs:
        groups.setdefault(group_of(d), []).append(d)

    # hubs first, then the districts, then the neighborhoods in order — the
    # same top-down reading order the site itself has.
    order = sorted(groups, key=lambda g: (g != "hubs", g != DISTRICTS, g))

    SITEMAP_DIR.mkdir(exist_ok=True)
    index = []
    for group in order:
        pages = sorted(groups[group], key=url_for)
        child = SITEMAP_DIR / f"{group}.xml"
        child.write_text(
            xml("urlset", [("url", url_for(p), lastmod[p]) for p in pages]),
            encoding="utf-8")
        newest = max((lastmod[p] for p in pages if lastmod[p]), default=None)
        index.append(("sitemap", f"/sitemaps/{group}.xml", newest))

    (ROOT / "sitemap.xml").write_text(xml("sitemapindex", index), encoding="utf-8")

    # A neighborhood that is renamed or removed would otherwise leave its
    # sitemap behind, still submitted and still listing pages that 404.
    keep = {f"{g}.xml" for g in groups}
    stale = [f for f in sorted(SITEMAP_DIR.glob("*.xml")) if f.name not in keep]
    for f in stale:
        f.unlink()

    undated = sum(1 for d in dirs if not lastmod[d])
    print(f"sitemap.xml written with {len(index)} child sitemap(s), "
          f"{len(dirs)} URL(s) total")
    if undated:
        print(f"     {undated} page(s) with no source date carry no <lastmod>")
    for f in stale:
        print(f"     removed stale {f.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
