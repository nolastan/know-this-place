#!/usr/bin/env python3
"""Resumable OAI-PMH harvester for DigitalSF. Stdlib only.

    python3 research/tools/digitalsf_harvest.py <set> [max_pages]

Sets: Photographs (57,647) · city (6,867) · sfhistory · lgbtq · basc.

Writes MARCXML pages to research/corpora/digitalsf/<set>/ and records the OAI
resumption token per set in that directory's state.json, so a later pass
resumes instead of re-downloading. Honours the 5-second Crawl-Delay in
https://digitalsf.org/robots.txt — do not parallelize this, and do not scrape
/search, which robots.txt disallows. See research/sources/digitalsf.md.
"""
import json, sys, time, urllib.request, urllib.parse, pathlib, re

BASE = "https://digitalsf.org/oai2d"
UA = "know-this-place research harvester (+https://knowthis.place)"
DELAY = 5
HERE = pathlib.Path(__file__).resolve().parents[1] / "corpora" / "digitalsf"
STATE = HERE / "state.json"
HERE.mkdir(parents=True, exist_ok=True)


def load():
    return json.loads(STATE.read_text()) if STATE.exists() else {"sets": {}}


def save(st):
    STATE.write_text(json.dumps(st, indent=2, sort_keys=True))


def fetch(params):
    url = BASE + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=120) as r:
        return r.read().decode("utf-8", "replace")


def main(setspec, max_pages):
    st = load()
    s = st["sets"].setdefault(setspec, {"token": None, "pages": 0, "records": 0, "total": None})
    outdir = HERE / setspec
    outdir.mkdir(exist_ok=True)

    for _ in range(max_pages):
        if s["token"]:
            params = {"verb": "ListRecords", "resumptionToken": s["token"]}
        else:
            if s["pages"]:
                print("set exhausted"); break
            params = {"verb": "ListRecords", "metadataPrefix": "marcxml", "set": setspec}
        try:
            xml = fetch(params)
        except Exception as e:
            print(f"fetch failed on page {s['pages']}: {e}"); break

        n = xml.count("<record>")
        (outdir / f"page-{s['pages']:04d}.xml").write_text(xml)
        s["pages"] += 1
        s["records"] += n

        m = re.search(r'completeListSize="(\d+)"', xml)
        if m:
            s["total"] = int(m.group(1))
        m = re.search(r"<resumptionToken[^>]*>([^<]+)</resumptionToken>", xml)
        s["token"] = m.group(1) if m else None
        save(st)
        print(f"  page {s['pages']:4} +{n:4} records  (total held {s['records']} of {s['total']})")
        if not s["token"]:
            print("no resumption token — set complete"); break
        time.sleep(DELAY)


if __name__ == "__main__":
    main(sys.argv[1], int(sys.argv[2]) if len(sys.argv) > 2 else 10)
