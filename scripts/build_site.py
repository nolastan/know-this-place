#!/usr/bin/env python3
"""Build the whole site from the tracked sources. Stdlib only.

Every `index.html` on this site, plus `sitemap.xml`, `sitemaps/`,
`shared/addresses.geojson`, `shared/nearby.json`, `corpus.jsonl` and `/stats/`,
is derived from `data.json` and the hub `index.md` files. None of it is
committed — the repository holds the sources, and this script turns them into
the site, in Actions before a deploy and on a laptop before a look.

It is the seven builders in the one order that works, and the order is the
whole reason it exists:

    districts → hubs → city-map → build_link_index → render → build_map_index
              → build_events → build_sitemap → build_corpus_index
              → build_stats

Every one of those edges is load-bearing, and none of them error when broken —
the site just comes out a step stale. `districts` runs first because a page or
a street hub names its historic district as a *link* only when that district's
hub is already on disk. `render` reads `shared/nearby.json`, so the link index
precedes it. `build_sitemap` walks the `index.html` files and reads each
district hub's buildings out of its HTML, so everything that writes a page
precedes it.

    python3 scripts/build_site.py              # build
    python3 scripts/build_site.py --serve      # build, then serve on :8517
    python3 scripts/build_site.py --no-build --stage _site   # copy out to publish

`--stage` is the deploy's last step (deploy.yml, netlify.toml): it copies the
working tree minus `.git` into a directory and stamps the stylesheet hash into
the committed pages on the way. Those pages are committed with an unhashed
link (seed_pages.CSS_SOURCE_LINK) so a CSS change touches no tracked file but
site.css itself; the published copy is the one that needs the cache-buster.

It also puts each neighborhood hub's overview (photo, boundary map, named
buildings) into the copy, and the homepage map over each hub that is one of
the city's Analysis Neighborhoods (seed_pages.map_into); `--serve` does the
same for each hub it sends.
The hubs are committed, and the overview shows every named building's photo,
so a committed overview went stale on any branch that touched a page — a
Know This Photo PR failed `validate` for it (#652). The overview is built
where the page leaves the tree instead, never in the working tree.

8517 is not arbitrary. The Mapbox token and the Google Maps embed key are
URL-restricted to `knowthis.place` and `http://localhost:8517`, so the maps
render on that port and on no other (shared/AGENTS.md).
"""
import argparse
import html
import json
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = Path(__file__).resolve().parent
CONTENT = ROOT / "san-francisco"
DISTRICTS = "historic-districts"
PORT = 8517


def neighborhoods() -> list:
    """Every neighborhood directory — the areas `hubs` takes one at a time.

    `historic-districts` is off the neighborhood tree and has its own command.
    """
    return sorted(d.name for d in CONTENT.iterdir()
                  if d.is_dir() and d.name != DISTRICTS)


def run(label: str, *args: str) -> None:
    """Run one builder, or stop the build where it broke."""
    started = time.monotonic()
    print(f"==> {label}", flush=True)
    result = subprocess.run([sys.executable, *args], cwd=ROOT)
    if result.returncode != 0:
        raise SystemExit(f"build_site: {label} failed "
                         f"(exit {result.returncode}) — nothing deployed")
    print(f"    {time.monotonic() - started:.1f}s", flush=True)


def build() -> None:
    seed = str(SCRIPTS / "seed_pages.py")

    # Districts first, and this is the subtle one. Which districts earned a hub
    # is a fact about the whole city, so `seed_pages._district_hubs` reads it
    # back off the directory tree — a page or a street hub names its district
    # as a link only when that hub is already on disk. Build the hubs after the
    # districts and 477 street hubs come out with the district named in plain
    # text instead.
    run("historic-district hubs", seed, "districts")
    for area in neighborhoods():
        run(f"hubs — {area}", seed, "hubs", "--city", "san-francisco",
            "--area", area)
    # The city page's map of every hub's boundary. Each hub's own overview is
    # not built here: `stage` and `serve` add it on the way out (see above).
    run("city neighborhoods map", seed, "city-map", "--city", "san-francisco")

    # Before the render: an address page prints its neighbors, and this is
    # where they come from.
    run("link index", str(SCRIPTS / "build_link_index.py"))
    run("address pages", seed, "render", "san-francisco")

    run("map index", str(SCRIPTS / "build_map_index.py"))
    run("events", str(SCRIPTS / "build_events.py"))
    run("sitemap", str(SCRIPTS / "build_sitemap.py"))
    run("corpus index", str(SCRIPTS / "build_corpus_index.py"))
    run("stats dashboard", str(SCRIPTS / "build_stats.py"))


