import pytest
from app.models.brand import BrandProfile, LogoItem, ProfileItem
from app.engine.adaptive_layout_engine import AdaptiveLayoutEngine
from app.design_library.templates.adaptive_templates import ADAPTIVE_TEMPLATES_REGISTRY
from app.engine.svg_repair import SVGRepair
from app.main import list_templates, repair_svg, RepairSvgRequest

engine = AdaptiveLayoutEngine()

SHORT_BRAND = BrandProfile(
    brand_name="Apex Media",
    phone="555-0100",
)

LONG_BRAND = BrandProfile(
    id="long-brand-1",
    brand_name="Acme International Audio Studios",
    tagline="World-Class Acoustic Engineering & Mastering Labs",
    phone="+1 (555) 234-5678",
    whatsapp="+1 (555) 234-5679",
    email="inquiries@acme-audio-studios.com",
    website="https://www.acme-audio-studios.com",
    address="800 West Hollywood Blvd, Suite 1200, Los Angeles, CA 90028",
    cta="Book Your Masterclass Today",
    social_handles={"instagram": "@acmeaudio", "youtube": "acmestudios"},
    qr_code_content="https://www.acme-audio-studios.com/vip",
    primary_color="#0f172a",
    secondary_color="#3b82f6",
    accent_color="#f59e0b",
    font_family="Inter",
    logos=[
        LogoItem(id="l1", name="Logo", url="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk+A8AAQUBAScY42YAAAAASUVORK5CYII=", aspect_ratio=3.2)
    ],
    profiles=[
        ProfileItem(id="p1", name="Engineer", url="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk+A8AAQUBAScY42YAAAAASUVORK5CYII=", frame_style="circle")
    ],
)

# ------------------------------------------------------------------------------
# Test 1: Portrait (9:16) with Short and Long Brand details
# ------------------------------------------------------------------------------
def test_portrait_short_brand():
    variations = engine.generate_adaptive_variations(
        poster_width=1080,
        poster_height=1920,
        brand=SHORT_BRAND,
    )
    assert len(variations) >= 15
    for v in variations:
        assert v.width <= 1080.0
        assert v.height >= 120.0
        assert v.quality_score >= 80.0
        assert "<svg" in v.svg_markup
        assert "</svg>" in v.svg_markup

def test_portrait_long_brand():
    variations = engine.generate_adaptive_variations(
        poster_width=1080,
        poster_height=1920,
        brand=LONG_BRAND,
    )
    assert len(variations) >= 15
    for v in variations:
        assert v.width <= 1080.0
        # Check that no element exceeds horizontal boundaries
        for el in v.elements:
            assert el.x + el.width <= v.width + 1.0, f"Element {el.id} overflowed width"

# ------------------------------------------------------------------------------
# Test 2: Square (1:1) with Short and Long Brand details
# ------------------------------------------------------------------------------
def test_square_short_brand():
    variations = engine.generate_adaptive_variations(
        poster_width=1080,
        poster_height=1080,
        brand=SHORT_BRAND,
    )
    assert len(variations) >= 15
    for v in variations:
        assert v.width <= 1080.0
        assert v.quality_score >= 80.0

def test_square_long_brand():
    variations = engine.generate_adaptive_variations(
        poster_width=1080,
        poster_height=1080,
        brand=LONG_BRAND,
    )
    assert len(variations) >= 15
    for v in variations:
        assert v.width <= 1080.0
        assert len(v.elements) >= 4
        for el in v.elements:
            assert el.x >= 0.0
            assert el.x + el.width <= v.width + 2.0

# ------------------------------------------------------------------------------
# Test 3: Landscape (16:9) with Short and Long Brand details
# ------------------------------------------------------------------------------
def test_landscape_short_brand():
    variations = engine.generate_adaptive_variations(
        poster_width=1920,
        poster_height=1080,
        brand=SHORT_BRAND,
    )
    assert len(variations) >= 15
    for v in variations:
        assert v.width <= 1920.0
        assert v.quality_score >= 80.0

def test_landscape_long_brand():
    variations = engine.generate_adaptive_variations(
        poster_width=1920,
        poster_height=1080,
        brand=LONG_BRAND,
    )
    assert len(variations) >= 15
    for v in variations:
        assert v.width <= 1920.0
        # In landscape mode, logo preservation check
        logos = [el for el in v.elements if el.type == "logo"]
        if logos:
            logo = logos[0]
            assert logo.width > logo.height  # 3.2 aspect ratio preserved

# ------------------------------------------------------------------------------
# Test 4: Template Registry API Endpoint
# ------------------------------------------------------------------------------
def test_template_registry_endpoint():
    templates = list_templates()
    assert len(templates) >= 18
    shape_keys = {t["shape_key"] for t in templates}
    assert "classic_rectangle" in shape_keys
    assert "fluid_wave_single" in shape_keys
    assert "floating_capsule" in shape_keys
    assert "executive_ribbon" in shape_keys

# ------------------------------------------------------------------------------
# Test 5: SVG Repair & Rejection
# ------------------------------------------------------------------------------
def test_svg_repair_success():
    raw_svg = '<svg width="500" height="100"><rect width="500" height="100" fill="red"/></svg>'
    res = repair_svg(RepairSvgRequest(svg_content=raw_svg, target_width=1080.0, target_height=160.0))
    assert res["is_valid"] is True
    assert res["was_repaired"] is True
    assert "viewBox" in res["repaired_svg"]
    assert "preserveAspectRatio" in res["repaired_svg"]

def test_svg_repair_rejection():
    broken_svg = "NOT AN SVG FILE <broken xml"
    res = repair_svg(RepairSvgRequest(svg_content=broken_svg, target_width=1080.0, target_height=160.0))
    assert res["is_valid"] is False
    assert len(res["notices"]) > 0
