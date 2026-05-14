---
name: skool-publisher
version: 1.1.0
description: "Publish course content to Skool via Camofox browser automation. Handles cookie import, page creation, HTML injection into TipTap editor, and save."
---

# Skool Publisher

Publishes course lessons to Skool's classroom using Camofox (anti-detection Playwright browser).

## Prerequisites

1. **Camofox server running** at `http://localhost:9377`
   - Start with `BROWSER_IDLE_TIMEOUT_MS=3600000 node server.js` (1-hour idle timeout for long runs)
   - Requires `CAMOFOX_API_KEY` env var for cookie import
2. **Fresh Skool cookies** at `~/.camofox/cookies/skool.txt` (Netscape format)
   - Export from browser after logging into Skool
3. **Python 3.10+** with `requests` module

## Quick Start

```bash
# Dry run -- preview what will be published
python3 .claude/skills/skool-publisher/scripts/skool-publish.py \
  --course-url "https://www.skool.com/YOUR_COMMUNITY/classroom/YOUR_COURSE_ID" \
  --manifest context-engineering/skool-manifest.json \
  --dry-run

# Publish a single section first
python3 .claude/skills/skool-publisher/scripts/skool-publish.py \
  --course-url "https://www.skool.com/YOUR_COMMUNITY/classroom/YOUR_COURSE_ID" \
  --manifest context-engineering/skool-manifest.json \
  --section "Context Foundations" --delay 5

# Publish everything
python3 .claude/skills/skool-publisher/scripts/skool-publish.py \
  --course-url "https://www.skool.com/YOUR_COMMUNITY/classroom/YOUR_COURSE_ID" \
  --manifest context-engineering/skool-manifest.json

# Resume from a specific lesson
python3 .claude/skills/skool-publisher/scripts/skool-publish.py \
  --course-url "..." --manifest "..." --start-from 3.2.1
```

## Options

| Flag | Default | Description |
|------|---------|-------------|
| `--course-url` | (required) | Skool classroom module URL |
| `--manifest` | (required) | Path to skool-manifest.json |
| `--dry-run` | false | Preview without executing |
| `--section NAME` | all | Only publish lessons in this section |
| `--start-from N.N.N` | beginning | Resume from a specific lesson number |
| `--delay N` | 3 | Seconds between lessons |
| `--cookies FILE` | `~/.camofox/cookies/skool.txt` | Cookie file path |
| `--camofox URL` | `http://localhost:9377` | Camofox base URL |
| `--user-id ID` | `skool-publisher` | Camofox session user ID |

## How It Works

1. Starts Camofox browser session, imports Skool cookies
2. Opens the course URL in a Camofox tab
3. **Creates section folders** from the manifest's `sections[].name` values if they don't already exist (via dropdown > "Add folder")
4. For each lesson:
   - Clicks the course dropdown > "Add page"
   - Sets the title via `input[placeholder="Title"]`
   - Injects HTML body into the TipTap ProseMirror editor (`.tiptap.ProseMirror`)
   - Clicks SAVE and waits for confirmation
5. Tracks published lessons in `.skool-publish-state.json` for resume capability

**Note:** Folders are created automatically but pages are added flat. After publishing, manually drag pages into their section folders in the Skool UI. Skool's page-to-folder assignment uses drag-and-drop which is difficult to automate reliably.

## Camofox REST API Quick Reference

