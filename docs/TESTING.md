# Testing & Verification Strategy

## 1. Overview
The testing framework ensures mathematical precision, zero-overflow geometry, WCAG contrast compliance, and stable API endpoints.

## 2. Test Suites

### Backend Unit & Integration Tests (`backend/tests/`)
- Framework: `pytest` with `pytest-asyncio` / `httpx.ASGITransport`.
- Scope:
  - `test_analyzer.py`: Verifies OpenCV color extraction, dominant clustering, perceived brightness, and safe zone calculations on synthetic 1080x1080 gradient images.
  - `test_layout_engine.py`: Verifies dynamic footer sizing across portrait, square, and landscape dimensions; verifies text wrapping and column division.
  - `test_validator.py`: Verifies detection of text overflow, element collision, and low-contrast alerts.
  - `test_api.py`: Tests all FastAPI endpoints (`/api/health`, `/api/analyze`, `/api/generate`, `/api/auto-fix`, `/api/validate`, `/api/export`, `/api/projects`, `/api/brands`).
  - `test_export.py`: Verifies binary generation of PNG, JPG, SVG, and PDF exports.

### Frontend Verification
- Type validation: `tsc --noEmit` ensures strict TypeScript type safety.
- Production build validation: `npm run build` verifies Vite packaging, CSS bundling, and zero asset errors.

## 3. Running Tests

### Backend Tests
```bash
cd backend
python -m pytest tests/ -v
```

### Frontend Typecheck & Build
```bash
cd frontend
npm run build
```
