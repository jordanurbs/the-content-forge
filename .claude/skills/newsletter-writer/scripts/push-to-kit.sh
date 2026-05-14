#!/usr/bin/env bash
# push-to-kit.sh — Push a newsletter draft to Kit as a broadcast draft
# Usage: ./push-to-kit.sh <subject> <html-file-or-stdin>
#
# Reads KIT_API_KEY from the .env file in the skill directory.
# NEVER sets send_at — always saves as draft for manual send.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"

# Load API key
if [ -f "$SKILL_DIR/.env" ]; then
  export $(grep -v '^#' "$SKILL_DIR/.env" | xargs)
fi

if [ -z "${KIT_API_KEY:-}" ]; then
  echo "Error: KIT_API_KEY not set. Check .env file." >&2
  exit 1
fi

SUBJECT="${1:?Usage: push-to-kit.sh <subject> [html-file]}"
HTML_FILE="${2:-}"

if [ -n "$HTML_FILE" ] && [ -f "$HTML_FILE" ]; then
  HTML_CONTENT=$(cat "$HTML_FILE")
else
  echo "Reading HTML from stdin..." >&2
  HTML_CONTENT=$(cat)
fi

# Escape JSON special characters
JSON_SUBJECT=$(echo "$SUBJECT" | python3 -c 'import json,sys; print(json.dumps(sys.stdin.read().strip()))')
JSON_CONTENT=$(echo "$HTML_CONTENT" | python3 -c 'import json,sys; print(json.dumps(sys.stdin.read().strip()))')

# Email template ID is read from $KIT_EMAIL_TEMPLATE_ID env var (optional)
KIT_EMAIL_TEMPLATE_ID="${KIT_EMAIL_TEMPLATE_ID:-}"

RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "https://api.kit.com/v4/broadcasts" \
  -H "X-Kit-Api-Key: $KIT_API_KEY" \
  -H "Content-Type: application/json" \
  -d "{
    \"subject\": $JSON_SUBJECT,
    \"content\": $JSON_CONTENT,
    \"email_template_id\": $KIT_EMAIL_TEMPLATE_ID,
    \"send_at\": null,
    \"public\": true
  }")

HTTP_CODE=$(echo "$RESPONSE" | tail -1)
BODY=$(echo "$RESPONSE" | sed '$d')

if [ "$HTTP_CODE" -ge 200 ] && [ "$HTTP_CODE" -lt 300 ]; then
  BROADCAST_ID=$(echo "$BODY" | python3 -c 'import json,sys; d=json.load(sys.stdin); print(d.get("broadcast",{}).get("id","unknown"))' 2>/dev/null || echo "unknown")
  echo "✅ Pushed to Kit as draft (Broadcast ID: $BROADCAST_ID)"
  echo "$BROADCAST_ID"
else
  echo "❌ Kit API error (HTTP $HTTP_CODE):" >&2
  echo "$BODY" >&2
  exit 1
fi
