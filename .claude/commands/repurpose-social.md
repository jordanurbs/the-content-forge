# /repurpose-social — Social Media Content Repurposing Pipeline

Repurpose a video transcript into a full social media content package: X threads, standalone tweets, LinkedIn post, Substack blog, YouTube metadata, branded images — delivered via email and Telegram.

## Input: $ARGUMENTS

If no arguments provided, ask the user for:
1. Path to the video file or transcript
2. (Optional) Working title for the content

## Context Rules (MANDATORY)

Follow the Context Engineering rules in CLAUDE.md:
- Do NOT read agent or skill files yourself
- Pass file PATHS to agents, not contents
- Agents write to disk directly
- You track status and file paths only

## Pipeline

### Phase 1: Input & Planning (MANDATORY)

1. **Identify inputs:**
   - Video file (.mp4, .mov, etc.) OR transcript (.txt, .clean.txt, .srt)
   - Optional: working title, target audience override

2. **Validate environment:**
   - Check `.env` exists and has: `MAILGUN_API_KEY`, `MAILGUN_DOMAIN`, `EMAIL_FROM`, `TELEGRAM_BOT_TOKEN`, `TELEGRAM_TWEETS_ID`, `SUBSTACK_EMAIL`, `SUBSTACK_PASSWORD`, `SUBSTACK_PUBLICATION_URL`
   - Check `EMAIL_YT_STRATEGIST` and `EMAIL_VIDEO_EDITOR` exist for email routing
   - Check `LINKEDIN_ACCESS_TOKEN` and `LINKEDIN_PERSON_URN` for LinkedIn posting (warn if missing — clip still generated, post sent via Telegram for manual copy-paste)
   - Check `KIT_API_KEY` in `.claude/skills/newsletter-writer/.env` for Kit newsletter push (warn if missing — draft still written to disk)
   - Warn (don't block) if any are missing — pipeline can still generate content
   - **CRITICAL: Strip quotes from `.env` values when reading via bash.** `.env` may have values like `EMAIL_YT_STRATEGIST="addr@example.com"` — bash `cut -d=` does NOT strip the surrounding quotes. Either:
     - Read env via Python (the delivery scripts do this correctly), OR
     - Pipe through `tr -d '"\''`, OR
     - Pass the literal address directly when known
   - **If `EMAIL_VIDEO_EDITOR` is empty**, fall back to sending timecodes to `EMAIL_FROM` or `${DEFAULT_RECIPIENT_EMAIL:-creator@example.com}` with `--cc ""` to override the env CC.

3. **Locate video file for clip extraction:**
   - If input is a video file: use it directly
   - If input is a transcript (.srt, .txt): look for matching .mp4/.mov in the same directory
   - Store as `<video-path>` (or null if no video found — clips will be skipped)

4. **Create output directories:**
   ```
   <input-dir>/social/
   <input-dir>/social/x/
   <input-dir>/social/x/tweet-images/
   <input-dir>/social/linkedin/
   <input-dir>/social/blog/
   <input-dir>/social/emails/
   <input-dir>/social/clips/
   <input-dir>/social/newsletter/
   ```

4. **Present plan to user:**
   ```
   ## Social Repurpose Plan

   - Source: [video/transcript path]
   - Title: [working title or derived from transcript]
   - Output: <input-dir>/social/
   - Audience: [from .audience.txt or default]

   ## What will be generated:
   1. Transcript analysis (topics, quotes, hooks, clips)
   2. X thread (5-10 tweets)
   3. Standalone tweets (7 short + 2 long with images)
   4. LinkedIn post with clip recommendation
   5. Substack blog post (MD + HTML + hero image)
   6. YouTube metadata (headlines, description, chapters, thumbnails)
   7. Branded Venice AI images (thread hero, tweet images, blog hero)
   8. Video clips with burned subtitles (from clip-worthy segments)
   9. LinkedIn clip (recommended segment or full video if <15 min)
   10. Kit newsletter draft (longer-form, pushed via API)
   11. Email delivery: YT metadata, timecodes, blog post
   12. Telegram delivery: tweets, LinkedIn, YT metadata, summary

   ## Delivery routing:
   - Tweets + LinkedIn + summary -> Telegram (TELEGRAM_TWEETS_ID) — tweets only, no YT metadata
   - Blog post -> Substack draft (preferred) OR Email (EMAIL_FROM) fallback
   - Clip timecodes -> Email (EMAIL_VIDEO_EDITOR; falls back to EMAIL_FROM if empty)
   - YT metadata -> Email (EMAIL_YT_STRATEGIST)
   ```
   **Wait for user approval before proceeding.**

5. **Save plan:**
   Write the plan to `<input-dir>/social/plan.md`

### Phase 2: Transcription (if video input)

Only if input is a video file (not a transcript). Spawn Transcript Processor:
```
Task tool:
  description: "Transcribe video for social repurposing"
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

### Phase 3: Transcript Analysis

Spawn Transcript Analyzer:
```
Task tool:
  description: "Analyze transcript for social content"
  subagent_type: "general-purpose"
  max_turns: 15
  prompt: |
    You are the Transcript Analyzer for {{PROJECT_NAME}}.
    Read your instructions at: .claude/agents/transcript-analyzer.md

    ## Task
    Analyze transcript for social media repurposing.

    ## Input Files (read these yourself)
    - Transcript: <transcript-path>
    - Plan: <input-dir>/social/plan.md
    - Audience: .audience.txt (if it exists, otherwise use default)

    ## Output Files (write these yourself)
    - <input-dir>/social/analysis.md

    ## CRITICAL FALLBACK
    If your Write tool is blocked by the sandbox, return ALL output file contents inline in your final message, clearly delimited with `===== FILE: <path> =====` markers, so the orchestrator can write them to disk. Otherwise write directly.

    ## Return Format
    Return ONLY: status, file path, quotable moments count, teaching points count. (Plus inline file contents if Write was blocked.)
```

### Phase 4: Content Generation (PARALLEL)

Spawn these three agents in parallel:

**4A: Social Content Writer**
```
Task tool:
  description: "Write X threads, tweets, LinkedIn post"
  subagent_type: "general-purpose"
  max_turns: 25
  prompt: |
    You are the Social Content Writer for {{PROJECT_NAME}}.
    Read your instructions at: .claude/agents/social-content-writer.md

    ## Task
    Create social media content from the transcript analysis.

    ## Input Files (read these yourself)
    - Analysis: <input-dir>/social/analysis.md
    - Plan: <input-dir>/social/plan.md

    ## Output Files (write these yourself)
    - <input-dir>/social/x/thread.md
    - <input-dir>/social/x/tweets.md
    - <input-dir>/social/x/image-prompts.md
    - <input-dir>/social/linkedin/post.md

    ## Return Format
    Return ONLY: status, file paths, thread count, tweet count, LinkedIn chars.
```

**4B: Blog Writer**
```
Task tool:
  description: "Write Substack blog post"
  subagent_type: "general-purpose"
  max_turns: 25
  prompt: |
    You are the Blog Writer for {{PROJECT_NAME}}.
    Read your instructions at: .claude/agents/blog-writer.md

    ## Task
    Create a Substack blog post from the transcript analysis.

    ## Input Files (read these yourself)
    - Analysis: <input-dir>/social/analysis.md
    - Plan: <input-dir>/social/plan.md
    - Transcript: <transcript-path>

    ## Output Files (write these yourself)
    - <input-dir>/social/blog/post.md
    - <input-dir>/social/blog/post.html
    - <input-dir>/social/blog/hero-prompt.md

    ## Return Format
    Return ONLY: status, file paths, word count, section count.
```

**4C: YouTube Packager** (existing agent)
```
Task tool:
  description: "Generate YouTube metadata"
  subagent_type: "general-purpose"
  max_turns: 15
  prompt: |
    You are the YouTube Packager for {{PROJECT_NAME}}.
    Read your instructions at: .claude/agents/youtube-packager.md

    ## Task
    Generate YouTube optimization content.

    ## Input Files (read these yourself)
    - Transcript: <transcript-path>
    - Audience: .audience.txt (if it exists, otherwise use default)

    ## Output Files (write these yourself)
    - <input-dir>/social/youtube.html
    - <input-dir>/social/youtube.md

    ## Return Format
    Return ONLY: status, file paths, best headline.
```

### Phase 5: QAS Gate (MANDATORY)

Spawn Quality Reviewer with SOCIAL CONTENT checklist:
```
Task tool:
  description: "QAS review social content package"
  subagent_type: "general-purpose"
  model: opus
  max_turns: 15
  prompt: |
    You are the Quality Reviewer (QAS) for {{PROJECT_NAME}}.
    Read your instructions at: .claude/agents/quality-reviewer.md

    ## Task
    Review the complete social content package.

    ## Files to Review
    - X thread: <input-dir>/social/x/thread.md
    - Standalone tweets: <input-dir>/social/x/tweets.md
    - LinkedIn post: <input-dir>/social/linkedin/post.md
    - Blog post (MD): <input-dir>/social/blog/post.md
    - Blog post (HTML): <input-dir>/social/blog/post.html
    - YouTube metadata: <input-dir>/social/youtube.html
    - Image prompts: <input-dir>/social/x/image-prompts.md

    ## SOCIAL CONTENT CHECKLIST (use this instead of the lesson/video checklist)

    ### X Thread
    - [ ] Hook has curiosity gap + specific number
    - [ ] 5-10 tweets total
    - [ ] Each tweet <=280 chars — **MANDATORY: count via `python3 -c "print(len(open('thread.md').read()))"` or equivalent. Do NOT trust the `<!-- Char count: NNN -->` comment in the file. Report the count YOU computed for any flagged tweet.**
    - [ ] Closer has single CTA + engagement question
    - [ ] defined voice (see config/voice.md)
    - [ ] At least one failure/struggle tweet
    - [ ] At least one standalone-worthy tweet

    ### Standalone Tweets
    - [ ] 7 short (<200 chars) + 2 long (200-280 chars) — **MANDATORY: programmatic char count required, do NOT rely on the `Chars:` metadata line. If the bucket distribution looks wrong, count each tweet body yourself.**
    - [ ] Mix of formulas (hot takes, observations, fragments, mini-stories)
    - [ ] Specific numbers in every tweet
    - [ ] No generic advice
    - [ ] Max 3 hashtags per tweet

    ### LinkedIn
    - [ ] Story-led opening (first 210 chars hook)
    - [ ] 1200-1800 chars total
    - [ ] Peer-to-peer, no hard CTA
    - [ ] Max 5 hashtags at bottom
    - [ ] Engagement question at end
    - [ ] Clip recommendation with timecode

    ### Blog
    - [ ] Headline not clickbait, 50-80 chars
    - [ ] Hook in first 3 sentences with specific detail
    - [ ] 3-5 sections with embedded quotes
    - [ ] At least one failure story
    - [ ] Actionable takeaway (3-5 bullet points)
    - [ ] 800-1500 words
    - [ ] Clean HTML (no inline styles/classes/JS)

    ### YouTube
    - [ ] Headlines accurate, not misleading
    - [ ] Chapters timestamped from transcript
    - [ ] Description has value prop
    - [ ] Thumbnail prompts include brand DNA

    ### Cross-Platform
    - [ ] Same core insights across all formats
    - [ ] No contradictions between platforms
    - [ ] Image prompts include brand DNA (synthwave, nautical, cyberpunk)
    - [ ] Voice consistent: consistent voice across all content

    ## Return Format
    Return: APPROVED or BLOCKED with specific issues per platform.
```

- **If APPROVED:** proceed to Phase 6
- **If BLOCKED:** identify which agent(s) need revision. Re-spawn only the affected agent(s) with the specific issues. Max 2 revision cycles before escalating to user.

### Phase 6: Image Generation

Generate branded images using Venice AI. The orchestrator runs these directly:

**NOTE:** `venice-image.py` uses `--out-dir` (not `--output`) and auto-generates filenames from the prompt. After each generation, rename the output file to the standard name.

1. **Thread hero image**: Read the prompt from `<input-dir>/social/x/image-prompts.md` (Thread Hero section)
   ```bash
   python3 ~/.claude/skills/venice-ai-media/scripts/venice-image.py --prompt "<prompt>" --negative-prompt "<negative>" --width 1200 --height 675 --format png --out-dir <input-dir>/social/x/
   mv <input-dir>/social/x/001-*.png <input-dir>/social/x/thread-hero.png
   ```

2. **Blog hero image**: Read the prompt from `<input-dir>/social/blog/hero-prompt.md`
   ```bash
   python3 ~/.claude/skills/venice-ai-media/scripts/venice-image.py --prompt "<prompt>" --negative-prompt "<negative>" --width 1200 --height 675 --format png --out-dir <input-dir>/social/blog/
   mv <input-dir>/social/blog/001-*.png <input-dir>/social/blog/hero.png
   ```

3. **Tweet images**: For each tweet with an image prompt in `<input-dir>/social/x/image-prompts.md`:
   ```bash
   python3 ~/.claude/skills/venice-ai-media/scripts/venice-image.py --prompt "<prompt>" --negative-prompt "<negative>" --width 1200 --height 675 --format png --out-dir <input-dir>/social/x/tweet-images/
   mv <input-dir>/social/x/tweet-images/001-*.png <input-dir>/social/x/tweet-images/<NN>-<slug>.png
   ```

Run all image generations in parallel (background), then rename after all complete. Clean up any `index.html` or `prompts.json` files left by venice-image.py.

### Phase 6.5: Clip Extraction with Subtitles

**Requires:** A video file (`<video-path>`) AND an SRT/transcript file. Skip this entire phase if no video file is available.

1. **Parse clip timecodes** from `<input-dir>/social/analysis.md` (Clip-Worthy Segments table). Each row has: Start, End, Duration, Description, Best For.

2. **CRITICAL: Symlink source files to a space-free path.** ffmpeg's `subtitles=` filter chokes on spaces in paths. Always create symlinks first:
   ```bash
   mkdir -p /tmp/clips-<slug>
   ln -sf "<video-path>" /tmp/clips-<slug>/source.mp4
   ln -sf "<srt-path>" /tmp/clips-<slug>/subs.srt
   ```
   Then `cd /tmp/clips-<slug>` before running ffmpeg, and reference `source.mp4` / `subs.srt`.

3. **Cut clips with burned subtitles** using ffmpeg. Run all clips in parallel (background):
   ```bash
   cd /tmp/clips-<slug> && ffmpeg -y -ss <start> -to <end> -i source.mp4 \
     -vf "subtitles=subs.srt:force_style='FontName=Arial,FontSize=24,PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,Outline=2,MarginV=30'" \
     -c:v libx264 -preset fast -crf 23 -c:a aac -b:a 128k \
     "<input-dir>/social/clips/<NN>-<slug>.mp4"
   ```
   Name clips sequentially: `01-<slug>.mp4`, `02-<slug>.mp4`, etc. Derive slug from the Description column (lowercase, hyphens, max 30 chars).

4. **Generate LinkedIn clip:**
   - Read the "Best LinkedIn Clip Recommendation" from `analysis.md` for the recommended timecode
   - If the full video is **under 15 minutes**, also copy/symlink the full video as `linkedin/linkedin-full.mp4` (LinkedIn's max is 15 min)
   - Always cut the recommended segment as `linkedin/linkedin-clip.mp4` (for a focused option)
   ```bash
   cd /tmp/clips-<slug> && ffmpeg -y -ss <start> -to <end> -i source.mp4 \
     -vf "subtitles=subs.srt:force_style='FontName=Arial,FontSize=24,PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,Outline=2,MarginV=30'" \
     -c:v libx264 -preset fast -crf 23 -c:a aac -b:a 128k \
     "<input-dir>/social/linkedin/linkedin-clip.mp4"
   ```

5. **Verify clips exist** after all background tasks complete. Report count and total duration. Cleanup `/tmp/clips-<slug>/` after verification.

### Phase 7: Substack Draft & Email Delivery

Prepare and send emails. Create HTML email files first, then send via Mailgun:

1. **YT metadata to strategist:**
   - Create `<input-dir>/social/emails/yt-metadata.html` from youtube.html content
   - ```bash
     python3 scripts/send-email.py --to "$EMAIL_YT_STRATEGIST" --subject "YT Metadata: [Title]" --html-file <input-dir>/social/emails/yt-metadata.html
     ```

2. **Clip timecodes to video editor:**
   - Create `<input-dir>/social/emails/timecodes.html` with clip-worthy segments from analysis.md + LinkedIn clip recommendation
   - ```bash
     python3 scripts/send-email.py --to "$EMAIL_VIDEO_EDITOR" --subject "Clip Timecodes: [Title]" --html-file <input-dir>/social/emails/timecodes.html
     ```

3. **Blog post to Substack (preferred) or Email (fallback):**
   - First, attempt Substack draft:
     ```bash
     python3 scripts/substack-post.py \
       --md-file <input-dir>/social/blog/post.md \
       --title "[Blog Title]" \
       --subtitle "[subtitle from analysis]" \
       --hero-image <input-dir>/social/blog/hero.png
     ```
   - Capture stdout. If Status: SUCCESS, record the draft URL. Skip email.
   - If Status: SKIPPED or FAILURE, fall back to email:
     ```bash
     python3 scripts/send-email.py --to "$EMAIL_FROM" --cc "" \
       --subject "Blog Draft: [Title]" \
       --html-file <input-dir>/social/emails/blog-post.html
     ```

Skip any email where the recipient env var is missing (warn, don't fail).

### Phase 7.25: Kit Newsletter Draft

Spawn the Newsletter Writer to create a longer-form newsletter from the blog content and push it to Kit as a draft:

```
Task tool:
  description: "Write newsletter and push to Kit"
  subagent_type: "general-purpose"
  max_turns: 20
  prompt: |
    You are the Newsletter Writer for {{PROJECT_NAME}}.
    Read your instructions at: .claude/agents/newsletter-writer.md

    ## Task
    Write a Kit newsletter from the social content package and push it as a draft.

    ## Input Files (read these yourself)
    - Blog post: <input-dir>/social/blog/post.md
    - Analysis: <input-dir>/social/analysis.md
    - Plan: <input-dir>/social/plan.md
    - Transcript: <transcript-path>

    ## Output Files (write these yourself)
    - <input-dir>/social/newsletter/draft.md
    - <input-dir>/social/newsletter/draft.html

    ## After writing, push to Kit using:
    bash .claude/skills/newsletter-writer/scripts/push-to-kit.sh "<subject>" <input-dir>/social/newsletter/draft.html

    ## Return Format
    Return ONLY: status, file paths, Kit broadcast ID (or error), word count, subject line used.
```

Record the Kit broadcast ID (or skip/failure status) for the README delivery table.

### Phase 7.5: LinkedIn Draft Posting

1. **Check prerequisites:** If `LINKEDIN_ACCESS_TOKEN` and `LINKEDIN_PERSON_URN` are missing, skip this phase (warn, don't block).

2. **Generate LinkedIn clip** (if source video exists):
   ```bash
   bash scripts/linkedin-clip.sh \
     --input <source-video-path> \
     --duration 180 \
     --title "[Video Title]" \
     --output-dir <input-dir>/social/linkedin/
   ```
   If no source video (transcript-only input), skip clip generation.

3. **Post LinkedIn draft:**
   ```bash
   python3 scripts/linkedin-post.py \
     --post-file <input-dir>/social/linkedin/post.md \
     --video-file <input-dir>/social/linkedin/linkedin-clip.mp4  # only if clip exists
   ```

4. **Record result** for README delivery table:
   - `Status: SUCCESS` → record as "Draft created"
   - `Status: SKIPPED` → record as "Skipped (no credentials)"
   - `Status: FAILURE` → record as "Failed ([reason])" — pipeline continues

### Phase 8: Telegram Delivery (Tweets Only)

Send tweets-and-LinkedIn to Telegram TWEETS_ID for easy copy-paste. **Do NOT send YouTube metadata to Telegram** — YT description / chapters / tags are delivered via email only (Phase 7).

**To TELEGRAM_TWEETS_ID:**
1. Thread (each tweet as a separate message, numbered):
   ```bash
   python3 scripts/telegram-notify.py --chat-id "$TELEGRAM_TWEETS_ID" --message "THREAD 1/N: [tweet text]"
   ```
2. Each standalone tweet as a separate message:
   ```bash
   python3 scripts/telegram-notify.py --chat-id "$TELEGRAM_TWEETS_ID" --message "TWEET: [tweet text]"
   ```
3. LinkedIn post:
   ```bash
   python3 scripts/telegram-notify.py --chat-id "$TELEGRAM_TWEETS_ID" --message "LINKEDIN:\n\n[post text]"
   ```
4. Pipeline summary (final message in the same chat):
   ```bash
   python3 scripts/telegram-notify.py --chat-id "$TELEGRAM_TWEETS_ID" --message "SOCIAL REPURPOSE COMPLETE\n\nTitle: [title]\nThread: [N] tweets\nStandalone: 9 tweets\nLinkedIn: [chars] chars\nLinkedIn Draft: [created/skipped/failed]\nBlog: [words] words\nNewsletter: [words] words (Kit ID: [id]/skipped/failed)\nYouTube: [headlines] headlines\nImages: [N] generated\nEmails: [N] sent"
   ```

**Implementation note:** Build a small Python script in `scripts/` that loads `.env` (strips quotes), parses thread.md / tweets.md / linkedin/post.md, and sends each message via `telegram-notify.py`. **Do not write the script to `/tmp/`** — sandbox blocks execution from `/tmp/`. Place it in `scripts/` (delete after the run if it's run-specific).

Skip Telegram delivery if `TELEGRAM_BOT_TOKEN` is missing (warn, don't fail).

### Phase 9: Output & README

1. **Verify all expected files exist** (use Glob):
   - `<input-dir>/social/plan.md`
   - `<input-dir>/social/analysis.md`
   - `<input-dir>/social/x/thread.md`
   - `<input-dir>/social/x/tweets.md`
   - `<input-dir>/social/x/image-prompts.md`
   - `<input-dir>/social/x/thread-hero.png`
   - `<input-dir>/social/x/tweet-images/*.png`
   - `<input-dir>/social/linkedin/post.md`
   - `<input-dir>/social/linkedin/linkedin-clip.mp4` (if source video existed)
   - `<input-dir>/social/clips/*.mp4` (if source video existed)
   - `<input-dir>/social/blog/post.md`
   - `<input-dir>/social/blog/post.html`
   - `<input-dir>/social/blog/hero.png`
   - `<input-dir>/social/youtube.html`
   - `<input-dir>/social/youtube.md`
   - `<input-dir>/social/newsletter/draft.md`
   - `<input-dir>/social/newsletter/draft.html`

2. **Generate README.md** (write this yourself):
   ```markdown
   # [Title] — Social Repurpose Package

   **Source:** [transcript/video path]
   **Generated:** [date]

   ## Content

   | Platform | File | Status |
   |----------|------|--------|
   | X Thread | `x/thread.md` | [N] tweets |
   | X Standalone | `x/tweets.md` | 7 short + 2 long |
   | X Images | `x/thread-hero.png`, `x/tweet-images/` | [N] images |
   | LinkedIn | `linkedin/post.md` | [chars] chars |
   | Blog (MD) | `blog/post.md` | [words] words |
   | Blog (HTML) | `blog/post.html` | Ready for Substack |
   | Blog Hero | `blog/hero.png` | Generated |
   | YouTube | `youtube.html` / `youtube.md` | [N] headlines |
   | Newsletter | `newsletter/draft.md` / `draft.html` | [words] words |

   ## Delivery

   | Content | Destination | Status |
   |---------|-------------|--------|
   | Tweets + LinkedIn | Telegram (TWEETS) | [sent/skipped] |
   | YT metadata | Telegram (NOTIFICATIONS) | [sent/skipped] |
   | LinkedIn Draft | LinkedIn | [draft created / skipped / failed] |
   | LinkedIn Clip | `linkedin/linkedin-clip.mp4` | [generated / skipped (no video)] |
   | Newsletter | Kit (ConvertKit) | [draft (ID: N) / skipped / failed] |
   | Blog draft | Substack | [draft URL / skipped / failed] |
   | Blog post | Email (creator) | [sent/skipped] |
   | Timecodes | Email (Video Editor) | [sent/skipped] |
   | YT metadata | Email (Strategist) | [sent/skipped] |

   ## Publishing Checklist

   - [ ] Review X thread in `x/thread.md` — post manually or via scheduler
   - [ ] Schedule standalone tweets from `x/tweets.md`
   - [ ] Post LinkedIn from `linkedin/post.md`
   - [ ] Review Kit newsletter draft (see Delivery table for broadcast ID) — edit and send
   - [ ] Review Substack draft (see Delivery table for URL) — edit and publish
   - [ ] Upload YouTube with metadata from `youtube.html`
   - [ ] Add images from `x/tweet-images/` and `blog/hero.png`
   ```

3. **Build journal:** Append entry to `${BUILD_JOURNAL_PATH:-./build-journal}/YYYY-MM-DD.md` inline (see CLAUDE.md pipeline rule).

4. **Report results:**
   ```
   ## Social Content Repurposed

   - Title: [title]
   - X thread: [N] tweets (QAS Approved)
   - Standalone tweets: 9 (7 short + 2 long)
   - LinkedIn post: [chars] chars
   - Blog post: [words] words
   - Newsletter: [words] words (Kit draft ID: [id] / skipped / failed)
   - YouTube: [N] headlines, [N] chapters
   - Images: [N] generated (thread hero, tweet images, blog hero)
   - Emails sent: [N]
   - Telegram messages: [N]
   - Output: <input-dir>/social/

   All content delivered. Check Telegram and email for copy-paste-ready posts.
   ```
