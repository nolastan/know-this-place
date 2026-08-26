#!/usr/bin/env python3
"""Poll the news feeds for stories that might name a San Francisco address.

    python3 news/tools/poll.py poll                  # every open feed
    python3 news/tools/poll.py poll --feed sfist     # one of them
    python3 news/tools/poll.py poll --dry-run        # screen, writing nothing at all
    python3 news/tools/poll.py poll --pages 20 --backfill-days 36500   # backfill a new feed
    python3 news/tools/poll.py status                # cursors, at a glance
    python3 news/tools/poll.py screen "a headline"   # why the screen rules the way it does
    python3 news/tools/poll.py find "1234 Valencia Street"   # does this address have a page?

Stdlib only. This is the mechanical half of [../AGENTS.md](../AGENTS.md): it
fetches each registered feed, works out which items the module has not already
considered, and gives every one of them a verdict — `read`, or `skip` with the
reason. It writes the queue an agent then reads, and advances the cursors.

What it will not do:

  * decide whether a story is worth a page — it only says whether the headline
    and metadata make an address plausible;
  * open an article (that is the reading stage, and it is a judgement call);
  * poll a feed whose `access` is `needs-human` in feeds.json.

The screen is deliberately cheap and deliberately conservative in one
direction: it skips on a clear signal and queues on doubt, because a queued
story costs a glance and a wrongly skipped one is invisible.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import date, datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent          # news/
REPO = ROOT.parent
FEEDS = ROOT / "feeds.json"
CURSORS = ROOT / "state" / "cursors.json"
QUEUE = ROOT / "queue"
GEOJSON = REPO / "shared" / "addresses.geojson"

UA = {"User-Agent": "know-this-place-news/1.0 (+https://knowthis.place)"}

# How many item ids a cursor remembers. A feed shows 10–30 items, so a few
# hundred is many runs' worth of overlap — enough that an item republished with
# a new date is still recognized, and small enough that the file stays readable.
SEEN_KEPT = 300


# --------------------------------------------------------------------------- #
# Fetching
# --------------------------------------------------------------------------- #

def fetch(url: str, timeout: int = 30, budget: int = 90, tries: int = 3) -> bytes:
    """One GET, retried, against a total time budget.

    urllib's timeout is per-read, so a response that trickles never fires it and
    the run hangs. Read in chunks against a wall clock instead — the same
    caution research/tools/resolve_eas.py takes with DataSF.
    """
    for attempt in range(tries):
        try:
            deadline = time.time() + budget
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=timeout) as r:
                buf = bytearray()
                while True:
                    if time.time() > deadline:
                        raise TimeoutError(f"response still arriving after {budget}s")
                    chunk = r.read(65536)
                    if not chunk:
                        break
                    buf.extend(chunk)
            return bytes(buf)
        except urllib.error.HTTPError as exc:
            # A 404 is an answer, not a transport failure. Retrying one costs
            # 25s of sleeps to be told the same thing three times, and the page
            # walk in fetch_feed() ends on exactly this.
            if exc.code == 404 or attempt == tries - 1:
                raise
        except Exception as exc:  # noqa: BLE001 — any transport error is retryable
            if attempt == tries - 1:
                raise
            wait = (5, 20)[min(attempt, 1)]
            print(f"    retry {attempt + 1}/{tries - 1} in {wait}s: {exc}",
                  file=sys.stderr, flush=True)
            time.sleep(wait)
    return b""


# --------------------------------------------------------------------------- #
# Parsing — three shapes of source
# --------------------------------------------------------------------------- #

def text_of(el) -> str:
    """An element's text with tags stripped and entities already decoded."""
    if el is None:
        return ""
    raw = "".join(el.itertext())
    return " ".join(re.sub(r"<[^>]+>", " ", raw).split())


def when(raw: str) -> str | None:
    """A feed's date string → ISO 8601 UTC, or None if it isn't one.

    Feeds here use RFC 2822 (`Sat, 15 Aug 2026 14:31:28 -0400`), Bluesky drops
    the weekday, and Atom uses ISO. None is a real answer: an item with no date
    is still an item, and the cursor identifies it by id rather than by date.
    """
    raw = (raw or "").strip()
    if not raw:
        return None
    try:
        return parsedate_to_datetime(raw).astimezone(timezone.utc).isoformat()
    except (TypeError, ValueError):
        pass
    try:
        dt = datetime.fromisoformat(raw.replace("Z", "+00:00"))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc).isoformat()
    except ValueError:
        return None