SITE_NAME = "Know This Place"
TITLE_SUFFIX = " \u2014 " + SITE_NAME
# Shown on a link preview for a page with no photo of its own.
FALLBACK_IMAGE = "/shared/icon-512.png"
HEAD_TITLE = re.compile(r"<title>(.*?)</title>", re.S)
HEAD_DESC = re.compile(r'<meta name="description" content="([^"]*)">')
HEAD_CANONICAL = re.compile(r'([ \t]*)<link rel="canonical" href="([^"]*)">\n?')
BODY_IMG = re.compile(r'<img\b[^>]*?\bsrc="([^"]+)"[^>]*>')
IMG_ALT = re.compile(r'\balt="([^"]*)"')


def social_tags(text: str) -> str:
    """`text` with Open Graph and Twitter card tags, read off its own head.

    A link pasted into Reddit, Slack or iMessage shows its preview from these.
    They say nothing the page does not already say — its `<title>` less the
    site name, its meta description, its canonical URL, and the first described photo in
    its `<main>` (a building's hero, a hub's own photo) — so they are written where
    the page leaves the tree, like the stylesheet hash, rather than kept as a
    second copy in every template and committed hub. A page with no canonical
    URL (a redirect stub, a fragment) or that already carries them is left as
    it is.
    """
    if 'property="og:title"' in text or "</head>" not in text:
        return text
    head, body = text.split("</head>", 1)
    canon = HEAD_CANONICAL.search(head)
    title = HEAD_TITLE.search(head)
    if not canon or not title:
        return text
    indent, url = canon.group(1), canon.group(2)
    name = html.unescape(title.group(1).strip())
    if name.endswith(TITLE_SUFFIX):
        name = name[: -len(TITLE_SUFFIX)]
    desc = HEAD_DESC.search(head)
    from urllib.parse import urljoin
    image = alt = None
    # The page's own content only: the map laid over a hub or the homepage
    # carries the news cards' photos, which are other buildings.
    main = body[body.find("<main"):] if "<main" in body else body
    for m in BODY_IMG.finditer(main):
        src = html.unescape(m.group(1))
        a = IMG_ALT.search(m.group(0))
        # A photo of the page's subject: the site's own file, described. An
        # image with an empty alt is decoration (a list's thumbnails), and a
        # third-party one (a map tile, a badge) is not of the subject.
        if (not a or not a.group(1).strip()
                or re.match(r"[a-z][a-z0-9+.-]*:|//", src) or src.endswith(".svg")):
            continue
        image, alt = urljoin(url, src), html.unescape(a.group(1))
        break
    tags = [("og:type", "website"), ("og:site_name", SITE_NAME), ("og:title", name),
            ("og:url", url)]
    if desc:
        tags.append(("og:description", html.unescape(desc.group(1))))
    tags.append(("og:image", image or urljoin(url, FALLBACK_IMAGE)))
    if image and alt:
        tags.append(("og:image:alt", alt))
    tags.append(("twitter:card", "summary_large_image" if image else "summary"))
    lines = "".join(
        f'{indent}<meta {"name" if k.startswith("twitter:") else "property"}="{k}" '
        f'content="{html.escape(v, quote=True)}">\n' for k, v in tags)
    end = canon.end()
    if not canon.group(0).endswith("\n"):
        lines = "\n" + lines.rstrip("\n")
    return head[:end] + lines + head[end:] + "</head>" + body


def stage(dest: Path) -> None:
    """Copy the built site to `dest`, the committed pages stamped with the CSS
    hash and every page given its link-preview tags (`social_tags`)."""
    sys.path.insert(0, str(SCRIPTS))
    from seed_pages import (CSS_LINK, CSS_SOURCE_LINK, home_into, is_neighborhood_hub,
                            map_into, overview_into)

    started = time.monotonic()
    dest = dest.resolve()
    print(f"==> stage → {dest}", flush=True)
    if dest.exists():
        shutil.rmtree(dest)
    stamped = overviews = 0

    def copy(src, dst):
        nonlocal stamped, overviews
        if src.endswith(".html"):
            text = original = Path(src).read_text(encoding="utf-8")
            if Path(src).name == "index.html" and is_neighborhood_hub(Path(src).parent):
                text = map_into(overview_into(text, Path(src).parent), Path(src).parent)
                overviews += 1
            elif Path(src).resolve() == ROOT / "index.html":
                text = home_into(text)
            text = social_tags(text)
            if CSS_SOURCE_LINK in text:
                text = text.replace(CSS_SOURCE_LINK, CSS_LINK)
                stamped += 1
            if text != original:
                Path(dst).write_text(text, encoding="utf-8")
                shutil.copystat(src, dst)
                return dst
        return shutil.copy2(src, dst)

    def skip(directory, names):
        here = Path(directory).resolve()
        return [n for n in names
                if (here == ROOT and n == ".git") or here / n == dest]

    shutil.copytree(ROOT, dest, ignore=skip, copy_function=copy, symlinks=True)
    moved = write_redirects(dest)
    print(f"    {stamped} committed pages stamped with the stylesheet hash, "
          f"{overviews} neighborhood overview(s) added, "
          f"{moved} moved page(s) forwarded, "
          f"{time.monotonic() - started:.1f}s", flush=True)


