---
name: stop-slop
version: 1.0.0
description: "Catch and eliminate AI writing patterns from prose. Universal AI slop detection; voice-specific exceptions are read from the project's voice-standard skill. Auto-loaded by Lesson Writer, Blog Writer, Social Content Writer, Script Writer, Newsletter Writer, and Quality Reviewer."
metadata:
  trigger: Writing prose, editing drafts, reviewing content for AI patterns
  origin: https://github.com/hardikpandya/stop-slop (MIT, by Hardik Pandya)
  customized: true
---

# Stop Slop

Eliminate predictable AI writing patterns from prose.

## How This Works With Your Voice

This skill defines **universal AI-slop detection rules** — the patterns that mark generic AI writing regardless of voice (corporate filler, throat-clearing openers, formulaic structures, vague declaratives).

**Voice-specific exceptions live in `.claude/skills/voice-standard/SKILL.md`.** When the universal rules conflict with deliberate creator voice patterns (e.g., a creator who uses sentence fragments rhythmically, or parenthetical asides intentionally), the voice-standard overrides win.

If your voice-standard doesn't list a specific exception, the universal rules apply.

## Core Rules

1. **Cut filler phrases.** Remove throat-clearing openers, emphasis crutches, and most adverbs. See [references/phrases.md](references/phrases.md).

2. **Break formulaic structures.** Avoid binary contrasts ("not X — it's Y"), negative listings, stacked staccato fragments, rhetorical setups, false agency. See [references/structures.md](references/structures.md).

3. **Use active voice.** Every sentence needs a human subject doing something. No passive constructions. No inanimate objects performing human actions ("the complaint becomes a fix" — someone fixed it).

4. **Be specific.** No vague declaratives ("The reasons are structural"). Name the specific thing. No lazy extremes ("every," "always," "never") doing vague work.

5. **Put the reader in the room.** No narrator-from-a-distance voice. "You" beats "People." Specifics beat abstractions.

6. **Vary rhythm.** Mix sentence lengths. Two items often beat three-item lists. End paragraphs differently.

7. **Trust readers.** State facts directly. Skip softening, justification, hand-holding.

8. **Cut quotables.** If it sounds like a pull-quote or motivational poster, rewrite it. Specifics and honesty beat aphorisms.

## Quick Checks

Before delivering prose:

- Filler adverbs ("really," "just," "simply," "actually") — kill them (unless your voice-standard explicitly allows one)
- Passive voice — find the actor, make them the subject
- Inanimate thing doing a human verb ("the decision emerges") — name the person
- "Here's the thing" / "Here's what" throat-clearing — cut to the point
- "Not X, it's Y" binary contrasts — state Y directly
- Three consecutive sentences match length — break one
- Every paragraph ends with a punchy one-liner — vary it
- Em dash in a binary contrast ("not X — it's Y") — remove the contrast framework
- More than 2 em dashes in one piece — cut to 1-2 (unless voice-standard says otherwise)
- Vague declarative ("The implications are significant") — name the specific implication
- Narrator-from-a-distance ("Nobody designed this") — put the reader in the scene
- Meta-joiners ("The rest of this essay...") — delete
- Stacked fragments ("[Noun]. That's it. That's the [thing].") — rewrite as a single sentence

## Scoring

Rate 1-10 on each dimension:

| Dimension | Question |
|-----------|----------|
| Directness | Statements or announcements? |
| Rhythm | Varied or metronomic? |
| Trust | Respects reader intelligence? |
| Authenticity | Sounds human — and specifically matches the project's voice-standard? |
| Density | Anything cuttable? |

Below 35/50: revise.

## Reference Files

- [references/phrases.md](references/phrases.md) — Banned phrases and replacements
- [references/structures.md](references/structures.md) — Structural anti-patterns
- [references/examples.md](references/examples.md) — Before/after transformations

## License

Original work MIT by Hardik Pandya (https://github.com/hardikpandya/stop-slop). Modifications by the {{PROJECT_NAME}} maintainers.
