#!/usr/bin/env python3
"""Build the whole site from the tracked sources. Stdlib only.

Every `index.html` on this site, plus `sitemap.xml`, `sitemaps/`,
`shared/addresses.geojson`, `shared/nearby.json`, `corpus.jsonl` and `/stats/`,
is derived from `data.json` and the hub `index.md` files. None of it is
committed — the repository holds the sources, and this script turns them into
the site, in Actions before a deploy and on a laptop before a look.

It is the seven builders in the one order that works, and the order is the
whole reason it exists:

    districts → hubs → overviews → build_link_index → render → build_map_index
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

8517 is not arbitrary. The Mapbox token and the Google Maps embed key are
URL-restricted to `knowthis.place` and `http://localhost:8517`, so the maps
render on that port and on no other (shared/AGENTS.md).
"""
import argparse
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
    # Each hub's photo, boundary map and named buildings. One pass for every
    # hub: the map of a boundary shows every page inside it, wherever that
    # page is filed, so it reads the whole city once rather than per area.
    run("neighborhood overviews", seed, "overviews", "--city", "san-francisco")

    # Before the render: an address page prints its neighbors, and this is
    # where they come from.
    run("link index", str(SCRIPTS / "build_link_index.py"))
    run("address pages", seed, "render", "san-francisco")

    run("map index", str(SCRIPTS / "build_map_index.py"))
    run("events", str(SCRIPTS / "build_events.py"))
    run("sitemap", str(SCRIPTS / "build_sitemap.py"))
    run("corpus index", str(SCRIPTS / "build_corpus_index.py"))
    run("stats dashboard", str(SCRIPTS / "build_stats.py"))


def stage(dest: Path) -> None:
    """Copy the built site to `dest`, the committed pages stamped with the CSS hash."""
    sys.path.insert(0, str(SCRIPTS))
    from seed_pages import CSS_LINK, CSS_SOURCE_LINK

    started = time.monotonic()
    dest = dest.resolve()
    print(f"==> stage → {dest}", flush=True)
    if dest.exists():
        shutil.rmtree(dest)
    stamped = 0

    def copy(src, dst):
        nonlocal stamped
        if src.endswith(".html"):
            text = Path(src).read_text(encoding="utf-8")
            if CSS_SOURCE_LINK in text:
                Path(dst).write_text(text.replace(CSS_SOURCE_LINK, CSS_LINK),
                                     encoding="utf-8")
                shutil.copystat(src, dst)
                stamped += 1
                return dst
        return shutil.copy2(src, dst)

    def skip(directory, names):
        here = Path(directory).resolve()
        return [n for n in names
                if (here == ROOT and n == ".git") or here / n == dest]

    shutil.copytree(ROOT, dest, ignore=skip, copy_function=copy, symlinks=True)
    print(f"    {stamped} committed pages stamped with the stylesheet hash, "
          f"{time.monotonic() - started:.1f}s", flush=True)


def serve(port: int) -> None:
    """Serve the built site the way a reader sees it."""
    import http.server
    import socketserver

    class Handler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *a, **kw):
            super().__init__(*a, directory=str(ROOT), **kw)

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
