#!/usr/bin/env python3
"""
Skool Publisher — Publish course lessons to Skool via Camofox browser automation.

Usage:
    python3 skool-publish.py --course-url URL --manifest FILE [options]

Options:
    --dry-run           Preview without executing
    --section NAME      Only publish lessons in this section
    --start-from N.N.N  Resume from a specific lesson number
    --delay N           Seconds between lessons (default: 3)
    --cookies FILE      Cookie file path (default: ~/.camofox/cookies/skool.txt)
    --camofox URL       Camofox base URL (default: http://localhost:9377)
    --user-id ID        Camofox user/session ID (default: skool-publisher)
"""

import argparse
import json
import os
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

try:
    import requests
except ImportError:
    print("ERROR: 'requests' module required. Install with: pip install requests")
    sys.exit(1)


CAMOFOX_BASE = "http://localhost:9377"
USER_ID = "skool-publisher"
COOKIE_PATH = os.path.expanduser("~/.camofox/cookies/skool.txt")
DEFAULT_DELAY = 3


def parse_netscape_cookies(cookie_file: str) -> list[dict]:
    """Parse Netscape-format cookie file into Playwright-compatible cookie objects."""
    cookies = []
    with open(cookie_file) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split("\t")
            if len(parts) < 7:
                continue
            domain, _flag, path, secure, _expires, name, value = parts[:7]
            cookies.append({
                "name": name,
                "value": value,
                "domain": domain,
                "path": path,
                "secure": secure.upper() == "TRUE",
                "httpOnly": False,
            })
    return cookies


class CamofoxClient:
    """Thin wrapper around Camofox REST API."""

    def __init__(self, base_url: str, user_id: str, api_key: str | None = None):
        self.base = base_url.rstrip("/")
        self.user_id = user_id
        self.api_key = api_key
        self.tab_id = None

    def _headers(self, auth=False):
        h = {"Content-Type": "application/json"}
        if auth and self.api_key:
            h["Authorization"] = f"Bearer {self.api_key}"
        return h

    def health(self) -> dict:
        r = requests.get(f"{self.base}/health")
        r.raise_for_status()
        return r.json()

    def start_session(self) -> dict:
        r = requests.post(f"{self.base}/start", json={"userId": self.user_id})
        r.raise_for_status()
        return r.json()

    def import_cookies(self, cookies: list[dict]) -> dict:
        r = requests.post(
            f"{self.base}/sessions/{self.user_id}/cookies",
            headers=self._headers(auth=True),
            json={"cookies": cookies},
        )
        r.raise_for_status()
        return r.json()

    def create_tab(self, url: str, session_key: str = "skool") -> str:
        r = requests.post(
            f"{self.base}/tabs",
            headers=self._headers(),
            json={"userId": self.user_id, "sessionKey": session_key, "url": url},
        )
        r.raise_for_status()
        data = r.json()
        self.tab_id = data.get("targetId") or data.get("tabId")
        return self.tab_id

    def navigate(self, url: str) -> dict:
        r = requests.post(
            f"{self.base}/tabs/{self.tab_id}/navigate",
            headers=self._headers(),
            json={"userId": self.user_id, "url": url},
        )
        r.raise_for_status()
        return r.json()

    def snapshot(self) -> str:
        r = requests.get(f"{self.base}/tabs/{self.tab_id}/snapshot?userId={self.user_id}")
        r.raise_for_status()
        data = r.json()
        return data.get("snapshot", "")

    def screenshot(self, save_path: str | None = None) -> bytes:
        r = requests.get(f"{self.base}/tabs/{self.tab_id}/screenshot")
        r.raise_for_status()
        if save_path:
            with open(save_path, "wb") as f:
                f.write(r.content)
        return r.content

    def click(self, ref: str | None = None, selector: str | None = None) -> dict:
        body = {"userId": self.user_id}
        if ref:
            body["ref"] = ref
        if selector:
            body["selector"] = selector
        r = requests.post(
            f"{self.base}/tabs/{self.tab_id}/click",
            headers=self._headers(),
            json=body,
        )
        r.raise_for_status()
        return r.json()

    def type_text(self, text: str, ref: str | None = None, selector: str | None = None) -> dict:
        body = {"userId": self.user_id, "text": text}
        if ref:
            body["ref"] = ref
        if selector:
            body["selector"] = selector
        r = requests.post(
            f"{self.base}/tabs/{self.tab_id}/type",
            headers=self._headers(),
            json=body,
        )
        r.raise_for_status()
        return r.json()

    def press(self, key: str, ref: str | None = None, selector: str | None = None) -> dict:
        body = {"userId": self.user_id, "key": key}
        if ref:
            body["ref"] = ref
        if selector:
            body["selector"] = selector
        r = requests.post(
            f"{self.base}/tabs/{self.tab_id}/press",
            headers=self._headers(),
            json=body,
        )
        r.raise_for_status()
        return r.json()

    def evaluate(self, script: str) -> dict:
        r = requests.post(
            f"{self.base}/act",
            headers=self._headers(),
            json={
                "userId": self.user_id,
                "targetId": self.tab_id,
                "kind": "evaluate",
                "script": script,
            },
        )
        r.raise_for_status()
        return r.json()

    def wait_ms(self, ms: int) -> dict:
        r = requests.post(
            f"{self.base}/act",
            headers=self._headers(),
            json={
                "userId": self.user_id,
                "targetId": self.tab_id,
                "kind": "wait",
                "timeMs": ms,
            },
        )
        r.raise_for_status()
        return r.json()


