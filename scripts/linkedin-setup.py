#!/usr/bin/env python3
"""Interactive LinkedIn OAuth setup. One-time use — NOT part of the pipeline."""

import http.server
import json
import os
import sys
import threading
import urllib.parse
import urllib.request
import urllib.error
import webbrowser


def load_env(env_file):
    """Load key=value pairs from a .env file."""
    env = {}
    if not os.path.exists(env_file):
        return env
    with open(env_file) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" not in line:
                continue
            key, _, value = line.partition("=")
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            env[key] = value
    return env


REDIRECT_PORT = 8585
REDIRECT_URI = f"http://localhost:{REDIRECT_PORT}/callback"
SCOPES = "w_member_social openid profile"

# Will be set by the callback handler
auth_code = None
auth_error = None
server_done = threading.Event()


class OAuthCallbackHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        global auth_code, auth_error
        parsed = urllib.parse.urlparse(self.path)
        params = urllib.parse.parse_qs(parsed.query)

        if "code" in params:
            auth_code = params["code"][0]
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            self.wfile.write(b"<h1>Authorization successful!</h1><p>You can close this tab.</p>")
        elif "error" in params:
            auth_error = params.get("error_description", params["error"])[0]
            self.send_response(400)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            self.wfile.write(f"<h1>Error</h1><p>{auth_error}</p>".encode())
        else:
            self.send_response(404)
            self.end_headers()
            return

        server_done.set()

    def log_message(self, format, *args):
        pass  # Suppress server logs


def api_request(url, data=None, headers=None, method="GET"):
    """Make an API request and return parsed JSON."""
    if data and isinstance(data, dict):
        data = urllib.parse.urlencode(data).encode()
    req = urllib.request.Request(url, data=data, method=method)
    if headers:
        for k, v in headers.items():
            req.add_header(k, v)
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode())


def exchange_code(client_id, client_secret, code):
    """Exchange authorization code for tokens."""
    url = "https://www.linkedin.com/oauth/v2/accessToken"
    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URI,
        "client_id": client_id,
        "client_secret": client_secret,
    }
    return api_request(url, data=data, method="POST")


def get_user_info(access_token):
    """Fetch user info to get the person URN."""
    url = "https://api.linkedin.com/v2/userinfo"
    headers = {"Authorization": f"Bearer {access_token}"}
    return api_request(url, headers=headers)


def test_permissions(access_token, person_urn):
    """Test w_member_social by checking the posts endpoint (GET, non-destructive)."""
    url = f"https://api.linkedin.com/rest/posts?author={urllib.parse.quote(person_urn)}&q=author&count=1"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "LinkedIn-Version": "202401",
        "X-Restli-Protocol-Version": "2.0.0",
    }
    try:
        api_request(url, headers=headers)
        return True, None
    except urllib.error.HTTPError as e:
        body = e.read().decode() if e.fp else ""
        if e.code == 403:
            return False, "w_member_social permission not granted. Check your LinkedIn app's Products tab."
        return False, f"HTTP {e.code}: {body}"


def main():
    env_file = ".env"
    env = load_env(env_file)
    os.environ.update({k: v for k, v in env.items() if k not in os.environ})

    client_id = os.environ.get("LINKEDIN_CLIENT_ID")
    client_secret = os.environ.get("LINKEDIN_CLIENT_SECRET")

    if not client_id or not client_secret:
        print("Error: LINKEDIN_CLIENT_ID and LINKEDIN_CLIENT_SECRET must be set in .env")
        print()
        print("Steps:")
        print("1. Go to https://www.linkedin.com/developers/apps")
        print("2. Create or select your app")
        print("3. Copy Client ID and Client Secret")
        print('4. Add to .env: LINKEDIN_CLIENT_ID="..." and LINKEDIN_CLIENT_SECRET="..."')
        print(f'5. Under Auth, add redirect URL: {REDIRECT_URI}')
        print('6. Under Products, request "Share on LinkedIn" (for w_member_social)')
        sys.exit(1)

    print("LinkedIn OAuth Setup")
    print("=" * 40)
    print()
    print(f"Client ID: {client_id[:8]}...")
    print(f"Redirect URI: {REDIRECT_URI}")
    print(f"Scopes: {SCOPES}")
    print()

    # Build OAuth URL
    auth_url = (
        "https://www.linkedin.com/oauth/v2/authorization?"
        + urllib.parse.urlencode({
            "response_type": "code",
            "client_id": client_id,
            "redirect_uri": REDIRECT_URI,
            "scope": SCOPES,
            "state": "aica-linkedin-setup",
        })
    )

    # Start temporary server
    server = http.server.HTTPServer(("localhost", REDIRECT_PORT), OAuthCallbackHandler)
    server_thread = threading.Thread(target=server.serve_forever)
    server_thread.daemon = True
    server_thread.start()

    print("Opening browser for LinkedIn authorization...")
    print(f"If it doesn't open, visit: {auth_url}")
    print()
    webbrowser.open(auth_url)

    # Wait for callback (timeout 120s)
    server_done.wait(timeout=120)
    server.shutdown()

    if auth_error:
        print(f"Authorization failed: {auth_error}")
        sys.exit(1)

    if not auth_code:
        print("Timed out waiting for authorization callback.")
        sys.exit(1)

    print("Authorization code received. Exchanging for tokens...")

    try:
        token_data = exchange_code(client_id, client_secret, auth_code)
    except urllib.error.HTTPError as e:
        body = e.read().decode() if e.fp else ""
        print(f"Token exchange failed: HTTP {e.code}: {body}")
        sys.exit(1)

    access_token = token_data.get("access_token")
    expires_in = token_data.get("expires_in", 0)
    refresh_token = token_data.get("refresh_token", "")

    if not access_token:
        print(f"No access token in response: {json.dumps(token_data, indent=2)}")
        sys.exit(1)

    print(f"Access token obtained (expires in {expires_in // 86400} days)")

    # Fetch person URN
    print("Fetching user info...")
    try:
        user_info = get_user_info(access_token)
    except urllib.error.HTTPError as e:
        body = e.read().decode() if e.fp else ""
        print(f"Failed to fetch user info: HTTP {e.code}: {body}")
        sys.exit(1)

    sub = user_info.get("sub", "")
    name = user_info.get("name", "Unknown")
    person_urn = f"urn:li:person:{sub}"

    print(f"Authenticated as: {name}")
    print(f"Person URN: {person_urn}")

    # Test permissions
    print()
    print("Testing w_member_social permission...")
    ok, err = test_permissions(access_token, person_urn)
    if ok:
        print("w_member_social: OK")
    else:
        print(f"w_member_social: FAILED - {err}")
        print()
        print("The pipeline will still generate video clips for manual upload.")
        print("To enable automated posting:")
        print("1. Go to your LinkedIn Developer App > Products")
        print('2. Request "Share on LinkedIn" product')
        print("3. Re-run this setup after approval")

    # Print env vars
    print()
    print("=" * 40)
    print("Add these to your .env file:")
    print("=" * 40)
    print()
    print(f'LINKEDIN_ACCESS_TOKEN="{access_token}"')
    print(f'LINKEDIN_PERSON_URN="{person_urn}"')
    if refresh_token:
        print(f'LINKEDIN_REFRESH_TOKEN="{refresh_token}"')
    print()
    print(f"# Token expires in {expires_in // 86400} days ({expires_in}s)")
    if not ok:
        print("# WARNING: w_member_social not available — posting will fail until granted")


if __name__ == "__main__":
    main()
