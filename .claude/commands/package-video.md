# /package-video — Video to Lesson Pipeline

Process a video file through the full pipeline: transcription > correction > lesson creation.

## Input: $ARGUMENTS

Expects a video file path. If not provided, look for video files in the current directory:
- `.mp4`, `.mov`, `.webm`, `.mkv`, `.m4v`, `.avi`
- If multiple found, ask which one to process

## Pipeline

This is a shortcut that chains Transcript Processor into the `/create-lesson` flow.

### Step 1: Transcribe

Spawn **Transcript Processor** agent:
- Read `.claude/agents/transcript-processor.md`
- Pass the video file path
- Wait for outputs: `.transcript.txt`, `.srt`, `.clean.txt`

### Step 2: Create Lesson

Feed the `.clean.txt` transcript into the `/create-lesson` pipeline:
- Start at Phase 1 (planning) with the transcript as input
- Follow all phases: planning > optional research > writing > presentation > quality gate > output

### Step 3: Build Journal

Append entry to `${BUILD_JOURNAL_PATH:-./build-journal}/YYYY-MM-DD.md` inline (see CLAUDE.md pipeline rule).

### Step 4: Report

```
## Video Packaged

### Transcription:
- Transcript: [path to .transcript.txt]
- Subtitles: [path to .srt]
- Clean transcript: [path to .clean.txt]
- Segments: [count]
- Language: [detected] ([confidence]%)

### Lesson:
- [lesson number] - [title]
- HTML: [path]
- Markdown: [path]
- Presentation: [path]
- QAS Status: Approved
```
