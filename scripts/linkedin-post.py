#!/usr/bin/env python3
"""Post to LinkedIn as a draft. Stdlib only -- no pip dependencies."""

import argparse
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request
import urllib.error

API_BASE = "https://api.linkedin.com"
API_VERSION = "202401"
CHUNK_SIZE = 4 * 1024 * 1024  # 4MB


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


def li_headers(access_token, extra=None):
    """Standard LinkedIn API headers."""
    h = {
        "Authorization": f"Bearer {access_token}",
        "LinkedIn-Version": API_VERSION,
        "X-Restli-Protocol-Version": "2.0.0",
    }
    if extra:
        h.update(extra)
    return h


def li_request(url, access_token, data=None, method="GET", extra_headers=None, raw_data=None):
    """Make a LinkedIn API request."""
    headers = li_headers(access_token, extra_headers)
    body = None
    if data is not None:
        body = json.dumps(data).encode()
        headers["Content-Type"] = "application/json"
    elif raw_data is not None:
        body = raw_data

    req = urllib.request.Request(url, data=body, method=method)
    for k, v in headers.items():
        req.add_header(k, v)

    resp = urllib.request.urlopen(req)
    content = resp.read().decode() if resp.length != 0 else ""
    if content:
        return json.loads(content), resp.status
    return {}, resp.status


def refresh_access_token(client_id, client_secret, refresh_token):
    """Attempt to refresh the access token."""
    url = "https://www.linkedin.com/oauth/v2/accessToken"
    data = urllib.parse.urlencode({
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
        "client_id": client_id,
        "client_secret": client_secret,
    }).encode()
    req = urllib.request.Request(url, data=data, method="POST")
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode())


def read_post_text(file_path):
    """Read post text from markdown file, stripping metadata headers."""
    with open(file_path) as f:
        content = f.read()

    # Strip YAML frontmatter if present
    if content.startswith("---"):
        end = content.find("---", 3)
        if end != -1:
            content = content[end + 3:].strip()

    # Strip leading markdown heading (# Title)
    lines = content.split("\n")
    cleaned = []
    skip_header = True
    for line in lines:
        if skip_header and re.match(r"^#+\s+", line):
            skip_header = False
            continue
        skip_header = False
        cleaned.append(line)

    return "\n".join(cleaned).strip()


def upload_video(access_token, person_urn, video_path):
    """Upload video via LinkedIn Videos API (initialize -> chunks -> finalize -> poll)."""
    file_size = os.path.getsize(video_path)

    # Step 1: Initialize upload
    init_data = {
        "initializeUploadRequest": {
            "owner": person_urn,
            "fileSizeBytes": file_size,
        }
    }
    init_resp, _ = li_request(
        f"{API_BASE}/rest/videos?action=initializeUpload",
        access_token,
        data=init_data,
        method="POST",
    )

    upload_info = init_resp.get("value", {})
    video_urn = upload_info.get("video")
    upload_instructions = upload_info.get("uploadInstructions", [])

    if not video_urn or not upload_instructions:
        raise RuntimeError(f"Video init failed: {json.dumps(init_resp, indent=2)}")

    print(f"  Video URN: {video_urn}")
    print(f"  Upload chunks: {len(upload_instructions)}")

    # Step 2: Upload chunks
    with open(video_path, "rb") as f:
        for i, instruction in enumerate(upload_instructions):
            upload_url = instruction["uploadUrl"]
            # Read the chunk
            chunk = f.read(CHUNK_SIZE)
            if not chunk:
                break

            req = urllib.request.Request(upload_url, data=chunk, method="PUT")
            req.add_header("Content-Type", "application/octet-stream")
            req.add_header("Authorization", f"Bearer {access_token}")
            urllib.request.urlopen(req)
            print(f"  Chunk {i + 1}/{len(upload_instructions)} uploaded")

    # Step 3: Finalize upload
    finalize_data = {
        "finalizeUploadRequest": {
            "video": video_urn,
            "uploadToken": "",
            "uploadedPartIds": [],
        }
    }
    li_request(
        f"{API_BASE}/rest/videos?action=finalizeUpload",
        access_token,
        data=finalize_data,
        method="POST",
    )

    # Step 4: Poll until AVAILABLE (max 5 min)
    print("  Waiting for video processing...")
    encoded_urn = urllib.parse.quote(video_urn, safe="")
    for attempt in range(60):
        time.sleep(5)
        try:
            status_resp, _ = li_request(
                f"{API_BASE}/rest/videos/{encoded_urn}",
                access_token,
            )
            status = status_resp.get("status")
            if status == "AVAILABLE":
                print("  Video: AVAILABLE")
                return video_urn
            if status in ("PROCESSING_FAILED", "UPLOAD_FAILED"):
                raise RuntimeError(f"Video processing failed: {status}")
            print(f"  Video status: {status} (attempt {attempt + 1}/60)")
        except urllib.error.HTTPError:
            pass  # Retry on transient errors

    raise RuntimeError("Video processing timed out (5 min)")


