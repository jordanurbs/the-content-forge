---
name: lesson-template
version: 1.0.0
description: "HTML template structure and formatting rules for {{PROJECT_NAME}} Skool lessons. Auto-loaded by Lesson Writer and Quality Reviewer agents."
---

# {{PROJECT_NAME}} Lesson Template

This is the definitive template reference for platform-agnostic clean lesson HTML. Every lesson must follow this structure and these formatting rules.

## Required Sections (in order)

Every lesson MUST include all of these sections. Omitting any is a QAS failure.

### 1. Title, Meta, and Hero Image (H1)

```html
<h1>Lesson [M.S.L]: [Title]</h1>
<p><strong>Time to Complete:</strong> [X] minutes</p>

<p><img src="../assets/<M.S.L>-<slug>.png" alt="[Descriptive alt text for the lesson topic]"></p>
```

The hero image goes immediately after the title block, before the first `<hr>`.

### 2. What You'll Get

```html
<h2>What You'll Get</h2>

<p><strong>Business Terms:</strong> [Technical description of the deliverable]</p>

<p><strong>AKA (In Other Words):</strong> [Conversational, relatable description of what they're actually getting]</p>
```

### 3. What You'll Do

```html
<h2>What You'll Do</h2>

<p>[Overview of the hands-on activity]</p>

<p>[CRITICAL/ACTION/CAUTION/PRO TIP callouts as relevant]</p>
```

### 4. Content Sections (H2 + H3)

Main lesson content. Each major topic gets an H2. Subtopics get H3. Use `<hr>` between major sections.

```html
<hr>

<h2>[Section Title]</h2>

<p>[Content in single-line paragraphs]</p>

<h3>[Subsection]</h3>

<p>[Content]</p>
```

### 5. Health Break (REQUIRED)

Place at approximately the midpoint of the lesson.

```html
<hr>

<h2>Health Break</h2>

<p><img src="../assets/health-break-<exercise-slug>.png" alt="illustration of the exercise"></p>

<p><strong>[Exercise Type]:</strong> [Specific instructions — breathing, stretching, grounding, hydration]</p>
```

Health break image filename uses the exercise slug (e.g., `health-break-box-breathing.png`, `health-break-full-body-stretch.png`). Always `.png` format.

### 6. Reflect & Share

```html
<hr>

<h2>Reflect & Share</h2>

<p>Before moving on, take a moment to reflect:</p>

<ol>
  <li><strong>[Reflection question 1]</strong></li>
  <li><strong>[Reflection question 2]</strong></li>
  <li><strong>[Reflection question 3]</strong></li>
</ol>

<p><strong>Share your thoughts:</strong> [What to share]</p>
<p><a href="https://skool.com/YOUR_COMMUNITY">Post in YOUR_COMMUNITY</a></p>
```

### 7. Checkpoint

```html
<hr>

<h2>Checkpoint</h2>

<p><strong>Ready for next lesson when:</strong></p>
<ul>
  <li>[Concrete checkpoint item]</li>
  <li>[Concrete checkpoint item]</li>
  <li>[Concrete checkpoint item]</li>
</ul>

<p><strong>Common Issues:</strong></p>
<ul>
  <li><strong>"[Issue description]":</strong> [Solution]</li>
  <li><strong>"[Issue description]":</strong> [Solution]</li>
</ul>

<p><strong>Stuck?</strong> Post in <a href="https://skool.com/YOUR_COMMUNITY">#setup-help</a> with screenshots.</p>
```

### 8. What's Next

```html
<hr>

<h2>What's Next</h2>

<p><strong>Next Lesson:</strong> Lesson [M.S.L] - [Title]</p>
<p><strong>Estimated Time:</strong> [X] minutes</p>

<p>[1-2 sentences teasing what's coming and why it matters]</p>

<p><strong>Continue to Lesson [M.S.L]: [Title]</strong></p>
```

---

## Callout Markers

Use these consistently for important information:

```html
<p><strong>CRITICAL:</strong> [Critical information — must know or things break]</p>

<p><strong>ACTION:</strong> [Something the reader needs to do right now]</p>

<p><strong>CAUTION:</strong> [Warning about a common mistake or gotcha]</p>

<p><strong>PRO TIP:</strong> [Helpful hint that makes things easier]</p>
```

