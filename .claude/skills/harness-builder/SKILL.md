---
name: harness-builder
description: This skill should be used when users want to create a multi-agent harness — a coordinated system of specialized sub-agents with orchestration, quality gates, and context engineering. It transforms a project from single-skill or ad-hoc agent usage into a structured harness where CLAUDE.md orchestrates, commands define workflows, agents do specialized work, and skills provide domain knowledge. Inspired by the SAFe agentic workflow pattern.
---

# Harness Builder

Build a multi-agent harness for any project. A harness is a coordinated system where an orchestrator (CLAUDE.md) spawns specialized sub-agents via the Task tool, each with scoped responsibilities, tools, and domain knowledge. Quality gates prevent bad output from shipping.

## When to Use

- Converting a project from ad-hoc Claude usage to a structured multi-agent pipeline
- Setting up a repeatable workflow with multiple specialized roles (writer, reviewer, researcher, etc.)
- Any project where work flows through distinct phases (plan > create > review > ship)
- When context window exhaustion is a problem during complex multi-step generation

## Architecture: Three-Layer System

Every harness follows this structure:

```
project/
  CLAUDE.md                    # Layer 1: Orchestration hub
  .claude/
    commands/                  # Layer 2: User-invoked workflows
      create-thing.md
      process-input.md
    agents/                    # Layer 3a: Specialized sub-agents
      researcher.md
      creator.md
      reviewer.md
    skills/                    # Layer 3b: Domain knowledge (loaded by agents)
      voice-standard/SKILL.md
      output-template/SKILL.md
```

| Layer | Purpose | Who Reads It |
|-------|---------|-------------|
| **CLAUDE.md** | Orchestration hub — agent team, workflow phases, context rules, spawning patterns | The orchestrator (Claude in the main session) |
| **Commands** | User-invoked workflows — step-by-step pipeline for each command | The orchestrator, when user runs a command |
| **Agents** | Specialized sub-agent definitions — role, inputs, outputs, tools, rules | The sub-agent itself (NOT the orchestrator) |
| **Skills** | Domain knowledge — style guides, templates, checklists, reference data | The sub-agents that need them (NOT the orchestrator) |

## Harness Creation Process

### Step 1: Identify the Pipeline

Map out the workflow as distinct phases. Every harness has at minimum:

1. **Planning phase** — gather inputs, present plan, get user approval
2. **Creation phase** — one or more agents produce output
3. **Quality gate** — a reviewer agent validates output before shipping
4. **Output phase** — save files, report results

Ask the user:
- What does this project produce? (lessons, reports, code, designs, etc.)
- What are the input types? (ideas, files, transcripts, URLs, etc.)
- What scales does it operate at? (single item, batch, collection)
- What quality standards exist? (style guides, templates, checklists)

### Step 2: Design the Agent Team

Each agent has a single responsibility. Common agent roles:

| Role | Purpose | Typical Tools |
|------|---------|---------------|
| **Researcher** | Gathers external information | WebSearch, WebFetch, Read |
| **Creator/Writer** | Produces the primary output | Read, Write, Edit, Grep, Glob |
| **Designer** | Creates visual/presentation output | Read, Write, Edit, Grep, Glob |
| **Reviewer (QAS)** | Validates output against standards | Read, Grep, Glob (read-only) |
| **Processor** | Transforms input formats | Read, Write, Bash |
| **Packager** | Creates distribution-ready output | Read, Write |

Rules for agent design:
- Each agent has **scoped tools** — only what it needs
- The **Quality Reviewer is read-only** — it reviews but never modifies
- The Quality Reviewer is the **gate owner** — nothing ships without APPROVED
- Agents **read their own skills** from disk — the orchestrator never reads skills
- Agents **write output directly to disk** — the orchestrator never receives generated content
- Agents **return only status** — success/failure, file paths, issues

### Step 3: Design the Skills

Skills are domain knowledge that agents load when needed. Each skill is a SKILL.md file in `.claude/skills/<skill-name>/`.

Common skill types:
- **Voice/style standard** — tone, writing rules, brand guidelines
- **Output template** — structure, formatting, required sections
- **Quality checklist** — what the reviewer validates against
- **Reference data** — correction dictionaries, glossaries, schemas

Skills are NOT loaded by the orchestrator. They are loaded by agents in their "First Steps" section.

### Step 4: Design the Commands

Commands are user-invoked workflows in `.claude/commands/`. Each command orchestrates a complete pipeline.

Every command follows this pattern:
1. Gather and validate inputs
2. Create output directory
3. Present plan to user, wait for approval
4. Save plan to disk (agents read it from there)
5. Spawn agents in sequence (respecting dependencies)
6. Run quality gate
7. Handle BLOCKED status (re-spawn with issues, max 2 iterations)
8. Report results

### Step 5: Write the CLAUDE.md Orchestration Hub

CLAUDE.md is the orchestration hub. It contains:

