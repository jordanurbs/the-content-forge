---
name: social-content
version: 1.0.0
description: "Platform constraints, defined social voice, hashtag strategy, and content formulas for social media repurposing. Auto-loaded by Social Content Writer and Quality Reviewer."
---

# Social Content Skill

Reference for all social media content produced by the `/repurpose-social` pipeline.

## Platform Constraints

### X (Twitter)
- **Character limit**: 280 per tweet
- **Thread mechanics**: First tweet is the hook (highest impression weight). Number threads: 1/N format. Last tweet is the closer + CTA.
- **Image**: 1200x675px (16:9) or 1080x1080px (1:1). Max 4 images per tweet.
- **Hashtags**: Max 3 per tweet. Place at end or woven naturally.
- **Links**: Shortened by Twitter (~23 chars). Place in closer, not hook.

### LinkedIn
- **Character limit**: ~3000 (first 210 chars visible before "see more")
- **Formatting**: Line breaks for readability. Bold with **asterisks** renders. No markdown headers.
- **Hashtags**: Max 5, placed at the bottom.
- **Images**: 1200x627px (landscape) or 1080x1080px (square).
- **No hard CTA**: LinkedIn penalizes "click the link" — use soft engagement prompts.

### Substack (Blog)
- **Length**: 800-1500 words
- **Format**: Full HTML. Headers, blockquotes, images, embedded links.
- **Structure**: Hook > Context > The Meat > The Verdict > Actionable Takeaway > P.S.

---

## Social Voice

