// Know This Place — the enhancement layer. The ONLY script.
//
// PROGRESSIVE ENHANCEMENT ONLY. Every custom element here wraps content that
// is ALREADY complete and readable in the page's HTML, and adds behavior on
// top. If this file never loads — a crawler, a reader with JS off, a slow
// network — every page still shows all of its content. Nothing here fetches,
// generates, or reveals page content; that would break the project's core
// goal of static, crawlable pages. Charts and icons remain CSS + SVG.
//
// No dependencies, no build. Loaded as a deferred module from the skeleton.
// Adding a component is a change to THIS file, reviewed by a human — never an
// inline <script> on a page. See shared/AGENTS.md.

// One memoized read of site-config for anything that needs it (the map key,
// the analytics site id).
let _config;
function siteConfig() {
  // no-store: this file gates behavior (the map key), so it must never read
  // a stale cached copy — imagery should switch on the day the key is set.
  return (_config ??= fetch("/shared/site-config.json", { cache: "no-store" })
    .then((r) => (r.ok ? r.json() : {}))
    .catch(() => ({})));
}

/* Analytics — aggregate page counts, loaded here rather than per page.

   This is the one third-party script on the site, and it lives here for the
   same reason everything else does: every page already loads this module, so
   adding it once covers every existing and future page with no regeneration,
   and turning it off is a one-line config change rather than a site-wide edit.
   It renders nothing and reads nothing from the page — pages are identical
   with it blocked.

   Fathom is cookieless and stores no per-visitor identifiers, which is what
   makes it acceptable under the project's privacy limits: we learn that a page
   was read, never who read it. Any analytics that profiles individuals would
   not belong here.

   Gated twice: on `fathom_site_id` being set, and on the page actually being
   served from the production host — so local previews and forks don't pollute
   the numbers. */
async function loadAnalytics() {
  const { fathom_site_id: siteId, site_url: siteUrl } = await siteConfig();
  if (!siteId || !siteUrl) return;

  let host;
  try {
    host = new URL(siteUrl).hostname;
  } catch {
    return;
  }
  if (location.hostname !== host) return; // localhost, forks, previews

  const script = document.createElement("script");
  script.src = "https://cdn.usefathom.com/script.js";
  script.dataset.site = siteId;
  script.defer = true;
  document.head.appendChild(script);
}
loadAnalytics();

/* <ktp-streetview location="LAT,LNG" label="123 Example St">
     <figure class="media"> …placeholder or fallback… </figure>
   </ktp-streetview>

   Google Street View, shown on page load. The light-DOM fallback (the
   .media-empty placeholder) is what shows with no JS or no configured key.
   When a Maps key IS configured, this swaps the placeholder for a static
   Street View image (Street View Static API). Imagery turns on site-wide the
   day the key is set, with no page regeneration.

   `source=outdoor` restricts the pick to Google's outdoor collections. The API
   otherwise returns the panorama *nearest* the coordinates, and on a dense
   downtown parcel that is regularly a business's indoor photosphere — a lobby,
   a stairwell, a shop counter — so the picture of the building turned out to
   be a picture of someone's foyer. Where a parcel has no outdoor panorama the
   API returns the generic grey "no imagery" tile instead of an interior; that
   is the better failure, since a page showing nothing is honest and a page
   showing the wrong room is not.

   A page with its own committed photo (seed_pages.facade_media) writes the
   <img> where the placeholder would be, so with no .media-empty to replace
   the element leaves the photo alone — on a card. In an address page's hero
   the photo is the first slide of a .media-track, and the placeholder waits
   in a second, `hidden` slide: there this fills it with Street View at the
   photo's shape, shows the slide once the image has loaded (a failed load
   leaves the photo alone, as with no key), and adds the dots and arrows. */
