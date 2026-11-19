import os
import sys
from pathlib import Path
import pytest

# Ensure backend root is in sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from app.models.brand import BrandProfile, LogoItem, ProfileItem, CustomField
from app.engine.arrangement_engine import ArrangementEngine
from app.engine.adaptive_layout_engine import AdaptiveLayoutEngine
from app.validator.layout_validator import LayoutValidator
from app.engine.typography_engine import TypographyEngine
from app.engine.auto_adjust import AutoAdjust
from app.models.footer import FooterDesign, FooterBackground, FooterElement, ElementStyle
from app.main import rearrange, RearrangeRequest, get_position_options, PositionOptionsRequest


@pytest.fixture
def rich_brand():
    return BrandProfile(
        brand_name="Aura Dynamics Technologies",
        tagline="Pioneering Autonomous Quantum Frameworks",
        website="https://auradynamics.com/cloud",
        email="contact@auradynamics.com",
        phone="+1 (800) 555-0199",
        whatsapp="+1 (800) 555-0198",
        address="100 Innovation Parkway, Suite 500, Seattle, WA",
        cta="Schedule Demo",
        qr_code_content="https://auradynamics.com/connect",
        social_handles={"twitter": "@auradynamics", "linkedin": "aura-dynamics"},
        logos=[
            LogoItem(id="l1", name="Aura", url="https://example.com/logo1.png", width=160, height=40, aspect_ratio=4.0),
            LogoItem(id="l2", name="ISO", url="https://example.com/iso.png", width=80, height=80, aspect_ratio=1.0)
        ],
        profiles=[
            ProfileItem(id="p1", name="Dr. Alex Rivera", title="Chief Architect", url="https://example.com/alex.jpg", frame_style="circle")
        ],
        custom_fields=[
            CustomField(id="cf1", label="Series", value="Quantum-X")
        ]
    )


def test_all_20_arrangements_implemented():
    """Verify that all 20 required content arrangements are defined and supported."""
    required_20 = [
        "classic_horizontal", "vertical_stacked", "two_column", "three_column",
        "four_column", "centred", "left_aligned_stack", "right_aligned_stack",
        "logo_centre", "profile_focused", "profile_circle", "logo_top",
        "contact_card", "social_bottom", "qr_focused", "split_panel",
        "vertical_sidebar", "floating_elements", "asymmetric", "compact"
    ]
    assert len(ArrangementEngine.ARRANGEMENTS) == 20
    for arr in required_20:
        assert arr in ArrangementEngine.ARRANGEMENTS, f"Missing required arrangement: {arr}"


def test_each_arrangement_produces_valid_elements(rich_brand):
    """Verify each of the 20 arrangements generates non-overlapping elements inside bounds."""
    fw, fh = 1080.0, 220.0
    pad_x, pad_y = 35.0, 15.0
    top_offset = 12.0
    font_scale = 1.0
    font_sizes = TypographyEngine.get_font_sizes(font_scale)
    colors = {
        "text_primary": "#ffffff",
        "text_secondary": "#cbd5e1",
        "acc_col": "#f59e0b",
        "sec_col": "#1e293b",
        "bg_col": "#0f172a"
    }

    for arr in ArrangementEngine.ARRANGEMENTS:
        elements = ArrangementEngine.apply_arrangement(
            arrangement_name=arr,
            fw=fw,
            fh=fh,
            pad_x=pad_x,
            pad_y=pad_y,
            top_offset=top_offset,
            brand=rich_brand,
            font_sizes=font_sizes,
            font_scale=font_scale,
            colors=colors,
            default_font="Inter",
            default_frame="circle",
            shape_key="classic_rectangle"
        )
        assert len(elements) >= 3, f"Arrangement {arr} produced too few elements ({len(elements)})"
        for el in elements:
            assert el.x >= 0, f"Element {el.id} in {arr} has negative x ({el.x})"
            assert el.y >= 0, f"Element {el.id} in {arr} has negative y ({el.y})"
            assert el.x + el.width <= fw + 2.0, f"Element {el.id} in {arr} overflows right edge ({el.x + el.width} > {fw})"
            assert el.y + el.height <= fh + 2.0, f"Element {el.id} in {arr} overflows bottom edge ({el.y + el.height} > {fh})"


