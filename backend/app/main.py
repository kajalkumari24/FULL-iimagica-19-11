"""
AI Footer Designer — FastAPI backend.
"""

import os
import io
import uuid
import base64
from pathlib import Path
from typing import List, Optional, Dict, Any

from fastapi import FastAPI, UploadFile, File, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import StreamingResponse, RedirectResponse
from pydantic import BaseModel

from app.models.brand import BrandProfile
from app.models.footer import FooterDesign, GenerationRequest
from app.models.poster import PosterAnalysis
from app.models.project import Project
from app.analyzer.poster_analyzer import PosterAnalyzer
from app.engine.layout_engine import LayoutEngine
from app.engine.auto_adjust import AutoAdjust
from app.engine.arrangement_engine import ArrangementEngine
from app.engine.typography_engine import TypographyEngine
from app.validator.layout_validator import LayoutValidator
from app.services.storage_service import StorageService
from app.services.export_service import ExportService
from app.renderer.footer_renderer import FooterRenderer
from app.renderer.svg_renderer import SVGRenderer
from app.engine.adaptive_layout_engine import AdaptiveLayoutEngine
from app.design_library.templates.adaptive_templates import ADAPTIVE_TEMPLATES_REGISTRY
from app.engine.svg_repair import SVGRepair
from app.analyzer.logo_color_extractor import logo_color_extractor, LogoPalette, ColorScheme
from app.engine.color_theme_engine import color_theme_engine

# ---------------------------------------------------------------------------
# Directories & App
# ---------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent  # backend/
UPLOADS_DIR = BASE_DIR / "uploads"
DATA_DIR = BASE_DIR / "data"

UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
DATA_DIR.mkdir(parents=True, exist_ok=True)

app = FastAPI(
    title="AI Footer Designer API",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static file serving for uploads
if UPLOADS_DIR.exists():
    app.mount("/uploads", StaticFiles(directory=str(UPLOADS_DIR)), name="uploads")

# ---------------------------------------------------------------------------
# Singletons
# ---------------------------------------------------------------------------
poster_analyzer = PosterAnalyzer()
layout_engine = LayoutEngine()
storage = StorageService()

# ===== Request / Response helper models ====================================
class AutoFixRequest(BaseModel):
    footer: FooterDesign
    poster_width: int = 1080
    poster_height: int = 1080

class AutoFixResponse(BaseModel):
    footer: FooterDesign
    changes: List[str]
    validation_report: Optional[Dict[str, Any]] = None

class ValidateRequest(BaseModel):
    footer: FooterDesign

class ExportRequest(BaseModel):
    poster_data_url: Optional[str] = None
    footer: FooterDesign
    format: str = "png"
    poster_width: int = 1080
    poster_height: int = 1080

class RepairSvgRequest(BaseModel):
    svg_content: str
    target_width: float = 1080.0
    target_height: float = 160.0

class RearrangeRequest(BaseModel):
    footer: FooterDesign
    arrangement: str
    brand: BrandProfile
    poster_width: float = 1080.0
    poster_height: float = 1080.0

class PositionOptionsRequest(BaseModel):
    footer: FooterDesign
    brand: BrandProfile
    poster_width: float = 1080.0
    poster_height: float = 1080.0

# ===== Root & Health ==========================================================
@app.get("/")
def root():
    return RedirectResponse(url="/docs")

@app.get("/health")
@app.get("/api/health")
def health():
    return {"status": "ok", "service": "ai-footer-designer"}

# ===== Adaptive Templates =====================================================
@app.get("/api/templates")
def list_templates():
    return [t.model_dump() for t in ADAPTIVE_TEMPLATES_REGISTRY]

# ===== SVG Repair & Validation ================================================
@app.post("/api/repair-svg")
def repair_svg(req: RepairSvgRequest):
    return SVGRepair.inspect_and_repair(
        svg_content=req.svg_content,
        target_width=req.target_width,
        target_height=req.target_height,
    )

MAX_FILE_SIZE = 25 * 1024 * 1024  # 25 MB
ALLOWED_MIME_TYPES = {"image/png", "image/jpeg", "image/jpg", "image/webp"}

# ===== Analyze ================================================================
@app.post("/api/analyze", response_model=PosterAnalysis)
def analyze(file: UploadFile = File(...)):
    if file.content_type and file.content_type.lower() not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {file.content_type}. Allowed types: PNG, JPEG, WebP."
        )

    contents = file.file.read()
    if not contents:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail=f"File exceeds maximum allowed size of 25MB (Received {len(contents)/(1024*1024):.2f}MB)."
        )

    try:
        result = poster_analyzer.analyze_image_bytes(contents, file.filename or "poster.png")
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))

    # Enforce reasonable dimension boundaries (100x100 min to 8000x8000 max)
    if result.width < 100 or result.height < 100:
        raise HTTPException(status_code=400, detail="Image dimensions too small (minimum 100x100 px).")
    if result.width > 8000 or result.height > 8000:
        raise HTTPException(status_code=400, detail="Image dimensions exceed maximum allowed size (8000x8000 px).")

    return result