customElements.define(
  "ktp-streetview",
  class extends HTMLElement {
    async connectedCallback() {
      const empty = this.querySelector(".media-empty");
      const location = this.getAttribute("location");
      if (!empty || !location) return; // leave the fallback untouched

      const { maps_embed_key: key } = await siteConfig();
      if (!key) return; // no key yet → keep the placeholder as-is

      const label = this.getAttribute("label") || "this address";
      const slide = empty.closest(".media-slide");
      const photo = slide && this.querySelector(".media-slide img[width][height]");
      let size = "640x480";
      if (photo) {
        // The Static API's longest side is 640; match the photo's shape so
        // the slide doesn't crop a landscape still into a portrait frame.
        const w = +photo.getAttribute("width"), h = +photo.getAttribute("height");
        size = w >= h ? `640x${Math.round((640 * h) / w)}` : `${Math.round((640 * w) / h)}x640`;
      }
      const img = document.createElement("img");
      img.src =
        `https://maps.googleapis.com/maps/api/streetview?size=${size}&source=outdoor&location=` +
        encodeURIComponent(location) +
        "&key=" +
        encodeURIComponent(key);
      img.alt = "Street View of " + label;
      img.decoding = "async";
      if (slide) {
        // A hidden slide is never on screen, so a lazy image there would
        // never load; this one is fetched straight away and shown on load.
        img.addEventListener("load", () => {
          slide.hidden = false;
          carousel(this.querySelector(".media-carousel"));
        }, { once: true });
      } else {
        // A hub lists a dozen facades below the fold; an address page's one
        // is at the top, where lazy loading fetches it at once anyway.
        img.loading = "lazy";
      }
      empty.replaceWith(img);
    }
  },
);

/* The hero's slides, once there is more than one: small dots for where the
   reader is, and arrows for a pointer that can't swipe. Both are added here,
   never written into the page — the track scrolls and snaps on its own, so
   without them it still works. No autoplay. */
function carousel(frame) {
  const track = frame && frame.querySelector(".media-track");
  if (!track || frame.querySelector(".media-dots")) return;
  const slides = [...track.children].filter((s) => !s.hidden);
  const count = slides.length;
  if (count < 2) return;
  frame.setAttribute("role", "group");
  frame.setAttribute("aria-roledescription", "carousel");
  track.tabIndex = 0;
  const calm = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  const dots = document.createElement("div");
  dots.className = "media-dots";
  dots.setAttribute("aria-hidden", "true");
  for (let i = 0; i < count; i++) dots.append(document.createElement("span"));
  const current = () =>
    Math.max(0, Math.min(count - 1, Math.round(track.scrollLeft / track.clientWidth)));
  const go = (i) =>
    track.scrollTo({ left: i * track.clientWidth, behavior: calm ? "auto" : "smooth" });
  const step = (label, cls, by) => {
    const button = document.createElement("button");
    button.type = "button";
    button.className = "media-step " + cls;
    button.setAttribute("aria-label", label);
    button.textContent = by < 0 ? "\u2039" : "\u203a";
    button.addEventListener("click", () => go(current() + by));
    frame.append(button);
    return button;
  };
  const back = step("Show the photo", "media-step-back", -1);
  const on = step("Show Street View", "media-step-on", 1);
  frame.append(dots);
  const mark = () => {
    const at = current();
    [...dots.children].forEach((d, i) => d.classList.toggle("is-current", i === at));
    back.disabled = at === 0;
    on.disabled = at === count - 1;
  };
  let waiting = false;
  track.addEventListener("scroll", () => {
    if (waiting) return;
    waiting = true;
    requestAnimationFrame(() => { waiting = false; mark(); });
  }, { passive: true });
  mark();
}

/* The credit the hub map draws over its Mapbox image, in its top-right
   corner. On a phone the links fold behind an "i", as mapbox-gl's compact
   attribution does on the homepage; the CSS hides the button elsewhere. */
function mapCredit() {
  const credit = document.createElement("div");
  credit.className = "map-credit";
  credit.innerHTML =
    '<a class="map-credit-logo" href="https://www.mapbox.com/" aria-label="Mapbox"></a>' +
    '<span class="map-credit-text">' +
    '<a href="https://www.mapbox.com/about/maps/">© Mapbox</a> ' +
    '<a href="https://www.openstreetmap.org/copyright">© OpenStreetMap</a> ' +
    '<a href="https://www.mapbox.com/map-feedback/"><strong>Improve this map</strong></a>' +
    "</span>" +
    '<button class="map-credit-toggle" type="button" aria-expanded="false" aria-label="Map attribution">i</button>';
  const toggle = credit.querySelector(".map-credit-toggle");
  toggle.addEventListener("click", () => {
    const open = toggle.getAttribute("aria-expanded") !== "true";
    toggle.setAttribute("aria-expanded", String(open));
    credit.toggleAttribute("data-open", open);
  });
  return credit;
}

const PHONE = matchMedia("(max-width: 720px)");

