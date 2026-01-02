import http.server
import socketserver
import json
import os
import sys

# Configuration
PORT = 8001
# Get the directory where the script is located to ensure absolute paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
WEB_ROOT = os.path.join(SCRIPT_DIR, "js-3d-area-explorer", "src")

class ExegetHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        # Serve files from the WEB_ROOT directory
        super().__init__(*args, directory=WEB_ROOT, **kwargs)

    def do_GET(self):
        print(f"📥 GET Request: {self.path}")
        # Debug: Check if file exists
        full_path = self.translate_path(self.path)
        if not os.path.exists(full_path):
            print(f"❌ File not found: {full_path}")
        else:
            print(f"✅ Serving: {full_path}")
        super().do_GET()

    def do_POST(self):
        """Handle Config Saves"""
        if self.path == '/save-config':
            try:
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length)
                new_config = json.loads(post_data)
                
                config_path = os.path.join(WEB_ROOT, "config.json")
                
                # Write directly to file
                with open(config_path, 'w', encoding='utf-8') as f:
                    json.dump(new_config, f, indent=2, ensure_ascii=False)
                
                print(f"✅ Config updated with {len(new_config.get('sectors', []))} sectors.")
                
                self.send_response(200)
                self.send_header('Content-type', 'text/plain')
                self.end_headers()
                self.wfile.write(b"Config saved successfully")
            except Exception as e:
                print(f"❌ Error saving config: {e}")
                self.send_response(500)
                self.end_headers()
                self.wfile.write(str(e).encode())
        else:
            self.send_response(404)
            self.end_headers()

if __name__ == "__main__":
    # Ensure we are in the right directory context
    if not os.path.exists(WEB_ROOT):
        print(f"❌ Error: Web root '{WEB_ROOT}' not found.")
        print(f"Script location: {SCRIPT_DIR}")
        sys.exit(1)

    print(f"🌍 Exeget:OS Server running on http://localhost:{PORT}")
    print(f"📂 Serving: {WEB_ROOT}")
    print("✨ Features: POST /save-config enabled")

    # Allow address reuse to prevent "Address already in use" errors during restarts
    socketserver.TCPServer.allow_reuse_address = True
    
    with socketserver.TCPServer(("", PORT), ExegetHandler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n🛑 Server stopped.")
