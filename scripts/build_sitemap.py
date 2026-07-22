#!/usr/bin/env python3
"""Regenerate sitemap.xml from the content tree. Stdlib only.

Run from anywhere: python3 scripts/build_sitemap.py
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = json.loads((ROOT / "shared" / "site-config.json").read_text())["site_url"].rstrip("/")


def main() -> None:
    urls = ["/"] if (ROOT / "index.html").exists() else []
    content = ROOT / "san-francisco"
    if content.exists():
        for page in sorted(content.rglob("index.html")):
            urls.append("/" + page.parent.relative_to(ROOT).as_posix() + "/")

    lines = ['<?xml version="1.0" encoding="UTF-8"?>',
             '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for url in urls:
        lines.append(f"  <url><loc>{SITE}{url}</loc></url>")
    lines.append("</urlset>")

    (ROOT / "sitemap.xml").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"sitemap.xml written with {len(urls)} URL(s)")


if __name__ == "__main__":
    main()
