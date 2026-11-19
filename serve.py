#!/usr/bin/env python3
"""Open this standalone site on this computer, without external services."""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import argparse
import threading
import webbrowser

ROOT = Path(__file__).resolve().parent

def main():
    parser = argparse.ArgumentParser(description='Preview Digiator Final locally.')
    parser.add_argument('--port', type=int, default=8352)
    parser.add_argument('--no-browser', action='store_true')
    args = parser.parse_args()
    handler = partial(SimpleHTTPRequestHandler, directory=str(ROOT / 'dist'))
    try:
        server = ThreadingHTTPServer(('127.0.0.1', args.port), handler)
    except OSError as error:
        parser.exit(1, f'Could not start the local preview: {error}\nTry python3 serve.py --port 8354\n')
    url = f'http://127.0.0.1:{args.port}/'
    print(f'\nDigiator — Final\n{url}\n\nKeep this window open while viewing the website.\nPress Control+C to stop.\n', flush=True)
    if not args.no_browser:
        threading.Timer(0.5, lambda: webbrowser.open(url)).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print('\nPreview stopped.')
    finally:
        server.server_close()

if __name__ == '__main__':
    main()
