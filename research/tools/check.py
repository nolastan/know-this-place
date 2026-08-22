#!/usr/bin/env python3
"""Consistency checks for the research module. Stdlib only.

    python3 research/tools/check.py            # check everything
    python3 research/tools/check.py --stats    # ...and print the yield so far

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


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--stats", action="store_true", help="print the yield so far")
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

    if errors:
        print(f"{len(errors)} problem(s):", file=sys.stderr)
        for e in errors:
            print(f"  {e}", file=sys.stderr)
        return 1
    print(f"research: OK — {len(ids)} source(s) registered, {len(files)} findings file(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
