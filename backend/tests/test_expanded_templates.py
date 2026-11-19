import os
import sys
from pathlib import Path
import pytest

# Ensure backend root is in sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from app.design_library.templates.adaptive_templates import (
    ADAPTIVE_TEMPLATES_REGISTRY,
    get_template_by_id,
    list_templates_by_category,
)
from app.design_library.shapes.adaptive_shapes import AdaptiveShapes
from app.engine.adaptive_layout_engine import AdaptiveLayoutEngine
from app.validator.layout_validator import LayoutValidator
from app.models.brand import BrandProfile, LogoItem, ProfileItem, CustomField
from app.services.export_service import ExportService


@pytest.fixture
def sample_brand():
    return BrandProfile(
        company_name="Apex Global Technologies Inc.",
        tagline="Empowering the Next Generation of Autonomous Systems",
        website="https://apexglobal.tech/enterprise/solutions",
        email="contact-corporate@apexglobal.tech",
        phone="+1 (800) 555-0199",
        address="Suite 400, 100 Innovation Boulevard, Silicon Valley, CA",
        primary_color="#4f46e5",
        secondary_color="#06b6d4",
        accent_color="#f59e0b",
        qr_code_content="https://apexglobal.tech/connect",
        social_media={"twitter": "@apextech", "linkedin": "apex-global"},
        logos=[
            LogoItem(id="logo1", name="Apex", url="https://example.com/logo1.png", width=200, height=50, aspect_ratio=4.0),
            LogoItem(id="logo2", name="ISO Certified", url="https://example.com/iso.png", width=100, height=100, aspect_ratio=1.0)
        ],
        profiles=[
            ProfileItem(id="prof1", name="Dr. Elena Vance", title="Chief Architect", url="https://example.com/elena.jpg")
        ],
        custom_fields=[
            CustomField(id="cf1", label="Reg ID", value="AG-2026-X99")
        ]
    )


def test_registry_count_and_completeness():
    """Verify all 48 templates are registered with unique IDs and valid mathematical SVG shapes."""
    assert len(ADAPTIVE_TEMPLATES_REGISTRY) == 48, f"Expected 48 templates, found {len(ADAPTIVE_TEMPLATES_REGISTRY)}"
    
    ids = [t.id for t in ADAPTIVE_TEMPLATES_REGISTRY]
    assert len(ids) == len(set(ids)), "Duplicate template IDs found"
    
    valid_categories = {"wave", "curved", "modern", "geometric", "minimal", "corporate", "creative", "editorial", "festival", "premium", "business"}
    for tpl in ADAPTIVE_TEMPLATES_REGISTRY:
        svg_shape = AdaptiveShapes.generate_shape_svg(tpl.shape_key, 1000.0, 150.0, "#4f46e5", "#06b6d4")
        assert len(svg_shape) > 0, f"Shape generation failed for '{tpl.shape_key}'"
        assert tpl.category in valid_categories, f"Invalid category '{tpl.category}' for template '{tpl.id}'"


def test_category_distributions():
    """Verify expected counts across categories."""
    wave_templates = list_templates_by_category("wave")
    curved_templates = list_templates_by_category("curved")
    modern_templates = list_templates_by_category("modern")
    geometric_templates = list_templates_by_category("geometric")
    minimal_templates = list_templates_by_category("minimal")
    corporate_templates = list_templates_by_category("corporate")

    assert len(wave_templates) >= 10, f"Expected at least 10 wave templates, found {len(wave_templates)}"
    assert len(curved_templates) >= 7, f"Expected at least 7 curved templates, found {len(curved_templates)}"
    assert len(modern_templates) >= 9, f"Expected at least 9 modern templates, found {len(modern_templates)}"
    assert len(geometric_templates) >= 3, f"Expected at least 3 geometric templates, found {len(geometric_templates)}"
    assert len(minimal_templates) >= 2, f"Expected at least 2 minimal templates, found {len(minimal_templates)}"
    assert len(corporate_templates) >= 1, f"Expected at least 1 corporate template, found {len(corporate_templates)}"


