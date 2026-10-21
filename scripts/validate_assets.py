"""Check local HTML/CSS resources without making network requests.

The root is the deployed site's document root. --page-url supplies the real
origin and URL path for resolving relative and same-origin absolute references.
Navigation links and remote resources require separate deployed-link checks.
"""
import argparse
import json
import re
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urljoin, urlsplit

CSS_URL = re.compile(r'''url\(\s*(?:"([^"]*)"|'([^']*)'|([^\s)]+))\s*\)''', re.IGNORECASE)
CSS_IMPORT = re.compile(r'@import\s*[\'"]([^\'"]+)[\'"]', re.IGNORECASE)


def css_urls(css):
    return [next(value for value in match if value) for match in CSS_URL.findall(css) if any(match)]


class Resources(HTMLParser):
    def __init__(self):
        super().__init__()
        self.urls = []
        self.in_style = False

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'base':
            raise ValueError('<base> is unsupported; resolve/remove it before validation')
        if tag in ('img', 'source', 'script', 'video', 'audio', 'track', 'input', 'iframe', 'embed'):
            self.urls.extend(attrs[k] for k in ('src', 'poster') if attrs.get(k))
        if tag == 'object' and attrs.get('data'):
            self.urls.append(attrs['data'])
        if tag in ('image', 'use'):
            self.urls.extend(attrs[k] for k in ('href', 'xlink:href') if attrs.get(k))
        if (tag == 'link' and attrs.get('href') and set(attrs.get('rel', '').lower().split()) & {
                'stylesheet', 'preload', 'icon', 'apple-touch-icon', 'modulepreload'}):
            self.urls.append(attrs['href'])
        if (tag == 'meta' and attrs.get('content') and (attrs.get('property') or attrs.get('name')) in {
                'og:image', 'og:image:url', 'og:image:secure_url', 'twitter:image'}):
            self.urls.append(attrs['content'])
        for name in ('srcset', 'imagesrcset'):
            # Data candidates are self-contained, not local files. Do not split
            # their payload commas into fictitious paths.
            value = attrs.get(name, '')
            value = re.sub(r'data:[^\s]+(?:\s+\d+(?:\.\d+)?[wx])?', '', value)
            self.urls.extend(x.strip().split()[0] for x in value.split(',') if x.strip())
        self.urls.extend(css_urls(attrs.get('style', '')))
        self.in_style = tag == 'style' or self.in_style

    def handle_endtag(self, tag):
        if tag == 'style':
            self.in_style = False

    def handle_data(self, data):
        if self.in_style:
            data = re.sub(r'/\*[\s\S]*?\*/', '', data)
            self.urls.extend(css_urls(data))
            self.urls.extend(CSS_IMPORT.findall(data))


def validate(root, html, page_url):
    root = root.resolve()
    source = (root / html).resolve()
    if not source.is_relative_to(root):
        raise ValueError('HTML must be inside the document root')
    page = urlsplit(page_url)
    if page.scheme not in ('https', 'http') or not page.hostname or page.username:
        raise ValueError('--page-url must be an absolute HTTP(S) URL without credentials')

    def origin(url):
        return (url.scheme.lower(), url.hostname, url.port or (443 if url.scheme == 'https' else 80))

    parser = Resources()
    parser.feed(source.read_text(encoding='utf-8'))
    queue = [(url, page_url) for url in parser.urls]
    seen = set()
    failures = []
    while queue:
        raw, base = queue.pop()
        if not raw or raw.startswith('#'):
            continue
        url = urlsplit(urljoin(base, raw))
        if url.scheme not in ('http', 'https'):
            if url.scheme not in ('data', 'mailto', 'tel'):
                failures.append({'url': raw, 'error': 'unsupported resource scheme'})
            continue
        if origin(url) != origin(page):
            continue
        relative = unquote(url.path).lstrip('/')
        # Backslashes must never become Windows filesystem separators.
        if '\\' in relative or '\x00' in relative:
            failures.append({'url': raw, 'error': 'unsafe path'})
            continue
        file = (root / relative).resolve()
        if not file.is_relative_to(root):
            failures.append({'url': raw, 'error': 'path escapes document root'})
            continue
        if file in seen:
            continue
        seen.add(file)
        if not file.is_file():
            failures.append({'url': raw, 'error': 'missing file', 'path': relative})
        elif file.suffix.lower() == '.css':
            css = re.sub(r'/\*[\s\S]*?\*/', '', file.read_text(encoding='utf-8'))
            queue.extend((item, url.geturl()) for item in css_urls(css) + CSS_IMPORT.findall(css))
    return {'checked': len(seen), 'failures': failures}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('root', type=Path)
    parser.add_argument('--html', default='index.html')
    parser.add_argument('--page-url', required=True)
    args = parser.parse_args()
    try:
        result = validate(args.root, args.html, args.page_url)
    except (OSError, ValueError) as error:
        print(json.dumps({'failures': [{'error': str(error)}]}))
        return 1
    print(json.dumps(result, ensure_ascii=True, indent=2))
    return int(bool(result['failures']))


if __name__ == '__main__':
    raise SystemExit(main())
