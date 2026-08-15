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
   day the key is set, with no page regeneration. */
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
      const img = document.createElement("img");
      img.src =
        "https://maps.googleapis.com/maps/api/streetview?size=640x480&scale=2&location=" +
        encodeURIComponent(location) +
        "&key=" +
        encodeURIComponent(key);
      img.alt = "Street View of " + label;
      img.decoding = "async";
      empty.replaceWith(img);
    }
  },
);

/* Read a design-system color at render time. The static map's pin is drawn by
   Mapbox, not by CSS, so its hue has to be passed to the server as a hex
   string — reading it from site.css keeps it the same brick the rest of the
   site uses, in both light and dark mode, and keeps every color in one file. */
const cssVar = (name) =>
  getComputedStyle(document.documentElement).getPropertyValue(name).trim();

/* <ktp-map location="LAT,LNG" label="123 Example St">
     <figure class="media media-map"> …placeholder or fallback… </figure>
   </ktp-map>

   The locator band: where this building sits, as one flat image from the
   Mapbox Static Images API, run across the top of the page above the address.
   Same shape and same law as <ktp-streetview> —
   the light-DOM .media-empty placeholder is the whole content of the block
   with no JS, and the image only replaces it once `mapbox_token` is set in
   site-config.json. Nothing a reader needs to know lives in the picture: the
   coordinates are in the placeholder, the address is in the <h1>, and the
   homepage map is where the site's geography is browsable.

   A static image rather than Mapbox GL JS deliberately — an address page
   loads no third-party script, and an <img> costs one request instead of a
   map engine. Mapbox bakes its own and OpenStreetMap's attribution into the
   returned image, so the credit travels with the picture and no page has to
   carry a second one.

   The basemap follows the reader's color scheme (the same two styles the
   homepage map uses) and re-renders if they switch mid-visit. */
/* The band is ~1000 CSS px wide on a full-width page, so the image is asked
   for at 1200x400 and @2x: `@2x` both doubles the pixels and draws labels and
   roads at twice the size, so the picture is sharp on a hidpi screen and
   correctly proportioned on an ordinary one. Zoom 17 rather than 16 because a
   band this wide at 16 covers most of a mile — the parcel's own block has to
   be the thing you see. On phones the same image is cropped to 16:9 by
   `object-fit`, so one request serves both layouts. */
const MAP_ZOOM = 17;
const MAP_SIZE = "1200x400@2x";

customElements.define(
  "ktp-map",
  class extends HTMLElement {
    async connectedCallback() {
      const empty = this.querySelector(".media-empty");
      const location = this.getAttribute("location");
      if (!empty || !location) return; // leave the fallback untouched

      const [lat, lng] = location.split(",").map((n) => Number(n.trim()));
      if (!Number.isFinite(lat) || !Number.isFinite(lng)) return;

      const { mapbox_token: token } = await siteConfig();
      if (!token) return; // no token yet → keep the placeholder as-is

      const label = this.getAttribute("label") || "this address";
      const dark = matchMedia("(prefers-color-scheme: dark)");
      const src = () =>
        "https://api.mapbox.com/styles/v1/mapbox/" +
        (dark.matches ? "dark-v11" : "light-v11") +
        "/static/pin-s+" +
        cssVar("--warm").replace("#", "") +
        `(${lng},${lat})/${lng},${lat},${MAP_ZOOM},0/${MAP_SIZE}` +
        "?access_token=" +
        encodeURIComponent(token);

      const img = document.createElement("img");
      img.src = src();
      // No width/height attributes: the .media-map frame sets the box in CSS,
      // and a height attribute would win over that aspect ratio. Not lazy
      // either — the band is the first thing on the page, so it is never the
      // image a reader has to scroll to.
      img.alt = "Map showing the location of " + label;
      img.decoding = "async";
      empty.replaceWith(img);

      // --warm resolves to the dark-mode brick on its own, so re-reading it
      // here is all the swap needs.
      dark.addEventListener("change", () => (img.src = src()));
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
