#!/usr/bin/env python3
"""Send emails via Mailgun API. Stdlib only — no pip dependencies."""

import argparse
import base64
import json
import os
import sys
import urllib.request
import urllib.error
import urllib.parse


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


def send_email(api_key, domain, from_addr, to_addr, subject, html_body, cc=None):
    """Send an email via Mailgun API."""
    url = f"https://api.mailgun.net/v3/{domain}/messages"

    data = {
        "from": from_addr,
        "to": to_addr,
        "subject": subject,
        "html": html_body,
    }
    if cc:
        data["cc"] = cc

    encoded = urllib.parse.urlencode(data).encode("utf-8")
    credentials = base64.b64encode(f"api:{api_key}".encode()).decode()

    req = urllib.request.Request(url, data=encoded, method="POST")
    req.add_header("Authorization", f"Basic {credentials}")
    req.add_header("Content-Type", "application/x-www-form-urlencoded")

    try:
        with urllib.request.urlopen(req) as resp:
            result = json.loads(resp.read().decode())
            print(f"Status: SUCCESS")
            print(f"Message: {result.get('message', 'Queued')}")
            print(f"ID: {result.get('id', 'unknown')}")
            return True
    except urllib.error.HTTPError as e:
        body = e.read().decode() if e.fp else ""
        print(f"Status: FAILURE")
        print(f"HTTP {e.code}: {body}")
        return False
    except urllib.error.URLError as e:
        print(f"Status: FAILURE")
        print(f"Error: {e.reason}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Send email via Mailgun API")
    parser.add_argument("--to", required=True, help="Recipient email address")
    parser.add_argument("--subject", required=True, help="Email subject line")
    parser.add_argument("--html-file", required=True, help="Path to HTML file for email body")
    parser.add_argument("--cc", help="CC email address")
    parser.add_argument("--env-file", default=".env", help="Path to .env file (default: .env)")

    args = parser.parse_args()

    # Load env
    env = load_env(args.env_file)
    os.environ.update({k: v for k, v in env.items() if k not in os.environ})

    api_key = os.environ.get("MAILGUN_API_KEY")
    domain = os.environ.get("MAILGUN_DOMAIN")
    from_addr = os.environ.get("EMAIL_FROM")

    if not all([api_key, domain, from_addr]):
        print("Status: FAILURE")
        print("Error: Missing MAILGUN_API_KEY, MAILGUN_DOMAIN, or EMAIL_FROM in environment/.env")
        sys.exit(1)

    if not os.path.exists(args.html_file):
        print("Status: FAILURE")
        print(f"Error: HTML file not found: {args.html_file}")
        sys.exit(1)

    with open(args.html_file) as f:
        html_body = f.read()

    # --cc flag explicitly set (even to empty string) overrides env var
    cc = args.cc if args.cc is not None else os.environ.get("EMAIL_CC")

    success = send_email(api_key, domain, from_addr, args.to, args.subject, html_body, cc)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
