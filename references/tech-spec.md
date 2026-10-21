# Technical Specification — Fast SEO-Friendly Landing Pages

Version 1.12 (21.10.2026)

This file is the single source of truth for the specification version and its
change record. Other documents (README, SKILL) must point here instead of
repeating the version number — a number that exists in one place cannot diverge.

## Change record
- **1.12 (21.10.2026)** — audit corrections: same-origin absolute asset validation has a runnable local checker, Lighthouse runtime matches Node ≥22.19, honeypot tests distinguish neutral discard from genuine errors, map geometry survives activation, provider referrers send origin only, and server/install/rollback examples are corrected. Historical benchmark measurements remain bound to their measured commit.
- **1.11 (30.08.2026)** — final audit batch: the video facade is reconciled with Google video discovery requirements — the click-only facade (Mode F, default) explicitly trades discovery/feature eligibility for pre-activation privacy and performance, no video-search benefit is claimed for it and `VideoObject` is reported as metadata-only; an opt-in SEO-discoverable Mode S (self-hosted `<video>` preferred, or a documented direct embed recorded as a first-load dependency) keeps the player discoverable in the rendered HTML, with watch-page honesty for feature eligibility, mode-gated `VideoObject` reporting, and rendered-HTML/URL-Inspection evidence instead of JSON-LD syntax alone (#39). Language, direction, and locale are separated into three collected-and-validated inputs: BCP-47 `<html lang>`, explicit base direction with `dir="rtl"` for RTL documents (`lang` does not set directionality; `dir="auto"`/`<bdi>` for unknown mixed values), and `og:locale` in the Open Graph `language_TERRITORY` format; direction-dependent layout uses logical CSS properties, RTL gets a dedicated responsive inspection, and hreflang/alternate locales are emitted only for real equivalents (#41).
- **1.10 (30.08.2026)** — skill process batch: every global installation recipe is self-contained (creates its own destination directory first) (#1); the skill routes explicitly between generate, audit-only, and fix-existing modes with mode-specific inputs and outputs (#2); forms get a functioning, testable submission contract — destination collected in the brief, end-to-end delivery test before reporting, idempotent handlers, success/error UX, data ownership (#17); validation is an executable contract of pinned commands with measured results and explicit BLOCKERs — no bundled script artifact, PageSpeed-style reports never fabricated (#18); the README benchmark is disclosed as reproducible lab measurement (fixture committed, Lighthouse 13.4.1 profile/flags, 5 rebuilt runs, median aggregation, raw reports) and separated from field Core Web Vitals — no CWV pass is claimed without field 75th-percentile data (#19); copied installations get a documented lifecycle — destinations table, bounded idempotent rsync update removing upstream-deleted files, backup/recovery, verification, reload, uninstall, and the explicit statement that git pull changes only the clone (#53).
- **1.9 (30.08.2026)** — performance & media batch: non-lazy responsive LCP image with a canonical `<picture>` recipe and a responsive `imagesrcset`/`imagesizes` preload that matches the rendered candidate, or no preload (#4); video-facade cover made responsive with placement-based eager/lazy loading (#5); hover preconnect removed — zero YouTube requests before activation for pointer and keyboard alike (#6); the contradictory lazy-map-iframe exception eliminated, maps are facade-only with a canonical accessible reference implementation (#7); nonessential third-party widgets consent-gated with budget claims qualified honestly (#8); `viewport-fit=cover` paired with mandatory safe-aware spacing rules (#32); the generated-project contract now includes every referenced CSS/script/image asset with a hard-failing existence check (#3).
- **1.8 (30.08.2026)** — server & security hardening batch: `immutable` caching restricted to fingerprinted asset URLs with verified Nginx location ordering (#9); security headers reach Nginx child locations and Apache error responses (#10); Brotli module prerequisite documented and validated, gzip-only fallback recorded honestly (#11); executable HTTP→HTTPS deployment contract (#12); context-aware output encoding and URL validation for untrusted brief input (#25); deployable per-page Content-Security-Policy with staged rollout (#26); HTTPS-only HSTS with safe staged rollout (#27); MIME mappings defined and verified per generated resource class (#29); Apache `.htaccess` activation (AllowOverride classes, module inventory) documented (#40); third-party code governance — dependency manifest, SRI, explicit referrer policy, minimum iframe sandbox (#51); exact-path never-immutable cache policies for robots.txt and sitemap.xml with 304/200 verification (#52). Server requirements declared server-agnostic with portability guidance for Caddy, IIS, OpenLiteSpeed, and managed platforms.
- **1.7 (30.08.2026)** — single source of truth: the specification version and change record live only in this file; the README footer points here instead of duplicating the version, and the version-divergence check script is removed (#20 follow-up).
- **1.6 (30.08.2026)** — accessibility contract: native-HTML-first ARIA rule (#45); no forced new tabs for external links (#46); accessible carousel contract (#47); complete modal `<dialog>` workflow (#48); form labels and input-purpose metadata (#49); reduced-motion gate over every permitted animation (#50); non-text contrast 3:1 (#33); conditional bypass/skip-link mechanism (#34); purpose-based image alternatives (#13); required manual accessibility checks before claiming WCAG AA (#14).
- **1.5 (29.08.2026)** — truthfulness and provenance: verified LocalBusiness identity and most-specific subtype (#15, #44); WebSite only on the domain/subdomain home page (#35); BreadcrumbList only with a real hierarchy (#22); FAQPage eligibility limits (#23); Review/AggregateRating gated to eligible source-backed cases (#16); Speakable restricted to its beta news eligibility (#21); VideoObject only from collected media facts (#36); crawlable favicon in the output contract (#38); truthful sitemap/robots discovery contract (#37); source-backed marketing claims (#42); asset rights and provenance manifest (#43).
- **1.4 (29.08.2026)** — canonical workflow order with stop point before validation (#24); mandatory `<meta charset="utf-8">` and UTF-8 Content-Type (#30); CSP/no-JS-safe deferred CSS (#31); `Vary: Accept-Encoding` for compressed responses (#28).
- **1.3 (27.08.2026)** — initial published revision.

## Contents
- 1. Performance (100/100 PageSpeed)
- 2. HTML structure
- 3. SEO optimization
- 4. Security and accessibility
- 5. CSS / fonts
- 6. Forbidden
- 7. Testing
- 8. Accessibility and inclusivity
- 9. Embedded video (facade by default; SEO-discoverable mode opt-in)
- 10. Typical blocks without speed loss
- 11. Deferred widgets
- 12. Content truthfulness & provenance
- 13. Input sanitization & output encoding
- Output requirements

Create a static HTML site focused on maximum performance and SEO.

## 1. PERFORMANCE (100/100 PageSpeed)
- **LCP target**: <2.5s (hero image or H1)
- **INP target**: <100ms (minimize JS on the first screen)
- **CLS target**: <0.1 (fixed dimensions for all elements, including fonts)
- Inline ALL critical CSS in `<style>` inside `<head>` (only first-screen styles)
- First screen = header + hero + CTA (up to 800px height on desktop, 70vh on smartphones)
- Critical CSS must include ONLY the styles of these blocks
- Below-the-fold CSS — two options, both must work with JavaScript disabled and under a strict CSP:
  - Default: inline ALL CSS (critical + below-the-fold) in `<head>` — landing CSS is usually small enough that deferral is not justified by measurement.
  - Only when measurement shows a real benefit: `<link rel="preload" href="styles.css" as="style">` plus `<link rel="stylesheet" href="styles.css" media="print">`, and switch `media` to `all` from the single deferred page script. Never use an inline `onload` handler on the link — it breaks under CSP and contradicts the script policy. Add a `<noscript><link rel="stylesheet" href="styles.css"></noscript>` fallback.
- Verify full screen rendering with JavaScript disabled, under the enforced CSP, and after a stylesheet load failure
- ALL images: AVIF with WebP/JPEG fallback via `<picture>`, `decoding="async"`, numeric width/height in pixels on every image
- Loading timing is placement-based, never blanket: `loading="lazy"` belongs ONLY on below-the-fold images. The LCP/above-the-fold image never carries `loading="lazy"` — a lazy-loaded LCP image waits for the intersection observer and delays LCP (web.dev "Optimize LCP"); omit the attribute there (eager is the default) and set `fetchpriority="high"` on it instead.
- Use `srcset` and `sizes` on all `<img>`
- Calculate `sizes` from the container max-width
- Responsive breakpoints: 320, 640, 768, 1024, 1280, 1920
- Blur placeholder or LQIP (Low Quality Image Placeholder)
- `aspect-ratio` in CSS to prevent layout shift
- `speakable` markup — BETA, do not use by default. Eligible only for topical news content from English-language publishers targeting Google Home users in the United States; recipes and ordinary landing pages are not eligible. When eligibility is established, collect the CSS selector or XPath targets, keep the selected text concise, visible and suitable for audio, and label the feature as beta. Omit it when eligibility cannot be confirmed.
- Static assets are emitted with fingerprinted filenames — a content-hash fragment in the name (e.g. `styles.a1b2c3d4.css`, `hero.9f31c2ab.webp`). Only fingerprinted URLs may receive `Cache-Control: public, max-age=31536000, immutable`; every asset change must regenerate the hash and update all HTML references (including `srcset`) in the same commit. A stable (unhashed) URL must never be marked `immutable` — a compliant cache may serve the old bytes for the entire max-age after the file is overwritten (RFC 9111); stable URLs get a revalidation policy (`no-cache`) instead.
- HTML: `max-age=0, must-revalidate`
- Server instructions must specify Brotli (br) preferred, gzip fallback — and state the Brotli module prerequisite honestly: Nginx needs ngx_brotli installed/loaded (verify with `nginx -t` and an `Accept-Encoding: br` request), Apache's `mod_brotli` block is skipped when absent. When the module cannot be installed, ship gzip-only and record that explicitly — never claim Brotli that is not actually served (see references/server-config.md)
- LCP image — one canonical responsive recipe (above the fold, never lazy):

```html
<picture>
  <source type="image/avif"
    srcset="https://site.com/images/hero-320.avif 320w, https://site.com/images/hero-640.avif 640w, https://site.com/images/hero-768.avif 768w, https://site.com/images/hero-1024.avif 1024w, https://site.com/images/hero-1280.avif 1280w, https://site.com/images/hero-1920.avif 1920w"
    sizes="(min-width: 1200px) 1200px, 100vw">
  <source type="image/webp"
    srcset="https://site.com/images/hero-320.webp 320w, https://site.com/images/hero-640.webp 640w, https://site.com/images/hero-768.webp 768w, https://site.com/images/hero-1024.webp 1024w, https://site.com/images/hero-1280.webp 1280w, https://site.com/images/hero-1920.webp 1920w"
    sizes="(min-width: 1200px) 1200px, 100vw">
  <img src="https://site.com/images/hero-1280.jpg"
    srcset="https://site.com/images/hero-320.jpg 320w, https://site.com/images/hero-640.jpg 640w, https://site.com/images/hero-768.jpg 768w, https://site.com/images/hero-1024.jpg 1024w, https://site.com/images/hero-1280.jpg 1280w, https://site.com/images/hero-1920.jpg 1920w"
    sizes="(min-width: 1200px) 1200px, 100vw"
    alt="Concise purpose-based description" width="1280" height="640" fetchpriority="high" decoding="async">
</picture>
```

  - `sizes` follows the container (§5 max-width 1200px → `(min-width: 1200px) 1200px, 100vw`); the identical `sizes` value must appear on every `<source>` and on the `<img>`.
  - This image carries NO `loading` attribute (eager is the default) — `loading="lazy"` on the LCP image is forbidden.
- Preloading the LCP image is NOT automatically required: an `<img>` present in the initial HTML is already discoverable by the preload scanner, and `fetchpriority="high"` is the primary priority signal. Add a preload only when the image is not directly discoverable (CSS background, JS-inserted) or measurement shows a benefit — then it must be responsive and match the first `<source>` so the browser fetches the same format/width it will render:
  `<link rel="preload" as="image" fetchpriority="high" imagesrcset="https://site.com/images/hero-320.avif 320w, …, https://site.com/images/hero-1920.avif 1920w" imagesizes="(min-width: 1200px) 1200px, 100vw">`
  A preload naming one fixed URL (e.g. `href="hero.webp"`) while `<picture>` renders a different format or width is forbidden — it produces an unused early request. When the rendered candidate cannot be matched safely (e.g. the audience includes browsers without AVIF support), omit the preload instead. Verify in DevTools that the preloaded response is the one the hero actually uses (no "preloaded but not used" warning).
- Add `fetchpriority="high"` to the main image
- ALL scripts (if any) must have the `defer` attribute and be placed before `</body>`
- Absolute paths for ALL resources: `src="https://site.com/images/photo.webp"`

## 2. HTML STRUCTURE
- Document encoding: `<meta charset="utf-8">` as the very first element inside `<head>`, entirely within the first 1024 bytes of the document. All files are saved as UTF-8 without BOM.
- Clean semantic HTML5: `<header>`, `<nav>`, `<main>`, `<article>`, `<section>`, `<footer>`
- Bypass mechanism (WCAG SC 2.4.1): when the output is part of a multi-page site sharing repeated header/navigation, emit a first-focusable "Skip to main content" link targeting a stable `<main>` ID; make it visible on focus and verify activation moves focus and scroll to the main content. A genuinely standalone one-page landing without repeated blocks does not need this conditional mechanism.
- One responsive HTML, no duplicate content (mobile/desktop)
- Heading hierarchy: one H1, then H2–H6 by logic
- Language, direction, and locale are three separate inputs collected in the brief — never one value copied across formats:
  - HTML language: a valid BCP-47 tag matching the content, on `<html>` (`lang="en-US"`, `lang="ar-SA"`).
  - Base direction: `lang` does NOT set directionality (W3C). RTL documents must carry `dir="rtl"` on `<html>` (LTR is the default). An Arabic/Hebrew page without `dir="rtl"` breaks punctuation placement, alignment, controls, and form entry.
  - Open Graph locale: `og:locale` uses the Open Graph format `language_TERRITORY` (ogp.me), e.g. `en_GB` — copying a hyphenated BCP-47 value like `en-US` into `og:locale` violates the advertised format.
  - Mixed/unknown direction: for genuinely unknown mixed-direction values (user-entered strings, names), use `dir="auto"` on the containing element or `<bdi>` for inline isolation — never on the document root.
  - Alternate versions: emit `hreflang`/alternate-locale metadata only when real localized equivalents exist at real URLs — never invent alternates for a single-language landing.
  - RTL validation: on RTL documents, verify rendered RTL text containing Latin-script URLs, phone numbers, forms, and form controls at mobile and desktop widths — punctuation, alignment, input direction, and control layout must all remain correct.
- Viewport: `<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=5.0, viewport-fit=cover">` — `viewport-fit=cover` ships ONLY together with the mandatory safe-area spacing rules in §5; a project that drops those rules must drop `viewport-fit=cover` with them.
- Minify HTML, CSS and JS files: remove comments and extra whitespace

## 3. SEO OPTIMIZATION
- Meta tags:
  - `<title>Unique keyword title up to 60 characters</title>`
  - `<meta name="description" content="Unique keyword description up to 160 characters">`
  - `<meta name="robots" content="index, follow, max-image-preview:large, max-snippet:-1, max-video-preview:-1">`
  - `<link rel="canonical" href="https://site.com/">`
- Open Graph: og:title, og:description, og:image, og:type, og:url, og:locale (plus og:image:width, og:image:height, og:image:alt). `og:locale` follows the Open Graph `language_TERRITORY` format (ogp.me, e.g. `en_GB`) — it is a separate input from the BCP-47 `lang` attribute (§2), not a copy of it.
- Twitter card: twitter:card, twitter:title, twitter:description, twitter:image
- `hreflang`/alternate-locale links are emitted only when real localized equivalents exist at real URLs; a single-language landing gets none — invented alternates are a generation error (§2).
- Favicon: a stable local square PNG/ICO of at least 48×48 (dimensions a multiple of 48px) plus `<link rel="icon" href="https://site.com/favicon.png">` on the home page. The asset must be brand-approved (or created with explicit permission), included in the project manifest, and verified to return 200 and remain crawlable. Meeting these rules makes the icon eligible for Google Search results — it does not guarantee display.
- JSON-LD structured data (at the end of body):
  - `@type: WebSite` (with `name` and the canonical root `url`) only on the domain or subdomain home page, consistent with visible branding; omit it for subdirectory landings when the root home page is outside this project's scope. Never invent a site identity or use a subdirectory URL as the WebSite root.
  - `Organization`/`LocalBusiness` (with GEO data: address, phone, coordinates)
  - `LocalBusiness` only when the verified identity facts exist: public/legal business name, complete structured postal address (street, locality, region, postal code, country), phone. Never invent identity data — fall back to `Organization` markup or omit entity markup when required facts are unavailable. Validate required properties against the current Google LocalBusiness structured-data documentation, not only schema.org syntax.
  - Emit the most specific truthful `LocalBusiness` subtype based on the actual business (e.g. `Restaurant`, `Dentist`), not target keywords; use an `@type` array only when multiple genuine types apply. Omit `LocalBusiness` markup entirely when no physical location exists. Validate the chosen type/property combination with Rich Results Test and Schema Markup Validator.
  - `@type: BreadcrumbList` only when a real site hierarchy exists: collect the visible breadcrumb trail and canonical parent URLs, require at least two truthful ordered `ListItem` entries, and keep the JSON-LD consistent with user-visible navigation. Omit `BreadcrumbList` for a standalone landing without a real hierarchy rather than inventing parent pages.
  - If a visible, complete FAQ content block exists, add `FAQPage` markup. Distinguish schema.org validity from Google rich-result eligibility: Google currently shows FAQ rich results regularly only for well-known authoritative government and health sites, and valid markup never guarantees display. Keep or omit the markup intentionally based on the user's goals, and never report it as an achieved rich-result benefit.
  - `Review`/`AggregateRating` markup is forbidden for the represented Organization/LocalBusiness itself (self-serving ratings are ineligible for LocalBusiness rich results). Emit review markup only for an eligible reviewed entity with collected facts: reviewed entity, author, date, source, rating scale and count — and only when every rating is visible on the page exactly as marked up. Omit rating markup when eligibility or source authenticity is not established.
  - All URLs absolute, `@id` specified
- Crawlability contract (robots.txt + sitemap.xml):
  - `sitemap.xml`: valid UTF-8 XML with XML-escaped, absolute canonical `<loc>` URLs; each `<loc>` must match the page's HTML canonical. Populate `lastmod` only from a verifiable significant-content-change timestamp — omit it when unknown rather than using generation time blindly.
  - `robots.txt`: deployed at the site root with a fully qualified `Sitemap:` URL; must not block the canonical page or required media (images, video covers).
  - Validation: parse the sitemap XML, compare every `<loc>` with the HTML canonical, check the `Sitemap:` URL in robots.txt, and request both deployed files successfully (HTTP 200).

## 4. SECURITY AND ACCESSIBILITY
- `<meta name="referrer" content="strict-origin-when-cross-origin">`
- Security headers (in the .htaccess instructions):
  - `X-Content-Type-Options: nosniff`
  - `X-Frame-Options: DENY`
  - `Permissions-Policy: camera=(), microphone=(), geolocation=()`
  - `Referrer-Policy: strict-origin-when-cross-origin`
  - They must reach every response class, not only successful HTML: configure inheritance so Nginx child locations and Apache locally generated responses (404/error pages, internal redirects) carry them too, and verify with `curl -I` on `/`, `.css`, `.js`, and a 404 (see references/server-config.md).
- Content-Security-Policy is generated per page from its actual feature set — restrictive `default-src 'self'` base with explicit `object-src 'none'`, `base-uri 'self'`, `frame-ancestors 'none'`; inline `<style>` authorized by `sha256-` hashes; no `unsafe-inline`/`unsafe-eval` for scripts; `youtube-nocookie.com` added to `frame-src` only when the video block exists (no `connect-src` entry — the facade contacts that origin only at iframe insertion, which `frame-src` covers). Roll out report-only first, browser-test every feature combination, then enforce (see references/server-config.md).
- `Strict-Transport-Security` is deployed on HTTPS responses only, in stages: short `max-age` first, long lifetime after clean rollout; `includeSubDomains` only when every applicable subdomain serves HTTPS; `preload` only as an explicitly warned opt-in. HSTS supplements the HTTP→HTTPS redirect, it never replaces it (see references/server-config.md).
- Every generated resource class must be served with its correct MIME type (HTML, CSS, JS, AVIF/WebP/JPEG/PNG, robots.txt, sitemap.xml) — with `nosniff` enabled a wrong type is an operational failure. The deployment instructions define the expected types, Nginx `mime.types` inclusion (or explicit mappings) and Apache `AddType` fallbacks, and require deployed `curl -I` verification per resource class (see references/server-config.md).
- The Apache instructions must document `.htaccess` activation: `AllowOverride FileInfo` grants the class; `AllowOverrideList` instead takes individual directive names, never class names. Include the required/optional module inventory and behavioral verification — Apache silently ignores `.htaccess` unless overrides are permitted, so file presence is never proof (see references/server-config.md).
- `/robots.txt` and `/sitemap.xml` get exact-path cache policies, never `immutable` and never a long `max-age` (default revalidation, or a documented short TTL with its worst-case propagation delay recorded); validators (ETag/Last-Modified) are preserved, and verification covers `304` on unchanged and `200` with new bytes on changed, at origin and behind any CDN (see references/server-config.md).
- Accessibility: native HTML first (W3C's first rule of ARIA). Use semantic elements (`<button>`, `<a>`, `<details>`, `<dialog>`, native form controls) and add ARIA only for necessary semantics not already supplied by the element. Never duplicate or override native roles/states. For each custom component define its accessible name, role, state, keyboard behavior, and how state changes are announced; validate ARIA conformance and inspect the resulting accessibility tree.
- Image alternatives are purpose-based (W3C images tutorial), not a blanket title/alt mandate:
  - Informative images: concise `alt` text conveying the image's purpose.
  - Decorative images or images whose content is duplicated in adjacent text: `alt=""` and no `title`, so assistive technology ignores them.
  - Images inside links: the `alt` describes the link destination/action (together with any adjacent link text).
  - Complex images (charts, diagrams): short `alt` identifying the image plus the essential information provided nearby in text.
  - Never use block-name/number wording as alt text. Include manual screen-reader and accessible-name checks in validation.
- External links open in the current browsing context by default. Use `target="_blank"` only for an explicit UX/task reason (e.g. a form submission must not be abandoned, a reference must stay open), keep `rel="noopener noreferrer"` when used, and warn users in advance both visibly and programmatically — e.g. `External site <span class="visually-hidden">(opens in a new tab)</span>` or equivalent link text. Test keyboard and screen-reader behavior so the link purpose and the new-tab context change are announced.
- All file links and external links must use HTTPS
- HTTPS enforcement is part of the deployment contract, not an assumption: the generated `SERVER-SETUP.md` must include a tested port-80 virtual host/server block that issues a single permanent 301/308 redirect preserving host, path, and query string to the canonical HTTPS host, plus the TLS certificate prerequisite and reverse-proxy/CDN caveats (see references/server-config.md).

## 5. CSS / FONTS
- ONLY system fonts: `font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", "Roboto", "Oxygen", "Ubuntu", "Cantarell", "Helvetica Neue", Arial, sans-serif;`
- Forbidden: external fonts, `font-display: swap`, Google Fonts
- CLS prevention:
  - `* { box-sizing: border-box; }`
  - `img { max-width: 100%; height: auto; display: block; }`
  - `.container { width: 100%; max-width: 1200px; margin: 0 auto; padding-inline: max(15px, env(safe-area-inset-left)) max(15px, env(safe-area-inset-right)); }`
- Direction-aware layout: direction-dependent spacing, positioning, and alignment use logical CSS properties (`margin-inline`, `padding-inline`, `inset-inline-start/end`, `text-align: start/end`) rather than physical left/right, so RTL documents (`dir="rtl"`, §2) render correctly from the same stylesheet without a mirrored copy.
- Safe-area spacing (paired with `viewport-fit=cover`, CSS env() spec): design spacing and system insets are COMBINED, never replaced — use `max(design-value, env(safe-area-inset-*))` or add them.
  - Every edge-aligned essential element gets safe-area-aware logical padding/margins: sticky/fixed headers (`padding-top: max(…, env(safe-area-inset-top))`), fixed/sticky bottom CTAs and controls (`padding-bottom: max(…, env(safe-area-inset-bottom))`), edge-to-edge footers, `<dialog>` panels, and any content flush to the left/right edges on landscape (`env(safe-area-inset-left/right)`).
  - Without this, `viewport-fit=cover` lets notches, rounded corners, and gesture-navigation bars obscure text and controls — readable/activatable targets are a hard requirement, so an unhandled inset is a generation failure.
  - Test both portrait and landscape on representative cutout/gesture-navigation viewports (e.g. Chrome DevTools device emulation with safe-area insets); verify no essential content or control sits under an inset.

## 6. FORBIDDEN
- External JS libraries (jQuery, React, Vue, etc.)
- External CSS frameworks (Bootstrap, Tailwind)
- SVG images
- External fonts
- iframe (exceptions: maps — ONLY via the facade pattern, a local screenshot in the initial DOM with the iframe inserted on explicit user activation (§10); YouTube video — via the facade pattern by default, or as a first-load embed ONLY under the explicitly documented SEO-discoverable mode chosen in the brief (§9 Mode S). A native `loading="lazy"` map iframe is NOT an exception — it can load automatically when approaching the viewport, without any click)
- `document.write()`, synchronous scripts

## 7. TESTING — executable validation contract
Validation is a set of pinned, runnable gates. Every gate prints/runs an exact command, produces a measured result, and either passes, fails, or reports an explicit BLOCKER. A gate that cannot run (missing tool, no served URL) is a BLOCKER — never an estimated or fabricated pass.

Prerequisites: `curl`, `python3` ≥ 3.10; URL gates additionally need Node.js ≥ 22.19 (`npx`) and Chrome/Chromium (override the binary with `CHROME_PATH`). This matches the pinned Lighthouse 13.4.1 package's supported Node runtime.

Serving requirement: URL gates run against a served or deployed page, never against a file path. Serve the project directory (e.g. `python3 -m http.server 8000` inside it → `http://localhost:8000/index.html`) or use the deployed URL.

1. **W3C HTML validity** (pass = zero `"type": "error"` messages):
   `curl -sS -H "Content-Type: text/html; charset=utf-8" --data-binary @index.html "https://validator.w3.org/nu/?out=json"`
   Offline fallback (needs Node + Java): `npx vnu-jar index.html`.
2. **Local asset existence**: run `python3 <skill-path>/scripts/validate_assets.py <site-document-root> --html index.html --page-url https://site.com/`. Supply the real canonical page URL (including its path) and HTML path relative to the document root. The checker covers resource `src`/`srcset`, preload/icon/stylesheet links, OG/Twitter images, inline CSS and recursive CSS `url()`/imports. Same-origin absolute HTTPS and root-relative URLs map to local files; never skip them merely because they are absolute. Missing files or paths escaping the root fail with exit 1. Remote-origin URLs and navigational links need separate deployed HTTP checks; data/fragment references do not require files. `<base>` is rejected rather than silently resolving URLs incorrectly. No network requests are made by this checker.
3. **JSON-LD syntax**: parse every `application/ld+json` block as JSON (e.g. `python3 -m json.tool`). Syntax validity is NOT Google rich-result eligibility — eligibility is a separate Rich Results Test / URL Inspection step on the deployed page, and valid syntax alone is never reported as an achieved search feature.
4. **Responsive layout**: headless Chrome screenshots at 320, 768, 1280, and 1920px — e.g. `chrome --headless=new --window-size=320,900 --screenshot=viewport-320.png <url>` — inspected for horizontal overflow, reflow, and broken controls at each width (320–1920 support per §2). RTL documents are additionally inspected per §2: RTL text containing Latin-script URLs, phone numbers, forms, and controls must render correctly at mobile and desktop widths.
5. **Lighthouse (lab measurement)**: pinned version and profile — `npx -y lighthouse@13.4.1 <url> --only-categories=performance,accessibility,best-practices,seo --output=json --output=html --output-path=reports/run-N` (mobile emulation, simulated throttling — Lighthouse defaults: 412×823 viewport, DPR 1.75, 150 ms RTT, 4× CPU slowdown). Run 3 times, aggregate the MEDIAN per category, threshold ≥ 90, artifacts kept at `reports/run-{1..3}.report.{json,html}` in the project folder. Lighthouse is lab evidence — never field Core Web Vitals (see README benchmark disclosure), and never WCAG certification.
6. **Crawlability**: parse `sitemap.xml`, compare every `<loc>` with the HTML canonical, check the `Sitemap:` URL in `robots.txt`, and request both deployed files (HTTP 200).
7. **Manual accessibility checks** (§8) — no automated gate replaces them.

Failure behavior: fix every gate failure before reporting. Report each number with the exact command and artifact path that produced it; where a gate cannot run, report `BLOCKER: <reason>` in place of a number. Never output a PageSpeed/LCP score that was not actually measured on the served page.

Negative fixture: `tests/fixtures/broken-landing/index.html` ships three intentional failures — a duplicate attribute (gate 1), a reference to a missing image file (gate 2), and a trailing comma in JSON-LD (gate 3). Gates 1–3 must each FAIL on it; a gate that passes the fixture is itself broken and must be fixed before any project validation is trusted.

## 8. ACCESSIBILITY AND INCLUSIVITY
- WCAG 2.1 Level AA compliance
- Text contrast ratio at least 4.5:1
- Non-text contrast at least 3:1 against adjacent colors (WCAG SC 1.4.11) for control boundaries, state indicators, focus indicators, and meaningful graphics needed to identify components or states. Validate the default, hover, `:focus-visible`, selected/expanded, error, and disabled states as applicable; record an exception only where the WCAG criterion itself excludes the component or state.
- `prefers-reduced-motion` support covers every permitted animation: gate nonessential CSS/JS animation behind `@media (prefers-reduced-motion: no-preference)` or provide a `reduce` branch that disables/replaces it. In reduced mode render final counter values without animated counting, avoid smooth/programmatic scrolling, and keep functional state cues that do not rely on motion. Test the reduced preference across every optional animation and interactive state.
- All interactive elements keyboard accessible
- Manual accessibility verification is required before claiming WCAG 2.1 AA — no automated tool alone determines conformance (W3C). Required manual checks: keyboard navigation, focus order and visibility, dialog/modal focus flow, zoom/reflow, reduced motion, semantic name-role-value, alternative-text quality, and all interactive visual states. Lighthouse accessibility output is automated audit evidence, not certification. Record pass/fail evidence per applicable WCAG 2.1 AA criterion and report unresolved items rather than silently certifying them.

## 9. EMBEDDED VIDEO (facade by default; SEO-discoverable mode opt-in)

### Video modes — chosen in the brief, trade-off stated in the report
Google discovers videos through `<video>`, `<embed>`, `<iframe>`, and `<object>` elements present in the RENDERED HTML, and warns that video loading must not depend on user actions such as clicking, scrolling, or typing (developers.google.com/search/docs/appearance/video). The mode is collected in the brief and disclosed in the final report — never switched silently.

- **Mode F — click-only facade (default).** The facade rules below. Buys zero third-party requests before activation and avoids ~0.5–1 MB of player JS on load; the price is explicit: the rendered HTML contains no video element before activation, so the page does NOT satisfy Google's video discovery requirements. Make no video-discovery or video-feature claims for Mode F pages; `VideoObject` there is optional metadata, reported as metadata-only (see the reporting gate below).
- **Mode S — SEO-discoverable (opt-in, when video search traffic matters).** The video element must exist in the rendered HTML without any user action. Two supported variants:
  - **S1 — self-hosted `<video>` (preferred):** a first-party `<video>` element with a Google-supported container format (MP4/WebM among them), a stable video URL, a `poster` thumbnail, numeric dimensions, and no user-action gate. Stays fully compatible with the zero-third-party-requests policy; the cost is hosting/bandwidth for the video file, and Googlebot must be able to fetch it (never blocked in robots.txt).
  - **S2 — direct `<iframe>` embed:** the YouTube (nocookie) iframe sits in the initial HTML, discoverable via `<iframe>` in the rendered HTML. It IS a first-load third-party dependency: record it in the dependency manifest (§11), add the CSP `frame-src` entry, and stop claiming "zero third-party requests on first load" for that page. The relaxation is explicit and documented, never silent.
  - Watch-page honesty: Google further recommends a dedicated watch page for video-feature eligibility (key moments, previews, live badge) and does not count pages where the video merely supplements other content — most landings are exactly that. Even Mode S on a landing makes the video DISCOVERABLE; feature eligibility may additionally require a real watch page, which is outside a single-landing project unless the user builds one.

### Facade rules (Mode F)
- Forbidden to load a YouTube iframe on page load — only on user click.
- Before the click show ONLY the video cover:
  - `<picture>` with a local cover in AVIF/WebP + JPEG fallback (no hotlinking from i.ytimg.com — extra domain, blocked by ad blockers);
  - width-descriptor `srcset` (320–1920w per §1 breakpoints) plus an accurate `sizes` derived from the facade container, on every `<source>` and the `<img>`;
  - numeric width/height + CSS `aspect-ratio: 16/9` (CLS prevention);
  - `decoding="async"`;
  - loading by placement, never hardcoded: when the cover is the LCP element or sits above the fold, load it eagerly (no `loading` attribute) with `fetchpriority="high"`; use `loading="lazy"` only when the video block is below the fold. Verify candidate selection at representative 320, 640, 1024, and 1920px viewports — each must pick the intended candidate, not an oversized one.
- Play button over the cover:
  - a real `<button>` (not a div), keyboard accessible (Enter/Space);
  - `aria-label="Watch video: <title>"`;
  - play icon — CSS only (no SVG, forbidden) or a raster image;
  - visible `:focus-visible`.
- On click/Enter remove the cover and button, insert an `<iframe>` in their place:
  - `src="https://www.youtube-nocookie.com/embed/<ID>?autoplay=1"` (privacy-enhanced mode);
  - `title="Video title"` (mandatory for accessibility);
  - `referrerpolicy="strict-origin-when-cross-origin"` (YouTube requires Referer identity; origin only, no path/query);
  - `loading="lazy"`, `allowfullscreen`;
  - `allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"`;
  - move focus to the iframe after insertion.
- No preconnect or other early contact with `https://www.youtube-nocookie.com`: a hover/focus preconnect performs third-party DNS/connection work before user intent and exposes the visitor's network address to that origin, contradicting the zero-requests-before-activation guarantee. The first contact with the YouTube origin is the iframe insertion on activation. Keyboard (Enter/Space) and pointer activation follow the same network policy — one delegated click handler covers both.
- Network test (browser, before reporting): open DevTools Network, filter `youtube-nocookie.com`, load the page, hover and keyboard-focus the cover without activating — zero requests; activate — the embed request appears.
- All pattern scripts — in one file with `defer` before `</body>`, no external libraries; for multiple videos use one delegated handler.
### VideoObject and discovery verification (mode-gated)
- `@type: VideoObject` (name, description, thumbnailUrl, uploadDate, embedUrl/contentUrl) is emitted only when all required facts are collected and source-backed: the video URL/ID, title, description, accurate ISO-8601 `uploadDate` with timezone, and a unique crawlable thumbnail. Never invent media facts; users must be able to watch that specific video on the page. Validate syntax with Rich Results Test and verify the thumbnail returns 200.
- Reporting is gated by the chosen mode. Mode F: report `VideoObject` strictly as optional metadata — the page does not satisfy Google's discovery requirements, so no video-search benefit is claimed. Mode S: report it as discovery-supporting metadata only after the rendered-HTML check below passes.
- Discovery evidence (Mode S): verify a video element (`<video>`/`<iframe>`/`<embed>`/`<object>`) is present in the RENDERED HTML — URL Inspection "rendered HTML" on the deployed page, or a headless rendered-DOM dump of the served page. JSON-LD syntax validity alone is NEVER evidence of discovery or feature eligibility. With Search Console access, the Video Indexing report is the follow-up evidence; without it, say so — never estimate.
- Reference implementation: [video-facade.md](./video-facade.md)

## 10. TYPICAL BLOCKS WITHOUT SPEED LOSS
- FAQ / accordion: `<details>/<summary>` — 0 bytes of JS, content immediately in the DOM (good for AEO).
- Slider / carousel: prefer a plain linear list when horizontal interaction is not essential. When the result is a carousel (W3C APG carousel pattern), CSS `scroll-snap` may serve as the scrolling mechanism, but the carousel additionally needs: a labeled container, named slides, native previous/next `<button>` controls (a few `scrollBy` lines in the common script), and keyboard traversal between slides. Auto-rotation is forbidden by default; if explicitly enabled, add a stop/start control first in tab order and stop rotation whenever focus enters the carousel. Test keyboard-only, touch, screen-reader, and 320px behavior.
- Tabs: CSS-only (radio inputs) or ~15 lines of JS; content of all tabs always in the DOM.
- Modal window: native `<dialog>` opened with `showModal()` — `.show()` or a static `open` attribute is not modal. Provide a visible title that serves as the accessible name, a visible keyboard-operable close/cancel control, and Escape support (native `cancel` event). Verify the focus flow: focus moves into the dialog on open, stays inside while it is open, and returns to the invoking control on close. Do not add redundant ARIA to the native `<dialog>` just to satisfy an ARIA rule (§4). Loads nothing on start.
- Map: facade like video (§9) — a local map screenshot in the initial DOM, the provider iframe inserted only on explicit user activation. The iframe `src` must be absent from the DOM until activation (a native `loading="lazy"` iframe can load on scroll proximity without any click and is forbidden). The activation control is a real keyboard-accessible `<button>` with a visible label naming the action and provider; after insertion the iframe carries a `title`, and focus moves into it. Network test: filter the provider domain in DevTools, load the page and scroll past the block — zero requests; activate — the embed request appears. Reference implementation: [map-facade.md](./map-facade.md)
- Reviews: static HTML, no widgets. `Review`/`AggregateRating` JSON-LD only under the §3 gates: never self-serving for the represented business, only source-backed facts, visible-page parity.
- Form: native validation (`required`, `type="email"`), honeypot field against spam, no external form builders. Every user-facing control gets a visible label programmatically associated via `<label for>` (not placeholder-only), plus any required format/instruction text. Personal-data fields carry the correct standardized `autocomplete` token where the WCAG 2.1 input-purpose taxonomy applies (e.g. `name`, `email`, `tel`, `street-address`). The honeypot stays out of the accessibility tree and tab order (`tabindex="-1"`, `aria-hidden="true"`, visually hidden) and is never given an `autocomplete` value that browsers could autofill. Validate autocomplete values and test browser autofill plus assistive-technology exposure.
- Form submission contract — a form that cannot deliver a lead is a generation failure:
  - Collect the submission destination and method in the brief BEFORE generating the form: an endpoint URL with its HTTP method (e.g. a first-party handler `POST /api/lead`, or a documented third-party form service), or an explicit statement that no backend exists. Never invent an endpoint.
  - No backend exists → omit the form, or ship it as an explicitly labeled stub (visible note or documented TODO) until a destination is provided. A form whose submission defaults to the current page and delivers nothing anywhere is forbidden.
  - Field contract: define the exact field set (name, type, required/optional) in the brief; the server-side handler validates the same contract independently of browser validation — client-side checks are UX, never a security boundary.
  - Honeypot handling: the server silently accepts but discards submissions with a filled honeypot field (no error response that would teach bots), while genuine validation errors return a recoverable error state.
  - Consent and privacy: when the form collects personal data, include the required consent/privacy text (e.g. a consent checkbox with a link to the privacy policy) as collected in the brief — never invent legal copy; omit the form or the field when the required text is unavailable.
  - Success/error UX: define and implement both outcomes — a visible success confirmation (no silent success) and a visible, recoverable error state that keeps the entered data and lets the user retry. Duplicate submissions (double-click, retry) must not create duplicate leads — the handler is idempotent or guarded.
  - Data ownership: record where submissions are stored and who owns/controls that data (first-party endpoint vs third-party service) in `SERVER-SETUP.md`; a third-party form service is additionally a documented dependency (§11 manifest) and loads only under its activation/consent rules.
  - End-to-end test (before reporting): submit a valid test entry and verify delivery at the destination (received email, database row, or service dashboard). Submit a genuinely invalid entry and verify a visible recoverable error that preserves user input. Separately submit a honeypot-filled entry: verify the neutral outward success response and confirm that no lead is stored or delivered; do not show a honeypot-specific error. Record evidence for all three paths. A form with an untested delivery path is a blocker, not done.
- Scroll counters and animations: one `IntersectionObserver` in the common script; animations only via `transform`/`opacity` and always inside the §8 reduced-motion gate — counters render their final value instantly and scrolling is never smoothed when the user prefers reduced motion.
- Sticky header: `position: sticky` — pure CSS, no JS listeners.
- Back-to-top button: anchor link or 5 lines of JS.
- General rules:
  - total page JS budget ≤ 15 KB, one file, `defer` before `</body>`;
  - one delegated handler for all interactivity;
  - 1 block = 0 external requests: no block may pull a script/style/widget from a third-party domain;
  - content always in the DOM: load on click only heavy media (video, maps);
  - forbidden on first load: third-party widgets, scroll-jacking, JS parallax.

## 11. DEFERRED WIDGETS (online chats, subscription popups, cookie banners)
- Forbidden to load their scripts/styles on first load — async only.
- Consent gate (default-off): nonessential third-party widgets never load on a timer alone.
  - Consent states: `none` (fresh visitor, no choice made), `accepted`, `rejected`; revoking returns the state to `none`. Persist the state in first-party `localStorage` under a documented key with a timestamp.
  - The consent UI (cookie banner) is first-party only: own block (~20 lines of CSS + 5 lines of JS for localStorage), no third-party services, zero third-party requests from the banner itself; show only if consent has not been given yet.
  - A nonessential external widget script loads only after one of: (a) the visitor makes the affirmative applicable consent choice (`accepted`), or (b) the visitor explicitly activates that feature (e.g. clicks the chat launcher — explicit activation is an affirmative choice for that widget).
  - Rejection keeps the widget unloaded; revocation removes the inserted widget (remove its script/iframe/container where feasible) and clears the stored choice.
  - The deferred timer may prepare first-party UI only — it must never create a third-party `<script>` on its own:

```javascript
document.addEventListener('DOMContentLoaded', function () {
  setTimeout(function () {
    // First-party only: show the consent banner when no choice exists yet.
    // Third-party widget scripts are inserted only after consent or
    // explicit feature activation — never by this timer.
    if (localStorage.getItem('consent') === null) showConsentBanner();
  }, 1000);
});
```

- Insert widget scripts dynamically (`createElement` + `appendChild`) with async/defer attributes, never as a static tag in `<head>`.
- Online chat and subscription popup: if it is a third-party service — load its script only per the consent gate above; the widget container must not reserve space before loading (no CLS).
- All deferred widgets: keyboard accessible, closable with Esc, carry only the ARIA needed beyond native semantics (§4), and show visible `:focus-visible`.
- Popups must not cover first-screen content and must not shift the layout.
- Budget honesty: the 15 KB JS budget (§10) and the "zero third-party dependencies" claim describe the FIRST LOAD of the generated page. Deferred third-party widget scripts are not counted against the 15 KB budget — but they ARE third-party dependencies, and any page shipping them must say so: they are documented in the dependency manifest (§11 governance), loaded only under the consent gate, and the page must never be marketed as having "zero third-party dependencies" unqualified. Qualify the claim as "zero third-party requests on first load" whenever deferred widgets exist.
- Network tests (browser, per state, before reporting): with DevTools filtered to third-party domains — (a) fresh visitor: no widget requests before any choice; (b) rejected: none at all; (c) accepted: widget requests appear only after the choice; (d) revoked: widget removed and no further requests. The consent banner itself must produce zero third-party requests in every state.
- Third-party code governance — every external script or iframe gets a per-page dependency manifest entry (in the project's `SERVER-SETUP.md` or a dedicated `DEPENDENCIES.md`): origin, exact path and version, purpose, owner/approver, activation moment (first load vs deferred), its CSP destination (`script-src`/`frame-src`/`connect-src` hash or host entry), and known subrequests it triggers. No undocumented third-party dependency may ship.
- Subresource integrity: third-party scripts loaded from a stable, versioned URL must carry `integrity` (sha384/sha512) plus `crossorigin="anonymous"`. A documented exception is allowed only when the vendor URL is mutable (no stable hash possible) — record the reason in the manifest and prefer self-hosting a pinned copy.
- Referrer: every third-party request gets an explicit referrer policy — `referrerpolicy="no-referrer"` (or `strict-origin-when-cross-origin` where the vendor requires the origin), set per element; never rely on the page default leaking full URLs to vendors.
- Iframe sandboxing: third-party iframes get the MINIMUM `sandbox` token set that keeps the feature working, or a documented incompatibility reason in the manifest (e.g. a vendor player that breaks under sandbox). The default is the most restrictive set that still functions; `allow-same-origin allow-scripts` together is treated as no sandbox and requires explicit justification.
- Verification: (a) serve a script with a wrong `integrity` hash and confirm the browser blocks it; (b) confirm third-party requests carry the configured referrer (or none) in the network panel; (c) for every embedded player/map: playback or map interaction works, and fullscreen works where offered.

## 12. CONTENT TRUTHFULNESS & PROVENANCE
- Never invent objective marketing facts: numerical results, prices, availability, credentials, certifications, comparisons, guarantees, customer logos/cases, or regulated claims.
- Every objective claim in the generated copy must trace back to approved source material collected in the brief, with an identified claim owner. Self-check before the stop point: list each objective claim and its source; a claim without a source is requested from the user or omitted — never silently filled with generated copy.
- Health, financial, legal and other sensitive claims additionally require an identified subject-matter or legal reviewer appropriate to the target jurisdiction before publication.
- When evidence is missing, report a blocker instead of publishing unsupported claims.
- Image rights and provenance: for every asset used on the page (photos, logos, video covers, and all generated derivatives such as AVIF/WebP conversions) record in an `ASSETS.md` manifest: creator/rightsholder, source, license or permission, allowed reproduction/adaptation, attribution, territory, and expiry where applicable. Public availability of an image is not permission to copy or transform it — exclude or replace assets whose clearance is unavailable. Every generated derivative must link back to its provenance record. The manifest records supplied rights assertions and does not replace jurisdiction-specific legal advice.

## 13. INPUT SANITIZATION & OUTPUT ENCODING
Every value collected in the brief (domain, keywords, business name, address, contacts, media IDs, any free-text field) is UNTRUSTED input by default. Encode it for its exact output context — never copy a raw value into markup (OWASP XSS prevention):
- HTML element content: escape `& < > " '` as HTML entities.
- Attribute values: always quoted, attribute-escaped; never place untrusted data in event-handler attributes (`onclick` etc.) at all.
- URL contexts (`href`, `src`, canonical, OG/JSON-LD URLs): validate the scheme against an allow-list of `https` (and `http` only where the brief requires it); REJECT `javascript:` and unexpected `data:` URLs outright — do not attempt to "clean" them.
- JSON-LD: serialize with a JSON encoder, then additionally escape `<` (e.g. as `\u003c`) so embedded data can never terminate the `<script>` element — JSON escaping alone does not protect the HTML script context.
- Structured identifiers are validated against their exact format before use in any URL built at runtime: a YouTube video ID must match `^[A-Za-z0-9_-]{11}$`; a malformed ID is a generation error, not a value to embed (see references/video-facade.md).
- Generation self-test: run the generator with hostile brief values — quotes, angle brackets, a literal `</script>`, an `onerror=`/`onload=` payload, and `javascript:`/`data:` URLs. The output must remain valid HTML and execute none of them; a value that cannot be encoded safely for its context is rejected or omitted, never emitted raw.

## OUTPUT — canonical workflow order
Generate the complete multi-file project complying with ALL points above: `index.html`, every local asset it references (all image variants at every declared breakpoint, favicon), `styles.css` only when below-the-fold CSS is deferred, the single `script.js` only when JS is used, plus `robots.txt`, `sitemap.xml`, `ASSETS.md`, and `SERVER-SETUP.md`. A referenced file that is never created is a generation failure — produce it, or remove the reference (and request missing source images from the user rather than inventing URLs).

One canonical sequence, shared with SKILL.md and README — do not reorder:
1. Generate the draft, then self-check it against every requirement in this spec; fix violations before showing the draft.
2. STOP POINT — show the draft to the user and ask explicitly whether the HTML version is OK. Do not run validation and do not report any metrics before the user approves.
3. After approval: serve the page, then run the executable validation contract (§7) — local asset/link existence (every local URL referenced by the output resolves to a real file in the project folder; any miss is a hard failure), W3C HTML validity, JSON-LD syntax, responsive screenshots, Lighthouse (pinned version, 3 runs, median, artifacts kept), the crawlability contract, and the manual accessibility checks in §8.
4. Fix any failures found. If fixes change the approved HTML, obtain renewed approval before reporting.
5. Final report — measured evidence only: LCP parameters, PageSpeed scores, schema.org types used.

Rules:
- Never claim LCP/PageSpeed numbers before the corresponding check has actually run on the served page.
- Every reported number is disclosed with the exact command and artifact path that produced it; a gate that could not run is reported as `BLOCKER: <reason>` instead of a number. A score that was not measured is never reported.
