# /quick-lesson — Lightweight Transcript-to-Lesson Pipeline

Fast-track a transcript or text into a lesson. No images, no presentation, no QAS gate.

## Input: $ARGUMENTS

Accepts one of:
- **A transcript/text** pasted directly as arguments
- **A file path** to a `.txt`, `.clean.txt`, or `.md` file
- **A video file path** (`.mp4`, `.mov`, `.webm`, `.mkv`, `.m4v`, `.avi`) — will transcribe first

If a video file is provided, spawn Transcript Processor first. Otherwise skip straight to lesson writing.

## Pipeline

### Step 1: Corrections (if raw transcript)

If input is raw text or a transcript file (not already `.clean.txt`):
- Read `.corrections.json` from project root
- Apply case-insensitive replacements (longer patterns first)
- Save as `<output-dir>/transcript.clean.txt`

If input is already `.clean.txt`, skip this step.

### Step 2: Plan

Create a brief lesson plan:
- Identify key teaching points from the transcript
- Propose a title and slug
- Determine output directory
- Ask user to confirm lesson title, slug, and output location
- Save to `<output-dir>/plan.md`

### Step 3: Write Lesson

Spawn **Lesson Writer** agent (via Task tool):
- Read `.claude/agents/lesson-writer.md` for agent instructions
- Pass: plan path, clean transcript path, voice standard path, lesson template path
- Agent writes HTML + MD directly to `<output-dir>/lessons/`
- **Skip image references** — no hero image in HTML

### Step 4: Build Journal

Append entry to `${BUILD_JOURNAL_PATH:-./build-journal}/YYYY-MM-DD.md` inline (see CLAUDE.md pipeline rule).

### Step 5: Report

```
## Quick Lesson Created

- Title: [title]
- HTML: [path]
- Markdown: [path]
- Time: [duration]
```

## What's Different from /create-lesson

| Feature | /create-lesson | /quick-lesson |
|---------|---------------|---------------|
| Hero image | Yes | No |
| Slidev presentation | Yes | No |
| QAS quality gate | Yes | No |
| Research phase | Optional | No |
| Voice standard | Full | Full |
| Lesson template structure | Full | Full (minus images) |
| Speed | 15-30 min | 5-10 min |

## Notes

- Voice standard still applies — lessons must sound like the configured voice
- All required sections still present (What You'll Get, What You'll Do, etc.)
- Hero image placeholder can be added later if needed
- Lesson can be upgraded to full pipeline later by running `/create-lesson` on the output
