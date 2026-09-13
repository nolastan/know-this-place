#!/usr/bin/env python3
"""Regenerate stats/index.html — the dashboard of what this repository holds.

Stdlib only, and a derived index like the sitemap and the map index: every
number on the page is counted from the committed files, never carried over
from the last run and never estimated. Nothing here is authored, so nothing
here needs a source — the source is the repo.

**This script is the reason the dashboard costs nothing.** The stats an agent
would have to *work out* — how many pages have prose, how many findings a
corpus yielded — are exactly the stats that cost tokens to maintain, so none
of them are gathered by an agent. A workflow runs this file, the walk takes a
few seconds, and the page is current. Adding a stat means adding a counter
here, never asking an agent to count something.

**The page is stamped, not live.** Several of its numbers are ages in days,
and an age is only true on the day it was measured, so the page says which day
that was and everything on it is read against that date. That is also why
`validate.py` does not check this file the way it checks the sitemap: a
freshness dashboard goes out of date by the clock alone, and a build that
failed every morning until someone re-ran a script would teach everyone to
ignore it.

Run from anywhere:  python3 scripts/build_stats.py
                    python3 scripts/build_stats.py --print   (numbers only)
"""
import json
import re
import subprocess
from collections import Counter
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONFIG = json.loads((ROOT / "shared" / "site-config.json").read_text())
SITE = CONFIG["site_url"].rstrip("/")
REPO = CONFIG["repo_url"].rstrip("/")

ADDRESS_DIR = re.compile(r"^\d+[a-z]?$")  # 123, 123a — same as validate.py
OUT = ROOT / "stats" / "index.html"

MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
          "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
MONTHS_LONG = ["January", "February", "March", "April", "May", "June", "July",
               "August", "September", "October", "November", "December"]

# The window the refresh job treats a page's city data as stale after. Kept
# equal to the one in .github/workflows/refresh.yml on purpose: the tile
# counting stale pages is that job's backlog, so a different number here would
# report a queue nothing is working from.
REFRESH_DAYS = 30


def short_date(iso):
    if not iso:
        return ""
    return f"{MONTHS[int(iso[5:7]) - 1]} {int(iso[8:10])}"


def long_date(iso):
    if not iso:
        return ""
    return f"{MONTHS_LONG[int(iso[5:7]) - 1]} {int(iso[8:10])}, {iso[:4]}"


def days_since(iso, today):
    if not iso:
        return None
    try:
        return (today - date.fromisoformat(iso[:10])).days
    except ValueError:
        return None


def n(v):
    return f"{v:,}" if isinstance(v, int) else v


# ----------------------------------------------------------------- the walk

