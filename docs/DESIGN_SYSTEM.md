# Design System & UI Specifications

## 1. Aesthetic Identity
- **Tone**: Professional, modern, creative workspace inspired by desktop creative tools (Figma, Canva, Lightroom).
- **Theme**: Dark Slate mode designed to give user artwork visual priority.

## 2. Color Palette
- **Canvas Backdrop**: `bg-slate-900` (`#0f172a`)
- **Panel Containers**: `bg-slate-800` (`#1e293b`)
- **Card Substrates**: `bg-slate-700/50` (`#334155`)
- **Borders & Dividers**: `border-slate-700` (`#334155`) / `border-slate-600` (`#475569`)
- **Primary Brand Accent**: Indigo (`#6366f1` / `#4f46e5`)
- **Secondary Accents**: Sky Blue (`#38bdf8`), Amber Gold (`#f59e0b`), Emerald Green (`#10b981`), Rose Red (`#f43f5e`)
- **Text Hierarchy**:
  - Primary: `text-slate-100` (`#f1f5f9`)
  - Secondary: `text-slate-400` (`#94a3b8`)
  - Muted: `text-slate-500` (`#64748b`)

## 3. Typography
- **Primary Interface**: Inter (Clean, geometric, high-legibility at micro-sizes).
- **Supported Poster Footer Fonts**:
  - `Inter`: Modern, clean tech and service designs.
  - `Montserrat`: Bold, corporate, institutional authority.
  - `Oswald`: High-impact, condensed festival and athletic banners.
  - `Playfair Display`: High-luxury serif for editorial and upscale retail.
  - `Roboto`: Neutral, balanced everyday business.

## 4. UI Architecture (Studio 4-Panel Layout)
- **Top Navigation Bar**: Brand logo, project title, Undo/Redo, Export button, and active tool indicators.
- **Left Panel (Inputs - 320px)**:
  - Collapsible accordions for Poster Upload, Logo Manager, Profile Photo Frame, Brand Details, and Custom Fields.
  - Prominent "Generate Footer" CTA.
- **Center Canvas Viewport**:
  - Pan/Zoom canvas with interactive transform matrix.
  - Poster container with SVG vector footer overlay.
  - Floating zoom controls (Zoom in, Zoom out, Fit to screen).
- **Right Panel (Properties - 280px)**:
  - Contextual properties for selected text, logo, photo, or background shape.
  - Auto-Fix All and Validation triggers.
- **Bottom Panel (Variations Strip - 160px)**:
  - Horizontal scrollable thumbnail cards of all 8 generated footer variations with one-click activation.