def clean_url(url: str) -> str:
    """Drop the campaign parameters a social post hangs off an article link."""
    if not url:
        return url
    parts = urllib.parse.urlsplit(url)
    kept = [(k, v) for k, v in urllib.parse.parse_qsl(parts.query)
            if not k.lower().startswith(("utm_", "ana"))]
    return urllib.parse.urlunsplit(
        (parts.scheme, parts.netloc, parts.path,
         urllib.parse.urlencode(kept), ""))


def parse_rss(body: bytes) -> list[dict]:
    """RSS 2.0 <item>s and Atom <entry>s, in the fields the screen reads."""
    root = ET.fromstring(body)
    out = []
    for el in root.iter():
        tag = el.tag.split("}")[-1]
        if tag not in ("item", "entry"):
            continue
        link = text_of(el.find("{*}link"))
        if not link:  # Atom puts it in an attribute
            href = el.find("{*}link")
            link = href.get("href", "") if href is not None else ""
        summary = (text_of(el.find("{*}description"))
                   or text_of(el.find("{*}summary"))
                   or text_of(el.find("{*}encoded")))
        published = (when(text_of(el.find("{*}pubDate")))
                     or when(text_of(el.find("{*}published")))
                     or when(text_of(el.find("{*}updated"))))
        out.append({
            "id": text_of(el.find("{*}guid")) or link,
            "title": text_of(el.find("{*}title")),
            "url": clean_url(link),
            "published": published,
            "summary": summary[:600],
            "categories": [text_of(c) for c in el.findall("{*}category") if text_of(c)],
            # Some feeds syndicate the whole article. news/tools/read.py uses it
            # when the article page refuses a fetcher — Hoodline's does — but it
            # is never written to disk: it is the outlet's text, not ours.
            "body": text_of(el.find("{*}encoded")),
        })
    return out


POST_LINK = re.compile(r"https?://\S+")


def parse_bluesky(body: bytes) -> list[dict]:
    """A Bluesky account's RSS: posts, not articles.

    There is no <title> element at all — the post text is the whole item — and
    the article it points at is a URL inside that text, frequently a bit.ly.
    So the headline here is the newsroom's own words about the story, and the
    link is the last URL in the post; both are what a reader would follow.
    """
    out = []
    for item in parse_rss(body):
        text = item["summary"] or item["title"]
        links = POST_LINK.findall(text)
        article = clean_url(links[-1].rstrip(".,)")) if links else ""
        headline = POST_LINK.sub("", text).strip(" →—-\n\t ")
        out.append({
            "id": item["id"],
            "title": " ".join(headline.split()),
            "url": article or item["url"],
            "post_url": item["url"],
            "published": item["published"],
            "summary": "",
            "categories": [],
            "link_is_shortened": bool(article) and "bit.ly" in article,
        })
    return out


