# AI Footer Designer / Footer Studio 🎨✨

A Canva-like automated footer design platform for promotional posters, event flyers, and social media banners. Powered by computer vision algorithms (OpenCV & NumPy), a deterministic layout engine, and an interactive React studio.

---

## 🚀 Quick Start Guide (Windows)

### Prerequisites
- **Python 3.10+** (tested on Python 3.13)
- **Node.js 18+** & **npm** (tested on Node.js 24)

### 1. Backend Setup & Startup
Open a PowerShell terminal in the project root:
```powershell
cd backend
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```
*The backend API will start on `http://127.0.0.1:8000`. Automatic OpenAPI documentation is available at `http://127.0.0.1:8000/docs`.*

### 2. Frontend Setup & Startup
Open a second PowerShell terminal in the project root:
```powershell
cd frontend
npm run dev
```
*The web studio will start on `http://localhost:5173`.*

---

## 🧪 Running Automated Tests

### Backend Unit & Integration Tests (pytest)
```powershell
cd backend
python -m pytest tests/test_api.py -v
```
*Runs all 9 test suites verifying API health, computer vision color analysis, multi-variation layout generation, auto-fix geometry corrections, validation, and project/brand persistence.*

### Frontend Production Build & Typecheck
```powershell
cd frontend
npm run build
```
*Validates TypeScript strict types and produces an optimized production bundle in `dist/`.*

---

## 📂 Project Architecture ("Pehle docs, phir code")

```
├── docs/
│   ├── ARCHITECTURE.md     # System topology and data flow diagram
│   ├── CODE_STYLE.md       # Python & TypeScript engineering standards
│   ├── DATABASE.md         # Schema definitions and storage service specs
│   ├── DESIGN_SYSTEM.md    # Dark slate theme and UI specifications
│   ├── PRD.md              # Product Requirements Document
│   ├── SECURITY.md         # Data safety, validation, and CORS policies
│   └── TESTING.md          # Test strategy and execution guide
├── AGENTS.md               # Autonomous Agent Roles and operating principles
├── BUILD_STATUS.md         # Real-time milestone tracker
├── backend/
│   ├── app/
│   │   ├── main.py                     # FastAPI REST API endpoints
│   │   ├── analyzer/                   # OpenCV & computer vision analyzer
│   │   │   ├── color_analyzer.py       # K-Means dominant color extraction & WCAG contrast
│   │   │   ├── space_detector.py       # Canny edge density & safe-margin detection
│   │   │   ├── content_analyzer.py     # Content density & column calculators
│   │   │   └── poster_analyzer.py      # Unified poster analysis orchestrator
│   │   ├── engine/                     # Deterministic layout & sizing algorithms
│   │   │   ├── layout_engine.py        # 8 distinct style presets (Modern, Wave, Luxury, etc.)
│   │   │   ├── size_calculator.py      # Proportional dimensioning & aspect-ratio preservation
│   │   │   ├── spacing_engine.py       # Grid gutters and padding distribution
│   │   │   ├── typography_engine.py    # Resolution-aware font scaling & line wrapping
│   │   │   └── auto_adjust.py          # Auto Fix All overlap & boundary correction
│   │   ├── design_library/             # Reusable vector shapes, frames, and icons
│   │   │   ├── shapes/footer_shapes.py # 12 scalable SVG background shapes
│   │   │   ├── icons/svg_icons.py      # 15 inline SVG branding icons
│   │   │   └── photo_frames/frames.py  # Circle, rounded, arch, and square frames
│   │   ├── renderer/
│   │   │   ├── svg_renderer.py         # Scalable SVG markup generation
│   │   │   └── footer_renderer.py      # High-res Pillow raster compositor
│   │   ├── validator/
│   │   │   └── layout_validator.py     # Quality score (0-100) & overflow checker
│   │   ├── services/
│   │   │   ├── storage_service.py      # Standalone JSON DB with MongoDB adapter
│   │   │   └── export_service.py       # PNG, JPG, SVG, and PDF high-DPI export
│   │   └── models/                     # Pydantic schemas (Brand, Footer, Poster, Project)
│   ├── data/                           # Local JSON persistence storage
│   ├── uploads/                        # Image uploads directory
│   └── tests/test_api.py               # Comprehensive pytest test suite
├── frontend/
│   ├── src/
│   │   ├── App.tsx                     # Main application layout with navigation
│   │   ├── components/
│   │   │   ├── Sidebar.tsx             # Studio, Brand Kit, Templates, Projects, Settings nav
│   │   │   └── studio/
│   │   │       ├── InputPanel.tsx      # Poster, logo, profile, brand form inputs
│   │   │       ├── CanvasPanel.tsx     # Zoomable, pannable interactive design canvas
│   │   │       ├── PropertiesPanel.tsx # Element font/color/size & Auto-Fix controls
│   │   │       ├── VariationsPanel.tsx # 8-card horizontal preview carousel
│   │   │       └── ExportModal.tsx     # PNG/JPG/SVG/PDF export modal
│   │   ├── pages/                      # Studio, Dashboard, BrandKit, Projects, Templates, Settings
│   │   ├── store/editorStore.ts        # Zustand global reactive editor state
│   │   ├── api/client.ts               # Backend API integration client
│   │   └── types/index.ts              # Strict TypeScript models
│   ├── package.json
│   ├── vite.config.ts
│   └── tailwind.config.js
```

---

## 🌟 Key Capabilities
1. **Computer Vision Poster Analysis**: Automatically clusters dominant colors using OpenCV K-Means, calculates perceived luminance, and identifies safe bottom regions using Canny edge density.
2. **Deterministic Layout Generation**: Produces 8 structurally distinct variations (Modern Studio, Corporate Pro, Minimalist Clean, Creative Wave, Premium Luxury, Festival Vibrant, Split Duo Banner, Floating Capsule).
3. **Aspect Ratio Preservation**: Logos and profile photos never stretch or distort.
4. **Auto Fix All**: Intelligently resolves element collisions, boundary overflows, and enhances text contrast to meet WCAG AA standards.
5. **Interactive Canvas**: High-fidelity vector overlay with zoom (10%-300%), pan, selection, and direct text/styling customization.
6. **High-Resolution Multi-Format Export**: Renders to exact poster pixel dimensions in PNG, JPG (95% quality), standalone SVG, or print-ready PDF.
7. **Zero Paid Dependencies**: Runs 100% locally on standard open-source Python and React libraries.