def test_at_least_10_distinct_arrangements_generated(rich_brand):
    """
    Acceptance Requirement: At least 10 visibly different content arrangements
    must be generated with the same uploaded poster and brand details.
    """
    engine = AdaptiveLayoutEngine()
    variations = engine.generate_adaptive_variations(
        poster_width=1080,
        poster_height=1920,
        brand=rich_brand,
        category_filter="all",
        arrangement_filter="all"
    )

    # Check arrangements in the first 20 generated variations
    first_20_arrangements = [v.content_arrangement for v in variations[:20]]
    unique_arrangements = set(first_20_arrangements)
    print(f"\nUnique arrangements in top 20 variations: {len(unique_arrangements)} ({unique_arrangements})")
    
    assert len(unique_arrangements) >= 10, f"Expected at least 10 distinct content arrangements, got {len(unique_arrangements)}"
    assert len(unique_arrangements) >= 15, f"Expected high arrangement diversity, got {len(unique_arrangements)}"


def test_intelligent_ranking_prioritizes_content(rich_brand):
    """Verify intelligent arrangement ranking adapts based on brand features."""
    # 1. Brand with Profile Photo -> profile_focused, profile_circle should be at top
    ranked_profile = AdaptiveLayoutEngine.rank_arrangements_for_brand(rich_brand, 1080, 1920)
    top_3 = ranked_profile[:3]
    assert "profile_focused" in top_3 or "profile_circle" in top_3, f"Profile arrangements should be prioritized: {top_3}"

    # 2. Brand without profile, but with multiple logos and heavy contacts
    brand_no_prof = BrandProfile(
        brand_name="Multi-Corp Global Holdings Inc.",
        logos=[LogoItem(id="1", name="A", url=""), LogoItem(id="2", name="B", url="")],
        phone="123", whatsapp="456", email="a@b.com", website="https://b.com", address="Main St",
        qr_code_content="https://qr.com"
    )
    ranked_logos = AdaptiveLayoutEngine.rank_arrangements_for_brand(brand_no_prof, 1080, 1080)
    top_5 = ranked_logos[:5]
    assert any(arr in top_5 for arr in ["logo_top", "four_column", "vertical_sidebar", "contact_card"])


def test_short_and_long_brand_names():
    """Verify zero overlap with both short (1 word) and extremely long (80 chars) brand names."""
    engine = AdaptiveLayoutEngine()

    short_brand = BrandProfile(brand_name="Go", phone="123", email="go@go.com")
    long_brand = BrandProfile(
        brand_name="International Consortium of Advanced Distributed Quantum Computing Laboratories & Co.",
        tagline="Revolutionizing Ultra-Scale Cryptographic Infrastructure Worldwide",
        phone="+1 (800) 555-0199",
        email="enterprise-compliance-officer@quantum-infrastructure-worldwide.corp",
        website="https://very-long-domain-name-for-enterprise-compliance.quantum-infrastructure.io",
        address="Floor 42, International Quantum Center, Zurich Innovation District, Switzerland"
    )

    for b in [short_brand, long_brand]:
        variations = engine.generate_adaptive_variations(1080, 1080, b)
        for v in variations:
            report = LayoutValidator.validate_footer(v)
            collisions = [e for e in report["critical_errors"] if "Collision" in e]
            assert len(collisions) == 0, f"Template {v.id} collided for {b.brand_name[:15]}: {collisions}"


