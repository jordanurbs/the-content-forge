# /repurpose-lesson — Post-Production Pipeline

Repurpose a recorded lesson into a YouTube-ready video package: intro/outro cards, animated B-roll, post-production script, and YouTube metadata — all derived from the existing lesson structure.

## Input: $ARGUMENTS

If no arguments provided, ask the user for:
1. Path to the video file or transcript
2. Path to the lesson directory (containing the lesson `.html` file)

## Context Rules (MANDATORY)

Follow the Context Engineering rules in CLAUDE.md:
- Do NOT read agent or skill files yourself
- Pass file PATHS to agents, not contents
- Agents write to disk directly
- You track status and file paths only

## Pipeline

### Phase 1: Input & Planning (MANDATORY)

1. **Identify inputs:**
   - Video file (.mp4, .mov, etc.) OR transcript (.txt, .clean.txt)
   - Lesson directory path (must contain a lesson `.html` file)

2. **Validate lesson directory:**
   - Find the lesson `.html` file (glob for `lessons/*.html`)
   - Extract from it: lesson title (first `<h2>`), M.S.L number (from filename pattern), `<h2>` section headings, "What's Next" content (next lesson title + number)
   - Confirm hero image exists in `assets/`
   - Note the presentations directory if it exists

3. **Create output directory:**
   ```
   <lesson-dir>/youtube/
   <lesson-dir>/youtube/cards/
   <lesson-dir>/youtube/storyboard/
   <lesson-dir>/youtube/storyboard/ref/
   <lesson-dir>/youtube/broll/slides/
   <lesson-dir>/youtube/broll/hero/
   <lesson-dir>/youtube/broll/storyboard/
   ```

4. **Present plan to user:**
   ```
   ## Repurpose Plan: [Lesson Title]

   - Lesson: [M.S.L] [Title]
   - Source: [video file or transcript path]
   - Lesson HTML: [path]
   - Next lesson: [M.S.L] [Title] (from "What's Next")
   - Hero image: [path]
   - Presentations: [path or "none"]
   - Output: <lesson-dir>/youtube/

   ## What will be generated:
   1. Post-production script (intro hook, outro/CTA, B-roll timing)
   2. Storyboard images (Venice AI)
   3. Animated B-roll clips (Remotion)
   4. Intro + outro branded cards (Remotion)
   5. YouTube metadata (title, description, chapters, thumbnails)
   ```
   **Wait for user approval before proceeding.**

5. **Save plan:**
   Write the plan to `<lesson-dir>/youtube/plan.md`

### Phase 2: Transcription (if video input)

Only if input is a video file (not a transcript). Spawn Transcript Processor:
```
Task tool:
  description: "Transcribe lesson recording"
  subagent_type: "general-purpose"
  max_turns: 10
  prompt: |
    You are the Transcript Processor for {{PROJECT_NAME}}.
    Read your instructions at: .claude/agents/transcript-processor.md

    ## Task
    Transcribe and correct: <video-file-path>

    ## Output
    Return: status, path to .clean.txt file
```

### Phase 3: Post-Production Script

Spawn Script Writer in **POST-PRODUCTION MODE**:
```
Task tool:
  description: "Write post-production script"
  subagent_type: "general-purpose"
  max_turns: 25
  prompt: |
    You are the Script Writer for {{PROJECT_NAME}}.
    Read your instructions at: .claude/agents/script-writer.md

    ## MODE: POST-PRODUCTION
    This is NOT a pre-production script. The video is already recorded.
    You are writing supplementary content to wrap around existing footage:

    1. **Intro Hook** (15-30s):
       - Compelling reason to watch — what will the viewer learn/gain?
       - Reference a specific moment or outcome from the lesson
       - Must create a reason to keep watching within the first 8 seconds
       - Format: talking points (this WILL be recorded as a new clip)

    2. **Outro/CTA** (30-45s):
       - Natural closing that references what was covered
       - Single CTA (subscribe, next lesson, or community)
       - Tease the next lesson: [NEXT_LESSON_TITLE] ([NEXT_LESSON_NUMBER])
       - Format: talking points (this WILL be recorded as a new clip)

    3. **B-Roll Timing Plan** (table):
       For each B-roll moment in the recording:
       | Timestamp | Duration | Type | Description |
       |-----------|----------|------|-------------|
       | MM:SS | 2-5s | slide/screenshot/generated | What to show |

       Types:
       - "slide" — export a Slidev slide as PNG, animate it
       - "screenshot" — screen capture from the recording, animate it
       - "generated" — Venice AI generated image (goes to storyboard)
       - "hero" — the lesson's hero image, animated

    ## Input Files (read these yourself)
    - Transcript: <transcript-path>
    - Lesson HTML: <lesson-html-path>
    - Plan: <lesson-dir>/youtube/plan.md

    ## Output Files (write these yourself)
    - <lesson-dir>/youtube/post-production.md

    ## Return Format
    Return ONLY: status, file path, intro duration, outro duration, B-roll count.
```