```markdown
# [Project Name] — [Purpose] Harness

## What This Is
[One paragraph describing the harness]

## Quick Start
- `/command-1` — [description]
- `/command-2` — [description]

## The Agent Team
| Agent | Role | When to Use |
|-------|------|-------------|
| **[Agent 1]** | [role] | [when] |
| **[Reviewer]** | **GATE**: [what it validates] | Before output is finalized |

## Context Engineering (CRITICAL)

### Rules for the Orchestrator (YOU)

1. **NEVER read skill files yourself.** Skills are for agents.
2. **NEVER read agent definition files yourself.** Pass the agent file path in the Task prompt so the agent reads its own instructions.
3. **Pass file PATHS, not file CONTENTS** to agents. Tell the agent: "Read the file at `<path>`."
4. **Agents write directly to disk.** You do NOT receive generated content back.
5. **Track status, not content.** After an agent finishes, you need: (a) status, (b) file paths, (c) issues. NOT file contents.
6. **Quality Reviewer reads from disk.** Pass it the output directory path.
7. **For batch operations, generate ONE item at a time.** Each item is a separate Task call.
8. **Use max_turns on Task calls.** Creators: 25, Reviewers: 15, Researchers: 10, Processors: 10.

### How to Spawn Agents (Context-Safe Pattern)

CORRECT — agent reads its own files, writes to disk:
```
Task tool:
  subagent_type: "general-purpose"
  prompt: |
    Read your agent instructions at .claude/agents/<agent>.md
    Read the plan at <output-dir>/plan.md
    Write output to <output-dir>/<path>
    Return ONLY: status, file paths created, any issues.
```

WRONG — orchestrator reads everything and pastes it in:
```
Read .claude/agents/<agent>.md          <- wastes orchestrator context
Read .claude/skills/<skill>/SKILL.md    <- wastes orchestrator context
Task tool with all that content pasted  <- doubled context usage
```

### Spawning Template

For every agent spawn, use this template:

```
Task tool:
  description: "<3-5 word summary>"
  subagent_type: "general-purpose"
  max_turns: <limit>
  prompt: |
    You are the [Agent Name] for [Project].
    Read your full instructions at: .claude/agents/<agent>.md

    ## Your Task
    [Brief task description]

    ## Input Files (read these yourself)
    - Plan: <path>
    - [Other inputs]: <path>

    ## Output Files (write these yourself)
    - <path-to-output>

    ## Return Format
    Return ONLY:
    - Status: SUCCESS or FAILED
    - Files created: [list of paths]
    - Issues: [any problems encountered]
```

## Workflow: [Pipeline Name]

### Phase 1: Input & Planning (MANDATORY)
[Steps specific to this harness]

### Phase 2: [Creation/Processing]
[Agent spawning sequence]

### Phase 3: Quality Gate (MANDATORY)
[Quality reviewer spawning]

### Phase 4: Output
[File verification and reporting]

## Quality Gate Checklist ([Reviewer] owns this)
- [ ] [Standard 1]
- [ ] [Standard 2]

## Output Structure
```
<slug>/
  README.md
  [output directories]
```

## Skills (Domain Knowledge)
| Skill | Location | Used By |
|-------|----------|---------|

## File Reference
| What | Where |
|------|-------|
```

### Step 6: Write the Agent Definitions

Each agent file (`.claude/agents/<name>.md`) follows this structure:

```markdown
# [Agent Name] Agent

You are the [Agent Name] for [Project]. [One-sentence role description].

## First Steps (MANDATORY)

1. Read `[skill path]` — [what it contains]
2. Read the input files provided in your task prompt
Do NOT skip reading these files. Do NOT rely on summaries from the orchestrator.

## Your Inputs

You read these from disk (paths provided in your task prompt):
1. **[Input 1]** at `<path>`
2. **[Input 2]** (optional) at `<path>`

## Your Outputs

Write directly to the paths specified in your task prompt:
- `<path>` — [description]

## Return Format

Return ONLY a brief status message:
```
Status: SUCCESS
Files created:
- <path>
Issues: none
```
Do NOT return the full file contents. Write them to disk.
The orchestrator tracks paths, not content.

## [Process/Rules specific to this agent]

## Rules
- [Agent-specific constraints]

## Tools Available
- [Scoped tool list]
```

**Key patterns for agent definitions:**
- "First Steps (MANDATORY)" section — agent reads its own skills from disk
- "Return Format" section — brief status only, never full content
- "Tools Available" section — scoped list, not everything
- Self-contained — agent never depends on orchestrator having read anything

### Step 7: Write the Quality Reviewer Agent

The Quality Reviewer is special. It is the **gate owner**:

