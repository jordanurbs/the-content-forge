---
name: presentation-template
version: 1.0.0
description: "Slidev presentation template, components, and brand standards for {{PROJECT_NAME}}. Auto-loaded by Presentation Designer and Quality Reviewer agents."
---

# {{PROJECT_NAME}} Presentation Template (Slidev)

This is the definitive template for creating Slidev presentations for {{PROJECT_NAME}} lessons. All presentations use the shared scaffold at `samples/presentations/`.

## Scaffold Location

The Slidev scaffold lives at `samples/presentations/` and includes:
- `components/` — Vue components (StrategyCard, InfoCard, CalloutCard, HealthBreak)
- `layouts/` — Custom layouts (cover, default, health-break, two-col, three-col)
- `styles/base.css` — Brand theme CSS
- `uno.config.ts` — UnoCSS shortcuts and theme colors
- `global-top.vue` — optional HUD overlay (see config/persona.md)

When outputting a new presentation, copy this scaffold (excluding `node_modules/`) to the output location.

## Frontmatter Template

Every slide deck starts with this frontmatter:

```yaml
---
theme: ./..
title: "Lesson Title — Descriptive Subtitle"
info: |
  Module X - Section Name
  {{PROJECT_NAME}}
lessonTitle: "SHORT TITLE"
terminalMessages:
  - "initializing_module..."
  - "loading_content..."
  - "analyzing_data..."
  - "system_ready..."
drawings:
  persist: false
transition: slide-left
mdc: true
fonts:
  provider: none
---
```

- `theme: ./..` — points to the parent directory where the scaffold theme lives
- `lessonTitle` — appears in the HUD overlay (if enabled) (keep it SHORT, uppercase)
- `terminalMessages` — rotating messages in the HUD terminal bar (4 items, snake_case with trailing `...`)

## Standard Slide Sequence

Every presentation follows this sequence:

### 1. Cover Slide

```markdown
---
layout: cover
---

# Lesson Title

### Subtitle in Cyan

A tagline or description
```

The cover layout auto-styles with the brand gradient background, gold-to-white title gradient, and cyan subtitle.

### 2. Hero Image (REQUIRED)

Full-bleed hero illustration. The Image Generator agent creates this file at `presentations/public/images/<M.S.L>-<slug>.png`.

```markdown
---

<div style="display: flex; justify-content: center; align-items: center; height: 100%;">
  <img src="./images/<M.S.L>-<slug>.png" alt="[Description]" style="max-width: 90%; max-height: 85vh; border-radius: 12px; box-shadow: 0 0 30px rgba(0,255,255,0.3);" />
</div>
```

### 3. What You'll Master

3 key objectives using StrategyCard:

```markdown
---

# What You'll Master

<p style="color: #B0C4DE; font-size: 1.1rem; margin-bottom: 1.5rem;">Brief context line</p>

<div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 1.5rem;">
  <StrategyCard title="Objective 1" titleColor="#00FFFF" v-click>
    <p>Description of first learning objective</p>
  </StrategyCard>
  <StrategyCard title="Objective 2" titleColor="#FFD700" v-click>
    <p>Description of second learning objective</p>
  </StrategyCard>
  <StrategyCard title="Objective 3" titleColor="#FFA500" v-click>
    <p>Description of third learning objective</p>
  </StrategyCard>
</div>
```

### 4-10. Content Slides

Main content. Mix these patterns:

**Comparison Slide (two columns):**
```markdown
---

# Slide Title

<div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 1.5rem;">
  <InfoCard variant="warning" v-click>
    <h3 style="color: #FF4444;">Without [thing]</h3>
    <ul style="font-size: 0.85em;">
      <li>Problem 1</li>
      <li>Problem 2</li>
    </ul>
  </InfoCard>
  <InfoCard variant="success" v-click>
    <h3 style="color: #00FF88;">With [thing]</h3>
    <ul style="font-size: 0.85em;">
      <li>Benefit 1</li>
      <li>Benefit 2</li>
    </ul>
  </InfoCard>
</div>
```