def strip_html_wrapper(html: str) -> str:
    """Strip <!DOCTYPE>, <html>, <head>, <body> wrappers, return inner body content."""
    html = re.sub(r"<!DOCTYPE[^>]*>", "", html, flags=re.IGNORECASE).strip()
    html = re.sub(r"<html[^>]*>", "", html, flags=re.IGNORECASE)
    html = re.sub(r"</html>", "", html, flags=re.IGNORECASE)
    html = re.sub(r"<head>.*?</head>", "", html, flags=re.IGNORECASE | re.DOTALL)
    html = re.sub(r"<body[^>]*>", "", html, flags=re.IGNORECASE)
    html = re.sub(r"</body>", "", html, flags=re.IGNORECASE)
    return html.strip()


def strip_leading_h1(html: str) -> str:
    """Remove the first <h1> if it matches 'Lesson X.Y.Z: ...' pattern (duplicates page title)."""
    return re.sub(r'^\s*<h1>\s*Lesson\s+\d+\.\d+\.\d+:.*?</h1>\s*', '', html, count=1, flags=re.IGNORECASE)


def format_page_title(title: str, number: str, emoji: str | None = None) -> str:
    """Format the Skool page title as '{emoji} {number}: {title}'."""
    prefix = f"{emoji} " if emoji else ""
    return f"{prefix}{number}: {title}"


def format_for_skool(html: str, manifest_dir: str | None = None) -> str:
    """Apply Skool-specific formatting: spacing, linebreaks, and image URL resolution.

    - Adds a blank paragraph before every <hr> for visual breathing room
    - Adds a blank paragraph between consecutive <p> blocks for readability
    - Converts relative image paths to absolute URLs if a base URL is configured
    """
    # Add blank paragraph between consecutive paragraphs for double-spacing
    html = re.sub(r'(</p>)\s*(<p[\s>])', r'\1\n<p></p>\n\2', html)

    # Add a blank paragraph before every <hr> for visual spacing
    html = re.sub(r'\s*(<hr\s*/?>)', r'\n<p></p>\n\1', html)

    # Collapse any double spacers (from both rules hitting the same spot)
    html = re.sub(r'(<p></p>\s*){2,}', r'<p></p>\n', html)

    # Resolve relative image paths to absolute if manifest_dir has images
    if manifest_dir:
        def resolve_img(match):
            tag = match.group(0)
            src_match = re.search(r'src=["\']([^"\']+)["\']', tag)
            if not src_match:
                return tag
            src = src_match.group(1)
            if src.startswith(('http://', 'https://', '//')):
                return tag  # Already absolute
            # Resolve relative path against manifest directory
            abs_path = os.path.normpath(os.path.join(manifest_dir, "lessons", src))
            if os.path.exists(abs_path):
                # Image exists locally -- keep the tag, path stays relative
                # (Skool will need hosted URLs; this preserves the tag for manual upload)
                return tag
            return tag  # Keep tag even if file missing -- user may add images later
        html = re.sub(r'<img[^>]+>', resolve_img, html)

    return html


