# /lesson-to-video — Lesson-to-Video Pre-Production Pipeline

Turn an existing lesson into a complete video pre-production package: unified script (intro hook + core content + outro/CTA), treatment with slide-aware B-roll, storyboard images, and pre-staged YouTube metadata — everything needed to record in one session.

## Input: $ARGUMENTS

If no arguments provided, ask the user for:
1. Path to the lesson directory (containing lesson `.html` and optionally `presentations/`)
2. Target duration: short (5-8 min), standard (10-15 min), or deep dive (20-30 min)

## Context Rules (MANDATORY)

Follow the Context Engineering rules in CLAUDE.md:
- Do NOT read agent or skill files yourself
- Pass file PATHS to agents, not contents
- Agents write to disk directly
- You track status and file paths only

## Pipeline

### Phase 1: Input & Planning (MANDATORY)

1. **Validate lesson directory:**
   - Find the lesson `.html` file (glob for `lessons/*.html`)
   - Extract: lesson title (first `<h1>` or `<h2>`), M.S.L number (from filename), `<h2>` section headings, "What's Next" content
   - Find the presentation slides (glob for `presentations/slides/*.md`)
   - Note how many slides exist and their section titles
   - Confirm hero image exists in `assets/`

2. **Gather video details:**
   - Working title (derived from lesson title)
   - Target duration: short (5-8 min), standard (10-15 min), or deep dive (20-30 min)
   - Visual style: `brand-default` (default)
   - Audience (default from `.audience.txt` or CLAUDE.md)

3. **Create output directory:**
   ```
   aica-lessons/<topic-slug>/
   aica-lessons/<topic-slug>/storyboard/
   aica-lessons/<topic-slug>/storyboard/ref/
   ```

4. **Present plan to user:**
   ```
   ## Lesson-to-Video Plan: [Working Title]

   - Lesson: [M.S.L] [Title]
   - Lesson HTML: [path]
   - Presentation: [path] ([N] slides)
   - Hero image: [path]
   - Next lesson: [M.S.L] [Title] (from "What's Next")
   - Target duration: [short/standard/deep dive] ([X-Y] minutes)
   - Visual style: [brand-default or custom]
   - Audience: [who this is for]

   ## Slide Inventory
   | Slide # | Title/Topic |
   |---------|-------------|
   | 1       | [Cover]     |
   | 2       | [topic]     |
   | ...     | ...         |

   ## What will be generated:
   1. Unified script (intro hook + core + outro in one file)
   2. Treatment with slide-aware B-roll markers
   3. Storyboard images (Venice AI)
   4. Pre-staged YouTube metadata (estimated timestamps)
   ```
   **Wait for user approval before proceeding.**

5. **Save approved plan:**
   Write the plan to `<output-dir>/plan.md` with `visual_style` field and the slide inventory.

### Phase 2: Research (Optional)

Ask: "Would you like me to research supplemental content for this video?"

If yes, spawn Content Researcher:
```
Task tool:
  description: "Research video topic"
  subagent_type: "general-purpose"
  max_turns: 10
  prompt: |
    You are the Content Researcher for {{PROJECT_NAME}}.
    Read your instructions at: .claude/agents/content-researcher.md

    ## Task
    Research supplemental content for a video about: [topic]
    Key areas to research: [specific questions]

    ## Output
    Write research notes to: <output-dir>/research.md
    Return: status, file path
```

### Phase 3: Script Writing

