/* DEMO ONLY — the homepage map with lots instead of dots.

   One script, two modes, chosen by <div id="map" data-mode="…">:

   basemap     MapLibre GL over a keyless OpenFreeMap vector basemap (stand-in
               for Mapbox, whose token is locked to knowthis.place and
               localhost, so it never renders on a Netlify preview). The
               layers added here are identical in Mapbox GL JS.
   no-basemap  MapLibre GL drawing only our own files: the city's land, every
               lot in the city (fetched a ~1 km cell at a time as you pan), the
               street centrelines and their names. No tile server at all — the
               only third-party request left is the label font.

   At city zoom a lot is smaller than a pixel, so the documented pages stay
   dots until about zoom 15, then cross-fade into their lot outlines. */

const shell = document.getElementById("map");
const MODE = shell.dataset.mode;
const D = "/demo/parcels/data/";
const dark = matchMedia("(prefers-color-scheme: dark)").matches;
const css = (n) => getComputedStyle(document.documentElement).getPropertyValue(n).trim();
const C = {
  warm: css("--warm"), muted: css("--muted"), paper: css("--paper"),
  ink: css("--ink"), rule: css("--rule"), panel: css("--panel"),
};
// Colours with no token yet: the ground the lots sit on (the streets, in the
// no-basemap mode), water, and parkland. Chosen per scheme, demo-grade.
const T = dark
  ? { water: "#1b232b", ground: "#2a2b2d", lot: "#1f2022", lotLine: "#3a3b3e",
      park: "#22302200", parkFill: "#233023", label: "#9a9a9a", halo: "#1b1c1e" }
  : { water: "#d6e1e8", ground: "#e4e1db", lot: "#faf8f4", lotLine: "#cfcac1",
      park: "#e3ecd9", parkFill: "#e3ecd9", label: "#6f6a62", halo: "#f4f1ec" };

const FONT = ["Noto Sans Regular"];
const GLYPHS = "https://tiles.openfreemap.org/fonts/{fontstack}/{range}.pbf";

const emptyFC = { type: "FeatureCollection", features: [] };

function ownStyle() {
  return {
    version: 8,
    glyphs: GLYPHS,
    sources: {
      land: { type: "geojson", data: D + "land.geojson" },
      lots: { type: "geojson", data: emptyFC, tolerance: 0.2 },
      streets: { type: "geojson", data: D + "streets.geojson", tolerance: 0.3 },
    },
    layers: [
      { id: "water", type: "background", paint: { "background-color": T.water } },
      { id: "land", type: "fill", source: "land", paint: { "fill-color": T.ground } },
      // Every lot. Where lots meet, the gap between blocks *is* the street:
      // the ground shows through, so the city's grid draws itself.
      { id: "lots", type: "fill", source: "lots", minzoom: 13,
        paint: {
          "fill-color": ["case", ["has", "z"], T.parkFill, T.lot],
          "fill-opacity": ["interpolate", ["linear"], ["zoom"], 13, 0, 14, 1],
        } },
      { id: "lot-lines", type: "line", source: "lots", minzoom: 15,
        paint: { "line-color": T.lotLine,
                 "line-width": ["interpolate", ["linear"], ["zoom"], 15, 0.3, 18, 1] } },
      // Below lot zoom, the streets are drawn as lines instead.
      { id: "street-lines", type: "line", source: "streets", maxzoom: 15,
        layout: { "line-cap": "round", "line-join": "round" },
        paint: {
          "line-color": dark ? "#3c3d40" : "#ffffff",
          "line-width": ["interpolate", ["linear"], ["zoom"],
            10, ["match", ["get", "c"], [1, 2], 1.6, 3, 1, 0.3],
            13, ["match", ["get", "c"], [1, 2], 4, 3, 2.5, 1],
            15, ["match", ["get", "c"], [1, 2], 8, 3, 6, 3]],
          "line-opacity": ["interpolate", ["linear"], ["zoom"], 13.5, 1, 15, 0],
        } },
      { id: "land-labels", type: "symbol", source: "land", maxzoom: 14,
        layout: { "text-field": ["get", "n"], "text-font": FONT, "text-size": 11,
                  "text-transform": "uppercase", "text-letter-spacing": 0.08,
                  "text-max-width": 7, "symbol-placement": "point" },
        paint: { "text-color": T.label, "text-halo-color": T.halo, "text-halo-width": 1.2,
                 "text-opacity": ["interpolate", ["linear"], ["zoom"], 11, 0, 11.5, 0.8, 13.5, 0.8, 14, 0] } },
      { id: "street-labels", type: "symbol", source: "streets",
        filter: ["any", ["<=", ["get", "c"], 3], [">=", ["zoom"], 15]],
        minzoom: 13,
        layout: { "text-field": ["get", "n"], "text-font": FONT,
                  "symbol-placement": "line", "symbol-spacing": 400,
                  "text-size": ["interpolate", ["linear"], ["zoom"], 13, 10, 18, 13],
                  "text-letter-spacing": 0.04 },
        paint: { "text-color": T.label, "text-halo-color": T.halo, "text-halo-width": 1.5 } },
    ],
  };
}