**Feature Grid (3-4 columns):**
```markdown
---

# Slide Title

<div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 1.5rem;">
  <StrategyCard title="Feature 1" titleColor="#00FFFF" v-click>
    <p>Description</p>
  </StrategyCard>
  <StrategyCard title="Feature 2" titleColor="#FFD700" v-click>
    <p>Description</p>
  </StrategyCard>
  <StrategyCard title="Feature 3" titleColor="#00FF88" v-click>
    <p>Description</p>
  </StrategyCard>
</div>
```

**Callout Slide:**
```markdown
---

# Important Point

<CalloutCard type="critical">
  <p>Critical information that must be highlighted</p>
</CalloutCard>
```

### 11. Health Break (at midpoint)

```markdown
---
layout: health-break
---

<HealthBreak title="Exercise Name" image="./images/health-break-<exercise-slug>.png" imageAlt="illustration of the exercise">
  <p>Specific instructions for the health break activity.</p>
</HealthBreak>
```

The Image Generator agent creates the health break image at `presentations/public/images/health-break-<exercise-slug>.png`. Always include the `image` and `imageAlt` props.

### 12-15. More Content Slides

Continue content after the health break.

### 16. Checkpoint

```markdown
---

# Checkpoint

<div style="display: grid; grid-template-columns: 1fr 1fr; gap: 2rem;">
  <InfoCard v-click>
    <h3 style="color: #FFD700;">Ready When You...</h3>
    <ul style="font-size: 0.8em;">
      <li>Checkpoint item 1</li>
      <li>Checkpoint item 2</li>
      <li>Checkpoint item 3</li>
    </ul>
  </InfoCard>
  <InfoCard variant="warning" v-click>
    <h3 style="color: #FF4444;">Common Concerns</h3>
    <ul style="font-size: 0.8em;">
      <li><strong>"Concern 1"</strong> -> Solution</li>
      <li><strong>"Concern 2"</strong> -> Solution</li>
    </ul>
  </InfoCard>
</div>
```

### 17. What's Next

```markdown
---

# What's Next?

<InfoCard style="max-width: 700px; margin: 0 auto 1rem;">
  <h3 style="color: #00FFFF;">Lesson [M.S.L]</h3>
  <h4 style="color: #FFFFFF;">Next Lesson Title</h4>
  <p style="margin-top: 1rem;">Brief teaser of what the next lesson covers and why it matters.</p>
</InfoCard>

<p style="text-align: center; margin-top: 1.5rem; color: #FFD700; font-family: 'SHPinscher', sans-serif; text-transform: uppercase; letter-spacing: 0.1em;" v-click>Motivational closing line.</p>
```

---

## Vue Components Reference

### StrategyCard

Card with hover effect, title, and content slot.

```html
<StrategyCard title="Card Title" titleColor="#00FFFF">
  <p>Content</p>
</StrategyCard>
```

Props:
- `title` (string) — Card heading
- `titleColor` (string) — Color hex for the title

### InfoCard

Information panel with colored left border.

```html
<InfoCard variant="default|warning|success">
  <h3>Title</h3>
  <p>Content</p>
</InfoCard>
```

Props:
- `variant` — `default` (cyan border), `warning` (red border), `success` (green border)

### CalloutCard

Attention-grabbing callout with type-based styling.

```html
<CalloutCard type="critical|action|caution|protip">
  <p>Content</p>
</CalloutCard>
```

Props:
- `type` — Determines color and label:
  - `critical` — Red, label "CRITICAL"
  - `action` — Green, label "ACTION"
  - `caution` — Orange, label "CAUTION"
  - `protip` — Cyan, label "PRO TIP"
- `icon` (optional) — Custom icon
- `label` (optional) — Override default label

### HealthBreak

Health break exercise card with optional image.

