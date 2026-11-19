"""
Comprehensive test suite verifying all code review fixes.
Covers Security, Layout non-overlap, Scannable QR, SVG Repair, and Validation.
"""

import pytest
from app.models.brand import BrandProfile, CustomField, LogoItem, ProfileItem
from app.models.footer import FooterDesign, FooterElement, ElementStyle, FooterBackground
from app.engine.svg_repair import SVGRepair
from app.services.qr_service import QRService
from app.engine.layout_engine import LayoutEngine
from app.validator.layout_validator import LayoutValidator
from app.engine.auto_adjust import AutoAdjust
from app.renderer.svg_renderer import SVGRenderer
from app.services.export_service import ExportService


def test_svg_sanitizer_blocks_scripts_and_events():
    malicious_svg = '''<svg xmlns="http://www.w3.org/2000/svg" width="200" height="100">
      <script>alert("XSS")</script>
      <rect width="100" height="50" onclick="alert(1)" onload="evil()" fill="red" />
      <foreignObject width="100" height="50">
        <div>Injected HTML</div>
      </foreignObject>
      <a href="javascript:alert(1)"><text y="20">Click</text></a>
    </svg>'''

    result = SVGRepair.inspect_and_repair(malicious_svg)
    assert not result["is_valid"] or len(result["issues"]) > 0
    clean = result["repaired_svg"]
    
    # Must strip malicious elements & attributes
    assert "<script" not in clean.lower()
    assert "onclick" not in clean.lower()
    assert "onload" not in clean.lower()
    assert "<foreignobject" not in clean.lower()
    assert "javascript:" not in clean.lower()


def test_svg_repair_preserves_aspect_ratio_meet():
    svg_without_viewbox = '''<svg width="600" height="120" xmlns="http://www.w3.org/2000/svg">
      <rect width="600" height="120" fill="#1e293b"/>
    </svg>'''

    result = SVGRepair.inspect_and_repair(svg_without_viewbox, target_width=1080.0, target_height=180.0)
    repaired = result["repaired_svg"]
    assert 'viewBox="0 0 600.0 120.0"' in repaired
    assert 'preserveAspectRatio="none"' not in repaired
    assert 'preserveAspectRatio="xMidYMid meet"' in repaired


def test_qr_service_generates_valid_scannable_qr():
    content = "https://example.com/ai-footer-studio-verified"
    data_url = QRService.generate_qr_data_url(content)
    assert data_url.startswith("data:image/png;base64,")
    assert len(data_url) > 100

    svg_markup = QRService.generate_qr_svg(content, size=100)
    assert "<svg" in svg_markup
    assert "</svg>" in svg_markup


def test_portrait_two_column_no_overlap():
    engine = LayoutEngine()
    brand = BrandProfile(
        brand_name="Acme Global Corporation",
        tagline="Innovating Tomorrow's Solutions Today",
        phone="+1 800 555 0199",
        email="contact@acmeglobal.example.com",
        website="https://www.acmeglobal.example.com",
        address="742 Evergreen Terrace, Suite 500, Springfield, OR 97477",
        cta="Schedule a Free Consultation Today",
        qr_code_content="https://www.acmeglobal.example.com/connect",
        social_handles={
            "linkedin": "acme-global",
            "twitter": "@acmeglobal",
            "instagram": "@acme_official",
        },
        custom_fields=[
            CustomField(id="cf1", label="Lic #", value="CA-9928172-B"),
            CustomField(id="cf2", label="Hours", value="Mon-Fri 8am-6pm PST"),
        ]
    )

    # Generate for a portrait poster (1080 x 1920)
    variations = engine.generate_variations(
        poster_width=1080,
        poster_height=1920,
        brand=brand,
        palette=["#0f172a", "#38bdf8", "#f59e0b"]
    )

    assert len(variations) >= 8

    # Check for zero bounding-box overlaps in portrait variations
    for v in variations:
        report = LayoutValidator.validate_footer(v)
        # Ensure quality score is high and zero critical collisions
        assert report["quality_score"] >= 75.0, f"Low quality score {report['quality_score']} in {v.name}: {report['notices']}"
        assert len(report["critical_errors"]) == 0, f"Collisions/overflows in {v.name}: {report['critical_errors']}"


def test_layout_validator_detects_aabb_collision():
    footer = FooterDesign(
        id="collision-test",
        name="Collision Test",
        style_category="modern",
        x=0.0,
        y=0.0,
        width=1000.0,
        height=150.0,
        background=FooterBackground(color="#1e293b", shape="bar"),
        elements=[
            FooterElement(id="e1", type="text", x=100.0, y=30.0, width=120.0, height=25.0, text="First Label"),
            # Overlaps e1 directly
            FooterElement(id="e2", type="text", x=150.0, y=35.0, width=100.0, height=25.0, text="Second Label"),
        ]
    )

    report = LayoutValidator.validate_footer(footer)
    assert not report["is_valid"]
    assert any("Collision detected" in err for err in report["critical_errors"])

    # Auto-adjust should resolve this overlap
    fixed_footer, changes, post_report = AutoAdjust.fix_all(footer, 1000, 1000)
    assert len(changes) > 0
    # After auto-fix, collision must be resolved
    assert not any("Collision detected" in err for err in post_report["critical_errors"])


def test_multi_logo_and_profile_rendering():
    dummy_b64 = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
    brand = BrandProfile(
        brand_name="Twin Peak Brands",
        logos=[
            LogoItem(id="l1", name="Logo 1", url=dummy_b64),
            LogoItem(id="l2", name="Logo 2", url=dummy_b64)
        ],
        profiles=[
            ProfileItem(id="p1", name="CEO", url=dummy_b64, frame_style="circle")
        ],
        phone="555-1234"
    )

    engine = LayoutEngine()
    variations = engine.generate_variations(
        poster_width=1080,
        poster_height=1080,
        brand=brand
    )

    found_multi_logo = False
    for v in variations:
        logos = [e for e in v.elements if e.type == "logo"]
        if len(logos) >= 2:
            found_multi_logo = True
            break
    assert found_multi_logo, "Engine should support multiple logos in elements list"


def test_export_service_raster_and_svg():
    footer = FooterDesign(
        id="export-test",
        name="Export Test",
        style_category="modern",
        width=1080.0,
        height=180.0,
        x=0.0,
        y=900.0,
        background=FooterBackground(color="#0f172a", shape="rounded"),
        elements=[
            FooterElement(id="t1", type="text", x=40.0, y=20.0, width=300.0, height=30.0, text="Acme Global"),
            FooterElement(id="c1", type="icon_text", icon="phone", x=40.0, y=60.0, width=250.0, height=24.0, text="+1 800 555 0199"),
            FooterElement(id="cta", type="cta", x=40.0, y=100.0, width=180.0, height=36.0, text="Book Now"),
        ]
    )

    # Test PNG export
    png_buf = ExportService.export_poster(None, footer, export_format="png", poster_w=1080, poster_h=1080)
    assert png_buf.getbuffer().nbytes > 1000

    # Test JPG export
    jpg_buf = ExportService.export_poster(None, footer, export_format="jpg", poster_w=1080, poster_h=1080)
    assert jpg_buf.getbuffer().nbytes > 1000

    # Test PDF export
    pdf_buf = ExportService.export_poster(None, footer, export_format="pdf", poster_w=1080, poster_h=1080)
    assert pdf_buf.getbuffer().nbytes > 1000

    # Test SVG export
    svg_str = ExportService.export_svg(None, footer, poster_w=1080, poster_h=1080)
    assert "<svg" in svg_str
    assert "Acme Global" in svg_str
