#!/usr/bin/env python3
"""Read queued articles and report the addresses in them.

    python3 news/tools/read.py news/queue/2026-08-16.json   # every queued item
    python3 news/tools/read.py https://example.com/story    # one article
    python3 news/tools/read.py <queue> --only-pages         # narrow a backlog

Stdlib only. This is the mechanical half of the reading stage: it fetches the
article, strips it to text, finds every street address in it, and says which of
them the site already has a page for. What it prints is **evidence for a
reader**, not copy for a page — the sentence around a hit is there so the next
step can judge what the story actually says about the building, in our own
words. See [../AGENTS.md](../AGENTS.md) → "Reading an article".

Whether a page exists is reported, not ranked on: an address with no page is a
page the publishing stage seeds. `--only-pages` is for narrowing a backlog by
hand, and it is not how a pass is meant to be worked.

It does not decide anything: an address in an article is not yet a fact about a
building, and the module's evidence bar is met by a person reading the story.
"""
from __future__ import annotations

import argparse
import html as html_mod
import json
import re
import sys
import time
import urllib.parse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from poll import (NUMBERED_ADDRESS, bare_addresses, clean_url, fetch,  # noqa: E402
                  fetch_landed, looks_like_transit, page_index, parse_rss,
                  plausible_street, street_vocabulary)

ROOT = Path(__file__).resolve().parent.parent
REPO = ROOT.parent

# Everything between these tags is furniture: navigation, related-story rails,
# newsletter pitches. Their addresses belong to other stories.
STRIP = re.compile(r"<(script|style|nav|aside|footer|header|form)\b.*?</\1>",
                   re.S | re.I)
TAG = re.compile(r"<[^>]+>")
SPACE = re.compile(r"[ \t\r\f\v]+")

# What the article calls itself. A feed's own title is not always the headline:
# the sf-chronicle feed is a Bluesky account, so its title is the social post's
# teaser sentence and its link is a bit.ly shortlink. The headline is the only
# text of an outlet's that reaches a page and the URL is the citation, so both
# have to come from the article rather than from the post about it. og:title is
# the display headline on every outlet measured here, agreeing with the page's
# own h1; the JSON-LD "headline" is often a different, search-tuned string, so
# it is not consulted.
META = re.compile(r"<meta\b[^>]*>", re.I)
ATTR = re.compile(r"""(\w[\w:.-]*)\s*=\s*["']([^"']*)["']""")
CANONICAL = re.compile(r"""<link\b[^>]*rel=["']canonical["'][^>]*>""", re.I)


def to_text(body: bytes) -> str:
    html = body.decode("utf-8", "replace")
    html = STRIP.sub(" ", html)
    html = re.sub(r"<(p|div|br|li|h[1-6])\b[^>]*>", "\n", html, flags=re.I)
    text = TAG.sub(" ", html)
    for entity, char in (("&nbsp;", " "), ("&amp;", "&"), ("&quot;", '"'),
                         ("&#8217;", "'"), ("&#039;", "'"), ("&rsquo;", "'"),
                         ("&ldquo;", '"'), ("&rdquo;", '"'), ("&#8216;", "'")):
            text = text.replace(entity, char)
    return "\n".join(SPACE.sub(" ", line).strip() for line in text.split("\n"))


def unescape(raw: str) -> str:
    return html_mod.unescape(raw).strip()


def self_description(body: bytes) -> tuple[str, str]:
    """(the article's own headline, its own URL) — either may be "".

    Read from the document's metadata rather than its body: a page's <title> is
    written for search results and its <h1> may be any of a dozen newsletter
    promos, but og:title is the headline the outlet displays.
    """
    page = body.decode("utf-8", "replace")[:400_000]
    headline = url = ""
    for tag in META.finditer(page):
        attrs = {k.lower(): v for k, v in ATTR.findall(tag.group(0))}
        key = (attrs.get("property") or attrs.get("name") or "").lower()
        if not headline and key in ("og:title", "twitter:title"):
            headline = unescape(attrs.get("content", ""))
        if not url and key == "og:url":
            url = unescape(attrs.get("content", ""))
    if not url:
        link = CANONICAL.search(page)
        if link:
            url = unescape(dict(ATTR.findall(link.group(0))).get("href", ""))
    return headline, url


