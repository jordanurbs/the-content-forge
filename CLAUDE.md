# The Content Forge — Content Creation & Repurposing Rig

## What This Is

A multi-agent Claude Code Rig for creating and repurposing content. Transforms ideas, outlines, transcripts, and videos into platform-agnostic lessons, Slidev decks, video pre-production packages, YouTube metadata, and cross-platform social content (X threads, LinkedIn posts, blog drafts, newsletters, captioned clips).

The Rig is voice-and-brand agnostic — members configure identity, audience, voice, persona, theme, and pipeline preferences via the `/setup` wizard. All publishing integrations are independently feature-flagged via `.env`.

## Quick Start

- `/setup` — Configure your member profile, brand, voice, and pipeline preferences (run once)
- `/create-lesson` — Single lesson from any input
- `/create-section` — Section of 3-5 related lessons
- `/create-module` — Full module with multiple sections
- `/create-video` — Video pre-production (script, treatment, storyboard)
- `/lesson-to-video` — Existing lesson > unified video package
- `/package-video` — Video > transcript > lesson pipeline
- `/youtube-package` — YouTube optimization from video/transcript
- `/repurpose-lesson` — Post-production: recording + lesson dir > YouTube-ready package
- `/quick-lesson` — Lightweight transcript-to-lesson (no images, no slides, no QAS)
- `/repurpose-social` — Transcript > social media content + delivery via email/Telegram

Output lands in `output/<slug>/`. Member config lives in `config/member-profile.md`.

Every time you update the Rig infrastructure, make sure CLAUDE.md and any relevant skill/command/agent files are updated as well.

## Context Engineering (CRITICAL)

### Rules for the Orchestrator (YOU)

1. **NEVER read skill files yourself.** Skills are for agents. They live at `.claude/skills/*/SKILL.md` and are auto-loaded by the agents that need them.
2. **NEVER read agent definition files yourself.** Pass the agent file path in the Task prompt so the agent reads its own instructions. They live at `.claude/agents/*.md`.
3. **Pass file PATHS, not file CONTENTS** to agents. Tell the agent: "Read the file at `<path>` and use it as input."
4. **Agents write directly to disk.** You do NOT receive generated content back — you receive a status report (success, file paths, issues).
5. **Track status, not content.** After an agent finishes, you need: (a) status, (b) file paths written, (c) issues encountered. NOT file contents.
6. **Quality Reviewer reads from disk.** Pass it the output directory path. Never paste content into its prompt.
7. **For section-level generation (multiple lessons, multiple report sections), spawn ONE agent per artifact.** Each spawn writes one file.
8. **Use sensible `max_turns` on Task calls.** Most agents complete in 10-20 turns. Set the cap explicitly.
9. **Read `config/member-profile.md` once at pipeline start** to access member identity, audience, voice notes, and brand. Pass relevant slices to agents as needed (typically: voice notes + audience description).

### How to Spawn Agents (Context-Safe Pattern)

```
Task tool:
  subagent_type: "general-purpose"
  description: "<short imperative>"
  prompt: |
    Read your full instructions at .claude/agents/<agent>.md.

    Member profile: read config/member-profile.md for voice/audience context.

    Inputs:
    - <input file path>
    - <another input path>

    Write output to: <output file path>

    When done, return a status report with:
    - Status (success/issues)
    - Files written (paths only)
    - Any blockers or notes
```

This keeps the orchestrator's context window clean for coordination, not generation.

## Pipeline Improvement Tracking

During every pipeline run, keep a running list of improvements, procedural changes, and corrections the user instructs mid-run (e.g., "skip that step," "add this to the output," "that email should go to X instead"). Also note any friction points, workarounds, or failures encountered. After the final output phase, display the full list to the user and ask: "Want me to update the Rig to include these changes for next time?" If yes, apply the changes to the relevant command/agent/skill/CLAUDE.md files.

## The Agent Team