/* <ktp-map location="LAT,LNG" label="123 Example St">
     <figure class="media media-map"> …placeholder… </figure>
   </ktp-map>

   The locator band: the blocks around this building, drawn from the city's
   own lines the way the homepage map draws them — the land, the street
   centrelines and their names, every lot, and the lots that have a page of
   their own in the map's two data hues, brick where research has published
   onto it, grey for permit history and little else. It is the homepage map
   held still: one fixed frame centred on the building, no panning and no
   zoom, so it needs only the few cells of build_map_index.py's grid that the
   frame covers (shared/map/near/<i>_<j>.json, ~440 m a side), and no map
   engine — the frame is a plain SVG, coloured in site.css from the tokens,
   so it follows the colour scheme on its own. Nothing here reaches past this
   site.

   A lot with a page is a link to it. A click opens the homepage's card for
   it (the page's photo or Street View, its heading and line, and "See this
   place"); a modified click goes straight there. The building's own lot is
   filled solid in brick and lifted on a paper halo (.nm-here).

   Same law as ever: the .media-empty placeholder is the whole content of the
   block with no JS, and stands if anything here fails. Nothing a reader needs
   is in the picture — the address is the <h1>, and the page's .nearby links
   carry the neighbours as text. */
const NEAR = "/shared/map/near/";
const NEAR_CELL = [0.005, 0.004];       // build_map_index.NEAR_CELL
const NEAR_ZOOM = 16.5;                  // MapLibre's 512px-tile zoom
const NEAR_WORLD = 512 * 2 ** NEAR_ZOOM;
const SVG_NS = "http://www.w3.org/2000/svg";
const mercX = (lng) => ((lng + 180) / 360) * NEAR_WORLD;
const mercY = (lat) => {
  const s = Math.sin((lat * Math.PI) / 180);
  return (0.5 - Math.log((1 + s) / (1 - s)) / (4 * Math.PI)) * NEAR_WORLD;
};
const unmercY = (y) =>
  (Math.atan(Math.sinh(Math.PI * (1 - (2 * y) / NEAR_WORLD))) * 180) / Math.PI;
const svgEl = (tag, attrs = {}) => {
  const n = document.createElementNS(SVG_NS, tag);
  for (const [k, v] of Object.entries(attrs)) n.setAttribute(k, v);
  return n;
};
/* The homepage map's card, for a lot here: built as nodes, never a string
   of HTML, from the text the cell file already carries. */
function nearCard(rec, lat, lng) {
  const card = document.createElement("article");
  card.className = "map-card";
  const sv = document.createElement("ktp-streetview");
  sv.setAttribute("location", `${lat.toFixed(5)},${lng.toFixed(5)}`);
  sv.setAttribute("label", rec.t);
  const fig = document.createElement("figure");
  fig.className = "media";
  if (rec.ph) {
    const img = document.createElement("img");
    img.src = rec.ph;
    img.alt = "Photo of " + rec.t;
    img.decoding = "async";
    fig.append(img);
  } else {
    const empty = document.createElement("div");
    empty.className = "media-empty";
    const pin = document.createElement("span");
    pin.className = "ic ic-pin";
    empty.append(pin);
    fig.append(empty);
  }
  sv.append(fig);
  const body = document.createElement("div");
  body.className = "map-card-body";
  const title = document.createElement("p");
  title.className = "map-card-title";
  title.textContent = rec.t;
  body.append(title);
  if (rec.s) {
    const sub = document.createElement("p");
    sub.className = "map-card-sub";
    sub.textContent = rec.s;
    body.append(sub);
  }
  const row = document.createElement("p");
  row.className = "map-card-links";
  const go = document.createElement("a");
  go.href = rec.p;
  go.textContent = "See this place";
  row.append(go);
  body.append(row);
  card.append(sv, body);
  return card;
}

