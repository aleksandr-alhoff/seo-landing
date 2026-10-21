"""Portable regression checks: python -m unittest discover -s tests -v."""
import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class AssetValidationTests(unittest.TestCase):
    def check_assets(self, folder):
        return subprocess.run(
            [sys.executable, str(ROOT / 'scripts/validate_assets.py'),
             str(folder), '--page-url', 'https://example.com/'],
            capture_output=True, text=True, check=False,
        )

    def test_missing_same_origin_absolute_asset_fails(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'index.html').write_text(
                '<img src="https://example.com/images/missing.jpg">', encoding='utf-8')
            result = self.check_assets(root)
            self.assertEqual(result.returncode, 1, result.stderr)
            self.assertIn('missing.jpg', result.stdout)

    def test_css_assets_and_srcsets_are_checked_without_fetching_external_urls(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'index.html').write_text(
                '<link rel="stylesheet" href="/style.css">'
                '<picture><source srcset="https://example.com/a.avif 320w, b.avif 640w">'
                '<img src="https://cdn.example.org/not-local.jpg"></picture>', encoding='utf-8')
            (root / 'style.css').write_text('body{background:url("missing.png")}', encoding='utf-8')
            (root / 'a.avif').touch()
            result = self.check_assets(root)
            self.assertEqual(result.returncode, 1)
            self.assertIn('missing.png', result.stdout)
            self.assertIn('b.avif', result.stdout)
            self.assertNotIn('not-local.jpg', result.stdout)
            (root / 'missing.png').touch()
            (root / 'b.avif').touch()
            self.assertEqual(self.check_assets(root).returncode, 0)

    def test_parent_path_cannot_escape_project(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / 'site'
            root.mkdir()
            (root.parent / 'secret.png').touch()
            (root / 'index.html').write_text('<img src="../../secret.png">', encoding='utf-8')
            self.assertEqual(self.check_assets(root).returncode, 1)

    def test_quoted_css_filename_with_spaces_is_not_skipped(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'index.html').write_text('<style>body{background:url("my photo.png")}</style>', encoding='utf-8')
            result = self.check_assets(root)
            self.assertEqual(result.returncode, 1)
            self.assertIn('my photo.png', result.stdout)
            (root / 'my photo.png').touch()
            self.assertEqual(self.check_assets(root).returncode, 0)

    def test_embedded_documents_and_svg_resource_references_are_checked(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'index.html').write_text(
                '<iframe src="frame.html"></iframe><embed src="document.pdf">'
                '<object data="object.html"></object><svg><image href="image.png"/>'
                '<use href="sprite.svg#icon"/></svg>', encoding='utf-8')
            result = self.check_assets(root)
            self.assertEqual(result.returncode, 1)
            for name in ('frame.html', 'document.pdf', 'object.html', 'image.png', 'sprite.svg'):
                self.assertIn(name, result.stdout)

    def test_inline_css_import_with_comment_is_checked(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'index.html').write_text('<style>@import/*comment*/"missing.css";</style>', encoding='utf-8')
            result = self.check_assets(root)
            self.assertEqual(result.returncode, 1)
            self.assertIn('missing.css', result.stdout)


class ReferenceRegressionTests(unittest.TestCase):
    def test_benchmark_does_not_publish_ineligible_rating_or_breadcrumbs(self):
        html = (ROOT / 'benchmark/rebuilt/index.html').read_text(encoding='utf-8')
        for block in re.findall(r'<script type="application/ld\+json">(.*?)</script>', html, re.DOTALL):
            graph = json.loads(block)['@graph']
            self.assertFalse(any(x['@type'] in ('AggregateRating', 'BreadcrumbList') for x in graph))

    def test_benchmark_stylesheet_works_without_inline_event_handlers(self):
        html = (ROOT / 'benchmark/rebuilt/index.html').read_text(encoding='utf-8')
        self.assertFalse(re.search(r'\bonload=', html), 'inline event handler is forbidden')
        self.assertIn('<link rel="stylesheet" href="styles.css">', html)


if __name__ == '__main__':
    unittest.main()