| Agent | Role | When to Use |
|-------|------|-------------|
| **Content Researcher** | Web research, YouTube transcripts, topic enrichment | Enriching lessons with external knowledge |
| **Lesson Writer** | Writes lesson HTML/MD in the configured creator voice | Creating lesson content |
| **Presentation Designer** | Creates Slidev slide decks | Building presentations for lessons |
| **Quality Reviewer** | **GATE**: Validates voice, structure, brand | Before any output is finalized |
| **Transcript Processor** | Transcription + correction | Processing video/audio files |
| **Image Generator** | Generates hero images via Venice AI | After content generation, before QAS |
| **YouTube Packager** | YouTube titles, descriptions, chapters, thumbnails | YouTube content optimization |
| **Script Writer** | Talking-points video scripts from any input | `/create-video` Phase 3 |
| **Script Editor** | YouTube engagement optimization (retention, hooks) | `/create-video` Phase 4 |
| **Treatment Creator** | Production document (pacing + B-roll callouts) | `/create-video` Phase 6 |
| **Storyboarder** | Shot list + Venice AI image generation | `/create-video` Phase 7 |
| **Transcript Analyzer** | Pre-process transcript into structured analysis | `/repurpose-social` Phase 3 |
| **Social Content Writer** | X threads, standalone tweets, LinkedIn posts | `/repurpose-social` Phase 4 |
| **Blog Writer** | Long-form blog posts in the configured creator voice | `/repurpose-social` Phase 4 |
| **Newsletter Writer** | Newsletter drafts (e.g. via Kit/ConvertKit) | `/repurpose-social` Phase 7.25 |

Agent definitions live in `.claude/agents/`. Each agent has specific tools and responsibilities. The orchestrator (you) spawns agents via the Task tool and coordinates the pipeline.

## Workflow: Lesson Creation Pipeline

### Phase 1: Input & Planning (MANDATORY)

1. Identify input type (idea, outline, transcript, video, collection)
2. Determine scale (lesson / section / module)
3. Present structured plan to user, wait for approval

### Phase 2: Research (optional, user-approved)

- Spawn Content Researcher for web/YouTube enrichment
- Results feed into Phase 4

### Phase 3: Transcription (if video input)

- Spawn Transcript Processor
- Applies `.corrections.json` automatically
- Produces `.clean.txt` for the Lesson Writer

### Phase 4: Content Generation

- Spawn Lesson Writer for each lesson (HTML + MD)
- Spawn Presentation Designer for each lesson (Slidev .md)
- For sections/modules: generate sequentially, cross-link

### Phase 4.5: Image Generation

- Spawn Image Generator for each lesson
- Generates hero image (lesson topic)
- Saves to `assets/` (for HTML) and `presentations/public/images/` (for Slidev)
- Hero images are deduplicated by filename (skip if file already exists)
- Requires `VENICE_API_KEY` — skipped gracefully if missing

### Phase 5: Quality Gate (MANDATORY)

- Spawn Quality Reviewer (use model: opus for this agent)
- Validates against all checklists
- Can bounce back to Phase 4 with specific issues
- Nothing ships without QAS approval
- Maximum 2 revision cycles before escalating to user

### Phase 6: Output

- Save to `<output-dir>/<topic-slug>/`
- Structure: `lessons/` for HTML/MD, `presentations/` for Slidev
- Generate README.md index
- Report what was created

## Workflow: Video Production Pipeline

### Phase 1: Input & Planning (MANDATORY)

1. Identify input type (idea, outline, transcript, lesson, video)
2. Gather: working title, target duration, visual style, audience
3. Present structured plan to user, wait for approval
4. Save plan with `visual_style` field to `<output-dir>/plan.md`

### Phase 2: Research (optional, user-approved)

- Spawn Content Researcher (same as lesson pipeline)

### Phase 2.5: Transcription (if video input)

- Spawn Transcript Processor (same as lesson pipeline)

