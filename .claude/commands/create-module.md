# /create-module -- Create a Full Module

Create a full {{PROJECT_NAME}} module (multiple sections, each with multiple lessons).

## Input: $ARGUMENTS

If no arguments provided, ask the user what module they want to create.

## Context Rules (MANDATORY)

Follow the Context Engineering rules in CLAUDE.md:
- Do NOT read agent or skill files yourself
- Pass file PATHS to agents, not contents
- Agents write to disk directly
- You track status and file paths only
- Generate ONE lesson at a time to keep context fresh

## Pipeline

### Phase 1: Module Planning

1. **Gather inputs:**
   - Module topic and scope
   - Module number (M format, e.g., 3)
   - Number of sections
   - Lessons per section
   - Any existing content (transcripts, outlines, videos)

2. **Create output directory:**
   ```
   aica-lessons/<module-slug>/
   ```

3. **Present module plan:**
   ```
   ## Module Plan: [Title]
   - Module: [M]
   - Sections: [count]
   - Total Lessons: [count]

   ### Section [M.1]: [Title]
   - Lesson [M.1.1]: [Title] — [input source]
   - Lesson [M.1.2]: [Title] — [input source]
   - Lesson [M.1.3]: [Title] — [input source]

   ### Section [M.2]: [Title]
   - Lesson [M.2.1]: [Title] — [input source]
   - Lesson [M.2.2]: [Title] — [input source]

   [... for each section]

   ### Flow:
   [How sections connect and build on each other]
   ```
   **Wait for user approval before proceeding.**

4. **Save approved plan:**
   Write the full plan to `<output-dir>/plan.md`

### Phase 2: Section-by-Section Generation

For each section, run the section pipeline:

1. **Research** (if applicable) -- spawn Content Researcher once per section
2. **Transcription** (if applicable) -- spawn Transcript Processor per video
3. **Sequential lesson generation** -- one lesson at a time:
   - Spawn Lesson Writer (max_turns: 25)
   - Spawn Presentation Designer (max_turns: 25)
   - Spawn Image Generator (max_turns: 10) — hero (per lesson) **(MANDATORY)**
   - Track output file paths
4. **Section quality review** -- spawn Quality Reviewer for the section's files (model: opus, max_turns: 15)
   - If BLOCKED: fix and re-review (max 2 iterations)

Use the exact spawning patterns from `/create-section` for each section.

Cross-section linking: ensure last lesson of section N references first lesson of section N+1 in its "What's Next".

### Phase 3: Module Quality Gate (MANDATORY)

After all sections pass their individual QAS reviews, spawn a final module-level review:
```
Task tool:
  description: "QAS module review [M]"
  subagent_type: "general-purpose"
  model: opus
  max_turns: 15
  prompt: |
    You are the Quality Reviewer (QAS) for {{PROJECT_NAME}}.
    Read your instructions at: .claude/agents/quality-reviewer.md

    ## Task
    Module-level review of Module [M]: [Title]
    Output directory: <output-dir>/

    ## Module-Specific Checks
    - Cross-section linking: last lesson of each section -> first lesson of next section
    - Consistent numbering across ALL sections (M.S.L format)
    - Progressive difficulty/complexity across sections
    - No content gaps or redundancy between sections
    - Overall flow makes sense as a learning journey

    ## Files to Review
    [list ALL lesson HTML and presentation files across all sections]

    ## Return Format
    Return: APPROVED or BLOCKED with specific issues per file.
```

### Phase 4: Output

1. Copy Slidev scaffold:
   ```bash
   rsync -a --exclude='node_modules' --exclude='.DS_Store' --exclude='slides/' samples/presentations/ <output-dir>/presentations/
   ```
2. Verify all expected files exist
3. Generate README.md with full module index
4. **Build journal:** Append entry to `${BUILD_JOURNAL_PATH:-./build-journal}/YYYY-MM-DD.md` inline (see CLAUDE.md pipeline rule).
5. Report:
   ```
   ## Module Created: [Title]

   ### Section [M.1]: [Title]
   - [M.1.1] - [Title]
   - [M.1.2] - [Title]
   - [M.1.3] - [Title]

   ### Section [M.2]: [Title]
   - [M.2.1] - [Title]
   - [M.2.2] - [Title]

   ### Total: [X] sections, [Y] lessons
   ### QAS Status: Approved
   ```
