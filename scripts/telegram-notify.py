#!/usr/bin/env python3
"""Send messages via Telegram Bot API. Stdlib only — no pip dependencies."""

import argparse
import json
import os
import sys
import urllib.request
import urllib.error

MAX_MESSAGE_LENGTH = 4096


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


def resolve_chat_id(chat_id_arg, env):
    """Resolve chat ID: accept numeric ID or env var name."""
    # If it looks like a number (with optional leading dash), use it directly
    stripped = chat_id_arg.strip()
    if stripped.lstrip("-").isdigit():
        return stripped
    # Otherwise treat as env var name
    resolved = env.get(stripped) or os.environ.get(stripped)
    if resolved:
        return resolved
    print(f"Status: FAILURE")
    print(f"Error: Could not resolve chat ID '{chat_id_arg}' — not a number and not found in env")
    sys.exit(1)


def send_message(bot_token, chat_id, text, parse_mode=None):
    """Send a single message via Telegram Bot API."""
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"

    payload = {
        "chat_id": chat_id,
        "text": text,
    }
    if parse_mode:
        payload["parse_mode"] = parse_mode
        # Disable link previews for cleaner messages
        payload["disable_web_page_preview"] = True

    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, method="POST")
    req.add_header("Content-Type", "application/json")

    try:
        with urllib.request.urlopen(req) as resp:
            result = json.loads(resp.read().decode())
            if result.get("ok"):
                return True
            print(f"Status: FAILURE")
            print(f"Telegram error: {result.get('description', 'unknown')}")
            return False
    except urllib.error.HTTPError as e:
        body = e.read().decode() if e.fp else ""
        print(f"Status: FAILURE")
        print(f"HTTP {e.code}: {body}")
        return False
    except urllib.error.URLError as e:
        print(f"Status: FAILURE")
        print(f"Error: {e.reason}")
        return False


def split_message(text):
    """Split text into chunks of MAX_MESSAGE_LENGTH, breaking at newlines when possible."""
    if len(text) <= MAX_MESSAGE_LENGTH:
        return [text]

    chunks = []
    while text:
        if len(text) <= MAX_MESSAGE_LENGTH:
            chunks.append(text)
            break
        # Find last newline within the limit
        split_at = text.rfind("\n", 0, MAX_MESSAGE_LENGTH)
        if split_at == -1:
            split_at = MAX_MESSAGE_LENGTH
        chunks.append(text[:split_at])
        text = text[split_at:].lstrip("\n")
    return chunks


def main():
    parser = argparse.ArgumentParser(description="Send message via Telegram Bot API")
    parser.add_argument("--chat-id", required=True,
                        help="Chat ID (numeric) or env var name (e.g. TELEGRAM_TWEETS_ID)")
    parser.add_argument("--message", help="Message text to send")
    parser.add_argument("--file", help="Path to text file to send as message content")
    parser.add_argument("--parse-mode", choices=["markdown", "html", "MarkdownV2"],
                        help="Telegram parse mode")
    parser.add_argument("--env-file", default=".env", help="Path to .env file (default: .env)")

    args = parser.parse_args()

    if not args.message and not args.file:
        print("Status: FAILURE")
        print("Error: Provide --message or --file")
        sys.exit(1)

    # Load env
    env = load_env(args.env_file)
    os.environ.update({k: v for k, v in env.items() if k not in os.environ})

    bot_token = os.environ.get("TELEGRAM_BOT_TOKEN")
    if not bot_token:
        print("Status: FAILURE")
        print("Error: TELEGRAM_BOT_TOKEN not found in environment/.env")
        sys.exit(1)

    chat_id = resolve_chat_id(args.chat_id, env)

    # Build message text
    if args.file:
        if not os.path.exists(args.file):
            print("Status: FAILURE")
            print(f"Error: File not found: {args.file}")
            sys.exit(1)
        with open(args.file) as f:
            text = f.read()
    else:
        text = args.message

    if not text.strip():
        print("Status: FAILURE")
        print("Error: Empty message")
        sys.exit(1)

    # Split and send
    chunks = split_message(text)
    success_count = 0
    for i, chunk in enumerate(chunks):
        ok = send_message(bot_token, chat_id, chunk, args.parse_mode)
        if ok:
            success_count += 1

    total = len(chunks)
    if success_count == total:
        print(f"Status: SUCCESS")
        print(f"Messages sent: {total}")
    else:
        print(f"Status: PARTIAL")
        print(f"Messages sent: {success_count}/{total}")
        sys.exit(1)


if __name__ == "__main__":
    main()
