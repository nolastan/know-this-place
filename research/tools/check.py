#!/usr/bin/env python3
"""Consistency checks for the research module. Stdlib only.

    python3 research/tools/check.py            # check everything
    python3 research/tools/check.py --stats    # ...and print the yield so far
    python3 research/tools/check.py --report <findings-file>   # the PR body's table
    python3 research/tools/check.py --overlap <findings-file>  # facts the pages already carry

What it checks:
  * every dossier in research/sources/ has a row in research/SOURCES.md, and
    every registered id has a dossier;
  * every findings file sits under a registered source id and validates against
    research/schema/finding.schema.json;
  * the cross-field rules the schema can't express (a resolved finding needs a
    parcel and a method; a published one needs to be resolved first);
  * the publish loop: once anything in a file is published, every resolved
    finding in it must carry a publish decision. PR #114 published 425 findings
    and marked none of them, and nobody could then tell finished work from
    unstarted work without re-checking all 425 against the pages.

--stats is the module's dashboard. Its `open` column counts resolved findings
with no publish decision — work already paid for and not yet on a page.

--report prints one batch broken down by neighborhood directory, in the Markdown
a run's PR body carries (RUNBOOK.md, "Close the books"). Only findings that
reached a parcel appear in it, because the parcel is what carries a
neighborhood; the unresolved and rejected ones are counted underneath it.

--overlap answers the question step 4 has to ask before it writes anything:
does the page already say this? Two statements routinely cover the same
buildings, so a citywide batch lands on parcels a neighbouring survey has
already documented. The LGBTQ citywide run found 16 of 307 resolved findings
restating what the page already carried, word for word in places — caught by
hand at audit time, after they had been written and rendered. Run it between
`resolve_eas.py apply` and publishing: it reports each resolved finding whose
wording substantially repeats an existing historical_record entry, hook or
narrative on its target page, so the decision to decline or trim is made before
the fact reaches the page rather than after.

The schema file is the single source of truth for shape — this script reads it
rather than restating it, so the two can't drift. It implements the subset of
JSON Schema the schema file actually uses: type, required, properties,
additionalProperties, items, enum, pattern, and local $ref.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent          # research/
REGISTER = ROOT / "SOURCES.md"
SCHEMA_PATH = ROOT / "schema" / "finding.schema.json"
EXAMPLE = ROOT / "schema" / "example-findings.json"

errors: list[str] = []


def err(where, msg: str) -> None:
    errors.append(f"{where}: {msg}")


# --------------------------------------------------------------------------- #
# A very small JSON Schema subset validator.
# --------------------------------------------------------------------------- #

TYPES = {
    "object": dict,
    "array": list,
    "string": str,
    "integer": int,
    "number": (int, float),
    "boolean": bool,
}


def validate(node, schema: dict, root: dict, path: str, report) -> None:
    if "$ref" in schema:
        ref = schema["$ref"]
        if not ref.startswith("#/"):
            report(path, f"unsupported $ref {ref!r}")
            return
        target = root
        for part in ref[2:].split("/"):
            target = target[part]
        validate(node, target, root, path, report)
        return

    if "enum" in schema and node not in schema["enum"]:
        report(path, f"{node!r} is not one of {schema['enum']}")
        return

    expected = schema.get("type")
    if expected:
        py = TYPES[expected]
        # bool is an int in Python; keep them distinct here.
        if isinstance(node, bool) != (expected == "boolean") or not isinstance(node, py):
            report(path, f"expected {expected}, got {type(node).__name__}")
            return

    if isinstance(node, str) and "pattern" in schema:
        if not re.match(schema["pattern"], node):
            report(path, f"{node!r} does not match {schema['pattern']}")

    if isinstance(node, dict):
        for key in schema.get("required", []):
            if key not in node:
                report(path, f"missing required key {key!r}")
        props = schema.get("properties", {})
        for key, value in node.items():
            if key in props:
                validate(value, props[key], root, f"{path}.{key}", report)
            elif schema.get("additionalProperties") is False:
                report(path, f"unexpected key {key!r}")

    if isinstance(node, list) and "items" in schema:
        for i, item in enumerate(node):
            validate(item, schema["items"], root, f"{path}[{i}]", report)


# --------------------------------------------------------------------------- #
# Register <-> dossiers
# --------------------------------------------------------------------------- #

ROW_ID = re.compile(r"^\|\s*\[`([a-z0-9-]+)`\]\(sources/([a-z0-9-]+)\.md\)\s*\|")


def registered_ids() -> set[str]:
    ids: set[str] = set()
    if not REGISTER.exists():
        err("research/SOURCES.md", "the register is missing")
        return ids
    for line in REGISTER.read_text(encoding="utf-8").splitlines():
        m = ROW_ID.match(line.strip())
        if not m:
            continue
        sid, link = m.groups()
        if sid != link:
            err("research/SOURCES.md", f"row `{sid}` links to sources/{link}.md")
        ids.add(sid)
    return ids


def check_register(ids: set[str]) -> None:
    on_disk = {p.stem for p in (ROOT / "sources").glob("*.md") if p.stem != "README"}
    for sid in sorted(on_disk - ids):
        err(f"research/sources/{sid}.md", "dossier has no row in SOURCES.md")
    for sid in sorted(ids - on_disk):
        err("research/SOURCES.md", f"`{sid}` is registered but has no dossier")
    for sid in sorted(on_disk & ids):
        text = (ROOT / "sources" / f"{sid}.md").read_text(encoding="utf-8")
        if not text.startswith(f"# {sid} "):
            err(f"research/sources/{sid}.md", f"first heading should start '# {sid} —'")
        if "**Verified:**" not in text and "**Verified:" not in text:
            err(f"research/sources/{sid}.md", "no Verified: line — every dossier records its last pass")


# --------------------------------------------------------------------------- #
# Findings
# --------------------------------------------------------------------------- #

def findings_files() -> list[Path]:
    return sorted((ROOT / "findings").glob("*/*.json"))


def check_findings_file(path: Path, schema: dict, ids: set[str]) -> dict | None:
    rel = path.relative_to(ROOT.parent)
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        err(str(rel), f"invalid JSON — {exc}")
        return None

    validate(data, schema, schema, "$", lambda p, m: err(str(rel), f"{p}: {m}"))

    if isinstance(data, dict):
        sid = data.get("source_id")
        if sid and ids and sid not in ids:
            err(str(rel), f"source_id {sid!r} is not registered in SOURCES.md")
        if path.parent.name != sid:
            err(str(rel), f"directory {path.parent.name!r} does not match source_id {sid!r}")
        check_rules(rel, data)
    return data if isinstance(data, dict) else None


def check_rules(rel: Path, data: dict) -> None:
    """Cross-field rules the schema can't state."""
    seen: set[str] = set()
    any_published = False
    unmarked: list[str] = []
    for f in data.get("findings", []):
        if not isinstance(f, dict):
            continue
        fid = f.get("id")
        if fid in seen:
            err(str(rel), f"duplicate finding id {fid!r}")
        seen.add(fid)

        res = f.get("resolution", {}) if isinstance(f.get("resolution"), dict) else {}
        status = res.get("status")
        pub = f.get("publish", {}) if isinstance(f.get("publish"), dict) else {}
        pub_status = pub.get("status", "pending")

        if status == "resolved":
            if not pub.get("status"):
                unmarked.append(str(fid))
            for key in ("apn", "path", "method"):
                if not res.get(key):
                    err(str(rel), f"{fid}: resolved findings need resolution.{key}")
            # The resolver files a page on the analysis neighborhood the
            # assessor and EAS give the parcel, and that vocabulary is not this
            # site's — "Twin Peaks" is a real analysis neighborhood and not one
            # of the directories under san-francisco/. Caught here it costs a
            # line; caught after `seed_pages.py seed-list` it is a directory
            # full of pages in a place the site does not use.
            area = (res.get("path") or "").strip("/").split("/")
            if len(area) >= 2 and not (ROOT.parent / area[0] / area[1]).is_dir():
                err(str(rel), f"{fid}: resolution.path names {area[0]}/{area[1]}/, "
                              f"which is not a directory this site has")
        elif status in ("unresolved", "rejected") and not res.get("note") and not res.get("method"):
            err(str(rel), f"{fid}: {status} findings must say why (resolution.note or .method)")

        if pub_status == "published":
            any_published = True
            if status != "resolved":
                err(str(rel), f"{fid}: published but resolution.status is {status!r}")
            if not pub.get("pr"):
                err(str(rel), f"{fid}: published findings need publish.pr")

    # The publish loop. A file with published entries has been through a
    # publishing run, so every resolved entry in it owes a decision — published
    # with its PR, or declined with a reason. Silence here is indistinguishable
    # from "not done yet", and telling the two apart costs a full re-check.
    if any_published and unmarked:
        shown = ", ".join(unmarked[:5]) + (" ..." if len(unmarked) > 5 else "")
        err(str(rel), f"{len(unmarked)} resolved finding(s) carry no publish "
                      f"decision in a file that has published entries — mark "
                      f"each published (with its PR) or declined (with a "
                      f"reason) in the same commit that edits the pages: {shown}")