```markdown
# Quality Reviewer Agent (QAS)

You are the Quality Reviewer — the GATE OWNER for [Project].
Nothing ships without your approval.

## First Steps (MANDATORY)
1. Read [all relevant skill/standard files] — checklists
2. Read the files to review (paths provided in your task prompt)
Do NOT skip reading these files.

## Your Authority
- **GATE OWNER**: Content does not ship without your explicit "APPROVED"
- **Iteration authority**: Can bounce work back with specific, actionable issues
- **Read-only**: Review but NEVER modify content directly

## Return Format
```
## QAS REVIEW: APPROVED (or BLOCKED)
[If BLOCKED, list specific issues with file paths and line references]
[If APPROVED, one-line summary per file]
```
Do NOT return full file contents. Do NOT quote large sections.

## What You Review
### 1. [Standard Category]
- [ ] [Specific check]
- [ ] [Specific check]

## Rules
- Be SPECIFIC — "fix the style" is not acceptable; "line 42: paragraph is 6 sentences, break into 2" is
- Do NOT modify any files — read-only
- Do NOT approve work that "almost" passes

## Tools Available
- Read, Grep, Glob (read-only tools only)
```

### Step 8: Write the Command Files

Each command (`.claude/commands/<name>.md`) orchestrates a pipeline:

```markdown
# /command-name -- [Description]

[What this command does]

## Input: $ARGUMENTS

If no arguments provided, ask the user.

## Context Rules (MANDATORY)
Follow the Context Engineering rules in CLAUDE.md:
- Do NOT read agent or skill files yourself
- Pass file PATHS to agents, not contents
- Agents write to disk directly
- You track status and file paths only

## Pipeline

### Phase 1: Input & Planning
1. Identify input type
2. Create output directory
3. Present plan to user, wait for approval
4. Save plan to `<output-dir>/plan.md`

### Phase 2: [Agent Spawning]
[Spawning templates with correct max_turns]

### Phase 3: Quality Gate (MANDATORY)
[QAS spawning template with model: opus]
- If APPROVED: proceed
- If BLOCKED: re-spawn relevant agent with issues. Max 2 iterations.

### Phase 4: Output
1. Verify files exist
2. Generate index/README
3. Report results
```

### Step 9: Verify the Harness

After creating all files, verify:

1. **CLAUDE.md** contains: agent team table, context engineering rules, spawning template, workflow phases, quality checklist, file reference
2. **Each agent** has: First Steps (reads own skills), Return Format (brief status only), scoped Tools Available
3. **Each command** has: Context Rules reference, spawning templates with max_turns, quality gate phase
4. **Quality Reviewer** is: read-only, gate owner, returns APPROVED/BLOCKED
5. **No agent or skill files are read by the orchestrator** — only file paths are passed
6. **Skills are read by agents, not the orchestrator**

### Step 10: Test the Pipeline

Run the primary command end-to-end with a simple input. Verify:
- Orchestrator stays lean (no skill/agent file reads in main context)
- Each agent reads its own instructions and skills
- Agents write output to disk and return brief status
- Quality gate runs and can bounce work back
- Output files are created in the correct structure

## Context Engineering: Why It Matters

The most common failure mode for multi-agent harnesses is **context window exhaustion**. The orchestrator reads agent files, skill files, and receives full generated content back — consuming the context window before the pipeline completes.

The fix is making the orchestrator a **lean dispatcher**:

| What | Orchestrator Does | Agent Does |
|------|-------------------|------------|
| Agent instructions | Passes file path | Reads from disk |
| Skill/domain knowledge | Never touches | Reads from disk |
| Input content | Passes file path | Reads from disk |
| Generated output | Tracks file path | Writes to disk |
| Status | Receives brief status | Returns status + paths |

Every file read in the orchestrator is wasted context. The orchestrator's job is coordination, not content handling.

## Anti-Patterns

| Anti-Pattern | Why It Fails | Correct Pattern |
|-------------|-------------|----------------|
| Reading skill files in orchestrator | Wastes 200-900 lines of context per skill | Agents read their own skills |
| Pasting transcript into Task prompt | Doubles the content in context | Pass the file path |
| Agent returns full generated HTML | Fills orchestrator context with output | Agent writes to disk, returns status |
| Generating all items in one Task call | Context accumulates across items | One Task call per item |
| No max_turns on Task calls | Runaway agents consume context | Set limits: creators 25, reviewers 15, researchers 10 |
| Orchestrator reading agent .md files | Wastes context on instructions the orchestrator doesn't execute | Tell agent to read its own .md file |

## Example: Minimal Harness

A documentation harness with 3 agents:

```
project/
  CLAUDE.md                           # Orchestration: agent team, context rules, workflow
  .claude/
    commands/
      create-doc.md                   # Pipeline: plan > write > review > ship
    agents/
      doc-writer.md                   # Writes documentation from outlines
      doc-reviewer.md                 # Gate owner: validates structure, accuracy, style
      researcher.md                   # Gathers technical details from codebase/web
    skills/
      style-guide/SKILL.md           # Writing style rules (loaded by writer + reviewer)
      doc-template/SKILL.md          # Document structure template (loaded by writer + reviewer)
```

Pipeline: `/create-doc` > user provides topic > plan presented > researcher gathers info > writer creates doc > reviewer validates > output saved.