def test_auto_adjust_fixes_font_sizes_padding_alignment_and_overflows():
    """Verify AutoAdjust.fix_all fixes font sizes, padding, alignment, overlaps, and overflows."""
    # Create a deliberately perturbed footer with bad padding, overlapping elements, oversized font, and poor contrast
    bad_footer = FooterDesign(
        id="test_bad",
        name="Bad Layout Test",
        style_category="modern",
        width=1080.0,
        height=180.0,
        x=0.0,
        y=900.0,
        padding={"left": 5.0, "right": 5.0, "top": 2.0, "bottom": 2.0},
        columns=2,
        background=FooterBackground(shape="classic_rectangle", color="#000000"),
        elements=[
            # Too small font
            FooterElement(
                id="el_small",
                type="text",
                text="Too Tiny Text",
                x=8.0,
                y=4.0,
                width=100.0,
                height=15.0,
                style=ElementStyle(font_size=6.0, color="#222222") # poor contrast on black
            ),
            # Overlapping elements
            FooterElement(
                id="el_overlap1",
                type="text",
                text="Collision Item 1",
                x=100.0,
                y=50.0,
                width=200.0,
                height=30.0,
                style=ElementStyle(font_size=16.0, color="#ffffff")
            ),
            FooterElement(
                id="el_overlap2",
                type="text",
                text="Collision Item 2",
                x=110.0,
                y=52.0,
                width=200.0,
                height=30.0,
                style=ElementStyle(font_size=16.0, color="#ffffff")
            ),
            # Overflowing width element with large font
            FooterElement(
                id="el_overflow",
                type="text",
                text="Massive text line that goes far beyond the 1080px right margin of the footer",
                x=900.0,
                y=100.0,
                width=450.0,
                height=30.0,
                style=ElementStyle(font_size=24.0, color="#ffffff")
            )
        ]
    )

    fixed, changes, val_report = AutoAdjust.fix_all(bad_footer, 1080.0, 1080.0)

    # 1. Padding normalized to minimum safety standards
    assert fixed.padding["left"] >= 16.0
    assert fixed.padding["right"] >= 16.0
    assert fixed.padding["top"] >= 10.0
    assert fixed.padding["bottom"] >= 10.0

    # 2. Font sizes normalized (no font below 10px)
    assert fixed.elements[0].style.font_size >= 10.0

    # 3. Overlaps resolved (overlap1 and overlap2 no longer collide)
    el1 = next(e for e in fixed.elements if e.id == "el_overlap1")
    el2 = next(e for e in fixed.elements if e.id == "el_overlap2")
    y_overlap = (el1.y + 2.0 < el2.y + el2.height) and (el1.y + el1.height > el2.y + 2.0)
    x_overlap = (el1.x + 2.0 < el2.x + el2.width) and (el1.x + el1.width > el2.x + 2.0)
    assert not (x_overlap and y_overlap), "Colliding elements should be separated"

    # 4. Overflow element constrained within footer width
    el_ov = next(e for e in fixed.elements if e.id == "el_overflow")
    assert el_ov.x + el_ov.width <= fixed.width

    # 5. Contrast improved (dark text on dark background fixed)
    assert fixed.elements[0].style.color != "#222222"
    assert len(changes) >= 4


def test_api_rearrange_endpoint(rich_brand):
    """Verify /api/rearrange allows any arrangement to work with any background shape."""
    # Start with a wave background footer
    initial_footer = FooterDesign(
        id="custom_footer",
        name="Custom Wave",
        style_category="wave",
        width=1080.0,
        height=200.0,
        x=0.0,
        y=880.0,
        columns=2,
        background=FooterBackground(shape="fluid_wave_single", color="#1e1b4b"),
        elements=[]
    )

    arrangements_to_test = [
        "centred", "two_column", "three_column", "four_column",
        "qr_focused", "contact_card", "vertical_sidebar", "asymmetric"
    ]

    for arr in arrangements_to_test:
        req = RearrangeRequest(
            footer=initial_footer,
            arrangement=arr,
            brand=rich_brand,
            poster_width=1080.0,
            poster_height=1080.0
        )
        res = rearrange(req)
        assert res.content_arrangement == arr
        # Background shape is preserved
        assert res.background.shape == "fluid_wave_single"
        assert len(res.elements) >= 3
        # Elements are strictly within bounds
        for el in res.elements:
            assert el.x >= 0
            assert el.x + el.width <= 1082.0


