import math
from typing import List, Dict, Any, Optional
from app.models.brand import BrandProfile, LogoItem, ProfileItem, CustomField
from app.models.footer import FooterDesign, FooterElement, FooterBackground, ElementStyle
from app.design_library.templates.adaptive_templates import (
    AdaptiveTemplate,
    ADAPTIVE_TEMPLATES_REGISTRY,
    get_template_by_id,
)
from app.design_library.shapes.adaptive_shapes import AdaptiveShapes
from app.analyzer.content_analyzer import ContentAnalyzer
from app.analyzer.color_analyzer import calculate_brightness, hex_to_rgb
from app.engine.typography_engine import TypographyEngine
from app.engine.arrangement_engine import ArrangementEngine
from app.renderer.svg_renderer import SVGRenderer
from app.validator.layout_validator import LayoutValidator

class AdaptiveLayoutEngine:
    def __init__(self):
        self.content_analyzer = ContentAnalyzer()

    @classmethod
    def rank_arrangements_for_brand(cls, brand: BrandProfile, pw: float, ph: float) -> List[str]:
        """
        Intelligently ranks and scores the 20 arrangements based on content metrics:
        - If profile photos exist: boost profile_focused, profile_circle, floating_elements, two_column
        - If QR code exists: boost qr_focused, split_panel, classic_horizontal, two_column
        - If multiple logos: boost logo_top, vertical_sidebar, four_column, three_column
        - If long brand name: boost two_column, asymmetric, left_aligned_stack, vertical_stacked
        - If high contact count (>=5): boost four_column, contact_card, two_column, social_bottom
        - If compact/narrow aspect: boost compact, centred, classic_horizontal
        """
        scores: Dict[str, float] = {arr: 10.0 for arr in ArrangementEngine.ARRANGEMENTS}
        aspect = pw / max(1.0, ph)

        # Profile Photo prioritization
        if brand.profiles:
            scores["profile_focused"] += 25.0
            scores["profile_circle"] += 22.0
            scores["floating_elements"] += 15.0
            scores["two_column"] += 12.0

        # QR Code prioritization
        if brand.qr_code_content:
            scores["qr_focused"] += 20.0
            scores["split_panel"] += 16.0
            scores["classic_horizontal"] += 14.0
            scores["two_column"] += 12.0

        # Multiple Logos prioritization
        if len(brand.logos) > 1:
            scores["logo_top"] += 22.0
            scores["vertical_sidebar"] += 18.0
            scores["four_column"] += 15.0
            scores["three_column"] += 14.0

        # Long Brand Title
        if len(brand.brand_name) > 24:
            scores["two_column"] += 18.0
            scores["asymmetric"] += 16.0
            scores["left_aligned_stack"] += 14.0
            scores["vertical_stacked"] += 14.0

        # Contact Density
        contact_count = sum(bool(getattr(brand, field, None)) for field in ["phone", "whatsapp", "email", "website", "address"])
        if contact_count >= 4:
            scores["four_column"] += 20.0
            scores["contact_card"] += 18.0
            scores["two_column"] += 15.0
            scores["social_bottom"] += 15.0

        # Poster Aspect
        if aspect < 0.85:  # Portrait
            scores["two_column"] += 12.0
            scores["vertical_stacked"] += 10.0
            scores["asymmetric"] += 8.0
        elif aspect > 1.3:  # Landscape
            scores["four_column"] += 15.0
            scores["classic_horizontal"] += 12.0
            scores["compact"] += 10.0

        # Sort arrangements by score descending
        ranked = sorted(scores.keys(), key=lambda k: scores[k], reverse=True)
        return ranked

    def generate_adaptive_variations(
        self,
        poster_width: int,
        poster_height: int,
        brand: BrandProfile,
        palette: Optional[List[str]] = None,
        target_ratio: Optional[float] = None,
        category_filter: Optional[str] = "all",
        arrangement_filter: Optional[str] = "all",
    ) -> List[FooterDesign]:
        pw = float(poster_width)
        ph = float(poster_height)
        aspect_ratio = pw / max(1.0, ph)

        if aspect_ratio < 0.85:
            aspect_category = "portrait"
        elif aspect_ratio <= 1.25:
            aspect_category = "square"
        else:
            aspect_category = "landscape"

        content_metrics = self.content_analyzer.analyze_brand_content(brand)

        templates = ADAPTIVE_TEMPLATES_REGISTRY
        if category_filter and category_filter != "all":
            filtered = [t for t in templates if t.category.lower() == category_filter.lower()]
            if filtered:
                templates = filtered

        if arrangement_filter and arrangement_filter != "all":
            filtered = [t for t in templates if t.arrangement.lower() == arrangement_filter.lower()]
            if filtered:
                templates = filtered

        # Generate footer designs
        variations: List[FooterDesign] = []
        for tpl in templates:
            var = self._build_adaptive_footer(
                tpl=tpl,
                pw=pw,
                ph=ph,
                aspect_category=aspect_category,
                aspect_ratio=aspect_ratio,
                brand=brand,
                content_metrics=content_metrics,
                palette=palette,
                target_ratio=target_ratio,
            )
            LayoutValidator.validate_footer(var)
            variations.append(var)

        # Intelligent sorting to ensure diversity:
        # Group by arrangement and round-robin pick so the top results contain at least 10 different arrangements
        if not arrangement_filter or arrangement_filter == "all":
            arrangement_groups: Dict[str, List[FooterDesign]] = {}
            for v in variations:
                arr = v.content_arrangement
                arrangement_groups.setdefault(arr, []).append(v)

            diverse_list: List[FooterDesign] = []
            max_len = max(len(g) for g in arrangement_groups.values()) if arrangement_groups else 0
            # Rank arrangements based on brand characteristics
            ranked_order = self.rank_arrangements_for_brand(brand, pw, ph)

            for i in range(max_len):
                for arr_name in ranked_order:
                    if arr_name in arrangement_groups and i < len(arrangement_groups[arr_name]):
                        diverse_list.append(arrangement_groups[arr_name][i])

            # Fallback to any remaining
            seen_ids = {d.id for d in diverse_list}
            for v in variations:
                if v.id not in seen_ids:
                    diverse_list.append(v)

            variations = diverse_list

        return variations

    def _build_adaptive_footer(
        self,
        tpl: AdaptiveTemplate,
        pw: float,
        ph: float,
        aspect_category: str,
        aspect_ratio: float,
        brand: BrandProfile,
        content_metrics: Dict[str, Any],
        palette: Optional[List[str]],
        target_ratio: Optional[float],
        override_arrangement: Optional[str] = None,
    ) -> FooterDesign:
        # 1. Height calculation
        if target_ratio and 0.08 <= target_ratio <= 0.35:
            ratio = target_ratio
        else:
            if aspect_category == "portrait":
                ratio = tpl.height_rules.portrait
            elif aspect_category == "square":
                ratio = tpl.height_rules.square
            else:
                ratio = tpl.height_rules.landscape

            field_count = content_metrics.get("field_count", 0)
            if field_count >= 8 or len(brand.logos) > 1 or len(brand.profiles) > 1:
                ratio = min(0.30, ratio * 1.22)
            elif field_count <= 2:
                ratio = max(0.09, ratio * 0.90)

        fh = round(ph * ratio, 1)

        # 2. Width and Position calculation
        shape_params = tpl.shape_parameters
        if shape_params.inset_margin_ratio > 0.0:
            margin_x = round(pw * shape_params.inset_margin_ratio)
            margin_b = round(ph * (shape_params.inset_margin_ratio * 0.75))
            fw = round(pw - (margin_x * 2), 1)
            fx = float(margin_x)
            fy = round(ph - fh - margin_b, 1)
        else:
            fw = pw
            fx = 0.0
            fy = round(ph - fh, 1)

        # 3. Dynamic Padding & Usable Boundary
        pad_x = max(18.0, fw * 0.035)
        pad_y = max(10.0, fh * 0.06)

        top_offset = 0.0
        if shape_params.has_notch:
            top_offset = min(fh * 0.20, 26.0)
        elif "wave" in tpl.shape_key:
            top_offset = min(fh * 0.18, 28.0)
        elif any(k in tpl.shape_key for k in ["diagonal", "bevel", "slanted", "angle"]):
            top_offset = min(fh * 0.15, 22.0)
        elif any(k in tpl.shape_key for k in ["convex", "concave", "arch", "circle", "zigzag", "polygon"]):
            top_offset = min(fh * 0.14, 20.0)

        # 4. Color Palette Resolution
        bg_col = brand.primary_color if brand.primary_color and brand.primary_color != "#ffffff" else tpl.default_bg_color
        sec_col = brand.secondary_color if brand.secondary_color else tpl.default_secondary_color
        acc_col = brand.accent_color if brand.accent_color else tpl.default_accent_color

        if palette and len(palette) >= 2:
            sec_col = palette[1]
            if len(palette) >= 3:
                acc_col = palette[2]

        is_bg_dark = True
        try:
            r, g, b = hex_to_rgb(bg_col)
            is_bg_dark = calculate_brightness(r, g, b) < 0.5
        except Exception:
            pass

        text_primary = "#ffffff" if is_bg_dark else "#09090b"
        text_secondary = "#e2e8f0" if is_bg_dark else "#334155"

        # 5. Proportional Typography Scaling
        font_scale = TypographyEngine.calculate_base_scale(pw, ph)
        font_sizes = TypographyEngine.get_font_sizes(font_scale)

        # 6. Apply Arrangement Layout Algorithm
        arrangement_name = override_arrangement or getattr(tpl, "arrangement", "classic_horizontal")
        elements = ArrangementEngine.apply_arrangement(
            arrangement_name=arrangement_name,
            fw=fw,
            fh=fh,
            pad_x=pad_x,
            pad_y=pad_y,
            top_offset=top_offset,
            brand=brand,
            font_sizes=font_sizes,
            font_scale=font_scale,
            colors={
                "text_primary": text_primary,
                "text_secondary": text_secondary,
                "acc_col": acc_col,
                "sec_col": sec_col,
                "bg_col": bg_col,
            },
            default_font=tpl.default_font,
            default_frame=tpl.default_frame,
            shape_key=tpl.shape_key,
        )

        # Determine column structure for metadata
        num_columns = 4 if "four" in arrangement_name else (2 if any(k in arrangement_name for k in ["two", "split", "sidebar", "asymmetric", "card", "qr"]) else (1 if any(k in arrangement_name for k in ["stacked", "centred", "compact"]) else 3))

        bg_obj = FooterBackground(
            type="solid",
            color=bg_col,
            secondary_color=sec_col,
            opacity=0.96 if shape_params.shadow else 1.0,
            shape=tpl.shape_key,
            border_radius=shape_params.corner_radius,
            shadow=shape_params.shadow
        )

        design = FooterDesign(
            id=f"{tpl.id}_{arrangement_name}_{int(aspect_ratio*100)}",
            name=tpl.name,
            style_category=tpl.category,
            content_arrangement=arrangement_name,
            width=fw,
            height=fh,
            x=fx,
            y=fy,
            columns=num_columns,
            padding={"top": pad_y + top_offset, "bottom": pad_y, "left": pad_x, "right": pad_x},
            background=bg_obj,
            elements=elements,
            quality_score=100.0
        )

        design.svg_markup = SVGRenderer.render_footer_svg(design)
        return design
