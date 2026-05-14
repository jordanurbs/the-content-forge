# Persona Config

The Content Forge's image-generator and storyboarder agents check this file when constructing prompts. If it is **empty or contains only comments**, agents generate persona-free illustrations (scene + concept only).

If you want a recurring character to appear across hero images and intro/outro video cards, write the **physical description** below.

## Important rules

- **Never include the persona's name** in the description — image models often render names as on-screen text.
- Use only physical attributes (clothing, build, expression, props, distinctive features).
- Keep it consistent across runs — agents will copy this description verbatim into every persona prompt.

---

## Persona Description

<!--
Example (DELETE THIS COMMENT and replace with your own):

a stylized illustrated character with [hair color/style], wearing [clothing], holding [optional prop], with [facial expression / pose], in a [style/aesthetic] illustration style
-->

[Leave empty for no persona — illustrations will be scene-only.]