class Links(HTMLParser):
    """Every <a href> on a page with the text inside it."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.found: list[tuple[str, str]] = []
        self._href = None
        self._text: list[str] = []

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            self._href = dict(attrs).get("href")
            self._text = []

    def handle_data(self, data):
        if self._href is not None:
            self._text.append(data)

    def handle_endtag(self, tag):
        if tag == "a" and self._href is not None:
            self.found.append((self._href, " ".join("".join(self._text).split())))
            self._href, self._text = None, []


def parse_html(body: bytes, feed: dict) -> list[dict]:
    """A section page: the article links on it, in the order they appear.

    No dates and no summaries — a listing page states neither — so an item here
    carries only its headline and its URL, and the cursor is the set of URLs
    already seen rather than a date.
    """
    parser = Links()
    parser.feed(body.decode("utf-8", "replace"))
    pattern = re.compile(feed["link_pattern"])
    seen, out = set(), []
    for href, text in parser.found:
        path = urllib.parse.urlsplit(href).path
        if not pattern.match(path):
            continue
        url = clean_url(urllib.parse.urljoin(feed["url"], href))
        if url in seen:
            continue
        seen.add(url)
        # A listing links each story twice — once from the image, once from the
        # headline — and the image link's anchor text is empty. Take the text
        # from whichever of the two has it.
        title = text or next((t for h, t in parser.found
                              if urllib.parse.urljoin(feed["url"], h) == url and t), "")
        out.append({"id": url, "title": title, "url": url,
                    "published": None, "summary": "", "categories": []})
    return out


PARSERS = {"rss": lambda body, feed: parse_rss(body),
           "bluesky": lambda body, feed: parse_bluesky(body),
           "html": parse_html}


def paged_url(url: str, page: int) -> str:
    """A WordPress feed's page N. Page 1 is the feed's own url, untouched."""
    if page <= 1:
        return url
    parts = urllib.parse.urlsplit(url)
    query = [(k, v) for k, v in urllib.parse.parse_qsl(parts.query) if k != "paged"]
    return urllib.parse.urlunsplit(
        (parts.scheme, parts.netloc, parts.path,
         urllib.parse.urlencode(query + [("paged", str(page))]), parts.fragment))


def fetch_feed(feed: dict, pages: int) -> list[dict]:
    """Every item the feed serves, walking back `pages` pages.

    A feed shows its newest handful and nothing else — SF YIMBY five items, The
    Voice ten — so `--backfill-days` cannot reach a story the feed no longer
    lists, however large it is set. WordPress serves the rest through `?paged=N`,
    and that is the only way back past the front page.

    **The end of the archive arrives as a 404**, and both feeds measured serve
    it as a valid RSS document titled "Page not found" with no items in it. So
    the walk stops on either signal — the 404, or a page that adds no id the
    earlier pages did not already hold — and it stops by *returning what it has*
    rather than raising. Letting the 404 out of here would be a real loss: it
    reaches poll() as a feed-level failure, which discards every page already
    walked and leaves the cursor unmoved. Asking for more pages than a feed has
    is the normal way to backfill one, not an error.

    Paging is an RSS affordance. An html feed is a section page whose paging is
    its own, and a Bluesky feed has none, so both stay at one page.
    """
    if feed["kind"] != "rss":
        pages = 1
    seen: set[str] = set()
    out: list[dict] = []
    for page in range(1, max(1, pages) + 1):
        try:
            body = fetch(paged_url(feed["url"], page))
        except urllib.error.HTTPError as exc:
            if exc.code == 404 and page > 1:
                break       # walked off the end of the archive
            raise           # page 1 is the feed itself; that 404 is a real fault
        fresh = [i for i in PARSERS[feed["kind"]](body, feed) if i["id"] not in seen]
        if not fresh:
            break
        seen.update(i["id"] for i in fresh)
        out.extend(fresh)
        if page < pages:
            time.sleep(2)  # be a polite client
    return out


# --------------------------------------------------------------------------- #
# The screen — is this San Francisco, and might it name an address?
# --------------------------------------------------------------------------- #

# Places that are not San Francisco. Naming one and not naming the city is the
# clearest signal a regional feed gives us.
#
# Richmond is deliberately absent: the Richmond District is San Francisco and
# Richmond is the East Bay, and a headline saying which is rare. Let the other
# signals decide rather than dropping half the Richmond District's coverage.
ELSEWHERE = [
    "oakland", "berkeley", "san jose", "alameda", "emeryville", "san leandro",
    "hayward", "fremont", "union city", "newark", "milpitas", "livermore",
    "dublin", "pleasanton", "danville", "walnut creek", "concord", "martinez",
    "antioch", "richmond, ca", "el cerrito", "albany, ca", "vallejo", "benicia",
    "fairfield", "napa", "sonoma", "santa rosa", "petaluma", "novato",
    "guerneville", "healdsburg", "sebastopol", "san rafael", "marin county",
    "mill valley", "sausalito", "tiburon", "larkspur", "corte madera",
    "daly city", "south san francisco", "brisbane", "pacifica", "colma",
    "san bruno", "millbrae", "burlingame", "san mateo", "foster city",
    "redwood city", "menlo park", "palo alto", "mountain view", "sunnyvale",
    "santa clara", "cupertino", "campbell", "saratoga", "los gatos",
    "half moon bay", "east bay", "south bay", "north bay", "peninsula",
    "silicon valley", "sacramento", "san diego", "los angeles", "fresno",
    "stockton", "santa cruz", "monterey", "tahoe", "napa valley",
]

# Phrases that contain "San Francisco" without meaning the city. Stripped before
# the city is looked for, or every Bay Area story reads as an SF story.
NOT_THE_CITY = [
    "south san francisco", "san francisco bay area", "san francisco bay",
    "san francisco 49ers", "san francisco giants", "greater san francisco",
    "san francisco peninsula", "university of san francisco",
    # Another city's neighborhood, wearing a San Francisco neighborhood's name.
    # "San Jose Japantown Boutique Announces Closure" was queued on the first
    # run because Japantown is in the list below and outvoted San Jose.
    "san jose japantown", "oakland chinatown", "oakland's chinatown",
    "west oakland", "east oakland", "north oakland", "downtown oakland",
    "downtown san jose", "downtown berkeley",
]

# Neighborhoods and landmarks that mean San Francisco on their own.
SF_PLACES = [
    "san francisco", "the mission", "mission district", "castro", "tenderloin",
    "soma", "south of market", "bayview", "hunters point", "dogpatch",
    "potrero hill", "bernal heights", "noe valley", "glen park", "excelsior",
    "outer mission", "visitacion valley", "portola", "sunset district",
    "inner sunset", "outer sunset", "richmond district", "inner richmond",
    "outer richmond", "the richmond", "haight", "cole valley", "hayes valley",
    "duboce triangle", "lower haight", "japantown", "fillmore", "western addition",
    "pacific heights", "cow hollow", "marina district", "russian hill",
    "nob hill", "telegraph hill", "north beach", "chinatown", "financial district",
    "union square", "mid-market", "civic center", "twin peaks", "diamond heights",
    "west portal", "st. francis wood", "ingleside", "oceanview", "lakeshore",
    "presidio", "treasure island", "mission bay", "embarcadero", "fisherman's wharf",
    "golden gate park", "the castro", "polk gulch", "russian hill", "sfmta",
    "sfpd", "sfusd", "sf city hall", "board of supervisors",
]

# Street types as a headline writes them.
STREET_TYPE = (r"(?:Street|St\.|Avenue|Ave\.?|Boulevard|Blvd\.?|Road|Rd\.?|Way|Place|Pl\.?|"
               r"Drive|Dr\.?|Terrace|Lane|Ln\.?|Alley|Court|Ct\.?|Plaza|Row|Steps|Stairway|Circle)")
NUMBERED_ADDRESS = re.compile(
    r"\b(\d{1,5})[A-Za-z]?\s+((?:[A-Z][A-Za-z'\.]+|\d{1,3}(?:st|nd|rd|th))"
    r"(?:\s+[A-Z][A-Za-z'\.]+){0,2})\s+" + STREET_TYPE + r"\b")
NAMED_STREET = re.compile(
    r"\b((?:[A-Z][A-Za-z'\.]+|\d{1,3}(?:st|nd|rd|th))(?:\s+[A-Z][A-Za-z'\.]+){0,1})\s+"
    + STREET_TYPE + r"\b")

# Story shapes that hang on a building. These are the ones that carry a street
# number in the body even when the headline only names the business.
PLACE_WORDS = [
    "open", "opens", "opening", "reopen", "close", "closes", "closing", "shutter",
    "debut", "launch", "restaurant", "bar", "cafe", "café", "coffee", "bakery",
    "brewery", "taqueria", "diner", "pizzeria", "market", "grocery", "store",
    "shop", "retail", "storefront", "gallery", "museum", "theater", "theatre",
    "venue", "club", "hotel", "motel", "hostel", "building", "tower", "highrise",
    "high-rise", "warehouse", "church", "school", "library", "clinic", "hospital",
    "housing", "apartment", "condo", "unit", "flat", "victorian", "mansion",
    "house", "home", "property", "parcel", "lot", "site", "block", "corner",
    "development", "project", "construction", "renovation", "remodel", "permit",
    "planning commission", "landmark", "historic", "preservation", "demolition",
    "demolish", "fire", "blaze", "collapse", "evict", "eviction", "tenant",
    "landlord", "lease", "leases", "leased", "sold", "sells", "sale", "buys",
    "acquire", "acquisition", "listing", "square feet", "sq ft", "sqft",
    "affordable", "shelter", "navigation center", "vacant", "vacancy",
    "restaurant space", "food hall", "mural", "sidewalk", "parklet",
]

# Story shapes that do not. Only consulted when nothing above matched.
NOT_LOCAL = [
    "weather", "forecast", "storm", "hurricane", "wildfire smoke", "heat wave",
    "earthquake early warning", "49ers", "giants", "warriors", "sharks",
    "valkyries", "super bowl", "playoff", "election", "poll finds", "endorse",
    "ballot measure", "governor", "congress", "senate", "white house", "trump",
    "supreme court", "lawsuit against the state", "recall", "obituary",
    "died at", "opinion", "editorial", "column", "review:", "recipe",
    "things to do", "guide to", "best of", "weekend getaway", "road trip",
    "horoscope", "quiz", "photos:", "video:",
]


def haystack(item: dict) -> str:
    return " ".join([item.get("title") or "", item.get("summary") or "",
                     " ".join(item.get("categories") or [])])


def sf_signal(item: dict, where: str = "all") -> str | None:
    """What says San Francisco about this item, if anything."""
    if where == "all":
        for c in item.get("categories") or []:
            if c.strip().lower() == "san francisco":
                return "tagged San Francisco"
    text = (item.get("title") if where == "title" else haystack(item)).lower()
    for phrase in NOT_THE_CITY:
        text = text.replace(phrase, " ")
    for place in SF_PLACES:
        if re.search(r"\b" + re.escape(place), text):
            return f"names {place}"
    return None


def elsewhere_signal(item: dict, where: str = "all") -> str | None:
    text = (item.get("title") if where == "title" else haystack(item)).lower()
    for place in ELSEWHERE:
        if re.search(r"\b" + re.escape(place) + r"\b", text):
            return place
    return None


# Words a sentence puts between a number and a street name — "1077 on Market
# Street", "40 at Turk Street". They capitalize at the start of a headline and
# read as part of the street name unless they are ruled out here.
CONNECTORS = {"on", "at", "in", "of", "the", "and", "for", "to", "near", "off",
              "from", "by", "with", "a", "an", "is", "was", "as", "its"}


def plausible_street(name: str) -> bool:
    """Is this capture a street name, or a sentence that ran into one?"""
    return not any(w.lower() in CONNECTORS for w in name.split())


# A number and a street with no street type — "400 Divisadero", "2918 Mission".
# The city writes addresses this way constantly and a headline almost always
# does, so the type cannot be required; what stands in for it is the street name
# being one the site already has pages on.
BARE_ADDRESS = re.compile(r"\b(\d{1,5})\s+([A-Z][A-Za-z'\-\.]+)\b")


TABLE = re.compile(r"(?:\b\d+[\d.]*\s+){3,}$")

# San Francisco names its bus lines the way it names its addresses: the 1
# California, the 5 Fulton, the 38 Geary, the 28R 19th Avenue. Nowhere else does
# this trap exist, and it is not academic — a Muni service-change story resolved
# "1 California" onto the page for 1 California Street on the first pass.
TRANSIT = re.compile(r"\b(muni|sfmta|bus|buses|line|lines|route|routes|rapid|owl|"
                     r"streetcar|trolley|shuttle|ridership|headway)\b", re.I)


def looks_like_transit(text: str, start: int, end: int) -> bool:
    """Is this number-and-street a Muni line rather than a building?"""
    return bool(TRANSIT.search(text[max(0, start - 60):start])
                or TRANSIT.search(text[end:end + 60]))


def bare_addresses(text: str, streets: set[str]):
    """(number, street, match) for each untyped address in the text.

    Two traps, both found in real articles on the first pass:

    * **The year.** "2026 Mission Local reported" is not an address on Mission
      Street. A number in the range years occupy counts only when the street
      name ends the phrase — one that runs straight into another capitalized
      word is part of a name.
    * **The table.** A baseball box score in a Chronicle story yielded "291
      Castro" and "239 Hill" out of batting averages, because a column of
      numbers beside a column of surnames looks exactly like a column of
      addresses. A number preceded by a decimal point, or sitting in a run of
      other numbers, is data in a table and not a street number in a sentence.
    """
    for m in BARE_ADDRESS.finditer(text):
        number, name = m.group(1), m.group(2)
        if name.lower() not in streets:
            continue
        before = text[max(0, m.start() - 30):m.start()]
        if before.endswith(".") or before.endswith("-") or TABLE.search(before):
            continue
        if looks_like_transit(text, m.start(), m.end()):
            continue
        rest = text[m.end():m.end() + 40].lstrip()
        continues = bool(re.match(r"[A-Z][a-z]", rest))
        if 1500 <= int(number) <= 2100 and continues:
            continue
        yield number, name, m


def address_signal(item: dict, streets: set[str]) -> tuple[str | None, str]:
    """(how strong, why) — what makes an address plausible in this story.

    `address` is a street number and a street; `street` is a street the site
    already has pages on; `shape` is a story about a building that usually
    carries its address in the body rather than the headline.
    """
    text = haystack(item)
    for m in NUMBERED_ADDRESS.finditer(text):
        if plausible_street(m.group(2)) and not looks_like_transit(text, m.start(), m.end()):
            return "address", f"a street address in the item ({m.group(0)})"
    for number, name, m in bare_addresses(text, streets):
        return "address", f"a street address in the item ({number} {name})"
    for m in NAMED_STREET.finditer(text):
        if m.group(1).lower() in streets:
            return "street", f"names {m.group(0)}, a street the site has pages on"
    lowered = text.lower()
    hit = next((w for w in PLACE_WORDS if re.search(r"\b" + re.escape(w), lowered)), None)
    if hit:
        return "shape", f"a story shape that usually carries an address ({hit!r})"
    return None, ""


def screen(item: dict, feed: dict, streets: set[str]) -> tuple[str, str]:
    """(verdict, reason) for one item. `read` queues it; `skip` records why."""
    sf = sf_signal(item)
    other = elsewhere_signal(item)
    kind, why = address_signal(item, streets)

    # The headline is where a story says what it is about. A feed that tags
    # every item "San Francisco" — Hoodline tags a Redwood City fire that way —
    # would otherwise let the tag outvote the headline's own subject.
    other_in_title = elsewhere_signal(item, "title")
    if other_in_title and not sf_signal(item, "title"):
        return "skip", (f"not San Francisco — the headline names {other_in_title} "
                        f"and not the city")
    if not sf and other:
        # A numbered address in a story about Oakland is an Oakland address.
        return "skip", f"not San Francisco — names {other} and not the city"
    if not sf and feed.get("scope") == "bay-area":
        if kind in ("address", "street"):
            # A headline can name the building without naming the city. A named
            # street is thin evidence on its own — plenty of street names are
            # shared across the region — so this queues the story for a reader
            # to confirm the city rather than deciding it here.
            return "read", f"{why}; the city is not named — confirm it is San Francisco"
        return "skip", "no San Francisco signal, and this feed covers the whole region"

    lowered = haystack(item).lower()
    topic = next((w for w in NOT_LOCAL if w in lowered), None)
    if kind in ("address", "street"):
        return "read", why
    if topic:
        # A ballgame at Oracle Park matches 'home' and a restaurant review
        # matches 'restaurant'. Where the only address signal is the shape of
        # the story, a subject that never carries a street number outranks it.
        return "skip", f"unlikely to name an address ({topic!r})"
    if kind:
        return "read", why
    return "skip", "nothing in the headline or metadata points at a building"


# --------------------------------------------------------------------------- #
# The site's own addresses — the street vocabulary, and the page lookup
# --------------------------------------------------------------------------- #

def page_index() -> dict[str, str]:
    """Every published address → its path, from the map's own index."""
    if not GEOJSON.exists():
        return {}
    data = json.loads(GEOJSON.read_text(encoding="utf-8"))
    return {f["properties"]["t"].lower(): f["properties"]["p"]
            for f in data.get("features", []) if f.get("properties")}


