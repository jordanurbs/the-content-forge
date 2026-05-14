# /create-video — YouTube Video Production Pipeline

Create a pre-production package for a YouTube tutorial video: talking-points script, engagement-optimized revision, treatment document, and visual storyboard with generated images.

## Input: $ARGUMENTS

If no arguments provided, ask the user what they want to create a video about.

## Context Rules (MANDATORY)

Follow the Context Engineering rules in CLAUDE.md:
- Do NOT read agent or skill files yourself
- Pass file PATHS to agents, not contents
- Agents write to disk directly
- You track status and file paths only

## Pipeline

### Phase 1: Input & Planning

1. **Identify input type:**
   - Idea/concept (text in chat) -> planning
   - Outline/notes (text or file) -> planning
   - Transcript file (.txt, .srt, .vtt) -> note path, plan, Phase 2.5
   - Lesson content (.html, .md from a lesson) -> note path, planning
   - Video file (.mp4, .mov, etc.) -> Phase 2.5 first

2. **Gather video details:**
   - Working title
   - Target duration: short (5-8 min), standard (10-15 min), or deep dive (20-30 min)
   - Visual style: `brand-default` (80s synthwave/maritime/pixel art) or custom description
   - Audience (default: AI developers and creators in the {{PROJECT_NAME}} community)

3. **Create output directory:**
   ```
   aica-lessons/<video-slug>/
   aica-lessons/<video-slug>/storyboard/
   ```

4. **Present video plan to user:**
   ```
   ## Video Plan: [Working Title]

   - Target duration: [short/standard/deep dive] ([X-Y] minutes)
   - Visual style: [brand-default or custom description]
   - Audience: [who this is for]
   - Input source: [what we're working from]
   - Key topics: [3-5 bullets]
   - Narrative arc: [hook > context > core sections > payoff > recap]
   ```
   **Wait for user approval before proceeding.**

5. **Save approved plan:**
   Write the plan to `<output-dir>/plan.md` with a `visual_style` field:
   ```markdown
   ## Video Plan: [Working Title]

   **visual_style:** brand-default

   ...rest of plan...
   ```

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

### Phase 2.5: Transcription (If Video Input)

Only if input is a video file. Spawn Transcript Processor:
```
Task tool:
  description: "Transcribe video file"
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

### Phase 3: Script Writing

Spawn Script Writer:
```
Task tool:
  description: "Write video script"
  subagent_type: "general-purpose"
  max_turns: 25
  prompt: |
    You are the Script Writer for {{PROJECT_NAME}}.
    Read your instructions at: .claude/agents/script-writer.md

    ## Task
    Write a talking-points video script for: [Working Title]

    ## Input Files (read these yourself)
    - Plan: <output-dir>/plan.md
    - Transcript: <path> (if applicable, otherwise skip)
    - Research: <output-dir>/research.md (if applicable, otherwise skip)
    - Lesson: <path> (if adapting from lesson content, otherwise skip)

    ## Output Files (write these yourself)
    - <output-dir>/script.md

    ## Return Format
    Return ONLY: status, file path, target duration, section count.
```

### Phase 4: Script Editing

Spawn Script Editor (after Script Writer completes):
```
Task tool:
  description: "Edit script for retention"
  subagent_type: "general-purpose"
  max_turns: 20
  prompt: |
    You are the Script Editor for {{PROJECT_NAME}}.
    Read your instructions at: .claude/agents/script-editor.md

    ## Task
    Optimize this script for YouTube viewer retention.

    ## Input Files (read these yourself)
    - Script: <output-dir>/script.md
    - Plan: <output-dir>/plan.md

    ## Output Files (write these yourself)
    - <output-dir>/script.md (edit in place)
    - <output-dir>/script-editor-notes.md

    ## Return Format
    Return ONLY: status, files, summary of changes, retention assessment.