Then spawn Script Editor on the post-production script:
```
Task tool:
  description: "Optimize post-production script"
  subagent_type: "general-purpose"
  max_turns: 20
  prompt: |
    You are the Script Editor for {{PROJECT_NAME}}.
    Read your instructions at: .claude/agents/script-editor.md

    ## MODE: POST-PRODUCTION
    You are editing a post-production script — intro hook and outro/CTA only.
    The main video content is already recorded and cannot be changed.

    Focus on:
    - Intro: Does it create a reason to watch in 8 seconds? Is the hook specific?
    - Outro: Is the CTA singular and natural? Does the next-lesson tease work?
    - B-roll timing: Are timestamps realistic? Are descriptions specific enough to generate?

    Do NOT add engagement markers to the B-roll timing table — those are for the recorded content.
    Only optimize the intro and outro talking points.

    ## Input Files (read these yourself)
    - Post-production script: <lesson-dir>/youtube/post-production.md
    - Plan: <lesson-dir>/youtube/plan.md

    ## Output Files (write these yourself)
    - <lesson-dir>/youtube/post-production.md (edit in place)
    - <lesson-dir>/youtube/script-editor-notes.md

    ## Return Format
    Return ONLY: status, files, summary of changes.
```

### Phase 4: QAS Gate #1 (MANDATORY)

Spawn Quality Reviewer with POST-PRODUCTION checklist:
```
Task tool:
  description: "QAS review post-production script"
  subagent_type: "general-purpose"
  model: opus
  max_turns: 15
  prompt: |
    You are the Quality Reviewer (QAS) for {{PROJECT_NAME}}.
    Read your instructions at: .claude/agents/quality-reviewer.md

    ## Task
    Review the post-production script.

    ## Files to Review
    - Post-production script: <lesson-dir>/youtube/post-production.md
    - Editor notes: <lesson-dir>/youtube/script-editor-notes.md
    - Plan: <lesson-dir>/youtube/plan.md

    ## POST-PRODUCTION CHECKLIST (use this instead of the lesson/video checklist)

    ### Intro Hook
    - [ ] 15-30 seconds duration
    - [ ] Creates reason to watch within 8 seconds
    - [ ] References specific examples from the lesson content
    - [ ] Talking-points format (not teleprompter script)
    - [ ] "Builders" tone

    ### Outro/CTA
    - [ ] 30-45 seconds duration
    - [ ] Single CTA (not multiple competing asks)
    - [ ] Next lesson tease includes title and number
    - [ ] Natural close — doesn't feel forced

    ### B-Roll Timing Plan
    - [ ] Timestamps from real transcript (not made up)
    - [ ] Each B-roll moment has specific visual description
    - [ ] Duration per clip: 2-5 seconds
    - [ ] Type column correctly categorizes each (slide/screenshot/generated/hero)
    - [ ] Mix of types (not all one type)

    ### Voice
    - [ ] Sounds like the configured voice — conversational, specific, honest
    - [ ] Ad-lib zones in intro and outro
    - [ ] No corporate speak

    ## Return Format
    Return: APPROVED or BLOCKED with specific issues referencing the checklist.
```

- **If APPROVED:** proceed to Phase 5
- **If BLOCKED:** re-spawn Script Writer + Script Editor with issue list. Max 2 revision cycles before escalating to user.

### Phase 5: Asset Generation

Run these in parallel where possible:

**5A: Storyboard images** — Spawn Storyboarder for B-roll moments marked as "generated":
```
Task tool:
  description: "Generate storyboard images"
  subagent_type: "general-purpose"
  max_turns: 20
  prompt: |
    You are the Storyboarder for {{PROJECT_NAME}}.
    Read your instructions at: .claude/agents/storyboarder.md

    ## Task
    Generate storyboard images for the B-roll moments marked "generated" in the post-production script.

    ## Input Files (read these yourself)
    - Post-production script: <lesson-dir>/youtube/post-production.md
    - Plan: <lesson-dir>/youtube/plan.md (check visual_style field — default: brand-default)

    ## Output Files (write these yourself)
    - <lesson-dir>/youtube/storyboard/storyboard.md
    - <lesson-dir>/youtube/storyboard/*.png

    ## Output Directory
    Images go in: <lesson-dir>/youtube/storyboard/

    ## Return Format
    Return ONLY: status, file list, image count, visual style used.
```

**5B: Export Slidev slides** (orchestrator does this directly):
If the lesson has a presentations directory with slides:
1. Check if Slidev slides exist at `<lesson-dir>/presentations/slides/`
2. For each B-roll moment marked "slide" in post-production.md, note which slide number to export
3. Run: `cd <lesson-dir>/presentations && npx slidev export --format png --output <lesson-dir>/youtube/storyboard/ref/`
4. If slidev export fails or presentations don't exist, skip gracefully — these become screenshots the user must capture manually

**5C: Copy hero image:**
Copy the hero image from `<lesson-dir>/assets/` to `<lesson-dir>/youtube/storyboard/ref/hero.png`

### Phase 5.5: Asset Animation (Sequential — CPU intensive)

After Phase 5 completes, animate the assets using the broll-animator:

1. **Animate storyboard images** (the "generated" ones):
   ```bash
   cd tools/broll-animator && bash render.sh <lesson-dir>/youtube/storyboard/
   ```
   Move the `animated/` output to `<lesson-dir>/youtube/broll/storyboard/`

2. **Animate reference images** (slides + hero):
   ```bash
   cd tools/broll-animator && bash render.sh <lesson-dir>/youtube/storyboard/ref/
   ```
   - Move slide MP4s to `<lesson-dir>/youtube/broll/slides/`
   - Move hero MP4 to `<lesson-dir>/youtube/broll/hero/`

3. **Render intro + outro cards:**
   Extract lesson title, module number, next lesson info from the plan.
   ```bash
   cd tools/broll-animator && bash render-cards.sh \
     --intro '{"lessonTitle":"<TITLE>","moduleNumber":"<M.S.L>"}' \
     --outro '{"nextLessonTitle":"<NEXT_TITLE>","nextLessonNumber":"<NEXT_M.S.L>"}' \
     --output-dir <lesson-dir>/youtube/cards/
   ```

### Phase 6: YouTube Packaging

Spawn YouTube Packager with BOTH transcript and lesson HTML:
```
Task tool:
  description: "Generate YouTube metadata"
  subagent_type: "general-purpose"
  max_turns: 15
  prompt: |
    You are the YouTube Packager for {{PROJECT_NAME}}.
    Read your instructions at: .claude/agents/youtube-packager.md

    ## Task
    Generate YouTube optimization content for this lesson recording.

    ## Input Files (read these yourself)
    - Transcript: <transcript-path>
    - Lesson HTML: <lesson-html-path> (USE THIS for chapter alignment — see your agent instructions)
    - Audience: .audience.txt (if it exists, otherwise use default)

    ## Output Files (write these yourself)
    - <lesson-dir>/youtube/youtube.html
    - <lesson-dir>/youtube/youtube.md

    ## Return Format
    Return ONLY: status, file paths, best headline.
```

### Phase 7: QAS Gate #2 (MANDATORY)

