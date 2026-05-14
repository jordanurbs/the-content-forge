# /create-lesson -- Create a Single Lesson

Create a single {{PROJECT_NAME}} lesson (HTML + presentation) from any input type.

## Input: $ARGUMENTS

If no arguments provided, ask the user what they want to create a lesson about.

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
   - Outline (text or file) -> planning
   - Transcript file (.txt, .srt, .vtt) -> note path, go to planning
   - Video file (.mp4, .mov, etc.) -> Phase 3 first

2. **Determine lesson number:**
   - Ask user for the lesson number (M.S.L format, e.g., 2.3.1)

3. **Create output directory:**
   ```
   aica-lessons/<topic-slug>/
   aica-lessons/<topic-slug>/assets/
   aica-lessons/<topic-slug>/presentations/public/images/
   ```

4. **Present lesson plan to user:**
   ```
   ## Lesson Plan: [Title]
   - Number: [M.S.L]
   - Topic: [description]
   - Key objectives: [3-5 bullets]
   - Estimated sections: [list]
   - Input source: [what we're working from]
   ```
   **Wait for user approval before proceeding.**

5. **Save approved plan:**
   Write the plan to `<output-dir>/plan.md` so agents can read it.

### Phase 2: Research (Optional)

Ask: "Would you like me to research supplemental content for this lesson?"

If yes, spawn Content Researcher:
```
Task tool:
  description: "Research lesson topic"
  subagent_type: "general-purpose"
  max_turns: 10
  prompt: |
    You are the Content Researcher for {{PROJECT_NAME}}.
    Read your instructions at: .claude/agents/content-researcher.md

    ## Task
    Research supplemental content for: [topic]
    Key areas to research: [specific questions]

    ## Output
    Write research notes to: <output-dir>/research.md
    Return: status, file path
```

### Phase 3: Transcription (If Video Input)

Spawn Transcript Processor:
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

### Phase 4: Content Generation

**Step 1 -- Spawn Lesson Writer:**
```
Task tool:
  description: "Write lesson [M.S.L]"
  subagent_type: "general-purpose"
  max_turns: 25
  prompt: |
    You are the Lesson Writer for {{PROJECT_NAME}}.
    Read your instructions at: .claude/agents/lesson-writer.md

    ## Task
    Write lesson [M.S.L]: [Title]

    ## Input Files (read these yourself)
    - Plan: <output-dir>/plan.md
    - Transcript: <path> (if applicable, otherwise skip)
    - Research: <output-dir>/research.md (if applicable, otherwise skip)

    ## Output Files (write these yourself)
    - <output-dir>/lessons/<number>-<slug>.html
    - <output-dir>/lessons/<number>-<slug>.md

    ## Return Format
    Return ONLY: status, files created, any issues.
```

**Step 2 -- Spawn Presentation Designer** (after Lesson Writer completes):
```
Task tool:
  description: "Design presentation [M.S.L]"
  subagent_type: "general-purpose"
  max_turns: 25
  prompt: |
    You are the Presentation Designer for {{PROJECT_NAME}}.
    Read your instructions at: .claude/agents/presentation-designer.md

    ## Task
    Create Slidev presentation for lesson [M.S.L]: [Title]

    ## Input Files (read these yourself)
    - Plan: <output-dir>/plan.md
    - Lesson HTML: <output-dir>/lessons/<number>-<slug>.html

    ## Output Files (write these yourself)
    - <output-dir>/presentations/slides/<number>.md

    ## Return Format
    Return ONLY: status, files created, any issues.
```

### Phase 4.5: Image Generation (MANDATORY)

**Step 3 -- Spawn Image Generator** (after Presentation Designer completes):
```
Task tool:
  description: "Generate images [M.S.L]"
  subagent_type: "general-purpose"
  max_turns: 10
  prompt: |
    You are the Image Generator for {{PROJECT_NAME}}.
    Read your instructions at: .claude/agents/image-generator.md

    ## Task
    Generate hero and health break images for lesson [M.S.L]: [Title]

    ## Input Files (read these yourself)
    - Plan: <output-dir>/plan.md
    - Lesson HTML: <output-dir>/lessons/<number>-<slug>.html

    ## Output Directories
    - Assets: <output-dir>/assets/
    - Presentation images: <output-dir>/presentations/public/images/

    ## Naming
    - Hero image: <M.S.L>-<slug>.png
    - Health break: health-break-<exercise-slug>.png
    - Lesson number: [M.S.L]
    - Lesson slug: [slug]

    ## Return Format
    Return ONLY: status, images created, any issues.
```

**Do NOT proceed to Phase 5 without images. QAS will reject content missing hero or health break images.**

### Phase 5: Quality Gate (MANDATORY)

Spawn Quality Reviewer:
```
Task tool:
  description: "QAS review lesson [M.S.L]"
  subagent_type: "general-purpose"
  model: opus
  max_turns: 15
  prompt: |
    You are the Quality Reviewer (QAS) for {{PROJECT_NAME}}.
    Read your instructions at: .claude/agents/quality-reviewer.md

    ## Task
    Review all generated content in: <output-dir>/

    ## Files to Review
    - Lesson HTML: <output-dir>/lessons/<number>-<slug>.html
    - Lesson MD: <output-dir>/lessons/<number>-<slug>.md
    - Presentation: <output-dir>/presentations/slides/<number>.md

    ## Return Format
    Return: APPROVED or BLOCKED with specific issues.
```

- **If APPROVED:** proceed to Phase 6
- **If BLOCKED:** re-spawn the relevant agent with the issue list appended. Max 2 iterations before escalating to user.

### Phase 6: Output

1. Copy Slidev scaffold:
   ```bash
   rsync -a --exclude='node_modules' --exclude='.DS_Store' --exclude='slides/' samples/presentations/ <output-dir>/presentations/
   ```
2. Verify all expected files exist (use Glob)
3. Generate README.md index for the output folder (write this yourself -- it's small)
4. **Build journal:** Append entry to `${BUILD_JOURNAL_PATH:-./build-journal}/YYYY-MM-DD.md` inline (see CLAUDE.md pipeline rule).
5. Report results:
   ```
   ## Lesson Created

   - Lesson: [M.S.L] - [Title]
   - HTML: [path]
   - Markdown: [path]
   - Presentation: [path]
   - Status: QAS Approved
   ```