```html
<HealthBreak title="Exercise Name" image="./images/health.png" imageAlt="Description">
  <p>Exercise instructions</p>
</HealthBreak>
```

Props:
- `title` (string, required) — Exercise name
- `image` (string, optional) — Image path
- `imageAlt` (string, optional) — Alt text

---

## Brand Color Palette

| Token | Hex | Usage |
|-------|-----|-------|
| `--neon-yellow` | `#FFD700` | Headings, H2, emphasis, gold accents |
| `--neon-cyan` | `#00FFFF` | Subheadings, links, tech highlights, default card borders |
| `--electric-blue` | `#0080FF` | Secondary accent |
| `--navy-dark` | `#0A1628` | Primary background |
| `--navy-medium` | `#1A2744` | Secondary background, card backgrounds |
| `--navy-light` | `#2A3F5F` | Borders, subtle accents |
| `--accent-gold` | `#FFA500` | Third accent, warnings |
| `--warning-red` | `#FF4444` | Errors, critical callouts |
| `--success-green` | `#00FF88` | Success states, health breaks |
| `--text-primary` | `#FFFFFF` | Main headings, bold text |
| `--text-secondary` | `#B0C4DE` | Body text, descriptions |
| `--text-muted` | `#708090` | Subtle text, meta info |

### Color Assignment for titleColor

When using multiple StrategyCards in a grid, cycle through these colors:
1. `#00FFFF` (cyan)
2. `#FFD700` (gold)
3. `#FFA500` (orange)
4. `#00FF88` (green)

---

## UnoCSS Shortcuts

These shortcuts are defined in `uno.config.ts` and can be used as CSS classes:

| Shortcut | Effect |
|----------|--------|
| `strategy-card` | Card with navy bg, border, rounded, hover effect |
| `info-card` | Panel with cyan left border |
| `info-card-warning` | Red left border override |
| `info-card-success` | Green left border override |
| `hero-title` | Gold-to-white gradient text |
| `page-title` | Gold colored heading |
| `page-description` | Secondary text, larger size |
| `grid-two-col` | 2-column CSS grid with gap |
| `grid-three-col` | 3-column CSS grid with gap |
| `grid-auto` | Auto-fit grid (min 250px columns) |

---

## Progressive Reveals

Use `v-click` on elements for step-by-step reveals:

```html
<StrategyCard title="Point 1" v-click>...</StrategyCard>
<StrategyCard title="Point 2" v-click>...</StrategyCard>
<StrategyCard title="Point 3" v-click>...</StrategyCard>
```

This shows each card on successive clicks/arrow presses.

---

## Slide Count Guidelines

- **Minimum**: 10 slides
- **Maximum**: 18 slides
- **Sweet spot**: 12-15 slides
- Health break should fall around slide 8-10

---

## Fonts

The theme uses two fonts:
- **SHPinscher** — Headings (uppercase, letter-spaced)
- **Courier Prime Code** — Body text (monospace)

Set `fonts.provider: none` in frontmatter (fonts are loaded by the theme).

---

## Presentation Quality Checklist (QAS uses this)

- [ ] 10-18 slides total
- [ ] Cover slide uses cover layout with title/subtitle
- [ ] Hero image slide present (REQUIRED) with `./images/<M.S.L>-<slug>.png`
- [ ] "What You'll Master" slide with 3 StrategyCards
- [ ] Content slides use Vue components (not raw HTML cards)
- [ ] Health break at midpoint using health-break layout
- [ ] HealthBreak component includes `image` prop with `./images/health-break-<exercise-slug>.png`
- [ ] Checkpoint slide with ready-when + common concerns
- [ ] What's Next slide with next lesson preview
- [ ] Progressive reveals (`v-click`) on key content
- [ ] Brand colors match the palette exactly
- [ ] Text is concise (not walls of text on slides)
- [ ] Frontmatter includes all required fields
- [ ] `terminalMessages` has 4 items in snake_case
