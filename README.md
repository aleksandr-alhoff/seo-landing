# SEO Landing

## Give your AI coding agent the capabilities of a senior Technical SEO engineer.

An agent skill for building high-performance, technically optimized SEO landing pages.
Turn an AI coding agent into a technical SEO specialist.

Build and improve landing pages with:

- 🚀 100/100 Google PageSpeed target
- ⚡ Core Web Vitals optimization
- 🔍 Technical SEO
- 🧩 Full Schema.org structured data
- 🖼️ AVIF image optimization
- 🎨 Critical CSS
- 🧹 Zero third-party requests on first load
- 📱 Mobile-first performance
- 🤖 Semantic HTML

🇷🇺 [Описание скила на русском языке](./README.ru.md)

## Works with AI coding agents

Designed for agentic coding workflows and compatible with Agent Skills–style environments.

## What it does?

The skill guides an AI coding agent through the complete landing-page workflow:

1. Analyze the existing page
2. Fix technical SEO issues
3. Optimize HTML structure
4. Improve Core Web Vitals
5. Optimize images and fonts
6. Add structured data
7. Remove unnecessary dependencies
8. Validate the final implementation

## Why?

AI can generate a beautiful landing page in seconds.
The problem is that generated pages often contain:

- unnecessary JavaScript
- oversized images
- poor semantic structure
- missing structured data
- weak metadata
- performance bottlenecks
- technical SEO mistakes

SEO Landing Skill gives the agent a repeatable technical SEO workflow instead of relying on generic prompting.

An agent skill that builds and updates landing pages toward **100/100 lab PageSpeed** and Core Web Vitals-friendly performance, and gets the technical SEO right. Static HTML, critical CSS, AVIF images, full schema.org markup, zero third-party requests on first load (deferred widgets, when used, are consent-gated and documented in the dependency manifest). These are optimization targets, not guaranteed outcomes — results depend on content, hosting, devices, and real traffic; Core Web Vitals status itself is determined by Google from field (RUM) data, not by lab tools.

```text
BEFORE
Landing page
↓
LCP: 4.2s
Performance: 61
Missing schema
Large PNG
Render-blocking CSS

        ↓ SEO LANDING SKILL ↓

AFTER
Landing page
↓
LCP: 1.1s
Performance: 100
Schema.org ✓
AVIF ✓
Critical CSS ✓
Semantic HTML ✓
```

