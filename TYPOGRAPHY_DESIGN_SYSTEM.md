# AetherOps — Typography & Responsive Design System

## 1. Typography Standard: Amazon Ember
Amazon Ember is established as the single primary typography family across AetherOps.
- **Primary Font Family**: `"Amazon Ember", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif`
- **Monospaced Technical Font**: `"JetBrains Mono", Menlo, Monaco, Consolas, monospace` (reserved strictly for code editors, terminal output, Terraform, YAML/JSON configs, and resource identifiers).

---

## 2. Responsive Font & Sizing Scale
Following AWS Console usability principles, font sizes have been optimized to ensure readability on small screens without requiring manual zooming:
- **Base Body Text**: `1rem` (16px) on mobile viewports (<768px), `0.9375rem` (15px) on desktop viewports.
- **Secondary Text**: `0.875rem` (14px).
- **Metadata & Captions**: `0.8125rem` (13px).
- **Page Titles**: `clamp(1.5rem, 2.5vw, 2rem)`.
- **Section Headings**: `clamp(1.25rem, 2vw, 1.5rem)`.
- **Card Headings**: `1.125rem` (18px).

---

## 3. Touch Targets & Usability Enhancements
- **Touch Target Minimums**: Primary interactive controls (buttons, form inputs, select dropdowns) enforce a minimum height of 40px–48px.
- **Mobile Navigation Drawer**: Slide-over drawer with instant backdrop blur, clear hierarchy, and accessible dismissal controls.
- **Responsive Tables**: Horizontal overflow wrapping and scrollable container wrapper to prevent page breakage on narrow screens.
