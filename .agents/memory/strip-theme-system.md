---
name: STRIP TUI theme system
description: How 4-theme switching works in the STRIP Textual app, and where to add new theme rules.
---

# STRIP TUI theme system

The theme system applies CSS class names to the root `App` widget. Textual cascades those classes down to all children via CSS specificity.

**Theme classes:** (none) = dark default, `theme-cyber`, `theme-ocean`, `theme-sunset`

**How switching works:**
1. User clicks a theme button in `screens/settings.py` → posts `ThemeChanged(name)` message
2. `app.py` handles `on_theme_changed` → clears old theme class, adds new one, saves to `Config`
3. App restores saved theme on `on_mount`

**Where theme rules live:**
- `styles/app.tcss` — ALL theme rules, including per-screen widget overrides
- Per-screen `CSS` strings in each screen file contain *dark-default* hardcoded hex values only
- Theme overrides for every per-screen widget ID (e.g. `#feed-header`, `VideoCard`, `#dash-nav`) are in the "PER-SCREEN THEME OVERRIDES" section at the bottom of `app.tcss`

**Why:**
Textual CSS class inheritance only works for rules in the App's stylesheet. Rules in per-screen `CSS` class attributes are injected into the same stylesheet but can be overridden by more-specific `App.theme-X #widget-id` rules in `app.tcss`.

**How to apply:**
Any new widget with a hardcoded background/color in a screen's `CSS` string needs a corresponding `App.theme-cyber/ocean/sunset` override added to the "PER-SCREEN THEME OVERRIDES" section of `app.tcss`.
