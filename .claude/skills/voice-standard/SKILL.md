---
name: voice-standard
version: 1.0.0
description: "Generic voice standard for content. REPLACE THIS FILE with your own voice patterns. Auto-loaded by Lesson Writer, Quality Reviewer, Blog Writer, Newsletter Writer, Social Content Writer, and Script Writer agents."
---

# Voice Standard (Generic — Replace This)

> This is a minimal placeholder. **Define your own voice here** — see `examples/voice-standard-creator-voice.md` for a worked example showing how a real creator defines their signature patterns, tone, and quality checklist.
>
> The agents that auto-load this skill will follow whatever rules you write. Keep the section structure (Signature Patterns, Tone Checklist, QAS Checklist) so the Quality Reviewer agent can validate against it.

## Universal Writing Rules (apply regardless of voice)

These rules are baseline writing quality and apply to any voice. Layer your own creator-specific patterns on top.

### Specificity Over Vagueness

- Exact numbers, not "a few" or "about"
- Named tools, not "various AI tools"
- Real costs, not "affordable" or "reasonable"
- Concrete examples, not abstract claims

### Conversational Sentence Variation

- Mix short sentences with longer ones
- Sentence fragments are allowed for rhythm
- Read it aloud — if you stumble, rewrite it
- Single-line paragraphs are fine; long paragraphs need breaking up

### Honest Tone

- Acknowledge difficulty when something is hard
- Admit uncertainty when you don't know
- Show failures and detours, not just polished outcomes
- Avoid corporate jargon and marketing-speak

### No AI Slop

See the `stop-slop` skill for the full pattern catalog. Briefly:
- No "delve", "tapestry", "navigate the landscape", etc.
- No three-item rule-of-three when it's filler ("comprehensive, robust, and scalable")
- No vague hedges ("It's important to note that...")
- No throat-clearing sentence openers ("Honestly,", "Truly,")

### Reader-Direct Voice

- Address the reader as "you", include yourself with "we" / "let's"
- Avoid third-person passive ("the user is presented with...")
- Avoid guru positioning ("I'll teach you...")

## Brand-Level Rules (override per project)

### Emoji Budget

Default: maximum 1-2 emojis per piece of content. Use them only for callout markers (CRITICAL, ACTION, CAUTION, PRO TIP). Override in your project's customized voice standard if your brand uses emojis differently.

### Audience Terminology

Default: address your readers as "builders" or whatever terminology fits your project. Avoid "students" / "members" / "users" unless the platform forces it. Update this when you fork the file.

---

## Voice Quality Checklist (QAS uses this)

These are the universal checks. Add project-specific checks when you fork this file.

### Specificity
- [ ] All time estimates are specific (no "a few hours")
- [ ] All costs are exact (no "around $50")
- [ ] All tools are named specifically
- [ ] At least one concrete example per major concept

### Honesty
- [ ] Failure or stuck-moment included (when relevant)
- [ ] Trade-offs acknowledged (no silver bullets)
- [ ] Honest "was it worth it?" assessment (when relevant)

### Formatting
- [ ] Single-line paragraphs dominate (1-3 sentences max)
- [ ] Generous white space between thought groups
- [ ] No paragraph exceeds 5 sentences without break

### Brand Standards
- [ ] Emoji budget respected
- [ ] Audience terminology consistent
- [ ] No AI slop patterns (see `stop-slop` skill)

---

## How to Customize

1. Copy `examples/voice-standard-creator-voice.md` to this file (replacing this placeholder), or
2. Write your own from scratch following the structure: Signature Patterns → What Makes It Specific → Tone Checklist → Transformation Rules → QAS Checklist.
3. Define 3-6 "signature patterns" unique to your voice (parenthetical asides, sentence rhythm, specific phrases, etc.).
4. List your bans and musts in the Tone Checklist.
5. Save and commit. Agents will auto-load the file on the next pipeline run.