Spawn Script Writer in **LESSON-TO-VIDEO MODE**:
```
Task tool:
  description: "Write unified video script"
  subagent_type: "general-purpose"
  max_turns: 25
  prompt: |
    You are the Script Writer for {{PROJECT_NAME}}.
    Read your instructions at: .claude/agents/script-writer.md

    ## MODE: LESSON-TO-VIDEO
    You are adapting an EXISTING LESSON into a unified video script.
    This is NOT a standard pre-production script and NOT a post-production script.

    Your script.md must be a SINGLE unified file with ALL of these sections:

    1. **Intro Hook** (15-30s):
       - Compelling reason to watch — what will the viewer learn/gain?
       - Reference a specific moment or outcome from the lesson
       - Must create a reason to keep watching within the first 8 seconds
       - Format: talking points (this WILL be recorded)

    2. **Cold Open** (30-60s):
       - The script template's standard cold open section
       - Bridge from the hook into the core content
       - Plant the first open loop

    3. **Intro** (30-45s):
       - Who you are, what we're covering, what they'll walk away with
       - Brief mention of Module/Section context

    4. **Core Content** (bulk of the video):
       - Adapt the lesson's content for verbal delivery
       - Restructure written sections for video pacing
       - Convert explanations to demo-oriented talking points
       - Preserve all specific numbers, tool names, examples
       - Include `[SLIDE REF: N]` markers where a Slidev slide should appear as B-roll
         (N = slide number from the presentation, as listed in the plan's Slide Inventory)

    5. **Payoff** (1-2 min):
       - The "aha" moment — concrete result or transformation
       - Resolve all open loops

    6. **Outro/CTA** (30-45s):
       - Natural closing that references what was covered
       - Single CTA (subscribe, next lesson, or community)
       - Tease the next lesson: [NEXT_LESSON_TITLE] ([NEXT_LESSON_NUMBER])

    ## SLIDE REF Rules
    - Read the lesson's Slidev presentation file to understand each slide's content
    - Place `[SLIDE REF: N]` in the script wherever that slide's content aligns with what's being discussed
    - Not every slide needs a reference — only where it adds visual value
    - Typical: 5-10 slide refs for a 10-15 minute video
    - These tell the Treatment Creator and editor which slides to show as B-roll

    ## Input Files (read these yourself)
    - Plan: <output-dir>/plan.md
    - Lesson HTML: <lesson-html-path>
    - Presentation slides: <presentation-slides-path>
    - Research: <output-dir>/research.md (if applicable, otherwise skip)

    ## Output Files (write these yourself)
    - <output-dir>/script.md

    ## Return Format
    Return ONLY: status, file path, target duration, section count, slide ref count.
```

### Phase 4: Script Editing

Spawn Script Editor in **LESSON-TO-VIDEO MODE**:
```
Task tool:
  description: "Edit script for retention"
  subagent_type: "general-purpose"
  max_turns: 20
  prompt: |
    You are the Script Editor for {{PROJECT_NAME}}.
    Read your instructions at: .claude/agents/script-editor.md

    ## MODE: LESSON-TO-VIDEO
    This script has a unified structure: Intro Hook + Cold Open + Intro + Core Content + Payoff + Outro/CTA — all in one file.

    Additional focus areas for this mode:
    - Intro Hook: Does it create a reason to watch in 8 seconds? Is the hook specific to the lesson content?
    - Outro/CTA: Is the CTA singular and natural? Does the next-lesson tease work?
    - [SLIDE REF: N] markers: Do NOT remove or renumber these — they're alignment anchors for post-production
    - Lesson fidelity: The core content must accurately represent the lesson. Do NOT cut key concepts to improve pacing.

    ## Input Files (read these yourself)
    - Script: <output-dir>/script.md
    - Plan: <output-dir>/plan.md

    ## Output Files (write these yourself)
    - <output-dir>/script.md (edit in place)
    - <output-dir>/script-editor-notes.md

    ## Return Format
    Return ONLY: status, files, summary of changes, retention assessment.
```

### Phase 5: QAS Gate #1 (MANDATORY)

