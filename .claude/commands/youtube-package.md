# /youtube-package — YouTube Content Optimization

Generate YouTube optimization content (titles, descriptions, chapters, thumbnail prompts) from a video or transcript.

## Input: $ARGUMENTS

Expects a video or transcript file path. If not provided:
- Look for video/transcript files in the current directory
- If multiple found, ask which one to process

## Pipeline

### Step 1: Get Transcript

- If video file → Spawn **Transcript Processor** first
- If transcript file → Read directly (prefer `.clean.txt` if available)

### Step 2: Get Audience Context

Check in order:
1. User provided audience in their message → use that
2. `.audience.txt` exists in project root → read and use
3. Default: "AI developers and creators learning Claude Code, AI coding tools, and AI-assisted development through the {{PROJECT_NAME}} community"

### Step 3: Generate YouTube Content

Spawn **YouTube Packager** agent:
- Read `.claude/agents/youtube-packager.md`
- Pass the cleaned transcript and audience context
- Wait for output: `.youtube.html` and `.youtube.md`

### Step 4: Build Journal

Append entry to `${BUILD_JOURNAL_PATH:-./build-journal}/YYYY-MM-DD.md` inline (see CLAUDE.md pipeline rule).

### Step 5: Report

```
## YouTube Package Created

### Files:
- HTML: [path to .youtube.html] (platform-agnostic — description, chapters, headlines)
- Markdown: [path to .youtube.md] (full version with thumbnail prompts)

### Headlines Generated: [count]
### Chapters: [count]
### Thumbnail Prompts: [count]

The HTML file is ready to paste into Skool.
The markdown file contains everything including thumbnail prompts.
```
