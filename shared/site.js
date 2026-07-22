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

// One memoized read of site-config for anything that needs it (the map key).
let _config;
function siteConfig() {
  // no-store: this file gates behavior (the map key), so it must never read
  // a stale cached copy — imagery should switch on the day the key is set.
  return (_config ??= fetch("/shared/site-config.json", { cache: "no-store" })
    .then((r) => (r.ok ? r.json() : {}))
    .catch(() => ({})));
}

/* <ktp-streetview location="LAT,LNG" label="123 Example St">
     <figure class="media"> …placeholder or fallback… </figure>
   </ktp-streetview>

   Click-to-load Google Street View. The light-DOM fallback (the .media-empty
   placeholder) is what shows with no JS or no configured key. When a Maps
   embed key IS configured, this swaps the placeholder for a "Load" facade and
   only contacts Google after the reader clicks — no third-party request on
   page load, and imagery turns on site-wide the day the key is set, with no
   page regeneration. */
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
      const facade = document.createElement("button");
      facade.type = "button";
      facade.className = "sv-facade";
      facade.innerHTML =
        '<span class="ic ic-pin" aria-hidden="true"></span>' +
        "<span>Load Street View</span>" +
        "<small>Loads present-day imagery from Google when you click.</small>";
      facade.setAttribute("aria-label", "Load Google Street View of " + label);
      empty.replaceWith(facade);

      facade.addEventListener(
        "click",
        () => {
          const iframe = document.createElement("iframe");
          iframe.src =
            "https://www.google.com/maps/embed/v1/streetview?key=" +
            encodeURIComponent(key) +
            "&location=" +
            encodeURIComponent(location);
          iframe.loading = "lazy";
          iframe.allowFullscreen = true;
          iframe.referrerPolicy = "no-referrer-when-downgrade";
          iframe.title = "Street view of " + label;
          facade.replaceWith(iframe);
        },
        { once: true },
      );
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