def sentence_around(text: str, start: int, end: int, span: int = 220) -> str:
    """The shortest span that shows what the story says about the address."""
    left = max(0, start - span)
    right = min(len(text), end + span)
    chunk = " ".join(text[left:right].split())
    return ("…" if left else "") + chunk + ("…" if right < len(text) else "")


def untyped_index(pages: dict[str, str]) -> dict[str, str]:
    """The page index keyed the way a headline writes an address: '400 divisadero'."""
    out = {}
    for addr, path in pages.items():
        m = re.match(r"^(\d+[a-z]?)\s+(.*?)\s+(street|avenue|boulevard|road|way|place|"
                     r"drive|terrace|lane|alley|court|plaza|row|steps|stairway|circle|"
                     r"park|path|walk)$", addr)
        if m:
            out.setdefault(f"{m.group(1)} {m.group(2)}", path)
    return out


def addresses_in(text: str, streets: set[str], pages: dict) -> list[dict]:
    """Every street address in the article, with the page it belongs to."""
    out, seen = [], set()
    bare_pages = untyped_index(pages)

    for number, name, m in bare_addresses(text, streets):
        key = f"{number} {name}".lower()
        if key in seen:
            continue
        seen.add(key)
        out.append({
            "as_written": f"{number} {name}",
            "street": name,
            "on_a_site_street": True,
            "page": bare_pages.get(key),
            "at": round(100 * m.start() / max(1, len(text))),
            "evidence": sentence_around(text, m.start(), m.end()),
        })

    for m in NUMBERED_ADDRESS.finditer(text):
        if not plausible_street(m.group(2)):
            continue
        if looks_like_transit(text, m.start(), m.end()):
            continue
        written = " ".join(m.group(0).split())
        key = written.lower()
        # Spell the street type out the way the site's index holds it.
        for short, long in (("st.", "street"), (" st", " street"), ("ave.", "avenue"),
                            (" ave", " avenue"), ("blvd.", "boulevard"),
                            (" blvd", " boulevard"), ("rd.", "road"), (" rd", " road"),
                            ("dr.", "drive"), (" dr", " drive"), ("ln.", "lane"),
                            (" ln", " lane"), ("pl.", "place"), (" pl", " place"),
                            ("ct.", "court"), (" ct", " court")):
            if key.endswith(short):
                key = key[:-len(short)] + long.strip()
                break
        bare = " ".join(key.split()[:-1])
        if key in seen or bare in seen:
            # The same address, once with its street type and once without.
            for row in out:
                if row["as_written"].lower() == bare and not row["page"]:
                    row.update(as_written=written, page=pages.get(key))
            continue
        seen.add(key)
        out.append({
            "as_written": written,
            "street": m.group(2),
            "on_a_site_street": m.group(2).lower() in streets,
            "page": pages.get(key),
            "at": round(100 * m.start() / max(1, len(text))),
            "evidence": sentence_around(text, m.start(), m.end()),
        })
    return out


def register() -> dict[str, dict]:
    return {f["id"]: f for f in
            json.loads((ROOT / "feeds.json").read_text(encoding="utf-8"))["feeds"]}


def feed_for(url: str) -> str:
    """Which registered feed a bare URL belongs to — so the fallback can work."""
    host = urllib.parse.urlsplit(url).netloc.removeprefix("www.")
    for fid, feed in register().items():
        if urllib.parse.urlsplit(feed["url"]).netloc.removeprefix("www.").endswith(host):
            return fid
    return ""


_FEED_TEXT: dict[str, dict[str, str]] = {}


def syndicated(feed_id: str) -> dict[str, str]:
    """Article text the feed itself carries, by URL. Held in memory only.

    Hoodline's article pages answer a fetcher with 403 while its feed syndicates
    the whole story, and Whatnow and SFist syndicate most of one. Reading the
    feed is then both the only way in and the more polite one. None of this text
    is written anywhere: research/AGENTS.md keeps source text out of the repo.
    """
    if feed_id in _FEED_TEXT:
        return _FEED_TEXT[feed_id]
    feed = register().get(feed_id)
    out: dict[str, str] = {}
    if feed and feed.get("kind") == "rss":
        try:
            for item in parse_rss(fetch(feed["url"])):
                if item.get("body"):
                    out[item["url"]] = item["body"]
        except Exception:  # noqa: BLE001 — the fallback failing is not fatal
            pass
    _FEED_TEXT[feed_id] = out
    return out