customElements.define(
  "ktp-map",
  class extends HTMLElement {
    connectedCallback() {
      const empty = this.querySelector(".media-empty");
      const [lat, lng] = (this.getAttribute("location") || "").split(",").map(Number);
      if (!empty || !Number.isFinite(lat) || !Number.isFinite(lng)) return;
      this.cx = mercX(lng);
      this.cy = mercY(lat);
      this.label = this.getAttribute("label") || "this address";
      this.cells = new Map();     // "i_j" → Promise of the cell, or null
      this.land = [];
      this.lots = new Map();      // id → { z, d }
      this.streets = new Map();   // id → { n, c, pts }
      this.pages = new Map();     // lot id → the first page on it
      let queued = false;
      new ResizeObserver(() => {
        if (queued) return;
        queued = true;
        requestAnimationFrame(() => { queued = false; this.update().catch(() => {}); });
      }).observe(this);
    }

    /* Fetch whatever cells the frame now covers, then draw it. */
    async update() {
      const w = this.clientWidth, h = this.clientHeight;
      if (!w || !h) return;
      const pad = 40;   // a lot just off the edge still draws its sliver
      const west = ((this.cx - w / 2 - pad) / NEAR_WORLD) * 360 - 180;
      const east = ((this.cx + w / 2 + pad) / NEAR_WORLD) * 360 - 180;
      const north = unmercY(this.cy - h / 2 - pad);
      const south = unmercY(this.cy + h / 2 + pad);
      const [cw, ch] = NEAR_CELL;
      const wanted = [];
      for (let i = Math.floor(west / cw); i <= Math.floor(east / cw); i++) {
        for (let j = Math.floor(south / ch); j <= Math.floor(north / ch); j++) {
          wanted.push(`${i}_${j}`);
        }
      }
      await Promise.all(wanted.map((k) => this.cell(k)));
      if (![...this.cells.values()].some(Boolean)) return;   // nothing to draw: keep the placeholder
      this.draw(w, h);
    }

    cell(key) {
      if (!this.cells.has(key)) {
        this.cells.set(key, fetch(NEAR + key + ".json")
          .then((r) => (r.ok ? r.json() : null))
          .catch(() => null)
          .then((c) => { if (c) this.take(c); return c; }));
      }
      return this.cells.get(key);
    }

    /* A cell's packed lines (whole microdegrees off the cell's corner, then
       the step to each next point) projected straight to pixels off the
       frame's centre, deduped against the cells already read. */
    take(c) {
      const [ox, oy] = c.o;
      const pts = (flat) => {
        let x = flat[0] + ox, y = flat[1] + oy;
        const out = [[mercX(x / 1e6) - this.cx, mercY(y / 1e6) - this.cy]];
        for (let k = 2; k < flat.length; k += 2) {
          x += flat[k]; y += flat[k + 1];
          out.push([mercX(x / 1e6) - this.cx, mercY(y / 1e6) - this.cy]);
        }
        return out;
      };
      // Each shape keeps its box, so the frame draws only what it shows.
      let box;
      const grow = ([x, y]) => {
        box[0] = Math.min(box[0], x); box[1] = Math.min(box[1], y);
        box[2] = Math.max(box[2], x); box[3] = Math.max(box[3], y);
      };
      const ring = (flat) => {
        const p = pts(flat);
        p.forEach(grow);
        return "M" + p.map(([x, y]) => `${x.toFixed(1)} ${y.toFixed(1)}`).join("L") + "Z";
      };
      const area = (packed) => {
        box = [Infinity, Infinity, -Infinity, -Infinity];
        return packed.map((poly) => poly.map(ring).join("")).join("");
      };
      this.land.push(area(c.land));
      for (const [id, z, packed] of c.lots) {
        if (!this.lots.has(id)) this.lots.set(id, { z, d: area(packed), box });
      }
      for (const [id, n, cls, flat] of c.streets) {
        if (this.streets.has(id)) continue;
        box = [Infinity, Infinity, -Infinity, -Infinity];
        const p = pts(flat);
        p.forEach(grow);
        this.streets.set(id, { n, c: cls, pts: p, box });
      }
      for (const rec of c.pages) {
        if (!this.pages.has(rec.l)) this.pages.set(rec.l, rec);
      }
    }

    draw(w, h) {
      const here = location.pathname;
      const seen = ({ box: b }) => b[2] >= -w / 2 && b[0] <= w / 2 && b[3] >= -h / 2 && b[1] <= h / 2;
      const svg = svgEl("svg", {
        class: "near-map", viewBox: `${-w / 2} ${-h / 2} ${w} ${h}`,
        role: "img", "aria-label": "Map of the blocks around " + this.label,
      });
      svg.append(svgEl("path", { class: "nm-land", d: this.land.join("") }));
      const line = (p) => "M" + p.map(([x, y]) => `${x.toFixed(1)} ${y.toFixed(1)}`).join("L");
      const byClass = { 1: [], 2: [], 3: [] };
      for (const s of this.streets.values()) if (seen(s)) byClass[s.c <= 2 ? 1 : s.c === 3 ? 2 : 3].push(line(s.pts));
      for (const k of [3, 2, 1]) {
        svg.append(svgEl("path", { class: `nm-street nm-street-${k}`, d: byClass[k].join("") }));
      }
      const plain = [], park = [];
      for (const lot of this.lots.values()) if (seen(lot)) (lot.z === 1 ? park : plain).push(lot.d);
      svg.append(svgEl("path", { class: "nm-lots", d: plain.join("") }),
                 svgEl("path", { class: "nm-lots nm-park", d: park.join("") }));
      const pages = svgEl("g", { class: "nm-pages" });
      let hereLot = null;
      for (const [id, rec] of this.pages) {
        const lot = this.lots.get(id);
        if (!lot || !seen(lot)) continue;
        if (rec.p === here) {
          // Drawn last, over its neighbours: a paper halo, then the lot.
          hereLot = lot;
          continue;
        }
        const a = svgEl("a", { href: rec.p, class: rec.r ? "nm-page nm-r" : "nm-page", tabindex: "-1" });
        const title = svgEl("title");
        title.textContent = rec.t;
        a.append(title, svgEl("path", { d: lot.d }));
        a.addEventListener("click", (e) => {
          if (e.metaKey || e.ctrlKey || e.shiftKey || e.altKey || e.button) return;
          e.preventDefault();
          this.open(rec, a, e);
        });
        pages.append(a);
      }
      svg.append(pages);
      if (hereLot) {
        svg.append(svgEl("path", { class: "nm-here-halo", d: hereLot.d }),
                   svgEl("path", { class: "nm-here", d: hereLot.d }));
      }
      svg.append(this.labels(w, h));
      svg.addEventListener("click", (e) => { if (!e.target.closest("a")) this.close(); });

      const old = this.querySelector(".near-map, .media-empty");
      if (old) old.replaceWith(svg);
      // The building is its own lot, filled solid and lifted. Only a page
      // with no lot in the cache (a building on a retired parcel, say) falls
      // back to the homepage's resting dot at the centre.
      this.querySelector(".map-dot")?.remove();
      if (!hereLot) {
        const dot = document.createElement("span");
        dot.className = "map-dot";
        this.append(dot);
      }
    }

    /* Street names along their lines, as the homepage map sets them at street
       level: on the straighter blocks long enough to hold the name, read left
       to right, a name repeated no closer than 400px, never two touching. */
    labels(w, h) {
      const g = svgEl("g", { class: "nm-labels", "aria-hidden": "true" });
      const SIZE = 12, CHAR = SIZE * 0.56, EDGE = 12;
      const cands = [];
      for (const [id, s] of this.streets) {
        if (!s.n || !(s.box[2] >= -w / 2 && s.box[0] <= w / 2 && s.box[3] >= -h / 2 && s.box[1] <= h / 2)) continue;
        let p = s.pts;
        let len = 0;
        for (let k = 1; k < p.length; k++) len += Math.hypot(p[k][0] - p[k - 1][0], p[k][1] - p[k - 1][1]);
        const [a, b] = [p[0], p[p.length - 1]];
        const chord = Math.hypot(b[0] - a[0], b[1] - a[1]);
        const text = s.n.length * CHAR;
        if (len < text + 24 || chord < len * 0.9) continue;
        const mx = (a[0] + b[0]) / 2, my = (a[1] + b[1]) / 2;
        if (Math.abs(mx) > w / 2 - text / 2 - EDGE || Math.abs(my) > h / 2 - EDGE * 2) continue;
        if (b[0] < a[0]) p = [...p].reverse();
        // The label's box, the rotated text's extent, for the overlap test.
        const ux = Math.abs(b[0] - a[0]) / chord, uy = Math.abs(b[1] - a[1]) / chord;
        const hw = (text * ux + SIZE * uy) / 2 + 4, hh = (text * uy + SIZE * ux) / 2 + 4;
        cands.push({ id, n: s.n, c: s.c, len, p, mx, my, hw, hh });
      }
      cands.sort((x, y) => x.c - y.c || y.len - x.len);
      const placed = [];
      for (const c of cands) {
        if (placed.some((o) => (o.n === c.n && Math.hypot(o.mx - c.mx, o.my - c.my) < 400) ||
            (Math.abs(o.mx - c.mx) < o.hw + c.hw && Math.abs(o.my - c.my) < o.hh + c.hh))) continue;
        placed.push(c);
        const pid = `nm-l-${this.idBase ??= Math.random().toString(36).slice(2, 8)}-${c.id}`;
        g.append(svgEl("path", { id: pid, d: "M" + c.p.map(([x, y]) => `${x.toFixed(1)} ${y.toFixed(1)}`).join("L"), fill: "none" }));
        const t = svgEl("text", { dy: "0.35em" });
        const tp = svgEl("textPath", { href: "#" + pid, startOffset: "50%", "text-anchor": "middle" });
        tp.textContent = c.n;
        t.append(tp);
        g.append(t);
      }
      return g;
    }

    /* The card, opened beside the tap and kept inside the band where it fits;
       on a short phone band it may hang below, over the page. */
    open(rec, a, e) {
      this.close();
      const box = this.getBoundingClientRect();
      const x = e.clientX - box.left, y = e.clientY - box.top;
      const lat = unmercY(this.cy + y - box.height / 2);
      const lng = ((this.cx + x - box.width / 2) / NEAR_WORLD) * 360 - 180;
      const pop = document.createElement("div");
      pop.className = "near-pop";
      const close = document.createElement("button");
      close.type = "button";
      close.className = "near-pop-close";
      close.setAttribute("aria-label", "Close");
      close.textContent = "×";
      close.addEventListener("click", () => this.close());
      pop.append(nearCard(rec, lat, lng), close);
      this.append(pop);
      const pw = pop.offsetWidth, ph = pop.offsetHeight, gap = 14;
      pop.style.left = `${Math.max(8, Math.min(box.width - pw - 8, x - pw / 2))}px`;
      const below = y + gap + ph <= box.height || y - gap - ph < 8;
      pop.style.top = `${below ? y + gap : y - gap - ph}px`;
      a.classList.add("is-active");
      this.active = a;
      this.onKey ??= (k) => { if (k.key === "Escape") this.close(); };
      addEventListener("keydown", this.onKey);
      pop.querySelector(".map-card-links a")?.focus({ preventScroll: true });
    }

    close() {
      this.querySelector(".near-pop")?.remove();
      this.active?.classList.remove("is-active");
      this.active = null;
      if (this.onKey) removeEventListener("keydown", this.onKey);
    }
  },
);

