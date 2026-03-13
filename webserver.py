# webserver.py
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading


class KeepAliveHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(b"The bot is active!")


def keep_alive():
    """Start the web server in a separate thread"""

    def run_server():
        server = HTTPServer(('0.0.0.0', 8080), KeepAliveHandler)
        server.serve_forever()

    web_thread = threading.Thread(target=run_server)
    web_thread.daemon = True
    web_thread.start()
    print("Web server started on port 8080")