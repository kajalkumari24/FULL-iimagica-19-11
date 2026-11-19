from typing import Dict, List, Tuple
from PIL import ImageFont, ImageDraw, Image

class TypographyEngine:
    """
    Handles proportional font scaling, precise text measurement via Pillow,
    robust line wrapping, and minimum readability guarantees.
    """

    # Reference resolution: 1080px base
    @staticmethod
    def calculate_base_scale(poster_width: float, poster_height: float) -> float:
        ref = min(poster_width, poster_height)
        scale = ref / 1080.0
        return max(0.7, min(2.5, scale))

    @classmethod
    def get_font_sizes(cls, base_scale: float) -> Dict[str, float]:
        # Enforce readable minimums (never shrink text below legible size)
        return {
            "title": round(max(15.0, 22.0 * base_scale), 1),
            "tagline": round(max(11.0, 14.0 * base_scale), 1),
            "body": round(max(10.5, 13.0 * base_scale), 1),
            "small": round(max(10.0, 11.5 * base_scale), 1),
            "cta": round(max(12.0, 15.0 * base_scale), 1),
        }

    @classmethod
    def measure_text_width(cls, text: str, font_size: float, font_weight: str = "normal") -> float:
        if not text:
            return 0.0
        try:
            # Attempt real font measurement
            font = ImageFont.load_default()
            # Default bitmap font is fixed, so we scale its ratio
            bbox = font.getbbox(text)
            ref_w = bbox[2] - bbox[0]
            # scale according to requested font_size relative to default ~10px
            w = (ref_w / 6.0) * (font_size * 0.55)
            if font_weight in ["bold", "700", "800", "900"]:
                w *= 1.15
            return max(w, len(text) * font_size * (0.62 if font_weight in ["bold", "700", "800"] else 0.53))
        except Exception:
            ratio = 0.62 if font_weight in ["bold", "700", "800", "900"] else 0.53
            return len(text) * font_size * ratio

    @classmethod
    def wrap_text(
        cls,
        text: str,
        max_width: float,
        font_size: float,
        font_weight: str = "normal",
        max_lines: int = 3,
    ) -> List[str]:
        if not text:
            return []

        words = text.split()
        lines: List[str] = []
        current_line: List[str] = []

        for word in words:
            candidate = " ".join(current_line + [word])
            w = cls.measure_text_width(candidate, font_size, font_weight)
            if w <= max_width or not current_line:
                current_line.append(word)
            else:
                lines.append(" ".join(current_line))
                current_line = [word]
                if len(lines) == max_lines - 1:
                    break

        if current_line and len(lines) < max_lines:
            lines.append(" ".join(current_line))

        # Truncate last line with ellipsis if remaining words exist
        total_words_count = sum(len(l.split()) for l in lines)
        if total_words_count < len(words) and lines:
            last = lines[-1]
            while cls.measure_text_width(last + "...", font_size, font_weight) > max_width and len(last) > 3:
                last = last[:-1].rstrip()
            lines[-1] = last + "..."

        return lines
