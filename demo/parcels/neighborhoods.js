/* DEMO ONLY — prototype D: pick a neighborhood, then see its lots.

   The city opens as its 41 Analysis Neighborhoods over B's own basemap (land,
   street lines and names; no tile server). The news and events dots sit above
   them at every zoom. A click on a neighborhood flies to its boundary, dims
   the rest of the city, and fetches that one neighborhood's file: every lot
   in it plus the lots of its documented pages, about 100–400 KB gzipped. */

const shell = document.getElementById("map");
const D = "/demo/parcels/data/";
const dark = matchMedia("(prefers-color-scheme: dark)").matches;
const css = (n) => getComputedStyle(document.documentElement).getPropertyValue(n).trim();
const C = { warm: css("--warm"), muted: css("--muted"), paper: css("--paper"),
            ink: css("--ink"), cool: css("--cool"), event: css("--event") };
const T = dark
  ? { water: "#1b232b", ground: "#2a2b2d", lot: "#1f2022", lotLine: "#3a3b3e", park: "#233023",
      street: "#3c3d40", label: "#9a9a9a", halo: "#1b1c1e", area: "#34363a", veil: "#16171a" }
  : { water: "#d6e1e8", ground: "#e4e1db", lot: "#faf8f4", lotLine: "#cfcac1", park: "#e3ecd9",
      street: "#ffffff", label: "#6f6a62", halo: "#f4f1ec", area: "#d9d4cc", veil: "#efece6" };
const FONT = ["Noto Sans Regular"];
const empty = { type: "FeatureCollection", features: [] };
const HOME = [[-122.5105, 37.7395], [-122.3937, 37.8095]];

const map = new maplibregl.Map({
  container: shell,
  style: {
    version: 8,
    glyphs: "https://tiles.openfreemap.org/fonts/{fontstack}/{range}.pbf",
    sources: {
      land: { type: "geojson", data: D + "land.geojson" },
      streets: { type: "geojson", data: D + "streets.geojson", tolerance: 0.3 },
      areas: { type: "geojson", data: D + "nhoods/index.geojson", promoteId: "slug" },
      lots: { type: "geojson", data: empty, tolerance: 0.2 },
      pages: { type: "geojson", data: empty, promoteId: "p", tolerance: 0.2 },
      news: { type: "geojson", data: empty },
      events: { type: "geojson", data: empty },
    },
    layers: [
      { id: "water", type: "background", paint: { "background-color": T.water } },
      { id: "land", type: "fill", source: "land", paint: { "fill-color": T.ground } },
      { id: "street-lines", type: "line", source: "streets",
        layout: { "line-cap": "round", "line-join": "round" },
        paint: { "line-color": T.street,
          "line-width": ["interpolate", ["linear"], ["zoom"],
            10, ["match", ["get", "c"], [1, 2], 1.6, 3, 1, 0.3],
            13, ["match", ["get", "c"], [1, 2], 4, 3, 2.5, 1],
            16, ["match", ["get", "c"], [1, 2], 10, 3, 8, 5]] } },
      // Neighborhoods: a soft tint you can hover and click.
      { id: "area-fill", type: "fill", source: "areas",
        paint: { "fill-color": T.area,
          "fill-opacity": ["case", ["boolean", ["feature-state", "hover"], false], 0.75, 0] } },
      // The selected neighborhood's lots.
      { id: "lots", type: "fill", source: "lots",
        paint: { "fill-color": ["case", ["has", "z"], T.park, T.lot] } },
      { id: "lot-lines", type: "line", source: "lots",
        paint: { "line-color": T.lotLine,
                 "line-width": ["interpolate", ["linear"], ["zoom"], 13, 0.15, 15, 0.4, 18, 1] } },
      { id: "page-fill", type: "fill", source: "pages",
        paint: { "fill-color": ["case", ["has", "r"], C.warm, C.muted],
          "fill-opacity": ["case", ["boolean", ["feature-state", "hover"], false], 0.9,
                           ["case", ["has", "r"], 0.6, 0.3]] } },
      { id: "page-line", type: "line", source: "pages",
        paint: { "line-color": ["case", ["has", "r"], C.warm, C.muted],
          "line-width": ["interpolate", ["linear"], ["zoom"], 13, 0.3, 16, 1],
          "line-opacity": 0.9 } },
      // Once one is picked, the rest of the city steps back behind a veil.
      { id: "veil", type: "fill", source: "areas", filter: ["==", ["get", "slug"], ""],
        paint: { "fill-color": T.veil, "fill-opacity": 0.72 } },
      { id: "area-line", type: "line", source: "areas",
        paint: { "line-color": T.label,
          "line-width": ["case", ["boolean", ["feature-state", "picked"], false], 2.5,
                        ["boolean", ["feature-state", "hover"], false], 1.5, 0.6],
          "line-opacity": ["case", ["boolean", ["feature-state", "picked"], false], 0.9, 0.55] } },
      { id: "street-labels", type: "symbol", source: "streets", minzoom: 14,
        filter: ["any", ["<=", ["get", "c"], 3], [">=", ["zoom"], 15.5]],
        layout: { "text-field": ["get", "n"], "text-font": FONT, "symbol-placement": "line",
                  "symbol-spacing": 400, "text-size": ["interpolate", ["linear"], ["zoom"], 14, 10, 18, 13] },
        paint: { "text-color": T.label, "text-halo-color": T.halo, "text-halo-width": 1.5 } },
      { id: "area-labels", type: "symbol", source: "areas", maxzoom: 14,
        layout: { "text-field": ["get", "n"], "text-font": FONT, "text-size": 11,
                  "text-transform": "uppercase", "text-letter-spacing": 0.08, "text-max-width": 7 },
        paint: { "text-color": T.label, "text-halo-color": T.halo, "text-halo-width": 1.2 } },
      // News and events always on top, with a soft ring so a dozen dots find
      // themselves in a city.
      ...["news", "events"].flatMap((s) => [
        { id: `${s}-halo`, type: "circle", source: s,
          paint: { "circle-color": s === "news" ? C.cool : C.event, "circle-opacity": 0.18,
                   "circle-radius": ["interpolate", ["linear"], ["zoom"], 10, 7, 16, 18] } },
        { id: `${s}-dot`, type: "circle", source: s,
          paint: { "circle-color": s === "news" ? C.cool : C.event,
                   "circle-radius": ["interpolate", ["linear"], ["zoom"], 10, 3, 16, 7],
                   "circle-stroke-color": C.paper, "circle-stroke-width": 1.5 } },
      ]),
    ],
  },
  bounds: HOME, fitBoundsOptions: { padding: 24 },
  minZoom: 10, maxZoom: 19, maxBounds: [[-122.70, 37.62], [-122.25, 37.92]],
  attributionControl: { compact: true },
});
new ResizeObserver(() => map.resize()).observe(shell);
map.addControl(new maplibregl.NavigationControl({ showCompass: false }), "top-right");