Base URL: `http://localhost:9377`

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/health` | GET | Server status |
| `/start` | POST | Start browser session `{userId}` |
| `/sessions/{userId}/cookies` | POST | Import cookies (needs `Authorization: Bearer <key>`) |
| `/tabs` | POST | Create tab `{userId, sessionKey, url}` |
| `/tabs/{tabId}/navigate` | POST | Navigate `{userId, url}` |
| `/tabs/{tabId}/snapshot` | GET | ARIA snapshot `?userId=...` |
| `/tabs/{tabId}/click` | POST | Click element `{userId, ref/selector}` |
| `/tabs/{tabId}/type` | POST | Type text `{userId, text, ref/selector}` |
| `/act` | POST | Advanced actions `{userId, targetId, kind, ...}` |

### /act kinds

- `click` -- `{ref, selector, doubleClick}`
- `type` -- `{ref, selector, text, pressEnter}`
- `press` -- `{ref, selector, key}`
- `scroll` -- `{ref, selector, direction}`
- `hover` -- `{ref, selector}`
- `wait` -- `{timeMs, text, loadState}`
- `evaluate` -- `{script}` -- Run arbitrary JS, returns result
- `close` -- Close the tab

## Skool Classroom Structure

- **Module**: Top-level course container (e.g., "3️⃣ Knowledge Infrastructure")
- **Folder**: Section grouping within a module (e.g., "Context Foundations")
- **Page**: Individual lesson within a module

Pages are flat at the module level. Folders group pages visually but pages exist as direct children of the module.

## Course Manifest Format

```json
{
  "course": "Context Engineering",
  "module": 3,
  "sections": [
    {
      "name": "Context Foundations",
      "lessons": [
        {
          "number": "3.1.1",
          "title": "From Prompt Engineering to Context Engineering",
          "emoji": "🧭",
          "file": "lessons/3.1.1-from-prompt-to-context.html"
        }
      ]
    }
  ]
}
```

File paths are relative to the manifest file's directory.

## Editor Details (TipTap/ProseMirror)

Skool uses a **TipTap (ProseMirror)** rich text editor.

- **Editor selector**: `.tiptap.ProseMirror.skool-editor2`
- **Title field**: `input[placeholder="Title"]` (use native value setter + input/change events)
- **HTML injection**: Set `innerHTML` on the editor element, then dispatch `input` + `change` events
- **Supported elements**: h1-h4, p, strong, em, s, code, pre, ul, ol, li, blockquote, a, img, hr
- **Images**: `<img>` tags are preserved during injection. Use absolute URLs for Skool-hosted images. Relative paths will appear broken until replaced with hosted URLs.
- **Page title format**: `{emoji} {number}: {title}` (e.g., "🧭 3.1.1: From Prompt Engineering to Context Engineering"). The `emoji` field in the manifest controls the prefix. If omitted, just `{number}: {title}` is used.
- **H1 stripping**: The first `<h1>Lesson X.Y.Z: ...</h1>` is automatically removed from the HTML body since the page title already displays this information.
- **Formatting**: The script auto-formats HTML for Skool readability:
  - Inserts a blank `<p></p>` between consecutive paragraphs (double-spacing)
  - Inserts a blank `<p></p>` before every `<hr>` (visual breathing room)
  - Deduplicates spacers to prevent excessive whitespace
- **Save button**: button with text "SAVE" (disabled until changes made)
- **Published toggle**: button with text "Published"

See `references/skool-editor-map.md` for the complete DOM selector reference.

## State Tracking

Published lessons are tracked in `<manifest-dir>/.skool-publish-state.json`:

```json
{
  "published": ["3.1.1", "3.1.2"],
  "failed": [{"number": "3.1.3", "error": "...", "step": "inject_html"}],
  "last_run": "2026-02-18T19:30:00Z"
}
```

Delete this file to republish everything. Use `--start-from` to skip to a specific lesson.

## Troubleshooting

- **"Tab not found"**: Session expired. Increase `BROWSER_IDLE_TIMEOUT_MS` or restart.
- **"Course dropdown button not found"**: Page didn't load or cookies are stale. Re-export cookies.
- **"TipTap editor not found"**: Edit mode didn't activate. Script auto-detects and clicks the pencil button.
- **SAVE stays disabled**: HTML injection may not have triggered change detection. Check evaluate result.
- **Rate limiting**: Increase `--delay` (default 3s between lessons).
- **DNS issues**: If Skool is unreachable, check VPN/network config.
