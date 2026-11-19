import io
import re
import base64
import colorsys
import numpy as np
from PIL import Image
import cv2
from typing import List, Dict, Tuple, Optional, Any
from pydantic import BaseModel, Field

def rgb_to_hex(r: int, g: int, b: int) -> str:
    return f"#{int(np.clip(r, 0, 255)):02x}{int(np.clip(g, 0, 255)):02x}{int(np.clip(b, 0, 255)):02x}"

def hex_to_rgb(hex_str: str) -> Tuple[int, int, int]:
    hex_str = hex_str.lstrip('#')
    if len(hex_str) == 3:
        hex_str = ''.join([c*2 for c in hex_str])
    if len(hex_str) != 6:
        return (0, 0, 0)
    return tuple(int(hex_str[i:i+2], 16) for i in (0, 2, 4))

def get_luminance(rgb: Tuple[int, int, int]) -> float:
    vals = []
    for val in rgb:
        v = val / 255.0
        vals.append(v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4)
    return 0.2126 * vals[0] + 0.7152 * vals[1] + 0.0722 * vals[2]

def calculate_contrast_ratio(rgb1: Tuple[int, int, int], rgb2: Tuple[int, int, int]) -> float:
    lum1 = get_luminance(rgb1)
    lum2 = get_luminance(rgb2)
    lighter = max(lum1, lum2)
    darker = min(lum1, lum2)
    return (lighter + 0.05) / (darker + 0.05)

def get_high_contrast_text_color(bg_hex: str) -> str:
    bg_rgb = hex_to_rgb(bg_hex)
    white_contrast = calculate_contrast_ratio(bg_rgb, (255, 255, 255))
    dark_contrast = calculate_contrast_ratio(bg_rgb, (15, 23, 42))  # slate-900
    return "#ffffff" if white_contrast >= dark_contrast else "#0f172a"

def get_subdued_text_color(bg_hex: str) -> str:
    bg_rgb = hex_to_rgb(bg_hex)
    white_contrast = calculate_contrast_ratio(bg_rgb, (255, 255, 255))
    dark_contrast = calculate_contrast_ratio(bg_rgb, (15, 23, 42))
    return "#cbd5e1" if white_contrast >= dark_contrast else "#475569"

class ColorScheme(BaseModel):
    id: str
    name: str
    description: str
    background: str
    secondary_color: str
    border_color: str
    accent: str
    text_primary: str
    text_secondary: str
    badge_bg: str
    badge_text: str
    is_dark_bg: bool

class LogoPalette(BaseModel):
    primary: str
    secondary: str
    accent: str
    dark_shade: str
    light_shade: str
    dominant_colors: List[Dict[str, Any]] = Field(default_factory=list)
    schemes: List[ColorScheme] = Field(default_factory=list)

