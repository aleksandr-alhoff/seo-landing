# Benchmark disclosure — lab measurements, not field Core Web Vitals

Everything in this folder is a **lab benchmark**: reproducible Lighthouse CLI
measurements of one concrete before/after comparison. It is NOT field data,
NOT a Core Web Vitals assessment, and NOT a guarantee of what any other page,
host, device, or audience will achieve.

## Measurement identity and current fixture

The reports below describe the fixture at commit
`1aa908f96a09e2e93fd1839ac51b02d362e7a8ef`, not every later revision.
The current `rebuilt/` example has since been hardened: ordinary stylesheet
loading compatible with strict CSP, truthful structured data, safe-area
spacing, and a corrected menu label. Historical reports remain unchanged;
their scores must not be attributed to the updated fixture without new runs.
To reproduce the measured bytes, use a separate checkout of that exact commit.

This is a local performance example, not a publish-ready site template.
It has no cleared asset-rights manifest, brand-approved favicon or production
hosting/crawler configuration. Do not publish the fixture or its third-party
assets without obtaining permissions and completing the current skill's
ASSETS.md, favicon, robots.txt, sitemap.xml and SERVER-SETUP.md contracts.
No rights clearance or production readiness is implied by committing a fixture.

## What was compared (the two revisions)

| Side | What it is | Where it lives |
|---|---|---|
| **Original** | The production Angular SPA at `https://udalenka.work/` (102 requests, ~769 KiB) as measured on 2026-08-27. A static HTML snapshot of the page as served is archived at [`original/original-snapshot.html`](./original/original-snapshot.html). | Live URL at measurement time |
| **Rebuilt** | The same page rebuilt as static HTML with this skill (17–18 requests, ~110 KiB). The complete served fixture — `index.html`, `styles.css`, `script.js`, and every referenced image variant — is committed at [`rebuilt/`](./rebuilt/) so the benchmark can be reproduced offline. | [`rebuilt/`](./rebuilt/) in this folder |

## Exact tool, version, and profile

- **Tool**: Lighthouse CLI via `npx -y lighthouse@13.4.1` (pinned version; `channel: cli`).
- **Browser**: HeadlessChrome/151 on the measurement host (macOS), no custom `--chrome-flags`.
- **Form factor**: mobile emulation — Moto G Power (2022) profile, 412×823 viewport, device pixel ratio 1.75.
- **Throttling**: simulated (`simulate`) — 150 ms RTT, 1638.4 Kbps throughput, 562.5 ms request latency, 4× CPU slowdown (Lighthouse mobile defaults).
- **Command shape** (one run):

```bash
npx -y lighthouse@13.4.1 <url> --output=json --output=html --output-path=<artifact>
```

All categories were measured (no `--only-categories` filter in these runs).

## Runs, timestamps, and raw reports

Every raw report is committed under [`reports/`](./reports/) as full Lighthouse
JSON (the complete audit data; `fetchTime` inside each file is the exact run
timestamp).

| Report file | fetchTime (UTC) | Measured URL |
|---|---|---|
| `reports/original-2026-08-27.report.json` | 2026-08-27T09:45:22Z | `https://udalenka.work/` |
| `reports/rebuilt-run1-2026-08-27.report.json` | 2026-08-27T12:08:39Z | `http://localhost:8000/index.html` |
| `reports/rebuilt-run2-2026-08-27.report.json` | 2026-08-27T12:11:27Z | `http://localhost:8000/index.html` |
| `reports/rebuilt-run3-2026-08-30.report.json` | 2026-08-30T03:53:34Z | `http://localhost:8123/index.html` |
| `reports/rebuilt-run4-2026-08-30.report.json` | 2026-08-30T03:53:48Z | `http://localhost:8123/index.html` |
| `reports/rebuilt-run5-2026-08-30.report.json` | 2026-08-30T03:54:02Z | `http://localhost:8123/index.html` |

Run counts: **original — 1 run** (a live third-party site measured once as the
baseline; repeated runs against someone else's production site were deliberately
not made), **rebuilt — 5 runs** served from the committed fixture via
`python3 -m http.server` (port 8000 on 27.08, port 8123 on 30.08).

**Aggregation**: median per category/metric across the 5 rebuilt runs.

## Results (median of 5 rebuilt runs vs the single original run)

| Metric | Original (1 run) | Rebuilt (median of 5) |
|---|---:|---:|
| Performance | 75 | **100** |
| Accessibility | 75 | **100** |
| Best Practices | 73 | **100** |
| SEO | 100 | **100** |
| LCP | 3.3 s | 1.6 s (median 1601 ms; range 1585–1613 ms) |
| Total Blocking Time | 490 ms | 13 ms (range 6–50 ms) |
| TTI | 9.4 s | 1.6 s |
| CLS | 0 | 0.007 |
| Total byte weight | 769 KiB | 110 KiB (median 112 496 B) |
| Requests | 102 | 17 (range 17–18) |

Per-run values are in the raw JSON files — verify any number above against them.

## Reproduce it

```bash
cd benchmark/rebuilt
python3 -m http.server 8000
# then, from anywhere:
npx -y lighthouse@13.4.1 http://localhost:8000/index.html \
  --output=json --output=html --output-path=run-N
```

## What these numbers are — and are not

- **Lab, not field.** Lighthouse measures a simulated single visit on throttled
  emulated hardware. Google determines Core Web Vitals threshold status from
  **field/RUM data** (CrUX, 75th percentile over 28 days), and INP cannot be
  measured by Lighthouse at all without real interaction
  (https://web.dev/articles/vitals-measurement-getting-started). Nothing in this
  folder is or implies a Core Web Vitals pass.
- **No CWV claim.** We do not claim this page "passes Core Web Vitals": that
  requires the applicable field dataset and the 75th-percentile methodology,
  which this repository does not have for the measured period.
- **Targets are goals, not guarantees.** The skill's targets (100/100 lab
  PageSpeed, LCP < 2.5 s, INP < 100 ms, CLS < 0.1) are optimization goals.
  Actual results depend on content, images, hosting, CDN, devices, and real
  traffic; a different page or host will produce different numbers.
- **One comparison, honestly scoped.** This is one before/after pair (the same
  page, same content, rebuilt with the skill), measured by one operator on one
  machine. It demonstrates what the workflow did once — not a universal outcome.
