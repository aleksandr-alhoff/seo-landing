"""Optional real-server tests. Set NGINX_EXE and OPENSSL_EXE to local binaries."""
import http.client
import os
import re
import socket
import ssl
import subprocess
import tempfile
import time
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def port():
    with socket.socket() as connection:
        connection.bind(('127.0.0.1', 0))
        return connection.getsockname()[1]


@unittest.skipUnless(os.environ.get('NGINX_EXE') and os.environ.get('OPENSSL_EXE'),
                     'set NGINX_EXE and OPENSSL_EXE for real HTTP/HTTPS checks')
class NginxReferenceTests(unittest.TestCase):
    def test_syntax_https_headers_and_missing_asset_caching(self):
        nginx = str(Path(os.environ['NGINX_EXE']).resolve())
        openssl = str(Path(os.environ['OPENSSL_EXE']).resolve())
        doc = (ROOT / 'references/server-config.md').read_text(encoding='utf-8')
        block = next(x for x in re.findall(r'```nginx\n(.*?)```', doc, re.DOTALL) if 'location ~*' in x)
        # The reference explicitly permits gzip-only when ngx_brotli is absent.
        block = re.sub(r'^brotli.*\n', '', block, flags=re.MULTILINE)
        security = '\n'.join(re.findall(r'^#   (add_header .*;)$', block, re.MULTILINE))
        hsts = next(x for x in re.findall(r'```nginx\n(.*?)```', doc, re.DOTALL)
                    if 'add_header Strict-Transport-Security "max-age=300"' in x)
        tls_block = block.replace('include conf.d/security-headers.conf;',
                                  'include conf.d/security-headers.conf; include conf.d/hsts-https.conf;')
        http_port, tls_port = port(), port()
        while tls_port == http_port:
            tls_port = port()
        with tempfile.TemporaryDirectory(prefix='seo-nginx-') as directory:
            prefix = Path(directory)
            for name in ('conf.d', 'logs', 'html', 'temp'):
                (prefix / name).mkdir()
            (prefix / 'conf.d/security-headers.conf').write_text(security, encoding='utf-8')
            (prefix / 'conf.d/hsts-https.conf').write_text(hsts, encoding='utf-8')
            for name in ('index.html', 'app.1234abcd.css', 'robots.txt', 'sitemap.xml'):
                (prefix / 'html' / name).write_text('test', encoding='utf-8')
            subprocess.run([openssl, 'req', '-x509', '-newkey', 'rsa:2048', '-nodes', '-days', '1',
                            '-subj', '/CN=localhost', '-keyout', str(prefix / 'key.pem'),
                            '-out', str(prefix / 'cert.pem')], check=True, capture_output=True)
            config = ('worker_processes 1; daemon off; master_process off;\n'
                      'events { worker_connections 64; }\nhttp {\n'
                      f'server {{ listen 127.0.0.1:{http_port}; root html;\n{block}\n}}\n'
                      f'server {{ listen 127.0.0.1:{tls_port} ssl; root html; '
                      'ssl_certificate cert.pem; ssl_certificate_key key.pem;\n'
                      f'{tls_block}\n}}\n}}')
            (prefix / 'nginx.conf').write_text(config, encoding='utf-8')
            command = [nginx, '-p', prefix.as_posix() + '/', '-c', 'nginx.conf']
            syntax = subprocess.run([*command, '-t'], capture_output=True, text=True, check=False)
            self.assertEqual(syntax.returncode, 0, syntax.stderr)
            process = subprocess.Popen(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                                       creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
            try:
                for attempt in range(50):
                    try:
                        with socket.create_connection(('127.0.0.1', http_port), timeout=.2):
                            break
                    except OSError:
                        time.sleep(.1)
                for secure in (False, True):
                    for url in ('/', '/index.html', '/app.1234abcd.css', '/missing.1234abcd.css', '/robots.txt', '/sitemap.xml'):
                        connection = (http.client.HTTPSConnection('127.0.0.1', tls_port,
                                      context=ssl._create_unverified_context(), timeout=5)
                                      if secure else http.client.HTTPConnection('127.0.0.1', http_port, timeout=5))
                        connection.request('GET', url)
                        response = connection.getresponse()
                        headers = response.getheaders()
                        response.read()
                        connection.close()
                        for header in ('X-Content-Type-Options', 'X-Frame-Options', 'Permissions-Policy', 'Referrer-Policy'):
                            self.assertEqual(len([v for k, v in headers if k.lower() == header.lower()]), 1, (url, header))
                        sts = [v for k, v in headers if k.lower() == 'strict-transport-security']
                        self.assertEqual(sts, ['max-age=300'] if secure else [], url)
                        cache = ','.join(v for k, v in headers if k.lower() == 'cache-control')
                        if 'missing' in url:
                            self.assertEqual(response.status, 404)
                            self.assertNotIn('immutable', cache)
                        else:
                            self.assertEqual(response.status, 200)
                        if url == '/app.1234abcd.css':
                            self.assertIn('immutable', cache)
            finally:
                process.terminate()
                process.wait(timeout=10)


if __name__ == '__main__':
    unittest.main()
