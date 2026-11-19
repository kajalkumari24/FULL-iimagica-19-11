# Product Requirements Document (PRD) — AI Footer Designer / Footer Studio

## 1. Executive Summary
**AI Footer Designer / Footer Studio** is a Canva-like desktop web application that automates the generation, styling, and alignment of professional poster footers. Users upload posters, logos, profile pictures, and brand details, and the application's computer vision and **Adaptive SVG Design Engine** automatically analyze color harmonies, contrast, and visual margins to deliver responsive, mathematically balanced, editable footer variations.

## 2. Target Audience & Problem Statement
- **Users**: Business owners, marketing agencies, content creators, and non-designers needing fast, publication-grade branding footers on promotional posters, social media banners, and event flyers.
- **Pain Point**: Static or downloaded SVG templates fail when applied across different poster resolutions and aspect ratios (9:16 story, 1:1 square, 16:9 banner). Rigid SVGs cause squished text, warped logos, clipped contacts, and awkward whitespace.
- **Solution**: An **Adaptive SVG Design Engine** utilizing dynamic `viewBox` definitions, parametric shape formulas, zone-based responsive positioning, and WCAG AA contrast enforcement.

## 3. Core Features & Functional Scope

### A. Automatic Poster Analysis
- **Image Ingestion**: Supports PNG, JPG, and WebP up to high-resolution (4K+).
- **Dimension & Aspect Ratio Detection**: Identifies portrait (9:16, 4:5), square (1:1), and landscape (16:9).
- **Color Extraction**: K-Means clustering in OpenCV/NumPy extracts top dominant colors and calculates perceived luminance.
- **Safe Zone & Clutter Detection**: Canny edge density across vertical bands identifies uncluttered bottom regions for footer placement.
- **Palette Suggestion**: Auto-recommends high-contrast backgrounds and matching accents.

### B. Adaptive SVG Design Engine
- **18 Reusable Base Shapes**:
  1. `classic_rectangle`: Standard full-bleed corporate bar.
  2. `rounded_box`: Proportional corner radius box.
  3. `fluid_wave_single`: Parametric sinusoidal wave top with clamped amplitude.
  4. `fluid_wave_double`: Layered dual wave with depth transparency.
  5. `convex_curve`: Gentle upward arched curve.
  6. `concave_curve`: Elegant dipped center curve.
  7. `diagonal_bevel`: Left-to-right slanted header.
  8. `diagonal_reverse`: Right-to-left slanted header.
  9. `executive_ribbon`: High-contrast top accent stripe.
  10. `floating_capsule`: Pill-shaped inset card with rounded ends and drop shadow.
  11. `floating_card`: Modern card inset with margin offsets and shadow.
  12. `double_layer_offset`: Layered dual cards with offset secondary accent.
  13. `split_banner`: Vertical 30/70 block split separating brand from contacts.
  14. `split_angled`: Diagonal 35/65 cut separating hero identity from contact grid.
  15. `arch_dome`: Soft arched center with tapered sides.
  16. `center_notch`: Header with elevated center badge for logo/profile emphasis.
  17. `accent_bar_minimal`: Translucent card with bright top neon line.
  18. `frosted_glass`: Frosted glass container with subtle border stroke.

- **Zone-Based Content Distribution**:
  - `identity_zone`: Logo + Brand Name + Tagline with aspect-ratio preservation.
  - `contacts_zone`: Phone, WhatsApp, Email, Website in auto-wrapping column matrices.
  - `actions_zone`: CTA Button, Address, QR Code, Social Badges.
  - `profile_zone`: Avatar placement with circle, arch, rounded, or square clip-paths.

- **Aspect Ratio Adaptability**:
  - **Portrait (9:16)**: Height ratio `0.11 - 0.14`, 2-column or stacked layout to prevent horizontal crowding.
  - **Square (1:1)**: Height ratio `0.14 - 0.17`, 3-column balanced distribution.
  - **Landscape (16:9)**: Height ratio `0.18 - 0.24`, wide 3-4 column layout with ample breathing room.

- **SVG Repair & Validation**:
  - Sanitizes external SVGs, repairs missing `viewBox` coordinates, strips hardcoded dimension tags, and rejects unrepairable inputs with automatic fallback to nearest adaptive template.

### C. Live Studio Editor & Manual Overrides
- **Interactive Canvas**: High-fidelity SVG overlay on poster with zoom (10%-300%), pan, and boundary guides.
- **Properties Panel**: Granular controls for fonts, weights, colors, line heights, dimensions, frame shapes (circle, rounded, arch, square), and opacity.
- **Auto Fix All**: One-click correction for text overflow, bounding overlaps, uneven spacing, and low contrast.
- **Variations Carousel**: Live preview strip allowing instant style switching.

### D. Multi-Format High-Resolution Export
- Export to PNG, JPG (quality 95), standalone SVG, and print-ready PDF at exact original poster dimensions.

### E. Brand & Project Management
- Save and switch reusable brand profiles (logos, colors, contact presets).
- Project persistence with duplicate, open, and delete capabilities (local JSON storage with optional MongoDB adapter).