def test_all_48_templates_generate_in_portrait(sample_brand):
    """Test all 48 templates on 1080x1920 (9:16 portrait) with zero critical collisions."""
    engine = AdaptiveLayoutEngine()
    variations = engine.generate_adaptive_variations(
        poster_width=1080,
        poster_height=1920,
        brand=sample_brand,
        category_filter="all",
    )
    assert len(variations) == 48
    for v in variations:
        assert v.x >= 0.0
        assert v.width > 0.0
        assert v.x + v.width <= 1080.5
        assert v.height > 100
        assert v.y + v.height <= 1920.5
        assert v.svg_markup and "<svg" in v.svg_markup and "</svg>" in v.svg_markup
        
        report = LayoutValidator.validate_footer(v)
        collisions = [e for e in report["critical_errors"] if "Collision" in e]
        assert len(collisions) == 0, f"Template {v.id} has collisions in portrait: {collisions}"


def test_all_48_templates_generate_in_square(sample_brand):
    """Test all 48 templates on 1080x1080 (1:1 square) with zero critical collisions."""
    engine = AdaptiveLayoutEngine()
    variations = engine.generate_adaptive_variations(
        poster_width=1080,
        poster_height=1080,
        brand=sample_brand,
        category_filter="all",
    )
    assert len(variations) == 48
    for v in variations:
        assert v.x >= 0.0
        assert v.width > 0.0
        assert v.x + v.width <= 1080.5
        assert v.height > 80
        assert v.y + v.height <= 1080.5
        assert v.svg_markup and "<svg" in v.svg_markup and "</svg>" in v.svg_markup

        report = LayoutValidator.validate_footer(v)
        collisions = [e for e in report["critical_errors"] if "Collision" in e]
        assert len(collisions) == 0, f"Template {v.id} has collisions in square: {collisions}"


def test_all_48_templates_generate_in_landscape(sample_brand):
    """Test all 48 templates on 1920x1080 (16:9 landscape) with zero critical collisions."""
    engine = AdaptiveLayoutEngine()
    variations = engine.generate_adaptive_variations(
        poster_width=1920,
        poster_height=1080,
        brand=sample_brand,
        category_filter="all",
    )
    assert len(variations) == 48
    for v in variations:
        assert v.x >= 0.0
        assert v.width > 0.0
        assert v.x + v.width <= 1920.5
        assert v.height > 80
        assert v.y + v.height <= 1080.5
        assert v.svg_markup and "<svg" in v.svg_markup and "</svg>" in v.svg_markup

        report = LayoutValidator.validate_footer(v)
        collisions = [e for e in report["critical_errors"] if "Collision" in e]
        assert len(collisions) == 0, f"Template {v.id} has collisions in landscape: {collisions}"


def test_category_filtering_action(sample_brand):
    """Test filtering by category works properly."""
    engine = AdaptiveLayoutEngine()
    wave_vars = engine.generate_adaptive_variations(1080, 1920, sample_brand, category_filter="wave")
    assert len(wave_vars) == 10
    assert all(v.style_category == "wave" for v in wave_vars)

    curved_vars = engine.generate_adaptive_variations(1080, 1920, sample_brand, category_filter="curved")
    assert len(curved_vars) == 7
    assert all(v.style_category == "curved" for v in curved_vars)


def test_export_pipeline_on_new_shapes(sample_brand):
    """Test SVG, PNG, JPG, PDF exports on a newly added wave shape and geometric shape."""
    engine = AdaptiveLayoutEngine()
    variations = engine.generate_adaptive_variations(1080, 1080, sample_brand, category_filter="wave")
    wave_footer = variations[0]

    # 1. SVG
    svg_data = ExportService.export_svg(None, wave_footer, 1080, 1080)
    assert isinstance(svg_data, str)
    assert "<svg" in svg_data

    # 2. PNG
    png_stream = ExportService.export_poster(None, wave_footer, "png", 1080, 1080)
    assert len(png_stream.getvalue()) > 1000

    # 3. JPG
    jpg_stream = ExportService.export_poster(None, wave_footer, "jpg", 1080, 1080)
    assert len(jpg_stream.getvalue()) > 1000

    # 4. PDF
    pdf_stream = ExportService.export_poster(None, wave_footer, "pdf", 1080, 1080)
    assert len(pdf_stream.getvalue()) > 1000
