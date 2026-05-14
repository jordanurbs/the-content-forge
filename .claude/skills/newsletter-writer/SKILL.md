---
name: newsletter-writer
description: Write, review, and publish newsletters in the creator'''s voice via Kit (ConvertKit). Covers the full lifecycle from context gathering through draft creation, revision, Kit API push, and send.
triggers:
  - write a newsletter
  - draft a newsletter
  - newsletter about
  - push to kit
  - send newsletter
  - newsletter draft
---

# Newsletter Writer Skill

Write long-form newsletters in the creator'''s authentic voice, push drafts to Kit (ConvertKit), and manage the full newsletter lifecycle.

---

## Overview

This skill handles everything from idea to inbox:

1. **Context Gathering** — Pull recent journals, memories, activities, and notes
2. **Theme Selection** — Identify the strongest narrative thread
3. **Drafting** — Write the newsletter following strict voice and structure rules
4. **Review & Revision** — Present to the user, iterate on feedback
5. **Kit Push** — Push approved draft to Kit as a broadcast draft
6. **Post-Publish** — Log the activity, update draft status

---

## Environment

This skill requires a `.env` file in the skill directory with:

```
KIT_API_KEY=<your Kit API key>
```

Load it before making Kit API calls:

```bash
source "$(dirname "$0")/../.env"
```

Or read it directly in shell:

```bash
KIT_API_KEY=$(grep KIT_API_KEY /path/to/skills/newsletter-writer/.env | cut -d'=' -f2)
```

---

## 1. Context Gathering

Before writing, always gather raw material:

### Automatic (Batch Generation)
When triggered by the long-form content cadence or "generate a newsletter":

- Last 30 memories (via `memory_search`)
- Last 30 activities (via `memory_search` with `[activity:]` queries)
- Last 15 notes
- Last 7 days of journal entries from `journals/` directory
- Last 5 drafts (to avoid repeating recent topics)

### Targeted (Specific Topic)
When the user says "write a newsletter about X":

- Search memories for X
- Search journals for X
- Pull any related notes
- Use conversation context

### Context Priority
Rank source material by:
1. **Recency** — What happened this week matters most
2. **Depth** — Entries with learnings, raw thoughts, and realizations over status updates
3. **Resonance** — Topics that connect to the project'''s core philosophy (sovereignty, intention, captain mindset)
4. **Novelty** — Things he hasn't written about recently

---

## 2. Theme Selection

From the gathered context, identify **one primary narrative thread**. A good newsletter theme:

- Has a **human entry point** (a feeling, struggle, realization — not a feature)
- Contains a **transferable insight** (something the reader can apply)
- Connects to the **bigger philosophy** (sovereignty, intention, clarity)
- Has enough **concrete detail** to be specific without being a tutorial

Present the theme to the user before writing (unless he already specified one):

> "Strongest thread from this week: [theme]. The angle would be [angle]. Want me to run with it, or do you have something else in mind?"

---

## 3. Drafting

### Structure (Mandatory)

Every newsletter follows this skeleton. Adapt the content, but keep the bones:

#### Opening (2-3 paragraphs)
- Punchy, conversational. Name the chaos, the hype, or the quiet thing nobody's saying.
- Use `{{ subscriber.first_name }}` personalization in the greeting.
- Quick personal context — what you've actually been doing, not a generic "hope you're well."

#### The Insight (3-5 paragraphs)
- The real thing nobody's talking about. The shift. The realization.
- Bold statements as standalone single-line paragraphs for emphasis.
- This is where the philosophy lives: sovereignty, intention, captain mindset.

#### The Deep Walkthrough (5-10 paragraphs)
- Show your ACTUAL system — name the agents, name the frameworks, describe what each one DOES.
- Tie every tool mention back to WHY it matters for your brain, workflow, or freedom.
- Section headers for each major concept or crew member.
- Freely admit failures and dead ends: "tried X but it couldn't handle it — FAIL"

#### The Human Takeaway (2-3 paragraphs)
- The lesson underneath the tech. Always about the HUMAN side.
- "The channel creates the context. The context creates the behavior." — that level of insight.
- Not feature comparisons. Not tool rankings.

#### Practical Action (1-2 paragraphs)
- Dead simple. One thing the reader can do this week.
- "Pick ONE thing, put an AI in a dedicated channel for it, use it for a week."
- Accessible to someone with zero setup.

#### Sign-Off
- Warm, personal. Like ending a conversation with a friend.
- Always include a P.S. that teases something coming next (a launch, a video, a new build, a future newsletter topic).

### Length

**1500-3000 words.** the project'''s newsletters are LONG — this is a feature, not a bug. This is the platform where he goes DEEP. Don't hold back.