def article_text(url: str, feed: str) -> tuple[str, str, str, str]:
    """(text, how it was got, the article's own headline, its own URL).

    The page first; the feed's own copy if it refuses. The last two are empty
    when the page could not be read at all — an outlet that answers 403 tells us
    nothing about itself, and the feed's title is all there is.
    """
    try:
        body, landed = fetch_landed(url, tries=2)
        headline, canonical = self_description(body)
        canonical = canonical or clean_url(landed)
        text = to_text(body)
        if len(text) > 400:
            return text, "page", headline, canonical
    except Exception as exc:  # noqa: BLE001 — a refusal is a result, not a crash
        fallback = syndicated(feed).get(url)
        if fallback:
            return fallback, "feed", "", ""
        return "", f"FAILED: {exc}", "", ""
    return (syndicated(feed).get(url, text),
            "feed" if syndicated(feed).get(url) else "page", headline, canonical)


def same_text(a: str, b: str) -> bool:
    """Two strings that differ only in typography are the same headline."""
    squash = str.maketrans({"\u2018": "'", "\u2019": "'", "\u201c": '"',
                            "\u201d": '"', "\u2013": "-", "\u2014": "-"})
    return (" ".join(a.translate(squash).lower().split())
            == " ".join(b.translate(squash).lower().split()))


def report(url: str, title: str, feed: str, streets: set[str], pages: dict,
           only_pages: bool) -> tuple[int, int]:
    """(addresses found, of which already have a page)."""
    text, how, headline, canonical = article_text(url, feed)
    if not text:
        print(f"\n[{feed}] {title}\n  {url}\n  {how}")
        return 0, 0
    hits = addresses_in(text, streets, pages)
    with_pages = [h for h in hits if h["page"]]
    if only_pages and not with_pages:
        return 0, 0
    print(f"\n[{feed}] {title}")
    print(f"  {url}")
    # Printed only when the feed got it wrong, so a run over well-behaved feeds
    # looks exactly as it did before. When it does print, these two lines are
    # what the citation must be built from — see ../AGENTS.md, "Reading an
    # article": the headline is published verbatim and the link is the
    # attribution, so neither may come from a social post about the story.
    if headline and not (title and same_text(headline, title)):
        print(f"  headline: {headline}")
    if canonical and canonical != url:
        print(f"  article:  {canonical}")
    if not hits:
        print("  no street address in the article text")
        return 0, 0
    for h in hits:
        where = h["page"] or ("(no page; on a street the site covers)"
                              if h["on_a_site_street"] else "(no page)")
        print(f"  • {h['as_written']:<28} {where}   @{h['at']}% in")
        print(f"      {h['evidence'][:200]}")
    return len(hits), len(with_pages)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("target", help="a queue file, or one article URL")
    ap.add_argument("--only-pages", action="store_true",
                    help="narrow a long backlog to articles naming an address that "
                         "already has a page; not the default, and not a ranking")
    ap.add_argument("--feed", action="append", default=[], help="only this feed id")
    ap.add_argument("--limit", type=int, default=0, help="stop after N articles")
    ap.add_argument("--skipped", action="store_true",
                    help="read what the screen threw away instead — the audit that "
                         "measures what a run of skips actually cost")
    args = ap.parse_args()

    pages = page_index()
    streets = {s.lower() for s in street_vocabulary(pages)}

    if args.target.startswith("http"):
        report(args.target, "", feed_for(args.target), streets, pages, False)
        return 0

    queue = json.loads(Path(args.target).read_text(encoding="utf-8"))
    items = [i for i in queue.get("skipped" if args.skipped else "items", [])
             if not args.feed or i["feed"] in args.feed]
    if args.limit:
        items = items[:args.limit]
    found, landed = 0, 0
    for i, item in enumerate(items, 1):
        n, on_pages = report(item["url"], item["title"], item["feed"], streets, pages,
                             args.only_pages)
        found += n
        landed += on_pages
        if i < len(items):
            time.sleep(1)  # be a polite client
    # Both halves are work: the ones with pages are edits, the rest are parcels
    # to seed. AGENTS.md → "No page yet? Seed it".
    print(f"\n{len(items)} article(s) read; {found} address hit(s), "
          f"{landed} on a page that already exists.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