REDIRECTS = CONTENT / "redirects.json"


def write_redirects(dest: Path) -> int:
    """A forwarding page at every URL in `redirects.json`, in the staged site.

    GitHub Pages has no server-side redirects, so a page that moves keeps its
    old URL working with a stub that sends the reader on. The stubs exist only
    in the deploy: they are not pages of the site, so nothing in the working
    tree (the contract, the sitemap, the link index) ever sees one.
    """
    if not REDIRECTS.exists():
        return 0
    moves = json.loads(REDIRECTS.read_text(encoding="utf-8"))
    for old, new in moves.items():
        stub = dest / old.strip("/") / "index.html"
        if stub.exists():
            continue
        stub.parent.mkdir(parents=True, exist_ok=True)
        url = html.escape(new)
        stub.write_text(
            "<!doctype html>\n<html lang=\"en\">\n<head>\n"
            "  <meta charset=\"utf-8\">\n"
            "  <title>Moved — Know This Place</title>\n"
            f"  <link rel=\"canonical\" href=\"https://knowthis.place{url}\">\n"
            "  <meta name=\"robots\" content=\"noindex\">\n"
            f"  <meta http-equiv=\"refresh\" content=\"0; url={url}\">\n"
            "</head>\n<body>\n"
            f"  <p>This page has moved to <a href=\"{url}\">{url}</a>.</p>\n"
            "</body>\n</html>\n", encoding="utf-8")
    return len(moves)


def serve(port: int) -> None:
    """Serve the built site the way a reader sees it."""
    import http.server
    import io
    import socketserver
    sys.path.insert(0, str(SCRIPTS))
    from seed_pages import home_into, is_neighborhood_hub, map_into, overview_into

    class Handler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *a, **kw):
            super().__init__(*a, directory=str(ROOT), **kw)

        # A neighborhood hub is served with its overview and the map, and the
        # homepage with the city's hub, as `stage` would publish them; the
        # files on disk never carry them.
        def send_head(self):
            path = Path(self.translate_path(self.path))
            page = path if path.is_dir() else path.parent
            is_page = ((path.is_dir() and self.path.split("?")[0].endswith("/"))
                       or path.name == "index.html")
            body = None
            if is_page and is_neighborhood_hub(page):
                body = map_into(overview_into((page / "index.html").read_text(encoding="utf-8"),
                                              page), page).encode("utf-8")
            elif is_page and page.resolve() == ROOT:
                body = home_into((ROOT / "index.html").read_text(encoding="utf-8")).encode("utf-8")
            if body is not None:
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                return io.BytesIO(body)
            return super().send_head()

        # The committed pages link site.css without a hash (`stage` adds it
        # for the deploy), so tell the browser to recheck it on every load.
        def end_headers(self):
            self.send_header("Cache-Control", "no-cache")
            super().end_headers()

        def log_message(self, fmt, *a):  # one line per request is enough
            sys.stderr.write(f"{self.requestline} {fmt % a}\n")

    socketserver.TCPServer.allow_reuse_address = True
    try:
        with socketserver.TCPServer(("127.0.0.1", port), Handler) as httpd:
            print(f"\nserving {ROOT} at http://localhost:{port}/  (ctrl-c to stop)")
            httpd.serve_forever()
    except OSError as e:
        raise SystemExit(
            f"build_site: can't listen on {port} ({e}). Something else is "
            f"already serving it — often a stale `http.server` rooted in "
            f"another worktree. The maps only work on this port, so free it "
            f"rather than choosing another.")
    except KeyboardInterrupt:
        print("\nstopped")


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--serve", action="store_true",
                    help=f"serve the result on localhost:{PORT} when the build finishes")
    ap.add_argument("--no-build", action="store_true",
                    help="skip the build and serve what is already on disk")
    ap.add_argument("--stage", type=Path, metavar="DIR",
                    help="after the build, copy the site into DIR for publishing, "
                         "the committed pages stamped with the stylesheet hash")
    ap.add_argument("--port", type=int, default=PORT,
                    help=f"port for --serve (default {PORT}; the map keys are "
                         f"restricted to it)")
    args = ap.parse_args()

    if not args.no_build:
        started = time.monotonic()
        build()
        print(f"\nbuilt in {time.monotonic() - started:.0f}s — "
              f"run `python3 scripts/validate.py` next")
    if args.stage:
        stage(args.stage)
    if args.serve:
        serve(args.port)
    return 0


if __name__ == "__main__":
    sys.exit(main())