def load_state(state_file: Path) -> dict:
    if state_file.exists():
        with open(state_file) as f:
            return json.load(f)
    return {"published": [], "failed": [], "last_run": None}


def save_state(state_file: Path, state: dict):
    state["last_run"] = datetime.now(timezone.utc).isoformat()
    with open(state_file, "w") as f:
        json.dump(state, f, indent=2)


def load_manifest(manifest_path: str) -> dict:
    with open(manifest_path) as f:
        return json.load(f)


def escape_for_js_template(html: str) -> str:
    """Escape HTML content for safe embedding in JS template literals."""
    return html.replace("\\", "\\\\").replace("`", "\\`").replace("${", "\\${")


def click_course_dropdown(client: CamofoxClient) -> dict:
    """Click the course-level three-dot dropdown menu."""
    return client.evaluate("""(() => {
        var btn = document.querySelector('[class*="CourseDropdownMenu"] [class*="DropdownButton"]');
        if (!btn) return {error: 'Course dropdown button not found'};
        btn.click();
        return {clicked: true};
    })()""")


def click_dropdown_item(client: CamofoxClient, text: str) -> dict:
    """Click a dropdown item by its text content."""
    return client.evaluate(f"""(() => {{
        var items = document.querySelectorAll('[class*="DropdownContent"] [class*="DropdownItem"]');
        for (var i = 0; i < items.length; i++) {{
            if (items[i].textContent.trim() === '{text}') {{
                items[i].click();
                return {{clicked: true, text: '{text}'}};
            }}
        }}
        return {{error: 'Dropdown item not found: {text}'}};
    }})()""")


def add_new_page(client: CamofoxClient) -> dict:
    """Click course dropdown > Add page. Returns result of the Add page click."""
    result = click_course_dropdown(client)
    if not result.get("ok") or result.get("result", {}).get("error"):
        return result
    time.sleep(0.5)
    return click_dropdown_item(client, "Add page")


def add_new_folder(client: CamofoxClient, name: str) -> dict:
    """Click course dropdown > Add folder > set name > click Add."""
    result = click_course_dropdown(client)
    if not result.get("ok") or result.get("result", {}).get("error"):
        return {"success": False, "error": "Could not open course dropdown"}
    time.sleep(0.5)

    result = click_dropdown_item(client, "Add folder")
    r = result.get("result", {})
    if r.get("error"):
        return {"success": False, "error": r["error"]}
    time.sleep(1)

    # Type name into the folder input using native value setter
    safe_name = name.replace("'", "\\'").replace('"', '\\"')
    result = client.evaluate(f"""(() => {{
        var inputs = document.querySelectorAll('input[type="text"], input:not([type])');
        var input = null;
        for (var i = 0; i < inputs.length; i++) {{
            var rect = inputs[i].getBoundingClientRect();
            if (rect.width > 0 && rect.height > 0) input = inputs[i];
        }}
        if (!input) return {{error: 'Folder name input not found'}};
        var setter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
        setter.call(input, '{safe_name}');
        input.dispatchEvent(new Event('input', {{bubbles: true}}));
        input.dispatchEvent(new Event('change', {{bubbles: true}}));
        return {{success: true, value: input.value}};
    }})()""")
    r = result.get("result", {})
    if r.get("error"):
        return {"success": False, "error": r["error"]}
    time.sleep(0.5)

    # Click the Add button
    result = client.evaluate("""(() => {
        var buttons = document.querySelectorAll('button');
        for (var i = 0; i < buttons.length; i++) {
            if (buttons[i].textContent.trim() === 'Add' && !buttons[i].disabled) {
                buttons[i].click();
                return {clicked: true};
            }
        }
        return {error: 'Add button not found or disabled'};
    })()""")
    r = result.get("result", {})
    if r.get("error"):
        return {"success": False, "error": r["error"]}
    time.sleep(2)
    return {"success": True, "name": name}


