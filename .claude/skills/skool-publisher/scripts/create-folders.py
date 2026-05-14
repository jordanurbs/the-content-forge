#!/usr/bin/env python3
"""Create section folders on Skool for a course module via Camofox."""

import os
import sys
import time

try:
    import requests
except ImportError:
    print("ERROR: 'requests' module required.")
    sys.exit(1)

BASE = "http://localhost:9377"
USER_ID = "skool-publisher"
COURSE_URL = "https://www.skool.com/YOUR_COMMUNITY/classroom/YOUR_COURSE_ID"
COOKIE_PATH = os.path.expanduser("~/.camofox/cookies/skool.txt")
API_KEY = os.environ.get("CAMOFOX_API_KEY", "")

# Folders to create (only ones that don't already exist)
FOLDERS = [
    "Context Foundations",
    "Skills",
    "Autonomous Agent Architectures",
    "Ship It",
]

TAB_ID = None


def act(kind, **params):
    body = {"userId": USER_ID, "targetId": TAB_ID, "kind": kind}
    body.update(params)
    r = requests.post(f"{BASE}/act", json=body, headers={"Content-Type": "application/json"})
    r.raise_for_status()
    return r.json()


def evaluate(script):
    return act("evaluate", script=script)


def snapshot():
    r = requests.get(f"{BASE}/tabs/{TAB_ID}/snapshot?userId={USER_ID}")
    r.raise_for_status()
    return r.json().get("snapshot", "")


def create_folder(name):
    """Create a single folder: open dropdown > Add folder > type name > click Add."""
    print(f"\n  Creating folder: {name}")

    # 1. Click the course dropdown (three-dot menu)
    result = evaluate("""(() => {
        var btn = document.querySelector('[class*="CourseDropdownMenu"] [class*="DropdownButton"]');
        if (!btn) return {error: 'Dropdown not found'};
        btn.click();
        return {clicked: true};
    })()""")
    r = result.get("result", {})
    if r.get("error"):
        print(f"    ERROR: {r['error']}")
        return False
    print(f"    Dropdown opened")
    time.sleep(0.5)

    # 2. Click "Add folder"
    result = evaluate("""(() => {
        var items = document.querySelectorAll('[class*="DropdownContent"] [class*="DropdownItem"]');
        for (var i = 0; i < items.length; i++) {
            if (items[i].textContent.trim() === 'Add folder') {
                items[i].click();
                return {clicked: true};
            }
        }
        return {error: 'Add folder not found'};
    })()""")
    r = result.get("result", {})
    if r.get("error"):
        print(f"    ERROR: {r['error']}")
        return False
    print(f"    Add folder clicked")
    time.sleep(1)

    # 3. Type the folder name into the textbox using evaluate (native setter)
    safe_name = name.replace("'", "\\'").replace('"', '\\"')
    result = evaluate(f"""(() => {{
        // Find the folder name input - look for a visible text input near "Add folder"
        var inputs = document.querySelectorAll('input[type="text"], input:not([type])');
        var input = null;
        for (var i = 0; i < inputs.length; i++) {{
            // Check if visible and inside a modal/form area
            var rect = inputs[i].getBoundingClientRect();
            if (rect.width > 0 && rect.height > 0) {{
                input = inputs[i];
            }}
        }}
        if (!input) return {{error: 'No visible input found'}};
        var setter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
        setter.call(input, '{safe_name}');
        input.dispatchEvent(new Event('input', {{bubbles: true}}));
        input.dispatchEvent(new Event('change', {{bubbles: true}}));
        return {{success: true, value: input.value}};
    }})()""")
    r = result.get("result", {})
    if r.get("error"):
        print(f"    ERROR setting name: {r['error']}")
        return False
    print(f"    Name set: {r.get('value', '?')}")
    time.sleep(0.5)

    # 4. Click the "Add" button via evaluate
    result = evaluate("""(() => {
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
        print(f"    ERROR clicking Add: {r['error']}")
        return False
    print(f"    Add clicked")

    time.sleep(2)
    print(f"    CREATED: {name}")
    return True


def main():
    global TAB_ID

    # Health check
    h = requests.get(f"{BASE}/health").json()
    print(f"Camofox: browser={'connected' if h.get('browserConnected') else 'disconnected'}")

    # Import cookies
    cookies = []
    with open(COOKIE_PATH) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split("\t")
            if len(parts) < 7:
                continue
            domain, _flag, path, secure, _exp, name, value = parts[:7]
            if "skool" in domain:
                cookies.append({"name": name, "value": value, "domain": domain, "path": path, "secure": secure.upper() == "TRUE", "httpOnly": False})

    print(f"Importing {len(cookies)} cookies...")
    headers = {"Content-Type": "application/json"}
    if API_KEY:
        headers["Authorization"] = f"Bearer {API_KEY}"
    requests.post(f"{BASE}/sessions/{USER_ID}/cookies", json={"cookies": cookies}, headers=headers)

    # Open course
    print(f"Opening course...")
    r = requests.post(f"{BASE}/tabs", json={"userId": USER_ID, "sessionKey": "skool", "url": COURSE_URL}, headers={"Content-Type": "application/json"})
    r.raise_for_status()
    data = r.json()
    TAB_ID = data.get("targetId") or data.get("tabId")
    print(f"Tab: {TAB_ID}")
    time.sleep(3)

    snap = snapshot()
    print(f"Page loaded ({len(snap)} chars)")

    # Check which folders already exist
    existing = []
    for folder in ["Context Foundations", "Skills", "Agentic Harnesses", "Autonomous Agent Architectures", "Ship It", "Requirements Docs", "Context Engineering 101"]:
        if f'button "{folder}"' in snap or f'text: {folder}' in snap:
            existing.append(folder)

    print(f"\nExisting folders: {existing}")

    to_create = [f for f in FOLDERS if f not in existing]
    print(f"Folders to create: {to_create}")

    for folder_name in to_create:
        success = create_folder(folder_name)
        if not success:
            print(f"\n  FAILED to create '{folder_name}', stopping.")
            break

    print(f"\nDone!")


if __name__ == "__main__":
    main()
