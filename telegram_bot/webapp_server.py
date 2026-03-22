"""Simple HTTP server to serve the Telegram Mini App files."""
import os
import logging
from http.server import HTTPServer, SimpleHTTPRequestHandler
import threading
import config

logger = logging.getLogger(__name__)

WEBAPP_DIR = os.path.join(os.path.dirname(__file__), 'webapp')
WEBAPP_PORT = int(os.getenv('WEBAPP_PORT', '8080'))


class WebAppHandler(SimpleHTTPRequestHandler):
    """Serve webapp files with proper CORS and content injection."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=WEBAPP_DIR, **kwargs)

    def do_GET(self):
        if self.path == '/' or self.path == '/index.html':
            self._serve_index()
        else:
            super().do_GET()

    def _serve_index(self):
        index_path = os.path.join(WEBAPP_DIR, 'index.html')
        with open(index_path, 'r', encoding='utf-8') as f:
            html = f.read()

        # Inject backend URL config
        backend_url = config.BACKEND_URL
        device_id = config.DEVICE_ID
        inject = f"""<script>
window.__API_BASE__ = '{backend_url}';
window.__DEVICE_ID__ = '{device_id}';
</script>"""
        html = html.replace('</head>', inject + '\n</head>')

        data = html.encode('utf-8')
        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.send_header('Content-Length', len(data))
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(data)

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.end_headers()

    def log_message(self, format, *args):
        logger.debug(f"WebApp: {args[0]}")


def start_webapp_server():
    """Start webapp HTTP server in a background thread."""
    server = HTTPServer(('0.0.0.0', WEBAPP_PORT), WebAppHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    logger.info(f'WebApp server started on port {WEBAPP_PORT}')
    return server