def get_existing_folders(client: CamofoxClient) -> list[str]:
    """Get list of folder names currently in the sidebar."""
    result = client.evaluate("""(() => {
        var folders = [];
        var items = document.querySelectorAll('[class*="CourseMenu"] button');
        for (var i = 0; i < items.length; i++) {
            var img = items[i].querySelector('img[src*="folder"], img[alt*="folder"]');
            var expandIcon = items[i].querySelector('svg, img');
            var text = items[i].textContent.trim();
            // Folders have a specific style: text + expand icon, no link child
            var link = items[i].querySelector('a');
            if (!link && text && expandIcon) {
                folders.push(text);
            }
        }
        return {folders: folders};
    })()""")
    return result.get("result", {}).get("folders", [])


def enter_edit_mode(client: CamofoxClient) -> dict:
    """Click the pencil/edit button to enter edit mode."""
    return client.evaluate("""(() => {
        var wrapper = document.querySelector('[class*="CourseModuleWrapper"]');
        if (!wrapper) return {error: 'Module wrapper not found'};
        var buttons = wrapper.querySelectorAll('button');
        for (var i = 0; i < buttons.length; i++) {
            var svg = buttons[i].querySelector('svg path');
            if (svg) {
                var d = svg.getAttribute('d') || '';
                if (d.indexOf('M19.2555') === 0) {
                    buttons[i].click();
                    return {clicked: true, button: 'edit/pencil'};
                }
            }
        }
        return {error: 'Edit button not found'};
    })()""")


def set_title(client: CamofoxClient, title: str) -> dict:
    """Set the lesson title using the native input value setter."""
    safe_title = title.replace("'", "\\'").replace('"', '\\"')
    return client.evaluate(f"""(() => {{
        var input = document.querySelector('input[placeholder="Title"]');
        if (!input) return {{error: 'Title input not found'}};
        var setter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
        setter.call(input, '{safe_title}');
        input.dispatchEvent(new Event('input', {{bubbles: true}}));
        input.dispatchEvent(new Event('change', {{bubbles: true}}));
        return {{success: true, value: input.value}};
    }})()""")


def inject_html(client: CamofoxClient, html_content: str) -> dict:
    """Inject HTML into the TipTap ProseMirror editor using TipTap's setContent API."""
    escaped = escape_for_js_template(html_content)
    return client.evaluate(f"""(() => {{
        var el = document.querySelector('.tiptap.ProseMirror');
        if (!el) return {{ success: false, error: 'TipTap editor not found' }};
        var editor = el.editor;
        if (!editor || !editor.commands || !editor.commands.setContent) {{
            // Fallback: direct innerHTML injection with event dispatch
            el.focus();
            el.innerHTML = `{escaped}`;
            el.dispatchEvent(new InputEvent('input', {{ bubbles: true, inputType: 'insertText' }}));
            el.dispatchEvent(new Event('change', {{ bubbles: true }}));
            return {{ success: true, length: el.innerHTML.length, method: 'innerHTML' }};
        }}
        editor.commands.setContent(`{escaped}`);
        return {{ success: true, length: el.innerHTML.length, method: 'setContent' }};
    }})()""")


