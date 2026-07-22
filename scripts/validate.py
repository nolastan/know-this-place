#!/usr/bin/env python3
"""Contract checks for Know This Place pages.

Bespoke page bodies are the point of this site; this script only enforces the
minimal shared contract described in shared/AGENTS.md. Stdlib only.

Run from anywhere: python3 scripts/validate.py
"""
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
    for required in ("index.md", "index.html", "data.json"):
        if not (page_dir / required).exists():
            err(page_dir / required, "required file missing")

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


def main() -> int:
    content = ROOT / "san-francisco"
    html_pages = [ROOT / "index.html"] if (ROOT / "index.html").exists() else []
    html_pages += sorted(content.rglob("index.html")) if content.exists() else []

    for html_path in html_pages:
        is_address = bool(ADDRESS_DIR.match(html_path.parent.name))
        check_html(html_path, is_address)
        if is_address:
            check_address_dir(html_path.parent)

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

    if errors:
        print(f"FAIL — {len(errors)} problem(s):")
        for e in errors:
            print(f"  - {e}")
        return 1
    print(f"OK — {len(html_pages)} page(s) pass the contract")
    return 0


if __name__ == "__main__":
    sys.exit(main())
