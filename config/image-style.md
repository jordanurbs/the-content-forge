# Image Style Config

Defines the Brand DNA suffix appended to every Venice AI prompt, and the negative prompt always included.

The image-generator and storyboarder agents read this file. If it's missing or empty, they fall back to a minimal default derived from `config/theme.json`.

---

## Brand DNA Suffix (appended to ALL image prompts)

```
clean illustration, dark navy background, subtle blue-gray gradients, sharp vector-style edges, muted teal and warm gold accents, modern tech aesthetic, polished infographic style, soft ambient lighting, high detail, cinematic composition
```

---

## Negative Prompt (always included with --negative-prompt)

```
blurry, low quality, watermark, photorealistic, stock photo
```

---

## How to Customize

1. Rewrite the **Brand DNA Suffix** to match your visual identity. Reference your `config/theme.json` colors directly in the prompt for cohesion.
2. Adjust the **Negative Prompt** to forbid aesthetics that conflict with your brand (e.g., add "neon, synthwave, pixel art" if you want a clean corporate look; remove restrictions if you want vintage aesthetics).
3. Test by running a single image generation manually and iterating until the output matches your brand expectations.

The agents will read this file fresh on each pipeline run, so changes take effect immediately.