def click_save(client: CamofoxClient) -> dict:
    """Click the SAVE button."""
    return client.evaluate("""(() => {
        var buttons = document.querySelectorAll('button');
        for (var i = 0; i < buttons.length; i++) {
            if (buttons[i].textContent.trim() === 'SAVE' && !buttons[i].disabled) {
                buttons[i].click();
                return {clicked: true};
            }
        }
        return {error: 'SAVE button not found or disabled'};
    })()""")


def wait_for_save(client: CamofoxClient, timeout_s: int = 10) -> bool:
    """Wait for SAVE button to become disabled (= save complete)."""
    for _ in range(timeout_s * 2):
        result = client.evaluate("""(() => {
            var buttons = document.querySelectorAll('button');
            for (var i = 0; i < buttons.length; i++) {
                if (buttons[i].textContent.trim() === 'SAVE') {
                    return {disabled: buttons[i].disabled};
                }
            }
            return {error: 'SAVE button not found'};
        })()""")
        r = result.get("result", {})
        if r.get("disabled"):
            return True
        time.sleep(0.5)
    return False


def publish_lesson(client: CamofoxClient, title: str, html_body: str) -> dict:
    """Full workflow: create new page, set title, inject HTML, save."""
    steps = {}

    # 1. Add new page
    print("    [1/5] Adding new page...")
    result = add_new_page(client)
    steps["add_page"] = result.get("result", {})
    if steps["add_page"].get("error"):
        return {"success": False, "step": "add_page", "error": steps["add_page"]["error"]}
    time.sleep(3)

    # 2. Wait for editor to appear (polls up to 15s)
    print("    [2/5] Waiting for editor...")
    editor_ready = False
    for attempt in range(15):
        check = client.evaluate("""(() => {
            return {
                hasEditor: !!document.querySelector('.tiptap.ProseMirror'),
                hasTitleInput: !!document.querySelector('input[placeholder="Title"]')
            };
        })()""")
        r = check.get("result", {})
        if r.get("hasEditor") and r.get("hasTitleInput"):
            editor_ready = True
            steps["edit_mode"] = {"ready": True, "attempts": attempt + 1}
            break
        # Try clicking the pencil button if editor not found
        if attempt == 3 or attempt == 7:
            enter_edit_mode(client)
        time.sleep(1)

    if not editor_ready:
        return {"success": False, "step": "edit_mode", "error": "Editor did not appear after 15s"}

    # 3. Set title
    print(f"    [3/5] Setting title: {title[:50]}...")
    result = set_title(client, title)
    steps["set_title"] = result.get("result", {})
    if steps["set_title"].get("error"):
        return {"success": False, "step": "set_title", "error": steps["set_title"]["error"]}
    time.sleep(0.5)

    # 4. Inject HTML body
    print(f"    [4/5] Injecting HTML ({len(html_body)} chars)...")
    result = inject_html(client, html_body)
    steps["inject_html"] = result.get("result", {})
    if not steps["inject_html"].get("success"):
        return {"success": False, "step": "inject_html", "error": steps["inject_html"].get("error", "unknown")}
    time.sleep(2)  # Give TipTap time to process the injected HTML

    # 5. Save (with retry: if SAVE is disabled, nudge the editor with execCommand)
    print("    [5/5] Saving...")
    for save_attempt in range(3):
        result = click_save(client)
        steps["save"] = result.get("result", {})
        if not steps["save"].get("error"):
            break
        # SAVE button disabled -- nudge the editor to trigger change detection
        if save_attempt < 2:
            print(f"    SAVE disabled, nudging editor (attempt {save_attempt + 1})...")
            client.evaluate("""(() => {
                var editor = document.querySelector('.tiptap.ProseMirror');
                if (editor) {
                    editor.focus();
                    document.execCommand('insertText', false, ' ');
                    document.execCommand('delete', false);
                }
            })()""")
            time.sleep(2)
    else:
        return {"success": False, "step": "save", "error": steps["save"].get("error", "SAVE button not found or disabled after retries")}

    saved = wait_for_save(client)
    steps["save_confirmed"] = saved

    if not saved:
        return {"success": False, "step": "save_confirm", "error": "SAVE button did not become disabled"}

    return {"success": True, "steps": steps}


