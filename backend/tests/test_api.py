"""
Comprehensive backend and API endpoint tests for AI Footer Designer.
"""

import io
import json
import pytest
from PIL import Image
from fastapi import UploadFile

from app.models.brand import BrandProfile, LogoItem, ProfileItem
from app.models.footer import FooterDesign, GenerationRequest
from app.analyzer.poster_analyzer import PosterAnalyzer
from app.engine.layout_engine import LayoutEngine
from app.engine.auto_adjust import AutoAdjust
from app.validator.layout_validator import LayoutValidator
from app.services.storage_service import StorageService
from app.services.export_service import ExportService
from app.renderer.footer_renderer import FooterRenderer
from app.main import (
    health,
    analyze,
    generate,
    auto_fix,
    validate,
    export,
    list_projects,
    save_project,
    get_project,
    delete_project,
    duplicate_project,
    list_brands,
    save_brand,
    delete_brand,
    AutoFixRequest,
    ValidateRequest,
    ExportRequest,
)

def _make_gradient_png(width: int = 1080, height: int = 1080) -> bytes:
    img = Image.new("RGB", (width, height))
    for y in range(height):
        ratio = y / max(height - 1, 1)
        r = int(255 * (1 - ratio))
        b = int(255 * ratio)
        for x in range(width):
            img.putpixel((x, y), (r, 0, b))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return buf.getvalue()

MINIMAL_BRAND = BrandProfile(
    brand_name="Apex Media",
    phone="555-0199",
)

FULL_BRAND = BrandProfile(
    id="full-brand-1",
    brand_name="Acme Studios",
    tagline="Design Excellence",
    phone="+1-555-0100",
    whatsapp="+1-555-0101",
    email="hello@acme.studio",
    website="https://acme.studio",
    address="123 Creative Lane, Art City, AC 90210",
    cta="Book Now",
    social_handles={"instagram": "@acme", "facebook": "fb/acme"},
    qr_code_content="https://acme.studio/qr",
    primary_color="#1e293b",
    secondary_color="#3b82f6",
    accent_color="#f59e0b",
    font_family="Inter",
)

SAMPLE_FOOTER_DICT = {
    "id": "test-footer",
    "name": "Test Footer",
    "style_category": "modern",
    "width": 1080.0,
    "height": 160.0,
    "x": 0.0,
    "y": 920.0,
    "columns": 3,
    "padding": {"top": 12.0, "bottom": 12.0, "left": 20.0, "right": 20.0},
    "background": {
        "type": "solid",
        "color": "#0f172a",
        "opacity": 1.0,
        "shape": "rectangle",
        "shadow": False,
        "shadow_color": "rgba(0,0,0,0.25)",
        "shadow_blur": 12.0,
        "border_width": 0.0,
        "border_radius": 0.0,
    },
    "elements": [
        {
            "id": "el_1",
            "type": "text",
            "text": "Apex Media",
            "x": 20.0,
            "y": 14.0,
            "width": 300.0,
            "height": 28.0,
            "rotation": 0.0,
            "z_index": 1,
            "locked": False,
            "visible": True,
            "style": {
                "font_family": "Inter",
                "font_size": 22.0,
                "font_weight": "800",
                "color": "#ffffff",
            },
        },
        {
            "id": "el_2",
            "type": "icon_text",
            "icon": "phone",
            "text": "555-0199",
            "x": 380.0,
            "y": 14.0,
            "width": 300.0,
            "height": 24.0,
            "rotation": 0.0,
            "z_index": 1,
            "locked": False,
            "visible": True,
            "style": {"font_size": 13.0, "color": "#ffffff"},
        },
    ],
    "quality_score": 100.0,
    "validation_notices": [],
}

def test_health_endpoint():
    res = health()
    assert res["status"] == "ok"
    assert res["service"] == "ai-footer-designer"

def test_analyze_endpoint():
    png_bytes = _make_gradient_png(1080, 1080)
    upload_file = UploadFile(
        file=io.BytesIO(png_bytes),
        filename="test_poster.png",
        headers={"content-type": "image/png"}
    )
    analysis = analyze(upload_file)
    assert analysis.width == 1080
    assert analysis.height == 1080
    assert len(analysis.dominant_colors) > 0
    assert analysis.safe_zone is not None
    assert len(analysis.suggested_footer_palette) > 0

def test_generate_variations_endpoint():
    req = GenerationRequest(
        poster_width=1080,
        poster_height=1920,
        brand=FULL_BRAND,
        style_preference="all",
        target_footer_height_ratio=0.15,
        custom_colors=["#1e293b", "#3b82f6"]
    )
    variations = generate(req)
    assert isinstance(variations, list)
    assert len(variations) >= 8  # Adaptive engine generates full template catalog (18)
    for v in variations:
        assert "id" in v
        assert "name" in v
        assert len(v["elements"]) > 0
        assert v["svg_markup"] is not None

def test_auto_fix_endpoint():
    footer_obj = FooterDesign(**SAMPLE_FOOTER_DICT)
    req = AutoFixRequest(footer=footer_obj, poster_width=1080, poster_height=1080)
    res = auto_fix(req)
    assert res.footer is not None
    assert len(res.changes) > 0

def test_validate_endpoint():
    footer_obj = FooterDesign(**SAMPLE_FOOTER_DICT)
    req = ValidateRequest(footer=footer_obj)
    res = validate(req)
    assert "is_valid" in res
    assert "quality_score" in res
    assert res["quality_score"] >= 80.0

def test_export_png_endpoint():
    footer_obj = FooterDesign(**SAMPLE_FOOTER_DICT)
    req = ExportRequest(footer=footer_obj, format="png", poster_width=1080, poster_height=1080)
    res = export(req)
    assert res.media_type == "image/png"

def test_export_svg_endpoint():
    footer_obj = FooterDesign(**SAMPLE_FOOTER_DICT)
    req = ExportRequest(footer=footer_obj, format="svg", poster_width=1080, poster_height=1080)
    res = export(req)
    assert res.media_type == "image/svg+xml"

def test_projects_crud():
    p_data = {"id": "test-p1", "name": "Test Project 1", "poster_width": 1080, "poster_height": 1080}
    saved = save_project(p_data)
    assert saved["id"] == "test-p1"

    fetched = get_project("test-p1")
    assert fetched["name"] == "Test Project 1"

    all_p = list_projects()
    assert any(p["id"] == "test-p1" for p in all_p)

    dup = duplicate_project("test-p1")
    assert "copy" in dup["id"]

    del_res = delete_project("test-p1")
    assert del_res["deleted"] is True
    delete_project(dup["id"])

def test_brands_crud():
    b_data = {"id": "test-b1", "brand_name": "Brand Apex", "phone": "555-9988"}
    saved = save_brand(b_data)
    assert saved["id"] == "test-b1"

    all_b = list_brands()
    assert any(b["id"] == "test-b1" for b in all_b)

    del_res = delete_brand("test-b1")
    assert del_res["deleted"] is True