def street_vocabulary(pages: dict[str, str]) -> set[str]:
    """The street names the site has pages on, as a headline would write them."""
    out = set()
    for addr in pages:
        m = re.match(r"^\d+[a-z]?\s+(.*)$", addr)
        if not m:
            continue
        name = re.sub(r"\s+(street|avenue|boulevard|road|way|place|drive|terrace|lane|"
                      r"alley|court|plaza|row|steps|stairway|circle|park|path|walk)$",
                      "", m.group(1))
        if name:
            out.add(name)
    return out


# --------------------------------------------------------------------------- #
# Cursors
# --------------------------------------------------------------------------- #

def load_cursors() -> dict:
    if CURSORS.exists():
        return json.loads(CURSORS.read_text(encoding="utf-8"))
    return {"$comment": "One cursor per feed: what news/tools/poll.py has already "
                        "considered. See news/AGENTS.md.", "feeds": {}}


def save_cursors(cursors: dict) -> None:
    CURSORS.parent.mkdir(parents=True, exist_ok=True)
    CURSORS.write_text(json.dumps(cursors, indent=2, ensure_ascii=False) + "\n",
                       encoding="utf-8")


def is_new(item: dict, cursor: dict, floor: str | None) -> bool:
    """Has this item been considered before?

    Identity is the item's id — a feed re-dates a story it edits, and a date
    alone would hand it back every run. The date is only a floor: on the first
    run of a feed it stops the whole backfill landing in one queue.
    """
    if item["id"] in set(cursor.get("seen") or []):
        return False
    published = item.get("published")
    if floor and published and published < floor:
        return False
    return True


