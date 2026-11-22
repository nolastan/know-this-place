#!/usr/bin/env python3
"""Cut each neighborhood hub's photo down to the thumbnail the city page lists
it with: `<hub>/assets/thumb.jpg`, 3:2, 240×160 (a 7.5rem-wide tile at 2x),
JPEG quality 72, EXIF stripped.

Run it after adding or replacing a hub's photo, and commit the thumbnail with
it; `validate.py` fails a hub photo that has none. It is the one script the
build does not run, because it needs Pillow (`pip install pillow`) and the
build is stdlib only: the thumbnails are committed, like the photos.

    python3 scripts/hub_thumbs.py            # every hub missing a thumbnail
    python3 scripts/hub_thumbs.py --all      # every hub, overwriting
"""
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))
from seed_pages import HUB_THUMB, HUB_THUMB_SIZE  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--city", default="san-francisco")
    ap.add_argument("--all", action="store_true", help="rewrite thumbnails that exist")
    args = ap.parse_args()
    try:
        from PIL import Image, ImageOps
    except ImportError:
        raise SystemExit("hub_thumbs.py needs Pillow: pip install pillow")
    w, h = HUB_THUMB_SIZE
    made = 0
    for hub_json in sorted((ROOT / args.city).glob("*/hub.json")):
        photo = json.loads(hub_json.read_text(encoding="utf-8")).get("photo")
        src = hub_json.parent / photo["file"] if photo else None
        if not src or not src.exists():
            continue
        dest = hub_json.parent / HUB_THUMB
        if dest.exists() and not args.all:
            continue
        with Image.open(src) as im:
            im = ImageOps.exif_transpose(im).convert("RGB")
            im = ImageOps.fit(im, (w, h), Image.LANCZOS)
            dest.parent.mkdir(parents=True, exist_ok=True)
            im.save(dest, "JPEG", quality=72, optimize=True, progressive=True)
        made += 1
        print(f"  {dest.relative_to(ROOT)}")
    print(f"wrote {made} hub thumbnail(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
