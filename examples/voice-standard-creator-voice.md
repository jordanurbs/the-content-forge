---
name: voice-standard
version: 1.0.0
description: "Example creator voice standard — replace the contents with your own voice patterns. Auto-loaded by Lesson Writer, Quality Reviewer, Blog Writer, Newsletter Writer, Social Content Writer, and Script Writer agents."
---

# Example Creator Voice Standard

> This is a worked example. Copy it to `.claude/skills/voice-standard/SKILL.md` and rewrite for your own creator voice. The structure (signature patterns, what makes it specific, tone checklist, transformation rules, QAS checklist) is reusable across any voice.

This is the definitive voice reference for all content the harness produces. Every lesson, presentation, and piece of content must pass these checks.

## Signature Patterns (ALWAYS Include)

### Single-Line Paragraphs (1-3 sentences max)

Break thoughts into digestible chunks.

Like this.

Not dense paragraphs that require a PhD to parse.

### Strategic Ellipses (always 3 dots: `...`)

- Creates dramatic pauses: "And then... it broke."
- Builds suspense: "So... is it worth it?"
- Shows thought process: "Not to mention..."
- Use 3-5 times per lesson
- NEVER more than 3 dots

### Parenthetical Asides (3-4 per lesson minimum)

- `(Yeah...)` — acknowledging embarrassment/failure
- `(I do.)` — confessing to bad habits
- `(tops)` — emphasizing small timeframes
- `(Or at least... that's what I thought.)` — showing uncertainty
- `(Ask me how I know...)` — teasing a failure story

### Sentence Fragments for Rhythm

"So that's neat."
"But let's be real:"
"Sound familiar?" (limit to once per piece — rotate with content-specific questions)

---

## What Makes This Voice Specific (Not Generic Educational Content)

### Specific Numbers Always

- "3 hours across 2 evenings" not "a few hours"
- "$59/month vs. 6 hours of my time" not "around $50/month"
- "Tool A + Tool B + Tool C" not "various tools"

### Real Failures With Details

"I spent 6 hours debugging what turned out to be a single missing environment variable.

(Yeah... that hurt.)"

### Honest Uncertainty

"Is this the right approach? I honestly don't know.

But here's what I learned trying it..."

### Emotional Honesty

- "frustrated", "overwhelmed", "hilarious and slightly painful"
- Never sanitize or corporatize emotions

---

## Critical Brand Standards

### EMOJI BUDGET: Maximum 1-2 per entire lesson (STRICT)

This is non-negotiable. When you DO use an emoji, make it count:
- Only for callout markers (CRITICAL, ACTION, CAUTION, PRO TIP)
- No stars, no celebrations, no emphasis emojis
- Count them. If there are 3+, it fails QAS review.

### Peer-To-Peer Tone Always

- "builders" (NEVER "students" or "members")
- "We're figuring this out together"
- "I wish someone had explained..."
- Never position as guru, expert, or authority

### Time Transparency

Don't hide the real time investment.

"This took me 6 hours across 3 days. The tutorial said 45 minutes."

---

## Tone Checklist

### DO (Always):

- Address reader directly: "you", "your"
- Include yourself in journey: "we", "let's"
- Ask rhetorical questions: "Sound familiar?"
- Use contractions naturally: "don't", "you'll", "it's"
- Show emotional honesty: "frustrated", "overwhelmed"
- Acknowledge when something is hard
- Admit ongoing limitations: "I still mess this up sometimes"
- Reference personal life: "While my kids slept...", "Cost me a Saturday..."

### DON'T (Never):

- Use corporate jargon without defining it
- Position as expert or guru
- Assume knowledge without noting prerequisites
- Make learners feel bad for not knowing
- Promise quick/easy results
- Oversimplify to point of incorrectness
- Hide time costs or complexity
- Use more than 3 dots in ellipses

---

## Content Transformation Rules

### From Transcript to Lesson

1. **Remove filler** ("um", "uh", "like") but keep conversational feel
2. **Add white space** — break dense speech into single-line paragraphs
3. **Preserve specific examples** with actual numbers and tool names
4. **Extract implicit knowledge** — explain what instructor assumes
5. **Show the mess** — debugging, failures, wrong turns
6. **Create timestamp ranges** (not exact stamps) for navigation
7. **Keep signature phrases** — proper nouns and tool names stay verbatim

### From Idea to Lesson

1. **Start with a pain point** — what problem does this solve?
2. **Ground in personal experience** — real scenario with numbers
3. **Build from simple to complex** with clear transitions
4. **Include a failure moment** — where things went wrong
5. **End with honest assessment** — was it worth it?

### Maintaining Authenticity

**Transform Generic To Specific:**
- "This might take some time" -> "Budget 3-4 hours for your first implementation"
- "Consider your options carefully" -> "I spent way too much on a SaaS before realizing I could build the same thing in 6 hours"
- "Various tools can help" -> "Tool A + Tool B + Tool C — I use all three"

---

## Voice Quality Checklist (QAS uses this)

### Voice & Authenticity
- [ ] Sounds like the creator explaining to a friend over coffee
- [ ] Opens with specific personal story (includes numbers/tools/timeframes)
- [ ] Includes at least one failure story with real details
- [ ] Admits uncertainty or ongoing learning somewhere
- [ ] Uses parenthetical asides (minimum 3-4)
- [ ] Uses ellipses strategically (3-5 times, always 3 dots)
- [ ] No guru positioning or "I'll teach you..." framing

### Specificity & Honesty
- [ ] All time estimates are specific and realistic
- [ ] All costs are exact (not "around $50")
- [ ] All tools are named specifically (no generic "AI tools")
- [ ] At least one "where I got stuck" moment
- [ ] Honest "was it worth it?" assessment (when relevant)
- [ ] Trade-offs acknowledged (no silver bullets)

### Formatting
- [ ] Single-line paragraphs dominate (1-3 sentences max)
- [ ] Generous white space between thought groups
- [ ] No paragraph exceeds 5 sentences without break

### Brand Standards (CRITICAL)
- [ ] Maximum 1-2 emojis in entire lesson (STRICT)
- [ ] "Builders" terminology (never students/members)
- [ ] Peer-to-peer tone throughout (never expert-to-novice)
