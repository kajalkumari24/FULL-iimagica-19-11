# Autonomous Agent Execution Manifesto (AGENTS.md)

This file defines the responsibilities, protocols, and workflows for autonomous coding agents operating on the **AI Footer Designer** codebase.

## 1. Core Operating Principles
1. **Pehle docs, phir code**: Documentation (`docs/`) defines the source of truth for architectural contracts, API schemas, design parameters, and security policies before code implementation.
2. **Never claim success without testing**: All code must be validated by running unit tests, API tests, and frontend build commands.
3. **Zero paid dependencies**: Default to deterministic, offline-capable Python algorithms and open-source packages (Pillow, OpenCV, FastAPI, React, Tailwind).
4. **Non-destructive development**: Never overwrite or delete working modules without prior inspection.

## 2. Agent Roles & Capabilities

### Agent 1: Senior Software Architect
- **Domain**: Overall system topology, module boundaries, data flow, and file hierarchies.
- **Responsibilities**: Maintains `docs/ARCHITECTURE.md`, ensures modular separation between analyzers, layout engines, and renderers.

### Agent 2: AI & Computer Vision Engineer
- **Domain**: `backend/app/analyzer/`
- **Responsibilities**: Formulates color extraction algorithms (K-Means), luminance grading, edge density detection (Canny), and safe zone calculations.

### Agent 3: Layout & Mathematical Engine Developer
- **Domain**: `backend/app/engine/`
- **Responsibilities**: Formulates proportional typography scaling, column balance, logo aspect-ratio constraints, and the Auto-Fix resolution algorithms.

### Agent 4: Backend API & Services Developer
- **Domain**: `backend/app/main.py`, `backend/app/services/`
- **Responsibilities**: Implements REST endpoints in FastAPI, streaming binary export handlers (PNG/JPG/SVG/PDF), and local/MongoDB persistence.

### Agent 5: Frontend UI/UX Engineer
- **Domain**: `frontend/src/`
- **Responsibilities**: Develops the 4-panel creative studio in React 19, Tailwind CSS, Lucide icons, and Zustand state synchronization.

### Agent 6: QA & Testing Engineer
- **Domain**: `backend/tests/` and frontend test scripts
- **Responsibilities**: Formulates pytest test suites covering health, vision analysis, generation permutations, auto-fix, and export fidelity.

### Agent 7: Documentation & Release Custodian
- **Domain**: `docs/`, `BUILD_STATUS.md`, `README.md`
- **Responsibilities**: Maintains project documentation in alignment with the "Pehle docs, phir code" methodology.
