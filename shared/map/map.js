/* The homepage map. San Francisco drawn from its own lines, with no basemap
   service: the land, the street centrelines and their names, and the city's
   41 Analysis Neighborhoods, from the lot cache seed_pages.py commits under
   shared/map/. The city opens with only the news and events on it — the
   news layer, the dozen addresses in the grid below, in the cool data hue,
   and the events layer, the next six days of public-space events in the
   violet --event hue, read from shared/events.geojson. A click on a
   neighborhood flies to its boundary, veils the rest of the city, and fetches
   that one neighborhood's lots (shared/map/lots/<slug>.json) and which of
   them have a page (shared/map/pages/<slug>.json, from build_map_index.py);
   a documented lot opens its card. A click on water, or anywhere outside
   every neighborhood, puts the city back.

   If anything here fails — blocked CDN, no WebGL — the placeholder in #map
   stands and the links below it still reach every page. */
const shell = document.getElementById("map");
const placeholder = document.querySelector(".map-shell .media-empty");
const MAP = "/shared/map/";
const HOME = [[-122.5105, 37.7395], [-122.3937, 37.8095]];

/* A page the research module has published a finding onto ("r" in the index)
   wears the site's brick hue; the rest, pages that are permit history and
   little else, wear the muted grey. Both are read live from site.css so light
   and dark mode stay in step and no new color enters the system. */
const cssVar = (name) =>
  getComputedStyle(document.documentElement).getPropertyValue(name).trim();

/* A dot under the pointer, or the one whose card is open, draws larger, fully
   opaque and ringed, so the reader can see which dot a click will open. MapLibre
   only accepts ["zoom"] at the top level of an interpolate, so the state is
   read inside each stop rather than wrapped around the curve. */
const LIT = ["any", ["boolean", ["feature-state", "hover"], false],
                    ["boolean", ["feature-state", "active"], false]];
const lit = (on, off) => ["case", LIT, on, off];

/* ---- the basemap: ours, so it wears the site's own tokens ---------------- */

/* Packed coordinates (seed_pages.py → "The homepage map's lot cache"): whole
   microdegrees, a ring's first point off the file's origin and then the step
   to each next point, closing point dropped. */
const unpack = (flat, [ox, oy], close) => {
  let x = flat[0] + ox, y = flat[1] + oy;
  const pts = [[x / 1e6, y / 1e6]];
  for (let i = 2; i < flat.length; i += 2) {
    x += flat[i]; y += flat[i + 1];
    pts.push([x / 1e6, y / 1e6]);
  }
  if (close) pts.push(pts[0]);
  return pts;
};
const polygons = (packed, o) =>
  ({ type: "MultiPolygon", coordinates: packed.map((p) => p.map((r) => unpack(r, o, true))) });
const collection = (features) => ({ type: "FeatureCollection", features });
const EMPTY = collection([]);

/* Colours the site has no token for — the street, the water, parkland, the
   veil over the city a reader has stepped past — mixed from the tokens it has,
   so a scheme change carries them along. Mixed here in sRGB rather than with
   CSS color-mix(), whose computed value (oklab) the map can't read. */
const rgbOf = (() => {
  const probe = document.createElement("span");
  return (name) => {
    probe.style.color = `var(${name})`;
    document.body.append(probe);
    const m = getComputedStyle(probe).color.match(/[\d.]+/g).map(Number);
    probe.remove();
    return m.slice(0, 3);
  };
})();
const mix = (a, b, pct) =>
  `rgb(${a.map((v, i) => Math.round((v * pct + b[i] * (100 - pct)) / 100)).join(",")})`;
const palette = () => {
  const [paper, ink, rule, cool, muted, ok] =
    ["--paper", "--ink", "--rule", "--cool", "--muted", "--ok"].map(rgbOf);
  return {
    water: mix(cool, paper, 16),
    ground: mix(rule, paper, 55),
    street: mix(paper, rule, 75),
    lot: mix(paper, paper, 100),
    lotLine: mix(rule, ink, 85),
    park: mix(ok, paper, 16),
    area: mix(rule, paper, 90),
    veil: mix(paper, paper, 100),
    label: mix(muted, muted, 100),
    halo: mix(paper, paper, 100),
    warm: cssVar("--warm"), muted: cssVar("--muted"),
  };
};
/* Self-hosted glyphs (shared/map/fonts/, Noto Sans, OFL), so the map reaches
   nothing but this site. */
const FONT = ["Noto Sans Regular"];