The social voice is a compressed, higher-energy version of the creator'''s lesson voice. Think: same person, but on stage instead of in a workshop.

### Core Traits
- **Nautical metaphors**: "Navigate", "chart a course", "uncharted waters", "anchor your workflow", "set sail"
- **80s references**: Synthwave energy, arcade metaphors, "press start", "level up", "boss fight", "high score"
- **"Builders"**: Always. Never "followers", "audience", "students".
- **Specific numbers**: Always. "3 hours" not "a while". "$47/month" not "affordable".
- **Real failures**: Every thread/post includes at least one honest failure or struggle.
- **Peer-to-peer**: "We're figuring this out together" — never guru positioning.

### Compression Rules (tweets vs. lessons)
- Single idea per tweet. No compound sentences.
- Fragment sentences are encouraged: "Three hours. Two bugs. One missing env var."
- Parenthetical asides still work: "(Ask me how I know...)"
- Ellipses for dramatic pause: "And then... it worked."
- No filler. Every word earns its place.

---

## Four Avatar Types

All content should resonate with at least one of these audience segments:

### 1. Tech-Hesitant Creative
- Has ideas but overwhelmed by AI tools
- Needs: Permission to start messy, proof it's not as hard as it looks
- Hook angle: "I didn't know how to code. Here's what happened when I tried Claude Code anyway..."

### 2. Marketing Upgrade-Seeker
- Already using basic AI (ChatGPT for copy). Wants more.
- Needs: Specific workflows, time savings, cost comparisons
- Hook angle: "I replaced 3 marketing tools with one Claude Code workflow. Total cost: $0 + 4 hours."

### 3. Tech Translator
- Technical background, wants to explain AI to clients/team
- Needs: Frameworks, analogies, teaching tools
- Hook angle: "How I explain AI agents to clients who still think ChatGPT is just autocomplete."

### 4. AI Consultant Aspirant
- Wants to build a business around AI expertise
- Needs: Positioning, pricing, service delivery systems
- Hook angle: "My first AI consulting client paid $2,500. Here's the exact workflow I delivered."

---

## Thread Architecture

### Hook Tweet (1/N)
Formula: `[Specific result/number] + [Curiosity gap] + [Promise]`

Examples:
- "I built a complete content pipeline in 6 hours. It now does what took my team 3 days. Here's the exact setup (thread):"
- "Claude Code just saved me $708/year in SaaS subscriptions. But it almost didn't work. Here's what happened:"

### Body Tweets (2-N-1)
- One idea per tweet
- Alternate between: insight, example, failure moment, tactical step
- Use `[KEY PHRASE]` markers for the most shareable standalone tweets
- Include at least one tweet that works as a standalone (for quote-tweets)

### Closer Tweet (N/N)
- Recap the core value
- Single CTA: watch the video OR join the community OR reply with your experience
- Never multiple competing CTAs
- End with engagement prompt: "What's your experience with [topic]?"

---

## Standalone Tweet Formulas

### Short Tweets (<200 chars)
- **Hot take**: "AI won't replace you. But someone using AI will out-build you. (That someone could be you.)"
- **Observation**: "The gap between 'I should learn AI' and 'I just built something with AI' is about 3 hours."
- **Fragment stack**: "Claude Code. 3 prompts. 45 minutes. A full landing page. This is the new normal."

### Long Tweets (200-280 chars)
- **Mini-story**: "Last week I spent 6 hours debugging. The fix? One missing env var. This week I asked Claude Code to audit my config first. Found 3 issues in 30 seconds. The tool isn't magic. The workflow is."
- **Framework drop**: "My AI workflow rule: Build to Learn, Buy to Scale. Start with Claude Code to understand what you need. Then decide if a SaaS does it better. Usually... it doesn't."

### Image Prompt Per Tweet
Each standalone tweet gets an image prompt. Include:
- Brand DNA (synthwave, nautical, cyberpunk)
- Specific visual tied to the tweet content
- Text overlay suggestion (2-4 words max)

---

## LinkedIn Post Structure

### Opening (first 210 chars — visible before "see more")
- Story-led hook. Personal, specific, surprising.
- Must create enough curiosity to click "see more"

### Body (800-1800 chars)
- Single narrative arc: situation > attempt > failure/learning > insight
- Peer-to-peer tone throughout
- Include specific numbers, tool names, timeframes
- Break into short paragraphs (1-2 sentences each)
- Use line breaks generously

### Close
- Insight or takeaway (not a hard CTA)
- Engagement question: "What's your take?" / "Anyone else experiencing this?"
- Hashtags at the very end (max 5)

### Clip Recommendation
- Include a timecode recommendation for a 30-60s video clip from the source recording
- The clip should be the most LinkedIn-appropriate moment (insight, framework, or relatable story)

---

## Image Guidance

### Brand DNA (appended to ALL image prompts)
80s synthwave, maritime nautical, cyberpunk arcade, deep navy backgrounds, neon yellow/cyan, pixelated 8-bit, VHS pixel art.

### Negative Prompt (always included)
modern flat design, minimalist, realistic photography, corporate, bright daylight, pastel colors.

### Per-Platform Specs
- **X thread hero**: 1200x675px (16:9). Bold visual, text overlay optional.
- **X tweet images**: 1200x675px (16:9). Visual metaphor tied to tweet content.
- **LinkedIn**: 1200x627px (landscape). More professional but still branded.
- **Blog hero**: 1200x675px (16:9). Illustrative, topic-driven.

---

## Hashtag Strategy

### X (max 3 per tweet)
- Primary: `#ClaudeCode` or `#AIAssisted` (always one of these)
- Secondary: topic-specific (e.g., `#VibeCoding`, `#AIWorkflow`, `#BuildInPublic`)
- Never use generic tags: `#AI`, `#Tech`, `#Innovation`

### LinkedIn (max 5, at bottom)
- Primary: `#AIAssisted` `#ClaudeCode`
- Secondary: topic + audience (e.g., `#ContentCreation`, `#SoloFounder`, `#BuildToLearn`)
- One broad-reach tag: `#Entrepreneurship` or `#ProductivityTips`

---

## Anti-Patterns (NEVER DO)

- **Emoji spam**: Max 1-2 per tweet, 3-4 per LinkedIn post. Zero in threads except hook.
- **Guru positioning**: "I'll teach you" / "Most people don't know" / "The secret is"
- **Generic motivational**: "Hustle harder" / "Believe in yourself" / "The grind never stops"
- **Clickbait that doesn't deliver**: If the thread promises "exact setup", it must include specifics
- **Multiple CTAs**: One CTA per piece of content. Pick one and commit.
- **Hashtag stuffing**: Never more than specified per platform
- **Corporate voice**: "Leveraging synergies" / "Driving innovation" / "Thought leadership"
- **Apologetic hedging**: "I'm no expert but..." — state things directly with honest uncertainty instead
