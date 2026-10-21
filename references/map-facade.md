# Map Facade Pattern — Reference Implementation

Load only a local map screenshot; insert the provider iframe only on explicit
user activation. A native `loading="lazy"` map iframe is forbidden — it can
load automatically when it approaches the viewport, without any click
(tech-spec §6, §10).

## HTML

```html
<div class="map-facade" data-map-embed="https://www.google.com/maps/embed?pb=…">
  <img src="https://site.com/images/map-screenshot-1280.jpg"
    srcset="https://site.com/images/map-screenshot-320.jpg 320w, https://site.com/images/map-screenshot-640.jpg 640w, https://site.com/images/map-screenshot-768.jpg 768w, https://site.com/images/map-screenshot-1024.jpg 1024w, https://site.com/images/map-screenshot-1280.jpg 1280w, https://site.com/images/map-screenshot-1920.jpg 1920w"
    sizes="(min-width: 1200px) 1200px, 100vw"
    alt="Map showing the business location: <address>" width="1280" height="480"
    loading="lazy" decoding="async">
  <button class="map-open" type="button">Show interactive map (Google Maps)</button>
</div>
```

The screenshot is a real local asset (AVIF/WebP/JPEG per §1 — JPEG shown for
brevity), generated from the provider with permission/rights recorded in
`ASSETS.md` (§12). The button label names both the action and the provider so
users know which third party they are about to contact.

## CSS

```css
.map-facade{position:relative;max-width:1200px;aspect-ratio:1280/480}
.map-facade img{width:100%;height:auto;display:block}
.map-facade iframe{position:absolute;inset:0;width:100%;height:100%;border:0}
.map-open{position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);
  padding:12px 20px;border:0;border-radius:6px;cursor:pointer;
  font:inherit;font-weight:600;color:#fff;background:rgba(0,0,0,.75)}
.map-open:focus-visible{outline:3px solid #fff;outline-offset:3px}
```

## JS (in the single deferred page script)

```javascript
document.addEventListener('click', function (e) {
  var btn = e.target.closest('.map-open');
  if (!btn) return;
  var box = btn.closest('.map-facade');
  // The embed URL is untrusted brief input (tech-spec §13): validate the
  // scheme and the provider host before it reaches the DOM. Adjust the
  // host allow-list to the provider actually used (Google Maps shown).
  var raw = box.dataset.mapEmbed || '';
  var url;
  try { url = new URL(raw); } catch (err) { return; }
  if (url.protocol !== 'https:' || url.hostname !== 'www.google.com' ||
      url.pathname.indexOf('/maps/embed') !== 0) return;
  var iframe = document.createElement('iframe');
  iframe.src = url.href;
  iframe.title = 'Interactive map: business location';
  iframe.loading = 'lazy';
  iframe.allowFullscreen = false;
  iframe.referrerPolicy = 'strict-origin-when-cross-origin';
  box.innerHTML = '';
  box.appendChild(iframe);
  iframe.focus();
});
```

## Notes
- Keep the container aspect ratio equal to the screenshot dimensions. It must
  retain its height when activation removes the image and inserts an absolute
  iframe. Test nonzero, unchanged geometry after pointer and keyboard activation.
- Send only the page origin to the HTTPS provider, never its full path/query.
- The iframe `src` is absent from the initial DOM entirely — the only map
  bytes before activation are the local screenshot. Network test: filter the
  provider domain in DevTools, load the page and scroll past the block — zero
  requests; click the button — the embed request appears.
- Keyboard (Enter/Space) and pointer activation both reach the same delegated
  click handler, so both follow the identical network policy.
- The provider host allow-list in the script must match the provider named in
  the button label; other providers (OpenStreetMap, Yandex) need their own
  embed-host check. A malformed or non-allowlisted URL is a generation error,
  never a value to embed.
- Third-party governance (tech-spec §11): the map embed is a documented
  dependency — record origin, activation moment (click only), CSP `frame-src`
  destination, and subrequests in the per-page manifest. The provider host
  must be added to `frame-src` in the generated CSP (server-config.md).
- Multiple map blocks: one delegated handler covers them all, as with video.
