import html
from app.models.footer import FooterDesign, FooterElement
from app.design_library.shapes.footer_shapes import FooterShapes
from app.design_library.photo_frames.frames import PhotoFrames
from app.design_library.icons.svg_icons import SVGIcons

class SVGRenderer:
    @classmethod
    def render_svg(cls, footer: FooterDesign) -> str:
        return cls.render_footer_svg(footer)

    @classmethod
    def render_footer_svg(cls, footer: FooterDesign) -> str:
        """
        Renders complete editable SVG string for a FooterDesign.
        """
        w = footer.width
        h = footer.height
        bg = footer.background

        # Generate background shape
        shape_svg = FooterShapes.get_shape_svg(
            shape_name=bg.shape,
            width=w,
            height=h,
            fill=bg.color,
            secondary_fill=bg.secondary_color or bg.color,
            opacity=bg.opacity,
            radius=bg.border_radius
        )

        elements_svg = []
        for el in footer.elements:
            if not el.visible:
                continue
            elements_svg.append(cls._render_element(el))

        svg_content = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" style="overflow:hidden;">
  <g id="footer_background">
    {shape_svg}
  </g>
  <g id="footer_elements">
    {''.join(elements_svg)}
  </g>
</svg>'''
        return svg_content

    @classmethod
    def _render_element(cls, el: FooterElement) -> str:
        st = el.style
        x = el.x
        y = el.y
        w = el.width
        h = el.height

        if el.type == "text":
            escaped_text = html.escape(el.text or "")
            font_family = st.font_family or "Inter, sans-serif"
            font_size = st.font_size or 14
            color = st.color or "#ffffff"
            weight = st.font_weight or "normal"
            align = st.text_align or "left"
            text_anchor = "start" if align == "left" else ("middle" if align == "center" else "end")
            text_x = x if align == "left" else (x + w/2 if align == "center" else x + w)

            return f'''<text id="{el.id}" x="{text_x}" y="{y + font_size * 0.9}" font-family="{font_family}" font-size="{font_size}" font-weight="{weight}" fill="{color}" text-anchor="{text_anchor}">{escaped_text}</text>'''

        elif el.type == "icon_text":
            icon_size = min(h, 18.0)
            icon_color = st.color or "#ffffff"
            icon_svg = SVGIcons.get_icon_svg(el.icon or "info", size=icon_size, color=icon_color)
            escaped_text = html.escape(el.text or "")
            font_family = st.font_family or "Inter, sans-serif"
            font_size = st.font_size or 13
            weight = st.font_weight or "normal"
            color = st.color or "#ffffff"

            return f'''<g id="{el.id}" transform="translate({x}, {y})">
  <g transform="translate(0, {(h - icon_size)/2})">{icon_svg}</g>
  <text x="{icon_size + 8}" y="{icon_size * 0.85 + (h - icon_size)/2}" font-family="{font_family}" font-size="{font_size}" font-weight="{weight}" fill="{color}">{escaped_text}</text>
</g>'''

        elif el.type == "logo":
            img_url = el.image_url or ""
            return f'''<image id="{el.id}" href="{img_url}" x="{x}" y="{y}" width="{w}" height="{h}" preserveAspectRatio="xMidYMid meet" />'''

        elif el.type == "profile":
            frame_style = st.frame_shape or "circle"
            img_url = el.image_url or ""
            border_c = st.border_color or "#ffffff"
            border_w = st.border_width or 2.0
            return PhotoFrames.get_frame_svg(frame_style, x, y, min(w, h), img_url, border_c, border_w)

        elif el.type == "badge" or el.type == "cta":
            bg_c = st.background_color or "#f59e0b"
            text_c = st.color or "#000000"
            radius = st.border_radius or 6.0
            escaped_text = html.escape(el.text or "Contact Us")
            font_size = st.font_size or 13
            return f'''<g id="{el.id}" transform="translate({x}, {y})">
  <rect width="{w}" height="{h}" rx="{radius}" fill="{bg_c}" />
  <text x="{w/2}" y="{h/2 + font_size*0.35}" font-family="{st.font_family or 'Inter'}" font-size="{font_size}" font-weight="700" fill="{text_c}" text-anchor="middle">{escaped_text}</text>
</g>'''

        elif el.type == "qr":
            if el.image_url:
                return f'''<g id="{el.id}" transform="translate({x}, {y})">
  <rect width="{w}" height="{h}" rx="4" fill="#ffffff" />
  <image href="{el.image_url}" x="2" y="2" width="{w - 4}" height="{h - 4}" preserveAspectRatio="xMidYMid meet" />
</g>'''
            else:
                return f'''<g id="{el.id}" transform="translate({x}, {y})">
  <rect width="{w}" height="{h}" rx="4" fill="#ffffff" />
  <g transform="translate(4, 4)">{SVGIcons.get_icon_svg("qr", size=min(w-8, h-8), color="#000000")}</g>
</g>'''

        elif el.type == "divider":
            return f'''<line x1="{x}" y1="{y}" x2="{x}" y2="{y + h}" stroke="{st.color or 'rgba(255,255,255,0.2)'}" stroke-width="{st.border_width or 1.0}" />'''

        return ""
