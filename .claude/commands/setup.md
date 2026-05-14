# /setup -- Member Customization Wizard

Walk the member through configuring their Content Forge instance. Fills out `config/member-profile.md` with identity, audience, voice, brand, and pipeline preferences. Run this **once** before using any pipeline.

## Input: $ARGUMENTS

No arguments expected. This is an interactive wizard.

## Context Rules (MANDATORY)

- This command runs directly (no agent spawning)
- Write the completed profile to `config/member-profile.md`
- Use `AskUserQuestion` for choices with discrete options (always offer "Other" implicitly via the tool)
- Free-text questions: just ask them inline
- Do NOT overwrite existing settings without confirming first if `config/member-profile.md` looks already filled in

## Pipeline

### Step 1: Welcome + Check Existing Profile

Read `config/member-profile.md`. If it's already filled in (i.e., the "Your Identity" section has real values, not `[placeholders]`), tell the member:

```
Your profile is already set up. What would you like to do?
```

Offer (via AskUserQuestion):
- "Show me my current profile" — print it back, ask if they want to re-run
- "Start over from scratch" — proceed with wizard, overwrite
- "Update specific sections only" — ask which sections, only re-prompt for those

Otherwise (profile is template-only), say:

```
Welcome to The Content Forge.

I'll ask you a series of questions to configure your identity, audience, voice, brand,
and pipeline preferences. This only needs to be done once — your settings will be used
by every pipeline you run.

Most questions are quick. The voice and audience sections take the most thought —
they're what makes the output sound like YOU instead of generic AI content.

This takes about 5-10 minutes. Ready?
```

Wait for affirmation.

### Step 2: Collect Information

Collect in this order. Use `AskUserQuestion` for choices; free-text inline.

**Your Identity**
1. What's your creator/business name?
2. What's your handle? (e.g., @yourhandle)
3. What's your website URL?
4. What's your contact email?

**Your Audience**
5. Who are you writing for? (1-2 sentences — describe the type of person, their context, their goals)
6. What's their assumed knowledge baseline? (e.g., "Comfortable in a terminal", "Knows React but new to AI", "Total beginner")
7. What do they REWARD in writing? (e.g., specific numbers, real failures, contrarian takes)
8. What do they REJECT? (e.g., hype, guru positioning, "secrets" framing)

**Your Voice**
9. Describe your voice in one sentence (e.g., "Conversational technical, peer-to-peer, specific over vague")
10. What do you call your audience? (e.g., "builders", "founders", "operators" — avoid "students", "users", "members" unless your platform forces it)
11. Do you have signature phrases you want preserved verbatim? (List 2-5, or "no")

After collecting these, tell the member:

```
Voice deep-dive: the harness ships with a minimal generic voice-standard at
.claude/skills/voice-standard/SKILL.md. To get full voice fidelity, you'll want
to flesh that file out using examples/voice-standard-creator-voice.md as a template.

Do you want to do that now, or skip and use the generic standard for now?
```

Use AskUserQuestion: "Customize voice now (recommended)" / "Use generic for now, customize later"

If "customize now": guide them through copying `examples/voice-standard-creator-voice.md` to `.claude/skills/voice-standard/SKILL.md` and prompt them to fill in their signature patterns. Then offer to help them define 3-5 signature patterns inline.

**Your Persona (Optional)**
12. Do you want a recurring character to appear in lesson hero images and intro/outro video cards?

Use AskUserQuestion: "Yes — define one now" / "No — persona-free" / "Maybe later (skip)"

If yes: ask them to describe the character's physical appearance (clothing, build, expression, props) — NEVER the name. Write this to `config/persona.md`.

**Visual Brand**
13. What's your primary brand color? (hex code, e.g., #0a0e1a)
14. What's your accent color? (hex code, e.g., #FFD700)
15. What's your secondary/highlight color? (hex code, e.g., #00FFFF)
16. Do you have a brand logo to use on video intro/outro cards?
    - If yes: ask them to drop the file into `tools/broll-animator/public/` and collect the filename
    - If no: leave empty (cards will render without a logo)
17. Brand display name shown on video CTA cards (e.g., "Your Brand", "@yourhandle")

**Image Generation Style**
18. Describe your visual aesthetic in 1 sentence (e.g., "Clean infographic illustration, dark navy + gold accents, no synthwave")

Tell the member:
```
This becomes the "Brand DNA" suffix appended to every Venice AI prompt. You can
fine-tune it later at config/image-style.md.
```

**Publishing Destinations**
19. Which platforms do you publish to? (multi-select):
    - YouTube
    - X / Twitter
    - LinkedIn
    - Newsletter platform (Kit/ConvertKit/etc.)
    - Substack
    - Skool
    - Personal blog/website
    - Other

**Pipeline Preferences**
20. Default lesson length? (e.g., "10-15 minutes")
21. Default video duration target? (e.g., "8-12 minutes")
22. Default emoji budget? (e.g., "1-2 per lesson", "0 — none ever", "use sparingly")

**Numbering Convention**
23. Do you want the default `<module>.<section>.<lesson>` numbering (e.g., 2.3.1)? Or a different scheme?

### Step 3: Write Profile

Write the completed profile to `config/member-profile.md` using the template structure already in that file. Fill in every `[bracketed]` field with the member's answers.

Also update `config/theme.json` with the colors, brand logo filename, and brand display name they provided.

If they defined a persona, write that to `config/persona.md`.

If they described an aesthetic, append it to `config/image-style.md` (rewriting the Brand DNA Suffix section).

### Step 4: Verify Outputs

After writing, confirm each file exists:
- `config/member-profile.md` (filled in)
- `config/theme.json` (colors + brand logo + brand name updated)
- `config/persona.md` (filled if they chose persona, otherwise unchanged)
- `config/image-style.md` (Brand DNA updated)

### Step 5: Confirm + Next Steps

Tell the member:

```
Setup complete.

Files written:
- config/member-profile.md
- config/theme.json (colors + brand)
- config/persona.md (if you defined one)
- config/image-style.md (Brand DNA prompt)

What's next:
1. Edit .env (copy from .env.example) and fill in any publishing integrations you want
   to use (Venice AI for images, Mailgun for email, Telegram, LinkedIn, Kit, Substack, etc).
   All are optional — missing credentials just skip that step.

2. (Recommended) Flesh out your voice standard at:
   .claude/skills/voice-standard/SKILL.md
   Use examples/voice-standard-creator-voice.md as a template. This is what makes the
   output sound like YOU instead of generic AI.

3. Run your first pipeline:
   /create-lesson — Single lesson from an idea/outline/transcript
   /create-video — Video pre-production (script + treatment + storyboard)
   /repurpose-social — Transcript → cross-platform social content

   Output lands in: output/<slug>/
```

Then ask:

```
Want me to walk you through writing your voice standard now, or pick a pipeline to run?
```

Use AskUserQuestion: "Walk me through voice standard" / "Run a pipeline now" / "I'm good, exit setup"
