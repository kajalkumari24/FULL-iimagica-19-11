# Code Style & Engineering Standards

## 1. Python Backend Standards
- **Style Guide**: PEP 8 compliance.
- **Type Annotations**: Comprehensive type hints using Python's `typing` module (`List`, `Dict`, `Optional`, `Tuple`, `Any`) and Pydantic models.
- **Error Handling**: Explicit HTTP exceptions (`HTTPException`) with meaningful status codes and descriptive error details.
- **Imports**: Grouped logically:
  1. Standard library (`os`, `io`, `json`, `uuid`)
  2. Third-party packages (`fastapi`, `cv2`, `numpy`, `PIL`, `pydantic`)
  3. Local application modules (`from app.models... import ...`)
- **Immutability & Pure Functions**: Calculation engines (`TypographyEngine`, `SizeCalculator`, `SpacingEngine`) must be deterministic and side-effect free.

## 2. Frontend React / TypeScript Standards
- **Type Safety**: No implicit `any`. All state and props must be typed through interfaces defined in `src/types/index.ts`.
- **Component Design**: Modular, single-responsibility functional components with hooks.
- **State Separation**:
  - Global editor state resides in Zustand (`src/store/editorStore.ts`).
  - Ephemeral UI state (open modals, dropdown toggles) resides in local component state (`useState`).
- **Styling Conventions**:
  - Tailwind utility classes for layout, spacing, and colors.
  - Consistent dark slate theme palette (`slate-900` canvas, `slate-800` panels, `slate-700` borders, `indigo-500/600` primary accents).
  - Explicit flex/grid containment to prevent UI layout jumps.

## 3. Version Control & File Organization
- Lowercase snake_case for Python modules (`poster_analyzer.py`, `layout_engine.py`).
- PascalCase for React components (`InputPanel.tsx`, `CanvasPanel.tsx`).
- kebab-case or camelCase for utilities and styling files.
- All configuration files (`vite.config.ts`, `tailwind.config.js`) kept lean and modular.