const ownStyle = (data) => {
  const P = palette();
  const picked = ["boolean", ["feature-state", "picked"], false];
  const hover = ["boolean", ["feature-state", "hover"], false];
  return {
    version: 8,
    glyphs: location.origin + MAP + "fonts/{fontstack}/{range}.pbf",
    sources: {
      land: { type: "geojson", data: data.land },
      streets: { type: "geojson", data: data.streets, tolerance: 0.3 },
      areas: { type: "geojson", data: data.areas, promoteId: "slug" },
      lots: { type: "geojson", data: EMPTY, tolerance: 0.2 },
      pages: { type: "geojson", data: EMPTY, promoteId: "p", tolerance: 0.2 },
    },
    layers: [
      { id: "water", type: "background", paint: { "background-color": P.water } },
      { id: "land", type: "fill", source: "land", paint: { "fill-color": P.ground } },
      { id: "street-lines", type: "line", source: "streets",
        layout: { "line-cap": "round", "line-join": "round" },
        paint: { "line-color": P.street,
          "line-width": ["interpolate", ["linear"], ["zoom"],
            10, ["match", ["get", "c"], [1, 2], 1.6, 3, 1, 0.3],
            13, ["match", ["get", "c"], [1, 2], 4, 3, 2.5, 1],
            16, ["match", ["get", "c"], [1, 2], 10, 3, 8, 5]] } },
      // A neighborhood tints under the pointer: the invitation to click it.
      { id: "area-fill", type: "fill", source: "areas",
        paint: { "fill-color": P.area, "fill-opacity": ["case", hover, 0.8, 0] } },
      // The picked neighborhood's lots. Where lots meet, the gap between
      // blocks is the street, so the grid draws itself at street level.
      { id: "lots", type: "fill", source: "lots",
        paint: { "fill-color": ["case", ["==", ["get", "z"], 1], P.park, P.lot] } },
      { id: "lot-lines", type: "line", source: "lots",
        paint: { "line-color": P.lotLine,
          "line-width": ["interpolate", ["linear"], ["zoom"], 13, 0.15, 15, 0.4, 18, 1] } },
      // A lot with a page wears the map's two data hues: brick where research
      // has published onto it, grey for permit history and little else.
      { id: "page-fill", type: "fill", source: "pages",
        paint: { "fill-color": ["case", ["has", "r"], P.warm, P.muted],
          "fill-opacity": ["case", hover, 0.9, ["has", "r"], 0.6, 0.3] } },
      { id: "page-line", type: "line", source: "pages",
        paint: { "line-color": ["case", ["has", "r"], P.warm, P.muted],
          "line-width": ["interpolate", ["linear"], ["zoom"], 13, 0.3, 16, ["case", hover, 2.5, 1]],
          "line-opacity": 0.9 } },
      // Once one is picked, the rest of the city steps back behind a veil.
      { id: "veil", type: "fill", source: "areas", filter: ["==", ["get", "slug"], ""],
        paint: { "fill-color": P.veil, "fill-opacity": 0.72 } },
      { id: "area-line", type: "line", source: "areas",
        paint: { "line-color": P.label,
          "line-width": ["case", picked, 2.5, hover, 1.5, 0.6],
          "line-opacity": ["case", picked, 0.9, 0.55] } },
      { id: "street-labels", type: "symbol", source: "streets", minzoom: 14,
        filter: ["any", ["<=", ["get", "c"], 3], [">=", ["zoom"], 15.5]],
        layout: { "text-field": ["get", "n"], "text-font": FONT, "symbol-placement": "line",
                  "symbol-spacing": 400,
                  "text-size": ["interpolate", ["linear"], ["zoom"], 14, 10, 18, 13] },
        paint: { "text-color": P.label, "text-halo-color": P.halo, "text-halo-width": 1.5 } },
      { id: "area-labels", type: "symbol", source: "areas", maxzoom: 14,
        layout: { "text-field": ["get", "name"], "text-font": FONT, "text-size": 11,
                  "text-transform": "uppercase", "text-letter-spacing": 0.08,
                  "text-max-width": 7 },
        paint: { "text-color": P.label, "text-halo-color": P.halo, "text-halo-width": 1.2 } },
    ],
  };
};

/* The basemap's three files, read once and kept: a scheme change rebuilds the
   style from them without fetching again. "no-cache" revalidates (one 304 on
   a repeat visit) so a refreshed cache is never served stale. */
const getJSON = async (url) => (await fetch(url, { cache: "no-cache" })).json();
async function loadBase() {
  const [areas, index, streets] = await Promise.all(
    ["areas.json", "index.json", "streets.json"].map((f) => getJSON(MAP + f)));
  const about = new Map(index.map((a) => [a.slug, a]));
  const areaFeatures = areas.areas.map((a) => ({
    type: "Feature", geometry: polygons(a.g, areas.o),
    properties: { slug: a.slug, name: a.name, ...(about.get(a.slug) ?? {}) },
  }));
  return {
    areas: collection(areaFeatures),
    // The land is the neighborhoods themselves: together they are the city.
    land: collection(areaFeatures.map((f) => ({ ...f, properties: {} }))),
    streets: collection(streets.s.map(([n, c, flat]) => ({
      type: "Feature", geometry: { type: "LineString", coordinates: unpack(flat, streets.o) },
      properties: { n: streets.names[n], c },
    }))),
  };
}
/* The addresses in the news, read out of the grid below rather than from a
   second data file. The cards are already the list of what the news module
   published, so taking the map's news layer from the same markup means the two
   cannot drift: a run that adds a card adds a dot, and one that drops a card
   drops it. Everything the card adds is text that is already on the page.
   Coordinates come off <ktp-streetview location="LAT,LNG">, which the card
   copies verbatim from the page's own data.json. */
const newsFeatures = (root = document) =>
  [...root.querySelectorAll(".news-cards > li")].flatMap((li, i) => {
    const sv = li.querySelector("ktp-streetview");
    const [lat, lng] = (sv?.getAttribute("location") ?? "").split(",").map(Number);
    if (!Number.isFinite(lat) || !Number.isFinite(lng)) return [];
    return [{
      type: "Feature",
      geometry: { type: "Point", coordinates: [lng, lat] },
      properties: {
        t: sv.getAttribute("label") ?? "",
        p: li.querySelector(".card-label")?.closest("a")?.getAttribute("href") ?? "",
        h: li.querySelector(".card-news em")?.textContent ?? "",
        o: li.querySelector(".card-outlet")?.textContent.trim() ?? "",
        u: li.querySelector(".card-outlet")?.getAttribute("href") ?? "",
        // Where this dot sits in the pulse cycle, 0 → 1. Stepping by the golden
        // ratio spreads any number of dots evenly with no two neighbours in the
        // grid firing together, so the rings take turns instead of beating as one.
        ph: (i * 0.618034) % 1,
      },
    }];
  });

