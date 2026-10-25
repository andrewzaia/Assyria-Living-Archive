"""Build a local root-path preview independently of production URL settings."""
import argparse
import http.server
import os
from pathlib import Path
import subprocess
import sys
from functools import partial

ROOT = Path(__file__).resolve().parents[1]

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--port', type=int, default=8000)
    args = parser.parse_args()
    environment = os.environ.copy()
    environment.update(BASE_PATH='', SITE_URL='', ALLOW_INDEXING='false')
    subprocess.run([sys.executable, 'generate.py'], cwd=ROOT, env=environment, check=True)
    handler = partial(http.server.SimpleHTTPRequestHandler, directory=str(ROOT / 'dist'))
    with http.server.ThreadingHTTPServer(('127.0.0.1', args.port), handler) as server:
        print(f'Local preview: http://127.0.0.1:{args.port}/', flush=True)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print('\nPreview stopped.')

if __name__ == '__main__':
    main()