```

### Phase 5: Quality Gate (MANDATORY)

Spawn Quality Reviewer with VIDEO-SPECIFIC checklist:
```
Task tool:
  description: "QAS review video script"
  subagent_type: "general-purpose"
  model: opus
  max_turns: 15
  prompt: |
    You are the Quality Reviewer (QAS) for {{PROJECT_NAME}}.
    Read your instructions at: .claude/agents/quality-reviewer.md

    ## Task
    Review the video script and editor notes in: <output-dir>/

    ## Files to Review
    - Script: <output-dir>/script.md
    - Editor notes: <output-dir>/script-editor-notes.md
    - Plan: <output-dir>/plan.md

    ## VIDEO SCRIPT CHECKLIST (use this instead of the lesson checklist)

    ### Voice
    - [ ] Sounds like the configured voice — conversational, specific, honest
    - [ ] Talking-points format maintained (NOT full sentences for reading)
    - [ ] Ad-lib zones present (2-4 minimum)
    - [ ] "Builders" tone, never guru/expert positioning
    - [ ] Specific numbers, tool names, real examples throughout

    ### Structure
    - [ ] All required sections present: Cold Open, Intro, Setup, Core Content, Payoff, Recap+CTA
    - [ ] Cold open creates a reason to watch within 8 seconds
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

Spawn Treatment Creator (after QAS approval):
```
Task tool:
  description: "Create production treatment"
  subagent_type: "general-purpose"
  max_turns: 15
  prompt: |
    You are the Treatment Creator for {{PROJECT_NAME}}.
    Read your instructions at: .claude/agents/treatment-creator.md

    ## Task
    Create a production treatment document from the approved script.

    ## Input Files (read these yourself)
    - Script: <output-dir>/script.md
    - Plan: <output-dir>/plan.md

    ## Output Files (write these yourself)
    - <output-dir>/treatment.md

    ## Return Format
    Return ONLY: status, file path, total duration, B-roll callout count.
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
    Generate storyboard images and shot list for the video.

    ## Input Files (read these yourself)
    - Treatment: <output-dir>/treatment.md
    - Script: <output-dir>/script.md
    - Plan: <output-dir>/plan.md (check visual_style field)

    ## Output Files (write these yourself)
    - <output-dir>/storyboard/storyboard.md
    - <output-dir>/storyboard/*.png (3-7 images, 10 max)

    ## Output Directory
    Images go in: <output-dir>/storyboard/

    ## Return Format
    Return ONLY: status, file list, image count, visual style used.
```

### Phase 8: Output & README

1. **Verify all expected files exist** (use Glob):
   - `<output-dir>/plan.md`
   - `<output-dir>/script.md`
   - `<output-dir>/script-editor-notes.md`
   - `<output-dir>/treatment.md`
   - `<output-dir>/storyboard/storyboard.md`
   - `<output-dir>/storyboard/*.png` (at least 1)
   - `<output-dir>/research.md` (only if research was done)

2. **Generate README.md** (write this yourself — it's small):
   ```markdown
   # [Video Title] — Pre-Production Package

   ## Files

   | File | Description |
   |------|-------------|
   | `plan.md` | Approved video plan |
   | `research.md` | Research notes (if applicable) |
   | `script.md` | QAS-approved talking-points script |
   | `script-editor-notes.md` | Editor's retention reasoning |
   | `treatment.md` | Pacing + B-roll callouts |
   | `storyboard/storyboard.md` | Shot list with image refs |
   | `storyboard/*.png` | Generated storyboard images |

   ## Target Duration
   [X] minutes ([short/standard/deep dive])

   ## Next Steps
   1. Review the script and treatment
   2. Record the video using script.md as your talking-points guide
   3. Use treatment.md during recording for pacing reference
   4. Use storyboard images for intro/B-roll overlay during editing
   5. After recording, run `/youtube-package` for title, description, chapters, and thumbnail
   ```

3. **Build journal:** Append entry to `${BUILD_JOURNAL_PATH:-./build-journal}/YYYY-MM-DD.md` inline (see CLAUDE.md pipeline rule).

4. **Report results:**
   ```
   ## Video Pre-Production Package Created

   - Video: [Working Title]
   - Target duration: [X] minutes
   - Script: [path] (QAS Approved)
   - Treatment: [path]
   - Storyboard: [path] ([N] images)
   - Status: Ready for recording

   Next steps: Record using script.md as your talking-points guide, then run `/youtube-package` after recording.
   ```