/* <ktp-areamap center="LNG,LAT" zoom="13.42" size="1280x800" label="Map of Marina">
     <figure class="area-map"><div class="area-map-frame"><svg>…</svg> …</div></figure>
   </ktp-areamap>

   A neighborhood hub's map. The page already holds the whole of it as inline
   SVG — the official boundary and a dot for every documented page inside it,
   projected by seed_pages.py onto the frame a Mapbox static image of this
   centre, zoom and size would cover — so this only slides that image under the
   SVG, once `mapbox_token` is set. Nothing in the picture is content.

   On a phone it asks for half the size at one zoom level less: the same
   ground, with the basemap's labels drawn at a size that survives the
   narrower frame. */
customElements.define(
  "ktp-areamap",
  class extends HTMLElement {
    async connectedCallback() {
      const frame = this.querySelector(".area-map-frame");
      const [lng, lat] = (this.getAttribute("center") || "").split(",").map(Number);
      const zoom = Number(this.getAttribute("zoom"));
      const [w, h] = (this.getAttribute("size") || "").split("x").map(Number);
      if (!frame || ![lng, lat, zoom, w, h].every(Number.isFinite)) return;

      const { mapbox_token: token } = await siteConfig();
      if (!token) return; // no token yet → the SVG alone

      const dark = matchMedia("(prefers-color-scheme: dark)");
      const src = () => {
        const half = PHONE.matches;
        return (
          "https://api.mapbox.com/styles/v1/mapbox/" +
          (dark.matches ? "dark-v11" : "light-v11") +
          `/static/${lng},${lat},${half ? zoom - 1 : zoom},0/` +
          (half ? `${Math.round(w / 2)}x${Math.round(h / 2)}` : `${w}x${h}`) +
          "@2x?attribution=false&logo=false&access_token=" +
          encodeURIComponent(token)
        );
      };
      const img = document.createElement("img");
      img.alt = "";
      img.decoding = "async";
      img.loading = "lazy";
      img.addEventListener("load", () => {
        this.querySelector(".area-map")?.setAttribute("data-basemap", "");
      }, { once: true });
      img.src = src();
      frame.prepend(img);
      frame.append(mapCredit());

      dark.addEventListener("change", () => (img.src = src()));
      PHONE.addEventListener("change", () => (img.src = src()));
    }
  },
);

