import html
from typing import Dict, Any, Optional

class AdaptiveShapes:
    """
    Parametric, responsive SVG shape generator.
    Produces mathematically clamped SVG path definitions that adapt dynamically
    to arbitrary widths, heights, and aspect ratios without distortion.
    Includes original 18 base shapes + 30 new professional modern shapes.
    """

    @classmethod
    def generate_shape_svg(
        cls,
        shape_key: str,
        width: float,
        height: float,
        fill: str,
        secondary_fill: str = "",
        accent_color: str = "#f59e0b",
        opacity: float = 1.0,
        radius: float = 0.0,
        params: Optional[Dict[str, Any]] = None,
    ) -> str:
        shape_key = (shape_key or "classic_rectangle").lower()
        sec = secondary_fill or fill
        p = params or {}

        # Safe proportional clamping
        w = max(100.0, float(width))
        h = max(40.0, float(height))
        uid = f"{int(w)}_{int(h)}"

        # ======================================================================
        # 1. WAVE DESIGNS (Original & New 10 Styles)
        # ======================================================================
        if shape_key in ["fluid_wave_single", "wave_single_smooth"]:
            # 1. Single smooth wave
            amp = min(h * 0.22, 35.0, p.get("curve_amplitude", 24.0))
            return f'''
            <defs>
              <linearGradient id="wave_grad_{uid}" x1="0%" y1="0%" x2="100%" y2="0%">
                <stop offset="0%" stop-color="{fill}" stop-opacity="{opacity}"/>
                <stop offset="100%" stop-color="{sec}" stop-opacity="{opacity}"/>
              </linearGradient>
            </defs>
            <path d="M 0,{amp} Q {w * 0.25},0 {w * 0.5},{amp * 0.5} T {w},{amp * 0.25} L {w},{h} L 0,{h} Z" fill="url(#wave_grad_{uid})" />
            '''

        elif shape_key in ["fluid_wave_double", "wave_double"]:
            # 2. Double wave
            amp = min(h * 0.24, 38.0)
            return f'''
            <path d="M 0,{amp * 0.7} Q {w * 0.35},0 {w * 0.7},{amp * 0.8} T {w},{amp * 0.4} L {w},{h} L 0,{h} Z" fill="{sec}" opacity="{max(0.3, opacity * 0.5)}" />
            <path d="M 0,{amp} Q {w * 0.25},{amp * 0.2} {w * 0.5},{amp * 0.6} T {w},{amp * 0.2} L {w},{h} L 0,{h} Z" fill="{fill}" opacity="{opacity}" />
            '''

        elif shape_key == "wave_triple_layered":
            # 3. Triple layered wave
            amp = min(h * 0.26, 42.0)
            return f'''
            <path d="M 0,{amp * 0.4} Q {w * 0.3},0 {w * 0.6},{amp * 0.5} T {w},{amp * 0.2} L {w},{h} L 0,{h} Z" fill="{accent_color}" opacity="{max(0.25, opacity * 0.35)}" />
            <path d="M 0,{amp * 0.7} Q {w * 0.45},{amp * 0.2} {w * 0.8},{amp * 0.7} T {w},{amp * 0.35} L {w},{h} L 0,{h} Z" fill="{sec}" opacity="{max(0.4, opacity * 0.6)}" />
            <path d="M 0,{amp} Q {w * 0.25},{amp * 0.3} {w * 0.5},{amp * 0.8} T {w},{amp * 0.25} L {w},{h} L 0,{h} Z" fill="{fill}" opacity="{opacity}" />
            '''

        elif shape_key == "wave_asymmetric":
            # 4. Asymmetric wave (high dramatic rise on left, dipping smoothly right)
            crest = min(h * 0.30, 48.0)
            return f'''
            <path d="M 0,0 C {w * 0.25},0 {w * 0.4},{crest} {w},{crest * 0.4} L {w},{h} L 0,{h} Z" fill="{fill}" opacity="{opacity}" />
            <path d="M 0,0 C {w * 0.25},0 {w * 0.4},{crest} {w},{crest * 0.4}" stroke="{accent_color}" stroke-width="2.5" fill="none" opacity="0.8" />
            '''

        elif shape_key == "wave_deep_bottom":
            # 5. Deep bottom wave
            amp = min(h * 0.35, 55.0)
            return f'''
            <path d="M 0,{amp} C {w * 0.33},0 {w * 0.66},{amp * 1.3} {w},{amp * 0.6} L {w},{h} L 0,{h} Z" fill="{fill}" opacity="{opacity}" />
            '''

        elif shape_key == "wave_side":
            # 6. Side wave (originates dynamic crest from left edge)
            return f'''
            <path d="M 0,{h * 0.15} C {w * 0.35},{h * 0.35} {w * 0.65},0 {w},{h * 0.1} L {w},{h} L 0,{h} Z" fill="{fill}" opacity="{opacity}" />
            <path d="M 0,{h * 0.15} C {w * 0.35},{h * 0.35} {w * 0.65},0 {w},{h * 0.1}" stroke="{sec}" stroke-width="3" fill="none" opacity="0.6" />
            '''

        elif shape_key == "wave_curved_corners":
            # 7. Wave with curved corners
            amp = min(h * 0.20, 32.0)
            r = min(20.0, h * 0.15)
            return f'''
            <defs>
              <clipPath id="corner_clip_{uid}">
                <rect width="{w}" height="{h}" rx="{r}" ry="{r}" />
              </clipPath>
            </defs>
            <g clip-path="url(#corner_clip_{uid})">
              <rect width="{w}" height="{h}" fill="{sec}" opacity="0.2" />
              <path d="M 0,{amp} Q {w * 0.25},0 {w * 0.5},{amp * 0.5} T {w},{amp * 0.25} L {w},{h} L 0,{h} Z" fill="{fill}" opacity="{opacity}" />
            </g>
            '''

        elif shape_key == "wave_gradient":
            # 8. Gradient wave (tri-color multi-stop wave)
            amp = min(h * 0.22, 36.0)
            return f'''
            <defs>
              <linearGradient id="grad_wave_multi_{uid}" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stop-color="{fill}" stop-opacity="{opacity}" />
                <stop offset="50%" stop-color="{sec}" stop-opacity="{opacity}" />
                <stop offset="100%" stop-color="{accent_color}" stop-opacity="{opacity * 0.9}" />
              </linearGradient>
            </defs>
            <path d="M 0,{amp} Q {w * 0.3},{amp * 0.2} {w * 0.6},{amp} T {w},{amp * 0.3} L {w},{h} L 0,{h} Z" fill="url(#grad_wave_multi_{uid})" />
            '''

        elif shape_key == "wave_floating_logo":
            # 9. Wave with floating logo area (elevated tab on left)
            amp = min(h * 0.22, 34.0)
            tab_w = min(w * 0.24, 160.0)
            return f'''
            <path d="M 0,0 L {tab_w},0 Q {tab_w + 20},0 {tab_w + 30},{amp} Q {w * 0.65},{amp * 0.3} {w},{amp * 0.8} L {w},{h} L 0,{h} Z" fill="{fill}" opacity="{opacity}" />
            <circle cx="{tab_w * 0.5}" cy="{amp * 0.5}" r="{min(28.0, amp)}" fill="{sec}" opacity="0.25" />
            '''

        elif shape_key == "wave_center_profile":
            # 10. Wave with centre profile section (raised central dome arch)
            amp = min(h * 0.22, 34.0)
            cx = w * 0.5
            dome_r = min(w * 0.12, 55.0)
            return f'''
            <path d="M 0,{amp} Q {cx - dome_r - 20},{amp * 0.6} {cx - dome_r},{amp * 0.4} A {dome_r} {dome_r} 0 0 1 {cx + dome_r},{amp * 0.4} Q {cx + dome_r + 20},{amp * 0.6} {w},{amp} L {w},{h} L 0,{h} Z" fill="{fill}" opacity="{opacity}" />
            <circle cx="{cx}" cy="{amp * 0.4}" r="{dome_r * 0.9}" fill="{sec}" opacity="0.3" />
            '''

        # ======================================================================
        # 2. CURVED DESIGNS (Original & New 7 Styles)
        # ======================================================================
        elif shape_key in ["convex_curve", "curve_convex"]:
            # 11 & 12. Convex curve
            amp = min(h * 0.20, 32.0)
            return f'''
            <path d="M 0,{amp} Q {w * 0.5},0 {w},{amp} L {w},{h} L 0,{h} Z" fill="{fill}" opacity="{opacity}" />
            '''

        elif shape_key in ["concave_curve", "curve_concave"]:
            # 13. Concave curve
            amp = min(h * 0.18, 28.0)
            return f'''
            <path d="M 0,0 Q {w * 0.5},{amp} {w},0 L {w},{h} L 0,{h} Z" fill="{fill}" opacity="{opacity}" />
            '''

        elif shape_key == "curve_half_circle":
            # 11. Half-circle curve
            r = min(w * 0.28, h * 0.45, 90.0)
            cx = w * 0.5
            return f'''
            <path d="M 0,{r * 0.5} Q {cx - r},{r * 0.5} {cx - r},0 A {r} {r} 0 0 1 {cx + r},0 Q {cx + r},{r * 0.5} {w},{r * 0.5} L {w},{h} L 0,{h} Z" fill="{fill}" opacity="{opacity}" />
            '''

        elif shape_key == "curve_double":
            # 14. Double curved footer (smooth rhythmic S-curve)
            amp = min(h * 0.22, 34.0)
            return f'''
            <path d="M 0,{amp * 0.5} C {w * 0.25},0 {w * 0.4},{amp} {w * 0.65},{amp * 0.3} C {w * 0.8},{amp * 0.1} {w * 0.9},{amp * 0.7} {w},{amp * 0.5} L {w},{h} L 0,{h} Z" fill="{fill}" opacity="{opacity}" />
            '''

        elif shape_key == "curve_organic_fluid":
            # 15. Organic fluid curve
            return f'''
            <path d="M 0,{h * 0.12} C {w * 0.2},{h * 0.28} {w * 0.45},0 {w * 0.7},{h * 0.18} C {w * 0.85},{h * 0.28} {w * 0.95},{h * 0.05} {w},{h * 0.1} L {w},{h} L 0,{h} Z" fill="{fill}" opacity="{opacity}" />
            <path d="M 0,{h * 0.12} C {w * 0.2},{h * 0.28} {w * 0.45},0 {w * 0.7},{h * 0.18} C {w * 0.85},{h * 0.28} {w * 0.95},{h * 0.05} {w},{h * 0.1}" stroke="{accent_color}" stroke-width="2" fill="none" opacity="0.75" />
            '''

        elif shape_key in ["arch_dome", "arch", "curve_arch"]:
            # 16. Arch-shaped footer
            arch_r = min(32.0, h * 0.25)
            return f'''
            <path d="M 0,{arch_r} A {arch_r} {arch_r} 0 0 1 {arch_r},0 L {w - arch_r},0 A {arch_r} {arch_r} 0 0 1 {w},{arch_r} L {w},{h} L 0,{h} Z" fill="{fill}" opacity="{opacity}" />
            '''

        elif shape_key == "curve_circular_corners":
            # 17. Circular corner footer
            corner_r = min(40.0, w * 0.08, h * 0.35)
            return f'''
            <path d="M 0,{corner_r} A {corner_r} {corner_r} 0 0 1 {corner_r},0 L {w - corner_r},0 A {corner_r} {corner_r} 0 0 1 {w},{corner_r} L {w},{h} L 0,{h} Z" fill="{fill}" opacity="{opacity}" />
            <line x1="{corner_r}" y1="0" x2="{w - corner_r}" y2="0" stroke="{accent_color}" stroke-width="2" />
            '''

        # ======================================================================
        # 3. MODERN DESIGNS (Original & New 13 Styles)
        # ======================================================================
        elif shape_key in ["diagonal_bevel", "diagonal", "modern_diagonal_layered"]:
            # 18. Diagonal layered footer
            slope = min(h * 0.25, 42.0)
            return f'''
            <polygon points="0,{slope * 1.3} {w},{slope * 0.3} {w},{h} 0,{h}" fill="{sec}" opacity="{max(0.35, opacity * 0.55)}" />
            <polygon points="0,{slope} {w},0 {w},{h} 0,{h}" fill="{fill}" opacity="{opacity}" />
            <line x1="0" y1="{slope}" x2="{w}" y2="0" stroke="{accent_color}" stroke-width="3" />
            '''

        elif shape_key in ["split_angled", "modern_slanted_split"]:
            # 19. Slanted split footer
            w_left = w * p.get("split_ratio", 0.35)
            cut = min(32.0, w * 0.05)
            return f'''
            <polygon points="0,0 {w_left + cut},0 {w_left - cut},{h} 0,{h}" fill="{sec}" opacity="{opacity}" />
            <polygon points="{w_left + cut},0 {w},0 {w},{h} {w_left - cut},{h}" fill="{fill}" opacity="{opacity}" />
            <line x1="{w_left + cut}" y1="0" x2="{w_left - cut}" y2="{h}" stroke="{accent_color}" stroke-width="2.5" />
            '''

        elif shape_key == "modern_zigzag":
            # 20. Zigzag footer (geometric sawtooth apex)
            saw_w = w / 12.0
            saw_h = min(12.0, h * 0.12)
            pts = ["M 0," + str(saw_h)]
            for i in range(12):
                x_mid = (i + 0.5) * saw_w
                x_end = (i + 1) * saw_w
                pts.append(f"L {x_mid},0 L {x_end},{saw_h}")
            pts.append(f"L {w},{h} L 0,{h} Z")
            return f'''
            <path d="{' '.join(pts)}" fill="{fill}" opacity="{opacity}" />
            <path d="{' '.join(pts[:25])}" stroke="{accent_color}" stroke-width="1.5" fill="none" opacity="0.8" />
            '''

        elif shape_key == "modern_geometric_polygon":
            # 21. Geometric polygon footer (faceted angled vertices)
            p1_x, p1_y = w * 0.22, min(h * 0.18, 25.0)
            p2_x, p2_y = w * 0.65, 0.0
            p3_x, p3_y = w * 0.88, min(h * 0.14, 20.0)
            return f'''
            <polygon points="0,{p1_y} {p1_x},0 {p2_x},{p1_y} {p3_x},0 {w},{p3_y} {w},{h} 0,{h}" fill="{fill}" opacity="{opacity}" />
            <line x1="0" y1="{p1_y}" x2="{p1_x}" y2="0" stroke="{accent_color}" stroke-width="2" />
            <line x1="{p2_x}" y1="{p1_y}" x2="{p3_x}" y2="0" stroke="{accent_color}" stroke-width="2" />
            '''

        elif shape_key in ["modern_floating_glass", "frosted_glass"]:
            # 22. Floating glass footer
            r = min(16.0, h * 0.15)
            pad = min(12.0, w * 0.015)
            return f'''
            <defs>
              <filter id="glass_blur_{uid}" x="-5%" y="-10%" width="110%" height="130%">
                <feDropShadow dx="0" dy="8" stdDeviation="14" flood-color="#000000" flood-opacity="0.45" />
              </filter>
            </defs>
            <rect x="{pad}" y="{pad * 0.5}" width="{w - pad * 2}" height="{h - pad}" rx="{r}" fill="{fill}" opacity="0.82" stroke="rgba(255,255,255,0.3)" stroke-width="1.5" filter="url(#glass_blur_{uid})" />
            '''

        elif shape_key in ["modern_transparent_overlay", "transparent"]:
            # 23. Transparent overlay footer
            return f'''
            <rect width="{w}" height="{h}" fill="{fill}" opacity="0.75" />
            <line x1="0" y1="0" x2="{w}" y2="0" stroke="rgba(255,255,255,0.2)" stroke-width="1" />
            '''

        elif shape_key in ["modern_rounded_capsule", "floating_capsule", "capsule"]:
            # 24. Rounded capsule footer
            r = min(h * 0.44, 46.0)
            pad = min(14.0, w * 0.02)
            return f'''
            <defs>
              <filter id="capsule_glow_{uid}" x="-5%" y="-15%" width="110%" height="140%">
                <feDropShadow dx="0" dy="6" stdDeviation="12" flood-color="#000000" flood-opacity="0.38"/>
              </filter>
            </defs>
            <rect x="{pad}" y="{pad * 0.5}" width="{w - pad * 2}" height="{h - pad}" rx="{r}" ry="{r}" fill="{fill}" opacity="{opacity}" filter="url(#capsule_glow_{uid})" stroke="{sec}" stroke-width="1" />
            '''

        elif shape_key in ["modern_layered_shadow", "double_layer_offset"]:
            # 25. Layered shadow footer
            offset = min(6.0, h * 0.05)
            return f'''
            <rect x="0" y="0" width="{w}" height="{h}" rx="14" fill="{sec}" opacity="0.6" />
            <rect x="{offset}" y="{offset}" width="{w - offset*2}" height="{h - offset*2}" rx="10" fill="{fill}" opacity="{opacity}" />
            '''

        elif shape_key in ["modern_ribbon", "executive_ribbon", "ribbon"]:
            # 26. Ribbon-style footer
            band_h = min(8.0, h * 0.08)
            return f'''
            <rect y="0" width="{w}" height="{band_h}" fill="{accent_color}" />
            <rect y="{band_h}" width="{w}" height="{h - band_h}" fill="{fill}" opacity="{opacity}" />
            '''

        elif shape_key == "modern_folded_corner":
            # 27. Folded corner footer (origami folded corner effect)
            fold = min(28.0, h * 0.25)
            return f'''
            <polygon points="0,0 {w - fold},0 {w},{fold} {w},{h} 0,{h}" fill="{fill}" opacity="{opacity}" />
            <polygon points="{w - fold},0 {w},{fold} {w - fold},{fold}" fill="{accent_color}" opacity="0.9" />
            '''

        elif shape_key in ["modern_asymmetric_split", "split_banner"]:
            # 28. Asymmetric split footer
            w_left = w * p.get("split_ratio", 0.32)
            return f'''
            <rect x="0" y="0" width="{w_left}" height="{h}" fill="{sec}" opacity="{opacity}" />
            <rect x="{w_left}" y="0" width="{w - w_left}" height="{h}" fill="{fill}" opacity="{opacity}" />
            <line x1="{w_left}" y1="0" x2="{w_left}" y2="{h}" stroke="{accent_color}" stroke-width="2.5" />
            '''

        elif shape_key == "modern_gradient_mesh":
            # 29. Gradient mesh footer
            return f'''
            <defs>
              <linearGradient id="mesh_base_{uid}" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stop-color="{fill}" stop-opacity="{opacity}" />
                <stop offset="60%" stop-color="{sec}" stop-opacity="{opacity}" />
                <stop offset="100%" stop-color="{accent_color}" stop-opacity="{max(0.6, opacity * 0.8)}" />
              </linearGradient>
            </defs>
            <rect width="{w}" height="{h}" fill="url(#mesh_base_{uid})" />
            '''

        elif shape_key in ["modern_minimal_accent", "accent_bar_minimal"]:
            # 30. Minimal accent-line footer
            bar_h = 3.5
            return f'''
            <rect y="0" width="{w}" height="{bar_h}" fill="{accent_color}" />
            <rect y="{bar_h}" width="{w}" height="{h - bar_h}" fill="{fill}" opacity="{max(0.8, opacity)}" />
            '''

        # ======================================================================
        # 4. ORIGINAL REMAINING SHAPES (Preserved 100%)
        # ======================================================================
        elif shape_key in ["classic_rectangle", "rectangle"]:
            return f'<rect width="{w}" height="{h}" fill="{fill}" opacity="{opacity}" />'

        elif shape_key in ["rounded_box", "rounded"]:
            r = radius if radius > 0 else min(24.0, h * 0.18, w * 0.05)
            return f'<rect width="{w}" height="{h}" rx="{r}" ry="{r}" fill="{fill}" opacity="{opacity}" />'

        elif shape_key == "diagonal_reverse":
            slope = min(h * 0.25, 42.0)
            return f'''
            <polygon points="0,0 {w},{slope} {w},{h} 0,{h}" fill="{fill}" opacity="{opacity}" />
            <line x1="0" y1="0" x2="{w}" y2="{slope}" stroke="{accent_color}" stroke-width="3" />
            '''

        elif shape_key in ["floating_card", "floating"]:
            r = min(18.0, h * 0.15)
            return f'''
            <defs>
              <filter id="floatCardShadow_{uid}" x="-5%" y="-15%" width="110%" height="140%">
                <feDropShadow dx="0" dy="8" stdDeviation="12" flood-color="#000000" flood-opacity="0.35"/>
              </filter>
            </defs>
            <rect width="{w}" height="{h}" rx="{r}" fill="{fill}" opacity="{opacity}" filter="url(#floatCardShadow_{uid})" />
            '''

        elif shape_key == "center_notch":
            notch_w = min(w * 0.32, 220.0)
            notch_h = min(26.0, h * 0.22)
            nx1 = (w - notch_w) / 2.0
            nx2 = nx1 + notch_w
            return f'''
            <path d="M 0,{notch_h} L {nx1},{notch_h} Q {nx1 + 10},0 {nx1 + 20},0 L {nx2 - 20},0 Q {nx2 - 10},0 {nx2},{notch_h} L {w},{notch_h} L {w},{h} L 0,{h} Z" fill="{fill}" opacity="{opacity}" />
            '''

        # Fallback default
        return f'<rect width="{w}" height="{h}" fill="{fill}" opacity="{opacity}" />'
