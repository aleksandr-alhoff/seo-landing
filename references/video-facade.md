# YouTube Facade Pattern — Reference Implementation

Load only the cover image; start loading the video only on click.

## Google video discovery trade-off (read first)
This pattern is click-only: the rendered HTML contains a cover and a button, and the iframe exists only after activation. Google discovers videos through `<video>`, `<embed>`, `<iframe>`, and `<object>` elements in the rendered HTML and warns that video loading must not depend on user actions such as clicking (developers.google.com/search/docs/appearance/video). The facade therefore deliberately trades Google video discovery and video-feature eligibility for zero third-party requests before activation:
- Do not claim video-search optimization for a facade-only page; `VideoObject` on such a page is optional metadata, reported as metadata-only (tech-spec §9 reporting gate).
- When video search traffic matters, choose the SEO-discoverable mode instead (self-hosted `<video>` or a documented direct embed — tech-spec §9 Mode S). A dedicated watch page is Google's further recommendation for video-feature eligibility and is out of scope for a single landing.

## HTML

The example below shows a below-the-fold video, hence `loading="lazy"` on the
cover. Placement decides loading (tech-spec §9): when the cover is the LCP
element or sits above the fold, remove `loading="lazy"` (eager is the default)
and add `fetchpriority="high"` to the `<img>` instead.

```html
<div class="video-facade" data-video-id="dQw4w9WgXcQ">
  <picture>
    <source type="image/avif"
      srcset="https://site.com/images/video-cover-320.avif 320w, https://site.com/images/video-cover-640.avif 640w, https://site.com/images/video-cover-768.avif 768w, https://site.com/images/video-cover-1024.avif 1024w, https://site.com/images/video-cover-1280.avif 1280w, https://site.com/images/video-cover-1920.avif 1920w"
      sizes="(min-width: 1200px) 1200px, 100vw">
    <source type="image/webp"
      srcset="https://site.com/images/video-cover-320.webp 320w, https://site.com/images/video-cover-640.webp 640w, https://site.com/images/video-cover-768.webp 768w, https://site.com/images/video-cover-1024.webp 1024w, https://site.com/images/video-cover-1280.webp 1280w, https://site.com/images/video-cover-1920.webp 1920w"
      sizes="(min-width: 1200px) 1200px, 100vw">
    <img src="https://site.com/images/video-cover-1280.jpg"
      srcset="https://site.com/images/video-cover-320.jpg 320w, https://site.com/images/video-cover-640.jpg 640w, https://site.com/images/video-cover-768.jpg 768w, https://site.com/images/video-cover-1024.jpg 1024w, https://site.com/images/video-cover-1280.jpg 1280w, https://site.com/images/video-cover-1920.jpg 1920w"
      sizes="(min-width: 1200px) 1200px, 100vw"
      alt="Video cover: Video title — Video block"
      width="1280" height="720" loading="lazy" decoding="async">
  </picture>
  <button class="video-play" type="button" aria-label="Watch video: Video title">
    <span class="video-play-icon" aria-hidden="true"></span>
  </button>
</div>
```

`sizes` must equal the facade container width (here the §5 container cap of
1200px) and must be identical on every `<source>` and the `<img>`. Verify at
320, 640, 1024, and 1920px viewports that the browser picks the intended
candidate in each case.

## CSS (play icon without SVG)

```css
.video-facade{position:relative;aspect-ratio:16/9;max-width:1200px;background:#000}
.video-facade img{width:100%;height:100%;object-fit:cover}
.video-facade iframe{position:absolute;inset:0;width:100%;height:100%;border:0}
.video-play{position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);
  width:72px;height:72px;border:0;border-radius:50%;cursor:pointer;
  background:rgba(0,0,0,.65);display:flex;align-items:center;justify-content:center}
.video-play-icon{width:0;height:0;border-style:solid;
  border-width:14px 0 14px 24px;border-color:transparent transparent transparent #fff;
  margin-left:5px}
.video-play:focus-visible{outline:3px solid #fff;outline-offset:3px}
@media (prefers-reduced-motion:no-preference){
  .video-play{transition:transform .2s}
  .video-play:hover{transform:translate(-50%,-50%) scale(1.1)}
}
```

## JS (defer, before `</body>`)

```javascript
document.addEventListener('click', function (e) {
  var btn = e.target.closest('.video-play');
  if (!btn) return;
  var box = btn.closest('.video-facade');
  // Validate the ID before building the URL — never interpolate untrusted
  // data into a DOM-created URL (tech-spec §13). A YouTube ID is exactly
  // 11 chars of [A-Za-z0-9_-]; anything else is a generation error.
  var id = box.dataset.videoId || '';
  if (!/^[A-Za-z0-9_-]{11}$/.test(id)) return;
  var iframe = document.createElement('iframe');
  iframe.src = 'https://www.youtube-nocookie.com/embed/' + id + '?autoplay=1';
  iframe.title = btn.getAttribute('aria-label').replace('Watch video: ', '');
  iframe.loading = 'lazy';
  iframe.allow = 'accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture';
  iframe.allowFullscreen = true;
  iframe.referrerPolicy = 'strict-origin-when-cross-origin'; // origin only; required player identity
  box.innerHTML = '';
  box.appendChild(iframe);
  iframe.focus();
});
```

There is deliberately NO preconnect handler here. A hover/focus preconnect
would perform third-party DNS/connection work before user intent and expose
the visitor's network address to YouTube — contradicting the guarantee below.
Keyboard (Enter/Space) and pointer activation both reach the single delegated
click handler, so both follow the same network policy: first contact with
`youtube-nocookie.com` is the iframe insertion itself.

## Notes
- Store the cover locally in `images/` (AVIF/WebP/JPEG) — never hotlink `i.ytimg.com`.
- One delegated handler covers any number of videos.
- Before activation (click or Enter/Space): zero requests to YouTube — no preconnect, no DNS, no connection setup; hovering or keyboard-focusing the cover contacts nothing. Verify in DevTools: filter `youtube-nocookie.com`, load the page, hover/focus without activating → zero requests; activate → the embed request appears. After activation the embed still avoids ~0.5–1 MB of JS and dozens of connections that an immediate embed would have caused on page load.
- CLS = 0: fixed `aspect-ratio: 16/9` and numeric `width/height`.
- The video ID is untrusted input: it is validated against `^[A-Za-z0-9_-]{11}$` at generation time (tech-spec §13) and again before the iframe URL is built — a malformed ID must fail generation, not reach the DOM.
- Third-party governance (tech-spec §11): the YouTube embed is a documented dependency — record origin, activation moment (click only), CSP `frame-src`/`connect-src` destination, and subrequests in the per-page manifest. Use `strict-origin-when-cross-origin`: YouTube requires HTTP Referer identification for embedded players; suppressing it can cause error 153. Only the origin is sent, without the landing path/query. See [YouTube client identity requirements](https://developers.google.com/youtube/terms/required-minimum-functionality#api-client-identity-and-credentials). `sandbox` is a documented incompatibility for this embed: YouTube playback requires `allow-scripts` + `allow-same-origin` together, which equals no sandbox — record that justification instead of adding a no-op sandbox. Verify after HTTPS deployment: playback starts on click, and fullscreen works; do not claim playback based only on iframe insertion.