Each callout type can optionally include ONE emoji at the start (counts toward the lesson's 1-2 emoji budget).

---

## HTML Formatting Rules for Skool

Skool uses a simplified HTML editor. These rules are NON-NEGOTIABLE:

### Allowed Elements

| Element | Usage |
|---------|-------|
| `<h1>` | Lesson title only (one per lesson) |
| `<h2>` | Major sections |
| `<h3>` | Subsections |
| `<h4>` | Rarely, sub-subsections |
| `<p>` | All paragraphs — single-line paragraphs get their own `<p>` |
| `<ul>` + `<li>` | Unordered lists |
| `<ol>` + `<li>` | Ordered lists |
| `<strong>` | Bold text |
| `<em>` | Italic text |
| `<code>` | Inline code |
| `<pre><code>` | Code blocks |
| `<blockquote>` | Callouts, direct quotes, principles |
| `<a href="">` | Links |
| `<img src="" alt="">` | Images |
| `<br>` | Line breaks within sections |
| `<hr>` | Section dividers |

### FORBIDDEN (Skool strips these)

- **NO** inline styles (`style="..."`) — EVER
- **NO** CSS classes (`class="..."`) — EVER
- **NO** JavaScript (`<script>`, `onclick`, etc.) — EVER
- **NO** `<div>` wrappers
- **NO** `<table>` elements (use lists instead)
- **NO** custom attributes
- **NO** embedded CSS (`<style>` blocks)

### Heading Hierarchy

- `<h1>` — Lesson title (ONE per lesson)
- `<h2>` — Major sections (every major topic)
- `<h3>` — Subsections within a topic
- `<h4>` — Sparingly, if at all
- NEVER go deeper than `<h4>`

### Paragraph Rules

- One thought per `<p>` tag
- Single-line paragraphs (1-3 sentences) dominate
- No paragraph exceeds 5 sentences
- Generous spacing between thought groups
- Add a `<br>` tag between consecutive `<p>` paragraphs for visible spacing in Skool
- Add a `<br>` tag before every `<hr>` section divider for extra breathing room

### List Rules

- Bullet points for related items without hierarchy
- Numbered lists for sequential steps
- Never more than 2 levels of nesting
- Each item is 1-2 sentences max

---

## Full HTML Template

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Lesson [M.S.L]: [Title]</title>
</head>
<body>

<h1>Lesson [M.S.L]: [Title]</h1>
<p><strong>Time to Complete:</strong> [X] minutes</p>

<p><img src="../assets/<M.S.L>-<slug>.png" alt="[Descriptive alt text]"></p>

<hr>

<h2>What You'll Get</h2>

<p><strong>Business Terms:</strong> [Technical deliverable description]</p>

<p><strong>AKA (In Other Words):</strong> [Conversational description]</p>

<hr>

<h2>What You'll Do</h2>

<p>[Activity overview]</p>

<p><strong>CRITICAL:</strong> [Critical callout if needed]</p>

<p><strong>ACTION:</strong> [Action required callout if needed]</p>

<hr>

<!-- CONTENT SECTIONS -->

<h2>[Section Title]</h2>

<p>[Content...]</p>

<h3>[Subsection]</h3>

<p>[Content...]</p>

<hr>

<h2>[Next Section]</h2>

<p>[Content...]</p>

<!-- HEALTH BREAK (at midpoint) -->

<hr>

<h2>Health Break</h2>

<p><img src="../assets/health-break-<exercise-slug>.png" alt="illustration of the exercise"></p>

<p><strong>[Exercise]:</strong> [Instructions]</p>

<!-- MORE CONTENT IF NEEDED -->

<hr>

<!-- REFLECT & SHARE -->

<h2>Reflect & Share</h2>

<p>Before moving on, take a moment to reflect:</p>

<ol>
  <li><strong>[Question 1]</strong></li>
  <li><strong>[Question 2]</strong></li>
  <li><strong>[Question 3]</strong></li>
</ol>

<p><strong>Share your thoughts:</strong> [Prompt]</p>
<p><a href="https://skool.com/YOUR_COMMUNITY">Post in YOUR_COMMUNITY</a></p>

<hr>

<!-- CHECKPOINT -->

<h2>Checkpoint</h2>

<p><strong>Ready for next lesson when:</strong></p>
<ul>
  <li>[Checkpoint 1]</li>
  <li>[Checkpoint 2]</li>
  <li>[Checkpoint 3]</li>
</ul>

<p><strong>Common Issues:</strong></p>
<ul>
  <li><strong>"[Issue]":</strong> [Fix]</li>
</ul>

<p><strong>Stuck?</strong> Post in <a href="https://skool.com/YOUR_COMMUNITY">#setup-help</a> with screenshots.</p>

<hr>

<!-- WHAT'S NEXT -->

<h2>What's Next</h2>

<p><strong>Next Lesson:</strong> Lesson [M.S.L] - [Title]</p>
<p><strong>Estimated Time:</strong> [X] minutes</p>

<p>[Teaser for next lesson]</p>

<p><strong>Continue to Lesson [M.S.L]: [Title]</strong></p>

</body>
</html>
```

---

## Template Checklist (QAS uses this)

### Image Assets (MANDATORY -- QAS blocks without these)
- [ ] Hero image `<img>` present after H1 title block, before "What You'll Get"
- [ ] Hero image src follows pattern `../assets/<M.S.L>-<slug>.png`
- [ ] Health break image `<img>` present in Health Break section
- [ ] Health break image src follows pattern `../assets/health-break-<exercise-slug>.png`
- [ ] All image references use `.png` extension
- [ ] All images have descriptive alt text

### Structure
- [ ] Has H1 lesson title with lesson number
- [ ] Has "Time to Complete" estimate
- [ ] Has "What You'll Get" with Business Terms + AKA
- [ ] Has "What You'll Do" with activity overview
- [ ] Has content sections with H2/H3 hierarchy
- [ ] Has Health Break at midpoint
- [ ] Has "Reflect & Share" with 3 questions
- [ ] Has Checkpoint with ready-when items and common issues
- [ ] Has "What's Next" with next lesson reference
- [ ] Uses `<hr>` between all major sections

### HTML Quality
- [ ] NO inline styles
- [ ] NO CSS classes
- [ ] NO JavaScript
- [ ] NO `<div>` wrappers
- [ ] NO `<table>` elements
- [ ] Only one `<h1>` in the document
- [ ] Proper heading hierarchy (H1 > H2 > H3 > H4)
- [ ] All lists properly nested (`<ul>/<ol>` > `<li>`)

### Content Quality
- [ ] No CTA, P.S., or sales pitch at the end
- [ ] Callout markers used appropriately
- [ ] Links point to correct destinations
- [ ] Images have alt text