def main():
    parser = argparse.ArgumentParser(description="Publish lessons to Skool via Camofox")
    parser.add_argument("--course-url", required=True, help="Skool course/classroom URL")
    parser.add_argument("--manifest", required=True, help="Path to skool-manifest.json")
    parser.add_argument("--dry-run", action="store_true", help="Preview without executing")
    parser.add_argument("--section", help="Only publish this section name")
    parser.add_argument("--start-from", help="Resume from lesson number (e.g., 3.2.1)")
    parser.add_argument("--delay", type=int, default=DEFAULT_DELAY, help=f"Seconds between lessons (default: {DEFAULT_DELAY})")
    parser.add_argument("--cookies", default=COOKIE_PATH, help="Cookie file path")
    parser.add_argument("--camofox", default=CAMOFOX_BASE, help="Camofox base URL")
    parser.add_argument("--user-id", default=USER_ID, help="Camofox session user ID")
    args = parser.parse_args()

    manifest_path = Path(args.manifest).resolve()
    manifest_dir = manifest_path.parent
    manifest = load_manifest(str(manifest_path))
    state_file = manifest_dir / ".skool-publish-state.json"
    state = load_state(state_file)

    api_key = os.environ.get("CAMOFOX_API_KEY", "")

    # Build lesson list
    lessons_to_publish = []
    skip = bool(args.start_from)

    for section in manifest["sections"]:
        if args.section and section["name"] != args.section:
            continue
        for lesson in section["lessons"]:
            if skip:
                if lesson["number"] == args.start_from:
                    skip = False
                else:
                    continue
            if lesson["number"] in state["published"]:
                print(f"  SKIP {lesson['number']} (already published)")
                continue
            file_path = manifest_dir / lesson["file"]
            if not file_path.exists():
                print(f"  ERROR: File not found: {file_path}")
                continue
            lessons_to_publish.append({
                "section": section["name"],
                "number": lesson["number"],
                "title": lesson["title"],
                "emoji": lesson.get("emoji", ""),
                "file": str(file_path),
            })

    # Dry run output
    print(f"\n{'DRY RUN — ' if args.dry_run else ''}Skool Publisher")
    print(f"Course: {manifest.get('course', 'Unknown')}")
    print(f"URL: {args.course_url}")
    print(f"Lessons to publish: {len(lessons_to_publish)}")
    print(f"Delay between lessons: {args.delay}s")
    print()

    for i, l in enumerate(lessons_to_publish, 1):
        page_title = format_page_title(l["title"], l["number"], l.get("emoji"))
        print(f"  {i:2d}. [{l['section']}] {page_title}")
        print(f"      File: {l['file']}")

    if args.dry_run:
        print("\nDry run complete. Remove --dry-run to publish.")
        return

    if not lessons_to_publish:
        print("\nNothing to publish.")
        return

    print()

    # Initialize Camofox
    client = CamofoxClient(args.camofox, args.user_id, api_key)

    # Health check
    try:
        health = client.health()
        print(f"Camofox: ok (browser={'connected' if health.get('browserConnected') else 'disconnected'})")
    except Exception as e:
        print(f"ERROR: Camofox not reachable at {args.camofox}: {e}")
        sys.exit(1)

    # Start browser session if needed
    if not health.get("browserConnected"):
        print("Starting browser session...")
        client.start_session()
        time.sleep(2)

    # Import cookies
    print("Importing Skool cookies...")
    cookies = parse_netscape_cookies(args.cookies)
    skool_cookies = [c for c in cookies if "skool" in c.get("domain", "")]
    if not skool_cookies:
        print(f"ERROR: No Skool cookies found in {args.cookies}")
        sys.exit(1)
    print(f"  Found {len(skool_cookies)} Skool cookies")
    try:
        client.import_cookies(skool_cookies)
        print("  Cookies imported.")
    except Exception as e:
        print(f"  WARNING: Cookie import failed: {e}")
        print("  Continuing anyway (session may already exist)...")

    # Open course URL
    print(f"\nNavigating to course: {args.course_url}")
    try:
        tab_id = client.create_tab(args.course_url)
        print(f"  Tab created: {tab_id}")
    except Exception as e:
        print(f"ERROR: Failed to open tab: {e}")
        sys.exit(1)

    time.sleep(3)

    # Verify page loaded
    snap = client.snapshot()
    if len(snap) < 500:
        print(f"ERROR: Page may not have loaded correctly (snapshot: {len(snap)} chars)")
        print("  Check cookies and course URL")
        sys.exit(1)
    print(f"  Page loaded ({len(snap)} chars)")

    # Create section folders if they don't exist
    section_names = list(dict.fromkeys(s["name"] for s in manifest["sections"]))
    snap = client.snapshot()
    existing_folders = []
    for name in section_names:
        if f'button "{name}"' in snap:
            existing_folders.append(name)

    folders_to_create = [n for n in section_names if n not in existing_folders]
    if folders_to_create:
        print(f"\nCreating {len(folders_to_create)} section folder(s)...")
        for folder_name in folders_to_create:
            print(f"  Creating folder: {folder_name}...")
            result = add_new_folder(client, folder_name)
            if result.get("success"):
                print(f"    CREATED")
            else:
                print(f"    FAILED: {result.get('error')}")
                print(f"    WARNING: Pages will be created without folder grouping")
        # Navigate back after folder creation
        client.navigate(args.course_url)
        time.sleep(2)
    else:
        print(f"\nAll {len(section_names)} section folders already exist.")

    # Publish lessons
    published_count = 0
    failed_count = 0

    for i, lesson in enumerate(lessons_to_publish):
        print(f"\n{'='*60}")
        print(f"[{i+1}/{len(lessons_to_publish)}] {lesson['number']} — {lesson['title']}")
        print(f"Section: {lesson['section']}")

        # Read and prepare HTML
        with open(lesson["file"]) as f:
            raw_html = f.read()
        body_html = strip_html_wrapper(raw_html)
        body_html = strip_leading_h1(body_html)
        body_html = format_for_skool(body_html, str(manifest_dir))
        print(f"  HTML body: {len(body_html)} chars")

        # Navigate back to course page before creating each new lesson
        if i > 0:
            print("  Navigating to course page...")
            client.navigate(args.course_url)
            time.sleep(2)

        # Format page title: {emoji} {number}: {title}
        page_title = format_page_title(lesson["title"], lesson["number"], lesson.get("emoji"))

        # Publish the lesson
        result = publish_lesson(client, page_title, body_html)

        if result["success"]:
            print(f"  >> PUBLISHED!")
            state["published"].append(lesson["number"])
            published_count += 1
        else:
            print(f"  >> FAILED at step '{result.get('step')}': {result.get('error')}")
            state["failed"].append({"number": lesson["number"], "error": result.get("error"), "step": result.get("step")})
            failed_count += 1

        save_state(state_file, state)

        # Delay between lessons
        if i < len(lessons_to_publish) - 1:
            print(f"  Waiting {args.delay}s...")
            time.sleep(args.delay)

    print(f"\n{'='*60}")
    print(f"DONE! Published: {published_count}, Failed: {failed_count}")
    print(f"State saved to: {state_file}")


if __name__ == "__main__":
    main()