const PULSE_MS = 2000;
const PULSE_MAX = 4;
const REDUCED_MOTION = matchMedia("(prefers-reduced-motion: reduce)").matches;

/* News dots are the cool half of the site's warm/cool data pair, against the
   brick of every other address — two hues that are already validated together,
   rather than a new color invented for the map. They are also drawn a size
   larger, because color alone would not find a dozen dots in eight thousand at
   city zoom. Event dots take the third data hue (--event violet): a color a
   reader can tell apart from both brick and blue even without hue vision. */
/* scale may be a number or a data expression; either way it sits inside the
   stops, where MapLibre allows it. */
const newsRadius = (scale) => ["interpolate", ["linear"], ["zoom"],
  // Scaled stop by stop: MapLibre only accepts ["zoom"] at the top level of an
  // interpolate, so ["*", scale, interpolate] is rejected and the layer is lost.
  ...[[10, 2.6], [12, 3.4], [14, 5], [16, 8], [18, 11]].flatMap(([z, r]) => [z, ["*", r, scale]])];

/* One pulsing layer pair per data hue — news and events share the geometry
   and the animation, and differ only in the token they draw with. `prefix`
   is both the GeoJSON source name and the layer prefix. */
const pulseLayers = (prefix, color) => [
  /* The halo. Its radius and opacity are driven frame by frame below; the
     values here are the resting state, which is also what a reader who has
     asked for reduced motion sees — a soft ring that never moves. */
  {
    id: `${prefix}-pulse`,
    type: "circle",
    source: prefix,
    paint: {
      "circle-color": cssVar(color),
      "circle-radius": newsRadius(PULSE_MAX),
      "circle-opacity": REDUCED_MOTION ? 0.14 : 0,
    },
  },
  {
    id: `${prefix}-dot`,
    type: "circle",
    source: prefix,
    paint: {
      "circle-color": cssVar(color),
      "circle-radius": newsRadius(lit(1.4, 1)),
      "circle-opacity": lit(1, 0.95),
      "circle-stroke-color": cssVar("--paper"),
      "circle-stroke-width": ["interpolate", ["linear"], ["zoom"],
        12, lit(1.5, 0.6), 16, lit(2.5, 1.5)],
    },
  },
];

/* Events come from shared/events.geojson — the build's second file alongside
   addresses.geojson, written by scripts/build_events.py out of the module's
   committed events.json. Unlike the news layer this one can't read its data
   off the page (there is no events grid), so the file carries the listing:
   the title, the venue, the when, the calendar's name, and "p", the page of
   the park, plaza or building it is at. An event with no page has no dot —
   build_events.py leaves it out, and it lists on /events only. The six-day window is applied here, off "d", so a
   stale build fades rather than being wrong. One dot per spot: a venue with
   five events this week is still one place, so only the soonest listing at
   each coordinate draws — the rest still list on /events. */
const EVENT_DAYS = 6;
const eventFeatures = (collection) => {
  const today = new Date(); today.setHours(0, 0, 0, 0);
  const horizon = today.getTime() + (EVENT_DAYS + 1) * 86400e3;
  const bySpot = new Map();
  for (const f of collection.features) {
    const d = new Date(f.properties.d).getTime();
    if (d < today.getTime() || d >= horizon) continue;
    const key = f.geometry.coordinates.join(",");
    const prev = bySpot.get(key);
    if (!prev || f.properties.d < prev.properties.d) bySpot.set(key, f);
  }
  let i = 0;
  return [...bySpot.values()].map((f) => ({
    ...f,
    properties: { ...f.properties, ph: (i++ * 0.618034) % 1 },
  }));
};

/* One ring per dot every two seconds, each dot on its own beat, growing to four
   times the dot and fading as it grows. MapLibre has no animated paint, so the halo is repainted per frame —
   cheap at a dozen features, and parked whenever the map is off-screen or the
   tab is hidden rather than repainting the city under the fold. */
function pulse(map) {
  if (REDUCED_MOTION) return;
  let running = false, frame = 0;
  const tick = (now) => {
    if (!running) return;
    for (const prefix of ["news", "events"]) {
      if (!map.getLayer(`${prefix}-pulse`)) continue;
      const t = (now % PULSE_MS) / PULSE_MS;          // 0 → 1, once a cycle
      const k = ["%", ["+", t, ["get", "ph"]], 1];    // this dot's own place in it
      map.setPaintProperty(`${prefix}-pulse`, "circle-radius",
        newsRadius(["+", 1, ["*", PULSE_MAX - 1, k]]));
      // Bright at the dot and fading as it grows, so the ring dissolves at its
      // widest rather than snapping back — but slowly enough that it is still
      // plainly visible halfway out, at city zoom among eight thousand dots.
      map.setPaintProperty(`${prefix}-pulse`, "circle-opacity",
        ["*", 0.6, ["^", ["-", 1, k], 1.1]]);
    }
    frame = requestAnimationFrame(tick);
  };
  const run = (on) => {
    if (on === running) return;
    running = on;
    if (on) frame = requestAnimationFrame(tick);
    else {
      cancelAnimationFrame(frame);
      for (const prefix of ["news", "events"]) {
        if (map.getLayer(`${prefix}-pulse`))
          map.setPaintProperty(`${prefix}-pulse`, "circle-opacity", 0);
      }
    }
  };
  let onScreen = true;
  const sync = () => run(onScreen && !document.hidden);
  new IntersectionObserver(([e]) => { onScreen = e.isIntersecting; sync(); })
    .observe(document.querySelector(".map-shell"));
  document.addEventListener("visibilitychange", sync);
  sync();
}

