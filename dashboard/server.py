# =========================================================
# Simple Static Dashboard Server
# =========================================================

import http.server
import socketserver
import os

PORT = 3000

# Serve files from the directory where server.py lives
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(BASE_DIR)

class Handler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        # Cleaner logs
        print("SERVER:", format % args)

print("==============================================")
print(" Predictive Execution Dashboard Server")
print("==============================================")
print(f"Serving files from: {BASE_DIR}")
print(f"Dashboard URL: http://127.0.0.1:{PORT}/index.html")
print("Press CTRL+C to stop the server.")
print("==============================================")

with socketserver.TCPServer(("", PORT), Handler) as httpd:
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nSERVER: Shutting down...")