def read_json(path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def count_pages(today):
    """One pass over every address page. Everything the tree can answer is
    answered here, because opening 16,000 files twice is the only part of this
    script with a cost worth caring about."""
    content = ROOT / "san-francisco"
    s = Counter()
    neighborhoods, streets, source_ids = set(), set(), set()

    for data_path in content.rglob("data.json") if content.exists() else []:
        page_dir = data_path.parent
        if not ADDRESS_DIR.match(page_dir.name):
            continue
        data = read_json(data_path)
        if data is None:
            s["unreadable"] += 1
            continue
        s["pages"] += 1

        parts = page_dir.relative_to(content).parts
        if len(parts) >= 3:                    # neighborhood / street / number
            neighborhoods.add(parts[0])
            streets.add(parts[:2])

        s["permits"] += len(data.get("permits") or [])
        record = data.get("historical_record") or []
        s["records"] += len(record)

        # The `retrieved` date the refresh job reads is per-source; a page is
        # as fresh as its freshest city-data query, which is what that job
        # re-runs. Secondary sources (a 1907 newspaper) never go stale, so
        # taking the newest date on the page is the honest reading.
        newest = None
        for src in data.get("sources") or []:
            s["citations"] += 1
            if src.get("id"):
                source_ids.add(src["id"])
            got = src.get("retrieved")
            if got and (newest is None or got > newest):
                newest = got
        age = days_since(newest, today)
        if age is not None and age > REFRESH_DAYS:
            s["stale"] += 1

        if record:
            s["with_record"] += 1
        if data.get("historic_survey"):
            s["with_survey"] += 1
        if data.get("historic_district"):
            s["in_district"] += 1
        if data.get("narrative"):
            s["with_prose"] += 1
        if data.get("occupants"):
            s["with_occupant"] += 1
            s["listings"] += len(data["occupants"])
        if data.get("notable_residents"):
            s["with_resident"] += 1
        if data.get("public_art"):
            s["with_art"] += 1
        if data.get("public_open_space"):
            s["with_popos"] += 1
        if data.get("rendered") is False:
            s["opted_out"] += 1

    s["neighborhoods"] = len(neighborhoods)
    s["streets"] = len(streets)
    s["sources_cited"] = len(source_ids)
    districts = content / "historic-districts"
    s["districts"] = sum(1 for d in districts.iterdir()
                         if d.is_dir()) if districts.exists() else 0
    return s


def count_findings(base):
    """Findings files — research batches and news items share one schema, so
    they are counted the same way. `publish.status` is missing on the older
    research batches, and missing means the same thing pending does: nobody
    has ruled on it yet."""
    s = Counter()
    last_read = None
    for path in sorted(Path(base).rglob("*.json")) if Path(base).exists() else []:
        data = read_json(path)
        if not isinstance(data, dict) or "findings" not in data:
            continue
        s["files"] += 1
        read_on = data.get("read_on")
        if read_on and (last_read is None or read_on > last_read):
            last_read = read_on
        for finding in data["findings"]:
            s["findings"] += 1
            status = (finding.get("publish") or {}).get("status")
            s[status if status in ("published", "declined") else "awaiting"] += 1
            if (finding.get("resolution") or {}).get("status") == "resolved":
                s["resolved"] += 1
    s["last_read"] = last_read
    return s


def count_news():
    s = {}
    feeds = (read_json(ROOT / "news" / "feeds.json") or {}).get("feeds", [])
    s["feeds"] = len(feeds)
    s["feeds_open"] = sum(1 for f in feeds if f.get("access") == "open")

    cursors = (read_json(ROOT / "news" / "state" / "cursors.json") or {}).get("feeds", {})
    s["considered"] = sum(c.get("considered", 0) for c in cursors.values())
    s["queued"] = sum(c.get("queued", 0) for c in cursors.values())
    runs = [c.get("last_run") for c in cursors.values() if c.get("last_run")]
    s["last_run"] = max(runs) if runs else None
    # A backfill is a run of the same pipeline, but it is deliberately NOT what
    # the "last run" tile measures: the daily poll is the heartbeat, and a
    # backfill walked last night would otherwise hide a poll that has been dead
    # for a week. It gets its own row instead.
    windows = [w for c in cursors.values()
               for w in (c.get("backfill") or {}).get("windows", [])]
    s["backfill_windows"] = len(windows)
    s["backfill_last"] = max((w.get("run") for w in windows if w.get("run")),
                             default=None)
    queue = ROOT / "news" / "queue"
    s["queue_files"] = len(list(queue.glob("*.json"))) if queue.exists() else 0
    return s


def count_git(today):
    """Cheap because git has already counted it. Returns an empty dict rather
    than a wrong one when the checkout cannot answer — a shallow clone (the
    Actions default) knows nothing about the history before its own depth, and
    a plausible-looking undercount is worse than no tile at all."""
    def git(*args):
        try:
            out = subprocess.run(["git", "-C", str(ROOT), *args],
                                 capture_output=True, text=True, timeout=30)
        except (OSError, subprocess.SubprocessError):
            return None
        return out.stdout.strip() if out.returncode == 0 else None

    if git("rev-parse", "--is-shallow-repository") != "false":
        return {}
    commits = git("rev-list", "--count", "HEAD")
    if not commits:
        return {}
    first = git("log", "--reverse", "--format=%cs", "--max-parents=0")
    last = git("log", "-1", "--format=%cs")
    authors = git("shortlog", "-sn", "--all", "--no-merges")
    return {
        "commits": int(commits),
        "commits_30d": int(git("rev-list", "--count", "--since=30 days ago", "HEAD") or 0),
        "first_commit": (first or "").splitlines()[0] if first else None,
        "last_commit": last or None,
        "authors": len(authors.splitlines()) if authors else 0,
        "age_days": days_since((first or "").splitlines()[0] if first else None, today),
    }


def collect(today):
    stats = {
        "generated": today.isoformat(),
        "site": count_pages(today),
        "research": count_findings(ROOT / "research" / "findings"),
        "news_items": count_findings(ROOT / "news" / "items"),
        "news": count_news(),
        "git": count_git(today),
    }
    sources = ROOT / "research" / "sources"
    stats["research"]["dossiers"] = len(list(sources.glob("*.md"))) if sources.exists() else 0
    findings = ROOT / "research" / "findings"
    stats["research"]["corpora"] = sum(1 for d in findings.iterdir()
                                       if d.is_dir()) if findings.exists() else 0
    merchants = ROOT / "merchants"
    stats["merchants"] = sum(1 for d in merchants.iterdir()
                             if d.is_dir()) if merchants.exists() else 0
    backlog = ROOT / "scripts" / "render-backlog.txt"
    stats["backlog"] = len([ln for ln in backlog.read_text().splitlines()
                            if ln.strip() and not ln.lstrip().startswith("#")]
                           ) if backlog.exists() else 0
    return stats


# ----------------------------------------------------------------- the page

def tile(icon, value, unit, label):
    """One `.stat`. `value` of None prints an em dash — a number nothing could
    be counted for is left blank rather than guessed at as a zero."""
    val = n(value) if value is not None else "—"
    small = f"<small> {unit}</small>" if unit and value is not None else ""
    return (f'    <div class="stat"><span class="ic {icon}"></span>'
            f'<span class="stat-val">{val}{small}</span>'
            f'<span class="stat-label">{label}</span></div>')


def band(tiles):
    return '  <div class="stats">\n' + "\n".join(tiles) + "\n  </div>"


def spec(icon, key, value):
    return (f'          <div class="spec"><span class="ic {icon}"></span>'
            f'<span class="spec-k">{key}</span>'
            f'<span class="spec-v">{n(value) if value is not None else "—"}</span></div>')


def panel(title, rows, chart=""):
    return ('      <section class="panel">\n'
            f'        <h3>{title}</h3>\n{chart}'
            '        <dl class="speclist">\n' + "\n".join(rows) + "\n        </dl>\n"
            '      </section>')


def cols(main, aside):
    """The two-column region. `.cols > .aside` is the only one of the two that
    carries a grid gap, which is why the left column holds one block and the
    right column is where panels stack."""
    return ('  <div class="cols">\n'
            f'    <div class="main">\n{main}\n    </div>\n'
            f'    <aside class="aside">\n{aside}\n    </aside>\n'
            '  </div>')


def stack(label, a_name, a_val, b_name, b_val):
    """The two-category part-to-whole bar from shared/BLOCKS.md, with the
    legend carrying the numbers so the chart survives with no JS."""
    total = (a_val or 0) + (b_val or 0)
    pct = round(100 * (a_val or 0) / total) if total else 0
    return (
        "        <ktp-figure>\n"
        f'          <div class="stack" role="group" aria-label="{label}">\n'
        f'            <div class="stack-seg seg-cool" style="width:{pct}%" tabindex="0"\n'
        f'                 data-tip="{a_name} · {n(a_val)} · {pct}%"'
        f' aria-label="{a_name}, {n(a_val)}, {pct} percent"></div>\n'
        f'            <div class="stack-seg seg-warm" style="width:{100 - pct}%" tabindex="0"\n'
        f'                 data-tip="{b_name} · {n(b_val)} · {100 - pct}%"'
        f' aria-label="{b_name}, {n(b_val)}, {100 - pct} percent"></div>\n'
        "          </div>\n"
        '          <div class="legend">\n'
        f'            <span class="legend-item"><span class="swatch seg-cool"></span>'
        f'<span>{a_name}</span>&nbsp;<b>{n(a_val)}</b></span>\n'
        f'            <span class="legend-item"><span class="swatch seg-warm"></span>'
        f'<span>{b_name}</span>&nbsp;<b>{n(b_val)}</b></span>\n'
        "          </div>\n"
        "        </ktp-figure>\n")


def age_tile(icon, iso, label, today):
    """A "days since" tile. The date it was measured from rides in the label,
    because the number alone stops being true tomorrow."""
    age = days_since(iso, today)
    if age is None:
        # Nothing in the repo records one — a pipeline that has never run, or a
        # shallow clone that cannot see the history. Either way the honest tile
        # is a blank, not a zero.
        return tile(icon, None, "", f"{label} · not recorded")
    unit = "day" if age == 1 else "days"
    return tile(icon, age, unit, f"{label} · {short_date(iso)}")


def render(s):
    today = date.fromisoformat(s["generated"])
    site, news, items, research, git = (
        s["site"], s["news"], s["news_items"], s["research"], s["git"])

    head = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>The state of the site — Know This Place</title>
  <meta name="description" content="What Know This Place holds today: {n(site['pages'])} address pages, {n(site['citations'])} citations, and how recently each part of the pipeline ran. Counted from the repository, not estimated.">
  <link rel="canonical" href="{SITE}/stats/">
  <link rel="icon" href="/favicon.ico" sizes="32x32">
  <link rel="icon" href="/shared/icon.svg" type="image/svg+xml">
  <link rel="apple-touch-icon" href="/apple-touch-icon.png">
  <link rel="manifest" href="/shared/site.webmanifest">
  <link rel="stylesheet" href="/shared/site.css">
  <script type="module" src="/shared/site.js"></script>
</head>
<body>
<header class="site-header">
  <a class="wordmark" href="/">Know This Place</a>
  <nav class="breadcrumb" aria-label="Breadcrumb">
    <a href="/">Home</a>
    <span aria-current="page">The state of the site</span>
  </nav>
</header>

<main>
  <h1>The state of the site</h1>
  <p class="lead">Every number below was counted from the files in this
  repository on {long_date(s['generated'])}, and every age on it is measured
  against that date and no other. Nothing here is live, sampled or
  estimated.</p>
"""

    body = [
        band([
            tile("ic-home", site["pages"], "", "Address pages"),
            tile("ic-layers", site["neighborhoods"], "", "Neighborhoods"),
            tile("ic-pin", site["streets"], "", "Streets"),
            tile("ic-plan", site["districts"], "", "Historic districts"),
        ]),

        '\n  <div class="section-head"><span class="ic ic-clock"></span>'
        "<h2>Is anything still running?</h2></div>",
        band([
            age_tile("ic-calendar", news["last_run"], "Since last news run", today),
            age_tile("ic-permit", items["last_read"], "Since last news item", today),
            age_tile("ic-help", research["last_read"], "Since last research batch", today),
            age_tile("ic-clock", git.get("last_commit"), "Since last commit", today),
        ]),

        '\n  <div class="section-head"><span class="ic ic-permit"></span>'
        "<h2>The record</h2></div>",
        band([
            tile("ic-permit", site["permits"], "", "Permits documented"),
            tile("ic-calendar", site["records"], "", "Dated entries beyond permits"),
            tile("ic-link", site["citations"], "", "Citations"),
            tile("ic-layers", site["sources_cited"], "", "Distinct sources cited"),
        ]),
        "",
        cols(
            panel("What the pages carry", [
                spec("ic-calendar", "With a record beyond permits", site["with_record"]),
                spec("ic-plan", "With a survey record", site["with_survey"]),
                spec("ic-pin", "Inside a historic district", site["in_district"]),
                spec("ic-home", "With a current occupant", site["with_occupant"]),
                spec("ic-help", "With written narrative", site["with_prose"]),
                spec("ic-check", "Naming a past resident", site["with_resident"]),
                spec("ic-ruler", "With public art on the parcel", site["with_art"]),
                spec("ic-lot", "With public open space", site["with_popos"]),
            ]),
            panel("Pages due a refresh", [
                spec("ic-clock", f"City data older than {REFRESH_DAYS} days", site["stale"]),
                spec("ic-none", "Opted out of rendering", site["opted_out"]),
                spec("ic-eligible", "Awaiting the render sweep", s["backlog"]),
                spec("ic-help", "data.json that would not parse", site["unreadable"]),
            ]),
        ),

        '\n  <div class="section-head"><span class="ic ic-link"></span>'
        "<h2>The pipelines</h2></div>",
        cols(
            panel("News · feeds to timeline", [
                spec("ic-link", "Feeds registered", news["feeds"]),
                spec("ic-check", "Open to polling", news["feeds_open"]),
                spec("ic-calendar", "Stories screened", news["considered"]),
                spec("ic-permit", "Queued for reading", news["queued"]),
                spec("ic-plan", "Items recorded", items["findings"]),
                spec("ic-home", "Entries on a page", items["published"]),
                spec("ic-help", "Awaiting a decision", items["awaiting"]),
                spec("ic-layers", "Backfill windows walked", news["backfill_windows"]),
                spec("ic-clock", "Queue files unread", news["queue_files"]),
            ], chart=stack("What the ten-year test kept",
                           "Published", items["published"],
                           "Declined", items["declined"])),
            panel("Research · archives to pages", [
                spec("ic-layers", "Sources catalogued", research["dossiers"]),
                spec("ic-plan", "Corpora with findings", research["corpora"]),
                spec("ic-permit", "Findings recorded", research["findings"]),
                spec("ic-home", "Published onto a page", research["published"]),
                spec("ic-none", "Declined", research["declined"]),
                spec("ic-help", "Awaiting a decision", research["awaiting"]),
            ], chart=stack("Findings resolved to a parcel",
                           "Resolved to a parcel", research["resolved"],
                           "Unresolved", research["findings"] - research["resolved"]))
            + "\n"
            + panel("Merchants · who trades there now", [
                spec("ic-link", "Directories registered", s["merchants"]),
                spec("ic-home", "Buildings with a listing", site["with_occupant"]),
                spec("ic-permit", "Listings carried", site["listings"]),
            ]),
        ),

        '\n  <div class="section-head"><span class="ic ic-plan"></span>'
        "<h2>The repository</h2></div>",
        band([
            tile("ic-permit", git.get("commits"), "", "Commits"),
            tile("ic-calendar", git.get("commits_30d"), "", "Commits in 30 days"),
            tile("ic-home", git.get("authors"), "", "Contributors"),
            tile("ic-clock", git.get("age_days"), "days",
                 "Since the first commit" + (f" · {short_date(git['first_commit'])}"
                                             if git.get("first_commit") else "")),
        ]),
    ]

    foot = f"""
</main>

<footer class="site-footer">
  <p class="feedback-cta">This page is generated. Run
  <a href="{REPO}/blob/main/scripts/build_stats.py">scripts/build_stats.py</a>
  to rebuild it from the repository.</p>
  <p class="colophon">Part of <a href="/">Know This Place</a>, a community
  encyclopedia of the built environment. Facts are cited; pages are reviewed
  by people. <a href="{REPO}">Source</a>.</p>
</footer>
</body>
</html>
"""
    return head + "\n".join(body) + foot


def as_text(s):
    """The same numbers as plain lines, for a workflow summary or a PR body —
    so reporting the run never means an agent reading back the HTML."""
    out = [f"stats as of {s['generated']}"]
    for section in ("site", "news", "news_items", "research", "git"):
        out.append(f"[{section}]")
        for k, v in sorted(s[section].items()):
            out.append(f"  {k}: {v}")
    out.append(f"[repo]\n  merchants: {s['merchants']}\n  render_backlog: {s['backlog']}")
    return "\n".join(out)


def main(argv):
    stats = collect(date.today())
    if "--print" in argv:
        print(as_text(stats))
        return 0
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(render(stats), encoding="utf-8")
    site = stats["site"]
    print(f"stats/index.html: {site['pages']:,} pages, {site['citations']:,} citations, "
          f"{stats['news_items']['published']} news entries, "
          f"{stats['research']['published']:,} research findings published "
          f"(as of {stats['generated']})")
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main(sys.argv[1:]))
