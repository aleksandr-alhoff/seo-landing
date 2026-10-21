# Server Setup — Caching, Compression, Security Headers

Include these instructions in the project's `SERVER-SETUP.md`.

## Apache (.htaccess)

```apache
# Compression: Brotli preferred, gzip fallback
<IfModule mod_brotli.c>
  AddOutputFilterByType BROTLI_COMPRESS text/html text/css application/javascript application/json image/svg+xml
</IfModule>
<IfModule mod_deflate.c>
  AddOutputFilterByType DEFLATE text/html text/css application/javascript application/json image/svg+xml
</IfModule>

# Mark compressed responses so caches vary on Accept-Encoding
<IfModule mod_headers.c>
  <FilesMatch "\.(html|css|js|json|svg)$">
    Header append Vary "Accept-Encoding"
  </FilesMatch>
</IfModule>

# Caching — Cache-Control (mod_headers) is authoritative; no Expires headers.
# `immutable` is allowed ONLY for fingerprinted assets: the generator renames
# each static asset with a content-hash fragment (styles.a1b2c3d4.css) and
# updates every HTML reference on change. A stable (unhashed) URL must never
# be `immutable`: after the file is overwritten, a compliant cache may keep
# serving the old bytes for the entire max-age (RFC 9111).
<IfModule mod_headers.c>
  # Stable (unhashed) asset URLs: may be stored but must revalidate on reuse
  <FilesMatch "\.(avif|webp|jpg|jpeg|png|css|js)$">
    Header set Cache-Control "no-cache"
  </FilesMatch>
  # Fingerprinted URLs (>=8 hex chars before the extension): 1 year, immutable
  <FilesMatch "\.[0-9a-f]{8,}\.(avif|webp|jpg|jpeg|png|css|js)$">
    Header set Cache-Control "public, max-age=31536000, immutable"
  </FilesMatch>
  # HTML: revalidate every time
  <FilesMatch "\.html$">
    Header set Cache-Control "max-age=0, must-revalidate"
  </FilesMatch>
  # robots.txt and sitemap.xml: exact files, never immutable (see the
  # "robots.txt & sitemap.xml caching" section below). These match by exact
  # filename, so they are not caught by the extension rules above.
  <Files "robots.txt">
    Header set Cache-Control "no-cache"
  </Files>
  <Files "sitemap.xml">
    Header set Cache-Control "no-cache"
  </Files>
</IfModule>

# Serve HTML as UTF-8
AddDefaultCharset utf-8
<IfModule mod_mime.c>
  AddCharset utf-8 .html .css .js .xml .json
  # Fallbacks for hosts whose MIME map lacks modern image types
  AddType image/avif .avif
  AddType image/webp .webp
</IfModule>

<IfModule mod_headers.c>
  # Security headers — `always` so they are also present on locally generated
  # responses: error pages (404/500), internal redirects, subrequests.
  # Use exactly this form (never a bare `Header set` alongside it) so headers
  # are set once and are not duplicated.
  Header always set X-Content-Type-Options "nosniff"
  Header always set X-Frame-Options "DENY"
  Header always set Permissions-Policy "camera=(), microphone=(), geolocation=()"
  Header always set Referrer-Policy "strict-origin-when-cross-origin"
</IfModule>
```

## Nginx