/* An event's day. It is worked out here, off "d", in
   San Francisco's time zone — like the six-day window, so a build a day old
   never calls yesterday "Today". The window never reaches the same weekday
   twice, so a bare weekday ("Tuesday") is never ambiguous and needs no date. */
const SF_TZ = "America/Los_Angeles";
const sfDate = (t) => new Intl.DateTimeFormat("en-CA", { timeZone: SF_TZ }).format(t);
const DAY_FMT = new Intl.DateTimeFormat("en-US", { weekday: "long", timeZone: SF_TZ });
const eventDay = (iso) => {
  const day = iso.slice(0, 10);
  if (day === sfDate(Date.now())) return "Today";
  if (day === sfDate(Date.now() + 86400e3)) return "Tomorrow";
  return DAY_FMT.format(new Date(iso));
};
const el = (tag, cls, text) => {
  const n = document.createElement(tag);
  if (cls) n.className = cls;
  if (text != null) n.textContent = text;
  return n;
};
const link = (href, text, external) => {
  const a = el("a", "", text);
  a.href = href;
  if (external) {
    // The same nowrap pairing the news cards use, so the icon never strands.
    const ext = el("span", "card-ext", "\u00a0");
    const ic = el("span", "ic ic-link");
    ic.setAttribute("aria-hidden", "true");
    ext.append(ic);
    a.append(ext);
  }
  return a;
};

/* The card. Built as nodes from text already in the page or its index —
   never a string of HTML — so a headline with an ampersand or a quote in it
   stays a headline. `place` is the page's own feature from addresses.geojson:
   its heading and .sub, and the coordinates its Street View is taken from,
   the same ones the page's own <ktp-streetview> uses. The Street View is that
   element too, so it arrives exactly as it does on the page — the image when
   a key is configured, the pin placeholder when there isn't one — unless the
   page has its own photo ("ph"), which takes Street View's place here as it
   does on the page. Its credit is on the page the card links to. */
const card = (place, story, links) => {
  const [lng, lat] = place.geometry.coordinates;
  const { t, s, ph } = place.properties;
  const root = el("article", "map-card");
  const sv = el("ktp-streetview");
  sv.setAttribute("location", `${lat},${lng}`);
  sv.setAttribute("label", t);
  const fig = el("figure", "media");
  if (ph) {
    const img = el("img");
    img.src = ph;
    img.alt = "Photo of " + t;
    img.decoding = "async";
    fig.append(img);
  } else {
    const empty = el("div", "media-empty");
    empty.append(el("span", "ic ic-pin"));
    fig.append(empty);
  }
  sv.append(fig);
  const body = el("div", "map-card-body");
  body.append(el("p", "map-card-title", t));
  if (s) body.append(el("p", "map-card-sub", s));
  if (story) body.append(story);
  const row = el("p", "map-card-links");
  row.append(...links);
  body.append(row);
  root.append(sv, body);
  return root;
};

/* A news dot adds the headline and the outlet, in the order the grid's card
   uses; an event dot adds the listing's own title, the when, and the calendar
   that published it. The venue is named only when it is not the page itself. */
const newsStory = ({ h, o }) => {
  const p = el("p", "map-card-story");
  p.append(el("em", "", h), el("small", "", o));
  return p;
};
const eventStory = ({ t, d, tm, v, s }, place) => {
  const p = el("p", "map-card-story");
  const where = v && v !== place.properties.t ? v : "";
  p.append(el("strong", "", t),
           el("span", "", [`${eventDay(d)}, ${tm}`, where].filter(Boolean).join(" · ")),
           el("small", "", s));
  return p;
};


/* The addresses index is the cards' source for a page's heading, line and
   photo. Only a card needs it, so it is fetched the first time one opens. */
let byPath;
const places = async () => {
  if (!byPath) {
    const all = await getJSON("/shared/addresses.geojson");
    byPath = new Map(all.features.map((f) => [f.properties.p, f]));
  }
  return byPath;
};

/* ---- public restrooms --------------------------------------------------- */
/* Every public restroom in DataSF's Public Bathrooms and Water Fountains,
   from shared/map/restrooms.json (seed_pages.py restrooms). They are a
   convenience, not the map's subject, so they stay quiet: a small muted
   toilet badge, absent at the city's scale and arriving as a reader zooms
   toward a street, drawn under the news and event dots. A restroom has no
   page; its card is the file's own words — the name, where it is, the hours —
   and a link for directions. */
const RESTROOM_ICON = "restroom";
const RESTROOM_MIN_ZOOM = 13;
/* A toilet seen from the side, on a 24-unit grid: the tank, then the bowl on
   its pedestal. */
