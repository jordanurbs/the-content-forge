---
name: corrections
version: 1.0.0
description: "Term correction patterns and transcription cleanup rules. Auto-loaded by Transcript Processor agent."
---

# Transcription Corrections

## Corrections File

The corrections dictionary lives at `.corrections.json` in the project root.

It maps common transcription errors to correct terms. Apply all corrections as **case-insensitive** replacements.

## Current Corrections

```json
{
  "cloud code": "Claude Code",
  "clod code": "Claude Code",
  "clawed code": "Claude Code",
  "claude coat": "Claude Code",
  "clod": "Claude",
  "claude ai": "Claude AI",
  "anthropic": "Anthropic",
  "open ai": "OpenAI",
  "open a i": "OpenAI",
  "chat gpt": "ChatGPT",
  "chat g p t": "ChatGPT",
  "g p t": "GPT",
  "g. p. t.": "GPT",
  "gpt4": "GPT-4",
  "gpt 4": "GPT-4",
  "github": "GitHub",
  "git hub": "GitHub",
  "copilot": "Copilot",
  "co-pilot": "Copilot",
  "VS code": "VS Code",
  "v s code": "VS Code",
  "vs. code": "VS Code",
  "vscode": "VS Code",
  "typescript": "TypeScript",
  "type script": "TypeScript",
  "javascript": "JavaScript",
  "java script": "JavaScript",
  "node js": "Node.js",
  "nodejs": "Node.js",
  "next js": "Next.js",
  "nextjs": "Next.js",
  "react js": "React.js",
  "an 8 n": "n8n",
  "API key": "API key",
  "a p i": "API",
  "LLM": "LLM",
  "l l m": "LLM"
}
```

## How to Apply Corrections

1. Read `.corrections.json` from the project root
2. For each key-value pair, perform a **case-insensitive** search-and-replace on the transcript text
3. Process longer patterns first (e.g., "cloud code" before "clod") to avoid partial matches
4. Save the corrected text as `<filename>.clean.txt`

## Adding New Corrections

Only add corrections for **clear misrecognitions** — patterns where the transcription is unambiguously wrong.

Do NOT add ambiguous terms. For example:
- "claw" could be "ClawBot" or could genuinely be "claw" — leave it
- "school" could be "Skool" or could genuinely be "school" — leave it

To add a correction, edit `.corrections.json` directly. The key is the wrong term (lowercase), the value is the correct term.

## Additional Cleanup Rules

After applying dictionary corrections, also:

1. Remove repeated words (stuttering): "the the" -> "the"
2. Fix common spacing issues around punctuation
3. Preserve all timestamps in their original format
4. Do NOT remove filler words (um, uh, like) — that's the Lesson Writer's job
5. Do NOT rewrite or rephrase content — only fix misrecognized terms