# --------------------------------------------------------------------------- #
# The run
# --------------------------------------------------------------------------- #

def poll(feed_ids: list[str], backfill_days: int, dry_run: bool,
         queue_all: bool, pages: int = 1) -> int:
    register = json.loads(FEEDS.read_text(encoding="utf-8"))["feeds"]
    cursors = load_cursors()
    pages = page_index()
    streets = {s.lower() for s in street_vocabulary(pages)}
    today = date.today().isoformat()
    floor_default = (datetime.now(timezone.utc)
                     - timedelta(days=backfill_days)).isoformat()

    polled, queued, skipped = [], [], []
    for feed in register:
        if feed_ids and feed["id"] not in feed_ids:
            continue
        if feed.get("access") != "open" and not feed_ids:
            polled.append({"feed": feed["id"], "skipped_feed": feed.get("access"),
                           "note": "not polled — see feeds.json"})
            print(f"{feed['id']}: not polled ({feed.get('access')})", flush=True)
            continue
        if feed.get("access") != "open":
            print(f"{feed['id']}: feeds.json marks this {feed.get('access')!r}; "
                  f"polling it is a decision for a human, not a flag. Skipped.",
                  file=sys.stderr, flush=True)
            continue

        cursor = cursors.setdefault("feeds", {}).setdefault(feed["id"], {})
        try:
            items = fetch_feed(feed, pages)
        except Exception as exc:  # noqa: BLE001 — one bad feed must not end the run
            polled.append({"feed": feed["id"], "error": str(exc)})
            print(f"{feed['id']}: FAILED — {exc}", file=sys.stderr, flush=True)
            continue

        # A feed with no cursor yet is being read for the first time; without a
        # floor its whole backfill would land in one queue.
        floor = None if cursor.get("seen") else floor_default
        fresh = [i for i in items if is_new(i, cursor, floor)]
        for item in fresh:
            verdict, reason = ("read", "queued by --all") if queue_all else \
                screen(item, feed, streets)
            row = dict(item, feed=feed["id"], outlet=feed["outlet"],
                       verdict=verdict, reason=reason)
            row.pop("body", None)   # the outlet's article text stays out of the repo
            (queued if verdict == "read" else skipped).append(row)

        n_read = sum(1 for i in queued if i["feed"] == feed["id"])
        polled.append({"feed": feed["id"], "fetched": len(items),
                       "considered": len(fresh), "queued": n_read,
                       "skipped": len(fresh) - n_read})
        print(f"{feed['id']}: {len(items)} in the feed, {len(fresh)} new, "
              f"{n_read} queued to read", flush=True)

        if not dry_run:
            seen = list(dict.fromkeys([i["id"] for i in items]
                                      + list(cursor.get("seen") or [])))[:SEEN_KEPT]
            dates = [i["published"] for i in items if i.get("published")]
            cursor.update({
                "url": feed["url"],
                "last_run": today,
                "latest_published": max(dates) if dates else cursor.get("latest_published"),
                "considered": (cursor.get("considered") or 0) + len(fresh),
                "queued": (cursor.get("queued") or 0) + n_read,
                "seen": seen,
            })
        time.sleep(2)  # be a polite client

    run = {"run": today, "polled": polled, "items": queued, "skipped": [
        {k: s[k] for k in ("feed", "title", "url", "reason") if k in s} for s in skipped]}
    if not (queued or skipped):
        print("\nNothing new.")
    elif dry_run:
        # A dry run writes no queue file. The queue is the durable worklist and
        # the cursor is not, so one written here would list items screened
        # against cursors that never moved — work the next real run would do
        # again, from a file claiming it had already been done. Worse where a
        # real queue exists: the append path below would mix these items into a
        # worklist someone is part-way through draining.
        print(f"\n{len(queued)} to read, {len(run['skipped'])} skipped "
              f"(--dry-run: no queue file written)")
    else:
        QUEUE.mkdir(parents=True, exist_ok=True)
        path = QUEUE / f"{today}.json"
        if path.exists():  # a second run the same day appends rather than clobbers
            prev = json.loads(path.read_text(encoding="utf-8"))
            have = {i["url"] for i in prev.get("items", [])}
            run["items"] = prev.get("items", []) + [i for i in queued if i["url"] not in have]
            run["skipped"] = prev.get("skipped", []) + run["skipped"]
            run["polled"] = prev.get("polled", []) + run["polled"]
        path.write_text(json.dumps(run, indent=2, ensure_ascii=False) + "\n",
                        encoding="utf-8")
        print(f"\n{len(run['items'])} to read, {len(run['skipped'])} skipped "
              f"→ {path.relative_to(REPO)}")

    if not dry_run:
        save_cursors(cursors)
    else:
        print("(--dry-run: cursors not moved, no queue file written)")
    return 0