Spawn Quality Reviewer with LESSON-TO-VIDEO checklist:
```
Task tool:
  description: "QAS review lesson-to-video script"
  subagent_type: "general-purpose"
  model: opus
  max_turns: 15
  prompt: |
    You are the Quality Reviewer (QAS) for {{PROJECT_NAME}}.
    Read your instructions at: .claude/agents/quality-reviewer.md

    ## Task
    Review the lesson-to-video script and editor notes.

    ## Files to Review
    - Script: <output-dir>/script.md
    - Editor notes: <output-dir>/script-editor-notes.md
    - Plan: <output-dir>/plan.md
    - Source lesson HTML: <lesson-html-path> (for fidelity check)

    ## LESSON-TO-VIDEO CHECKLIST (use this instead of the lesson or standard video checklist)

    ### Voice
    - [ ] Sounds like the configured voice — conversational, specific, honest
    - [ ] Talking-points format maintained (NOT full sentences for reading)
    - [ ] Ad-lib zones present (2-4 minimum)
    - [ ] "Builders" tone, never guru/expert positioning
    - [ ] Specific numbers, tool names, real examples throughout

    ### Structure
    - [ ] All required sections present: Intro Hook, Cold Open, Intro, Core Content, Payoff, Outro/CTA
    - [ ] Intro Hook creates a reason to watch within 8 seconds
    - [ ] Outro/CTA includes next lesson tease with title and number
    - [ ] Every section has a target duration
    - [ ] Section durations sum to the target range

    ### Engagement Architecture
    - [ ] Open loops planted every 3-5 minutes
    - [ ] All open loops resolved before recap
    - [ ] Pattern interrupts every 3-4 minutes (no 5+ min gaps)
    - [ ] Retention risk markers at likely drop-off points
    - [ ] CTAs only at high-engagement moments (max 2)

    ### Timing
    - [ ] Every section has a target duration in minutes
    - [ ] Total duration falls within target range (from plan)
    - [ ] Setup section is under 2 minutes
    - [ ] No single section exceeds 5 minutes without a pattern interrupt

    ### Lesson Fidelity (NEW — specific to lesson-to-video)
    - [ ] Core lesson concepts are all represented in the script
    - [ ] Specific numbers, tool names, and examples from the lesson are preserved
    - [ ] The lesson's narrative arc (the "story" it tells) survives adaptation
    - [ ] No key sections from the lesson were dropped entirely
    - [ ] [SLIDE REF: N] markers are present and reference valid slide numbers

    ### Content Quality
    - [ ] At least one failure story with real details
    - [ ] Specific numbers/tools/examples (not generic advice)
    - [ ] Honest assessment present (not just hype)
    - [ ] Transitions between sections are clear

    ### Editor Notes
    - [ ] Editor notes file exists
    - [ ] Notes explain retention reasoning for changes
    - [ ] Engagement marker summary is included

    ## Return Format
    Return: APPROVED or BLOCKED with specific issues referencing the checklist above.
```

- **If APPROVED:** proceed to Phase 6
- **If BLOCKED:** re-spawn Script Writer and/or Script Editor with the issue list appended. Max 2 revision cycles before escalating to user with the QAS feedback.

### Phase 6: Treatment Creation

Spawn Treatment Creator in **LESSON-TO-VIDEO MODE**:
```
Task tool:
  description: "Create production treatment"
  subagent_type: "general-purpose"
  max_turns: 15
  prompt: |
    You are the Treatment Creator for {{PROJECT_NAME}}.
    Read your instructions at: .claude/agents/treatment-creator.md

    ## MODE: LESSON-TO-VIDEO
    This treatment has an additional B-roll categorization system.

    In addition to standard B-roll callouts, categorize each B-roll moment by TYPE:

    ### B-Roll Type Legend
    Use this legend at the top of the treatment, and tag each B-roll callout:

    - **SLIDE** — A Slidev slide from the lesson's presentation (referenced by `[SLIDE REF: N]` in the script)
    - **GENERATED** — A Venice AI generated image (will go to the Storyboarder)
    - **HERO** — The lesson's hero image
    - **SCREENSHARE** — Live screen capture during recording (not pre-produced)

    Format B-roll callouts as:
    ```
    [B-ROLL: TYPE — description — ~Xs]
    ```

    Examples:
    - `[B-ROLL: SLIDE — Slide 5: Three Layers diagram — ~4s]`
    - `[B-ROLL: GENERATED — pixelated prompt dissolving into void — ~3s]`
    - `[B-ROLL: HERO — lesson hero image, context engineering visual — ~3s]`
    - `[B-ROLL: SCREENSHARE — terminal showing CLAUDE.md file — ~5s]`

    ## Input Files (read these yourself)
    - Script: <output-dir>/script.md
    - Plan: <output-dir>/plan.md

    ## Output Files (write these yourself)
    - <output-dir>/treatment.md

    ## Return Format
    Return ONLY: status, file path, total duration, B-roll callout count, breakdown by type (SLIDE/GENERATED/HERO/SCREENSHARE).
```

### Phase 7: Storyboarding