/* ---- news and events: the homepage's own sources ------------------------ */
async function loadStories() {
  // News: the homepage's grid of cards is the list, as on the real map.
  try {
    const doc = new DOMParser().parseFromString(await (await fetch("/")).text(), "text/html");
    const news = [...doc.querySelectorAll(".news-cards > li")].flatMap((li) => {
      const sv = li.querySelector("ktp-streetview");
      const [lat, lng] = (sv?.getAttribute("location") ?? "").split(",").map(Number);
      if (!Number.isFinite(lat)) return [];
      return [{ type: "Feature", geometry: { type: "Point", coordinates: [lng, lat] },
        properties: { t: sv.getAttribute("label") ?? "",
          p: li.querySelector(".card-label")?.closest("a")?.getAttribute("href") ?? "",
          h: li.querySelector(".card-news em")?.textContent ?? "",
          o: li.querySelector(".card-outlet")?.textContent.trim() ?? "",
          u: li.querySelector(".card-outlet")?.getAttribute("href") ?? "" } }];
    });
    map.getSource("news").setData({ type: "FeatureCollection", features: news });
  } catch {}
  // Events: the next six days, one dot per spot, soonest first.
  try {
    const all = await (await fetch("/shared/events.geojson")).json();
    const today = new Date(); today.setHours(0, 0, 0, 0);
    const horizon = today.getTime() + 7 * 86400e3, spot = new Map();
    for (const f of all.features) {
      const d = new Date(f.properties.d).getTime();
      if (d < today.getTime() || d >= horizon) continue;
      const k = f.geometry.coordinates.join(",");
      if (!spot.has(k) || f.properties.d < spot.get(k).properties.d) spot.set(k, f);
    }
    map.getSource("events").setData({ type: "FeatureCollection", features: [...spot.values()] });
  } catch {}
}