def status() -> int:
    register = {f["id"]: f for f in json.loads(FEEDS.read_text(encoding="utf-8"))["feeds"]}
    cursors = load_cursors().get("feeds", {})
    head = f"{'feed':<22}{'last run':<12}{'newest item':<28}{'considered':>11}{'queued':>8}"
    print(head)
    print("-" * len(head))
    for fid, feed in register.items():
        c = cursors.get(fid, {})
        newest = (c.get("latest_published") or "")[:19].replace("T", " ")
        note = "" if feed.get("access") == "open" else f"   ({feed.get('access')})"
        print(f"{fid:<22}{c.get('last_run', '—'):<12}{newest or '—':<28}"
              f"{c.get('considered', 0):>11}{c.get('queued', 0):>8}{note}")
    pending = sorted(QUEUE.glob("*.json"))
    if pending:
        total = sum(len(json.loads(p.read_text(encoding='utf-8')).get("items", []))
                    for p in pending)
        print(f"\n{len(pending)} queue file(s) waiting to be read, {total} item(s):")
        for p in pending:
            print(f"  {p.relative_to(REPO)}")
    return 0


def explain(headline: str) -> int:
    """Run the screen over one headline and say what it saw. Tuning aid."""
    pages = page_index()
    streets = {s.lower() for s in street_vocabulary(pages)}
    item = {"title": headline, "summary": "", "categories": []}
    for scope in ("sf", "bay-area"):
        verdict, reason = screen(item, {"scope": scope}, streets)
        print(f"  scope={scope:<9} {verdict:<5} — {reason}")
    kind, why = address_signal(item, streets)
    print(f"\n  San Francisco signal: {sf_signal(item) or '—'}")
    print(f"  elsewhere signal:     {elsewhere_signal(item) or '—'}")
    print(f"  address signal:       {f'{kind} — {why}' if kind else '—'}")
    return 0