### Phase 3: Script Writing

- Spawn Script Writer for talking-points format script
- Outputs `script.md` — NOT a teleprompter script

### Phase 4: Script Editing

- Spawn Script Editor for YouTube retention optimization
- Adds engagement markers (hooks, open loops, pattern interrupts)
- Outputs edited `script.md` + `script-editor-notes.md`

### Phase 5: Quality Gate (MANDATORY)

- Spawn Quality Reviewer (model: opus) with video-specific checklist
- Validates voice, structure, engagement architecture, timing, content
- Can bounce back to Phase 3+4 (max 2 revision cycles)

### Phase 6: Treatment Creation

- Spawn Treatment Creator (after QAS approval)
- Outputs `treatment.md` — pacing notes + B-roll callouts per section

### Phase 7: Storyboarding

- Spawn Storyboarder for shot list + Venice AI image generation
- 3-7 images typical (10 max), configurable visual style
- Outputs `storyboard/storyboard.md` + `storyboard/*.png`

### Phase 8: Output

- Verify all files exist, generate README
- Report results, suggest running `/youtube-package` after recording

## Workflow: Lesson-to-Video Pipeline

### Phase 1: Input & Planning (MANDATORY)

1. Takes: path to lesson directory (with HTML + optionally presentations/)
2. Validates lesson HTML, extracts title/M.S.L/sections/What's Next
3. Inventories Slidev slides (count + titles)
4. Presents plan, waits for approval

### Phase 2: Research (optional, user-approved)

- Same as other pipelines

### Phase 3: Script Writing

- Script Writer in LESSON-TO-VIDEO mode
- Unified script: Intro Hook + Cold Open + Intro + Core Content + Payoff + Outro/CTA
- `[SLIDE REF: N]` markers placed where Slidev slides align with content

### Phase 4: Script Editing

- Script Editor in LESSON-TO-VIDEO mode
- Preserves `[SLIDE REF: N]` markers and lesson fidelity

### Phase 5: QAS Gate #1 (MANDATORY)

- Quality Reviewer (opus) with lesson-to-video checklist
- Includes Lesson Fidelity check (core concepts, slide refs, narrative arc)

### Phase 6: Treatment Creation

- Treatment Creator in LESSON-TO-VIDEO mode
- B-roll type legend: SLIDE / GENERATED / HERO / SCREENSHARE

### Phase 7: Storyboarding

- Storyboarder generates images for GENERATED B-roll only
- Hero image copied to storyboard/ref/

### Phase 8: YouTube Packaging

- YouTube Packager in PRE-STAGING mode
- Estimated timestamps from script section durations

### Phase 9: QAS Gate #2 (MANDATORY)

- Final package check: file completeness + internal consistency

### Phase 10: Output

- Verify all files, generate README with recording guide
- Report results + build journal entry

## Build Journal (Pipeline Rule)

After the final output phase of every pipeline, the orchestrator appends a build journal entry directly to `${BUILD_JOURNAL_PATH:-./build-journal}/YYYY-MM-DD.md`. Do NOT spawn a background agent for this — write it inline. Include: what pipeline ran, how many agents, key files produced, any notable learnings or failures.

The build journal directory is configurable via the `BUILD_JOURNAL_PATH` env var (default: `./build-journal/`).

## How to Spawn Agents

Read the agent definition file, then spawn via Task tool:

```
# Example: Spawning the Lesson Writer
1. Read .claude/agents/lesson-writer.md
2. Task tool with subagent_type: "general-purpose"
3. Include: agent instructions + lesson plan + transcript + research notes
```

For the Quality Reviewer, use `model: opus` for thorough review.

## Quality Gate Checklist (QAS owns this)