/* <ktp-copy class="offer-code">
     <span class="offer-code-claim">Get 100 points at Insomnia Cookies</span>
     <code>Stanft6246</code>
   </ktp-copy>

   A string the reader has to carry somewhere else — a referral code a merchant
   makes you type in yourself — with the whole box as the copy target.

   The code is already the element's own text, so this reveals nothing: with no
   JS the box still prints it, and `user-select: all` still hands it over in one
   click. Everything that promises a click — the role, the copy icon, the
   pointer and hover that hang off the role in site.css — is added here rather
   than rendered into the page, so a reader whose script never ran is never
   shown an affordance that cannot work.

   role="button" on a plain element is not a <button>: it takes its own
   tabindex, and Enter and Space have to be wired by hand.

   The clipboard can refuse (an insecure origin, a permission the browser will
   not grant, a reader who has denied it). There is nothing to fall back to and
   nothing worth an alert, so the box selects the code instead and says so,
   which is where it started. */
customElements.define(
  "ktp-copy",
  class extends HTMLElement {
    connectedCallback() {
      const code = this.querySelector("code");
      if (!code || !navigator.clipboard) return; // nothing to copy, or no way to

      const icon = document.createElement("span");
      icon.className = "ic ic-copy";
      this.appendChild(icon);

      // role="status" so the outcome is announced, not only shown.
      const said = document.createElement("span");
      said.className = "visually-hidden";
      said.setAttribute("role", "status");
      this.appendChild(said);

      this.setAttribute("role", "button");
      this.tabIndex = 0;
      this.setAttribute("aria-label", `Copy the referral code ${code.textContent.trim()}`);

      let revert;
      const copy = async () => {
        let spoken;
        try {
          await navigator.clipboard.writeText(code.textContent.trim());
          spoken = "Referral code copied to the clipboard.";
          icon.className = "ic ic-check";
          this.dataset.copied = "";
        } catch {
          // Selecting it is the whole of the fallback: the reader copies it
          // with their own keyboard, as they would have without the icon.
          getSelection()?.selectAllChildren(code);
          spoken = "Could not reach the clipboard. The code is selected — copy it yourself.";
          delete this.dataset.copied;
        }
        said.textContent = spoken;
        clearTimeout(revert);
        revert = setTimeout(() => {
          icon.className = "ic ic-copy";
          said.textContent = "";
          delete this.dataset.copied;
        }, 2500);
      };

      this.addEventListener("click", copy);
      this.addEventListener("keydown", (e) => {
        if (e.key !== "Enter" && e.key !== " ") return;
        e.preventDefault(); // Space would scroll the page
        copy();
      });
    }
  },
);