Spawn Storyboarder (after Treatment Creator completes):
```
Task tool:
  description: "Generate storyboard images"
  subagent_type: "general-purpose"
  max_turns: 20
  prompt: |
    You are the Storyboarder for {{PROJECT_NAME}}.
    Read your instructions at: .claude/agents/storyboarder.md

    ## Task
    Generate storyboard images for B-roll moments marked as GENERATED in the treatment.
    Ignore SLIDE, HERO, and SCREENSHARE types — those are handled separately.

    ## Input Files (read these yourself)
    - Treatment: <output-dir>/treatment.md
    - Script: <output-dir>/script.md
    - Plan: <output-dir>/plan.md (check visual_style field)

    ## Output Files (write these yourself)
    - <output-dir>/storyboard/storyboard.md
    - <output-dir>/storyboard/*.png (3-7 images, 10 max)

    ## Additional Reference Asset
    Copy the hero image to the ref directory:
    - Source: <hero-image-path>
    - Destination: <output-dir>/storyboard/ref/hero.png

    ## Output Directory
    Images go in: <output-dir>/storyboard/

    ## Return Format
    Return ONLY: status, file list, image count, visual style used.
```

### Phase 8: YouTube Packaging

Spawn YouTube Packager in **PRE-STAGING MODE**:
```
Task tool:
  description: "Pre-stage YouTube metadata"
  subagent_type: "general-purpose"
  max_turns: 15
  prompt: |
    You are the YouTube Packager for {{PROJECT_NAME}}.
    Read your instructions at: .claude/agents/youtube-packager.md

    ## MODE: PRE-STAGING
    The video has NOT been recorded yet. You are pre-staging YouTube metadata from a script, not a transcript.

    Key differences from normal mode:
    1. **Chapter timestamps are ESTIMATED** — derive them from section durations in the script
       Format: `~MM:SS (est.)` instead of precise `MM:SS`
    2. **Description** — write it based on the script content and lesson objectives
    3. **Headlines** — generate from the video topic, not transcript analysis
    4. **Thumbnail prompts** — generate as normal

    After recording, timestamps will be updated to match the actual video. Include a note:
    ```
    NOTE: Timestamps are estimated from script section durations. Update after recording.
    ```

    ## Input Files (read these yourself)
    - Script: <output-dir>/script.md
    - Plan: <output-dir>/plan.md
    - Lesson HTML: <lesson-html-path> (for "What You'll Get" and section headings)
    - Audience: .audience.txt (if it exists, otherwise use default)

    ## Output Files (write these yourself)
    - <output-dir>/youtube.html
    - <output-dir>/youtube.md

    ## Return Format
    Return ONLY: status, file paths, best headline.
```

