#!/usr/bin/env python3
"""Consistency checks for the news module. Stdlib only.

    python3 news/tools/check.py            # check everything
    python3 news/tools/check.py --stats    # ...and print the yield so far

What it checks:
  * feeds.json is well formed — unique ids, a known kind, an access flag, and a
    link_pattern on every html feed;
  * every cursor belongs to a registered feed, and every queue file's items name
    one too;
  * every items file sits under a registered feed id and validates against
    research/schema/finding.schema.json — the news module writes findings files,
    so it is checked against the same schema, by the same validator;
  * the rules the schema can't state: a news finding cites a URL, and a
    published one names the page it went on.

The schema and the validator both come from the research module rather than
being restated here, so the two modules cannot drift apart.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent           # news/
REPO = ROOT.parent
RESEARCH = REPO / "research"

sys.path.insert(0, str(RESEARCH / "tools"))
from check import check_rules, validate  # noqa: E402  — the research validator

SCHEMA_PATH = RESEARCH / "schema" / "finding.schema.json"
KINDS = {"rss", "bluesky", "html"}
ACCESS = {"open", "needs-human", "blocked"}

errors: list[str] = []


def err(where, msg: str) -> None:
    errors.append(f"{where}: {msg}")


def check_feeds() -> dict[str, dict]:
    if not (ROOT / "feeds.json").exists():
        err("news/feeds.json", "the register is missing")
        return {}
    data = json.loads((ROOT / "feeds.json").read_text(encoding="utf-8"))
    feeds: dict[str, dict] = {}
    for feed in data.get("feeds", []):
        fid = feed.get("id")
        if not fid:
            err("news/feeds.json", "a feed has no id")
            continue
        if fid in feeds:
            err("news/feeds.json", f"duplicate feed id {fid!r}")
        for key in ("outlet", "url", "kind", "scope", "access"):
            if not feed.get(key):
                err("news/feeds.json", f"{fid}: missing {key!r}")
        if feed.get("kind") not in KINDS:
            err("news/feeds.json", f"{fid}: kind {feed.get('kind')!r} is not one of "
                                   f"{sorted(KINDS)}")
        if feed.get("kind") == "html" and not feed.get("link_pattern"):
            err("news/feeds.json", f"{fid}: an html feed needs a link_pattern")
        if feed.get("access") not in ACCESS:
            err("news/feeds.json", f"{fid}: access {feed.get('access')!r} is not one of "
                                   f"{sorted(ACCESS)}")
        if feed.get("scope") not in ("sf", "bay-area"):
            err("news/feeds.json", f"{fid}: scope must be 'sf' or 'bay-area'")
        if not feed.get("note"):
            err("news/feeds.json", f"{fid}: no note — every feed records what it is "
                                   f"and how it misbehaves")
        feeds[fid] = feed
    return feeds


def check_cursors(feeds: dict) -> None:
    path = ROOT / "state" / "cursors.json"
    if not path.exists():
        return                      # nothing polled yet is a valid state
    data = json.loads(path.read_text(encoding="utf-8"))
    for fid, cursor in (data.get("feeds") or {}).items():
        if fid not in feeds:
            err("news/state/cursors.json", f"cursor for unregistered feed {fid!r}")
        if cursor.get("url") and feeds.get(fid, {}).get("url") != cursor["url"]:
            err("news/state/cursors.json",
                f"{fid}: the cursor's url is not the one in feeds.json — the feed "
                f"moved, and the cursor's 'seen' ids may not mean what they did")


def check_queues(feeds: dict) -> None:
    for path in sorted((ROOT / "queue").glob("*.json")):
        rel = path.relative_to(REPO)
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            err(str(rel), f"invalid JSON — {exc}")
            continue
        for item in data.get("items", []) + data.get("skipped", []):
            if item.get("feed") not in feeds:
                err(str(rel), f"item from unregistered feed {item.get('feed')!r}")
                break
            if not item.get("url"):
                err(str(rel), f"an item has no url: {item.get('title', '')[:50]!r}")
                break


def check_items(feeds: dict, schema: dict) -> list[Path]:
    files = sorted((ROOT / "items").glob("*/*.json"))
    for path in files:
        rel = path.relative_to(REPO)
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            err(str(rel), f"invalid JSON — {exc}")
            continue

        validate(data, schema, schema, "$", lambda p, m: err(str(rel), f"{p}: {m}"))
        if not isinstance(data, dict):
            continue

        sid = data.get("source_id")
        if sid and sid not in feeds:
            err(str(rel), f"source_id {sid!r} is not a feed in news/feeds.json")
        if path.parent.name != sid:
            err(str(rel), f"directory {path.parent.name!r} does not match "
                          f"source_id {sid!r}")
        check_rules(rel, data)

        for f in data.get("findings", []):
            if not isinstance(f, dict):
                continue
            fid = f.get("id")
            citation = f.get("citation") or {}
            # The link is the whole attribution deal — a news finding without one
            # cannot be published, because the timeline entry has nothing to link.
            if not citation.get("url"):
                err(str(rel), f"{fid}: a news finding needs citation.url")
            if not citation.get("label"):
                err(str(rel), f"{fid}: a news finding needs citation.label")
            publish = f.get("publish") or {}
            if publish.get("status") == "published":
                if not (f.get("resolution") or {}).get("path"):
                    err(str(rel), f"{fid}: published but no resolution.path")
            # A decline is a judgement, and a judgement with no reason recorded is
            # indistinguishable from an oversight the next time anyone reads this.
            if publish.get("status") == "declined" and not publish.get("note"):
                err(str(rel), f"{fid}: declined findings must say why (publish.note)")
    return files


def stats(files: list[Path]) -> None:
    per: dict[str, dict] = {}
    for path in files:
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        s = per.setdefault(data.get("source_id", "?"), dict(
            batches=0, read=0, found=0, resolved=0, published=0))
        s["batches"] += 1
        s["read"] += (data.get("coverage") or {}).get("examined") or 0
        for f in data.get("findings", []):
            s["found"] += 1
            if (f.get("resolution") or {}).get("status") == "resolved":
                s["resolved"] += 1
            if (f.get("publish") or {}).get("status") == "published":
                s["published"] += 1

    cursors = {}
    path = ROOT / "state" / "cursors.json"
    if path.exists():
        cursors = json.loads(path.read_text(encoding="utf-8")).get("feeds", {})

    head = (f"{'feed':<22}{'considered':>11}{'queued':>8}{'read':>7}"
            f"{'found':>7}{'resolved':>10}{'published':>11}")
    print(head)
    print("-" * len(head))
    for fid in sorted(set(cursors) | set(per)):
        c, s = cursors.get(fid, {}), per.get(fid, {})
        print(f"{fid:<22}{c.get('considered', 0):>11}{c.get('queued', 0):>8}"
              f"{s.get('read', 0):>7}{s.get('found', 0):>7}"
              f"{s.get('resolved', 0):>10}{s.get('published', 0):>11}")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--stats", action="store_true", help="print the yield so far")
    args = ap.parse_args()

    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    feeds = check_feeds()
    check_cursors(feeds)
    check_queues(feeds)
    files = check_items(feeds, schema)

    if args.stats:
        stats(files)
        print()

    if errors:
        print(f"{len(errors)} problem(s):", file=sys.stderr)
        for e in errors:
            print(f"  {e}", file=sys.stderr)
        return 1
    open_feeds = sum(1 for f in feeds.values() if f.get("access") == "open")
    print(f"news: OK — {len(feeds)} feed(s) registered ({open_feeds} polled), "
          f"{len(files)} items file(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