const style = MODE === "basemap"
  ? `https://tiles.openfreemap.org/styles/${dark ? "dark" : "positron"}`
  : ownStyle();

const map = new maplibregl.Map({
  container: shell, style,
  bounds: [[-122.5105, 37.7395], [-122.3937, 37.8095]],
  fitBoundsOptions: { padding: 24 },
  minZoom: 10, maxZoom: 19,
  maxBounds: [[-122.70, 37.62], [-122.25, 37.92]],
  attributionControl: { compact: true },
});
map.addControl(new maplibregl.NavigationControl({ showCompass: false }), "top-right");

/* ---- the documented pages: dots, then lots ------------------------------ */
const FADE = [14.5, 15.5];          // dots out, lots in, across this zoom band
const LIT = ["boolean", ["feature-state", "hover"], false];
const pageColor = ["case", ["has", "r"], C.warm, C.muted];

function addPages() {
  map.addSource("dots", { type: "geojson", data: "/shared/addresses.geojson", promoteId: "p" });
  map.addSource("pages", { type: "geojson", data: emptyFC, promoteId: "p", tolerance: 0.2 });
  map.addLayer({ id: "page-fill", type: "fill", source: "pages", minzoom: 13.5,
    paint: {
      "fill-color": pageColor,
      "fill-opacity": ["interpolate", ["linear"], ["zoom"], FADE[0], 0,
        FADE[1], ["case", LIT, 0.85, ["case", ["has", "r"], 0.55, 0.28]]],
    } });
  map.addLayer({ id: "page-line", type: "line", source: "pages", minzoom: 13.5,
    paint: {
      "line-color": pageColor,
      "line-width": ["case", LIT, 2.5, 1],
      "line-opacity": ["interpolate", ["linear"], ["zoom"], FADE[0], 0, FADE[1], 0.9],
    } });
  map.addLayer({ id: "page-dots", type: "circle", source: "dots",
    layout: { "circle-sort-key": ["case", ["has", "r"], 1, 0] },
    paint: {
      "circle-color": pageColor,
      "circle-radius": ["interpolate", ["linear"], ["zoom"], 10, 0.8, 12, 1.4, 14, 3, 15.5, 5],
      "circle-opacity": ["interpolate", ["linear"], ["zoom"],
        10, ["case", ["has", "r"], 0.45, 0.15], 13, ["case", ["has", "r"], 0.7, 0.25],
        FADE[0], ["case", ["has", "r"], 0.95, 0.5], FADE[1], 0],
    } });
}

/* The page lots file is 9 MB (1.5 MB gzipped), so it's fetched the first time
   the reader zooms in far enough to see a lot, not on load. */
let ready = false, pagesLoaded = false;
async function maybeLoadPages() {
  if (!ready || pagesLoaded || map.getZoom() < 13.5) return;
  pagesLoaded = true;
  const t = performance.now();
  const fc = await (await fetch(D + "pages.geojson")).json();
  map.getSource("pages").setData(fc);
  stat("page lots", fc.features.length, t);
}