const TOILET = "M6 3h4.5v8H6z M5 12h14c0 3.2-2.1 5.6-5 6.3l.8 2.7H8.6l.9-3.1C6.9 17 5 14.8 5 12z";
const restroomImage = () => {
  const px = 2, size = 18 * px;   // pixelRatio 2, so 18 CSS px
  const c = document.createElement("canvas");
  c.width = c.height = size;
  const g = c.getContext("2d");
  g.fillStyle = cssVar("--muted");
  g.beginPath(); g.arc(size / 2, size / 2, size / 2 - px / 2, 0, Math.PI * 2); g.fill();
  g.strokeStyle = cssVar("--paper"); g.lineWidth = px; g.stroke();
  const s = (size * 0.62) / 24;
  g.translate(size / 2 - 12 * s, size / 2 - 12 * s);
  g.scale(s, s);
  g.fillStyle = cssVar("--paper");
  g.fill(new Path2D(TOILET));
  g.setTransform(1, 0, 0, 1, 0, 0);
  return g.getImageData(0, 0, size, size);
};
const restroomLayer = {
  id: "restrooms-icon", type: "symbol", source: "restrooms", minzoom: RESTROOM_MIN_ZOOM,
  layout: {
    "icon-image": RESTROOM_ICON, "icon-allow-overlap": true, "icon-ignore-placement": true,
    "icon-size": ["interpolate", ["linear"], ["zoom"], RESTROOM_MIN_ZOOM, 0.7, 16, 1],
  },
  paint: {
    "icon-opacity": ["interpolate", ["linear"], ["zoom"],
      RESTROOM_MIN_ZOOM, 0, RESTROOM_MIN_ZOOM + 0.5, lit(1, 0.75)],
  },
};
const restroomFeatures = (doc) => doc.r.map(({ x, y, ...props }) => ({
  type: "Feature", geometry: { type: "Point", coordinates: [x, y] }, properties: props,
}));
let restrooms;
const restroomCard = ({ t, s, h, a, n }, [lng, lat]) => {
  const root = el("article", "map-card map-card-plain");
  const body = el("div", "map-card-body");
  const kicker = el("p", "map-card-kicker");
  const ic = el("span", "ic ic-restroom");
  ic.setAttribute("aria-hidden", "true");
  kicker.append(ic, document.createTextNode("Public restroom"));
  body.append(kicker, el("p", "map-card-title", t));
  if (s) body.append(el("p", "map-card-sub", s));
  const lines = [h, a, n].filter(Boolean);
  if (lines.length) {
    const p = el("p", "map-card-story");
    p.append(...lines.map((line) => el("span", "", line)));
    body.append(p);
  }
  const row = el("p", "map-card-links");
  row.append(link(`https://www.google.com/maps/dir/?api=1&destination=${lat},${lng}`,
                  "Directions", true));
  body.append(row);
  if (restrooms?.source) {
    const src = el("p", "map-card-source");
    src.append(link(restrooms.source.url, "DataSF"),
               document.createTextNode(`, retrieved ${restrooms.retrieved}`));
    body.append(src);
  }
  root.append(body);
  return root;
};

/* News and events go on above everything, on every style load — a light/dark
   switch throws the layers away — which is also how the dots pick up the other
   scheme's hues. A dot the reader can act on today outranks a story already
   told, so events draw over news. */
let events;
/* Read off the news overlay's list, which every page with the map carries. */
let news = newsFeatures();
async function addOverlays(map) {
  /* Restrooms first, so the news and event dots draw over them. A missing
     file only means no icons. */
  try { restrooms ??= await getJSON(MAP + "restrooms.json"); } catch { /* none this load */ }
  if (restrooms && !map.getSource("restrooms")) {
    map.addSource("restrooms", { type: "geojson", generateId: true,
      data: collection(restroomFeatures(restrooms)) });
  }
  if (restrooms) {
    if (!map.hasImage(RESTROOM_ICON)) map.addImage(RESTROOM_ICON, restroomImage(), { pixelRatio: 2 });
    const before = ["news-pulse", "events-pulse"].find((id) => map.getLayer(id));
    if (!map.getLayer(restroomLayer.id)) map.addLayer(restroomLayer, before);
  }
  if (!map.getSource("news")) {
    map.addSource("news", { type: "geojson", generateId: true,
      data: collection(news) });
  }
  for (const layer of pulseLayers("news", "--cool")) {
    if (!map.getLayer(layer.id)) map.addLayer(layer);
  }
  /* A missing or stale events index is not an error worth a broken map over —
     the dots just don't draw. */
  try { events ??= await getJSON("/shared/events.geojson"); } catch { /* none this load */ }
  if (events && !map.getSource("events")) {
    map.addSource("events", { type: "geojson", generateId: true,
      data: collection(eventFeatures(events)) });
  }
  if (events) {
    for (const layer of pulseLayers("events", "--event")) {
      if (!map.getLayer(layer.id)) map.addLayer(layer);
    }
  }
}