# --------------------------------------------------------------------------- #

def stats(files: list[Path]) -> None:
    per: dict[str, dict] = {}
    for path in files:
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        s = per.setdefault(data.get("source_id", "?"), dict(
            batches=0, examined=0, found=0, resolved=0, unresolved=0,
            rejected=0, published=0, declined=0, open=0))
        s["batches"] += 1
        s["examined"] += (data.get("coverage") or {}).get("examined") or 0
        for f in data.get("findings", []):
            s["found"] += 1
            st = (f.get("resolution") or {}).get("status", "unresolved")
            s[st if st in s else "unresolved"] += 1
            pub = (f.get("publish") or {}).get("status")
            if pub == "published":
                s["published"] += 1
            elif pub == "declined":
                s["declined"] += 1
            elif st == "resolved":
                s["open"] += 1

    if not per:
        print("No findings files yet. research/findings/README.md says how to add one.")
        return
    head = (f"{'source':<30}{'batches':>8}{'read':>10}{'found':>8}"
            f"{'resolved':>10}{'published':>10}{'open':>7}")
    print(head)
    print("-" * len(head))
    for sid, s in sorted(per.items()):
        print(f"{sid:<30}{s['batches']:>8}{s['examined']:>10}{s['found']:>8}"
              f"{s['resolved']:>10}{s['published']:>10}{s['open']:>7}")

    still_open = sum(s["open"] for s in per.values())
    print()
    if still_open:
        print(f"{still_open} resolved finding(s) are not on a page and not declined.")
        print("That is the module's to-do list — a publishing run, per "
              "research/RUNBOOK.md.")
    else:
        print("No open publish loops: every resolved finding is published or "
              "declined.")