/* ---- picking a neighborhood -------------------------------------------- */
const panel = document.getElementById("panel");
const esc = (s) => String(s ?? "").replace(/[&<>"]/g, (c) => `&${{ "&": "amp", "<": "lt", ">": "gt", '"': "quot" }[c]};`);
let picked = null, hoverArea = null, hoverPage = null;

function idle() {
  panel.innerHTML = `<strong>Pick a neighborhood</strong>
    <p>Tap one to zoom in and see every lot in it. News and events stay on top.</p>
    <p class="demo-small"><a href="/demo/parcels/">All prototypes</a></p>`;
}

async function pick(f) {
  const p = f.properties, slug = p.slug;
  const bbox = typeof p.bbox === "string" ? JSON.parse(p.bbox) : p.bbox;
  if (picked) map.setFeatureState({ source: "areas", id: picked }, { picked: false });
  picked = slug;
  map.setFeatureState({ source: "areas", id: slug }, { picked: true });
  map.setFilter("veil", ["!=", ["get", "slug"], slug]);
  map.setFilter("area-labels", ["!=", ["get", "slug"], slug]);
  map.getSource("lots").setData(empty); map.getSource("pages").setData(empty);
  popup.remove();
  // Keep the boundary clear of the panel, which covers the bottom on a phone.
  const narrow = shell.clientWidth < 720;
  const under = narrow ? panel.offsetHeight + 24 : 40;
  map.fitBounds([[bbox[0], bbox[1]], [bbox[2], bbox[3]]],
    { padding: { top: 64, bottom: under, left: narrow ? 16 : 40, right: narrow ? 16 : 40 }, duration: 900 });
  panel.innerHTML = `<strong>${esc(p.n)}</strong><p>Loading lots…</p>`;
  const t = performance.now();
  const res = await fetch(`${D}nhoods/${slug}.json`);
  const data = await res.json();
  if (picked !== slug) return;            // another click got there first
  map.getSource("lots").setData(data.lots);
  map.getSource("pages").setData(data.pages);
  const ms = Math.round(performance.now() - t);
  panel.innerHTML = `<strong>${esc(p.n)}</strong>
    <p>${data.pages.features.length.toLocaleString()} documented buildings among
    ${data.lots.features.length.toLocaleString()} lots.
    ${p.hub ? `<a href="${esc(p.hub)}">Neighborhood page →</a>` : ""}</p>
    <p class="demo-small">Fetched in ${ms} ms ·
    <button type="button" id="back">All neighborhoods</button></p>`;
  document.getElementById("back").onclick = reset;
}

function reset() {
  if (picked) map.setFeatureState({ source: "areas", id: picked }, { picked: false });
  picked = null;
  map.setFilter("veil", ["==", ["get", "slug"], ""]);
  map.setFilter("area-labels", null);
  map.getSource("lots").setData(empty); map.getSource("pages").setData(empty);
  popup.remove();
  map.fitBounds(HOME, { padding: 24, duration: 900 });
  idle();
}

/* ---- pointer: a story dot first, then a page lot, then a neighborhood --- */
const popup = new maplibregl.Popup({ closeButton: true, closeOnClick: false, offset: 10,
  className: "demo-pop", maxWidth: "18rem" });
const at = (pt, layers) => map.queryRenderedFeatures(
  [[pt.x - 5, pt.y - 5], [pt.x + 5, pt.y + 5]], { layers: layers.filter((l) => map.getLayer(l)) })[0];
const day = (d) => new Date(d).toLocaleDateString("en-US", { weekday: "short", month: "short", day: "numeric" });

map.on("mousemove", (e) => {
  const story = at(e.point, ["events-dot", "news-dot"]);
  const page = !story && picked ? at(e.point, ["page-fill"]) : null;
  const area = !story && !page ? at(e.point, ["area-fill"]) : null;
  const pageId = page?.properties.p ?? null, areaId = area?.properties.slug ?? null;
  if (pageId !== hoverPage) {
    if (hoverPage) map.setFeatureState({ source: "pages", id: hoverPage }, { hover: false });
    hoverPage = pageId;
    if (pageId) map.setFeatureState({ source: "pages", id: pageId }, { hover: true });
  }
  // Hovering the open neighborhood itself does nothing; others still invite a click.
  const hv = areaId === picked ? null : areaId;
  if (hv !== hoverArea) {
    if (hoverArea) map.setFeatureState({ source: "areas", id: hoverArea }, { hover: false });
    hoverArea = hv;
    if (hv) map.setFeatureState({ source: "areas", id: hv }, { hover: true });
  }
  map.getCanvas().style.cursor = story || page || hv ? "pointer" : "";
});

map.on("click", (e) => {
  const story = at(e.point, ["events-dot", "news-dot"]);
  if (story) {
    const p = story.properties;
    const body = story.layer.id === "news-dot"
      ? `<strong>${esc(p.t)}</strong><em>${esc(p.h)}</em><span>${esc(p.o)}</span>`
      : `<strong>${esc(p.t)}</strong><span>${esc(day(p.d))}, ${esc(p.tm)} · ${esc(p.v)}</span>`;
    popup.setLngLat(story.geometry.coordinates).setHTML(body +
      (p.p ? `<a href="${esc(p.p)}">See this place →</a>` : "")).addTo(map);
    return;
  }
  const page = picked ? at(e.point, ["page-fill"]) : null;
  if (page) {
    const p = page.properties;
    popup.setLngLat(e.lngLat).setHTML(`<strong>${esc(p.t)}</strong>` +
      (p.s ? `<span>${esc(p.s)}</span>` : "") + `<a href="${esc(p.p)}">See this place →</a>`).addTo(map);
    return;
  }
  popup.remove();
  const area = at(e.point, ["area-fill"]);
  if (area && area.properties.slug !== picked) pick(area);
});

map.on("load", () => {
  document.querySelector(".map-shell .media-empty")?.remove();
  idle();
  loadStories();
});
