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

# Migrate a destination installed with the old cp -R recipe, preserving metadata.
mkdir "$DEST/.git"
printf 'legacy-history\n' > "$DEST/.git/history"
BACKUP_ROOT="$scratch/backups"
mkdir -p "$BACKUP_ROOT"
BACKUP=$(mktemp -d "$BACKUP_ROOT/backup-XXXXXXXX") || exit 1
mkdir "$BACKUP/skill" && rsync -a --exclude=.git "$DEST/" "$BACKUP/skill/" || exit 1
if [ -d "$DEST/.git" ]; then mv "$DEST/.git" "$BACKUP/git-metadata" || exit 1; fi
first_backup=$BACKUP
test ! -e "$DEST/.git"
test "$(cat "$BACKUP/git-metadata/history")" = legacy-history
printf 'v2\n' > seo-landing/SKILL.md
mv seo-landing/removed.md seo-landing/renamed.md
rsync -a --delete --exclude=.git seo-landing/ "$DEST/"
test ! -e "$DEST/removed.md"
BACKUP=$(mktemp -d "$BACKUP_ROOT/backup-XXXXXXXX") || exit 1
mkdir "$BACKUP/skill" && rsync -a --exclude=.git "$DEST/" "$BACKUP/skill/" || exit 1
test "$first_backup" != "$BACKUP"
test "$(cat "$first_backup/skill/SKILL.md")" = v1
test "$(cat "$BACKUP/skill/SKILL.md")" = v2
printf 'v3\n' > seo-landing/SKILL.md
rsync -a --delete --exclude=.git seo-landing/ "$DEST/"
rsync -a --delete --exclude=.git "$BACKUP/skill/" "$DEST/"
test "$(cat "$DEST/SKILL.md")" = v2
test ! -e "$DEST/.git"

cd project
git init -q
git add .agents/skills/seo-landing
test "$(git ls-files --stage | cut -d ' ' -f 1 | sort -u)" = 100644
printf 'PASS: unique backups, exact rollback, removed-file sync and ordinary Git files. Scratch: %s\n' "$scratch"
