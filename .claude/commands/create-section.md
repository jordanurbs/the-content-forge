# /create-section -- Create a Section (3-5 Lessons)

Create a section of 3-5 related {{PROJECT_NAME}} lessons with cross-linking and shared presentation scaffold.

## Input: $ARGUMENTS

If no arguments provided, ask the user what section they want to create.

## Context Rules (MANDATORY)

Follow the Context Engineering rules in CLAUDE.md:
- Do NOT read agent or skill files yourself
- Pass file PATHS to agents, not contents
- Agents write to disk directly
- You track status and file paths only
- Generate ONE lesson at a time to keep context fresh

## Pipeline

### Phase 1: Section Planning

1. **Gather inputs:**
   - Section topic and scope
   - Number of lessons (3-5)
   - Input types per lesson (ideas, outlines, transcripts, videos -- can be mixed)
   - Section number (M.S format, e.g., 2.3)

2. **Create output directory:**
   ```
   aica-lessons/<section-slug>/
   aica-lessons/<section-slug>/assets/
   aica-lessons/<section-slug>/presentations/public/images/
   ```

3. **Present section plan:**
   ```
   ## Section Plan: [Title]
   - Section: [M.S]
   - Lessons: [count]

   ### Lesson [M.S.1]: [Title]
   - Input: [source type + path if file]
   - Key topics: [bullets]

   ### Lesson [M.S.2]: [Title]
   - Input: [source type + path if file]
   - Key topics: [bullets]

   [... for each lesson]

   ### Cross-Linking Plan:
   - Lesson 1 "What's Next" -> Lesson 2: [connection]
   - Lesson 2 "What's Next" -> Lesson 3: [connection]
   ```
   **Wait for user approval before proceeding.**

4. **Save approved plan:**
   Write the full plan to `<output-dir>/plan.md`

### Phase 2: Research (Optional)

Ask if research is needed for the section as a whole.

If yes, spawn Content Researcher ONCE for the entire section:
```
Task tool:
  description: "Research section topic"
  subagent_type: "general-purpose"
  max_turns: 10
  prompt: |
    You are the Content Researcher for {{PROJECT_NAME}}.
    Read your instructions at: .claude/agents/content-researcher.md

    ## Task
    Research supplemental content for section: [title]
    Lessons covered: [list of lesson topics]

    ## Output
    Write research notes to: <output-dir>/research.md
    Return: status, file path
```

### Phase 3: Transcription (If Any Videos)

For each video input, spawn Transcript Processor:
```
Task tool:
  description: "Transcribe [filename]"
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

Track transcript paths for each lesson.

### Phase 4: Sequential Lesson Generation

Generate each lesson ONE AT A TIME, in order (so cross-links work):

For each lesson [M.S.N]:

**Step 1 -- Lesson Writer:**
```
Task tool:
  description: "Write lesson [M.S.N]"
  subagent_type: "general-purpose"
  max_turns: 25
  prompt: |
    You are the Lesson Writer for {{PROJECT_NAME}}.
    Read your instructions at: .claude/agents/lesson-writer.md

    ## Task
    Write lesson [M.S.N]: [Title]
    This is lesson [N] of [total] in section [M.S]: [Section Title]

    ## Cross-Linking
    - Previous lesson: [M.S.(N-1)] - [Title] (or "none" if first)
    - Next lesson: [M.S.(N+1)] - [Title] (or "none" if last)
    - Use these in the "What's Next" section

    ## Input Files (read these yourself)
    - Plan: <output-dir>/plan.md
    - Transcript: <path> (if applicable)
    - Research: <output-dir>/research.md (if applicable)

    ## Output Files (write these yourself)
    - <output-dir>/lessons/<number>-<slug>.html
    - <output-dir>/lessons/<number>-<slug>.md

    ## Return Format
    Return ONLY: status, files created, any issues.
```

**Step 2 -- Presentation Designer** (after Lesson Writer completes):
```
Task tool:
  description: "Design presentation [M.S.N]"
  subagent_type: "general-purpose"
  max_turns: 25
  prompt: |
    You are the Presentation Designer for {{PROJECT_NAME}}.
    Read your instructions at: .claude/agents/presentation-designer.md

    ## Task
    Create Slidev presentation for lesson [M.S.N]: [Title]

    ## Input Files (read these yourself)
    - Plan: <output-dir>/plan.md
    - Lesson HTML: <output-dir>/lessons/<number>-<slug>.html

    ## Cross-Linking
    - Next lesson: [M.S.(N+1)] - [Title] (for "What's Next" slide)

    ## Output Files (write these yourself)
    - <output-dir>/presentations/slides/<number>.md

    ## Return Format
    Return ONLY: status, files created, any issues.
```

**Step 3 -- Image Generator (MANDATORY)** (after Presentation Designer completes):
```
Task tool:
  description: "Generate images [M.S.N]"
  subagent_type: "general-purpose"
  max_turns: 10
  prompt: |
    You are the Image Generator for {{PROJECT_NAME}}.
    Read your instructions at: .claude/agents/image-generator.md

    ## Task
    Generate hero and health break images for lesson [M.S.N]: [Title]

    ## Input Files (read these yourself)
    - Plan: <output-dir>/plan.md
    - Lesson HTML: <output-dir>/lessons/<number>-<slug>.html

    ## Output Directories
    - Assets: <output-dir>/assets/
    - Presentation images: <output-dir>/presentations/public/images/

    ## Naming
    - Hero image: <M.S.N>-<slug>.png
    - Health break: health-break-<exercise-slug>.png
    - Lesson number: [M.S.N]
    - Lesson slug: [slug]

    ## Deduplication
    Check if health break image already exists before generating.

    ## Return Format
    Return ONLY: status, images created, any issues.
```

Repeat for each lesson before moving to Phase 5.

### Phase 5: Section Quality Gate (MANDATORY)

Spawn Quality Reviewer for ALL lessons together:
```
Task tool:
  description: "QAS review section [M.S]"
  subagent_type: "general-purpose"
  model: opus
  max_turns: 15
  prompt: |
    You are the Quality Reviewer (QAS) for {{PROJECT_NAME}}.
    Read your instructions at: .claude/agents/quality-reviewer.md

    ## Task
    Review ALL content in section [M.S]: [Title]
    Output directory: <output-dir>/

    ## Files to Review
    [list all lesson HTML, MD, and presentation files]

    ## Section-Specific Checks
    - Verify "What's Next" in each lesson correctly references the next
    - Verify consistent M.S.L numbering
    - Verify no content gaps or redundancy between lessons

    ## Return Format
    Return: APPROVED or BLOCKED with specific issues per file.
```

- **If BLOCKED:** re-spawn only the affected agent(s) with specific issues. Max 2 iterations.

### Phase 6: Output

1. Copy Slidev scaffold:
   ```bash
   rsync -a --exclude='node_modules' --exclude='.DS_Store' --exclude='slides/' samples/presentations/ <output-dir>/presentations/
   ```
2. Verify all expected files exist
3. Generate README.md with section index
4. **Build journal:** Append entry to `${BUILD_JOURNAL_PATH:-./build-journal}/YYYY-MM-DD.md` inline (see CLAUDE.md pipeline rule).
5. Report:
   ```
   ## Section Created: [Title]

   ### Lessons:
   1. [M.S.1] - [Title]
   2. [M.S.2] - [Title]
   3. [M.S.3] - [Title]

   ### Files Created:
   - lessons/[list]
   - presentations/slides/[list]
   - README.md

   ### QAS Status: Approved
   ```