- Voice: matches `.claude/skills/voice-standard/SKILL.md`
- Emoji budget: respects what's defined in voice-standard (default: max 1-2 decorative)
- HTML: No inline styles/classes/JS, all required sections present
- Sections: What You'll Get, What You'll Do, Reflect & Share, Checkpoint, What's Next
- Presentation: 10-18 slides, cover/checkpoint/what's-next
- Cross-links: "What's Next" correctly links between lessons
- Brand: audience terminology matches voice-standard
- Images: Hero image exists in both `assets/` and `presentations/public/images/`, HTML/presentation references match filenames

## Output Structure

```
output/<topic-slug>/
  README.md
  assets/
    <M.S.L>-<slug>.png              # Hero image
  lessons/
    <number>-<slug>.html
    <number>-<slug>.md
  presentations/
    [Slidev scaffold copied from harness-templates/presentations/]
    public/
      images/
        <M.S.L>-<slug>.png          # Hero image (copy)
    slides/
      <number>.md
```

## Workflow: Lesson Repurpose Pipeline

### Phase 1: Input & Planning (MANDATORY)

1. Takes: video/transcript + path to lesson directory
2. Validates lesson HTML, extracts title/M.S.L/sections/What's Next
3. Creates `youtube/` output directory inside lesson dir
4. Presents plan, waits for approval

### Phase 2: Transcription (if video input)

- Spawn Transcript Processor (same as other pipelines)

### Phase 3: Post-Production Script

- Spawn Script Writer in POST-PRODUCTION MODE (intro hook, outro/CTA, B-roll timing)
- Spawn Script Editor (retention optimization on intro/outro only)
- Outputs `post-production.md` + `script-editor-notes.md`

### Phase 4: QAS Gate #1 (MANDATORY)

- Spawn Quality Reviewer (model: opus) with post-production checklist
- Validates intro hook, outro/CTA, B-roll timing, voice
- Can bounce back to Phase 3 (max 2 revision cycles)

### Phase 5: Asset Generation (parallel where possible)

- Storyboarder generates Venice AI images for B-roll moments
- Slidev slides exported as PNGs (if presentations exist)
- Hero image copied for animation

### Phase 5.5: Asset Animation (sequential)

- broll-animator `render.sh` on storyboard + reference images
- broll-animator `render-cards.sh` generates intro.mp4 + outro.mp4 (also supports --section and --roadmap for title cards)

### Phase 6: YouTube Packaging

- YouTube Packager with BOTH transcript + lesson HTML
- Chapters aligned to lesson `<h2>` sections via fuzzy-matching

### Phase 7: QAS Gate #2 (MANDATORY)

- Final package review: file completeness, internal consistency, brand compliance

### Phase 8: Output

- Verify all files, generate README with editing guide
- Report results

## Repurpose Output Structure

```
output/<lesson-dir>/youtube/
  README.md
  plan.md
  post-production.md          # Intro hook + outro/CTA + B-roll timing table
  script-editor-notes.md      # Editor's retention reasoning
  youtube.html                # YouTube metadata
  youtube.md                  # Full metadata + thumbnail prompts
  cards/
    intro.mp4                 # Branded intro card (Remotion, ~4s)
    outro.mp4                 # Branded outro card (Remotion, ~6s)
  storyboard/
    storyboard.md             # Shot list
    *.png                     # Venice AI generated images
    ref/                      # Reference screenshots + hero
  broll/
    slides/                   # Slidev slides > PNG > animated MP4
    hero/                     # Hero image > animated MP4
    storyboard/               # Venice AI images > animated MP4
```

## Video Output Structure

```
output/<video-slug>/
  README.md
  plan.md
  research.md                    # (optional)
  script.md                      # QAS-approved talking points
  script-editor-notes.md         # Editor's retention reasoning
  treatment.md                   # Pacing + B-roll callouts
  storyboard/
    storyboard.md                # Shot list with image refs
    01-intro-hook.png
    02-concept-illustration.png
    ...
```

## Lesson-to-Video Output Structure