### Brotli prerequisite — the module must exist before these directives
`brotli`/`brotli_types` are NOT part of stock Nginx. On a build without the
module, `nginx -t` fails with `unknown directive "brotli"` and Nginx will not
start. Before including the Brotli lines, confirm the module is present
(https://github.com/google/ngx_brotli):

```bash
# Does this build know the brotli directives? (fails on stock builds)
nginx -t 2>&1 | grep -i 'unknown directive' ; echo "exit: $?"
# Which modules were compiled in / available?
nginx -V 2>&1 | tr ' ' '\n' | grep -i brotli
```

Install paths (pick one, matching the host):
- Distribution package that ships the module (e.g. Debian/Ubuntu
  `libnginx-mod-brotli` where available) — enable it and keep the package
  name/version in `SERVER-SETUP.md`.
- Dynamic build: compile with `--add-dynamic-module=.../ngx_brotli`, then load
  it in the MAIN context of `nginx.conf`, before any `http` block:
  ```nginx
  load_module modules/ngx_http_brotli_filter_module.so;
  load_module modules/ngx_http_brotli_static_module.so;
  ```
- Static build: compile Nginx with `--add-module=.../ngx_brotli` (directives
  then need no `load_module`).

If the module cannot be installed on the target host: REMOVE the `brotli`
lines entirely, ship gzip-only, and record that in the checklist — never leave
directives that fail `nginx -t`, and never claim Brotli when only gzip is
served. Apache behaves differently: the `<IfModule mod_brotli.c>` block is
silently skipped when the module is absent, so the checklist must likewise be
marked gzip-only (mod_brotli requires Apache ≥ 2.4.26).

```nginx
# Only when the ngx_brotli module is installed and loaded (see above):
brotli on;
brotli_types text/html text/css application/javascript application/json image/svg+xml;
gzip on;
gzip_vary on;
gzip_types text/html text/css application/javascript application/json image/svg+xml;
# ngx_brotli does not add Vary itself; if Brotli is served, ensure responses
# carry exactly one Vary: Accept-Encoding (e.g. via a map on $http_accept_encoding
# or CDN rules) without duplicating the value gzip_vary already adds.

# Security headers live in ONE shared file that is included at every level
# that carries its own add_header. Nginx inherits parent add_header values
# only when the child level defines NONE of its own — a location with a
# Cache-Control add_header would otherwise silently lose all security headers.
# Create conf.d/security-headers.conf containing exactly (a relative include
# path resolves against the nginx prefix — /etc/nginx on packaged installs;
# use an absolute path in every include below if your layout differs):
#   add_header X-Content-Type-Options "nosniff" always;
#   add_header X-Frame-Options "DENY" always;
#   add_header Permissions-Policy "camera=(), microphone=(), geolocation=()" always;
#   add_header Referrer-Policy "strict-origin-when-cross-origin" always;

# Cache-Control: `immutable` is allowed ONLY for fingerprinted assets — the
# generator renames each static asset with a content-hash fragment
# (styles.a1b2c3d4.css) and updates every HTML reference on change. Never mark
# a stable (unhashed) URL `immutable`: after the file is overwritten a
# compliant cache may keep serving the old bytes for the entire max-age
# (RFC 9111). Stable URLs get a revalidation policy instead.
# ORDER MATTERS: Nginx serves the FIRST matching regex location, so the
# fingerprinted rule must come before the generic asset rule — otherwise
# every fingerprinted file matches the generic rule and never gets immutable.
location ~* "\.[0-9a-f]{8,}\.(avif|webp|jpg|jpeg|png|css|js)$" {
  try_files $uri =404;
  # No `always`: missing assets must not receive a year-long cache policy.
  add_header Cache-Control "public, max-age=31536000, immutable";
  include conf.d/security-headers.conf;
}
location ~* \.(avif|webp|jpg|jpeg|png|css|js)$ {
  add_header Cache-Control "no-cache" always;
  include conf.d/security-headers.conf;
}
location ~* \.html$ {
  add_header Cache-Control "max-age=0, must-revalidate" always;
  include conf.d/security-headers.conf;
}
# robots.txt and sitemap.xml: EXACT-path locations, never immutable (see the
# "robots.txt & sitemap.xml caching" section below). Exact `location =` blocks
# win over the regex asset rules above, so these files can never inherit an
# immutable policy.
location = /robots.txt {
  add_header Cache-Control "no-cache" always;
  include conf.d/security-headers.conf;
}
location = /sitemap.xml {
  add_header Cache-Control "no-cache" always;
  include conf.d/security-headers.conf;
}

# Serve HTML/CSS/JS as UTF-8
charset utf-8;
charset_types text/html text/css application/javascript application/json;

# Server-level security headers (inherited by locations without their own
# add_header; locations above re-include the file explicitly).
include conf.d/security-headers.conf;
```

## HTTPS enforcement (HTTP → HTTPS redirect)

Prerequisites: a valid TLS certificate for the canonical host must already be
installed and the HTTPS endpoint must serve the site successfully before the
redirect is enabled. Behind a reverse proxy/CDN (Cloudflare, ALB, etc.) the
redirect may be terminated at the edge — apply the same rule there and make
sure the edge forwards the original scheme/host (e.g. `X-Forwarded-Proto`) if
the origin decides on the redirect.

The redirect must be a permanent `301` (or `308`, which additionally preserves
the request method), must preserve host, path, and query string, and must point
at the canonical host chosen for the project (e.g. always `https://site.com/…`
or always `https://www.site.com/…` — one canonical host, matching the HTML
canonical URL).

### Apache — port-80 virtual host

```apache
<VirtualHost *:80>
  ServerName site.com
  ServerAlias www.site.com
  # Preserve host, path and query; normalize to the canonical host
  Redirect permanent / https://site.com/
</VirtualHost>
```

`Redirect permanent` issues a 301 and appends the request path and query
automatically. If the canonical host equals the requested host and only the
scheme must change, `RewriteEngine On` +
`RewriteRule ^ https://%{HTTP_HOST}%{REQUEST_URI} [L,R=301]` is the
equivalent (requires `mod_rewrite`).

### Nginx — port-80 server block

```nginx
server {
  listen 80;
  listen [::]:80;
  server_name site.com www.site.com;
  # 301 to the canonical host, preserving path and query string
  return 301 https://site.com$request_uri;
}
```

### Verification
```bash
curl -I 'http://site.com/path?q=1'
# Expected: one 301/308 with Location: https://site.com/path?q=1
curl -I 'https://site.com/'
# Expected: 200 over HTTPS with the security headers present
```

## Content-Security-Policy (generated per page)

CSP cannot be bolted on generically — the policy is GENERATED from the exact
features the page uses (OWASP recommends CSP as defense-in-depth against
XSS/data injection, delivered via response header). The generated page keeps
CSP-compatible by design: no inline event handlers, no inline scripts (the
single page script is an external file with `defer`), inline CSS only in
`<style>` blocks, JSON-LD as non-executable `application/ld+json`.

Build the policy from this restrictive base, adding destinations only for
features that exist on the page:

```
default-src 'self';
script-src 'self';
style-src 'self' 'sha256-<hash>';
img-src 'self' data:;
font-src 'self';
connect-src 'self';
object-src 'none';
base-uri 'self';
form-action 'self';
frame-ancestors 'none'
```

Feature-specific additions:
- Inline `<style>` blocks (critical CSS): authorize each block with its
  `sha256-` hash in `style-src` — compute the hash of the exact emitted CSS.
  Never fall back to `style-src 'unsafe-inline'` as the default; and NEVER use
  `unsafe-inline` or `unsafe-eval` for `script-src`.
- YouTube facade block present: add `https://www.youtube-nocookie.com` to
  `frame-src` (iframe inserted on click). `connect-src` needs no YouTube entry
  — the facade performs no fetch/preconnect to that origin before activation.
  Omit the entry when the page has no video.
- Form submitting to an external endpoint from the brief: extend
  `form-action` with that exact origin. Default is `'self'`.
- `data:` in `img-src` covers base64 LQIP placeholders; drop it when unused.

Rollout — report-only first, then enforce:
1. Deploy `Content-Security-Policy-Report-Only` with the generated policy.
2. Exercise every generated feature combination in a real browser (video
   click-through, form, deferred CSS path) and fix every reported violation.
3. Switch the same policy to the enforcing `Content-Security-Policy` header
   and re-test. Keep report-only available for future feature changes.

Apache (inside the existing `<IfModule mod_headers.c>`):

```apache
Header always set Content-Security-Policy-Report-Only "<generated policy>"
# After a clean report-only rollout, replace with:
# Header always set Content-Security-Policy "<generated policy>"
```

Nginx — add to `conf.d/security-headers.conf` so it follows the same
inheritance rules as the other headers (§ above):

```nginx
add_header Content-Security-Policy-Report-Only "<generated policy>" always;
# After a clean report-only rollout, replace with:
# add_header Content-Security-Policy "<generated policy>" always;
```

## Strict-Transport-Security (HSTS) — HTTPS only, staged rollout

HSTS (RFC 6797) makes browsers upgrade later HTTP attempts before sending
them and blocks certificate-warning bypass. It SUPPLEMENTS the #12 redirect —
it never replaces it (the very first request still needs the redirect).

Rollout rules:
- Emit the header ONLY on HTTPS responses — never on the port-80 redirect
  response (browsers ignore it there, and a misconfigured HTTP copy can poison
  caches).
- Start with a short `max-age` (e.g. 300 seconds). Adopt the long lifetime
  (e.g. `max-age=31536000`) only after the HTTPS deployment runs cleanly.
- Add `includeSubDomains` only when EVERY applicable subdomain serves HTTPS.
- `preload` (hstspreload.org submission) is an explicit, warned opt-in: it is
  hard to undo and affects every browser's preload list — record the user's
  explicit decision before adding it.

Apache — inside the HTTPS virtual host only (NOT in the port-80 vhost):

```apache
# Phase 1: short trial
Header always set Strict-Transport-Security "max-age=300"
# Phase 2 (after clean rollout):
# Header always set Strict-Transport-Security "max-age=31536000; includeSubDomains"
```

Nginx — create a separate `conf.d/hsts-https.conf` file:

```nginx
# Phase 1: short trial
add_header Strict-Transport-Security "max-age=300" always;
# Phase 2 (after clean rollout):
# add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
```

Include `conf.d/hsts-https.conf` inside the `listen 443 ssl` server block
AND inside every HTTPS location that declares any `add_header`, including
each asset, HTML, robots.txt and sitemap.xml location shown above. Nginx does
not inherit the server's HSTS when a child defines its own headers. Never add
this include to the shared security-headers file used by HTTP, or to the
port-80 server. Verify `/`, HTML, an asset and a 404 over HTTPS each carry
exactly one HSTS header; the HTTP redirect carries none.

Verification:
```bash
curl -I 'https://site.com/'   # Header present exactly once
curl -I 'http://site.com/'    # Header ABSENT on the redirect response
```

## MIME types — every generated resource class must be served correctly

With `X-Content-Type-Options: nosniff` enabled, a wrong `Content-Type` is an
operational failure (browsers refuse mistyped CSS/JS), and wrong XML/image
types can impair crawling and rendering. Expected types for everything this
skill generates:

| Resource | Content-Type |
|---|---|
| HTML page | `text/html; charset=utf-8` |
| CSS | `text/css; charset=utf-8` |
| JavaScript | `application/javascript; charset=utf-8` (or `text/javascript`) |
| AVIF | `image/avif` |
| WebP | `image/webp` |
| JPEG | `image/jpeg` |
| PNG | `image/png` |
| robots.txt | `text/plain; charset=utf-8` |
| sitemap.xml | `application/xml; charset=utf-8` (or `text/xml`) |

Nginx: the default `mime.types` is pulled in by the stock `http` block —
verify it is included (`include mime.types;` or the distro default) and that
`default_type` is not masking anything. Current `mime.types` already maps
avif/webp; on older releases add the missing entries explicitly in the `http`
block:

```nginx
types {
  image/avif avif;
  image/webp webp;
}
```

Apache: `mod_mime` is required, and `.htaccess` `AddType` only takes effect
when the directory permits overrides (`AllowOverride` — see below). The main
`.htaccess` block above already carries the `AddType` fallbacks for hosts
whose map lacks avif/webp.

Verification — deployed `curl -I` for every generated resource class (HTML,
one `.css`, one `.js`, each image format actually used, `robots.txt`,
`sitemap.xml`); a missing or incorrect `Content-Type` fails deployment
verification.

## robots.txt & sitemap.xml caching

These two files are CRAWLER-FACING contracts: a stale copy means crawlers keep
following disallowed or removed URLs, or miss new pages. They must NEVER be
`immutable` and never get a long `max-age` — Google itself documents that
robots.txt responses are cached for up to 24 hours regardless of headers, so
any TTL you choose adds to that propagation delay.

Policy (already encoded in the Apache/Nginx blocks above):
- Exact-path rules only (`<Files "robots.txt">` / `location = /robots.txt`,
  same for `sitemap.xml`) — never an extension or prefix rule that could also
  catch other files, and never inside a rule that can mark them `immutable`.
- Default: `no-cache` (may be stored, must revalidate every reuse). If a CDN
  or host requires a positive TTL, use a short one (e.g. `max-age=3600`) and
  record it in `SERVER-SETUP.md` together with the resulting worst-case
  propagation delay (TTL + any CDN edge TTL + Google's own ~24h robots cache).
- Keep conditional-request support intact: ETag/Last-Modified must survive so
  unchanged files answer `304 Not Modified` — do not strip validators or
  disable them for these paths.

Verification (at the origin AND behind any CDN):
1. `curl -I https://site/robots.txt` and `.../sitemap.xml` show the expected
   `Cache-Control` and no `immutable`.
2. Unchanged file: a second request with `If-None-Match`/`If-Modified-Since`
   returns `304`.
3. Changed file: after redeploying a modified robots.txt/sitemap.xml, the next
   request returns `200` with the NEW bytes — at origin and at the CDN edge
   (purge if the CDN caches; record the purge step in `SERVER-SETUP.md`).

## Other servers — portability of these requirements

Apache (.htaccess) and Nginx cover most self-managed hosting, and LiteSpeed
Enterprise on shared hosting usually reads the same `.htaccess`. The
REQUIREMENTS themselves are server-agnostic — whatever serves the site, the
deployed result must satisfy the checklist below. On other stacks, translate
the same mechanisms:

- **Caddy**: `header` directives for the security headers, automatic HTTPS
  plus `redir` for the redirect, matchers for per-path Cache-Control.
- **IIS / Windows**: `web.config` — `<customHeaders>` under `<httpProtocol>`
  plus URL Rewrite rules for the redirect.
- **OpenLiteSpeed**: response-header and rewrite rules in the admin console —
  port the same directives (`.htaccess` support is partial).
- **Managed/static platforms** (Netlify, Vercel, Cloudflare Pages, GitHub
  Pages): there is no `.htaccess`/`nginx.conf` at all. Security headers and
  redirects go in platform config (`netlify.toml` or `_headers`/`_redirects`,
  `vercel.json` headers/rewrites, Cloudflare Pages `_headers`/`_redirects`);
  compression and MIME types are platform-managed. Run the same `curl -I`
  checklist against the deployed URLs instead.

Record the actual server software and version in `SERVER-SETUP.md`, and verify
behavior with the checklist — file presence or platform defaults are not proof
that any of this is active.

## Apache .htaccess activation — AllowOverride

Apache IGNORES `.htaccess` completely unless the containing directory permits
overrides (httpd howto/htaccess) — installing the file is not proof it is
active. Every directive class used by this skill's `.htaccess` needs the
`FileInfo` override class:

| Directive | Module | Override class |
|---|---|---|
| `AddOutputFilterByType` | mod_deflate / mod_brotli | FileInfo |
| `Header` (Cache-Control, Vary, security headers, CSP, HSTS) | mod_headers | FileInfo |
| `AddType`, `AddCharset` | mod_mime | FileInfo |
| `AddDefaultCharset` | core | FileInfo |

So the directory must allow at least:

```apache
# In the server/virtual-host config (NOT in .htaccess itself)
<Directory /var/www/site>
  AllowOverride FileInfo
</Directory>
# or simply: AllowOverride All
```

`AllowOverrideList` takes individual directive names, not override classes.
Do not substitute `AllowOverrideList FileInfo`. If the host requires a
fine-grained list, have its administrator enumerate and test every permitted
directive and container used by the complete file; use the working
`AllowOverride FileInfo` example above when that class is permitted.

If the host disables overrides entirely, move the same directives into the
virtual-host/`<Directory>` config instead — the behavioral requirements below
do not change.

Module inventory — record it in `SERVER-SETUP.md`:
- Required: `mod_headers`, `mod_mime`, `mod_deflate` (gzip).
- Optional: `mod_brotli` (needs Apache ≥ 2.4.26; its `<IfModule>` block is
  silently skipped when absent), `mod_rewrite` (only for the RewriteRule
  redirect variant).
- Every skipped `<IfModule>` block must be reflected as MISSING in the
  checklist — never checked off as if active.

Verification:
1. `apachectl configtest` passes.
2. Identify the effective `<Directory>` block (`apachectl -S` for vhosts, then
   inspect its `AllowOverride`/`AllowOverrideList`).
3. Behavioral proof only: deployed `curl -I` requests for the HTML page, a
   static asset, and a 404 must show the expected caching, compression, and
   security behavior. Missing behavior FAILS deployment verification — file
   presence never substitutes for it.

## Checklist
- [ ] Config syntax check passes BEFORE reload: `nginx -t` (Nginx) or `apachectl configtest` (Apache)
- [ ] Compression state recorded honestly: Brotli module installed and loaded (Nginx: package name / `load_module` lines documented; Apache: `mod_brotli` present). If not installed — the Brotli lines are removed and this is marked gzip-only, never silently skipped
- [ ] Brotli verified with `curl -I -H 'Accept-Encoding: br' <url>` → `Content-Encoding: br`; gzip fallback with `curl -I -H 'Accept-Encoding: gzip' <url>` → `Content-Encoding: gzip`. In gzip-only mode verify the gzip request only
- [ ] Compressed responses carry `Vary: Accept-Encoding`; identity, gzip and Brotli requests each get the right `Content-Encoding` (verify at origin and through any CDN)
- [ ] Only fingerprinted asset URLs (content-hash in the filename) carry `immutable` with max-age 1 year; stable URLs carry a revalidation policy
- [ ] Two-version deploy check: publish asset version A, deploy version B (new hash + updated HTML references), reload from a warm cache — version B loads immediately, no stale styles/scripts/images
- [ ] HTML revalidated on every request
- [ ] All four security headers present on every response class — verify with `curl -I` against `/`, a `.css` file, a `.js` file, and a nonexistent URL (404); each response carries exactly one copy of all four headers (no duplicates, none missing on error responses or Nginx asset locations)
- [ ] CSP generated for this page's exact feature set; deployed report-only first, browser-tested across every feature combination with zero unexpected violations, then enforced; no `unsafe-inline`/`unsafe-eval` in `script-src`; `youtube-nocookie.com` present in `frame-src` only when the video block exists
- [ ] HTTPS enforced: TLS certificate installed, HTTPS endpoint serves the site, and a port-80 vhost/server block issues exactly one 301/308 preserving host/path/query to the canonical host. Verify deployed: `curl -I 'http://<host>/path?q=1'` returns the single redirect to the expected HTTPS URL, and the HTTPS request succeeds
- [ ] HSTS deployed in stages: short `max-age` first, long lifetime only after clean rollout; header present exactly once on HTTPS responses and absent on the HTTP redirect (verify with `curl -I`); `includeSubDomains` only when every subdomain is HTTPS-capable; `preload` only with the user's explicit recorded consent. HSTS supplements, never replaces, the HTTP→HTTPS redirect
- [ ] HTML responses carry `Content-Type: text/html; charset=utf-8` (verify with `curl -I`); `<meta charset="utf-8">` present within the first 1024 bytes; representative non-ASCII text, metadata and JSON-LD render correctly
- [ ] MIME types verified with deployed `curl -I` for every generated resource class (CSS, JS, each image format used, robots.txt, sitemap.xml) against the expected-type table; Nginx `mime.types` included (avif/webp mapped) or Apache `AddType` fallbacks in place — an absent or wrong `Content-Type` fails verification
- [ ] Apache only: `.htaccess` activation verified — the effective `<Directory>` allows `AllowOverride FileInfo` (or `All`/`AllowOverrideList`), or the directives were moved into the vhost config; module inventory recorded (required: mod_headers, mod_mime, mod_deflate; optional: mod_brotli, mod_rewrite) and every skipped `<IfModule>` block marked missing, not checked off. `apachectl configtest` passes and deployed requests for HTML, an asset, and a 404 show the expected behavior — file presence is never treated as proof
- [ ] robots.txt & sitemap.xml: exact-path cache rules active (never `immutable`, default `no-cache` or a documented short TTL with its worst-case propagation delay recorded); ETag/Last-Modified preserved — unchanged file answers `304`, changed file answers `200` with new bytes, verified at origin AND behind the CDN (with purge step recorded if the CDN caches)
