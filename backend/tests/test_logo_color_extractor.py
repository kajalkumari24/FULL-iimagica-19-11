import io
import base64
import pytest
from PIL import Image, ImageDraw
from fastapi.testclient import TestClient

from app.main import app
from app.analyzer.logo_color_extractor import (
    LogoColorExtractor,
    rgb_to_hex,
    hex_to_rgb,
    calculate_contrast_ratio,
    get_high_contrast_text_color,
    logo_color_extractor,
)
from app.engine.color_theme_engine import color_theme_engine
from app.models.footer import FooterDesign, FooterBackground, FooterElement, ElementStyle
from app.models.brand import BrandProfile
from app.main import (
    extract_logo_colors,
    apply_logo_colors,
    generate_logo_color_variations,
    ExtractLogoColorsRequest,
    ApplyLogoColorsRequest,
    GenerateLogoColorVariationsRequest,
)

def create_sample_logo_png_base64() -> str:
    # Create 100x100 transparent image with blue (#1d4ed8) circle and orange (#f97316) star
    img = Image.new("RGBA", (100, 100), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    # Blue dominant badge
    draw.rectangle([10, 10, 90, 90], fill=(29, 78, 216, 255))
    # Orange accent circle
    draw.ellipse([30, 30, 70, 70], fill=(249, 115, 22, 255))
    
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    b64 = base64.b64encode(buf.getvalue()).decode("utf-8")
    return f"data:image/png;base64,{b64}"

def create_sample_footer() -> FooterDesign:
    return FooterDesign(
        id="test_footer_1",
        name="Test Footer",
        style_category="modern",
        content_arrangement="classic_horizontal",
        width=1080,
        height=180,
        x=0,
        y=1740,
        background=FooterBackground(
            color="#0f172a",
            secondary_color="#1e293b",
            shape="rounded_box"
        ),
        elements=[
            FooterElement(
                id="brand_name",
                type="text",
                text="Apex Global",
                x=50,
                y=30,
                width=200,
                height=30,
                style=ElementStyle(color="#ffffff", font_size=20)
            ),
            FooterElement(
                id="contact_phone",
                type="icon_text",
                text="+1 555 0199",
                x=500,
                y=30,
                width=150,
                height=20,
                style=ElementStyle(color="#cbd5e1", font_size=14)
            ),
            FooterElement(
                id="cta_badge",
                type="badge",
                text="Contact Us",
                x=800,
                y=30,
                width=120,
                height=35,
                style=ElementStyle(color="#ffffff", background_color="#3b82f6")
            )
        ]
    )

def test_contrast_ratio_formula():
    white = (255, 255, 255)
    black = (0, 0, 0)
    ratio = calculate_contrast_ratio(white, black)
    assert ratio >= 20.0  # Max is 21.0

    # Ensure contrast of text color against dark bg
    dark_bg = "#0f172a"
    text_color = get_high_contrast_text_color(dark_bg)
    assert text_color == "#ffffff"

    # Ensure contrast of text color against light bg
    light_bg = "#f8fafc"
    text_color_light = get_high_contrast_text_color(light_bg)
    assert text_color_light == "#0f172a"

def test_extract_palette_from_image():
    logo_b64 = create_sample_logo_png_base64()
    palette = logo_color_extractor.extract_palette(logo_b64)

    assert palette.primary is not None
    assert palette.primary.startswith("#")
    assert palette.secondary is not None
    assert palette.accent is not None
    assert palette.dark_shade is not None
    assert palette.light_shade is not None
    assert len(palette.schemes) == 5

    # Scheme names check
    scheme_ids = [s.id for s in palette.schemes]
    assert "bold_brand" in scheme_ids
    assert "dark_luxury" in scheme_ids
    assert "clean_light" in scheme_ids
    assert "gradient_duo" in scheme_ids
    assert "accent_pop" in scheme_ids

def test_extract_palette_from_svg():
    svg_sample = '<svg viewBox="0 0 100 100"><rect fill="#0ea5e9" width="100" height="100"/><circle fill="#ec4899" cx="50" cy="50" r="30"/></svg>'
    palette = logo_color_extractor.extract_palette(svg_sample)
    assert palette.primary in ["#0ea5e9", "#ec4899"]
    assert palette.secondary in ["#0ea5e9", "#ec4899"]
    assert len(palette.schemes) == 5

def test_apply_color_scheme_to_footer():
    footer = create_sample_footer()
    logo_b64 = create_sample_logo_png_base64()
    palette = logo_color_extractor.extract_palette(logo_b64)
    
    clean_light_scheme = next(s for s in palette.schemes if s.id == "clean_light")
    updated = color_theme_engine.apply_scheme_to_footer(footer, clean_light_scheme)

    # Background must match clean light
    assert updated.background.color == clean_light_scheme.background
    # Positions must be strictly preserved
    assert updated.width == footer.width
    assert updated.height == footer.height
    assert updated.elements[0].x == footer.elements[0].x
    # Text contrast must be compliant with light background
    brand_el = next(e for e in updated.elements if e.id == "brand_name")
    assert brand_el.style.color != "#ffffff" # Cannot be white on light bg

def test_generate_palette_variations():
    footer = create_sample_footer()
    logo_b64 = create_sample_logo_png_base64()
    palette = logo_color_extractor.extract_palette(logo_b64)

    variations = color_theme_engine.generate_palette_variations(footer, palette)
    assert len(variations) == 5
    bg_colors = [v.background.color for v in variations]
    # Variations should have differing backgrounds
    assert len(set(bg_colors)) >= 3

def test_api_extract_logo_colors():
    logo_b64 = create_sample_logo_png_base64()
    req = ExtractLogoColorsRequest(logo_url=logo_b64)
    data = extract_logo_colors(req)
    assert data.primary is not None
    assert data.secondary is not None
    assert data.accent is not None
    assert len(data.schemes) == 5

def test_api_apply_logo_colors():
    footer = create_sample_footer()
    logo_b64 = create_sample_logo_png_base64()
    req = ExtractLogoColorsRequest(logo_url=logo_b64)
    palette = extract_logo_colors(req)
    scheme = palette.schemes[0]

    applied = apply_logo_colors(ApplyLogoColorsRequest(
        footer=footer,
        scheme=scheme
    ))
    assert applied.background.color == scheme.background

def test_api_generate_logo_color_variations():
    footer = create_sample_footer()
    logo_b64 = create_sample_logo_png_base64()
    
    variations = generate_logo_color_variations(GenerateLogoColorVariationsRequest(
        footer=footer,
        logo_url=logo_b64
    ))
    assert len(variations) == 5

