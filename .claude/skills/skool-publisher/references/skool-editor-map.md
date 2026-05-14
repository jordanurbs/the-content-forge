# Skool Editor DOM Map

Discovered 2026-02-18 via Camofox browser automation against www.skool.com.

## Status: DISCOVERED

Skool uses React with styled-components. The classroom editor is TipTap (ProseMirror-based).

## Course Page (Classroom View)

### Navigation
- **Module title**: `[class*="CourseMenuTopTitle"]` — shows module name (e.g., "3️⃣ Knowledge Infrastructure")
- **Section buttons**: `button` containing section name in sidebar (e.g., button "Context Engineering 101")
- **Page items**: `button` containing page name, with nested `link` to page URL

### Course Dropdown (Admin Actions)
- **Trigger**: `[class*="CourseDropdownMenu"] [class*="DropdownButton"]` — three-dot menu at module level
- **Add page**: `[data-testid="dropdown-item-0"]` — creates a new page (lesson) in the module
- **Add folder**: `[data-testid="dropdown-item-1"]` — creates a new folder (section) in the module

### Page Kebab Menu (Per-Page Actions)
- **Trigger**: `[class*="MenuItemDropdownMenu"] [class*="DropdownButton"]` — indexed by sidebar position (0-based)
- **Edit page**: `[data-testid="dropdown-item-0"]`
- **Revert to draft**: `[data-testid="dropdown-item-1"]`
- **Change folder**: `[data-testid="dropdown-item-2"]`
- **Duplicate**: `[data-testid="dropdown-item-3"]`
- **Drip status**: `[data-testid="dropdown-item-4"]`
- **Delete**: `[data-testid="dropdown-item-5"]` — opens confirmation modal

## Lesson Editor (Edit Mode)

### Activation
- **Pencil button**: Second `button` inside `[class*="CourseModuleWrapper"]` (SVG path starts with `M19.2555`)
- Clicking the pencil button activates edit mode, revealing the toolbar, title input, and TipTap editor

### Title
- **Input**: `input[placeholder="Title"]` — class `styled__SingleLineInput-sc-1saiqqb-1`
- Set value using native setter: `Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set`
- Dispatch `input` + `change` events with `{bubbles: true}`

### Body Editor (TipTap/ProseMirror)
- **Selector**: `.tiptap.ProseMirror.skool-editor2` (or `.tiptap.ProseMirror`)
- **Type**: contenteditable div (TipTap/ProseMirror)
- **HTML injection**: Set `editor.innerHTML = htmlContent`, then dispatch `input` + `change` events
- TipTap re-parses injected HTML and wraps list items in `<p>` tags (standard behavior)
- Supported elements: `<h1>`-`<h4>`, `<p>`, `<strong>`, `<em>`, `<s>`, `<code>`, `<pre>`, `<ul>`, `<ol>`, `<li>`, `<blockquote>`, `<a>`, `<img>`, `<hr>`

### Toolbar Buttons (ARIA refs in edit mode)
- Heading 1, Heading 2, Heading 3, Heading 4
- Bold, Italic, Strikethrough, Inline code
- Bullet list, Numbered list, Blockquote, Code block
- Image, Link, Horizontal rule, Add video

### Action Buttons
- **ADD**: button "ADD" — opens dropdown for additional content types
- **Published**: button "Published" — toggle between Published/Draft state (class `styled__ToggleWrapper`)
- **CANCEL**: button "CANCEL" — exits edit mode without saving
- **SAVE**: button "SAVE" — saves changes (disabled when no changes; enabled after title or body modification)

## Delete Confirmation Modal
- **Modal wrapper**: `.skool-ui-base-modal`
- **Text**: "Delete page? Are you sure you want to delete the page {name}? You can't undo this."
- **Cancel**: first button in modal footer
- **Delete**: second button in modal footer (shows loading spinner while processing)
- Both buttons become disabled during delete processing

## Workflow: Creating a New Folder (Section)

1. Click course dropdown trigger
2. Click "Add folder" (`[data-testid="dropdown-item-1"]`)
3. A form appears at the bottom of the sidebar with:
   - Text input for folder name (find via visible `input[type="text"]`)
   - Character counter "Name 0 / 50"
   - "Published" toggle, "Cancel" button, "Add" button (disabled until name entered)
4. Set folder name using native HTMLInputElement value setter + `input`/`change` events
5. Click "Add" button (becomes enabled after name is set)
6. Folder appears in sidebar; pages can be dragged into it manually

## Workflow: Creating a New Lesson

1. Click course dropdown trigger
2. Click "Add page" (`[data-testid="dropdown-item-0"]`)
3. Page auto-creates with title "New page" and navigates to it in edit mode
4. Set title via `input[placeholder="Title"]` (native value setter + events)
5. Inject HTML via `.tiptap.ProseMirror` innerHTML + events
6. Click SAVE button
7. (Optional) Set Published/Draft state

## Workflow: Editing an Existing Lesson

1. Click lesson name in sidebar to navigate to it
2. Click the pencil button (second button in `[class*="CourseModuleWrapper"]`)
3. Modify title and/or body
4. Click SAVE

## Notes

- Camofox session timeout: default 5 min idle (`BROWSER_IDLE_TIMEOUT_MS`). Set to 3600000 (1 hour) for long publishing runs.
- Cookies must be imported via `POST /sessions/{userId}/cookies` with `Authorization: Bearer {CAMOFOX_API_KEY}`
- Tab creation requires both `userId` and `sessionKey` params
- Snapshot endpoint requires `userId` as query param: `GET /tabs/{tabId}/snapshot?userId={userId}`
- The new `/act` evaluate kind allows arbitrary JS execution: `POST /act` with `{userId, targetId, kind: "evaluate", script: "..."}`
