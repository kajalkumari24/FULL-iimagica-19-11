# Security & Data Safety Guidelines

## 1. Local Processing & Privacy
- **Zero Third-Party Image Leaks**: Image analysis and vector generation run entirely locally on the host machine using OpenCV and NumPy. Posters, personal photos, and corporate logos are never sent to external AI vendors by default.
- **Optional AI Keys**: When external LLM/Vision APIs are configured in `.env`, keys are read strictly through environment variables and never logged or exposed in client bundles.

## 2. Input Validation & File Handling
- **Image Content Sanitization**: Uploaded files are verified by OpenCV / Pillow byte decoders. Malformed files, corrupted headers, or non-image payloads are rejected with explicit HTTP 400 errors.
- **MIME & Extension Whitelist**: Only `.png`, `.jpg`, `.jpeg`, `.webp` file formats are parsed.
- **Path Traversal Prevention**: File writes utilize UUIDs and sanitized project identifiers to prevent directory traversal attacks.

## 3. Web & API Security
- **CORS Protection**: FastAPI is pre-configured with restrictive origins (`http://localhost:5173`, `http://127.0.0.1:5173`).
- **SVG Injection Prevention**: All dynamic text strings injected into SVG markup pass through `html.escape()` sanitization to prevent XSS payloads in exported vectors.
- **Resource Constraints**: High-resolution image resizing applies memory-safe streaming and downsampling during K-Means clustering to prevent memory exhaustion attacks.