```
output/<topic-slug>/
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

## Workflow: Social Media Repurpose Pipeline

### Phase 1: Input & Planning (MANDATORY)

1. Takes: video file or transcript
2. Validates `.env` for Mailgun + Telegram credentials (optional integrations)
3. Creates `social/` output directory next to input
4. Presents plan, waits for approval

### Phase 2: Transcription (if video input)

- Spawn Transcript Processor (same as other pipelines)

### Phase 3: Transcript Analysis

- Spawn Transcript Analyzer
- Produces structured `analysis.md` with: topics, quotable moments, teaching points, hook angles, emotional beats, clip-worthy segments

### Phase 4: Content Generation (PARALLEL)

- Spawn Social Content Writer: X thread, standalone tweets, LinkedIn post
- Spawn Blog Writer: long-form blog post (MD + HTML)
- Spawn YouTube Packager: YouTube metadata

### Phase 5: QAS Gate (MANDATORY)

- Spawn Quality Reviewer (model: opus) with social content checklist
- Validates per-platform constraints, voice, cross-platform consistency
- Can bounce back to Phase 4 (max 2 revision cycles)

### Phase 6: Image Generation

- Orchestrator runs Venice AI image generation for thread hero, tweet images, blog hero
- Brand DNA applied from `config/image-style.md`
- Skipped gracefully if `VENICE_API_KEY` missing

### Phase 6.5: Clip Extraction with Subtitles

- Requires video file + SRT — skipped if transcript-only input
- Parse clip timecodes from `analysis.md` (Clip-Worthy Segments table)
- Cut all clips in parallel via ffmpeg with burned SRT subtitles
- Generate LinkedIn clip (recommended segment from analysis)
- If full video is under 15 minutes, also link it as `linkedin/linkedin-full.mp4`

### Phase 7: Substack Draft & Email Delivery (OPTIONAL)

- `substack-post.py`: Creates Substack draft from blog/post.md (skips if env vars missing)
- `send-email.py`: Sends outputs via Mailgun (skips gracefully if credentials missing)

### Phase 8: Telegram Delivery (OPTIONAL)

- Tweets + LinkedIn to `TELEGRAM_TWEETS_ID`
- Skips gracefully if `TELEGRAM_BOT_TOKEN` is missing

### Phase 9: Output & README

- Verify files, generate README, build journal

## Social Output Structure

```
output/<input-dir>/social/
  README.md
  plan.md
  analysis.md                    # Structured transcript analysis
  youtube.html                   # YT metadata
  youtube.md                     # Full YT metadata + thumbnail prompts
  blog/
    post.md                      # Long-form blog post
    post.html                    # HTML version
    hero.png                     # Venice AI hero image (if VENICE_API_KEY set)
    hero-prompt.md               # Prompt used
  x/
    thread.md                    # X thread (5-10 posts)
    tweets.md                    # Standalone tweets (7 short + 2 long)
    image-prompts.md             # Venice AI prompts
    thread-hero.png              # Thread hook image
    tweet-images/
      01-<slug>.png ...          # Per-tweet images
  clips/
    01-<slug>.mp4                # Clip with burned subtitles
    02-<slug>.mp4                # (from analysis.md Clip-Worthy Segments)
    ...
  linkedin/
    post.md                      # LinkedIn post
    linkedin-clip.mp4            # Recommended segment with subtitles
    linkedin-full.mp4            # Full video (if <15 min, symlink)
  newsletter/
    draft.md                     # Newsletter draft (1500-3000 words)
    draft.html                   # HTML version (for Kit, etc.)
  emails/
    yt-metadata.html
    timecodes.html
    blog-post.html
