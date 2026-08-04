import os
import json
import base64
import hashlib
import secrets
import urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.request
import webbrowser

REDIRECT_URI = "http://localhost:8080/callback"
TOKEN_FILE = os.path.join(os.path.dirname(__file__), "swiggy_token.json")
CLIENT_ID = "swiggy-mcp" # Swiggy MCP default/DCR client id

class AuthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path.startswith("/callback"):
            query = urllib.parse.urlparse(self.path).query
            params = urllib.parse.parse_qs(query)
            if "code" in params:
                self.server.auth_code = params["code"][0]
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(b"<html><body><h1>Authentication Successful!</h1><p>You can close this window and return to your terminal.</p></body></html>")
            else:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b"No code found")
        else:
            self.send_response(404)
            self.end_headers()
            
    def log_message(self, format, *args):
        pass # Suppress logs

def authenticate():
    print("🔄 Starting Swiggy OAuth 2.1 (PKCE) flow...")
    
    # 1. PKCE
    verifier = secrets.token_urlsafe(32)
    challenge = base64.urlsafe_b64encode(hashlib.sha256(verifier.encode('ascii')).digest()).decode('ascii').rstrip('=')
    
    # 2. Redirect to authorize
    state = secrets.token_urlsafe(16)
    auth_url = f"https://mcp.swiggy.com/auth/authorize?response_type=code&client_id={CLIENT_ID}&redirect_uri={urllib.parse.quote(REDIRECT_URI)}&code_challenge={challenge}&code_challenge_method=S256&state={state}&scope=mcp:tools"
    
    print("🌐 Opening browser for Swiggy Authentication...")
    webbrowser.open(auth_url)
    
    # 3. Start local server to receive code
    print(f"⏳ Waiting for authentication callback on {REDIRECT_URI}...")
    server = HTTPServer(('localhost', 8080), AuthHandler)
    server.auth_code = None
    
    while not server.auth_code:
        server.handle_request()
        
    code = server.auth_code
    print("✅ Authorization code received! Exchanging for token...")
    
    # 4. Exchange code for token
    token_url = "https://mcp.swiggy.com/auth/token"
    data = json.dumps({
        "grant_type": "authorization_code",
        "code": code,
        "code_verifier": verifier,
        "redirect_uri": REDIRECT_URI,
        "client_id": CLIENT_ID
    }).encode('utf-8')
    
    req = urllib.request.Request(token_url, data=data, headers={'Content-Type': 'application/json'})
    try:
        with urllib.request.urlopen(req) as response:
            res = json.loads(response.read())
            access_token = res.get('access_token')
            if access_token:
                with open(TOKEN_FILE, 'w') as f:
                    json.dump(res, f)
                print(f"🎉 Authentication successful! Token saved to {TOKEN_FILE}")
                return access_token
    except urllib.error.HTTPError as e:
        print(f"❌ Error exchanging token: {e.read().decode()}")
        return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def get_access_token():
    """Retrieve existing token or authenticate if missing."""
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, 'r') as f:
            data = json.load(f)
            # Basic check, in production we would check 'expires_in' / jwt expiration
            if data.get('access_token'):
                return data['access_token']
    
    # Fallback: token not found or invalid
    print("⚠️ No valid Swiggy token found. Please run this script directly to authenticate.")
    return None

if __name__ == "__main__":
    authenticate()
