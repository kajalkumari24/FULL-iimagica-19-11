from typing import List, Tuple, Dict, Any
from app.models.footer import FooterDesign, FooterElement
from app.analyzer.color_analyzer import calculate_brightness, calculate_contrast_ratio, hex_to_rgb
from app.validator.layout_validator import LayoutValidator
from app.engine.typography_engine import TypographyEngine

class AutoAdjust:
    @classmethod
    def fix_all(cls, footer: FooterDesign, poster_width: float, poster_height: float) -> Tuple[FooterDesign, List[str], Dict[str, Any]]:
        changes = []

        # 1. Padding normalization
        pad_fixes = cls.fix_padding(footer)
        if pad_fixes > 0:
            changes.append(f"Normalized layout padding and safety margins ({pad_fixes} bounds aligned)")

        # 2. Font sizes & readable limits
        font_fixes = cls.fix_font_sizes(footer)
        if font_fixes > 0:
            changes.append(f"Adjusted font sizes and text wrapping for {font_fixes} elements")

        # 3. Column alignment normalization
        align_fixes = cls.fix_alignment(footer)
        if align_fixes > 0:
            changes.append(f"Snapped {align_fixes} elements to clean column alignment axes")

        # 4. Spacing balancing by columns
        cls.fix_spacing(footer)
        changes.append("Balanced elements across columns and normalized vertical flow")

        # 5. Overlap separation using iterative AABB resolution
        overlaps_resolved = cls.fix_overlaps(footer.elements, footer.height)
        if overlaps_resolved > 0:
            changes.append(f"Separated {overlaps_resolved} colliding elements")

        # 6. Bounds & Overflow correction
        cls.fix_overflows(footer)
        changes.append("Constrained elements within canvas padding and safety margins")

        # 7. Contrast adjustment
        contrast_fixes = cls.fix_contrast(footer)
        if contrast_fixes > 0:
            changes.append(f"Enhanced readability for {contrast_fixes} text elements against background")

        # 8. Mandatory Post-Fix Revalidation
        validation_report = LayoutValidator.validate_footer(footer)
        footer.quality_score = validation_report["quality_score"]
        footer.validation_notices = validation_report["notices"]
        if validation_report["is_valid"]:
            changes.append(f"Validated clean layout (Quality score: {validation_report['quality_score']}/100)")
        else:
            changes.append(f"Warning: Layout has remaining notices (Quality score: {validation_report['quality_score']}/100)")

        return footer, changes, validation_report

    @classmethod
    def fix_padding(cls, footer: FooterDesign) -> int:
        fixes = 0
        current_pad = footer.padding or {}
        min_l = max(16.0, float(current_pad.get("left", 20.0)))
        min_r = max(16.0, float(current_pad.get("right", 20.0)))
        min_t = max(10.0, float(current_pad.get("top", 12.0)))
        min_b = max(10.0, float(current_pad.get("bottom", 12.0)))

        if (footer.padding.get("left") != min_l or
            footer.padding.get("right") != min_r or
            footer.padding.get("top") != min_t or
            footer.padding.get("bottom") != min_b):
            footer.padding = {"left": min_l, "right": min_r, "top": min_t, "bottom": min_b}
            fixes += 1
        return fixes

    @classmethod
    def fix_font_sizes(cls, footer: FooterDesign) -> int:
        fixes = 0
        pad_x = footer.padding.get("left", 20.0)
        pad_r = footer.padding.get("right", 20.0)
        max_content_w = footer.width - pad_x - pad_r

        for el in footer.elements:
            if not el.visible or el.type not in ["text", "icon_text", "badge"]:
                continue
            if not el.style:
                continue

            fs = el.style.font_size or 13.0
            # Enforce minimum readable font size (10.0px)
            if fs < 10.0:
                el.style.font_size = 10.0
                fs = 10.0
                fixes += 1

            # Check if text exceeds available horizontal width from el.x
            avail_w = max(50.0, footer.width - pad_r - el.x)
            text_str = el.text or ""
            if text_str and el.width > avail_w:
                # Need to downscale font size or wrap
                current_w = el.width
                scale_ratio = avail_w / current_w
                new_fs = max(10.0, fs * scale_ratio)
                el.style.font_size = round(new_fs, 1)
                
                # Recalculate text width
                measured_w = TypographyEngine.measure_text_width(
                    text_str, el.style.font_size, el.style.font_weight or "normal"
                )
                if el.type == "icon_text":
                    measured_w += 24.0  # include icon + gap
                el.width = min(avail_w, round(measured_w, 1))
                fixes += 1

        return fixes

    @classmethod
    def fix_alignment(cls, footer: FooterDesign) -> int:
        fixes = 0
        col_count = max(1, footer.columns)
        col_w = footer.width / col_count
        pad_l = footer.padding.get("left", 20.0)

        # Cluster elements by approximate column X
        clusters: Dict[int, List[FooterElement]] = {}
        for el in footer.elements:
            if not el.visible or el.type == "divider":
                continue
            col_idx = int(el.x // col_w)
            clusters.setdefault(col_idx, []).append(el)

        for col_idx, els in clusters.items():
            if len(els) < 2:
                continue
            # Determine dominant left alignment
            min_x = min(e.x for e in els)
            # If elements are within 24px of each other, snap them to common left
            for e in els:
                if 0 < abs(e.x - min_x) <= 24.0:
                    e.x = min_x
                    fixes += 1

        return fixes

    @classmethod
    def fix_overflows(cls, footer: FooterDesign):
        pad_x = footer.padding.get("left", 16.0)
        pad_y = footer.padding.get("top", 10.0)
        max_x = footer.width - footer.padding.get("right", 16.0)
        max_y = footer.height - footer.padding.get("bottom", 10.0)

        for el in footer.elements:
            if not el.visible:
                continue
            # Constrain X
            if el.x < pad_x:
                el.x = pad_x
            if el.x + el.width > max_x:
                if el.width > (max_x - pad_x):
                    el.width = max(20.0, max_x - pad_x)
                    el.x = pad_x
                else:
                    el.x = max(pad_x, max_x - el.width)
            
            # Constrain Y
            if el.y < pad_y:
                el.y = pad_y
            if el.y + el.height > max_y:
                if el.height > (max_y - pad_y):
                    el.height = max(14.0, max_y - pad_y)
                    el.y = pad_y
                else:
                    el.y = max(pad_y, max_y - el.height)

    @classmethod
    def fix_overlaps(cls, elements: List[FooterElement], max_h: float) -> int:
        resolved = 0
        non_dividers = [e for e in elements if e.visible and e.type != "divider"]
        # Sort top-to-bottom, left-to-right
        sorted_els = sorted(non_dividers, key=lambda e: (e.x // 100, e.y))
        
        for i in range(len(sorted_els)):
            for j in range(i + 1, len(sorted_els)):
                e1 = sorted_els[i]
                e2 = sorted_els[j]

                # Check AABB collision
                x_overlap = (e1.x + 2.0 < e2.x + e2.width) and (e1.x + e1.width > e2.x + 2.0)
                y_overlap = (e1.y + 2.0 < e2.y + e2.height) and (e1.y + e1.height > e2.y + 2.0)

                if x_overlap and y_overlap:
                    # Resolve by shifting e2 down below e1
                    shift_amount = (e1.y + e1.height + 4.0) - e2.y
                    if shift_amount > 0:
                        e2.y += shift_amount
                        resolved += 1
        return resolved

    @classmethod
    def fix_contrast(cls, footer: FooterDesign) -> int:
        bg_hex = footer.background.color or "#0f172a"
        bg_rgb = hex_to_rgb(bg_hex)
        is_bg_dark = calculate_brightness(bg_rgb[0], bg_rgb[1], bg_rgb[2]) < 0.5

        fixes = 0
        for el in footer.elements:
            if not el.visible:
                continue
            if el.type in ["text", "icon_text"]:
                el_color = el.style.color or ("#ffffff" if is_bg_dark else "#0f172a")
                el_rgb = hex_to_rgb(el_color)
                contrast = calculate_contrast_ratio(bg_rgb, el_rgb)

                # WCAG AA requires at least 4.5:1 for body
                if contrast < 3.5:
                    el.style.color = "#ffffff" if is_bg_dark else "#09090b"
                    fixes += 1
        return fixes

    @classmethod
    def fix_spacing(cls, footer: FooterDesign):
        # Evenly balance elements by column
        by_col: Dict[int, List[FooterElement]] = {}
        col_width = max(100.0, footer.width / max(1, footer.columns))
        for el in footer.elements:
            if not el.visible or el.type == "divider":
                continue
            col_idx = int(el.x // col_width)
            by_col.setdefault(col_idx, []).append(el)

        pad_t = footer.padding.get("top", 10.0)
        max_b = footer.height - footer.padding.get("bottom", 10.0)

        for col_idx, els in by_col.items():
            els.sort(key=lambda e: e.y)
            cur_y = pad_t
            for el in els:
                if el.y < cur_y:
                    el.y = cur_y
                cur_y = min(max_b - el.height, el.y + el.height + 4.0)