def find(address: str) -> int:
    """Does the site have a page for this address? The reader's first question."""
    pages = page_index()
    key = " ".join(address.lower().split())
    hit = pages.get(key)
    if hit:
        print(f"{address} → {hit}")
        return 0
    m = re.match(r"^(\d+[a-z]?)\s+(.*)$", key)
    if m:
        near = sorted(p for a, p in pages.items()
                      if a.endswith(" " + m.group(2)))[:8]
        if near:
            print(f"No page for {address}. The site has {len(near)} page(s) on that "
                  f"street, e.g.:")
            for p in near:
                print(f"  {p}")
            return 1
    print(f"No page for {address}, and none on that street. "
          f"research/tools/resolve_eas.py decides whether one should exist.")
    return 1


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="command", required=True)

    p = sub.add_parser("poll", help="fetch every open feed and screen what's new")
    p.add_argument("--feed", action="append", default=[], help="only this feed id")
    p.add_argument("--backfill-days", type=int, default=14,
                   help="on a feed's first run, ignore items older than this (default 14)")
    p.add_argument("--dry-run", action="store_true",
                   help="screen without moving cursors or writing a queue file")
    p.add_argument("--all", action="store_true", dest="queue_all",
                   help="queue every new item, screening nothing out")
    p.add_argument("--pages", type=int, default=1,
                   help="walk this many pages back through an rss feed's archive "
                        "(default 1; the feed's own page). Pair with a large "
                        "--backfill-days to backfill a newly registered feed.")

    sub.add_parser("status", help="what each cursor knows")

    p = sub.add_parser("screen", help="explain the screen's verdict on a headline")
    p.add_argument("headline")

    p = sub.add_parser("find", help="the page path for an address, if the site has one")
    p.add_argument("address")

    args = ap.parse_args()
    if args.command == "poll":
        return poll(args.feed, args.backfill_days, args.dry_run,
                    args.queue_all, args.pages)
    if args.command == "status":
        return status()
    if args.command == "screen":
        return explain(args.headline)
    return find(args.address)


if __name__ == "__main__":
    sys.exit(main())