# ===== Generate ===============================================================
@app.post("/api/generate")
def generate(req: GenerationRequest):
    variations = layout_engine.generate_variations(
        poster_width=req.poster_width,
        poster_height=req.poster_height,
        brand=req.brand,
        palette=req.custom_colors or (list(req.custom_palette.values()) if req.custom_palette else None),
        target_ratio=req.target_footer_height_ratio,
        style_preference=req.style_preference,
        arrangement_preference=req.arrangement_preference,
    )
    for v in variations:
        LayoutValidator.validate_footer(v)
    return [v.model_dump() for v in variations]

# ===== Auto-fix ===============================================================
@app.post("/api/auto-fix", response_model=AutoFixResponse)
def auto_fix(req: AutoFixRequest):
    fixed, changes, val_report = AutoAdjust.fix_all(req.footer, req.poster_width, req.poster_height)
    return AutoFixResponse(footer=fixed, changes=changes, validation_report=val_report)

# ===== Rearrange ==============================================================
@app.post("/api/rearrange", response_model=FooterDesign)
def rearrange(req: RearrangeRequest):
    font_scale = TypographyEngine.calculate_base_scale(req.poster_width, req.poster_height)
    font_sizes = TypographyEngine.get_font_sizes(font_scale)
    colors = {
        "text_primary": "#ffffff",
        "text_secondary": "#cbd5e1",
        "acc_col": "#38bdf8",
        "sec_col": "#1e293b",
        "bg_col": req.footer.background.color or "#0f172a"
    }
    new_elements = ArrangementEngine.apply_arrangement(
        arrangement_name=req.arrangement,
        fw=req.footer.width,
        fh=req.footer.height,
        pad_x=req.footer.padding.get("left", 24.0),
        pad_y=req.footer.padding.get("top", 16.0),
        top_offset=getattr(req.footer.background, "divider_thickness", 0.0) or 0.0,
        brand=req.brand,
        font_sizes=font_sizes,
        font_scale=font_scale,
        colors=colors,
        default_font=req.brand.font_family or "Inter",
        default_frame="circle",
        shape_key=req.footer.background.shape or "classic_rectangle",
    )
    req.footer.elements = new_elements
    req.footer.content_arrangement = req.arrangement
    LayoutValidator.validate_footer(req.footer)
    req.footer.svg_markup = SVGRenderer.render_svg(req.footer)
    return req.footer

# ===== Position & Layout Options ==============================================
@app.post("/api/position-options", response_model=List[FooterDesign])
def get_position_options(req: PositionOptionsRequest):
    font_scale = TypographyEngine.calculate_base_scale(req.poster_width, req.poster_height)
    font_sizes = TypographyEngine.get_font_sizes(font_scale)
    colors = {
        "text_primary": "#ffffff",
        "text_secondary": "#cbd5e1",
        "acc_col": "#38bdf8",
        "sec_col": "#1e293b",
        "bg_col": req.footer.background.color or "#0f172a"
    }

    # Rank arrangements based on brand content
    ranked_arrs = AdaptiveLayoutEngine.rank_arrangements_for_brand(
        req.brand, int(req.poster_width), int(req.poster_height)
    )

    options: List[FooterDesign] = []
    for arr in ranked_arrs:
        bg_clone = req.footer.background.model_copy(deep=True)
        top_offset = getattr(bg_clone, "divider_thickness", 0.0) or 0.0

        elements = ArrangementEngine.apply_arrangement(
            arrangement_name=arr,
            fw=req.footer.width,
            fh=req.footer.height,
            pad_x=req.footer.padding.get("left", 24.0),
            pad_y=req.footer.padding.get("top", 16.0),
            top_offset=top_offset,
            brand=req.brand,
            font_sizes=font_sizes,
            font_scale=font_scale,
            colors=colors,
            default_font=req.brand.font_family or "Inter",
            default_frame="circle",
            shape_key=bg_clone.shape or "classic_rectangle",
        )

        col_count = 3
        if arr in ["centred", "vertical_stacked", "compact"]:
            col_count = 1
        elif arr in ["two_column", "contact_card", "split_panel", "vertical_sidebar", "qr_focused", "asymmetric"]:
            col_count = 2
        elif arr in ["four_column"]:
            col_count = 4

        opt = FooterDesign(
            id=f"{req.footer.id}_{arr}",
            name=f"{req.footer.name} ({arr.replace('_', ' ').title()})",
            style_category=req.footer.style_category,
            content_arrangement=arr,
            width=req.footer.width,
            height=req.footer.height,
            x=req.footer.x,
            y=req.footer.y,
            columns=col_count,
            padding=req.footer.padding.copy(),
            background=bg_clone,
            elements=elements,
        )

        LayoutValidator.validate_footer(opt)
        opt.svg_markup = SVGRenderer.render_svg(opt)
        options.append(opt)

    return options

