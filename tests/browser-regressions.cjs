/* npm install --prefix tests; npx --prefix tests playwright install chromium;
 * npm test --prefix tests. CHROME_PATH may select an existing browser. */
const { chromium } = require(process.env.PLAYWRIGHT_MODULE || 'playwright');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const http = require('node:http');
const crypto = require('node:crypto');
const root = path.resolve(__dirname, '..');
const fixture = path.join(root, 'benchmark/rebuilt');
const read = file => fs.readFileSync(path.join(root, file), 'utf8');
const block = (doc, language) => doc.match(new RegExp('```' + language + '\\r?\\n([\\s\\S]*?)```'))[1];
const map = read('references/map-facade.md');
const mapPage = '<!doctype html><style>' + block(map, 'css') + '</style>' +
  block(map, 'html').replace(/https:\/\/site.com\/images\/[^" ]+/g, '/map.svg') +
  '<script>' + block(map, 'javascript') + '</script>';
const html = read('benchmark/rebuilt/index.html');
const hashes = [...html.matchAll(/<style[^>]*>([\s\S]*?)<\/style>/g)].map(m =>
  "'sha256-" + crypto.createHash('sha256').update(m[1].replace(/\r\n/g, '\n')).digest('base64') + "'").join(' ');
const csp = `default-src 'self'; script-src 'self'; style-src 'self' ${hashes}; img-src 'self' data:; object-src 'none'`;
const server = http.createServer((req, res) => {
  if (req.url.startsWith('/map?')) { res.setHeader('Content-Type', 'text/html'); return res.end(mapPage); }
  if (req.url === '/map.svg') { res.setHeader('Content-Type', 'image/svg+xml'); return res.end('<svg xmlns="http://www.w3.org/2000/svg" width="1280" height="480"></svg>'); }
  const u = new URL(req.url, 'http://localhost');
  const file = path.resolve(fixture, u.pathname === '/' ? 'index.html' : u.pathname.slice(1));
  if (!file.startsWith(fixture + path.sep) || !fs.existsSync(file) || !fs.statSync(file).isFile()) { res.statusCode = 404; return res.end(); }
  if (u.searchParams.has('csp')) res.setHeader('Content-Security-Policy', csp);
  const ext = path.extname(file);
  res.setHeader('Content-Type', ({ '.html': 'text/html; charset=utf-8', '.css': 'text/css', '.js': 'text/javascript', '.avif': 'image/avif', '.jpg': 'image/jpeg', '.webp': 'image/webp' })[ext] || 'application/octet-stream');
  res.end(fs.readFileSync(file));
});
(async () => {
  let browser;
  try {
    await new Promise(r => server.listen(0, '127.0.0.1', r));
    const origin = `http://127.0.0.1:${server.address().port}`;
    browser = await chromium.launch({ headless: true, ...(process.env.CHROME_PATH ? { executablePath: process.env.CHROME_PATH } : {}) });
    const page = await browser.newPage();
    let providerRequests = 0;
    let referrer;
    await page.route('**/*', async route => {
      if (!route.request().url().startsWith(origin)) {
        providerRequests++;
        referrer = route.request().headers().referer;
        return route.fulfill({ status: 200, contentType: 'text/html', body: '<title>Local provider stub</title>' });
      }
      return route.continue();
    });
    for (const width of [320, 768, 1280, 1920]) {
      await page.setViewportSize({ width, height: 900 });
      await page.goto(origin + '/?csp=1');
      assert.equal(await page.evaluate(() => document.documentElement.scrollWidth), width, 'horizontal overflow');
      assert.equal(await page.locator('.cities').evaluate(e => getComputedStyle(e).display), 'grid', 'stylesheet blocked by CSP');
    }
    await page.setViewportSize({ width: 320, height: 900 });
    await page.locator('.burger').click();
    await page.keyboard.press('Escape');
    assert.equal(await page.locator('.burger').getAttribute('aria-expanded'), 'false');
    assert.equal(await page.locator('.burger').getAttribute('aria-label'), 'Открыть меню');
    for (const keyboard of [false, true]) {
      const beforeRequests = providerRequests;
      await page.goto(origin + '/map?private=synthetic-value');
      assert.equal(providerRequests, beforeRequests, 'provider contacted before activation');
      const before = await page.locator('.map-facade').evaluate(e => e.getBoundingClientRect().height);
      if (keyboard) { await page.locator('.map-open').focus(); await page.keyboard.press('Enter'); }
      else await page.locator('.map-open').click();
      await page.locator('.map-facade iframe').waitFor();
      await page.waitForFunction(() => !!document.querySelector('iframe').contentWindow);
      const after = await page.locator('.map-facade iframe').evaluate(e => e.getBoundingClientRect().height);
      assert(before > 0 && after > 0 && Math.abs(before - after) < 1, 'map collapsed/shifted');
      await page.waitForLoadState('networkidle');
      assert.equal(referrer, origin + '/', 'map disclosed path/query');
    }
    const noScript = await browser.newContext({ javaScriptEnabled: false });
    const noScriptPage = await noScript.newPage();
    await noScriptPage.goto(origin + '/?csp=1');
    assert.equal(await noScriptPage.locator('.cities').evaluate(e => getComputedStyle(e).display), 'grid');
    await noScript.close();
    console.log('PASS: 4 viewports + strict CSP, no-JS CSS, menu Escape, pointer/keyboard map geometry and origin-only Referer.');
    console.log('External providers were stubbed; playback/real map functionality is not certified.');
  } finally { if (browser) await browser.close(); server.close(); }
})().catch(error => { console.error(error); process.exitCode = 1; });
