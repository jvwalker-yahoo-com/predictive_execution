"""
eToro ReAuth Standalone APK Mobile Delivery Server
Runs a local Wi-Fi HTTP distribution server with a mobile download page and QR code.
"""
import os
import sys
import socket
import hashlib
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler

PORT = 8080
WORKSPACE_DIR = Path(__file__).resolve().parent
APK_PATH = WORKSPACE_DIR / "etoro-authorizer.apk"

def get_lan_ip():
    """Detect local LAN IP address."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # Does not actually send data
        s.connect(('8.8.8.8', 1))
        ip = s.getsockname()[0]
    except Exception:
        ip = '127.0.0.1'
    finally:
        s.close()
    return ip

def get_file_sha256(filepath):
    """Compute SHA256 checksum of the APK."""
    h = hashlib.sha256()
    with open(filepath, 'rb') as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()

def render_ascii_qr(data_str):
    """Renders an ASCII QR code in terminal if qrcode library is available."""
    try:
        import qrcode
        qr = qrcode.QRCode(border=1)
        qr.add_data(data_str)
        qr.make(fit=True)
        import io
        f = io.StringIO()
        qr.print_ascii(out=f, invert=True)
        return f.getvalue()
    except Exception:
        return None

class ApkDeliveryHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path in ("/", "/index.html"):
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()

            apk_size_kb = APK_PATH.stat().st_size / 1024 if APK_PATH.exists() else 0
            sha256 = get_file_sha256(APK_PATH) if APK_PATH.exists() else "N/A"

            html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Download eToro ReAuth Mobile</title>
  <style>
    body {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      background: #070a10;
      color: #f1f5f9;
      display: flex;
      justify-content: center;
      align-items: center;
      min-height: 100vh;
      margin: 0;
      padding: 16px;
    }}
    .box {{
      background: #0d131f;
      border: 1px solid #10b981;
      border-radius: 12px;
      padding: 24px;
      max-width: 440px;
      width: 100%;
      text-align: center;
      box-shadow: 0 0 24px rgba(16, 185, 129, 0.2);
    }}
    .badge {{
      display: inline-block;
      background: #064e3b;
      color: #34d399;
      font-size: 11px;
      font-weight: bold;
      padding: 4px 10px;
      border-radius: 999px;
      margin-bottom: 12px;
      letter-spacing: 1px;
    }}
    h1 {{ font-size: 22px; margin: 0 0 6px; color: #fff; }}
    p {{ font-size: 13px; color: #94a3b8; margin: 0 0 20px; }}
    .btn {{
      display: block;
      background: linear-gradient(135deg, #059669 0%, #10b981 100%);
      color: #fff;
      text-decoration: none;
      font-weight: bold;
      font-size: 15px;
      padding: 14px 20px;
      border-radius: 8px;
      box-shadow: 0 4px 16px rgba(16, 185, 129, 0.4);
      margin-bottom: 20px;
    }}
    .meta {{
      font-size: 11px;
      color: #64748b;
      text-align: left;
      background: #030712;
      padding: 12px;
      border-radius: 6px;
      border: 1px solid #1e293b;
      word-break: break-all;
    }}
    .meta strong {{ color: #cbd5e1; }}
    .steps {{
      font-size: 12px;
      color: #94a3b8;
      text-align: left;
      margin-top: 16px;
      line-height: 1.6;
    }}
  </style>
</head>
<body>
  <div class="box">
    <span class="badge">STANDALONE APK v1.0.0</span>
    <h1>eToro ReAuth</h1>
    <p>Predictive Execution Cockpit Mobile Companion</p>
    <a href="/etoro-authorizer.apk" class="btn" download>📥 DOWNLOAD APK ({apk_size_kb:.1f} KB)</a>
    <div class="meta">
      <div><strong>File:</strong> etoro-authorizer.apk</div>
      <div><strong>Package:</strong> com.cockpit.etoroauth</div>
      <div><strong>Target SDK:</strong> Android 35 (Android 15)</div>
      <div><strong>SHA256:</strong> {sha256[:16]}...{sha256[-16:]}</div>
    </div>
    <div class="steps">
      <strong>Installation Instructions:</strong>
      <ol style="margin-top:6px; padding-left:18px;">
        <li>Tap the button above to download.</li>
        <li>Open the downloaded file on your phone.</li>
        <li>If prompted, tap "Settings" and enable "Allow from this source".</li>
        <li>Tap "Install" &amp; launch!</li>
      </ol>
    </div>
  </div>
</body>
</html>"""
            self.wfile.write(html.encode("utf-8"))

        elif self.path in ("/etoro-authorizer.apk", "/download"):
            if not APK_PATH.exists():
                self.send_error(404, "APK not found. Please build it first.")
                return

            self.send_response(200)
            self.send_header("Content-Type", "application/vnd.android.package-archive")
            self.send_header("Content-Length", str(APK_PATH.stat().st_size))
            self.send_header("Content-Disposition", 'attachment; filename="etoro-authorizer.apk"')
            self.end_headers()

            with open(APK_PATH, "rb") as f:
                while chunk := f.read(65536):
                    self.wfile.write(chunk)
        else:
            self.send_error(404, "Not Found")

    def log_message(self, format, *args):
        print(f"[HTTP] {self.address_string()} - {args[0]}")

def main():
    if not APK_PATH.exists():
        print(f"Error: APK file not found at {APK_PATH}")
        print("Please run build_apk.py first.")
        return 1

    ip = get_lan_ip()
    url = f"http://{ip}:{PORT}"

    print("=" * 60)
    print("      eToro ReAuth Standalone APK Delivery Server")
    print("=" * 60)
    print(f"APK Path:     {APK_PATH}")
    print(f"File Size:    {APK_PATH.stat().st_size:,} bytes")
    print(f"Local URL:    http://localhost:{PORT}")
    print(f"Phone Wi-Fi:  {url}")
    print("=" * 60)

    qr = render_ascii_qr(url)
    if qr:
        print("\nScan this QR Code with your phone camera:")
        print(qr)
    else:
        print(f"\nOpen this link in your mobile browser:\n  -> {url}\n")

    print("Press Ctrl+C to stop the server.\n")

    server = HTTPServer(("0.0.0.0", PORT), ApkDeliveryHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
