#!/usr/bin/env python3
"""Read and write a page's data.json in the format it came in.

Pages on disk are indented by one space or two, and some escape non-ASCII.
A publisher that re-dumps every page at indent=2 turns a one-line addition
into a 700-line diff; this trap was paid for in at least five runs (see
research/LESSONS.md, "Write a page's data.json back in the format it came
in"). Import these two functions instead of calling json.dump yourself:

    sys.path.insert(0, "research/tools"); import pagejson
    data, fmt = pagejson.load(path)
    data["historical_record"].append({...})   # append; never re-sort
    pagejson.save(path, data, fmt)

Stdlib only.
"""
import json
import re


def load(path):
    """Return (data, fmt): the parsed page and the format to write it back in."""
    text = open(path, encoding="utf-8").read()
    m = re.match(r"\{\n( +)\S", text)
    fmt = {
        "indent": len(m.group(1)) if m else 2,
        "ensure_ascii": "\\u" in text and not re.search(r"[^\x00-\x7f]", text),
        "newline": text.endswith("\n"),
    }
    return json.loads(text), fmt


def save(path, data, fmt):
    """Write data back with the indent, escaping and trailing newline it had."""
    out = json.dumps(data, indent=fmt["indent"], ensure_ascii=fmt["ensure_ascii"])
    with open(path, "w", encoding="utf-8") as f:
        f.write(out + ("\n" if fmt["newline"] else ""))
