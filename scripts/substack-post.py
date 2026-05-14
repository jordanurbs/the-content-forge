#!/usr/bin/env python3
"""Create a Substack draft post from a Markdown file."""

import argparse
import json
import os
import re
import sys
import tempfile


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


def md_to_prosemirror(md_text):
    """Convert Markdown to Substack's ProseMirror JSON format."""
    doc = {"type": "doc", "content": []}
    lines = md_text.split("\n")
    i = 0

    while i < len(lines):
        line = lines[i]

        # Skip empty lines
        if not line.strip():
            i += 1
            continue

        # Headings
        heading_match = re.match(r"^(#{1,6})\s+(.*)", line)
        if heading_match:
            level = len(heading_match.group(1))
            text = heading_match.group(2).strip()
            node = {"type": "heading", "attrs": {"level": level}, "content": parse_inline(text)}
            doc["content"].append(node)
            i += 1
            continue

        # Blockquote
        if line.startswith("> "):
            quote_lines = []
            while i < len(lines) and lines[i].startswith("> "):
                quote_lines.append(lines[i][2:])
                i += 1
            text = " ".join(quote_lines)
            node = {"type": "blockquote", "content": [{"type": "paragraph", "content": parse_inline(text)}]}
            doc["content"].append(node)
            continue

        # Unordered list
        if re.match(r"^[-*]\s+", line):
            items = []
            while i < len(lines) and re.match(r"^[-*]\s+", lines[i]):
                item_text = re.sub(r"^[-*]\s+", "", lines[i])
                items.append({"type": "list_item", "content": [{"type": "paragraph", "content": parse_inline(item_text)}]})
                i += 1
            doc["content"].append({"type": "bullet_list", "content": items})
            continue

        # Ordered list
        if re.match(r"^\d+\.\s+", line):
            items = []
            while i < len(lines) and re.match(r"^\d+\.\s+", lines[i]):
                item_text = re.sub(r"^\d+\.\s+", "", lines[i])
                items.append({"type": "list_item", "content": [{"type": "paragraph", "content": parse_inline(item_text)}]})
                i += 1
            doc["content"].append({"type": "ordered_list", "attrs": {"start": 1}, "content": items})
            continue

        # Horizontal rule
        if re.match(r"^(-{3,}|\*{3,}|_{3,})\s*$", line):
            doc["content"].append({"type": "horizontal_rule"})
            i += 1
            continue

        # Regular paragraph (collect consecutive non-empty, non-special lines)
        para_lines = []
        while i < len(lines) and lines[i].strip() and not re.match(r"^(#{1,6}\s|>\s|[-*]\s|\d+\.\s|(-{3,}|\*{3,}|_{3,})\s*$)", lines[i]):
            para_lines.append(lines[i])
            i += 1
        text = " ".join(para_lines)
        if text.strip():
            doc["content"].append({"type": "paragraph", "content": parse_inline(text)})

    return doc


def parse_inline(text):
    """Parse inline Markdown (bold, italic, links, code) into ProseMirror nodes."""
    nodes = []
    # Pattern handles: **bold**, *italic*, [link](url), `code`
    pattern = re.compile(
        r"(\*\*(.+?)\*\*)"       # bold
        r"|(\*(.+?)\*)"          # italic
        r"|(\[(.+?)\]\((.+?)\))" # link
        r"|(`(.+?)`)"            # inline code
    )

    last_end = 0
    for m in pattern.finditer(text):
        # Add plain text before this match
        if m.start() > last_end:
            plain = text[last_end:m.start()]
            if plain:
                nodes.append({"type": "text", "text": plain})

        if m.group(2):  # bold
            nodes.append({"type": "text", "marks": [{"type": "strong"}], "text": m.group(2)})
        elif m.group(4):  # italic
            nodes.append({"type": "text", "marks": [{"type": "em"}], "text": m.group(4)})
        elif m.group(6):  # link
            nodes.append({"type": "text", "marks": [{"type": "link", "attrs": {"href": m.group(7), "title": None}}], "text": m.group(6)})
        elif m.group(9):  # code
            nodes.append({"type": "text", "marks": [{"type": "code"}], "text": m.group(9)})

        last_end = m.end()

    # Remaining plain text
    if last_end < len(text):
        remaining = text[last_end:]
        if remaining:
            nodes.append({"type": "text", "text": remaining})

    if not nodes:
        nodes.append({"type": "text", "text": text or " "})

    return nodes


