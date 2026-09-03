#!/usr/bin/env python3
"""Consistency checks for the research module. Stdlib only.

    python3 research/tools/check.py            # check everything
    python3 research/tools/check.py --stats    # ...and print the yield so far
    python3 research/tools/check.py --report <findings-file>   # the PR body's table
    python3 research/tools/check.py --overlap <findings-file>  # facts the pages already carry
    python3 research/tools/check.py --landed  <findings-file>  # published entries that changed nothing

What it checks:
  * every dossier in research/sources/ has a row in research/SOURCES.md, and
    every registered id has a dossier;
  * every findings file sits under a registered source id and validates against
    research/schema/finding.schema.json;
  * the cross-field rules the schema can't express (a resolved finding needs a
    parcel and a method; a published one needs to be resolved first);
  * that every published finding has a page at the path it records — a parcel
    addressed on two streets keeps one page, at the number the assessor files
    it under, so a path formed from the finding's own number can name a
    directory that never gets created;
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
import functools
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


# The source talking about itself, in a field that becomes page prose. Matches
# "the volume records", "this statement dates", "the survey gives" and friends —
# a determiner, one of the source nouns, and a reporting verb.
SOURCE_VOICE = re.compile(
    r"\b(?:the|this|its|a)\s+(?:same\s+)?"
    r"(?:volume|statement|survey|report|archive|newsletter|document|guide|nomination|inventory)\b"
    r"[^.]{0,40}?\b(?:says?|said|states?|records?|recorded|gives?|dates?|notes?|lists?|"
    r"describes?|identifies|credits?|calls?|marks?|reports?|mentions?|shows?|holds?|"
    r"attributes?|according)\b", re.I)

# The same slip with the noun elided. "Illustrated as a good example of Greek
# Revival" names no source and still reads on the page as the document talking
# about its own figures — there is no illustration on the page. It slipped past
# the pattern above four times in one run because it needs no noun at all.
# "photographed as an example of the neighbourhood's flats" is the same slip and
# was not caught: it survived the first sweep in nine descriptions because the
# verb list here was written from the four that happened to be in front of it.
SOURCE_VOICE_PASSIVE = re.compile(
    r"\b(?:illustrated|pictured|depicted|reproduced|photographed)\s+"
    r"(?:above|below|here|opposite)?\s*as\b"
    r"|\bgiven\s+as\s+an\s+example\b|\bcaptioned\b", re.I)


@functools.lru_cache(maxsize=1)
def pages_by_apn() -> dict:
    """Every address page on disk, keyed by the parcel it documents.

    Reading 15,000 files is not free, so nothing calls this until a finding has
    already failed the cheap test — a `resolution.path` with no `data.json`
    under it. Then it answers the only question worth asking next: does the
    parcel have a page somewhere else?
    """
    out: dict[str, str] = {}
    for p in (ROOT.parent / "san-francisco").glob("*/*/*/data.json"):
        try:
            d = json.loads(p.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        apn = d.get("apn")
        if apn and apn not in out:
            out[apn] = d.get("path") or "/" + str(p.relative_to(ROOT.parent).parent) + "/"
    return out


def missing_page(res: dict) -> str | None:
    """Why a resolution's path has no page, phrased for the run that has to fix it.

    A parcel addressed on two streets keeps its single page at the number the
    assessor files it under, and `resolve_eas.py` forms a path from the
    finding's own number — so a resolution written before the page existed can
    name a directory that will never be created. The publisher then writes the
    fact onto the page the parcel does have and the findings file still points
    at the phantom. 28 sfp-23 findings sat like that, and eight umb-survey
    findings were declined outright with "no page was seeded for it" while the
    parcel's page had been sitting one street over the whole time.
    """
    rel = (res.get("path") or "").strip("/")
    if not rel or (ROOT.parent / rel / "data.json").exists():
        return None
    elsewhere = pages_by_apn().get(res.get("apn"))
    if elsewhere:
        return (f"no page at resolution.path {res.get('path')!r}, but parcel "
                f"{res.get('apn')} is documented at {elsewhere} — one parcel is "
                f"one page, so record that path")
    return (f"no page at resolution.path {res.get('path')!r} and parcel "
            f"{res.get('apn')} has no page anywhere — seed it, or decline the "
            f"finding with the reason (no roll row, or a condominium APN)")


def check_rules(rel: Path, data: dict) -> None:
    """Cross-field rules the schema can't state."""
    seen: set[str] = set()
    any_published = False
    unmarked: list[str] = []
    # One parcel is one page. Two findings that resolve to the same parcel and
    # are both going to a page, under different paths, mean one of them is
    # filed on a page the parcel does not have — the corner-lot case, where the city addresses a building on
    # both its streets and the site keeps a single page at the lowest number of
    # the street the assessor files it under. Caught here it is a line; caught
    # after seeding it is a page that never gets created and a fact that never
    # lands.
    paths_by_apn: dict[str, dict[str, str]] = {}
    for f in data.get("findings", []):
        if not isinstance(f, dict):
            continue
        fid = f.get("id")
        if fid in seen:
            err(str(rel), f"duplicate finding id {fid!r}")
        seen.add(fid)

        # A hyphenated street_number is a range the resolver cannot read. It
        # looks the number up literally, finds nothing, and reports "EAS has no
        # address near it on this street" — which reads like a dead address and
        # is really a mis-filled field. The range belongs in
        # extra.address_range_as_recorded, with street_number holding the low
        # number alone. One batch lost 40 resolutions to this before anyone
        # noticed 809-811 Pierce Street coming back unresolved.
        num = f.get("street_number") or ""
        extra = f.get("extra") if isinstance(f.get("extra"), dict) else {}
        _res = f.get("resolution") if isinstance(f.get("resolution"), dict) else {}
        if ("-" in num and not extra.get("address_range_as_recorded")
                and _res.get("status") == "unresolved"):
            err(str(rel), f"{fid}: street_number {num!r} is a range, but "
                          f"extra.address_range_as_recorded is not set — the "
                          f"resolver reads the range from that field and looks "
                          f"street_number up literally, so this will come back "
                          f"unresolved. Put the range there and the low number "
                          f"in street_number.")

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
            apn, path = res.get("apn"), res.get("path")
            if apn and path and pub_status != "declined":
                paths_by_apn.setdefault(apn, {}).setdefault(path, str(fid))
        elif status in ("unresolved", "rejected") and not res.get("note") and not res.get("method"):
            err(str(rel), f"{fid}: {status} findings must say why (resolution.note or .method)")

        # A page's Sources footer is the attribution; the body never names the
        # archive it came from. The trap is not a deliberate citation but a
        # hedge carried over in the extractor's voice — "the volume gives no
        # year", "the survey records it as demolished" — which reads on the
        # page as the source talking about itself. One run wrote 50 of these
        # before a grep caught them. State the fact, or drop the hedge and let
        # date_precision carry it.
        desc = f.get("description") or ""
        hit = SOURCE_VOICE.search(desc) or SOURCE_VOICE_PASSIVE.search(desc)
        if hit:
            err(str(rel), f"{fid}: description names its own source "
                          f"({hit.group(0)!r}) — a page body "
                          f"never says where the fact came from; the Sources "
                          f"footer is the attribution. State the fact instead.")

        if pub_status == "published":
            any_published = True
            if status != "resolved":
                err(str(rel), f"{fid}: published but resolution.status is {status!r}")
            if not pub.get("pr"):
                err(str(rel), f"{fid}: published findings need publish.pr")
            # "Published" is a claim about a page, and the cheapest way for it
            # to be false is for the page never to have existed.
            why = missing_page(res)
            if why:
                err(str(rel), f"{fid}: published, {why}")
            # A page's timeline is ordered by date, and an entry with no date
            # renders a row that literally reads "unknown" above the 1930s. An
            # undated fact still has two homes that carry no year by design:
            # a spec row (building.architect, .builder, .developer, .name) for
            # a credit, and the historic_survey block for a survey's own
            # observation of style, integrity or listing. So a published
            # undated finding must say which of the two took it. The Modern
            # Architecture statement wrote 92 of these into timelines before a
            # render caught them.
            if str(f.get("date") or "").strip().lower() in (
                    "", "unknown", "undated", "undated in the source",
                    "n.d.", "n. d.", "no date", "none"):
                note = (pub.get("note") or "").lower()
                if not any(w in note for w in ("spec row", "survey block")):
                    err(str(rel), f"{fid}: published with no date at all "
                                  f"({f.get('date')!r}) — an undated fact belongs in a "
                                  f"spec row or the survey block: say which one took "
                                  f"it in publish.note, or decline the finding.")

    for apn, paths in sorted(paths_by_apn.items()):
        if len(paths) > 1:
            where = "; ".join(f"{p} ({f})" for p, f in sorted(paths.items()))
            err(str(rel), f"parcel {apn} is resolved to {len(paths)} different "
                          f"paths — one parcel is one page, so pick the one the "
                          f"parcel actually has: {where}")

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


