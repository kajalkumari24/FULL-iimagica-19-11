"""
Pillow-based high-resolution raster renderer.

Composites the footer design onto a poster image for PNG / JPG / PDF export.
Delegates final file encoding to ExportService.
"""

import io
import base64
from PIL import Image, ImageDraw, ImageFont
from typing import Optional

from app.models.footer import FooterDesign
from app.analyzer.color_analyzer import hex_to_rgb
from app.renderer.svg_renderer import SVGRenderer


class FooterRenderer:
    """Renders a FooterDesign as a Pillow RGBA layer and composites it onto a poster."""

    @classmethod
    def render_to_bytes(
        cls,
        poster_data_url: Optional[str],
        footer: FooterDesign,
        export_format: str = "png",
        poster_w: int = 1080,
        poster_h: int = 1080,
    ) -> io.BytesIO:
        from app.services.export_service import ExportService
        return ExportService.export_poster(
            poster_data_url=poster_data_url,
            footer=footer,
            export_format=export_format,
            poster_w=poster_w,
            poster_h=poster_h,
        )

    # ------------------------------------------------------------------
    # Standalone footer layer (useful for previews / composites)
    # ------------------------------------------------------------------
    @classmethod
    def render_footer_layer(cls, footer: FooterDesign) -> Image.Image:
        """Return an RGBA Image of the footer without the poster background."""
        fw = max(10, int(footer.width))
        fh = max(10, int(footer.height))
        layer = Image.new("RGBA", (fw, fh), (0, 0, 0, 0))
        draw = ImageDraw.Draw(layer)

        # --- background shape ---
        bg = footer.background
        bg_rgb = hex_to_rgb(bg.color or "#0f172a")
        alpha = int(max(0.0, min(1.0, bg.opacity)) * 255)
        fill = (bg_rgb[0], bg_rgb[1], bg_rgb[2], alpha)

        shape = (bg.shape or "rectangle").lower()
        if any(k in shape for k in ["rounded", "floating", "capsule", "glass", "card"]):
            r = int(min(24, fh * 0.2))
            draw.rounded_rectangle([(0, 0), (fw, fh)], radius=r, fill=fill)
        elif "wave" in shape:
            amp = int(min(fh * 0.22, 32))
            pts = [
                (0, amp),
                (fw // 4, 0),
                (fw // 2, amp // 2),
                (3 * fw // 4, 0),
                (fw, amp // 3),
                (fw, fh),
                (0, fh),
            ]
            draw.polygon(pts, fill=fill)
        elif any(k in shape for k in ["convex", "concave", "arch", "circle", "crest"]):
            amp = int(min(fh * 0.2, 28))
            pts = [(0, amp), (fw // 2, 0), (fw, amp), (fw, fh), (0, fh)]
            draw.polygon(pts, fill=fill)
        elif any(k in shape for k in ["diagonal", "bevel", "angle", "slanted"]):
            slope = int(min(fh * 0.22, 35))
            pts = [(0, slope), (fw, 0), (fw, fh), (0, fh)]
            draw.polygon(pts, fill=fill)
        elif "zigzag" in shape:
            saw_w = max(10, fw // 8)
            pts = [(0, 10)]
            for i in range(8):
                pts.append(((i * 2 + 1) * saw_w // 2, 0))
                pts.append(((i + 1) * saw_w, 10))
            pts.extend([(fw, fh), (0, fh)])
            draw.polygon(pts, fill=fill)
        elif any(k in shape for k in ["polygon", "folded"]):
            pts = [(0, 14), (fw // 5, 0), (fw, 14), (fw, fh), (0, fh)]
            draw.polygon(pts, fill=fill)
        else:
            draw.rectangle([(0, 0), (fw, fh)], fill=fill)

        # --- elements ---
        for el in footer.elements:
            if not el.visible:
                continue
            cls._draw_element(layer, draw, el)

        return layer

    # ------------------------------------------------------------------
    # Element drawing helpers
    # ------------------------------------------------------------------
    @classmethod
    def _draw_element(cls, layer: Image.Image, draw: ImageDraw.Draw, el):
        ex, ey = int(el.x), int(el.y)
        ew, eh = max(1, int(el.width)), max(1, int(el.height))

        if el.type in ("text", "icon_text"):
            txt = el.text or ""
            color_rgb = hex_to_rgb(el.style.color or "#ffffff")
            fsize = int(el.style.font_size or 14)
            try:
                # Pillow default font
                font = ImageFont.load_default()
            except Exception:
                font = None
            text_x = ex + (22 if el.type == "icon_text" else 0)
            draw.text(
                (text_x, ey + 2),
                txt,
                fill=(color_rgb[0], color_rgb[1], color_rgb[2], 255),
                font=font,
            )

        elif el.type in ("logo", "profile", "qr"):
            if el.image_url and "base64," in el.image_url:
                try:
                    raw = el.image_url.split("base64,")[1]
                    img = Image.open(io.BytesIO(base64.b64decode(raw))).convert("RGBA")
                    # Preserve aspect ratio
                    orig_w, orig_h = img.size
                    ratio = min(ew / max(1, orig_w), eh / max(1, orig_h))
                    new_w = max(1, int(orig_w * ratio))
                    new_h = max(1, int(orig_h * ratio))
                    img = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
                    offset_x = ex + (ew - new_w) // 2
                    offset_y = ey + (eh - new_h) // 2

                    if el.type == "profile":
                        # Circular mask for profile photo
                        mask = Image.new("L", (new_w, new_h), 0)
                        m_draw = ImageDraw.Draw(mask)
                        m_draw.ellipse((0, 0, new_w, new_h), fill=255)
                        layer.paste(img, (offset_x, offset_y), mask)
                    elif el.type == "qr":
                        # White rounded backplate for scannable QR
                        draw.rounded_rectangle([(ex, ey), (ex + ew, ey + eh)], radius=4, fill=(255, 255, 255, 255))
                        layer.paste(img, (offset_x, offset_y), img)
                    else:
                        layer.paste(img, (offset_x, offset_y), img)
                except Exception:
                    pass

        elif el.type in ("badge", "cta"):
            b_color = hex_to_rgb(el.style.background_color or "#f59e0b")
            draw.rounded_rectangle(
                [(ex, ey), (ex + ew, ey + eh)],
                radius=int(el.style.border_radius or 6),
                fill=(b_color[0], b_color[1], b_color[2], 255),
            )
            txt_c = hex_to_rgb(el.style.color or "#000000")
            draw.text(
                (ex + 12, ey + eh // 3),
                el.text or "CTA",
                fill=(txt_c[0], txt_c[1], txt_c[2], 255),
            )

        elif el.type == "divider":
            c = hex_to_rgb(el.style.color or "#ffffff")
            draw.line([(ex, ey), (ex, ey + eh)], fill=(c[0], c[1], c[2], 120), width=1)
