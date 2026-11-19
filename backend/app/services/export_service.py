import io
import base64
from PIL import Image
from typing import Dict, Any, Optional
from app.models.footer import FooterDesign
from app.renderer.footer_renderer import FooterRenderer
from app.renderer.svg_renderer import SVGRenderer

class ExportService:
    @classmethod
    def export_poster(
        cls,
        poster_data_url: Optional[str],
        footer: FooterDesign,
        export_format: str = "png",
        poster_w: int = 1080,
        poster_h: int = 1080
    ) -> io.BytesIO:
        export_format = export_format.lower()
        
        # 1. Base canvas image
        if poster_data_url and "base64," in poster_data_url:
            raw_b64 = poster_data_url.split("base64,")[1]
            img_bytes = base64.b64decode(raw_b64)
            base_img = Image.open(io.BytesIO(img_bytes)).convert("RGBA")
            poster_w, poster_h = base_img.size
        else:
            # Create a neutral canvas if no poster was provided
            base_img = Image.new("RGBA", (int(poster_w), int(poster_h)), (30, 41, 59, 255))

        # 2. Composite footer onto base image
        footer_img = FooterRenderer.render_footer_layer(footer)
        paste_x = max(0, min(poster_w - 1, int(footer.x)))
        paste_y = max(0, min(poster_h - 1, int(footer.y)))
        base_img.paste(footer_img, (paste_x, paste_y), footer_img)

        output = io.BytesIO()

        if export_format in ["jpg", "jpeg"]:
            rgb_img = base_img.convert("RGB")
            rgb_img.save(output, format="JPEG", quality=95)
        elif export_format == "pdf":
            rgb_img = base_img.convert("RGB")
            rgb_img.save(output, format="PDF", resolution=150.0)
        else:  # PNG default
            base_img.save(output, format="PNG")

        output.seek(0)
        return output

    @classmethod
    def export_svg(
        cls,
        poster_data_url: Optional[str],
        footer: FooterDesign,
        poster_w: int = 1080,
        poster_h: int = 1080
    ) -> str:
        """
        Creates a high resolution standalone SVG of the whole poster with editable vector layers.
        Regenerates dynamic SVG markup to guarantee accuracy.
        """
        poster_href = poster_data_url or ""
        # Re-render fresh SVG markup
        footer_svg_content = SVGRenderer.render_footer_svg(footer)
        
        return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{poster_w}" height="{poster_h}" viewBox="0 0 {poster_w} {poster_h}">
  <!-- Poster Base -->
  <image href="{poster_href}" width="{poster_w}" height="{poster_h}" preserveAspectRatio="xMidYMid slice" />
  <!-- Footer Vector Layer -->
  <g id="footer_group" transform="translate({footer.x}, {footer.y})">
    {footer_svg_content}
  </g>
</svg>'''