### Phase 9: QAS Gate #2 (MANDATORY)

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
    Review the complete lesson-to-video output package.

    ## Files to Review
    - Script: <output-dir>/script.md
    - Editor notes: <output-dir>/script-editor-notes.md
    - Treatment: <output-dir>/treatment.md
    - YouTube HTML: <output-dir>/youtube.html
    - YouTube MD: <output-dir>/youtube.md
    - Storyboard: <output-dir>/storyboard/storyboard.md
    - Plan: <output-dir>/plan.md

    ## Also verify these files exist (glob for them):
    - <output-dir>/storyboard/*.png (at least 1 generated image)
    - <output-dir>/storyboard/ref/hero.png (hero image copied)

    ## FINAL PACKAGE CHECKLIST

    ### File Completeness
    - [ ] plan.md exists with slide inventory
    - [ ] script.md exists with unified structure (intro hook through outro)
    - [ ] script-editor-notes.md exists
    - [ ] treatment.md exists with B-roll type legend (SLIDE/GENERATED/HERO/SCREENSHARE)
    - [ ] youtube.html exists with estimated chapter timestamps
    - [ ] youtube.md exists with thumbnail prompts
    - [ ] storyboard/storyboard.md exists
    - [ ] At least 1 generated image in storyboard/
    - [ ] Hero image in storyboard/ref/hero.png

    ### Internal Consistency
    - [ ] Script [SLIDE REF: N] markers correspond to real slides in the presentation
    - [ ] Treatment SLIDE B-roll callouts match script's [SLIDE REF: N] markers
    - [ ] Treatment GENERATED callouts match storyboard images
    - [ ] YouTube chapters align with script sections
    - [ ] Next lesson info in outro matches "What's Next" from lesson HTML
    - [ ] Estimated chapter timestamps are plausible given section durations

    ### Brand Compliance
    - [ ] No clickbait headlines that don't deliver
    - [ ] Thumbnail prompts include brand DNA (synthwave, maritime, cyber)
    - [ ] "Builders" tone throughout

    ## Return Format
    Return: APPROVED or BLOCKED with specific issues.
```

- **If APPROVED:** proceed to Phase 10
- **If BLOCKED:** address issues (max 1 revision cycle), then escalate to user if still blocked.

### Phase 10: Output & README

1. **Verify all expected files exist** (use Glob):
   - `<output-dir>/plan.md`
   - `<output-dir>/script.md`
   - `<output-dir>/script-editor-notes.md`
   - `<output-dir>/treatment.md`
   - `<output-dir>/youtube.html`
   - `<output-dir>/youtube.md`
   - `<output-dir>/storyboard/storyboard.md`
   - `<output-dir>/storyboard/*.png` (at least 1)
   - `<output-dir>/storyboard/ref/hero.png`
   - `<output-dir>/research.md` (only if research was done)

2. **Generate README.md** (write this yourself — it's small):
   ```markdown
   # [Video Title] — Lesson-to-Video Pre-Production Package

   **Source Lesson:** [M.S.L] [Title]
   **Target Duration:** [X] minutes ([short/standard/deep dive])

   ## Files

   | File | Description |
   |------|-------------|
   | `plan.md` | Approved video plan with slide inventory |
   | `research.md` | Research notes (if applicable) |
   | `script.md` | QAS-approved unified script (intro hook + core + outro) |
   | `script-editor-notes.md` | Editor's retention reasoning |
   | `treatment.md` | Pacing + B-roll callouts (SLIDE/GENERATED/HERO/SCREENSHARE) |
   | `youtube.html` | Pre-staged YouTube metadata (estimated timestamps) |
   | `youtube.md` | Full metadata + thumbnail prompts |
   | `storyboard/storyboard.md` | Shot list with image refs |
   | `storyboard/*.png` | Generated storyboard images |
   | `storyboard/ref/hero.png` | Lesson hero image for B-roll |

   ## Recording Guide

   1. Review the script sections — record in order (intro hook through outro)
   2. Use treatment.md during recording for pacing reference
   3. When you see `[SLIDE REF: N]`, plan to show that slide as B-roll
   4. Use storyboard images for generated B-roll overlay during editing
   5. After recording, update youtube.html timestamps from estimated to actual

   ## B-Roll Types (from treatment.md)

   - **SLIDE** — Export Slidev slide N as PNG, overlay during section
   - **GENERATED** — Venice AI image from storyboard/
   - **HERO** — Lesson hero image (in storyboard/ref/hero.png)
   - **SCREENSHARE** — Capture live during recording

   ## Next Steps
   1. Record the video using script.md as your talking-points guide
   2. Edit with treatment.md for pacing + B-roll placement
   3. Update YouTube timestamps in youtube.html after recording
   4. Upload with youtube.html metadata

   ## Next Lesson
   [Next M.S.L] [Next Title]
   ```

3. **Build journal:** Append entry to `${BUILD_JOURNAL_PATH:-./build-journal}/YYYY-MM-DD.md` inline (see CLAUDE.md pipeline rule).

4. **Report results:**
   ```
   ## Lesson-to-Video Package Created

   - Source: [M.S.L] [Lesson Title]
   - Target duration: [X] minutes
   - Script: [path] (QAS Approved, unified: intro hook + core + outro)
   - Treatment: [path] (B-roll: [N] SLIDE, [N] GENERATED, [N] HERO, [N] SCREENSHARE)
   - Storyboard: [path] ([N] images)
   - YouTube: [path] (pre-staged with estimated timestamps)
   - Status: Ready for recording

   Next steps: Record using script.md, edit with treatment.md, update youtube.html timestamps after recording.
   ```

## Lesson-to-Video Output Structure

```
<topic-slug>/
  README.md
  plan.md
  script.md                      # Unified: intro hook + core + outro
  script-editor-notes.md
  treatment.md                   # B-roll: SLIDE + GENERATED + HERO + SCREENSHARE
  youtube.html                   # Pre-staged (estimated timestamps)
  youtube.md                     # Full metadata + thumbnail prompts
  storyboard/
    storyboard.md                # Shot list with image refs
    01-<slug>.png
    02-<slug>.png
    ...
    ref/
      hero.png                   # Copied from lesson assets
      ref-*.png                  # Reference screenshots
```