def report(path: Path) -> None:
    """One batch by neighborhood directory, in the PR body's Markdown.

    A neighborhood is a property of the *parcel*, so only findings that reached
    one can be grouped at all. Unresolved and rejected findings have no parcel
    and therefore no row — they are counted below the table instead, which is
    the honest shape rather than a "unknown" bucket that invites guessing.

    Pages created versus edited is read from git: a page this batch created is
    one whose data.json was added by a commit that also touched this findings
    file — which is the batch's own commits, since a run marks its findings in
    the same commit that edits the pages. Uncommitted pages count as created,
    so the table is right when run before the commit as well as after.
    """
    import collections
    import subprocess

    data = json.loads(path.read_text(encoding="utf-8"))
    site = ROOT.parent / "san-francisco"

    created = collections.Counter(); edited = collections.Counter()
    facts = collections.Counter(); declined = collections.Counter()
    conflicts = collections.Counter(); dates = collections.Counter()
    pages: dict[str, str] = {}
    unplaced = collections.Counter()

    for f in data.get("findings", []):
        res = f.get("resolution") or {}
        pub = (f.get("publish") or {}).get("status")
        if res.get("status") != "resolved" or not res.get("path"):
            unplaced[res.get("status", "unresolved")] += 1
            continue
        area = res["path"].split("/")[2]
        if pub == "declined":
            declined[area] += 1
        elif pub == "published":
            facts[area] += 1
            pages.setdefault(res["path"], area)

    batch_commits = set(subprocess.run(
        ["git", "log", "--format=%H", "--", str(path)],
        cwd=ROOT.parent, capture_output=True, text=True).stdout.split())
    for page_path, area in pages.items():
        rel = page_path.strip("/") + "/data.json"
        added = subprocess.run(
            ["git", "log", "--diff-filter=A", "--format=%H", "--", rel],
            cwd=ROOT.parent, capture_output=True, text=True).stdout.split()
        # Not committed yet, or added by one of this batch's own commits.
        (created if not added or added[-1] in batch_commits else edited)[area] += 1
        try:
            page = json.loads((ROOT.parent / rel).read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        conflicts[area] += len(page.get("unknowns") or [])
        if ((page.get("building") or {}).get("completed_conflict")):
            dates[area] += 1

    areas = sorted(set(created) | set(edited) | set(facts) | set(declined),
                   key=lambda a: (-(created[a] + edited[a]), a))
    cols = ("Pages created", "Pages edited", "Facts published",
            "Conflicts stated", "Dates disputed", "Resolved, no page")
    print(f"| Neighborhood | {' | '.join(cols)} |")
    print("|---" + "|---:" * len(cols) + "|")
    counters = (created, edited, facts, conflicts, dates, declined)
    for a in areas:
        cells = " | ".join(str(c[a]) if c[a] else ("0" if c is not declined else "—")
                           for c in counters)
        print(f"| `{a}` | {cells} |")
    totals = " | ".join(f"**{sum(c.values())}**" for c in counters)
    print(f"| **Total** | {totals} |")

    if unplaced:
        rest = ", ".join(f"{n} {s}" for s, n in sorted(unplaced.items()))
        print()
        print(f"{sum(unplaced.values())} finding(s) never reached a parcel ({rest}) "
              f"and cannot be grouped by neighborhood.")



STOPWORDS = set("""about after also been before being between both came could described
during each first from have here into more most much only other over said same
some such than that their them then there these they this those through under
until were what when where which while with would""".split())


def _words(text: str) -> set[str]:
    """Content words of a passage, for comparing what two sentences say."""
    return {w for w in re.findall(r"[a-z']{4,}", text.lower())} - STOPWORDS


def overlap(path: Path) -> None:
    """Report resolved findings whose wording the target page already carries.

    Compares each finding against the page's other historical_record entries
    (its own source excluded) plus any hook and narrative prose. The threshold
    is deliberately low: this prints candidates for a human decision, and a
    false positive costs one glance while a miss costs a duplicated fact.
    """
    repo = ROOT.parent
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        err(str(path), f"--overlap could not read the file: {exc}")
        return

    source_id = data.get("source_id", "")
    hits, checked, missing = [], 0, 0
    for finding in data.get("findings", []):
        res = finding.get("resolution") or {}
        if res.get("status") != "resolved" or not res.get("path"):
            continue
        # A finding already declined has had this decision made about it.
        if (finding.get("publish") or {}).get("status") == "declined":
            continue
        page = repo / res["path"].strip("/") / "data.json"
        if not page.exists():
            missing += 1
            continue
        try:
            doc = json.loads(page.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            missing += 1
            continue
        checked += 1
        mine = _words(finding.get("description", ""))
        if not mine:
            continue
        theirs: set[str] = set()
        for entry in doc.get("historical_record", []):
            # An entry this batch wrote is not evidence the page already had it.
            if entry.get("source") in (source_id, data.get("batch")):
                continue
            if entry.get("description") == finding.get("description"):
                continue
            theirs |= _words(entry.get("description", ""))
        for key in ("hook", "narrative"):
            if isinstance(doc.get(key), str):
                theirs |= _words(doc[key])
        if not theirs:
            continue
        share = len(mine & theirs) / len(mine)
        if share >= 0.34:
            hits.append((share, finding.get("id", "?"), res["path"],
                         finding.get("description", "")[:70]))

    hits.sort(reverse=True)
    print(f"overlap: {checked} resolved finding(s) checked against their pages"
          + (f", {missing} page(s) not on disk yet" if missing else ""))
    if not hits:
        print("  none — no finding repeats what its page already says.")
        return
    print(f"  {len(hits)} finding(s) may repeat what the page already carries:")
    for share, fid, page_path, text in hits:
        print(f"    {share:.0%}  {fid}  {page_path}")
        print(f"          {text}...")
    print("  Read each one: decline it, or trim it to the part that is new.")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--stats", action="store_true", help="print the yield so far")
    ap.add_argument("--report", type=Path, metavar="FINDINGS",
                    help="print one batch by neighborhood, as the PR body's table")
    ap.add_argument("--overlap", type=Path, metavar="FINDINGS",
                    help="report findings whose target page already says the same thing")
    args = ap.parse_args()

    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    ids = registered_ids()
    check_register(ids)

    files = findings_files()
    for path in files:
        check_findings_file(path, schema, ids)

    # The example is documentation, so it has to stay valid; it is exempt from
    # the registered-directory rule because it lives under schema/.
    if EXAMPLE.exists():
        example = json.loads(EXAMPLE.read_text(encoding="utf-8"))
        validate(example, schema, schema, "$",
                 lambda p, m: err(str(EXAMPLE.relative_to(ROOT.parent)), f"{p}: {m}"))
        check_rules(EXAMPLE.relative_to(ROOT.parent), example)

    if args.stats:
        stats(files)
        print()

    if args.report:
        report(args.report)
        print()

    if args.overlap:
        overlap(args.overlap)
        print()

    if errors:
        print(f"{len(errors)} problem(s):", file=sys.stderr)
        for e in errors:
            print(f"  {e}", file=sys.stderr)
        return 1
    print(f"research: OK — {len(ids)} source(s) registered, {len(files)} findings file(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