### Voice Rules (from SOUL.md — strictly enforced)

- **Lead with the human, not the implementation.** Never let it read like a changelog or tutorial.
- **Name AI agent frameworks when relevant**: Claude Code, OpenClaw, Agent Zero, Roo Code, etc. — but only when it serves the story or the lesson.
- **Describe outcomes, not plumbing**: "a system that writes and schedules my content while I sleep" NOT "a TypeScript pipeline with Drizzle ORM"
- **EXCEPTION for newsletters**: You CAN go deeper into stack details (PostgreSQL, Docker, WASM, etc.) when explaining WHY a design choice matters for sovereignty or workflow. The rule: name the tech only when it serves the story or principle.
- **Anti-hype energy**: "There's no best agent tool" — directly counter breathless Twitter takes.
- **Authentic vulnerability**: Share actual struggles, real timelines, real emotions. Admit uncertainties.
- **Single-line paragraphs dominate.** Strategic ellipses... Parenthetical asides (yeah, I know). Sentence fragments for emphasis. Like this.

### NEVER in Newsletters

- Guru positioning ("I'll show you the way")
- Manufactured urgency ("Act now!")
- Vague promises ("Transform your business")
- Hype language ("Revolutionary!" "Game-changing!" "10x!")
- Manipulation tactics (false scarcity, FOMO)
- Excessive emojis (max 1-2 per entire newsletter)
- Sounding like documentation or a tutorial — always sound like a person

---

## 4. Review & Revision

After drafting, present the full newsletter to the user:

> "Here's this week's newsletter draft. [word count] words.
>
> **Subject line**: [subject]
>
> ---
> [full newsletter content]
> ---
>
> Want me to revise anything, or push to Kit as a draft?"

### Revision Rules
- If the user gives feedback, apply it and present the revised version
- Don't explain what you changed — just show the new version
- If the user says "shorter" — cut aggressively, keep the soul
- If the user says "more on X" — expand that section, compress others to maintain balance
- Maximum 3 revision rounds before asking: "Want to just edit this directly in Kit after I push it?"

---

## 5. Kit (ConvertKit) API Push

### When to Push
Only after the user explicitly approves: "push it," "send to kit," "looks good, push," "approved," etc.

### API Details

**Endpoint**: `POST https://api.kit.com/v4/broadcasts`

**Auth Header**: `X-Kit-Api-Key: <KIT_API_KEY from .env>`

**Content-Type**: `application/json`

**Payload**:
```json
{
  "subject": "<subject line>",
  "content": "<HTML content>",
  "send_at": null,
  "public": true
}
```

### Markdown → HTML Conversion

Before pushing, convert the newsletter markdown to Kit-friendly HTML:

1. Strip YAML frontmatter
2. Strip the H1 title (it becomes the `subject` field)
3. Convert `**bold**` → `<strong>bold</strong>`
4. Convert `*italic*` → `<em>italic</em>`
5. Split on double newlines into `<p>` tags
6. Convert `## Headings` → `<h2>Headings</h2>`
7. Convert `### Headings` → `<h3>Headings</h3>`
8. Convert markdown links `[text](url)` → `<a href="url">text</a>`
9. Convert `---` horizontal rules → `<hr>`
10. Preserve `{{ subscriber.first_name }}` template tags as-is (Kit processes these)

