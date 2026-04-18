#!/usr/bin/env python3
"""
One-time Strava OAuth flow.
Opens the browser, captures the redirect, exchanges for tokens.
Run once to get your refresh token, then store it as a GitHub Secret.

Usage: python3 scripts/strava-auth.py
"""

import http.server
import json
import threading
import urllib.parse
import urllib.request
import webbrowser

CLIENT_ID     = "149973"
CLIENT_SECRET = "7926ca3288c78c0e15bc35dc3125819d897c8b6b"
PORT          = 8080
REDIRECT_URI  = f"http://localhost:{PORT}"
SCOPE         = "read,activity:read"

auth_url = (
    f"https://www.strava.com/oauth/authorize"
    f"?client_id={CLIENT_ID}"
    f"&redirect_uri={REDIRECT_URI}"
    f"&response_type=code"
    f"&scope={SCOPE}"
    f"&approval_prompt=auto"
)

code_holder = {"code": None}


class _Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        params = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
        if "code" in params:
            code_holder["code"] = params["code"][0]
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(
                b"<html><body style='font-family:sans-serif;padding:2rem'>"
                b"<h2>&#x2705; Authorized!</h2><p>You can close this tab.</p></body></html>"
            )
        else:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b"Authorization failed - no code received.")
        threading.Thread(target=self.server.shutdown, daemon=True).start()

    def log_message(self, *_):
        pass


print(f"\nOpening Strava authorization in your browser…")
print(f"If it doesn't open automatically, visit:\n  {auth_url}\n")
webbrowser.open(auth_url)

server = http.server.HTTPServer(("localhost", PORT), _Handler)
print(f"Waiting for Strava to redirect back (port {PORT})…")
server.serve_forever()

code = code_holder["code"]
if not code:
    raise SystemExit("❌  No authorization code received.")

print("Got code — exchanging for tokens…")
data = urllib.parse.urlencode({
    "client_id":     CLIENT_ID,
    "client_secret": CLIENT_SECRET,
    "code":          code,
    "grant_type":    "authorization_code",
}).encode()

req = urllib.request.Request(
    "https://www.strava.com/api/v3/oauth/token",
    data=data, method="POST",
    headers={"Content-Type": "application/x-www-form-urlencoded"},
)
with urllib.request.urlopen(req) as resp:
    tokens = json.loads(resp.read())

athlete = tokens.get("athlete", {})
print(f"\n✅  Authorized as: {athlete.get('firstname')} {athlete.get('lastname')}")
print(f"    Athlete ID:     {athlete.get('id')}")
print(f"\n─────────────────────────────────────────")
print(f"  ACCESS TOKEN (short-lived, ~6hrs):")
print(f"  {tokens['access_token']}")
print(f"\n  REFRESH TOKEN (long-lived — store as GitHub Secret STRAVA_REFRESH_TOKEN):")
print(f"  {tokens['refresh_token']}")
print(f"─────────────────────────────────────────")
print(f"\nNext step: python3 scripts/list-clubs.py {tokens['access_token']}")