# ===== Logo Color Extraction & Theming ========================================
class ExtractLogoColorsRequest(BaseModel):
    logo_url: str

class ApplyLogoColorsRequest(BaseModel):
    footer: FooterDesign
    scheme: ColorScheme

class GenerateLogoColorVariationsRequest(BaseModel):
    footer: FooterDesign
    logo_url: Optional[str] = None
    palette: Optional[LogoPalette] = None

@app.post("/api/extract-logo-colors", response_model=LogoPalette)
def extract_logo_colors(req: ExtractLogoColorsRequest):
    if not req.logo_url:
        raise HTTPException(status_code=400, detail="Logo URL or base64 data required")
    return logo_color_extractor.extract_palette(req.logo_url)

@app.post("/api/extract-logo-colors-upload", response_model=LogoPalette)
def extract_logo_colors_upload(file: UploadFile = File(...)):
    contents = file.file.read()
    if not contents:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")
    return logo_color_extractor.extract_palette_from_bytes(contents)

@app.post("/api/apply-logo-colors", response_model=FooterDesign)
def apply_logo_colors(req: ApplyLogoColorsRequest):
    return color_theme_engine.apply_scheme_to_footer(req.footer, req.scheme)

@app.post("/api/generate-logo-color-variations", response_model=List[FooterDesign])
def generate_logo_color_variations(req: GenerateLogoColorVariationsRequest):
    palette = req.palette
    if not palette and req.logo_url:
        palette = logo_color_extractor.extract_palette(req.logo_url)
    if not palette:
        raise HTTPException(status_code=400, detail="Either palette or logo_url must be provided.")
    return color_theme_engine.generate_palette_variations(req.footer, palette)


# ===== Validate ===============================================================
@app.post("/api/validate")
def validate(req: ValidateRequest):
    result = LayoutValidator.validate_footer(req.footer)
    return result

# ===== Export =================================================================
CONTENT_TYPES = {
    "png": "image/png",
    "jpg": "image/jpeg",
    "jpeg": "image/jpeg",
    "pdf": "application/pdf",
    "svg": "image/svg+xml",
}

@app.post("/api/export")
def export(req: ExportRequest):
    fmt = req.format.lower()
    content_type = CONTENT_TYPES.get(fmt, "application/octet-stream")

    if fmt == "svg":
        svg_str = ExportService.export_svg(
            poster_data_url=req.poster_data_url,
            footer=req.footer,
            poster_w=req.poster_width,
            poster_h=req.poster_height,
        )
        return StreamingResponse(
            io.BytesIO(svg_str.encode("utf-8")),
            media_type=content_type,
            headers={"Content-Disposition": f"attachment; filename=poster.{fmt}"},
        )

    buf = FooterRenderer.render_to_bytes(
        poster_data_url=req.poster_data_url,
        footer=req.footer,
        export_format=fmt,
        poster_w=req.poster_width,
        poster_h=req.poster_height,
    )
    return StreamingResponse(
        buf,
        media_type=content_type,
        headers={"Content-Disposition": f"attachment; filename=poster.{fmt}"},
    )

# ===== Projects ===============================================================
@app.get("/api/projects")
def list_projects():
    return storage.list_projects()

@app.post("/api/projects")
def save_project(project: Dict[str, Any] = Body(...)):
    return storage.save_project(project)

@app.get("/api/projects/{project_id}")
def get_project(project_id: str):
    p = storage.get_project(project_id)
    if p is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return p

@app.delete("/api/projects/{project_id}")
def delete_project(project_id: str):
    ok = storage.delete_project(project_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Project not found")
    return {"deleted": True}

@app.post("/api/projects/{project_id}/duplicate")
def duplicate_project(project_id: str):
    dup = storage.duplicate_project(project_id)
    if dup is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return dup

# ===== Brands =================================================================
@app.get("/api/brands")
def list_brands():
    return storage.list_brands()

@app.post("/api/brands")
def save_brand(brand: Dict[str, Any] = Body(...)):
    return storage.save_brand(brand)

@app.delete("/api/brands/{brand_id}")
def delete_brand(brand_id: str):
    ok = storage.delete_brand(brand_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Brand not found")
    return {"deleted": True}