async function init() {
  if (!window.maplibregl) return;   // keep the placeholder
  const dark = matchMedia("(prefers-color-scheme: dark)");
  const base = await loadBase();

  /* The opening frame is four landmarks, not a zoom number: Fisherman's Wharf
     at the north, the Great Highway at the west, the Ferry Building at the
     east, Bernal Heights at the south. The map picks the tightest zoom that
     keeps all four inside whatever viewport it was handed, so the guarantee
     holds at any window size. The box's aspect is 1.32, wider than it is tall,
     so a desktop window binds on height and buys east-west margin for free,
     while a phone binds on width and buys north-south. */
  const map = new maplibregl.Map({
    container: shell,
    style: ownStyle(base),
    bounds: HOME,
    fitBoundsOptions: { padding: 24 },
    minZoom: 10, maxZoom: 19,
    // No credit control: the lots, streets and neighborhoods are the city's
    // own public records (DataSF), cited in DATA-SOURCES.md.
    attributionControl: false,
  });
  /* The shell's size can settle after the map is made (a late stylesheet, a
     phone's toolbar showing or hiding), so follow it rather than the window. */
  new ResizeObserver(() => map.resize()).observe(shell);

  /* Panning is fenced to San Francisco, but the fence has to contain the
     opening frame or the camera is quietly clamped and the fit never happens —
     on a phone the frame reaches latitude 37.66..37.89, which busts the city
     box at both ends. So fence to the frame the reader was actually given,
     widened to the whole city. Read off the canvas corners rather than
     getBounds(), which reports the frame inside the fitBounds padding while
     the clamp is applied to the full canvas. */
  const canvas = map.getCanvas();
  const frame = new maplibregl.LngLatBounds(
    map.unproject([0, canvas.clientHeight]), map.unproject([canvas.clientWidth, 0]));
  map.setMaxBounds(frame.extend([[-122.60, 37.68], [-122.30, 37.88]]));   // San Francisco

  map.addControl(new maplibregl.NavigationControl({ showCompass: false }), "top-right");
  map.on("style.load", () => { addOverlays(map); restorePick(); });
  /* The pulse starts only once the map has loaded: it repaints every frame, and
     a map that is always repainting never fires "load" — which is what takes
     the placeholder down. */
  map.on("load", () => {
    placeholder?.remove();
    pulse(map);
  });

  /* The wheel zooms the map — no modifier key. That only works because the map
     hands the wheel back once the reader has scrolled past it: otherwise
     scrolling back up would zoom instead of returning to the top. */
  const syncScrollZoom = () =>
    scrollY < 4 ? map.scrollZoom.enable() : map.scrollZoom.disable();
  addEventListener("scroll", syncScrollZoom, { passive: true });
  syncScrollZoom();
  dark.addEventListener("change", () => map.setStyle(ownStyle(base)));

  const popup = new maplibregl.Popup({
    closeButton: true, closeOnClick: false, offset: 12,
    className: "map-cardpop", maxWidth: "none",
  });

  /* ---- picking a neighborhood ------------------------------------------ */
  const brand = document.querySelector(".map-shell .map-brand");
  const HOME_BRAND = "Know This Place";
  let picked = null;          // the picked neighborhood's feature properties
  const loaded = new Map();   // slug → { lots, pages }, once fetched
  const fetchArea = async (slug) => {
    if (!loaded.has(slug)) {
      const [lots, pages] = await Promise.all([
        getJSON(`${MAP}lots/${slug}.json`), getJSON(`${MAP}pages/${slug}.json`)]);
      const geom = new Map(lots.lots.map(([id, z, g]) => [id, [z, polygons(g, lots.o)]]));
      loaded.set(slug, {
        lots: collection(lots.lots.map(([id, z]) => ({ type: "Feature",
          geometry: geom.get(id)[1], properties: { z } }))),
        // One lot can carry two pages (a corner building, say); the first
        // drawn takes the click, and both are on the neighborhood's page.
        pages: collection(pages.filter((p) => geom.has(p.l)).map((p) => ({ type: "Feature",
          geometry: geom.get(p.l)[1], properties: p }))),
      });
    }
    return loaded.get(slug);
  };
  /* The wordmark names where the reader is: the site at the city's scale,
     the neighborhood once one is picked (its hub's own heading when the hub
     arrives), and it is always the way back to the whole city. */
  const setBrand = (text) => { if (brand) brand.textContent = text; };
  brand?.addEventListener("click", (e) => {
    if (!picked || e.metaKey || e.ctrlKey || e.shiftKey || e.button) return;
    e.preventDefault();
    unpick();
    scrollTo({ top: 0 });
  });
  /* Until the style has loaded there is nothing to set state or data on; a
     hub opens with its neighborhood already picked, and restorePick() puts
     the pick on the style once it is up. */
  const ready = () => !!map.getSource("areas");
  const setPicked = (slug) => {
    if (!ready()) return;
    map.setFilter("veil", slug ? ["!=", ["get", "slug"], slug] : ["==", ["get", "slug"], ""]);
    map.setFilter("area-labels", slug ? ["!=", ["get", "slug"], slug] : null);
  };
  const setArea = (slug, on) => ready() && map.setFeatureState({ source: "areas", id: slug }, { picked: on });
  const setLots = (data) => {
    if (!ready()) return;
    map.getSource("lots").setData(data?.lots ?? EMPTY);
    map.getSource("pages").setData(data?.pages ?? EMPTY);
  };
  async function pick(a, how = "push", instant = false) {
    if (picked) setArea(picked.slug, false);
    picked = a;
    setArea(a.slug, true);
    setPicked(a.slug);
    setLots(null);
    popup.remove();
    if (!a.hub) setBrand(a.name);
    showHub(a, how);
    const bb = bounds(base.areas.features.find((f) => f.properties.slug === a.slug));
    const narrow = shell.clientWidth < 720;
    // On a phone the news strip spans the foot of the map; keep clear of it.
    const strip = narrow && newsBox
      ? shell.getBoundingClientRect().bottom - newsBox.getBoundingClientRect().top + 12 : 72;
    map.fitBounds(bb, { padding: { top: 64, bottom: strip, left: narrow ? 16 : 24,
                                   right: narrow ? 16 : 24 }, duration: instant ? 0 : 900 });
    const data = await fetchArea(a.slug);
    if (picked?.slug !== a.slug) return;      // another click got there first
    setLots(data);
  }
  function unpick(how = "push") {
    if (!picked) return;
    setArea(picked.slug, false);
    picked = null;
    setPicked(null);
    setLots(null);
    popup.remove();
    setBrand(HOME_BRAND);
    showHub(null, how);
    map.fitBounds(HOME, { padding: 24, duration: 900 });
  }

  /* ---- the picked neighborhood's hub, below the map --------------------- */
  /* Picking a neighborhood swaps what is below the map for that
     neighborhood's hub, and the address bar takes the hub's URL; "All
     neighborhoods" brings the homepage's news back, at "/". The hub is its
     own static page, the one a crawler or a reload gets, and build_site.py
     lays this same map over it (seed_pages.map_into), so a hub looks the same
     whether it was picked here or opened directly. A view is a page's <main>
     and footer, fetched and moved in, every link resolved against that
     page's own URL so its relative links still land. Back and forward walk
     the picks; a neighborhood with no hub of its own shows the news. */
  const below = document.querySelector("main#below");
  const footer = document.querySelector("body > footer");
  const cue = document.querySelector(".map-cue");
  const views = new Map();    // URL → Promise of { title, label, main, foot }
  views.set(location.pathname, Promise.resolve({
    title: document.title, label: cue?.firstChild?.textContent ?? "",
    main: below ? [...below.childNodes] : [], foot: footer ? [...footer.childNodes] : [] }));
  const resolve = (node, attr, at) => {
    for (const n of node.querySelectorAll(`[${attr}]`)) {
      const u = new URL(n.getAttribute(attr), at);
      n.setAttribute(attr, u.origin === location.origin ? u.pathname + u.search + u.hash : u.href);
    }
  };
  const fetchView = (url) => {
    if (!views.has(url)) {
      views.set(url, fetch(url).then((r) => (r.ok ? r.text() : Promise.reject(r.status))).then((html) => {
        const doc = new DOMParser().parseFromString(html, "text/html");
        const main = doc.querySelector("main");
        if (!main) throw new Error("no <main>");
        const foot = doc.querySelector("body > footer");
        const at = new URL(url, location.href);
        for (const n of [main, foot]) if (n) { resolve(n, "href", at); resolve(n, "src", at); }
        // The page's own cue says what is below the map: the homepage's, or
        // the hub's heading.
        const label = doc.querySelector(".map-cue")?.firstChild?.textContent
          ?? main.querySelector("h1")?.textContent ?? "";
        return { title: doc.title, label, main: [...main.childNodes],
                 foot: foot ? [...foot.childNodes] : [] };
      }).catch((err) => { views.delete(url); throw err; }));
    }
    return views.get(url);
  };
  const put = (view) => {
    if (!below) return;
    below.replaceChildren(...view.main);
    footer?.replaceChildren(...view.foot);
    document.title = view.title;
    if (cue?.firstChild) cue.firstChild.textContent = view.label;
    setBrand(picked ? view.label : HOME_BRAND);
  };
  let showing = location.pathname;
  async function showHub(a, how) {
    const url = a?.hub ?? "/";
    if (how) history[`${how}State`]({ area: a?.slug ?? null }, "", url);
    if (url === showing) return;
    try {
      const view = await fetchView(url);
      if ((picked?.hub ?? "/") !== url) return;   // another pick got there first
      put(view);
      showing = url;
    } catch { if (picked?.hub === url) setBrand(picked.name); }
  }
  addEventListener("popstate", (e) => {
    if (!e.state || !("area" in e.state)) return;     // a jump to #below, say
    const f = e.state.area && base.areas.features.find((x) => x.properties.slug === e.state.area);
    if (f) { if (f.properties.slug !== picked?.slug) pick(f.properties, null); }
    else unpick(null);
  });
  /* A scheme change rebuilds the style empty; put the pick back on it. */
  function restorePick() {
    if (!picked || !ready()) return;
    setArea(picked.slug, true);
    setPicked(picked.slug);
    setLots(loaded.get(picked.slug));
  }
  /* Even-odd ray casting over a MultiPolygon's rings, holes included. */
  const polygonsHold = (polys, x, y) => {
    let inside = false;
    for (const poly of polys) for (const ring of poly) {
      for (let i = 0, j = ring.length - 1; i < ring.length; j = i++) {
        const [xi, yi] = ring[i], [xj, yj] = ring[j];
        if ((yi > y) !== (yj > y) && x < ((xj - xi) * (y - yi)) / (yj - yi) + xi) inside = !inside;
      }
    }
    return inside;
  };
  const bounds = (f) => {
    const b = new maplibregl.LngLatBounds();
    for (const poly of f.geometry.coordinates) for (const p of poly[0]) b.extend(p);
    return b;
  };

  /* ---- what is under the pointer ---------------------------------------- */
  /* An event dot sits over a news dot for the same address, so the layers are
     asked in that order and the top one answers. A few pixels of slack make a
     small dot something a finger can hit. Below the dots, a documented lot in
     the picked neighborhood; below that, a neighborhood. */
  const DOTS = ["events-dot", "news-dot", "restrooms-icon"];
  const SLACK = 4;
  const dotAt = (pt) => {
    const layers = DOTS.filter((id) => map.getLayer(id));
    if (!layers.length) return null;
    const hits = map.queryRenderedFeatures(
      [[pt.x - SLACK, pt.y - SLACK], [pt.x + SLACK, pt.y + SLACK]], { layers });
    for (const id of layers) {
      const near = hits.filter((f) => f.layer.id === id);
      if (!near.length) continue;
      const d = (f) => map.project(f.geometry.coordinates).dist(pt);
      return near.reduce((a, b) => (d(b) < d(a) ? b : a));
    }
    return null;
  };
  const lotAt = (pt) => (picked ? map.queryRenderedFeatures(pt, { layers: ["page-fill"] })[0] : null);
  const areaAt = (pt) => map.queryRenderedFeatures(pt, { layers: ["area-fill"] })[0] ?? null;
  const key = (f) => f && (f.source === "pages" ? f.properties.p
    : f.source === "areas" ? f.properties.slug : f.id);
  const mark = (f, state, on) => f && map.getSource(f.source) &&
    map.setFeatureState({ source: f.source, id: key(f) }, { [state]: on });

  let hovered = null, active = null;
  const hover = (f) => {
    if (f?.source === hovered?.source && key(f) === key(hovered)) return;
    mark(hovered, "hover", false);
    hovered = f;
    mark(hovered, "hover", true);
    map.getCanvas().style.cursor = f ? "pointer" : "";
  };
  map.on("mousemove", (e) => {
    const area = areaAt(e.point);
    hover(dotAt(e.point) ?? lotAt(e.point) ??
      (area && area.properties.slug !== picked?.slug ? area : null));
  });
  map.on("mouseout", () => hover(null));
  /* A style switch throws the sources away, and their feature state with them. */
  map.on("style.load", () => { hovered = null; popup.remove(); });
  popup.on("close", () => { mark(active, "active", false); active = null; });

  /* A dot opens its card; so does a documented lot. Every card links to the
     page of the address or place; a news dot also links the story, and an
     event dot the calendar's own listing. A click on another neighborhood
     picks it; a click on water, or outside every neighborhood, puts the city
     back. Escape closes a card, or with none open puts the city back. */
  map.on("click", async (e) => {
    const f = dotAt(e.point) ?? lotAt(e.point);
    if (!f) {
      popup.remove();
      const area = areaAt(e.point);
      if (area && area.properties.slug !== picked?.slug) pick(area.properties);
      else if (!area) unpick();
      return;
    }
    openCard(f, f.source === "pages" ? e.lngLat : f.geometry.coordinates);
  });
  async function openCard(f, at) {
    const props = f.properties;
    if (f.source === "restrooms") {
      popup.remove();
      active = f;
      mark(active, "active", true);
      popup.setLngLat(at).setDOMContent(restroomCard(props, f.geometry.coordinates)).addTo(map);
      return;
    }
    const ll = maplibregl.LngLat.convert(at);
    const place = (await places()).get(props.p) ?? {
      geometry: { coordinates: [ll.lng, ll.lat] }, properties: { t: props.t, s: props.s ?? "" },
    };
    const here = link(props.p, "See this place");
    let content;
    if (f.source === "news") {
      content = card(place, newsStory(props),
        [here, ...(props.u ? [link(props.u, "Read article", true)] : [])]);
    } else if (f.source === "events") {
      content = card(place, eventStory(props, place),
        [here, ...(props.u ? [link(props.u, "See event", true)] : [])]);
    } else {
      content = card(place, null, [here]);
    }
    popup.remove();
    active = f;
    mark(active, "active", true);
    popup.setLngLat(at).setDOMContent(content).addTo(map);
  }

  /* ---- the news overlay -------------------------------------------------- */
  /* The news sits on the map, folded into a glassy strip at its foot. A story
     picked from the list opens on the map, as its dot would: the camera goes
     to the building and its card opens there, the page one more click away.
     A pick elsewhere in the city is let go first, so its veil can't hide the
     building. On a phone the list folds back so the card has the room. */
  const newsBox = document.querySelector(".map-news");
  const more = newsBox?.querySelector(".map-news-more");
  const list = newsBox?.querySelector(".news-cards");
  /* Folded, the strip is exactly the newest row tall, so the fold lands on
     its border whatever the headline's length; measured again on resize. */
  const fitFirst = () => {
    const first = list?.firstElementChild;
    if (first) list.style.setProperty("--first", `${first.offsetHeight}px`);
  };
  fitFirst();
  new ResizeObserver(fitFirst).observe(shell);
  /* On a phone the folded strip shows no story, only the button, so there it
     says what it opens rather than "more". */
  const phone = matchMedia("(max-width: 720px)");
  const label = () => {
    const open = newsBox.classList.contains("is-open");
    more.textContent = open ? "Show less" : phone.matches ? "In the news" : "Show more";
  };
  const setOpen = (open) => {
    if (!newsBox) return;
    newsBox.classList.toggle("is-open", open);
    more.setAttribute("aria-expanded", String(open));
    label();
    if (!open) list.scrollTop = 0;
  };
  if (newsBox) { label(); phone.addEventListener("change", label); }
  more?.addEventListener("click", () => setOpen(!newsBox.classList.contains("is-open")));
  newsBox?.addEventListener("click", (e) => {
    const li = e.target.closest(".news-cards > li");
    const a = li?.querySelector("a:not(.card-outlet)");
    if (!a || e.metaKey || e.ctrlKey || e.shiftKey) return;
    const i = news.findIndex((n) => n.properties.p === a.getAttribute("href"));
    if (i < 0) return;
    e.preventDefault();
    const n = news[i];
    const [lng, lat] = n.geometry.coordinates;
    if (picked) {
      const area = base.areas.features.find((x) => x.properties.slug === picked.slug);
      if (!polygonsHold(area.geometry.coordinates, lng, lat)) unpick();
    }
    if (shell.clientWidth < 720) setOpen(false);
    map.flyTo({ center: [lng, lat], zoom: Math.max(map.getZoom(), 14.5), duration: 900 });
    map.once("moveend", () => openCard({ source: "news", id: i, ...n }, [lng, lat]));
  });
  /* Escape closes an open card first; with none open it puts the city back. */
  addEventListener("keydown", (e) => {
    if (e.key !== "Escape" || e.defaultPrevented) return;
    if (popup.isOpen()) popup.remove();
    else unpick();
  });

  /* A hub opens on its own neighborhood, already picked, with no flight. Its
     breadcrumb header gives way to the wordmark, which already names the
     neighborhood, so the page is the one a pick on the homepage would have
     made. */
  const opening = document.querySelector(".map-shell")?.dataset.area;
  const first = opening && base.areas.features.find((f) => f.properties.slug === opening);
  if (first) {
    document.querySelector("body > .site-header")?.remove();
    pick(first.properties, null, true);
  }
  history.replaceState({ area: first ? opening : null }, "");
}

/* maplibre-gl.js is deferred, so it may not have run yet. */
if (window.maplibregl) init().catch(() => {});
else addEventListener("DOMContentLoaded", () => init().catch(() => {}));