class LogoColorExtractor:
    """
    Offline, deterministic brand color analyzer for logos.
    Extracts chromatic and dominant colors using Pillow and K-Means clustering,
    filtering transparent and neutral alpha canvas pixels.
    """

    @staticmethod
    def decode_image_data(image_input: str) -> Optional[Image.Image]:
        """
        Decodes base64 data URI, raw base64 string, or handles SVG data.
        """
        if not image_input:
            return None

        # Check for SVG Data URI or SVG markup
        if "image/svg+xml" in image_input or image_input.strip().startswith("<svg"):
            return None

        # Handle data URI: "data:image/png;base64,..."
        if "base64," in image_input:
            _, encoded = image_input.split("base64,", 1)
        else:
            encoded = image_input

        try:
            image_bytes = base64.b64decode(encoded)
            img = Image.open(io.BytesIO(image_bytes))
            return img.convert("RGBA")
        except Exception:
            return None

    @staticmethod
    def extract_svg_colors(svg_text: str) -> List[str]:
        """
        Extracts hex colors from raw SVG markup (fills, strokes, styles).
        """
        matches = re.findall(r'#(?:[0-9a-fA-F]{3}){1,2}\b', svg_text)
        cleaned = []
        for m in matches:
            m_lower = m.lower()
            if m_lower not in cleaned and m_lower not in ["#fff", "#ffffff", "#000", "#000000", "#none"]:
                cleaned.append(m_lower)
        return cleaned

    def extract_palette(self, image_input: str) -> LogoPalette:
        """
        Main entry point: analyzes logo image input (base64, data URI, or SVG)
        and builds a complete, contrast-compliant LogoPalette.
        """
        # If it's SVG, extract vector colors directly
        if "image/svg+xml" in image_input or image_input.strip().startswith("<svg"):
            svg_content = image_input
            if "base64," in image_input:
                try:
                    svg_content = base64.b64decode(image_input.split("base64,")[1]).decode("utf-8", errors="ignore")
                except Exception:
                    pass
            svg_colors = self.extract_svg_colors(svg_content)
            if svg_colors:
                return self._build_palette_from_hex_list(svg_colors)

        img = self.decode_image_data(image_input)
        if img is None:
            # Fallback default professional tech palette
            return self._build_palette_from_hex_list(["#3b82f6", "#1e40af", "#f59e0b"])

        return self.extract_palette_from_pil(img)

    def extract_palette_from_bytes(self, image_bytes: bytes) -> LogoPalette:
        try:
            img = Image.open(io.BytesIO(image_bytes)).convert("RGBA")
            return self.extract_palette_from_pil(img)
        except Exception:
            return self._build_palette_from_hex_list(["#3b82f6", "#1e40af", "#f59e0b"])

    def extract_palette_from_pil(self, img: Image.Image) -> LogoPalette:
        # Resize for fast clustering
        img_small = img.resize((120, 120), Image.Resampling.BOX)
        np_img = np.array(img_small)

        # Filter out transparent pixels (alpha < 30)
        alpha = np_img[:, :, 3]
        visible_mask = alpha > 30

        if not np.any(visible_mask):
            return self._build_palette_from_hex_list(["#3b82f6", "#1e40af", "#f59e0b"])

        rgb_pixels = np_img[:, :, :3][visible_mask]

        # Further filter out pure white/black background canvases if chromatic pixels exist
        hsv_pixels = [colorsys.rgb_to_hsv(r/255.0, g/255.0, b/255.0) for r, g, b in rgb_pixels]
        # chromatic: saturation > 0.15 and 0.1 < value < 0.95
        chromatic_indices = [
            i for i, (h, s, v) in enumerate(hsv_pixels)
            if s > 0.15 and 0.08 < v < 0.98
        ]

        # If we have chromatic brand pixels, cluster primarily on them
        if len(chromatic_indices) > 50:
            target_pixels = rgb_pixels[chromatic_indices].astype(np.float32)
        else:
            target_pixels = rgb_pixels.astype(np.float32)

        k = min(5, len(target_pixels))
        if k < 2:
            single_rgb = rgb_pixels[0]
            hex_val = rgb_to_hex(single_rgb[0], single_rgb[1], single_rgb[2])
            return self._build_palette_from_hex_list([hex_val])

        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 25, 0.2)
        flags = cv2.KMEANS_RANDOM_CENTERS
        _, labels, centers = cv2.kmeans(target_pixels, k, None, criteria, 10, flags)

        counts = np.bincount(labels.flatten())
        total = len(labels)

        sorted_indices = np.argsort(-counts)
        clustered_colors: List[Dict[str, Any]] = []

        for idx in sorted_indices:
            r, g, b = [int(np.clip(c, 0, 255)) for c in centers[idx]]
            hex_c = rgb_to_hex(r, g, b)
            h, s, v = colorsys.rgb_to_hsv(r/255.0, g/255.0, b/255.0)
            clustered_colors.append({
                "hex": hex_c,
                "rgb": [r, g, b],
                "percentage": round(float(counts[idx] / total) * 100, 1),
                "saturation": s,
                "value": v,
            })

        hex_candidates = [c["hex"] for c in clustered_colors]
        return self._build_palette_from_hex_list(hex_candidates, clustered_colors)

    def _build_palette_from_hex_list(
        self,
        hex_list: List[str],
        cluster_info: Optional[List[Dict[str, Any]]] = None
    ) -> LogoPalette:
        if not hex_list:
            hex_list = ["#3b82f6"]

        primary = hex_list[0]
        # Choose secondary as distinct from primary
        p_rgb = hex_to_rgb(primary)
        secondary = None
        for candidate in hex_list[1:]:
            c_rgb = hex_to_rgb(candidate)
            dist = np.linalg.norm(np.array(p_rgb) - np.array(c_rgb))
            if dist > 45:
                secondary = candidate
                break

        if not secondary:
            # Generate harmonious analogous/complementary secondary
            p_h, p_s, p_v = colorsys.rgb_to_hsv(p_rgb[0]/255.0, p_rgb[1]/255.0, p_rgb[2]/255.0)
            sec_h = (p_h + 0.08) % 1.0  # slight analogous hue shift
            sec_rgb = colorsys.hsv_to_rgb(sec_h, max(0.4, p_s), min(0.9, max(0.3, p_v)))
            secondary = rgb_to_hex(int(sec_rgb[0]*255), int(sec_rgb[1]*255), int(sec_rgb[2]*255))

        # Accent color (high saturation contrast or triadic)
        s_rgb = hex_to_rgb(secondary)
        accent = None
        for candidate in hex_list:
            if candidate not in [primary, secondary]:
                c_rgb = hex_to_rgb(candidate)
                if np.linalg.norm(np.array(p_rgb) - np.array(c_rgb)) > 60:
                    accent = candidate
                    break

        if not accent:
            # Triadic / complementary accent
            p_h, p_s, p_v = colorsys.rgb_to_hsv(p_rgb[0]/255.0, p_rgb[1]/255.0, p_rgb[2]/255.0)
            acc_h = (p_h + 0.5) % 1.0  # Complementary
            acc_rgb = colorsys.hsv_to_rgb(acc_h, max(0.7, p_s), 0.95)
            accent = rgb_to_hex(int(acc_rgb[0]*255), int(acc_rgb[1]*255), int(acc_rgb[2]*255))

        # Build deep dark shade tinted with primary
        p_h, p_s, _ = colorsys.rgb_to_hsv(p_rgb[0]/255.0, p_rgb[1]/255.0, p_rgb[2]/255.0)
        dark_rgb = colorsys.hsv_to_rgb(p_h, min(0.45, max(0.15, p_s * 0.5)), 0.11)
        dark_shade = rgb_to_hex(int(dark_rgb[0]*255), int(dark_rgb[1]*255), int(dark_rgb[2]*255))

        # Build soft light shade tinted with primary
        light_rgb = colorsys.hsv_to_rgb(p_h, min(0.06, p_s * 0.1), 0.98)
        light_shade = rgb_to_hex(int(light_rgb[0]*255), int(light_rgb[1]*255), int(light_rgb[2]*255))

        # Construct 5 distinct professional color schemes
        schemes = self._generate_color_schemes(primary, secondary, accent, dark_shade, light_shade)

        return LogoPalette(
            primary=primary,
            secondary=secondary,
            accent=accent,
            dark_shade=dark_shade,
            light_shade=light_shade,
            dominant_colors=cluster_info or [{"hex": h, "percentage": 100 // len(hex_list)} for h in hex_list],
            schemes=schemes,
        )

    def _generate_color_schemes(
        self,
        primary: str,
        secondary: str,
        accent: str,
        dark_shade: str,
        light_shade: str
    ) -> List[ColorScheme]:
        schemes = []

        # 1. Bold Brand (Primary dominant)
        text_p1 = get_high_contrast_text_color(primary)
        text_s1 = get_subdued_text_color(primary)
        schemes.append(ColorScheme(
            id="bold_brand",
            name="Bold Brand",
            description="Vibrant primary brand background with high-contrast typography and accent badges.",
            background=primary,
            secondary_color=secondary,
            border_color=accent,
            accent=accent,
            text_primary=text_p1,
            text_secondary=text_s1,
            badge_bg=accent,
            badge_text=get_high_contrast_text_color(accent),
            is_dark_bg=get_luminance(hex_to_rgb(primary)) < 0.5,
        ))

        # 2. Dark Luxury (Deep tinted charcoal/navy with brand highlights)
        schemes.append(ColorScheme(
            id="dark_luxury",
            name="Dark Luxury",
            description="Deep rich dark surface tinted with brand tone, crisp white text, and glowing brand accents.",
            background=dark_shade,
            secondary_color=primary,
            border_color=primary,
            accent=accent,
            text_primary="#ffffff",
            text_secondary="#cbd5e1",
            badge_bg=primary,
            badge_text=get_high_contrast_text_color(primary),
            is_dark_bg=True,
        ))

        # 3. Clean Light / Minimalist
        schemes.append(ColorScheme(
            id="clean_light",
            name="Clean Light",
            description="Pristine light background with dark brand typography, clean borders, and vibrant icons.",
            background=light_shade,
            secondary_color="#ffffff",
            border_color=secondary,
            accent=primary,
            text_primary=dark_shade,
            text_secondary="#475569",
            badge_bg=primary,
            badge_text=get_high_contrast_text_color(primary),
            is_dark_bg=False,
        ))

        # 4. Gradient Duo
        schemes.append(ColorScheme(
            id="gradient_duo",
            name="Gradient Duo",
            description="Harmonious linear gradient between primary and secondary brand colors.",
            background=primary,
            secondary_color=secondary,
            border_color=accent,
            accent=accent,
            text_primary="#ffffff",
            text_secondary="#f1f5f9",
            badge_bg=accent,
            badge_text=get_high_contrast_text_color(accent),
            is_dark_bg=True,
        ))

        # 5. Accent Pop
        schemes.append(ColorScheme(
            id="accent_pop",
            name="Accent Pop",
            description="Contrast-heavy dark background with glowing accent focal points and badges.",
            background=dark_shade,
            secondary_color=accent,
            border_color=accent,
            accent=accent,
            text_primary="#ffffff",
            text_secondary="#94a3b8",
            badge_bg=accent,
            badge_text=get_high_contrast_text_color(accent),
            is_dark_bg=True,
        ))

        return schemes

logo_color_extractor = LogoColorExtractor()