def main():
    parser = argparse.ArgumentParser(description="Create a Substack draft from Markdown")
    parser.add_argument("--md-file", required=True, help="Path to Markdown file")
    parser.add_argument("--title", required=True, help="Post title")
    parser.add_argument("--subtitle", help="Post subtitle")
    parser.add_argument("--hero-image", help="Path to hero image file")
    parser.add_argument("--image-prompt", help="Generate hero image via Venice AI with this prompt")
    parser.add_argument("--env-file", default=".env", help="Path to .env file (default: .env)")

    args = parser.parse_args()

    # Load env
    env = load_env(args.env_file)
    os.environ.update({k: v for k, v in env.items() if k not in os.environ})

    email = os.environ.get("SUBSTACK_EMAIL")
    password = os.environ.get("SUBSTACK_PASSWORD")
    pub_url = os.environ.get("SUBSTACK_PUBLICATION_URL")
    cookies_path = os.environ.get("SUBSTACK_COOKIES_PATH")

    # Auth: cookies OR email+password. Publication URL always required.
    has_cookies = bool(cookies_path)
    has_credentials = bool(email) and bool(password)

    if not pub_url:
        print("Status: SKIPPED")
        print("Reason: Missing SUBSTACK_PUBLICATION_URL")
        sys.exit(0)

    if not has_cookies and not has_credentials:
        print("Status: SKIPPED")
        print("Reason: Missing SUBSTACK_COOKIES_PATH or SUBSTACK_EMAIL+SUBSTACK_PASSWORD")
        sys.exit(0)

    if has_cookies and not os.path.exists(cookies_path):
        print("Status: FAILURE")
        print(f"Error: Cookies file not found: {cookies_path}")
        sys.exit(1)

    # Convert Netscape cookies.txt to JSON if needed (python-substack expects JSON)
    if has_cookies:
        with open(cookies_path) as f:
            first_line = f.readline()
        if first_line.startswith("# Netscape") or first_line.startswith("# HTTP"):
            cookie_dict = {}
            with open(cookies_path) as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue
                    parts = line.split("\t")
                    if len(parts) >= 7 and ".substack.com" in parts[0]:
                        cookie_dict[parts[5]] = parts[6]
            tmp = tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False)
            json.dump(cookie_dict, tmp)
            tmp.close()
            cookies_path = tmp.name

    if not os.path.exists(args.md_file):
        print("Status: FAILURE")
        print(f"Error: Markdown file not found: {args.md_file}")
        sys.exit(1)

    try:
        from substack import Api
    except ImportError:
        print("Status: FAILURE")
        print("Error: python-substack not installed. Run: pip3 install python-substack")
        sys.exit(1)

    try:
        if has_cookies:
            api = Api(cookies_path=cookies_path, publication_url=pub_url)
        else:
            api = Api(email=email, password=password, publication_url=pub_url)
    except Exception as e:
        print("Status: FAILURE")
        print(f"Error: Substack login failed: {e}")
        sys.exit(1)

    with open(args.md_file) as f:
        md_content = f.read()

    # Convert markdown to ProseMirror JSON body
    body_json = md_to_prosemirror(md_content)

    try:
        user_id = api.get_user_id()
        draft_body = {
            "draft_title": args.title,
            "draft_subtitle": args.subtitle or "",
            "draft_body": json.dumps(body_json),
            "draft_bylines": [{"id": user_id, "is_guest": False}],
            "type": "newsletter",
            "audience": "everyone",
        }
        draft = api.post_draft(draft_body)
    except Exception as e:
        print("Status: FAILURE")
        print(f"Error: Failed to create draft: {e}")
        sys.exit(1)

    # Generate hero image via Venice AI if --image-prompt provided
    if args.image_prompt and not args.hero_image:
        venice_script = os.path.expanduser("~/.claude/skills/venice-ai-media/scripts/venice-image.py")
        if os.path.exists(venice_script):
            import subprocess
            out_dir = tempfile.mkdtemp(prefix="substack-hero-")
            cmd = [
                "python3", venice_script,
                "--prompt", args.image_prompt,
                "--width", "1280", "--height", "720",
                "--format", "png",
                "--style-preset", "Photographic",
                "--out-dir", out_dir,
            ]
            print(f"Generating hero image via Venice AI...")
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                import glob as globmod
                pngs = globmod.glob(os.path.join(out_dir, "*.png"))
                if pngs:
                    args.hero_image = pngs[0]
                    print(f"Hero image generated: {args.hero_image}")
                else:
                    print("Warning: Venice AI returned success but no PNG found")
            else:
                print(f"Warning: Venice AI image generation failed: {result.stderr.strip()}")
        else:
            print("Warning: Venice AI script not found, skipping image generation")

    # Best-effort hero image upload
    if args.hero_image and os.path.exists(args.hero_image):
        try:
            import base64
            ext = os.path.splitext(args.hero_image)[1].lower()
            mime = {"png": "image/png", "jpg": "image/jpeg", "jpeg": "image/jpeg", "webp": "image/webp", "gif": "image/gif"}.get(ext.lstrip("."), "image/png")
            with open(args.hero_image, "rb") as f:
                image_data = f"data:{mime};base64,".encode() + base64.b64encode(f.read())
            resp = api._session.post(f"{api.publication_url}/image", data={"image": image_data})
            if resp.status_code == 200:
                image_url = resp.json().get("url")
                if image_url:
                    api.put_draft(draft["id"], cover_image=image_url)
            else:
                print(f"Warning: Hero image upload failed: HTTP {resp.status_code}")
        except Exception as e:
            print(f"Warning: Hero image upload failed: {e}")

    draft_id = draft.get("id", "unknown")
    # Construct draft URL from publication URL
    pub_base = pub_url.rstrip("/")
    draft_url = f"{pub_base}/publish/post/{draft_id}" if draft_id != "unknown" else "unknown"

    print("Status: SUCCESS")
    print(f"Draft ID: {draft_id}")
    print(f"Draft URL: {draft_url}")


if __name__ == "__main__":
    main()
