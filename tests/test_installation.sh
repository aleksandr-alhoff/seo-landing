#!/bin/sh
# Run from the repository root: sh tests/test_installation.sh
set -eu
scratch=$(mktemp -d "${TMPDIR:-/tmp}/seo-install-test-XXXXXXXX")
cd "$scratch"
mkdir -p seo-landing/.git project/.agents/skills
printf 'v1\n' > seo-landing/SKILL.md
printf 'obsolete\n' > seo-landing/removed.md
DEST="$scratch/project/.agents/skills/seo-landing"
rsync -a --exclude=.git seo-landing/ "$DEST/"
test ! -e "$DEST/.git"

# Exercise the documented backup command twice, in the same invocation/day.
BACKUP=$(mktemp -d "${DEST}.backup-XXXXXXXX") && cp -R "$DEST/." "$BACKUP/" || exit 1
first_backup=$BACKUP
printf 'v2\n' > seo-landing/SKILL.md
mv seo-landing/removed.md seo-landing/renamed.md
rsync -a --delete --exclude=.git seo-landing/ "$DEST/"
test ! -e "$DEST/removed.md"
BACKUP=$(mktemp -d "${DEST}.backup-XXXXXXXX") && cp -R "$DEST/." "$BACKUP/" || exit 1
test "$first_backup" != "$BACKUP"
test "$(cat "$first_backup/SKILL.md")" = v1
test "$(cat "$BACKUP/SKILL.md")" = v2
printf 'v3\n' > seo-landing/SKILL.md
rsync -a --delete --exclude=.git seo-landing/ "$DEST/"
rsync -a --delete --exclude=.git "$BACKUP/" "$DEST/"
test "$(cat "$DEST/SKILL.md")" = v2
test ! -e "$DEST/.git"

cd project
git init -q
git add .agents/skills/seo-landing
test "$(git ls-files --stage | cut -d ' ' -f 1 | sort -u)" = 100644
printf 'PASS: unique backups, exact rollback, removed-file sync and ordinary Git files. Scratch: %s\n' "$scratch"