def _page_before_batch(rel: str, batch_commits: set[str]) -> dict:
    """The page's data.json as it stood before this batch's commits touched it."""
    import subprocess
    log = subprocess.run(["git", "log", "--format=%H", "--", rel],
                         cwd=ROOT.parent, capture_output=True, text=True).stdout.split()
    mine = [c for c in log if c in batch_commits]
    if not mine:
        return {}
    blob = subprocess.run(["git", "show", f"{mine[-1]}^:{rel}"],
                          cwd=ROOT.parent, capture_output=True, text=True)
    if blob.returncode != 0:
        return {}
    try:
        return json.loads(blob.stdout)
    except json.JSONDecodeError:
        return {}


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
        is_new = not added or added[-1] in batch_commits
        (created if is_new else edited)[area] += 1
        try:
            page = json.loads((ROOT.parent / rel).read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        # Count what THIS batch stated, not what the page happens to hold. A
        # page other runs have already documented usually carries their
        # conflicts too, and counting those credited one digitalsf batch with
        # five conflicts and four disputed dates it had not written a word of.
        # For a page the batch created, everything on it is the batch's; for a
        # page it edited, subtract what was there before it touched it.
        before_unknowns, before_dates = 0, 0
        if not is_new:
            prev = _page_before_batch(rel, batch_commits)
            before_unknowns = len(prev.get("unknowns") or [])
            before_dates = 1 if (prev.get("building") or {}).get("completed_conflict") else 0
        conflicts[area] += max(0, len(page.get("unknowns") or []) - before_unknowns)
        now_dates = 1 if (page.get("building") or {}).get("completed_conflict") else 0
        dates[area] += max(0, now_dates - before_dates)

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


def _people(text: str) -> set[str]:
    """Surnames and firm words in a credit, for matching a person across sources."""
    return {w for w in re.findall(r"[A-Z][A-Za-z'\u2019&.-]{3,}", text or "")
            if w.lower() not in STOPWORDS}


def _year(value) -> int | None:
    m = re.search(r"\b(1[89]\d\d|20\d\d)\b", str(value or ""))
    return int(m.group(1)) if m else None


def _proper_names(extra) -> set[str]:
    """Business, organisation and building names a finding names in ``extra``.

    These are the handles a page already uses when it carries the same fact from
    another source. A leading article is dropped because sources disagree about
    it, and anything under five characters is dropped because it produces
    matches on ordinary words.
    """
    if not isinstance(extra, dict):
        return set()
    out: set[str] = set()
    for key in ("business_name", "organisation", "building_name", "also_known_as"):
        raw = extra.get(key)
        if not isinstance(raw, str):
            continue
        for part in re.split(r"[;/]| and later ", raw):
            name = part.strip().strip(".,")
            name = re.sub(r"^(the|a|an)\s+", "", name, flags=re.I).strip()
            if len(name) >= 5:
                out.add(name)
    return out


def overlap(path: Path) -> None:
    """Report resolved findings the target page already carries.

    Two scans, because they catch different duplicates:

    * **wording** — content-word overlap against the page's other
      historical_record entries (its own source excluded) plus hook and
      narrative prose. The threshold is deliberately low: this prints
      candidates for a human decision, and a false positive costs one glance
      while a miss costs a duplicated fact.
    * **name and date** — the practitioner named in ``extra`` plus a year
      within two of an entry already on the page from another source. Wording
      overlap misses these whenever the two sources phrase the same credit
      differently, which they usually do. A citywide source organised by
      architect or builder overlaps a neighbourhood survey of the same person
      almost completely; volume D-F of the professionals biographies had 20
      duplicates flagged by wording and 35 more flagged only by this scan.
    * **the proper name** — a business, organisation or building named in
      ``extra`` that already appears, verbatim, in prose the page carries from
      another source. Undated and date-independent, which is the point: a venue
      moves, a survey and a thematic statement give it different years, and both
      the wording scan and the name-and-date scan let it through. The 2004
      sexual-identity subcultures statement had 21 findings flagged by wording
      and 28 flagged by name, most of them not in the first set — nearly its
      whole Appendix C, which is the same list of North Beach bars the North
      Beach survey had already published.
    * **the roll year** — a finding dated exactly the parcel's
      ``year_built`` whose fact is not the building going up. Every page
      already prints the assessor's year in its "Built NNNN" tag, so such a
      date adds nothing; worse, it is what a source looks like when it prints
      a build year in one column and a present-day use in the next, and the
      extractor reads the pair as one event. The SoMa Filipino addendum's
      appendix table did exactly that and put a child care centre, a bookshop
      and a Filipino cultural centre on their buildings' construction dates —
      five entries, all withdrawn. This scan flags the shape, not the error:
      an occupancy that genuinely began the year the building opened is real,
      and says so in its publish note.
    """
    repo = ROOT.parent
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        err(str(path), f"--overlap could not read the file: {exc}")
        return

    source_id = data.get("source_id", "")
    # A page records the source by the id it cites, not the register id, so the
    # only reliable way to tell "the page already had this" from "this batch just
    # wrote it" is the text of the batch's own findings.
    ours = {f.get("description", "") for f in data.get("findings", [])}

    def is_ours(entry: dict) -> bool:
        """Did this batch write this entry?

        Matching on the description text alone is not enough: a publisher
        trims the address and the date out of a finding's sentence before it
        goes on the page, so "Willard E. Worden photographed the property at
        710 Victoria Street in 1912" is stored as "…photographed the house."
        and every entry the batch had just written came back as a duplicate of
        itself — 60 of them in one run. Where a source cites per item, the
        page's source id is the register id with the item appended
        (`digitalsf-8325`), so the prefix is the reliable test.
        """
        src = entry.get("source") or ""
        return (src in (source_id, data.get("batch"))
                or (bool(source_id) and src.startswith(source_id + "-"))
                or entry.get("description", "") in ours)
    hits, name_hits, roll_hits, proper_hits, checked, missing = [], [], [], [], 0, 0
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

        # scan three: a date that is only the assessor's build year restated.
        # The page prints that year already, and a fact which is not about the
        # building going up has no business carrying it — see the docstring.
        built = _year((doc.get("parcel") or {}).get("year_built"))
        mine_year = _year(finding.get("date"))
        if (built and mine_year == built
                and finding.get("kind") not in ("construction", "building contract")):
            roll_hits.append((finding.get("id", "?"), res["path"], built,
                              finding.get("kind", "?"),
                              finding.get("description", "")[:70]))

        # scan two: the same person, credited at the same date, from another source
        who = (finding.get("extra") or {}).get("architect_as_recorded")
        names = _people(who)
        if names and mine_year:
            for entry in doc.get("historical_record", []):
                if is_ours(entry):
                    continue
                their_year = _year(entry.get("date"))
                if their_year is None or abs(their_year - mine_year) > 2:
                    continue
                if names & _people(entry.get("description", "")):
                    name_hits.append((finding.get("id", "?"), res["path"], who,
                                      entry.get("source", "?")))
                    break

        # scan four: the same named business, organisation or building, already
        # on the page from another source. See the docstring.
        wanted = _proper_names(finding.get("extra"))
        if wanted:
            for entry in doc.get("historical_record", []):
                if is_ours(entry):
                    continue
                low = entry.get("description", "").lower()
                found = sorted(n for n in wanted if n.lower() in low)
                if found:
                    proper_hits.append((finding.get("id", "?"), res["path"],
                                        found[0], entry.get("source", "?")))
                    break
            else:
                prose = " ".join(doc[k] for k in ("hook", "narrative")
                                if isinstance(doc.get(k), str)).lower()
                found = sorted(n for n in wanted if n.lower() in prose)
                if found:
                    proper_hits.append((finding.get("id", "?"), res["path"],
                                        found[0], "the page's own prose"))

        mine = _words(finding.get("description", ""))
        if not mine:
            continue
        theirs: set[str] = set()
        for entry in doc.get("historical_record", []):
            # An entry this batch wrote is not evidence the page already had it.
            if is_ours(entry):
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
    if not hits and not name_hits and not roll_hits and not proper_hits:
        print("  none — no finding repeats what its page already says.")
        return
    if hits:
        print(f"  by wording — {len(hits)} finding(s) may repeat what the page already carries:")
        for share, fid, page_path, text in hits:
            print(f"    {share:.0%}  {fid}  {page_path}")
            print(f"          {text}...")
    flagged = {h[1] for h in hits}
    only_names = [n for n in name_hits if n[0] not in flagged]
    if only_names:
        print(f"  by name and date — {len(only_names)} more finding(s) credit someone "
              f"the page already credits within two years:")
        for fid, page_path, who, other in only_names:
            print(f"    {fid}  {page_path}")
            print(f"          {who} — already on the page from {other}")
    only_proper = [n for n in proper_hits if n[0] not in flagged]
    if only_proper:
        print(f"  by name — {len(only_proper)} more finding(s) name a business, "
              f"organisation or building the page already names:")
        for fid, page_path, who, other in only_proper:
            print(f"    {fid}  {page_path}")
            print(f"          {who} — already on the page from {other}")
    if roll_hits:
        print(f"  by the roll year — {len(roll_hits)} finding(s) are dated the year "
              f"the assessor says the building went up, but are not about it going up:")
        for fid, page_path, built, kind, text in roll_hits:
            print(f"    {fid}  {page_path}  ({kind}, roll built {built})")
            print(f"          {text}...")
    print("  Read each one: decline it, or trim it to the part that is new.")


def landed(path: Path) -> None:
    """After publishing: did every "published" finding change its page?

    "Published" is a claim about a page, and the cheapest way for it to be
    false is a page that already held the same credit under a slightly
    different spelling. The write guard sees a value, does nothing, and the
    finding is marked published anyway — indistinguishable, afterwards, from a
    fact that landed. One run produced four of these before a hand check found
    them; the fix in every case is to decline the finding, or to trim the
    description to the part the page lacked and say so in publish.note.

    Deliberately not part of the always-on rule pass: most published findings
    across the repo land as structured data — a historic_survey panel, a spec
    row, a conflict sentence — rather than as their own description, so a
    global version of this rule reports thousands of false positives and gets
    ignored. Run it on the one file you just published.
    """
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        err(str(path), f"--landed could not read the file: {exc}")
        return

    checked = 0
    missing: list[tuple[str, str]] = []
    noop: list[tuple[str, str, str]] = []
    for finding in data.get("findings", []):
        pub = finding.get("publish") or {}
        if pub.get("status") != "published":
            continue
        res = finding.get("resolution") or {}
        rel = (res.get("path") or "").strip("/")
        if not rel:
            continue
        page = ROOT.parent / rel / "data.json"
        why = missing_page(res)
        if why:
            missing.append((finding.get("id", "?"), why))
            continue
        try:
            doc = json.loads(page.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            missing.append((finding.get("id", "?"),
                            f"{res.get('path')} could not be read"))
            continue
        checked += 1

        blob = json.dumps(doc, ensure_ascii=False)

        desc = (finding.get("description") or "").strip()
        if desc and desc in blob:
            continue
        # The page citing this finding's own record is proof the write landed,
        # and it is a better signal than matching text: a publisher is supposed
        # to trim the description for the page — the timeline already shows the
        # date and the page is the address — so a source whose house style is a
        # short page sentence fails the text test on every single entry. Both
        # digitalsf batches did: 885 of 885 and 116 of 116 reported as no-ops,
        # every one of them actually on its page. A check that cries wolf on a
        # whole source teaches the next run to skip it.
        cite = ((finding.get("citation") or {}).get("url") or "").strip()
        if cite and cite in blob:
            continue
        recorded = {str(v).strip() for k, v in (finding.get("extra") or {}).items()
                    if k.endswith("_as_recorded") and v}
        spec = {str(v).strip() for k, v in (doc.get("building") or {}).items()
                if k in ("architect", "builder", "developer", "name")}
        if recorded & spec:
            continue
        note = (pub.get("note") or "").lower()
        if any(w in note for w in ("spec row", "survey block", "re-worded",
                                   "reworded", "trimmed", "rewritten")):
            continue
        noop.append((finding.get("id", "?"), res.get("path", "?"), desc[:70]))

    print(f"landed: {checked} published finding(s) checked against their pages"
          + (f", {len(missing)} with no page on disk" if missing else ""))
    # A published finding whose page does not exist never landed at all, and a
    # bare count of them reads as a rounding error rather than as the failure it
    # is. `check.py` fails the run on these too; naming them here saves the run
    # a second pass to find out which.
    for fid, why in missing:
        print(f"    {fid}  {why}")
    if not noop:
        print("  every published finding left its description or a spec row on its page.")
        return
    print(f"  {len(noop)} finding(s) marked published left nothing on the page:")
    for fid, page_path, text in noop:
        print(f"    {fid}  {page_path}")
        print(f"          {text}...")
    print("  Decline each one, or trim its description to the part the page "
          "lacked and say so in publish.note.")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--stats", action="store_true", help="print the yield so far")
    ap.add_argument("--report", type=Path, metavar="FINDINGS",
                    help="print one batch by neighborhood, as the PR body's table")
    ap.add_argument("--overlap", type=Path, metavar="FINDINGS",
                    help="report findings whose target page already says the same thing")
    ap.add_argument("--landed", type=Path, metavar="FINDINGS",
                    help="after publishing: report published findings that changed nothing")
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

    if args.landed:
        landed(args.landed)
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
