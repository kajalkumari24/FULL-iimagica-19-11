from typing import List, Dict, Any
from app.models.footer import FooterDesign, FooterElement
from app.analyzer.color_analyzer import calculate_contrast_ratio, hex_to_rgb

class LayoutValidator:
    @classmethod
    def validate_footer(cls, footer: FooterDesign) -> Dict[str, Any]:
        """
        Validates the footer layout for overflow, collisions, contrast, and edge safety.
        Uses accurate Axis-Aligned Bounding Box (AABB) collision checks and full 4-boundary overflow tests.
        Returns is_valid (bool), quality_score (0-100), and list of notices.
        """
        notices: List[str] = []
        critical_errors: List[str] = []
        score = 100.0

        bg_rgb = hex_to_rgb(footer.background.color or "#0f172a")
        pad_l = footer.padding.get("left", 16.0)
        pad_t = footer.padding.get("top", 10.0)
        pad_r = footer.width - footer.padding.get("right", 16.0)
        pad_b = footer.height - footer.padding.get("bottom", 10.0)

        visible_els = [el for el in footer.elements if el.visible]

        # 1. Check all four boundaries and overflow
        for el in visible_els:
            name = el.label or el.id
            if el.width <= 0 or el.height <= 0:
                critical_errors.append(f"Element '{name}' has invalid dimensions ({el.width}x{el.height})")
                score -= 15.0

            # Hard boundary checks (outside canvas)
            if el.x < 0:
                critical_errors.append(f"Element '{name}' overflows left canvas edge (x={el.x:.1f})")
                score -= 12.0
            if el.y < 0:
                critical_errors.append(f"Element '{name}' overflows top canvas edge (y={el.y:.1f})")
                score -= 12.0
            if el.x + el.width > footer.width + 1.0:
                critical_errors.append(f"Element '{name}' overflows right canvas edge (right={el.x + el.width:.1f} > {footer.width:.1f})")
                score -= 12.0
            if el.y + el.height > footer.height + 1.0:
                critical_errors.append(f"Element '{name}' overflows bottom canvas edge (bottom={el.y + el.height:.1f} > {footer.height:.1f})")
                score -= 12.0

            # Soft padding warnings
            if el.x < pad_l - 2.0 or el.x + el.width > pad_r + 2.0:
                notices.append(f"Element '{name}' encroaches on horizontal padding")
                score -= 2.0
            if el.y < pad_t - 2.0 or el.y + el.height > pad_b + 2.0:
                notices.append(f"Element '{name}' encroaches on vertical padding")
                score -= 2.0

            # Typography readability check
            if el.type in ["text", "icon_text"]:
                font_sz = el.style.font_size or 12.0
                if font_sz < 8.5:
                    notices.append(f"Text in '{name}' is below readable threshold ({font_sz}px < 8.5px)")
                    score -= 5.0

        # 2. Check collisions using accurate AABB intersection (excluding vertical/horizontal dividers)
        non_dividers = [el for el in visible_els if el.type != "divider"]
        for i in range(len(non_dividers)):
            for j in range(i + 1, len(non_dividers)):
                e1 = non_dividers[i]
                e2 = non_dividers[j]

                # AABB intersection check with 1.5px tolerance
                x_overlap = (e1.x + 1.5 < e2.x + e2.width) and (e1.x + e1.width > e2.x + 1.5)
                y_overlap = (e1.y + 1.5 < e2.y + e2.height) and (e1.y + e1.height > e2.y + 1.5)

                if x_overlap and y_overlap:
                    n1 = e1.label or e1.id
                    n2 = e2.label or e2.id
                    critical_errors.append(f"Collision detected between '{n1}' and '{n2}'")
                    score -= 10.0

        # 3. Check readability contrast
        for el in visible_els:
            if el.type in ["text", "icon_text"]:
                c_rgb = hex_to_rgb(el.style.color or "#ffffff")
                contrast = calculate_contrast_ratio(bg_rgb, c_rgb)
                if contrast < 3.0:
                    notices.append(f"Low contrast ({contrast:.1f}:1) for text in '{el.label or el.id}'")
                    score -= 6.0

        all_notices = critical_errors + notices
        final_score = max(0.0, min(100.0, round(score, 1)))
        footer.quality_score = final_score
        footer.validation_notices = all_notices

        # Must have zero critical errors and score >= 75 to be considered valid
        is_valid = len(critical_errors) == 0 and final_score >= 75.0

        return {
            "is_valid": is_valid,
            "quality_score": final_score,
            "notices": all_notices,
            "critical_errors": critical_errors
        }
