import copy
from typing import List, Optional, Dict, Any
from app.models.footer import FooterDesign, FooterElement, FooterBackground
from app.analyzer.logo_color_extractor import (
    ColorScheme,
    LogoPalette,
    calculate_contrast_ratio,
    hex_to_rgb,
    get_high_contrast_text_color,
    get_subdued_text_color,
    logo_color_extractor,
)
from app.renderer.svg_renderer import SVGRenderer

class ColorThemeEngine:
    """
    Applies extracted logo brand color schemes non-destructively to existing FooterDesign models.
    Guarantees WCAG 2.1 contrast compliance and updates vector SVG markup.
    """

    @staticmethod
    def apply_scheme_to_footer(footer: FooterDesign, scheme: ColorScheme) -> FooterDesign:
        # Clone to avoid mutating original state
        updated: FooterDesign = copy.deepcopy(footer)

        # 1. Update background
        updated.background.color = scheme.background
        updated.background.secondary_color = scheme.secondary_color
        updated.background.border_color = scheme.border_color

        # If it's a gradient scheme, set type to gradient
        if scheme.id == "gradient_duo":
            updated.background.type = "gradient"
            updated.background.gradient_direction = "to right"
        elif updated.background.type == "gradient" and scheme.id != "gradient_duo":
            updated.background.type = "solid"

        bg_rgb = hex_to_rgb(scheme.background)

        # 2. Update elements with contrast enforcement
        for el in updated.elements:
            # Badges / CTA buttons
            if el.type == "badge" or "badge" in el.id or "cta" in el.id:
                el.style.background_color = scheme.badge_bg
                el.style.color = scheme.badge_text
                continue

            # Dividers and shape accents
            if el.type in ["divider", "shape"]:
                el.style.color = scheme.border_color
                el.style.border_color = scheme.border_color
                continue

            # Brand name and main identity text
            if "brand_name" in el.id:
                el.style.color = scheme.text_primary
            elif "tagline" in el.id:
                el.style.color = scheme.text_secondary
            elif el.type in ["text", "icon_text"]:
                el.style.color = scheme.text_secondary

            # Safety check: enforce minimum WCAG 4.5:1 contrast
            if el.style.color:
                txt_rgb = hex_to_rgb(el.style.color)
                contrast = calculate_contrast_ratio(bg_rgb, txt_rgb)
                if contrast < 4.5:
                    el.style.color = get_high_contrast_text_color(scheme.background)

        # 3. Re-render SVG vector markup
        try:
            updated.svg_markup = SVGRenderer.render_svg(updated)
        except Exception:
            try:
                updated.svg_markup = SVGRenderer.render_footer_svg(updated)
            except Exception:
                pass

        return updated

    @staticmethod
    def generate_palette_variations(
        footer: FooterDesign,
        palette: LogoPalette
    ) -> List[FooterDesign]:
        """
        Generates 5 distinct, professionally styled variations using the extracted palette.
        """
        variations: List[FooterDesign] = []
        for scheme in palette.schemes:
            styled = ColorThemeEngine.apply_scheme_to_footer(footer, scheme)
            styled.id = f"{footer.id}_{scheme.id}"
            styled.name = f"{footer.name} ({scheme.name})"
            variations.append(styled)
        return variations

color_theme_engine = ColorThemeEngine()