Spawn Quality Reviewer for final package review:
```
Task tool:
  description: "QAS review final package"
  subagent_type: "general-purpose"
  model: opus
  max_turns: 15
  prompt: |
    You are the Quality Reviewer (QAS) for {{PROJECT_NAME}}.
    Read your instructions at: .claude/agents/quality-reviewer.md

    ## Task
    Review the complete repurpose-lesson output package.

    ## Files to Review
    - Post-production script: <lesson-dir>/youtube/post-production.md
    - YouTube HTML: <lesson-dir>/youtube/youtube.html
    - YouTube MD: <lesson-dir>/youtube/youtube.md
    - Storyboard: <lesson-dir>/youtube/storyboard/storyboard.md
    - Plan: <lesson-dir>/youtube/plan.md

    ## Also verify these files exist (glob for them):
    - <lesson-dir>/youtube/cards/intro.mp4
    - <lesson-dir>/youtube/cards/outro.mp4
    - <lesson-dir>/youtube/broll/ (at least one subdirectory with .mp4 files)
    - <lesson-dir>/youtube/storyboard/*.png (at least 1)

    ## FINAL PACKAGE CHECKLIST

    ### File Completeness
    - [ ] post-production.md exists and has intro/outro/B-roll sections
    - [ ] script-editor-notes.md exists
    - [ ] youtube.html exists with chapters, description, headlines
    - [ ] youtube.md exists with thumbnail prompts
    - [ ] cards/intro.mp4 exists
    - [ ] cards/outro.mp4 exists
    - [ ] At least 1 animated B-roll MP4 in broll/

    ### Internal Consistency
    - [ ] YouTube chapters align with lesson <h2> sections
    - [ ] B-roll descriptions in post-production.md match actual generated files
    - [ ] Next lesson info in outro matches "What's Next" from lesson HTML

    ### Brand Compliance
    - [ ] {{PROJECT_NAME}} branding present (cards use brand colors/fonts)
    - [ ] No clickbait headlines that don't deliver
    - [ ] Thumbnail prompts include brand DNA (synthwave, maritime, cyber)

    ## Return Format
    Return: APPROVED or BLOCKED with specific issues.
```

- **If APPROVED:** proceed to Phase 8
- **If BLOCKED:** address issues (max 1 revision cycle), then escalate to user if still blocked.

### Phase 8: Output & README

1. **Verify all expected files exist** (use Glob):
   - `<lesson-dir>/youtube/plan.md`
   - `<lesson-dir>/youtube/post-production.md`
   - `<lesson-dir>/youtube/script-editor-notes.md`
   - `<lesson-dir>/youtube/youtube.html`
   - `<lesson-dir>/youtube/youtube.md`
   - `<lesson-dir>/youtube/cards/intro.mp4`
   - `<lesson-dir>/youtube/cards/outro.mp4`
   - `<lesson-dir>/youtube/storyboard/storyboard.md`
   - `<lesson-dir>/youtube/storyboard/*.png`
   - `<lesson-dir>/youtube/broll/**/*.mp4`

2. **Generate README.md** (write this yourself):
   ```markdown
   # [Lesson Title] — YouTube Repurpose Package

   **Lesson:** [M.S.L] [Title]
   **Source:** [video/transcript path]

   ## Files

   | File | Description |
   |------|-------------|
   | `plan.md` | Repurpose plan |
   | `post-production.md` | Intro hook + outro/CTA + B-roll timing |
   | `script-editor-notes.md` | Editor's retention reasoning |
   | `youtube.html` | YouTube metadata |
   | `youtube.md` | Full metadata + thumbnail prompts |
   | `cards/intro.mp4` | Branded intro card (~4s) |
   | `cards/outro.mp4` | Branded outro card (~6s) |
   | `storyboard/` | Shot list + Venice AI images |
   | `broll/slides/` | Animated Slidev slides (MP4) |
   | `broll/hero/` | Animated hero image (MP4) |
   | `broll/storyboard/` | Animated storyboard images (MP4) |

   ## Editing Guide

   1. **Start with** `cards/intro.mp4` — the branded intro
   2. **Record** the intro hook from `post-production.md` (15-30s talking head)
   3. **Main content** — the original lesson recording
   4. **B-roll overlays** — drop animated clips from `broll/` at timestamps in `post-production.md`
   5. **Record** the outro from `post-production.md` (30-45s talking head)
   6. **End with** `cards/outro.mp4` — the branded outro
   7. **Upload** — use `youtube.html` for title/description/chapters

   ## Next Lesson
   [Next M.S.L] [Next Title]
   ```

3. **Build journal:** Append entry to `${BUILD_JOURNAL_PATH:-./build-journal}/YYYY-MM-DD.md` inline (see CLAUDE.md pipeline rule).

4. **Report results:**
   ```
   ## Lesson Repurposed for YouTube

   - Lesson: [M.S.L] [Title]
   - Intro card: [path] (branded, ~4s)
   - Outro card: [path] (branded, ~6s)
   - Post-production script: [path] (QAS Approved)
   - B-roll clips: [N] animated MP4s
   - Storyboard images: [N] generated PNGs
   - YouTube metadata: [path]
   - Status: Ready for editing

   Next steps: Record intro hook + outro from post-production.md, then edit using the guide in README.md.
   ```