/* ---- no-basemap: every lot in the city, a cell at a time ---------------- */
let cellIndex = null;
const cells = new Map();            // id → features, once fetched
async function maybeLoadCells() {
  if (!ready || MODE !== "no-basemap" || map.getZoom() < 13) return;
  cellIndex ??= await (await fetch(D + "lots/index.json")).json();
  const b = map.getBounds();
  const want = cellIndex.filter(({ bbox: [w, s, e, n] }) =>
    e > b.getWest() && w < b.getEast() && n > b.getSouth() && s < b.getNorth());
  const missing = want.filter((c) => !cells.has(c.id));
  if (!missing.length) return;
  const t = performance.now();
  missing.forEach((c) => cells.set(c.id, null));
  await Promise.all(missing.map(async (c) => {
    cells.set(c.id, (await (await fetch(`${D}lots/${c.id}.json`)).json()).features);
  }));
  const all = [...cells.values()].filter(Boolean).flat();
  map.getSource("lots").setData({ type: "FeatureCollection", features: all });
  stat(`lots (${[...cells.values()].filter(Boolean).length} cells)`, all.length, t);
}

/* ---- the card ----------------------------------------------------------- */
const popup = new maplibregl.Popup({ closeButton: true, closeOnClick: false, offset: 10,
  className: "demo-pop", maxWidth: "18rem" });
const esc = (s) => String(s ?? "").replace(/[&<>"]/g, (c) => `&${{ "&": "amp", "<": "lt", ">": "gt", '"': "quot" }[c]};`);
let hovered = null;
const hit = (pt) => {
  const layers = map.getZoom() >= FADE[0] + 0.5 ? ["page-fill"] : ["page-dots"];
  const box = [[pt.x - 4, pt.y - 4], [pt.x + 4, pt.y + 4]];
  return map.queryRenderedFeatures(box, { layers })[0] ?? null;
};
map.on("mousemove", (e) => {
  const f = hit(e.point);
  const id = f?.properties.p ?? null;
  if (id === hovered) return;
  if (hovered) for (const s of ["pages", "dots"]) map.setFeatureState({ source: s, id: hovered }, { hover: false });
  hovered = id;
  if (id) for (const s of ["pages", "dots"]) map.setFeatureState({ source: s, id }, { hover: true });
  map.getCanvas().style.cursor = id ? "pointer" : "";
});
map.on("click", (e) => {
  const f = hit(e.point);
  if (!f) { popup.remove(); return; }
  const p = f.properties;
  popup.setLngLat(e.lngLat).setHTML(
    `<strong>${esc(p.t)}</strong>${p.s ? `<span>${esc(p.s)}</span>` : ""}` +
    `<a href="${esc(p.p)}">See this place →</a>`).addTo(map);
});

/* ---- the readout: what each layer cost --------------------------------- */
const readout = document.getElementById("readout");
function stat(what, n, t0) {
  const ms = Math.round(performance.now() - t0);
  const li = document.createElement("li");
  li.textContent = `${what}: ${n.toLocaleString()} features in ${ms} ms`;
  readout?.append(li);
}
function zoomline() {
  const z = document.getElementById("zoom");
  if (z) z.textContent = `zoom ${map.getZoom().toFixed(1)}` +
    (map.getZoom() < FADE[0] ? " · zoom past 15 to see lots" : "");
}

map.on("load", () => {
  document.querySelector(".map-shell .media-empty")?.remove();
  addPages();
  ready = true;
  maybeLoadPages(); maybeLoadCells(); zoomline();
});
map.on("moveend", () => { maybeLoadPages(); maybeLoadCells(); });
map.on("zoom", zoomline);

/* Deep links: #lng,lat,zoom, so a reader can be sent straight to a block. */
const m = location.hash.match(/^#(-?[\d.]+),(-?[\d.]+),([\d.]+)$/);
if (m) map.jumpTo({ center: [+m[1], +m[2]], zoom: +m[3] });