/* <ktp-figure> … a chart whose marks carry data-tip="…" … </ktp-figure>

   Adds the hover/focus tooltip layer to any chart. Marks that carry a
   `data-tip` attribute (e.g. stacked-bar segments) become keyboard-focusable
   and show their exact value on hover or focus. The values already exist in
   the page (labels, legend, aria-label); this only surfaces them at the mark.
   With no JS the chart and its legend read exactly the same, minus the
   pop-up. */
customElements.define(
  "ktp-figure",
  class extends HTMLElement {
    connectedCallback() {
      const marks = this.querySelectorAll("[data-tip]");
      if (!marks.length) return;

      const tip = document.createElement("div");
      tip.className = "ktp-tip";
      tip.setAttribute("role", "status");
      tip.hidden = true;
      this.appendChild(tip);

      const show = (mark) => {
        tip.textContent = mark.getAttribute("data-tip");
        tip.hidden = false;
        const box = this.getBoundingClientRect();
        const m = mark.getBoundingClientRect();
        tip.style.left = m.left - box.left + m.width / 2 + "px";
        tip.style.top = m.top - box.top + "px";
      };
      const hide = () => (tip.hidden = true);

      marks.forEach((mark) => {
        if (!mark.hasAttribute("tabindex")) mark.tabIndex = 0;
        mark.addEventListener("pointerenter", () => show(mark));
        mark.addEventListener("pointerleave", hide);
        mark.addEventListener("focus", () => show(mark));
        mark.addEventListener("blur", hide);
      });
    }
  },
);