def create_draft_post(access_token, person_urn, text, video_urn=None):
    """Create a LinkedIn DRAFT post."""
    post_data = {
        "author": person_urn,
        "commentary": text,
        "visibility": "PUBLIC",
        "lifecycleState": "DRAFT",
        "distribution": {
            "feedDistribution": "MAIN_FEED",
            "targetEntities": [],
            "thirdPartyDistributionChannels": [],
        },
    }

    if video_urn:
        post_data["content"] = {
            "media": {
                "id": video_urn,
            }
        }

    try:
        resp_body, status = li_request(
            f"{API_BASE}/rest/posts",
            access_token,
            data=post_data,
            method="POST",
        )
        return resp_body, status
    except urllib.error.HTTPError as e:
        body = e.read().decode() if e.fp else ""
        return {"error": body, "status": e.code}, e.code


def main():
    parser = argparse.ArgumentParser(description="Post to LinkedIn as a draft")
    parser.add_argument("--post-file", required=True, help="Path to post markdown file")
    parser.add_argument("--video-file", help="Path to video file for attachment")
    parser.add_argument("--env-file", default=".env", help="Path to .env file")

    args = parser.parse_args()

    # Load env
    env = load_env(args.env_file)
    os.environ.update({k: v for k, v in env.items() if k not in os.environ})

    access_token = os.environ.get("LINKEDIN_ACCESS_TOKEN")
    person_urn = os.environ.get("LINKEDIN_PERSON_URN")

    if not access_token or not person_urn:
        print("Status: SKIPPED")
        print("Reason: Missing LINKEDIN_ACCESS_TOKEN or LINKEDIN_PERSON_URN")
        print("Run: python3 scripts/linkedin-setup.py")
        sys.exit(0)

    if not os.path.exists(args.post_file):
        print("Status: FAILURE")
        print(f"Error: Post file not found: {args.post_file}")
        sys.exit(1)

    if args.video_file and not os.path.exists(args.video_file):
        print("Status: FAILURE")
        print(f"Error: Video file not found: {args.video_file}")
        sys.exit(1)

    # Validate video constraints if provided
    if args.video_file:
        file_size = os.path.getsize(args.video_file)
        if file_size > 5 * 1024 * 1024 * 1024:
            print("Status: FAILURE")
            print("Error: Video exceeds 5GB LinkedIn limit")
            sys.exit(1)

    # Read post text
    post_text = read_post_text(args.post_file)
    if not post_text:
        print("Status: FAILURE")
        print("Error: Post file is empty after stripping headers")
        sys.exit(1)

    print(f"Post text: {len(post_text)} chars")

    # Upload video if provided
    video_urn = None
    if args.video_file:
        print(f"Uploading video: {args.video_file}")
        try:
            video_urn = upload_video(access_token, person_urn, args.video_file)
        except Exception as e:
            print(f"Status: FAILURE")
            print(f"Error: Video upload failed: {e}")
            sys.exit(1)

    # Create draft post (with retry on 401)
    retried = False
    while True:
        try:
            resp, status = create_draft_post(access_token, person_urn, post_text, video_urn)
        except Exception as e:
            print(f"Status: FAILURE")
            print(f"Error: {e}")
            sys.exit(1)

        if status in (200, 201):
            print("Status: SUCCESS")
            print("LinkedIn draft created.")
            sys.exit(0)

        error_status = resp.get("status", status)

        # 401: try token refresh once
        if error_status == 401 and not retried:
            retried = True
            client_id = os.environ.get("LINKEDIN_CLIENT_ID")
            client_secret = os.environ.get("LINKEDIN_CLIENT_SECRET")
            refresh_token = os.environ.get("LINKEDIN_REFRESH_TOKEN")

            if client_id and client_secret and refresh_token:
                print("Access token expired, attempting refresh...")
                try:
                    token_data = refresh_access_token(client_id, client_secret, refresh_token)
                    access_token = token_data.get("access_token", access_token)
                    print("Token refreshed, retrying...")
                    continue
                except Exception as e:
                    print(f"Token refresh failed: {e}")

            print("Status: FAILURE")
            print("Error: Unauthorized (401). Token may be expired.")
            print("Run: python3 scripts/linkedin-setup.py")
            sys.exit(1)

        if error_status == 403:
            print("Status: FAILURE")
            print("Error: Forbidden (403). Ensure w_member_social permission is granted.")
            print("Check your LinkedIn Developer App > Products > Share on LinkedIn")
            sys.exit(1)

        print("Status: FAILURE")
        print(f"Error: HTTP {error_status}: {json.dumps(resp, indent=2)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