def test_demonstration_of_visibly_different_arrangements_on_same_input(rich_brand):
    """
    Demonstrate that with identical poster dimensions and identical brand data,
    the layout engine generates genuinely distinct spatial and column arrangements.
    """
    engine = AdaptiveLayoutEngine()
    variations = engine.generate_adaptive_variations(
        poster_width=1080,
        poster_height=1920,
        brand=rich_brand,
        category_filter="all",
        arrangement_filter="all"
    )

    arrangements_found = {}
    for v in variations:
        arr = v.content_arrangement
        if arr not in arrangements_found:
            # Record key layout fingerprints: column count, logo x/y, contacts x/y
            logo_el = next((e for e in v.elements if e.type == "logo"), None)
            qr_el = next((e for e in v.elements if e.type == "qr"), None)
            brand_el = next((e for e in v.elements if e.type == "text" and e.text == rich_brand.brand_name), None)

            fingerprint = {
                "arrangement": arr,
                "columns": v.columns,
                "logo_pos": (round(logo_el.x, 1), round(logo_el.y, 1)) if logo_el else None,
                "brand_pos": (round(brand_el.x, 1), round(brand_el.y, 1)) if brand_el else None,
                "qr_pos": (round(qr_el.x, 1), round(qr_el.y, 1)) if qr_el else None,
                "element_count": len(v.elements)
            }
            arrangements_found[arr] = fingerprint

    print(f"\n--- DEMONSTRATION: {len(arrangements_found)} VISIBLY DIFFERENT ARRANGEMENTS ON SAME INPUT ---")
    for name, fp in sorted(arrangements_found.items()):
        print(f"• [{fp['arrangement'].upper()}] Cols: {fp['columns']} | Logo @ {fp['logo_pos']} | Brand @ {fp['brand_pos']} | QR @ {fp['qr_pos']} | Elements: {fp['element_count']}")

    assert len(arrangements_found) >= 15, f"Expected >= 15 distinct arrangements demonstrated, found {len(arrangements_found)}"


def test_get_position_options_for_any_footer_design(rich_brand):
    """
    Feature Verification: When any footer design is selected, automatically generate
    multiple position variations preserving background shape, brand info, and scannable QR.
    """
    base_footer = FooterDesign(
        id="test_design_wave",
        name="Ocean Wave Luxe",
        style_category="wave",
        content_arrangement="classic_horizontal",
        width=1080.0,
        height=220.0,
        x=0.0,
        y=860.0,
        columns=3,
        background=FooterBackground(shape="fluid_wave_double", color="#0f172a", opacity=0.95),
        elements=[]
    )

    req = PositionOptionsRequest(
        footer=base_footer,
        brand=rich_brand,
        poster_width=1080.0,
        poster_height=1080.0
    )

    options = get_position_options(req)

    # 1. Must return all 20 distinct position variations
    assert len(options) == 20, f"Expected 20 position options, got {len(options)}"

    # 2. Every option must preserve the base background shape and styling
    for opt in options:
        assert opt.background.shape == "fluid_wave_double"
        assert opt.background.color == "#0f172a"
        assert opt.width == 1080.0
        assert opt.height == 220.0
        # Must have valid SVG markup
        assert opt.svg_markup is not None
        assert "<svg" in opt.svg_markup
        # Quality score must be clean
        assert opt.quality_score >= 90.0

    # 3. Position options must span diverse arrangements
    arrs = [o.content_arrangement for o in options]
    assert len(set(arrs)) == 20
    assert "centred" in arrs
    assert "four_column" in arrs
    assert "logo_top" in arrs
    assert "profile_focused" in arrs
    assert "qr_focused" in arrs
    assert "contact_card" in arrs
    assert "vertical_sidebar" in arrs