### Conversion Script

Use the included helper script:

```bash
./scripts/md-to-kit-html.sh drafts/newsletter-draft.md
```

Or do inline conversion via the agent's own markdown→HTML logic.

### Push Execution

```bash
source .env

curl -s -X POST "https://api.kit.com/v4/broadcasts" \
  -H "X-Kit-Api-Key: $KIT_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "subject": "'"$SUBJECT"'",
    "content": "'"$HTML_CONTENT"'",
    "send_at": null,
    "public": true
  }'
```

### Post-Push
- Report to the user: "Pushed to Kit as draft (ID: [broadcast_id]). You can review and send from the Kit dashboard."
- **NEVER set `send_at` to a timestamp** — the user sends manually from the Kit dashboard.
- If the API returns an error, report it clearly and do not retry automatically.

---

## 6. Draft File Management

### Save Location
All newsletter drafts go to the workspace `drafts/` directory:

```
drafts/YYYY-MM-DD-newsletter-[slug].md
```

Example: `drafts/2026-03-11-newsletter-context-engineering.md`

### Frontmatter Format
```markdown
---
type: newsletter
platform: kit
status: draft
generated: YYYY-MM-DDTHH:MM:SS-10:00
subject: "The subject line goes here"
word_count: 2100
context_window: long-form
kit_broadcast_id: null
---
```

### Status Flow
```
draft → approved → pushed → sent (manual from Kit)
```

Update the frontmatter as the draft moves through stages:
- `draft` — Written, awaiting user review
- `approved` — the user approved the content
- `pushed` — Successfully pushed to Kit as a broadcast draft (set `kit_broadcast_id`)
- `sent` — [Creator] manually sent from Kit dashboard (update if he confirms)

---

## 7. Post-Publish

After pushing to Kit:

1. Update draft frontmatter: `status: pushed`, add `kit_broadcast_id`
2. Store a memory: `[activity:shipping] Pushed newsletter to Kit: "[subject line]"`
3. Confirm to the user with the broadcast ID

---

## 8. Subject Line Guidelines

Strong subject lines for the project'''s newsletters:

- **Conversational**: "So I built a crew this week..."
- **Provocative**: "There's no best AI agent tool"
- **Curiosity-driven**: "The part nobody talks about when building with AI"
- **Direct**: "How I replaced 4 hours of daily work with agents"
- **Vulnerable**: "I almost gave up on this three times"

Avoid:
- Clickbait ("You won't believe...")
- Numbers-first ("7 ways to...")
- Generic ("My thoughts on AI")
- ALL CAPS anything

Always present 2-3 subject line options and let the user pick.

---

## 9. Quick Reference: Targeted vs Batch

| | Targeted Newsletter | Batch Newsletter |
|---|---|---|
| **Trigger** | "Write a newsletter about context engineering" | "Generate today's content" (long-form cycle) |
| **Theme** | Specified by the user | Extracted from recent context |
| **Context** | Conversation + targeted memory search | Full 7-day context sweep |
| **Confirmation** | Theme already given, write directly | Present theme for approval first |
| **Output** | 1 newsletter draft | 1 newsletter + 1 blog + 1 skool post |

---

## Templates

See `templates/` for reference newsletter structures:
- `templates/standard.md` — The default newsletter skeleton
- `templates/deep-dive.md` — For technical deep-dives with more walkthrough sections
- `templates/manifesto.md` — For philosophical / big-idea newsletters

---

## Checklist Before Push

Before pushing any newsletter to Kit, verify:

- [ ] 1500-3000 words
- [ ] Opens with a human moment, not a tool name
- [ ] `{{ subscriber.first_name }}` in the greeting
- [ ] At least one bold standalone statement
- [ ] Admits a failure or uncertainty somewhere
- [ ] Practical action step anyone can do
- [ ] P.S. with a tease for what's next
- [ ] No hype language, no guru energy
- [ ] Subject line approved by the user
- [ ] the user explicitly approved the push
