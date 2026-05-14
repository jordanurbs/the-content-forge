# The Content Forge

A Claude Code **Rig** that turns ideas, outlines, transcripts, and videos into a full content pipeline: lessons (HTML + Slidev decks), video pre-production packages (script + treatment + storyboard), YouTube metadata, and cross-platform social repurposing (X threads, LinkedIn posts, blog drafts, newsletters, captioned clips).

15 specialized sub-agents, 11 slash commands, a Quality Reviewer gate before every output, and 8 optional publishing integrations. Voice, brand, persona, and audience are all member-configurable — the Rig ships with a generic template and you make it yours via `/setup`.

**The "create once, repurpose everywhere" motion.** Record one video. Run `/repurpose-social`. Walk away with: a YouTube package (title + chapters + description + thumbnail prompts), 7-9 standalone tweets, a 5-10 post X thread, a LinkedIn post + 60-second captioned clip, a 1500-word blog post, a 2000-word newsletter draft, and email/Telegram delivery of every artifact. Pipeline takes ~10-15 minutes; replaces a full editorial workflow.

## Requirements

- [Claude Code](https://docs.anthropic.com/en/docs/claude-code) CLI installed and configured
- Python 3.10+ (for transcription, email, Telegram, LinkedIn scripts)
- Node 20+ (for Slidev scaffold and Remotion broll-animator)
- `ffmpeg` (for clip extraction with burned subtitles)
- Optional: `faster-whisper`, `puppeteer`, [Camofox](https://github.com/camoufox/camoufox) (for Skool publishing), the `venice-ai-media` Claude Code skill

## Setup

1. **Clone this repo**
   ```bash
   git clone <your-fork-url> the-content-forge
   cd the-content-forge
   ```

2. **Open the directory in Claude Code**
   ```bash
   claude
   ```

3. **Run the setup wizard**
   ```
   /setup
   ```
   Walks you through configuring your identity, audience, voice, brand, persona (optional), visual style, publishing destinations, and pipeline preferences. Writes to `config/member-profile.md`, `config/theme.json`, `config/persona.md`, and `config/image-style.md`. Takes 5-10 minutes.

4. **Configure integrations** (optional — all are independently feature-flagged)
   ```bash
   cp .env.example .env
   # Edit .env and fill in only the services you want to use
   ```

5. **Install Node + Python deps if you'll use them**
   ```bash
   ./setup.sh  # one-shot installer
   ```

6. **You're ready.** Pick a pipeline from the table below.

## Usage

| Command | What It Does | Input |
|---------|--------------|-------|
| `/setup` | Configure member profile, brand, voice | — (interactive) |
| `/create-lesson` | Single lesson from any input | idea / outline / transcript / video |
| `/create-section` | Section of 3-5 related lessons | section plan |
| `/create-module` | Full module (multiple sections) | module outline |
| `/create-video` | Video pre-production package | idea / outline / transcript / lesson |
| `/lesson-to-video` | Lesson → unified video package | existing lesson directory |
| `/package-video` | Video → transcript → lesson | video file |
| `/youtube-package` | YouTube optimization | video / transcript |
| `/repurpose-lesson` | Post-production for an existing lesson | recording + lesson dir |
| `/quick-lesson` | Lightweight transcript-to-lesson (no images/slides/QAS) | transcript |
| `/repurpose-social` | Transcript → X, LinkedIn, blog, newsletter, clips | video / transcript |

Output lands in `output/<slug>/`.

Every pipeline gates on a **Quality Reviewer** agent (`model: opus`) before producing final output. The reviewer reads your voice-standard skill and validates structure, brand compliance, and AI-slop patterns.

## What You Get

Per pipeline, the output structure varies — see `CLAUDE.md` for full layouts. As an example, a single lesson produces:

```
output/<topic-slug>/
  README.md                          # Index + delivery notes
  assets/
    <M.S.L>-<slug>.png               # Hero image (Venice AI)
    health-break-<exercise>.png      # Health break illustration
  lessons/
    <number>-<slug>.html             # Lesson HTML
    <number>-<slug>.md               # Lesson markdown
  presentations/
    [full Slidev scaffold copied + themed]
    slides/<number>.md               # 10-18 slides per lesson
```

And a `/repurpose-social` run produces:

```
output/social/
  analysis.md                        # Structured transcript analysis
  youtube.html + youtube.md          # YouTube metadata
  blog/post.md + hero.png            # Blog draft + AI hero image
  x/thread.md + tweets.md + images/  # X thread + standalone tweets
  linkedin/post.md + clip.mp4        # LinkedIn post + 60s captioned clip
  newsletter/draft.{md,html}         # Newsletter draft (ready for Kit/etc)
  clips/01-*.mp4 ... 05-*.mp4        # Highlight clips with burned subtitles
  emails/                            # Pre-formatted email outputs for delivery
```

## How the Workflow Feels

You start a pipeline. The orchestrator presents a plan and asks for approval. You approve. It spawns agents in parallel where possible, sequentially where they depend on each other. Each agent writes directly to disk — you see status updates as files land. The Quality Reviewer gates the final output and bounces back up to 2 revision cycles if it finds issues.

You can interrupt mid-run to redirect: "skip that step," "send the email to X instead," "add a section about Y." The orchestrator notes these improvements and offers to apply them to the Rig itself at the end.

You finish with a `output/<slug>/` directory full of deliverables. Take what works, edit what doesn't, publish.

## Customizing for Your Brand

The Rig is **brand-agnostic out of the box**. The `/setup` wizard does the heavy lifting, but you can also edit these files directly anytime:

| File | What It Controls |
|------|------------------|
| `config/member-profile.md` | Identity, audience, signature phrases, pipeline preferences |
| `config/theme.json` | Brand colors, fonts, logo filename, brand name (consumed by Slidev + Remotion cards) |
| `config/persona.md` | Optional recurring character (for hero/health-break images + intro/outro cards). Leave empty for persona-free output. |
| `config/image-style.md` | Venice AI Brand DNA prompt + negative prompt |
| `.audience.txt` | Target audience paragraph (optional override; falls back to `member-profile.md`) |
| `.claude/skills/voice-standard/SKILL.md` | **The big one.** Defines your voice — signature patterns, tone checklist, transformation rules, QAS checklist. The harness ships with a minimal generic version. See `examples/voice-standard-creator-voice.md` for a worked example. |
| `.corrections.json` | Transcription term corrections (proper nouns, technical terms specific to your domain) |

The Quality Reviewer agent (`.claude/agents/quality-reviewer.md`) reads `voice-standard/SKILL.md` to validate every output. Customizing it is the single highest-leverage thing you can do to make the Rig produce content that sounds like *you*.

## Optional Integrations

Each integration activates only when its env vars are set. Missing credentials = that step is skipped gracefully.

| Service | Env Vars | Used By |
|---------|----------|---------|
| Venice AI | `VENICE_API_KEY` | Image generation (hero, health break, storyboard) |
| Mailgun | `MAILGUN_API_KEY` | Email delivery of outputs |
| Telegram | `TELEGRAM_BOT_TOKEN` | Push notifications |
| LinkedIn | `LINKEDIN_ACCESS_TOKEN` | Draft post creation with clip |
| Kit / ConvertKit | `KIT_API_KEY` | Newsletter draft push |
| Substack | `SUBSTACK_*` | Blog draft push (cookie auth) |
| Skool | `CAMOFOX_API_KEY` + `SKOOL_COURSE_URL` | Course publishing |
| Google Drive | `GOOGLE_SERVICE_ACCOUNT_KEY_PATH` | File uploads |

See `.env.example` for the full list and where to get keys.

## Anatomy of This Rig

Every Rig has the same three folders. Once you've seen one, you've seen them all:

- **`.claude/`** — The brain. Agents (specialized sub-agents), commands (the slash commands you run), skills (domain expertise), and `settings.local.json` (tool permissions).
- **`config/`** — Personalization. Member profile, theme, persona, image style.
- **`output/`** — Where deliverables land. Empty until you run a pipeline.

Plus the harness-specific scaffolding:

- **`harness-templates/`** — Slidev presentation scaffold + sample lesson template (copied into `output/` per pipeline run).
- **`tools/broll-animator/`** — Remotion v4 project for intro/outro/CTA video cards.
- **`scripts/`** — Helper scripts (transcription, email, Telegram, LinkedIn, Substack, Skool).
- **`examples/`** — Reference examples (voice standard, audience, populated .env).

## Commands Reference

| Command | What it does |
|---------|-------------|
| `/setup` | Configure member profile, brand, voice |
| `/create-lesson` | Single lesson |
| `/create-section` | Section (3-5 lessons) |
| `/create-module` | Full module |
| `/create-video` | Video pre-production |
| `/lesson-to-video` | Lesson → video package |
| `/package-video` | Video → lesson |
| `/youtube-package` | YouTube metadata |
| `/repurpose-lesson` | Post-production for a lesson |
| `/quick-lesson` | Lightweight transcript-to-lesson |
| `/repurpose-social` | Cross-platform social repurposing |

## License

MIT. See [LICENSE](LICENSE).

This Rig is **yours.** Fork it, modify it, sell with it. The MIT license is permissive — just keep the license file in there.

## Acknowledgments

- Built on the [Claude Code](https://claude.com/claude-code) multi-agent harness pattern.
- The `stop-slop` skill incorporates [Hardik Pandya's stop-slop](https://github.com/hardikpandya/stop-slop) (MIT).
- Inspired by the safe-agentic-workflow pattern by Bybren LLC.
- Forked from the AICA Lessons harness used by [AI Captains Academy](https://aicaptains.academy).
