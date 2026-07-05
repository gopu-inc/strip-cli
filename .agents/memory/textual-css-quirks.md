---
name: Textual CSS quirks
description: Non-obvious CSS limitations in the Textual framework that cause runtime errors or silent failures.
---

# Textual CSS quirks

## `display` property — no `flex`
`widget.styles.display` only accepts `"block"` or `"none"`. Assigning `"flex"` raises `StyleValueError` at runtime.

**Why:** Textual has its own layout engine; `flex` is not a recognized display value.

**How to apply:** Replace any `styles.display = "flex"` with `styles.display = "block"`.

## No descendant/child selectors
Textual CSS does not support CSS descendant or child combinators.

```css
/* INVALID — causes parse error */
Markdown h1 { color: red; }
Container > Button { background: blue; }

/* VALID — use the Textual widget class name directly */
MarkdownH1 { color: red; }
Button { background: blue; }
```

**Why:** Textual uses its own CSS parser that is a strict subset of browser CSS.

**How to apply:** Always target Textual widget class names directly. For Markdown heading colours use `MarkdownH1`, `MarkdownH2`, `MarkdownH3`; for code blocks use `MarkdownFence`.
