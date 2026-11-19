# Database & Persistence Specification

## 1. Storage Strategy
AI Footer Designer uses a dual-mode persistence architecture:
1. **Local File-System JSON Database (Default)**: Zero-setup, standalone file-based persistence storing projects and brand profiles under `backend/data/`.
2. **MongoDB Integration (Configurable)**: Pluggable database driver activated via environment variables (`MONGODB_URI`, `MONGODB_DB_NAME`) when distributed persistence is required.

The application remains 100% operational in offline and local desktop environments without MongoDB.

## 2. Schema Definitions

### A. Projects Collection (`projects.json` / `projects`)
```json
{
  "id": "proj_abc123",
  "name": "Summer Festival Flyer",
  "created_at": "2026-11-19T10:00:00Z",
  "updated_at": "2026-11-19T10:30:00Z",
  "poster_filename": "poster.png",
  "poster_data_url": "data:image/png;base64,...",
  "poster_width": 1080,
  "poster_height": 1920,
  "brand": {
    "brand_name": "Apex Sound",
    "phone": "+1 555-0192",
    "email": "contact@apexsound.com"
  },
  "active_footer": {
    "id": "var_creative",
    "name": "Creative Wave",
    "width": 1080.0,
    "height": 280.0,
    "x": 0.0,
    "y": 1640.0,
    "background": { ... },
    "elements": [ ... ]
  },
  "footer_variations": [ ... ],
  "thumbnail_url": null,
  "tags": ["event", "festival"]
}
```

### B. Brands Collection (`brands.json` / `brands`)
```json
{
  "id": "brand_default",
  "brand_name": "Acme Innovations",
  "tagline": "Building Tomorrow Today",
  "phone": "+1 234 567 8900",
  "whatsapp": "+1 234 567 8900",
  "email": "hello@acme.com",
  "website": "www.acme.com",
  "address": "100 Market St, Suite 400",
  "cta": "Get A Free Quote",
  "primary_color": "#0f172a",
  "secondary_color": "#3b82f6",
  "accent_color": "#f59e0b",
  "font_family": "Inter",
  "logos": [
    {
      "id": "logo_1",
      "name": "Primary Logo",
      "url": "data:image/png;base64,...",
      "aspect_ratio": 2.5
    }
  ],
  "profiles": [
    {
      "id": "prof_1",
      "name": "Founder",
      "url": "data:image/png;base64,...",
      "frame_style": "circle"
    }
  ],
  "custom_fields": [
    {
      "id": "cf_1",
      "label": "Licence #",
      "value": "CA-88912",
      "icon": "info",
      "order": 1,
      "visible": true
    }
  ]
}
```

## 3. Storage Service Implementation
The `StorageService` class (`app/services/storage_service.py`) encapsulates all read, write, update, duplicate, and delete operations with transactional thread safety and automated file creation.
