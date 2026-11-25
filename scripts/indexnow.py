#!/usr/bin/env python3
"""Tell search engines which pages a deploy changed, by IndexNow. Stdlib only.

IndexNow is one POST that Bing, Yandex, Seznam and Naver share: a list of URLs
that changed, and a key that proves the site sent it — a text file at the
site's root holding the key (`<key>.txt`, committed; the key is in
`shared/site-config.json`). They recrawl those URLs within hours instead of
waiting for the sitemap to come round.

"Changed" is measured against the last deploy, not against git: a page is
derived from many files, and one data.json edit can change its neighbors'
Nearby lists, its street hub and its district hub. So the staged site is
fingerprinted page by page and compared with the fingerprints the last deploy
left (deploy.yml keeps them in the Actions cache):

    python3 scripts/indexnow.py _site --previous prev.json --out next.json
    python3 scripts/indexnow.py _site --previous prev.json --out next.json --dry-run

The fingerprint is the page's `<head>` title and description and its `<body>`,
less the `?v=` cache-busters that every CSS or JS change rewrites on every
page — a stylesheet change is not news to a search engine. A page that is new,
changed, or gone since the last deploy is sent. With no previous fingerprints
(the first run, or an evicted cache) nothing is sent but the homepage: there
is nothing to compare against, and the sitemap already lists every page.

Never fails the deploy: an unreachable or refusing endpoint is reported, and
the pages it did not take keep their old fingerprints, so the next deploy
sends them again.
"""
import argparse
import hashlib
import json
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONFIG = json.loads((ROOT / "shared" / "site-config.json").read_text(encoding="utf-8"))
SITE = CONFIG["site_url"].rstrip("/")
KEY = CONFIG["indexnow_key"]
ENDPOINT = "https://api.indexnow.org/indexnow"
BATCH = 10_000  # the protocol's limit per request

CACHE_BUSTER = re.compile(r"\?v=[0-9A-Za-z_-]+")
TITLE = re.compile(r"<title>.*?</title>", re.S)
DESC = re.compile(r'<meta name="description"[^>]*>')
BODY = re.compile(r"<body\b.*</body>", re.S)


def fingerprint(text: str) -> str | None:
    """A short hash of what a reader and a crawler see, or None for a page
    that is not one (a redirect stub, a noindex page)."""
    if 'name="robots" content="noindex' in text:
        return None
    parts = [m.group(0) for rx in (TITLE, DESC, BODY) for m in [rx.search(text)] if m]
    if not parts:
        return None
    return hashlib.sha1(CACHE_BUSTER.sub("", "\n".join(parts)).encode()).hexdigest()[:12]


def fingerprints(site: Path) -> dict:
    out = {}
    for f in sorted(site.rglob("index.html")):
        fp = fingerprint(f.read_text(encoding="utf-8", errors="replace"))
        if fp:
            rel = f.parent.relative_to(site).as_posix()
            out["/" if rel == "." else f"/{rel}/"] = fp
    return out


def changed(prev: dict, now: dict) -> list:
    return sorted({p for p, h in now.items() if prev.get(p) != h} | (prev.keys() - now.keys()))


def submit(urls: list) -> bool:
    host = SITE.split("://", 1)[1]
    ok = True
    for i in range(0, len(urls), BATCH):
        body = json.dumps({"host": host, "key": KEY, "keyLocation": f"{SITE}/{KEY}.txt",
                           "urlList": urls[i:i + BATCH]}).encode()
        req = urllib.request.Request(ENDPOINT, data=body, method="POST",
                                     headers={"Content-Type": "application/json; charset=utf-8"})
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                print(f"    IndexNow: {r.status} for {len(urls[i:i + BATCH])} URL(s)")
        except urllib.error.HTTPError as e:
            # 202 is "received, key not yet checked" and arrives as success;
            # 403 is a key the endpoint can't fetch, 422 a URL off the host.
            print(f"    IndexNow: HTTP {e.code} {e.reason}: {e.read()[:200]!r}", file=sys.stderr)
            ok = False
        except (urllib.error.URLError, TimeoutError) as e:
            print(f"    IndexNow: unreachable ({e})", file=sys.stderr)
            ok = False
    return ok


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    ap.add_argument("site", type=Path, help="the staged site (_site)")
    ap.add_argument("--previous", type=Path, help="the last deploy's fingerprints")
    ap.add_argument("--out", type=Path, required=True, help="where to write this deploy's")
    ap.add_argument("--dry-run", action="store_true", help="list the URLs, send nothing")
    args = ap.parse_args()

    if not (args.site / f"{KEY}.txt").is_file():
        raise SystemExit(f"indexnow: {args.site}/{KEY}.txt is missing; the endpoint "
                         "would refuse every submission")
    now = fingerprints(args.site)
    prev = None
    if args.previous and args.previous.is_file():
        try:
            prev = json.loads(args.previous.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            prev = None
    paths = changed(prev, now) if prev is not None else ["/"]
    urls = [SITE + p for p in paths]
    print(f"==> IndexNow: {len(now):,} pages fingerprinted, "
          + (f"{len(urls):,} changed since the last deploy" if prev is not None
             else "no previous fingerprints, sending the homepage only"))
    for u in urls[:20]:
        print(f"    {u}")
    if len(urls) > 20:
        print(f"    … and {len(urls) - 20:,} more")
    if urls and not args.dry_run and not submit(urls) and prev is not None:
        # Unsent: record those pages as the last deploy had them, so the next
        # run sees them as changed and sends them again.
        for p in paths:
            if p in prev:
                now[p] = prev[p]
            else:
                now.pop(p, None)
    args.out.write_text(json.dumps(now, separators=(",", ":"), sort_keys=True), encoding="utf-8")


if __name__ == "__main__":
    main()