```

## Numbering Convention

`<module>.<section>.<lesson>` — e.g., 2.3.1 = Module 2, Section 3, Lesson 1.

This is the default convention; rename in your project's lesson-template skill if you prefer something else.

## Customizing for Your Project

The fastest path: run `/setup`. It walks you through every customization point interactively and writes the right files in the right places. The sections below describe what `/setup` configures and where to make manual edits later.

### Member Profile (`/setup`)

`config/member-profile.md` holds your identity, audience description, voice notes, signature phrases, publishing destinations, and pipeline defaults. Agents read it at the start of every pipeline to calibrate output.

### Voice & Tone

Define your creator voice in `.claude/skills/voice-standard/SKILL.md`. The Rig ships with a generic placeholder — see `examples/voice-standard-creator-voice.md` for a fully worked example showing the structure (signature patterns, tone checklist, transformation rules, QAS checklist).

**This is the single highest-leverage file to customize.** The Quality Reviewer agent reads it on every run.

### Persona (Optional)

If you want a recurring character to appear in lesson hero images and intro/outro video cards, define their physical description in `config/persona.md`. Image-generator and storyboarder will use it. If empty, persona-free illustrations are produced.

### Theme (Colors, Fonts, Brand Logo)

`config/theme.json` — consumed by both the Remotion broll-animator cards and the Slidev presentation scaffold. Format:

```json
{
  "colors": { "primary": "#0a0e1a", "accent": "#FFD700", "secondary": "#00FFFF" },
  "fonts": { "heading": "...", "body": "...", "mono": "..." },
  "brandLogo": "your-logo.png",
  "brandName": "Your Project"
}
```

Drop your logo into `tools/broll-animator/public/` and reference the filename in `brandLogo`.

### Visual Style for AI Image Generation

`config/image-style.md` defines the Brand DNA suffix appended to every Venice AI prompt + the negative prompt. Customize to match your aesthetic.

### Audience

`config/member-profile.md` has an Audience section. Optionally override with a separate `.audience.txt` at the project root if you want to vary audience between projects.

### Output Location

All pipelines write to `output/<slug>/`. The `output/` directory is git-ignored (only `.gitkeep` is committed) so your generated content stays private.

## Skills (Domain Knowledge)

Auto-loaded by agents as needed:

| Skill | Location | Used By |
|-------|----------|---------|
| Voice Standard | `.claude/skills/voice-standard/SKILL.md` | Lesson Writer, Quality Reviewer, Blog Writer, Newsletter Writer, Social Content Writer, Script Writer |
| Stop Slop | `.claude/skills/stop-slop/SKILL.md` | All writing agents + Quality Reviewer |
| Lesson Template | `.claude/skills/lesson-template/SKILL.md` | Lesson Writer, Quality Reviewer |
| Presentation Template | `.claude/skills/presentation-template/SKILL.md` | Presentation Designer, Quality Reviewer |
| Corrections | `.claude/skills/corrections/SKILL.md` | Transcript Processor |
| Video Script Template | `.claude/skills/video-script-template/SKILL.md` | Script Writer, Script Editor, Treatment Creator |
| Social Content | `.claude/skills/social-content/SKILL.md` | Social Content Writer, Blog Writer, Quality Reviewer |
| Newsletter Writer | `.claude/skills/newsletter-writer/SKILL.md` | Newsletter Writer |
| Harness Builder | `.claude/skills/harness-builder/SKILL.md` | Building new agents/skills inside this harness |
| Skool Publisher | `.claude/skills/skool-publisher/SKILL.md` | OPTIONAL: publishing to Skool via Camofox |

## Image Generation

Uses Venice AI `nano-banana-pro` model at 16:9 / 1K resolution. The image-generator and storyboarder agents call out to a Python script via `python3 ~/.claude/skills/venice-ai-media/scripts/venice-image.py` (an external Claude Code skill — install separately or wrap the API call directly).

Requires `VENICE_API_KEY` in `.env`. All image generation is skipped gracefully if the key is missing.

**Image types:**
- **Hero image**: One per lesson, illustrates the topic. Filename: `<M.S.L>-<slug>.png`
**Brand DNA** is read from `config/image-style.md`. **Negative prompt** is configurable in the same file.

Images are saved to both `assets/` (for lesson HTML) and `presentations/public/images/` (for Slidev). Image-generator skips regeneration if the target file already exists (deduplication by filename).

## Diagram Generation (HTML/SVG -> PNG)

For **technical concept diagrams** (architecture flows, comparison charts, protocol diagrams), use HTML/SVG rendered via Puppeteer instead of Venice AI. This gives legible text, clean arrows/boxes, and exact technical accuracy.

**Approach:**
1. Write a single `diagrams.html` with each diagram as a `<section id="diagram-NN">` at exactly 1920x1080px
2. Brand styling via CSS variables sourced from `config/theme.json`
3. Screenshot each section via Puppeteer at 1920x1080: `npm i puppeteer && node screenshot.mjs`
4. Keep `diagrams.html` + `screenshot.mjs` in the output dir for re-rendering

**When to use Venice AI vs HTML/SVG:**
- Venice AI: artistic illustrations, hero images, storyboard B-roll
- HTML/SVG: architecture diagrams, protocol flows, comparison charts, folder trees, anything with precise text labels

## Remotion Card Types

All card components live in `tools/broll-animator/src/`. Render via `render-cards.sh`. Theme colors are read from `config/theme.json` via `tools/broll-animator/src/theme.ts`. Pass `brandLogo` (filename in `tools/broll-animator/public/`) and `brandName` as props to display branding.

| Card | Component | Duration | Use Case |
|------|-----------|----------|----------|
| IntroCard | `IntroCard.tsx` | 4s (120f) | Lesson intro with logo animation |
| OutroCard | `OutroCard.tsx` | 6s (180f) | Lesson outro with next lesson tease |
| YouTubeCtaCard | `YouTubeCtaCard.tsx` | 5s (150f) | YouTube CTA for LinkedIn clips |
| SectionTitleCard | `SectionTitleCard.tsx` | 2.5s (75f) | Section marker (part label + title + subtitle) |
| RoadmapCard | `RoadmapCard.tsx` | 5s (150f) | Video structure overview (title + staggered bullet items) |

**render-cards.sh flags:**
- `--intro '{...}'` — IntroCard props
- `--outro '{...}'` — OutroCard props
- `--section '{...}' --section-output name.mp4` — SectionTitleCard (multiple allowed)
- `--roadmap '{...}' --roadmap-output name.mp4` — RoadmapCard
- `--output-dir /path` — required

**CRITICAL: Remotion v4 props.** All Compositions must have `calculateMetadata={mergeProps<T>()}` for CLI `--props` to override `defaultProps`. Without this, `--props` is silently ignored. The `mergeProps` helper is defined in Root.tsx.

## Transcription

Uses `faster-whisper` with `large-v3` model (CPU, int8 quantization).

```bash
python3 scripts/transcribe.py <video_file>
python3 scripts/transcribe.py <video_file> --model medium   # faster, less accurate
```

Corrections: `.corrections.json` in project root. Edit this file to capture transcription mistakes specific to your domain (proper nouns, technical terms, etc).

## LinkedIn Integration (Optional)

Posts LinkedIn drafts with optional trimmed video clip (intro + branded YouTube CTA card).

**Env vars** (in `.env`):
- `LINKEDIN_ACCESS_TOKEN` (required for posting)
- `LINKEDIN_PERSON_URN` (required, e.g. `urn:li:person:abc123`)
- `LINKEDIN_CLIENT_ID`, `LINKEDIN_CLIENT_SECRET`, `LINKEDIN_REFRESH_TOKEN` (optional, for auto-refresh)

**Setup:** `python3 scripts/linkedin-setup.py` — interactive OAuth flow, tests `w_member_social`, prints env vars.

**Clip generation:** `scripts/linkedin-clip.sh` trims first N seconds of video + appends YouTubeCtaCard (Remotion). Output: `linkedin-clip.mp4`.

**Posting:** `scripts/linkedin-post.py` creates a DRAFT post (not published). Supports text-only or text+video. Gracefully skips if credentials missing.

## Default Audience

If `.audience.txt` exists in this directory, its contents override the default. Otherwise the default audience is generic: content creators learning multi-agent AI workflows.

## Slidev Scaffold

The presentation scaffold lives at `harness-templates/presentations/`. When creating lesson presentations, copy the scaffold (excluding `node_modules/`) to the output directory. The scaffold includes:

- `components/` — StrategyCard, InfoCard, CalloutCard
- `layouts/` — cover, default, two-col, three-col
- `styles/base.css` — Theme (reads CSS vars; customize via `config/theme.json`)
- `uno.config.ts` — UnoCSS shortcuts

The scaffold ships without a HUD overlay. Add one in `global-top.vue` if your project wants persistent on-screen branding.

## File Reference

| What | Where |
|------|-------|
| This file (orchestration hub) | `CLAUDE.md` |
| Member profile (personal config) | `config/member-profile.md` |
| Setup wizard command | `.claude/commands/setup.md` |
| Tool permissions allowlist | `.claude/settings.local.json` |
| Pipeline output (per-run dirs) | `output/<slug>/` |
| Agent definitions | `.claude/agents/*.md` |
| Command definitions | `.claude/commands/*.md` |
| Voice standard | `.claude/skills/voice-standard/SKILL.md` |
| Stop slop (AI pattern removal) | `.claude/skills/stop-slop/SKILL.md` |
| Lesson template | `.claude/skills/lesson-template/SKILL.md` |
| Presentation template | `.claude/skills/presentation-template/SKILL.md` |
| Corrections dictionary | `.corrections.json` |
| Theme config | `config/theme.json` |
| Persona config | `config/persona.md` |
| Image style config | `config/image-style.md` |
| Transcription script | `scripts/transcribe.py` |
| Image generator agent | `.claude/agents/image-generator.md` |
| Video script template | `.claude/skills/video-script-template/SKILL.md` |
| Script writer agent | `.claude/agents/script-writer.md` |
| Script editor agent | `.claude/agents/script-editor.md` |
| Treatment creator agent | `.claude/agents/treatment-creator.md` |
| Storyboarder agent | `.claude/agents/storyboarder.md` |
| Sample lesson | `harness-templates/lessons/SAMPLE-1.0.1-your-first-lesson.{html,md}` |
| Slidev scaffold | `harness-templates/presentations/` |
| B-roll animator | `tools/broll-animator/render.sh` |
| Card renderer | `tools/broll-animator/render-cards.sh` |
| Card type schemas | `tools/broll-animator/src/card-types.ts` |
| Card theme | `tools/broll-animator/src/theme.ts` |
| Lesson-to-video command | `.claude/commands/lesson-to-video.md` |
| Repurpose command | `.claude/commands/repurpose-lesson.md` |
| Social repurpose command | `.claude/commands/repurpose-social.md` |
| Transcript analyzer agent | `.claude/agents/transcript-analyzer.md` |
| Social content writer agent | `.claude/agents/social-content-writer.md` |
| Blog writer agent | `.claude/agents/blog-writer.md` |
| Newsletter writer agent | `.claude/agents/newsletter-writer.md` |
| Newsletter writer skill | `.claude/skills/newsletter-writer/SKILL.md` |
| Email sender script | `scripts/send-email.py` |
| Telegram notify script | `scripts/telegram-notify.py` |
| Substack poster script | `scripts/substack-post.py` |
| LinkedIn post script | `scripts/linkedin-post.py` |
| LinkedIn clip script | `scripts/linkedin-clip.sh` |
| LinkedIn OAuth setup | `scripts/linkedin-setup.py` |

## Acknowledgments

- Built on Claude Code's multi-agent harness pattern.
- Stop-slop skill: original work MIT by Hardik Pandya (https://github.com/hardikpandya/stop-slop).
- Forked from the AICA Lessons harness used by AI Captains Academy.