Format — [Agent Skills](https://agentskills.io) (open standard originally developed by Anthropic): works in VS Code Copilot, Claude Code, OpenAI Codex, Google Antigravity, Cursor, Gemini CLI, OpenClaw, Hermes, and other compatible agents.

## What's inside

```
seo-landing/
├── SKILL.md              # Main workflow: mode routing → brief → generation → stop point → validation → report
├── scripts/validate_assets.py # Offline same-origin HTML/CSS resource check (Python ≥3.10)
├── references/
│   ├── tech-spec.md      # Technical spec (13 requirement sections + executable validation contract)
│   ├── server-config.md  # Server config: caching, Brotli/gzip, security headers (Nginx/Apache)
│   ├── video-facade.md   # Reference implementation of the "facade" pattern for YouTube
│   └── map-facade.md     # Reference implementation of the "facade" pattern for map embeds
├── benchmark/            # Lab benchmark disclosure: fixture, raw Lighthouse reports, methodology
└── tests/
    └── fixtures/broken-landing/  # Negative fixture: every validator gate must fail on it
```

## Key requirements enforced by the skill

- **Performance**: LCP < 2.5s, INP < 100ms, CLS < 0.1; critical CSS inlined, the rest loaded async; the LCP image loads eagerly with `fetchpriority="high"` (a responsive `imagesrcset`/`imagesizes` preload only when measurement shows a benefit)
- **Images**: AVIF → WebP → JPEG via `<picture>`, `srcset`/`sizes`, `width`/`height`, `loading="lazy"` for below-the-fold images only (never on the LCP image), breakpoints 320–1920
- **SEO**: title/description/canonical/robots, Open Graph, Twitter Card, JSON-LD (`WebSite`, `Organization`, `BreadcrumbList`, `FAQPage`, `VideoObject` — emitted only when fact-backed and reported per the chosen video mode, never as a guaranteed search feature)
- **Accessibility**: WCAG 2.1 AA, contrast ≥ 4.5:1, keyboard navigation, `prefers-reduced-motion`
- **Security**: `X-Content-Type-Options`, `X-Frame-Options`, `Permissions-Policy`, `Referrer-Policy`, per-page CSP, staged HSTS, HTTPS enforcement, `rel="noopener noreferrer"`
- **Fonts**: system fonts only — no external fonts, no Google Fonts
- **JS budget ≤ 15 KB** for the first load, one file with `defer`; deferred third-party widgets (when used) are consent-gated, excluded from the budget, and disclosed in the dependency manifest
- **Forbidden**: external JS/CSS libraries, SVG images, synchronous scripts, iframes on first load
- **Video & maps**: "facade" pattern by default — the cover is a local responsive image (eager when it is the LCP/above the fold, lazy below the fold), the iframe loads only on click. Click-only video trades Google video discovery for pre-activation privacy/performance; an opt-in SEO-discoverable mode (self-hosted `<video>` or a documented direct embed) exists when video search matters (tech-spec §9). Maps remain facade-only.
- **Common blocks without JS**: FAQ via `<details>`, slider via `scroll-snap`, modal via `<dialog>`
- **Stop point**: before validation and the final report, the skill always asks the user to confirm the HTML version

## Real-world result (lab measurements — not field Core Web Vitals)

One reproducible lab benchmark: Lighthouse CLI 13.4.1, mobile emulation, simulated throttling. Original — an Angular SPA (102 requests, 1 run); the same page rebuilt as static HTML with this skill (17–18 requests, median of 5 runs). Full disclosure — fixture, exact flags, raw JSON reports, timestamps, and aggregation method — is in [benchmark/README.md](./benchmark/README.md).

| Metric | Original | Rebuilt | Gain |
|---|---:|---:|---:|
| Performance | 75 | **100** | +25 |
| Accessibility | 75 | **100** | +25 |
| Best Practices | 73 | **100** | +27 |
| LCP | 3.3 s | 1.6 s | −52% |
| Total Blocking Time | 490 ms | 13 ms | −97% |
| TTI | 9.4 s | 1.6 s | −83% |
| Data transferred | 769 KiB | 110 KiB | −86% |
| Requests | 102 | 17 | −83% |

These are **lab** numbers for one before/after pair. They are not field Core Web Vitals (Google determines CWV status from CrUX/RUM field data at the 75th percentile, and Lighthouse cannot measure INP without real interaction), and they are not a guarantee that another page, host, device, or audience will reach the same results — the skill's targets are optimization goals, not promised outcomes.

## Installation

Repository regression checks: `python3 -m unittest discover -s tests -v`.
The asset checker needs Python ≥3.10. Lighthouse 13.4.1 needs Node ≥22.19,
`npx`, and Chrome/Chromium. Missing tools are blockers, never passing checks.

The skill is hosted at [github.com/aleksandr-alhoff/seo-landing](https://github.com/aleksandr-alhoff/seo-landing). Clone the repository — the repo root is the skill folder itself — then run the commands below from the directory that contains `seo-landing/`:

```bash
git clone https://github.com/aleksandr-alhoff/seo-landing.git
```

### Global (available in all projects)

Every recipe below is self-contained: it creates its destination directory first, then copies the skill into it. Each one must exit with status `0` and leave the layout `<skills-dir>/seo-landing/SKILL.md` in place.

Manual installation needs `rsync`. The recipes exclude the clone's `.git`: copying it into another repository creates an embedded Git repository, so a parent commit may record a gitlink instead of the skill files. Only the source clone should retain its `.git`.

```bash
# VS Code Copilot
mkdir -p ~/.copilot/skills
rsync -a --exclude=.git seo-landing/ ~/.copilot/skills/seo-landing/

# Claude Code
mkdir -p ~/.claude/skills
rsync -a --exclude=.git seo-landing/ ~/.claude/skills/seo-landing/

# OpenAI Codex CLI / ChatGPT desktop
mkdir -p ~/.agents/skills
rsync -a --exclude=.git seo-landing/ ~/.agents/skills/seo-landing/

# Cursor
mkdir -p ~/.cursor/skills
rsync -a --exclude=.git seo-landing/ ~/.cursor/skills/seo-landing/

# Gemini CLI
mkdir -p ~/.gemini/skills
rsync -a --exclude=.git seo-landing/ ~/.gemini/skills/seo-landing/

# Google Antigravity
mkdir -p ~/.gemini/config/skills
rsync -a --exclude=.git seo-landing/ ~/.gemini/config/skills/seo-landing/

# OpenCode
mkdir -p ~/.config/opencode/skills
rsync -a --exclude=.git seo-landing/ ~/.config/opencode/skills/seo-landing/

# OpenClaw (via CLI — installs into the shared ~/.openclaw/skills)
openclaw skills install git:aleksandr-alhoff/seo-landing --global
# or from a local clone: openclaw skills install ./seo-landing --global
# or manually:
mkdir -p ~/.openclaw/skills
rsync -a --exclude=.git seo-landing/ ~/.openclaw/skills/seo-landing/

# Hermes
mkdir -p ~/.hermes/skills
rsync -a --exclude=.git seo-landing/ ~/.hermes/skills/seo-landing/
```

OpenClaw also picks up skills from `~/.agents/skills` (the Codex path above), and Hermes can scan it too if you add `~/.agents/skills` to `skills.external_dirs` in `~/.hermes/config.yaml`.

Gemini CLI can also install straight from a Git repository:

```bash
gemini skills install https://github.com/aleksandr-alhoff/seo-landing.git
```

### Per project (workspace only)

```bash
# Shared .agents/skills — picked up by VS Code Copilot, Codex, Cursor, Antigravity, Gemini CLI, OpenCode, OpenClaw, Hermes
mkdir -p .agents/skills
rsync -a --exclude=.git seo-landing/ .agents/skills/seo-landing/

# Claude Code
mkdir -p .claude/skills
rsync -a --exclude=.git seo-landing/ .claude/skills/seo-landing/

# VS Code Copilot (GitHub-style location)
mkdir -p .github/skills
rsync -a --exclude=.git seo-landing/ .github/skills/seo-landing/

# OpenClaw (workspace skills — highest precedence)
# via CLI: openclaw skills install ./seo-landing
mkdir -p skills
rsync -a --exclude=.git seo-landing/ skills/seo-landing/

# Hermes (project-local; then trust the repo once: hermes skills trust)
mkdir -p .hermes/skills
rsync -a --exclude=.git seo-landing/ .hermes/skills/seo-landing/
```

## Updating, verifying, and uninstalling installed copies

Two facts drive everything below:

1. **`git pull` changes only the clone.** An installed copy made with `cp -R` is independent — pulling the source clone does NOT update any installation.
2. **`cp -R` copies, it does not synchronize.** GNU `cp` has no destination-sync/removal behavior: a file deleted upstream stays in the installed copy forever, producing a mixed release of old and new instructions.

So an update is an explicit, bounded, idempotent sync into the resolved skill destination — never a blind re-copy.

### Destinations (one per client and scope)

| Client / scope | Installed skill destination (`$DEST`) |
|---|---|
| VS Code Copilot — global | `~/.copilot/skills/seo-landing` |
| Claude Code — global | `~/.claude/skills/seo-landing` |
| OpenAI Codex CLI / ChatGPT desktop — global | `~/.agents/skills/seo-landing` |
| Cursor — global | `~/.cursor/skills/seo-landing` |
| Gemini CLI — global | `~/.gemini/skills/seo-landing` |
| Google Antigravity — global | `~/.gemini/config/skills/seo-landing` |
| OpenCode — global | `~/.config/opencode/skills/seo-landing` |
| OpenClaw — global | `~/.openclaw/skills/seo-landing` |
| Hermes — global | `~/.hermes/skills/seo-landing` |
| Shared per-project (Copilot, Codex, Cursor, Antigravity, Gemini CLI, OpenCode, OpenClaw, Hermes) | `.agents/skills/seo-landing` |
| Claude Code — per project | `.claude/skills/seo-landing` |
| VS Code Copilot — per project (GitHub-style) | `.github/skills/seo-landing` |
| OpenClaw — workspace (highest precedence) | `skills/seo-landing` |
| Hermes — per project | `.hermes/skills/seo-landing` |

### Update (idempotent sync, removes upstream-deleted files)

Run from the directory that contains the updated `seo-landing/` clone, with `$DEST` set to the destination from the table above:

```bash
DEST=~/.copilot/skills/seo-landing   # ← substitute the right destination

# 1. Recovery first: back up the current installation (the sync is destructive).
# Copied installations only: never migrate the source clone or a worktree.
SOURCE_PATH=$(cd seo-landing && pwd -P) || exit 1
DEST_PATH=$(cd "$DEST" && pwd -P) || exit 1
[ "$SOURCE_PATH" != "$DEST_PATH" ] || exit 1
if [ -L "$DEST/.git" ] || [ -f "$DEST/.git" ]; then
  printf '%s\n' 'Stop: symlink/worktree Git metadata needs manual migration.' >&2
  exit 1
fi
BACKUP_ROOT="${XDG_STATE_HOME:-$HOME/.local/state}/seo-landing/backups"
mkdir -p "$BACKUP_ROOT" || exit 1
# Keep backups outside versioned projects, including per-project skill folders.
if git -C "$BACKUP_ROOT" rev-parse --show-toplevel >/dev/null 2>&1; then exit 1; fi
BACKUP=$(mktemp -d "$BACKUP_ROOT/backup-XXXXXXXX") || exit 1
mkdir "$BACKUP/skill" && rsync -a --exclude=.git "$DEST/" "$BACKUP/skill/" || exit 1
# Preserve legacy clone metadata separately; never put it back into the skill.
if [ -d "$DEST/.git" ]; then mv "$DEST/.git" "$BACKUP/git-metadata" || exit 1; fi
printf 'Backup: %s\n' "$BACKUP"

# 2. Bounded idempotent sync: copy new/changed files AND delete files inside
#    $DEST that no longer exist upstream. --delete only ever touches $DEST.
rsync -a --delete --exclude=.git seo-landing/ "$DEST/"

# 3. Verify: zero differences (exit status 0) and the installed SKILL.md
#    matches the source revision byte-for-byte.
test ! -e "$DEST/.git" && test ! -L "$DEST/.git" && diff -qr -x .git seo-landing "$DEST" && cmp "$DEST/SKILL.md" seo-landing/SKILL.md
```

Notes:
- `rsync -a --delete` is available out of the box on macOS (openrsync) and on typical Linux systems; `--exclude=.git` keeps the clone's history out of the installation.
- The backup in step 1 is the recovery path: if the new version misbehaves, restore the exact printed backup with `rsync -a --delete --exclude=.git "$BACKUP/skill/" "$DEST/"` after checking both paths. Each run creates a distinct backup, even on the same day; keep `$BACKUP` or its printed path for rollback. Legacy Git metadata is preserved separately in `$BACKUP/git-metadata`, outside the project, and must not be restored into the installed skill.
- The sync is safe to re-run at any time — running it twice in a row changes nothing the second time.
- Tested upgrade path: an installation containing a file that the new revision removed loses that file after the sync, and the installed `SKILL.md` becomes byte-identical to the source revision.

### Verify an existing installation at any time

```bash
diff -qr -x .git seo-landing "$DEST"
```

Exit status `0` (no output) means the installation matches the clone exactly. Any printed difference is a stale, modified, or extra file — re-run the update sync to resolve it. To check which specification version is installed, read the `Version` line at the top of `$DEST/references/tech-spec.md` (the single source of truth for versions).

### Reload / restart after an update

Agents read skills when a session starts. After updating, **start a new chat session** (or restart the agent CLI) before relying on the new version. Clients that gate skills behind trust/approval (e.g. Hermes: `hermes skills trust`) may require re-trusting the updated copy.

### Uninstall

```bash
rm -rf "$DEST"   # the destination from the table above
```

If the copy was installed through a client CLI (`openclaw skills install`, `gemini skills install`), prefer that client's own uninstall command when it provides one; otherwise removing the destination directory is sufficient. Also remove any printed backup directories you no longer need.

### Symlinked installations — optional/experimental

Symlinking the clone into a skills directory (so `git pull` updates it in place) is possible in principle, but official symlink support, trust handling, and reload behavior differ per client and are NOT verified here — treat this as experimental. The rsync sync above is the supported, client-independent update path.

Once installed, the skill is picked up automatically by its description — just ask your agent to "build a landing page from a brief with focus on SEO and PageSpeed".

## Usage

1. Give the agent a brief: domain, language (BCP-47 tag, base direction for RTL languages, and Open Graph locale — three separate inputs), topic and keywords, business type, CTA and contacts.
2. The skill creates a separate project folder (`<workspace>/<project-slug>/`) with `index.html` and every local asset it references (all image variants, favicon), plus — conditionally — `styles.css` (deferred CSS only), `script.js` (when JS is used), `robots.txt`, `sitemap.xml`, `ASSETS.md`, and `SERVER-SETUP.md`. Missing source images are requested from the user, never invented.
3. At the stop point, confirm the HTML version — the skill then runs validation (local asset/link existence, W3C, JSON-LD, Lighthouse as automated evidence, plus required manual accessibility checks) and produces a report: LCP, PageSpeed scores, and the schema.org types used.

## About the author

**Aleksandr Alhov** — 14+ years of experience in SEO, content marketing, and GEO/AEO. Runs an SEO boutique for product teams working across EN, LATAM, MENA, and CIS markets: building in-house SEO departments turnkey, launching profitable corporate media, discovering growth hypotheses in the SEO channel, and providing hands-on SEO consulting.

Co-founder of:

- [Total Site Control](https://totalsitecontrol.com/)
- [Udalenka.work](https://udalenka.work)
- [QR Barcode Hub](https://qrbarcodehub.com)
- [DealRocket](https://dealrocket.ru/)

Made for the [t.me/sdelay_tam](https://t.me/sdelay_tam) channel — a cozy SEO channel for product teams. SEO questions: [t.me/alhov](https://t.me/alhov).

## License
[MIT](./LICENSE) — free to use, modify, and distribute, including commercially. Just keep the copyright notice.
Specification: see [references/tech-spec.md](./references/tech-spec.md) — the current version and change record are declared there.
