# Regression checks

From the repository root:

```sh
python3 -m unittest discover -s tests -v
python3 scripts/validate_assets.py benchmark/rebuilt --page-url https://udalenka.work/
sh tests/test_installation.sh
npm ci --prefix tests
npx --prefix tests playwright install chromium
npm test --prefix tests
```

Python requires ≥3.10. Node ≥22.19 matches the documented Lighthouse runtime.
Shell checks require Git, rsync and POSIX utilities. They keep a small isolated
scratch folder and print its path. Browser checks use pinned Playwright;
`CHROME_PATH` can select an existing Chrome/Chromium instead of downloading one.
`PLAYWRIGHT_MODULE` can point at a preinstalled Playwright package.

Real Nginx tests run when `NGINX_EXE` and `OPENSSL_EXE` name installed binaries.
They extract the actual documented configuration, use gzip-only without Brotli,
create a one-day self-signed test certificate, bind loopback HTTP/HTTPS ports,
and stop their own process after checking syntax, headers and asset caching.
Without those variables the test reports SKIP, not a tested server result.
The HTTPS client accepts that test certificate only for its loopback connection.

Browser tests check four widths, strict CSP/no-JS CSS, menu Escape, map geometry
for pointer/keyboard activation, no pre-activation provider request and
origin-only Referer. External requests are stubbed; actual provider playback,
production headers and search eligibility still require deployed checks.
Historical Lighthouse reports remain historical; these tests do not claim
new Lighthouse scores, field Core Web Vitals or WCAG conformance.
