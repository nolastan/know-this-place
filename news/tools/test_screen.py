#!/usr/bin/env python3
"""Cases the screen and the address matcher got wrong once. Stdlib only.

    python3 news/tools/test_screen.py

Every case here is a real headline or a real sentence out of a real article,
kept because the module's judgement lives in word lists and regexes that are
edited often and are easy to break quietly. Add a case whenever you change one.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from poll import (address_signal, bare_addresses, elsewhere_signal,  # noqa: E402
                  screen, sf_signal)

# A small stand-in for the site's street vocabulary; the real one comes from
# shared/addresses.geojson and has thousands of names in it.
STREETS = {"divisadero", "mission", "mcallister", "powell", "valencia", "castro",
           "hill", "geary", "third", "bay", "california", "market"}

SF = {"scope": "sf"}
BAY = {"scope": "bay-area"}


def item(title, summary="", categories=()):
    return {"title": title, "summary": summary, "categories": list(categories)}


GEOGRAPHY = [
    # (item, feed, expected verdict, what the case is about)
    (item("Redwood City Police Say Liquor Store Manager Chained Himself",
          categories=["San Francisco", "Bay Area"]), SF, "skip",
     "a feed tagging everything San Francisco must not outvote the headline"),
    (item("Nightwave Bar And Kitchen To Open In Guerneville"), SF, "skip",
     "the What Now SF feed files Sonoma County stories"),
    (item("South San Francisco approves 400-unit project"), SF, "skip",
     "South San Francisco is a different city"),
    (item("Giants land 2028 All-Star Game at Oracle Park"), SF, "skip",
     "'San Francisco Giants' is not the city"),
    (item("San Jose Japantown Boutique Announces Closure Following Building Sale"),
     SF, "skip",
     "another city's neighborhood wearing a San Francisco neighborhood's name"),
    (item("Foundation work begins at 2918 Mission Street"), BAY, "read",
     "an address on a regional feed is queued even with the city unnamed"),
    (item("New apartments rise in the Mission"), BAY, "read",
     "a neighborhood name is a San Francisco signal"),
]

ADDRESSES = [
    (item("Greystar Takes Over Stalled 400 Divisadero Site, 203 Units Break Ground"),
     "address", "a bare number and street, the way a headline writes one"),
    (item("Lone Mountain Lot Vacant Since 2014 Finally Set for Three New Apartments",
          summary="A vacant lot at 2740 McAllister Street is one step closer."),
     "address", "the address is in the summary, not the headline"),
    (item("North Beach Renters Fight Eviction After New Owners Invoke Ellis Act"),
     "shape", "an eviction story usually carries its address in the body"),
    (item("Meet the District 8 candidates: Should S.F. allow taller buildings?"),
     "shape", "'building' is a weak signal, and NOT_LOCAL outranks it"),
]

# Sentences that must NOT produce an address.
NOT_ADDRESSES = [
    ("Carrigg cf 4 0 1 1 0 1 .291 Castro rf 3 0 0 0 0 1 .239 Hill ss",
     "a box score is a table of numbers beside a column of surnames"),
    ("In 2026 Mission Local reported that the permit had lapsed",
     "a year running into a publication name is not an address"),
    ("Gilbert cf 4 2 3 3 1 1 .243 Castro dh 5 1 1 1 0 0",
     "the same table trap with a decimal immediately before the number"),
    ("Muni is adding service on the 1 California and the 5 Fulton this month",
     "San Francisco names its bus lines number-then-street, and 1 California "
     "Street is a real page on this site"),
    ("riders on the 38 Geary route will see longer trains",
     "the transit word can follow the line name as well as precede it"),
]
# There is deliberately no case here demanding that "1200 Market" be rejected
# inside some other phrase. A number, a street name and a lowercase word after
# it is what a real address looks like in prose — "at 1200 Market, the tower…" —
# and a guard tight enough to reject the contrived case rejects the real ones.
# The reader discards the rest; that is the asymmetry AGENTS.md argues for.

ARE_ADDRESSES = [
    ("Foundation work is underway at 2918 Mission, the former laundromat site",
     "2918", "Mission"),
    ("permits were resubmitted for 2740 McAllister in Lone Mountain",
     "2740", "McAllister"),
    ("Six households at 2055 Powell are fighting to stay", "2055", "Powell"),
]


def main() -> int:
    failed = 0

    for it, feed, expected, why in GEOGRAPHY:
        verdict, reason = screen(it, feed, STREETS)
        if verdict != expected:
            failed += 1
            print(f"FAIL  {why}\n      {it['title'][:70]!r}\n"
                  f"      expected {expected}, got {verdict} — {reason}")

    for it, expected, why in ADDRESSES:
        kind, _ = address_signal(it, STREETS)
        if kind != expected:
            failed += 1
            print(f"FAIL  {why}\n      {it['title'][:70]!r}\n"
                  f"      expected {expected!r}, got {kind!r}")

    for text, why in NOT_ADDRESSES:
        hits = list(bare_addresses(text, STREETS))
        if hits:
            failed += 1
            print(f"FAIL  {why}\n      {text[:70]!r}\n"
                  f"      matched {[f'{n} {s}' for n, s, _ in hits]}")

    for text, number, street in ARE_ADDRESSES:
        hits = [(n, s) for n, s, _ in bare_addresses(text, STREETS)]
        if (number, street) not in hits:
            failed += 1
            print(f"FAIL  expected {number} {street} in {text[:60]!r}\n"
                  f"      matched {hits}")

    total = len(GEOGRAPHY) + len(ADDRESSES) + len(NOT_ADDRESSES) + len(ARE_ADDRESSES)
    if failed:
        print(f"\n{failed} of {total} case(s) failed.")
        return 1
    print(f"screen: OK — {total} case(s).")

    # The signal helpers, spot-checked on their own trap.
    assert sf_signal(item("South San Francisco housing")) is None
    assert elsewhere_signal(item("A fire in the Richmond District")) is None, \
        "Richmond must stay out of the elsewhere list"
    return 0


if __name__ == "__main__":
    sys.exit(main())
