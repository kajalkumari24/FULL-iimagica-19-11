import math
from typing import List, Dict, Any, Optional, Tuple
from app.models.brand import BrandProfile, LogoItem, ProfileItem, CustomField
from app.models.footer import FooterElement, ElementStyle
from app.engine.size_calculator import SizeCalculator
from app.engine.typography_engine import TypographyEngine
from app.services.qr_service import QRService

class ArrangementEngine:
    """
    Arrangement Engine formulating 20 distinct, responsive content layouts for footers.
    Each layout algorithm strictly calculates element coordinates, typography scale,
    margins, and boundaries to prevent element collisions and overflows.
    """

    ARRANGEMENTS = [
        "classic_horizontal",
        "vertical_stacked",
        "two_column",
        "three_column",
        "four_column",
        "centred",
        "left_aligned_stack",
        "right_aligned_stack",
        "logo_centre",
        "profile_focused",
        "profile_circle",
        "logo_top",
        "contact_card",
        "social_bottom",
        "qr_focused",
        "split_panel",
        "vertical_sidebar",
        "floating_elements",
        "asymmetric",
        "compact",
    ]

    @classmethod
    def apply_arrangement(
        cls,
        arrangement_name: str,
        fw: float,
        fh: float,
        pad_x: float,
        pad_y: float,
        top_offset: float,
        brand: BrandProfile,
        font_sizes: Dict[str, float],
        font_scale: float,
        colors: Dict[str, str],
        default_font: str = "Inter",
        default_frame: str = "circle",
        shape_key: str = "classic_rectangle",
    ) -> List[FooterElement]:
        """
        Dispatches to one of the 20 distinct content arrangement algorithms.
        """
        arr = (arrangement_name or "classic_horizontal").lower()
        method_name = f"_arrange_{arr}"
        handler = getattr(cls, method_name, cls._arrange_classic_horizontal)
        return handler(
            fw=fw,
            fh=fh,
            pad_x=pad_x,
            pad_y=pad_y,
            top_offset=top_offset,
            brand=brand,
            font_sizes=font_sizes,
            font_scale=font_scale,
            colors=colors,
            default_font=default_font,
            default_frame=default_frame,
            shape_key=shape_key,
        )

    # --------------------------------------------------------------------------
    # Helper utilities
    # --------------------------------------------------------------------------
    @staticmethod
    def _extract_contacts(brand: BrandProfile) -> List[Tuple[str, str]]:
        contacts = []
        if brand.phone and brand.phone.strip():
            contacts.append(("phone", brand.phone.strip()))
        if brand.whatsapp and brand.whatsapp.strip():
            contacts.append(("whatsapp", brand.whatsapp.strip()))
        if brand.email and brand.email.strip():
            contacts.append(("email", brand.email.strip()))
        if brand.website and brand.website.strip():
            contacts.append(("website", brand.website.strip()))
        return contacts

    @staticmethod
    def _extract_socials(brand: BrandProfile) -> List[Tuple[str, str]]:
        socials = []
        for p, h in (brand.social_handles or {}).items():
            if h and h.strip():
                socials.append((p, h.strip()))
        return socials

    # ==========================================================================
    # 1. Classic Horizontal: Logo Left, Brand Details Centre, Contacts Right
    # ==========================================================================
    @classmethod
    def _arrange_classic_horizontal(cls, fw, fh, pad_x, pad_y, top_offset, brand, font_sizes, font_scale, colors, default_font, default_frame, shape_key):
        elements: List[FooterElement] = []
        usable_w = fw - (pad_x * 2)
        usable_h = fh - (pad_y * 2) - top_offset
        y_top = pad_y + top_offset

        col1_w = usable_w * 0.28
        col2_w = usable_w * 0.38
        col3_w = usable_w * 0.30
        gap = usable_w * 0.02

        col1_x = pad_x
        col2_x = col1_x + col1_w + gap
        col3_x = col2_x + col2_w + gap

        # Col 1: Logo & Profile
        y_c1 = y_top
        if brand.profiles:
            psize = min(usable_h * 0.45, 50.0 * font_scale)
            for p_idx, prof in enumerate(brand.profiles[:2]):
                elements.append(FooterElement(
                    id=f"prof_{p_idx+1}", type="profile", image_url=prof.url,
                    x=col1_x + (p_idx * (psize + 6.0)), y=y_c1, width=psize, height=psize,
                    style=ElementStyle(frame_shape=default_frame, border_color=colors["acc_col"], border_width=2.0)
                ))
            y_c1 += psize + 6.0

        if brand.logos:
            logo_max_w = min(col1_w * 0.48, 90.0 * font_scale) if len(brand.logos) > 1 else col1_w
            logo_max_h = min(usable_h * 0.38, 45.0 * font_scale)
            l_x = col1_x
            for l_idx, logo in enumerate(brand.logos[:2]):
                lw, lh = SizeCalculator.calculate_logo_size(logo, logo_max_w, logo_max_h)
                elements.append(FooterElement(
                    id=f"logo_{l_idx+1}", type="logo", image_url=logo.url,
                    x=l_x, y=y_c1, width=lw, height=lh
                ))
                l_x += lw + 6.0

        # Col 2: Brand Details (Title, Tagline, CTA)
        y_c2 = y_top
        if brand.brand_name.strip():
            lines = TypographyEngine.wrap_text(brand.brand_name, col2_w, font_sizes["title"], "bold", max_lines=2)
            lh_t = font_sizes["title"] * 1.22
            for line in lines:
                elements.append(FooterElement(
                    id=f"bname_{len(elements)}", type="text", text=line,
                    x=col2_x, y=y_c2, width=col2_w, height=lh_t,
                    style=ElementStyle(font_family=default_font, font_size=font_sizes["title"], font_weight="800", color=colors["text_primary"])
                ))
                y_c2 += lh_t + 2.0

        if brand.tagline and brand.tagline.strip():
            lines = TypographyEngine.wrap_text(brand.tagline, col2_w, font_sizes["tagline"], "normal", max_lines=2)
            lh_tag = font_sizes["tagline"] * 1.2
            for line in lines:
                elements.append(FooterElement(
                    id=f"tag_{len(elements)}", type="text", text=line,
                    x=col2_x, y=y_c2, width=col2_w, height=lh_tag,
                    style=ElementStyle(font_family=default_font, font_size=font_sizes["tagline"], font_weight="500", color=colors["acc_col"])
                ))
                y_c2 += lh_tag + 2.0

        if brand.cta and brand.cta.strip():
            btn_h = min(28.0 * font_scale, max(24.0, usable_h * 0.22))
            btn_w = min(col2_w * 0.85, 160.0 * font_scale)
            elements.append(FooterElement(
                id="cta_1", type="badge", text=brand.cta,
                x=col2_x, y=min(fh - pad_y - btn_h, y_c2 + 4.0), width=btn_w, height=btn_h,
                style=ElementStyle(background_color=colors["acc_col"], color="#ffffff", font_size=font_sizes["cta"], border_radius=4.0)
            ))

        # Col 3: Contacts & QR
        contacts = cls._extract_contacts(brand)
        qr_sz = min(usable_h * 0.70, 56.0 * font_scale) if brand.qr_code_content else 0.0
        c3_text_w = col3_w - (qr_sz + 8.0 if qr_sz > 0 else 0.0)

        y_c3 = y_top
        line_h = min(18.0 * font_scale, max(12.0, usable_h / max(1, len(contacts) + 1)))
        f_sz = max(9.0, min(font_sizes["body"], line_h * 0.72))

        for icon, val in contacts[:4]:
            if y_c3 + line_h > fh - pad_y:
                break
            elements.append(FooterElement(
                id=f"cnt_{len(elements)}", type="icon_text", icon=icon, text=val,
                x=col3_x, y=y_c3, width=c3_text_w, height=line_h,
                style=ElementStyle(font_family="Inter", font_size=f_sz, font_weight="500", color=colors["text_primary"])
            ))
            y_c3 += line_h + 2.0

        if qr_sz > 0:
            qr_url = QRService.generate_qr_data_url(brand.qr_code_content)
            elements.append(FooterElement(
                id="qr_1", type="qr", image_url=qr_url,
                x=col3_x + col3_w - qr_sz, y=y_top, width=qr_sz, height=qr_sz
            ))

        return elements

    # ==========================================================================
    # 2. Vertical Stacked: Logo at top, Brand Name below, Contacts underneath
    # ==========================================================================
    @classmethod
    def _arrange_vertical_stacked(cls, fw, fh, pad_x, pad_y, top_offset, brand, font_sizes, font_scale, colors, default_font, default_frame, shape_key):
        elements: List[FooterElement] = []
        usable_w = fw - (pad_x * 2)
        usable_h = fh - (pad_y * 2) - top_offset
        y_curr = pad_y + top_offset

        # Tier 1: Logo & Profile Centered or Top Left
        tier1_h = usable_h * 0.32
        x_start = pad_x
        if brand.logos:
            lw, lh = SizeCalculator.calculate_logo_size(brand.logos[0], usable_w * 0.35, tier1_h)
            elements.append(FooterElement(
                id="logo_1", type="logo", image_url=brand.logos[0].url,
                x=x_start, y=y_curr, width=lw, height=lh
            ))
            x_start += lw + 12.0

        if brand.profiles:
            psize = min(tier1_h, 45.0 * font_scale)
            elements.append(FooterElement(
                id="prof_1", type="profile", image_url=brand.profiles[0].url,
                x=x_start, y=y_curr, width=psize, height=psize,
                style=ElementStyle(frame_shape=default_frame, border_color=colors["acc_col"], border_width=2.0)
            ))

        y_curr += tier1_h + 4.0

        # Tier 2: Brand Name & Tagline
        if brand.brand_name.strip():
            th = font_sizes["title"] * 1.2
            elements.append(FooterElement(
                id="bname_1", type="text", text=brand.brand_name,
                x=pad_x, y=y_curr, width=usable_w * 0.70, height=th,
                style=ElementStyle(font_family=default_font, font_size=font_sizes["title"], font_weight="800", color=colors["text_primary"])
            ))
            y_curr += th + 2.0

        if brand.tagline and brand.tagline.strip():
            tag_h = font_sizes["tagline"] * 1.2
            elements.append(FooterElement(
                id="tag_1", type="text", text=brand.tagline,
                x=pad_x, y=y_curr, width=usable_w * 0.70, height=tag_h,
                style=ElementStyle(font_family=default_font, font_size=font_sizes["tagline"], font_weight="500", color=colors["acc_col"])
            ))
            y_curr += tag_h + 4.0

        # Tier 3: Contact Items in a Horizontal Strip
        contacts = cls._extract_contacts(brand)
        if contacts:
            cnt_w = usable_w / len(contacts)
            lh = min(16.0 * font_scale, max(11.0, (fh - pad_y - y_curr)))
            fsz = max(8.5, min(font_sizes["body"], lh * 0.75))
            for i, (icon, val) in enumerate(contacts):
                elements.append(FooterElement(
                    id=f"cnt_{i+1}", type="icon_text", icon=icon, text=val,
                    x=pad_x + (i * cnt_w), y=y_curr, width=cnt_w - 6.0, height=lh,
                    style=ElementStyle(font_family="Inter", font_size=fsz, color=colors["text_secondary"])
                ))

        # QR Code bottom right
        if brand.qr_code_content:
            qr_sz = min(usable_h * 0.65, 54.0 * font_scale)
            qr_url = QRService.generate_qr_data_url(brand.qr_code_content)
            elements.append(FooterElement(
                id="qr_1", type="qr", image_url=qr_url,
                x=fw - pad_x - qr_sz, y=pad_y + top_offset, width=qr_sz, height=qr_sz
            ))

        return elements

    # ==========================================================================
    # 3. Two-Column: Branding on Left, Contact Information on Right
    # ==========================================================================
    @classmethod
    def _arrange_two_column(cls, fw, fh, pad_x, pad_y, top_offset, brand, font_sizes, font_scale, colors, default_font, default_frame, shape_key):
        elements: List[FooterElement] = []
        usable_w = fw - (pad_x * 2)
        usable_h = fh - (pad_y * 2) - top_offset
        y_top = pad_y + top_offset

        col_w = (usable_w - (16.0 * font_scale)) / 2.0
        col1_x = pad_x
        col2_x = pad_x + col_w + (16.0 * font_scale)

        # Left Column: Branding
        y_l = y_top
        if brand.profiles:
            psize = min(usable_h * 0.40, 48.0 * font_scale)
            for p_idx, prof in enumerate(brand.profiles[:2]):
                elements.append(FooterElement(
                    id=f"prof_{p_idx+1}", type="profile", image_url=prof.url,
                    x=col1_x + (p_idx * (psize + 6.0)), y=y_l, width=psize, height=psize,
                    style=ElementStyle(frame_shape=default_frame, border_color=colors["acc_col"], border_width=2.0)
                ))
            y_l += psize + 4.0

        if brand.logos:
            logo_max_w = min(col_w * 0.46, 100.0 * font_scale) if len(brand.logos) > 1 else col_w * 0.70
            logo_max_h = min(usable_h * 0.35, 45.0 * font_scale)
            l_x = col1_x
            max_lh = 0.0
            for l_idx, logo in enumerate(brand.logos[:2]):
                lw, lh = SizeCalculator.calculate_logo_size(logo, logo_max_w, logo_max_h)
                elements.append(FooterElement(
                    id=f"logo_{l_idx+1}", type="logo", image_url=logo.url,
                    x=l_x, y=y_l, width=lw, height=lh
                ))
                l_x += lw + 6.0
                max_lh = max(max_lh, lh)
            y_l += max_lh + 4.0

        if brand.brand_name.strip():
            th = font_sizes["title"] * 1.25
            elements.append(FooterElement(
                id="bname_1", type="text", text=brand.brand_name,
                x=col1_x, y=y_l, width=col_w, height=th,
                style=ElementStyle(font_family=default_font, font_size=font_sizes["title"], font_weight="800", color=colors["text_primary"])
            ))
            y_l += th + 2.0

        if brand.tagline and brand.tagline.strip():
            tag_h = font_sizes["tagline"] * 1.2
            elements.append(FooterElement(
                id="tag_1", type="text", text=brand.tagline,
                x=col1_x, y=y_l, width=col_w, height=tag_h,
                style=ElementStyle(font_family=default_font, font_size=font_sizes["tagline"], font_weight="500", color=colors["acc_col"])
            ))
            y_l += tag_h + 4.0

        if brand.cta and brand.cta.strip():
            btn_h = min(28.0 * font_scale, 24.0)
            btn_w = min(col_w * 0.75, 150.0 * font_scale)
            elements.append(FooterElement(
                id="cta_1", type="badge", text=brand.cta,
                x=col1_x, y=min(fh - pad_y - btn_h, y_l + 4.0), width=btn_w, height=btn_h,
                style=ElementStyle(background_color=colors["acc_col"], color="#ffffff", font_size=font_sizes["cta"], border_radius=4.0)
            ))

        # Right Column: Contacts + QR
        contacts = cls._extract_contacts(brand)
        qr_sz = min(usable_h * 0.65, 52.0 * font_scale) if brand.qr_code_content else 0.0
        text_w = col_w - (qr_sz + 8.0 if qr_sz > 0 else 0.0)

        y_r = y_top
        line_h = min(18.0 * font_scale, max(12.0, usable_h / max(1, len(contacts))))
        fsz = max(9.0, min(font_sizes["body"], line_h * 0.72))

        for icon, val in contacts:
            if y_r + line_h > fh - pad_y:
                break
            elements.append(FooterElement(
                id=f"cnt_{len(elements)}", type="icon_text", icon=icon, text=val,
                x=col2_x, y=y_r, width=text_w, height=line_h,
                style=ElementStyle(font_family="Inter", font_size=fsz, font_weight="600", color=colors["text_primary"])
            ))
            y_r += line_h + 2.0

        if qr_sz > 0:
            qr_url = QRService.generate_qr_data_url(brand.qr_code_content)
            elements.append(FooterElement(
                id="qr_1", type="qr", image_url=qr_url,
                x=col2_x + col_w - qr_sz, y=y_top, width=qr_sz, height=qr_sz
            ))

        return elements

    # ==========================================================================
    # 4. Three-Column: Logo & Brand, Contact Details, Social Links
    # ==========================================================================
    @classmethod
    def _arrange_three_column(cls, fw, fh, pad_x, pad_y, top_offset, brand, font_sizes, font_scale, colors, default_font, default_frame, shape_key):
        elements: List[FooterElement] = []
        usable_w = fw - (pad_x * 2)
        usable_h = fh - (pad_y * 2) - top_offset
        y_top = pad_y + top_offset

        col_w = usable_w / 3.0 - 10.0
        c1_x = pad_x
        c2_x = c1_x + col_w + 15.0
        c3_x = c2_x + col_w + 15.0

        # Col 1: Logo & Brand
        y1 = y_top
        if brand.logos:
            lw, lh = SizeCalculator.calculate_logo_size(brand.logos[0], col_w * 0.8, min(usable_h * 0.4, 45.0 * font_scale))
            elements.append(FooterElement(id="logo_1", type="logo", image_url=brand.logos[0].url, x=c1_x, y=y1, width=lw, height=lh))
            y1 += lh + 4.0

        if brand.brand_name.strip():
            th = font_sizes["title"] * 1.2
            elements.append(FooterElement(
                id="bname_1", type="text", text=brand.brand_name,
                x=c1_x, y=y1, width=col_w, height=th,
                style=ElementStyle(font_family=default_font, font_size=font_sizes["title"], font_weight="800", color=colors["text_primary"])
            ))

        # Col 2: Contacts
        contacts = cls._extract_contacts(brand)
        y2 = y_top
        line_h = min(18.0 * font_scale, max(12.0, usable_h / max(1, len(contacts))))
        fsz = max(9.0, min(font_sizes["body"], line_h * 0.72))
        for icon, val in contacts[:4]:
            elements.append(FooterElement(
                id=f"cnt_{len(elements)}", type="icon_text", icon=icon, text=val,
                x=c2_x, y=y2, width=col_w, height=line_h,
                style=ElementStyle(font_family="Inter", font_size=fsz, color=colors["text_primary"])
            ))
            y2 += line_h + 2.0

        # Col 3: Socials & QR
        socials = cls._extract_socials(brand)
        y3 = y_top
        for p, h in socials[:3]:
            elements.append(FooterElement(
                id=f"soc_{len(elements)}", type="icon_text", icon=p, text=h,
                x=c3_x, y=y3, width=col_w * 0.65, height=line_h,
                style=ElementStyle(font_family="Inter", font_size=fsz, color=colors["text_secondary"])
            ))
            y3 += line_h + 2.0

        if brand.qr_code_content:
            qr_sz = min(usable_h * 0.65, 48.0 * font_scale)
            qr_url = QRService.generate_qr_data_url(brand.qr_code_content)
            elements.append(FooterElement(
                id="qr_1", type="qr", image_url=qr_url,
                x=c3_x + col_w - qr_sz, y=y_top, width=qr_sz, height=qr_sz
            ))

        return elements

    # ==========================================================================
    # 5. Four-Column: Branding, Phone, Address, Social Details
    # ==========================================================================
    @classmethod
    def _arrange_four_column(cls, fw, fh, pad_x, pad_y, top_offset, brand, font_sizes, font_scale, colors, default_font, default_frame, shape_key):
        elements: List[FooterElement] = []
        usable_w = fw - (pad_x * 2)
        usable_h = fh - (pad_y * 2) - top_offset
        y_top = pad_y + top_offset

        col_w = usable_w / 4.0 - 8.0
        c_x = [pad_x + (i * (col_w + 10.0)) for i in range(4)]

        # Col 1: Branding
        if brand.logos:
            lw, lh = SizeCalculator.calculate_logo_size(brand.logos[0], col_w * 0.85, min(usable_h * 0.45, 40.0 * font_scale))
            elements.append(FooterElement(id="logo_1", type="logo", image_url=brand.logos[0].url, x=c_x[0], y=y_top, width=lw, height=lh))
            if brand.brand_name.strip():
                th = font_sizes["title"] * 1.1
                elements.append(FooterElement(id="bname_1", type="text", text=brand.brand_name, x=c_x[0], y=y_top + lh + 4.0, width=col_w, height=th, style=ElementStyle(font_size=font_sizes["body"], font_weight="bold", color=colors["text_primary"])))

        # Col 2: Phone & WhatsApp
        y2 = y_top
        line_h = 16.0 * font_scale
        if brand.phone.strip():
            elements.append(FooterElement(id="p_1", type="icon_text", icon="phone", text=brand.phone, x=c_x[1], y=y2, width=col_w, height=line_h, style=ElementStyle(font_size=font_sizes["small"], color=colors["text_primary"])))
            y2 += line_h + 3.0
        if brand.whatsapp.strip():
            elements.append(FooterElement(id="w_1", type="icon_text", icon="whatsapp", text=brand.whatsapp, x=c_x[1], y=y2, width=col_w, height=line_h, style=ElementStyle(font_size=font_sizes["small"], color=colors["text_primary"])))

        # Col 3: Email & Website / Address
        y3 = y_top
        if brand.email.strip():
            elements.append(FooterElement(id="e_1", type="icon_text", icon="email", text=brand.email, x=c_x[2], y=y3, width=col_w, height=line_h, style=ElementStyle(font_size=font_sizes["small"], color=colors["text_primary"])))
            y3 += line_h + 3.0
        if brand.website.strip():
            elements.append(FooterElement(id="web_1", type="icon_text", icon="website", text=brand.website, x=c_x[2], y=y3, width=col_w, height=line_h, style=ElementStyle(font_size=font_sizes["small"], color=colors["text_primary"])))

        # Col 4: Socials + QR
        socials = cls._extract_socials(brand)
        y4 = y_top
        for p, h in socials[:2]:
            elements.append(FooterElement(id=f"soc_{p}", type="icon_text", icon=p, text=h, x=c_x[3], y=y4, width=col_w * 0.65, height=line_h, style=ElementStyle(font_size=font_sizes["small"], color=colors["text_secondary"])))
            y4 += line_h + 3.0

        if brand.qr_code_content:
            qr_sz = min(usable_h * 0.70, 48.0 * font_scale)
            qr_url = QRService.generate_qr_data_url(brand.qr_code_content)
            elements.append(FooterElement(id="qr_1", type="qr", image_url=qr_url, x=c_x[3] + col_w - qr_sz, y=y_top, width=qr_sz, height=qr_sz))

        return elements

    # ==========================================================================
    # 6. Centred Layout: Logo & Brand Centred, Contacts Arranged Below
    # ==========================================================================
    @classmethod
    def _arrange_centred(cls, fw, fh, pad_x, pad_y, top_offset, brand, font_sizes, font_scale, colors, default_font, default_frame, shape_key):
        elements: List[FooterElement] = []
        usable_w = fw - (pad_x * 2)
        usable_h = fh - (pad_y * 2) - top_offset
        y_curr = pad_y + top_offset

        # Logo Centered
        if brand.logos:
            lw, lh = SizeCalculator.calculate_logo_size(brand.logos[0], usable_w * 0.35, min(usable_h * 0.35, 45.0 * font_scale))
            elements.append(FooterElement(
                id="logo_1", type="logo", image_url=brand.logos[0].url,
                x=pad_x + (usable_w - lw) / 2.0, y=y_curr, width=lw, height=lh
            ))
            y_curr += lh + 3.0

        # Brand Name Centered
        if brand.brand_name.strip():
            th = font_sizes["title"] * 1.25
            elements.append(FooterElement(
                id="bname_1", type="text", text=brand.brand_name,
                x=pad_x, y=y_curr, width=usable_w, height=th,
                style=ElementStyle(font_family=default_font, font_size=font_sizes["title"], font_weight="800", color=colors["text_primary"], text_align="center")
            ))
            y_curr += th + 2.0

        # Tagline Centered
        if brand.tagline and brand.tagline.strip():
            tag_h = font_sizes["tagline"] * 1.2
            elements.append(FooterElement(
                id="tag_1", type="text", text=brand.tagline,
                x=pad_x, y=y_curr, width=usable_w, height=tag_h,
                style=ElementStyle(font_family=default_font, font_size=font_sizes["tagline"], font_weight="500", color=colors["acc_col"], text_align="center")
            ))
            y_curr += tag_h + 4.0

        # Centered inline contacts
        contacts = cls._extract_contacts(brand)
        if contacts:
            cnt_w = usable_w / len(contacts)
            lh = min(18.0 * font_scale, max(12.0, fh - pad_y - y_curr))
            for i, (icon, val) in enumerate(contacts):
                elements.append(FooterElement(
                    id=f"cnt_{i+1}", type="icon_text", icon=icon, text=val,
                    x=pad_x + (i * cnt_w), y=y_curr, width=cnt_w - 4.0, height=lh,
                    style=ElementStyle(font_family="Inter", font_size=font_sizes["small"], color=colors["text_secondary"], text_align="center")
                ))

        return elements

    # ==========================================================================
    # 7. Left-Aligned Stack: All Content Aligned Vertically on the Left
    # ==========================================================================
    @classmethod
    def _arrange_left_aligned_stack(cls, fw, fh, pad_x, pad_y, top_offset, brand, font_sizes, font_scale, colors, default_font, default_frame, shape_key):
        elements: List[FooterElement] = []
        usable_w = fw - (pad_x * 2)
        usable_h = fh - (pad_y * 2) - top_offset
        y_curr = pad_y + top_offset
        content_w = usable_w * 0.65

        if brand.logos:
            lw, lh = SizeCalculator.calculate_logo_size(brand.logos[0], content_w * 0.5, min(usable_h * 0.35, 42.0 * font_scale))
            elements.append(FooterElement(id="logo_1", type="logo", image_url=brand.logos[0].url, x=pad_x, y=y_curr, width=lw, height=lh))
            y_curr += lh + 3.0

        if brand.brand_name.strip():
            th = font_sizes["title"] * 1.2
            elements.append(FooterElement(id="bname_1", type="text", text=brand.brand_name, x=pad_x, y=y_curr, width=content_w, height=th, style=ElementStyle(font_size=font_sizes["title"], font_weight="800", color=colors["text_primary"])))
            y_curr += th + 2.0

        contacts = cls._extract_contacts(brand)
        lh = min(16.0 * font_scale, max(11.0, (fh - pad_y - y_curr) / max(1, len(contacts))))
        for icon, val in contacts:
            elements.append(FooterElement(id=f"cnt_{len(elements)}", type="icon_text", icon=icon, text=val, x=pad_x, y=y_curr, width=content_w, height=lh, style=ElementStyle(font_size=font_sizes["small"], color=colors["text_secondary"])))
            y_curr += lh + 2.0

        if brand.qr_code_content:
            qr_sz = min(usable_h * 0.75, 60.0 * font_scale)
            qr_url = QRService.generate_qr_data_url(brand.qr_code_content)
            elements.append(FooterElement(id="qr_1", type="qr", image_url=qr_url, x=fw - pad_x - qr_sz, y=pad_y + top_offset, width=qr_sz, height=qr_sz))

        return elements

    # ==========================================================================
    # 8. Right-Aligned Stack: All Content Aligned Vertically on the Right
    # ==========================================================================
    @classmethod
    def _arrange_right_aligned_stack(cls, fw, fh, pad_x, pad_y, top_offset, brand, font_sizes, font_scale, colors, default_font, default_frame, shape_key):
        elements: List[FooterElement] = []
        usable_w = fw - (pad_x * 2)
        usable_h = fh - (pad_y * 2) - top_offset
        y_curr = pad_y + top_offset
        content_w = usable_w * 0.65
        right_x = fw - pad_x - content_w

        # Left area for avatar or QR
        if brand.profiles:
            psize = min(usable_h * 0.65, 60.0 * font_scale)
            elements.append(FooterElement(id="prof_1", type="profile", image_url=brand.profiles[0].url, x=pad_x, y=y_curr, width=psize, height=psize, style=ElementStyle(frame_shape="circle", border_color=colors["acc_col"], border_width=2.0)))
        elif brand.qr_code_content:
            qr_sz = min(usable_h * 0.65, 55.0 * font_scale)
            qr_url = QRService.generate_qr_data_url(brand.qr_code_content)
            elements.append(FooterElement(id="qr_1", type="qr", image_url=qr_url, x=pad_x, y=y_curr, width=qr_sz, height=qr_sz))

        if brand.logos:
            lw, lh = SizeCalculator.calculate_logo_size(brand.logos[0], content_w * 0.5, min(usable_h * 0.35, 42.0 * font_scale))
            elements.append(FooterElement(id="logo_1", type="logo", image_url=brand.logos[0].url, x=fw - pad_x - lw, y=y_curr, width=lw, height=lh))
            y_curr += lh + 3.0

        if brand.brand_name.strip():
            th = font_sizes["title"] * 1.2
            elements.append(FooterElement(id="bname_1", type="text", text=brand.brand_name, x=right_x, y=y_curr, width=content_w, height=th, style=ElementStyle(font_size=font_sizes["title"], font_weight="800", color=colors["text_primary"], text_align="right")))
            y_curr += th + 2.0

        contacts = cls._extract_contacts(brand)
        lh = min(16.0 * font_scale, max(11.0, (fh - pad_y - y_curr) / max(1, len(contacts))))
        for icon, val in contacts:
            elements.append(FooterElement(id=f"cnt_{len(elements)}", type="icon_text", icon=icon, text=val, x=right_x, y=y_curr, width=content_w, height=lh, style=ElementStyle(font_size=font_sizes["small"], color=colors["text_secondary"], text_align="right")))
            y_curr += lh + 2.0

        return elements

    # ==========================================================================
    # 9. Logo-Centre Layout: Logo in Centre, Info Distributed on Both Sides
    # ==========================================================================
    @classmethod
    def _arrange_logo_centre(cls, fw, fh, pad_x, pad_y, top_offset, brand, font_sizes, font_scale, colors, default_font, default_frame, shape_key):
        elements: List[FooterElement] = []
        usable_w = fw - (pad_x * 2)
        usable_h = fh - (pad_y * 2) - top_offset
        y_top = pad_y + top_offset

        col_w = usable_w * 0.38
        center_w = usable_w * 0.24

        left_x = pad_x
        center_x = left_x + col_w
        right_x = center_x + center_w

        # Center: Logo
        if brand.logos:
            lw, lh = SizeCalculator.calculate_logo_size(brand.logos[0], center_w * 0.9, min(usable_h * 0.55, 60.0 * font_scale))
            elements.append(FooterElement(id="logo_1", type="logo", image_url=brand.logos[0].url, x=center_x + (center_w - lw) / 2.0, y=y_top, width=lw, height=lh))

        # Left: Brand Name & Tagline
        y_l = y_top
        if brand.brand_name.strip():
            th = font_sizes["title"] * 1.2
            elements.append(FooterElement(id="bname_1", type="text", text=brand.brand_name, x=left_x, y=y_l, width=col_w, height=th, style=ElementStyle(font_size=font_sizes["title"], font_weight="800", color=colors["text_primary"])))
            y_l += th + 2.0
        if brand.tagline and brand.tagline.strip():
            tag_h = font_sizes["tagline"] * 1.2
            elements.append(FooterElement(id="tag_1", type="text", text=brand.tagline, x=left_x, y=y_l, width=col_w, height=tag_h, style=ElementStyle(font_size=font_sizes["tagline"], color=colors["acc_col"])))

        # Right: Contacts & QR
        contacts = cls._extract_contacts(brand)
        qr_sz = min(usable_h * 0.65, 48.0 * font_scale) if brand.qr_code_content else 0.0
        c_w = col_w - (qr_sz + 8.0 if qr_sz > 0 else 0.0)

        y_r = y_top
        line_h = min(18.0 * font_scale, max(12.0, usable_h / max(1, len(contacts))))
        for icon, val in contacts[:3]:
            elements.append(FooterElement(id=f"cnt_{len(elements)}", type="icon_text", icon=icon, text=val, x=right_x, y=y_r, width=c_w, height=line_h, style=ElementStyle(font_size=font_sizes["small"], color=colors["text_primary"])))
            y_r += line_h + 2.0

        if qr_sz > 0:
            qr_url = QRService.generate_qr_data_url(brand.qr_code_content)
            elements.append(FooterElement(id="qr_1", type="qr", image_url=qr_url, x=right_x + col_w - qr_sz, y=y_top, width=qr_sz, height=qr_sz))

        return elements

    # ==========================================================================
    # 10. Profile-Focused: Large Profile Photo with Brand Details and Contacts
    # ==========================================================================
    @classmethod
    def _arrange_profile_focused(cls, fw, fh, pad_x, pad_y, top_offset, brand, font_sizes, font_scale, colors, default_font, default_frame, shape_key):
        elements: List[FooterElement] = []
        usable_w = fw - (pad_x * 2)
        usable_h = fh - (pad_y * 2) - top_offset
        y_top = pad_y + top_offset

        # Prominent Profile Photo
        psize = min(usable_h * 0.85, 75.0 * font_scale)
        prof_url = brand.profiles[0].url if brand.profiles else "https://via.placeholder.com/150"
        elements.append(FooterElement(
            id="prof_1", type="profile", image_url=prof_url,
            x=pad_x, y=y_top, width=psize, height=psize,
            style=ElementStyle(frame_shape="circle", border_color=colors["acc_col"], border_width=2.5)
        ))

        # Brand Info beside Profile
        center_x = pad_x + psize + 14.0
        center_w = usable_w * 0.42
        y_c = y_top

        if brand.brand_name.strip():
            th = font_sizes["title"] * 1.2
            elements.append(FooterElement(id="bname_1", type="text", text=brand.brand_name, x=center_x, y=y_c, width=center_w, height=th, style=ElementStyle(font_size=font_sizes["title"], font_weight="800", color=colors["text_primary"])))
            y_c += th + 2.0

        if brand.tagline and brand.tagline.strip():
            elements.append(FooterElement(id="tag_1", type="text", text=brand.tagline, x=center_x, y=y_c, width=center_w, height=font_sizes["tagline"] * 1.2, style=ElementStyle(font_size=font_sizes["tagline"], color=colors["acc_col"])))
            y_c += font_sizes["tagline"] * 1.2 + 2.0

        # Right: Contacts & QR
        right_x = center_x + center_w + 10.0
        right_w = fw - pad_x - right_x
        contacts = cls._extract_contacts(brand)
        y_r = y_top
        line_h = min(17.0 * font_scale, max(12.0, usable_h / max(1, len(contacts))))
        for icon, val in contacts:
            elements.append(FooterElement(id=f"cnt_{len(elements)}", type="icon_text", icon=icon, text=val, x=right_x, y=y_r, width=right_w, height=line_h, style=ElementStyle(font_size=font_sizes["small"], color=colors["text_primary"])))
            y_r += line_h + 2.0

        return elements

    # ==========================================================================
    # 11. Profile-Circle Layout: Circular Profile Photo with Surrounding Info
    # ==========================================================================
    @classmethod
    def _arrange_profile_circle(cls, fw, fh, pad_x, pad_y, top_offset, brand, font_sizes, font_scale, colors, default_font, default_frame, shape_key):
        elements: List[FooterElement] = []
        usable_w = fw - (pad_x * 2)
        usable_h = fh - (pad_y * 2) - top_offset
        y_top = pad_y + top_offset

        side_w = (usable_w - (usable_h * 0.85)) / 2.0 - 10.0
        psize = min(usable_h * 0.85, 75.0 * font_scale)
        prof_x = pad_x + side_w + 10.0

        # Left side: Brand
        y_l = y_top
        if brand.brand_name.strip():
            elements.append(FooterElement(id="bname_1", type="text", text=brand.brand_name, x=pad_x, y=y_l, width=side_w, height=font_sizes["title"] * 1.2, style=ElementStyle(font_size=font_sizes["title"], font_weight="800", color=colors["text_primary"])))
            y_l += font_sizes["title"] * 1.2 + 2.0
        if brand.website.strip():
            elements.append(FooterElement(id="web_1", type="icon_text", icon="website", text=brand.website, x=pad_x, y=y_l, width=side_w, height=16.0 * font_scale, style=ElementStyle(font_size=font_sizes["small"], color=colors["acc_col"])))

        # Center: Circular Avatar
        prof_url = brand.profiles[0].url if brand.profiles else "https://via.placeholder.com/150"
        elements.append(FooterElement(id="prof_1", type="profile", image_url=prof_url, x=prof_x, y=y_top, width=psize, height=psize, style=ElementStyle(frame_shape="circle", border_color=colors["acc_col"], border_width=3.0)))

        # Right side: Contacts
        right_x = prof_x + psize + 10.0
        contacts = cls._extract_contacts(brand)
        y_r = y_top
        line_h = min(17.0 * font_scale, max(12.0, usable_h / max(1, len(contacts))))
        for icon, val in contacts[:3]:
            elements.append(FooterElement(id=f"cnt_{len(elements)}", type="icon_text", icon=icon, text=val, x=right_x, y=y_r, width=side_w, height=line_h, style=ElementStyle(font_size=font_sizes["small"], color=colors["text_primary"])))
            y_r += line_h + 2.0

        return elements

    # ==========================================================================
    # 12. Logo-Top Layout: Logo at the Top with Two Content Columns Below
    # ==========================================================================
    @classmethod
    def _arrange_logo_top(cls, fw, fh, pad_x, pad_y, top_offset, brand, font_sizes, font_scale, colors, default_font, default_frame, shape_key):
        elements: List[FooterElement] = []
        usable_w = fw - (pad_x * 2)
        usable_h = fh - (pad_y * 2) - top_offset
        y_curr = pad_y + top_offset

        # Top Tier: Logo & Brand Name Inline
        tier1_h = usable_h * 0.35
        if brand.logos:
            l_x = pad_x
            max_lw = usable_w * 0.35
            for l_idx, logo in enumerate(brand.logos[:2]):
                lw, lh = SizeCalculator.calculate_logo_size(logo, max_lw / len(brand.logos[:2]), tier1_h)
                elements.append(FooterElement(id=f"logo_{l_idx+1}", type="logo", image_url=logo.url, x=l_x, y=y_curr, width=lw, height=lh))
                l_x += lw + 8.0
            if brand.brand_name.strip():
                elements.append(FooterElement(id="bname_1", type="text", text=brand.brand_name, x=l_x + 6.0, y=y_curr + (tier1_h - font_sizes["title"] * 1.2) / 2.0, width=fw - pad_x - l_x - 6.0, height=font_sizes["title"] * 1.2, style=ElementStyle(font_size=font_sizes["title"], font_weight="800", color=colors["text_primary"])))

        y_curr += tier1_h + 4.0

        # Bottom Tier: Two Columns
        col_w = usable_w / 2.0 - 10.0
        contacts = cls._extract_contacts(brand)
        half = len(contacts) // 2 or 1

        y_b1 = y_curr
        line_h = min(17.0 * font_scale, max(12.0, (fh - pad_y - y_curr) / max(1, half)))
        for icon, val in contacts[:half]:
            elements.append(FooterElement(id=f"c1_{len(elements)}", type="icon_text", icon=icon, text=val, x=pad_x, y=y_b1, width=col_w, height=line_h, style=ElementStyle(font_size=font_sizes["small"], color=colors["text_secondary"])))
            y_b1 += line_h + 2.0

        y_b2 = y_curr
        for icon, val in contacts[half:]:
            elements.append(FooterElement(id=f"c2_{len(elements)}", type="icon_text", icon=icon, text=val, x=pad_x + col_w + 15.0, y=y_b2, width=col_w, height=line_h, style=ElementStyle(font_size=font_sizes["small"], color=colors["text_secondary"])))
            y_b2 += line_h + 2.0

        return elements

    # ==========================================================================
    # 13. Contact-Card Layout: Each Contact Detail Inside Its Own Small Card
    # ==========================================================================
    @classmethod
    def _arrange_contact_card(cls, fw, fh, pad_x, pad_y, top_offset, brand, font_sizes, font_scale, colors, default_font, default_frame, shape_key):
        elements: List[FooterElement] = []
        usable_w = fw - (pad_x * 2)
        usable_h = fh - (pad_y * 2) - top_offset
        y_top = pad_y + top_offset

        left_w = usable_w * 0.35
        right_x = pad_x + left_w + 15.0
        right_w = usable_w - left_w - 15.0

        # Left: Identity
        y_l = y_top
        if brand.logos:
            lw, lh = SizeCalculator.calculate_logo_size(brand.logos[0], left_w * 0.8, min(usable_h * 0.4, 45.0 * font_scale))
            elements.append(FooterElement(id="logo_1", type="logo", image_url=brand.logos[0].url, x=pad_x, y=y_l, width=lw, height=lh))
            y_l += lh + 4.0

        if brand.brand_name.strip():
            elements.append(FooterElement(id="bname_1", type="text", text=brand.brand_name, x=pad_x, y=y_l, width=left_w, height=font_sizes["title"] * 1.2, style=ElementStyle(font_size=font_sizes["title"], font_weight="800", color=colors["text_primary"])))

        # Right: Pill Cards Grid
        contacts = cls._extract_contacts(brand)
        if contacts:
            card_w = (right_w - 10.0) / 2.0
            card_h = min(26.0 * font_scale, max(18.0, usable_h / 2.5))
            for i, (icon, val) in enumerate(contacts[:4]):
                row = i // 2
                col = i % 2
                cx = right_x + (col * (card_w + 8.0))
                cy = y_top + (row * (card_h + 6.0))
                elements.append(FooterElement(
                    id=f"card_{i+1}", type="badge", icon=icon, text=val,
                    x=cx, y=cy, width=card_w, height=card_h,
                    style=ElementStyle(background_color=colors["sec_col"], color=colors["text_primary"], font_size=font_sizes["small"], border_radius=6.0)
                ))

        return elements

    # ==========================================================================
    # 14. Social-Bottom Layout: Brand & Contacts Above, Socials in Bottom Strip
    # ==========================================================================
    @classmethod
    def _arrange_social_bottom(cls, fw, fh, pad_x, pad_y, top_offset, brand, font_sizes, font_scale, colors, default_font, default_frame, shape_key):
        elements: List[FooterElement] = []
        usable_w = fw - (pad_x * 2)
        usable_h = fh - (pad_y * 2) - top_offset
        y_top = pad_y + top_offset

        top_tier_h = usable_h * 0.70
        bottom_tier_y = fh - pad_y - (usable_h * 0.25)

        # Upper Left: Brand
        if brand.logos:
            lw, lh = SizeCalculator.calculate_logo_size(brand.logos[0], usable_w * 0.3, top_tier_h * 0.5)
            elements.append(FooterElement(id="logo_1", type="logo", image_url=brand.logos[0].url, x=pad_x, y=y_top, width=lw, height=lh))
            if brand.brand_name.strip():
                elements.append(FooterElement(id="bname_1", type="text", text=brand.brand_name, x=pad_x + lw + 12.0, y=y_top, width=usable_w * 0.35, height=font_sizes["title"] * 1.2, style=ElementStyle(font_size=font_sizes["title"], font_weight="800", color=colors["text_primary"])))

        # Upper Right: Phone & Email
        c_x = pad_x + usable_w * 0.65
        c_w = usable_w * 0.35
        y_c = y_top
        line_h = 16.0 * font_scale
        if brand.phone.strip():
            elements.append(FooterElement(id="cnt_p", type="icon_text", icon="phone", text=brand.phone, x=c_x, y=y_c, width=c_w, height=line_h, style=ElementStyle(font_size=font_sizes["small"], color=colors["text_primary"])))
            y_c += line_h + 3.0
        if brand.email.strip():
            elements.append(FooterElement(id="cnt_e", type="icon_text", icon="email", text=brand.email, x=c_x, y=y_c, width=c_w, height=line_h, style=ElementStyle(font_size=font_sizes["small"], color=colors["text_primary"])))

        # Lower Strip: Social Media Row
        socials = cls._extract_socials(brand)
        if socials:
            s_w = usable_w / len(socials)
            for i, (p, h) in enumerate(socials):
                elements.append(FooterElement(
                    id=f"soc_{p}", type="icon_text", icon=p, text=h,
                    x=pad_x + (i * s_w), y=bottom_tier_y, width=s_w - 6.0, height=18.0 * font_scale,
                    style=ElementStyle(font_size=font_sizes["small"], color=colors["acc_col"])
                ))

        return elements

    # ==========================================================================
    # 15. QR-Focused Layout: QR Code in a Prominent Section with Contacts
    # ==========================================================================
    @classmethod
    def _arrange_qr_focused(cls, fw, fh, pad_x, pad_y, top_offset, brand, font_sizes, font_scale, colors, default_font, default_frame, shape_key):
        elements: List[FooterElement] = []
        usable_w = fw - (pad_x * 2)
        usable_h = fh - (pad_y * 2) - top_offset
        y_top = pad_y + top_offset

        # Prominent QR on Right
        qr_sz = min(usable_h * 0.85, 75.0 * font_scale)
        qr_url = QRService.generate_qr_data_url(brand.qr_code_content or "https://example.com")
        elements.append(FooterElement(id="qr_1", type="qr", image_url=qr_url, x=fw - pad_x - qr_sz, y=y_top, width=qr_sz, height=qr_sz))

        left_w = usable_w - qr_sz - 15.0

        # Left Column: Brand & Contacts
        y_l = y_top
        if brand.logos:
            lw, lh = SizeCalculator.calculate_logo_size(brand.logos[0], left_w * 0.45, min(usable_h * 0.35, 42.0 * font_scale))
            elements.append(FooterElement(id="logo_1", type="logo", image_url=brand.logos[0].url, x=pad_x, y=y_l, width=lw, height=lh))
            y_l += lh + 3.0

        if brand.brand_name.strip():
            elements.append(FooterElement(id="bname_1", type="text", text=brand.brand_name, x=pad_x, y=y_l, width=left_w, height=font_sizes["title"] * 1.2, style=ElementStyle(font_size=font_sizes["title"], font_weight="800", color=colors["text_primary"])))
            y_l += font_sizes["title"] * 1.2 + 2.0

        contacts = cls._extract_contacts(brand)
        lh = min(16.0 * font_scale, max(11.0, (fh - pad_y - y_l) / max(1, len(contacts))))
        for icon, val in contacts[:3]:
            elements.append(FooterElement(id=f"cnt_{len(elements)}", type="icon_text", icon=icon, text=val, x=pad_x, y=y_l, width=left_w, height=lh, style=ElementStyle(font_size=font_sizes["small"], color=colors["text_secondary"])))
            y_l += lh + 2.0

        return elements

    # ==========================================================================
    # 16. Split-Panel Layout: Branding in One Panel, Contacts in Another
    # ==========================================================================
    @classmethod
    def _arrange_split_panel(cls, fw, fh, pad_x, pad_y, top_offset, brand, font_sizes, font_scale, colors, default_font, default_frame, shape_key):
        elements: List[FooterElement] = []
        usable_w = fw - (pad_x * 2)
        usable_h = fh - (pad_y * 2) - top_offset
        y_top = pad_y + top_offset

        split_w = usable_w * 0.38
        p1_x = pad_x
        p2_x = pad_x + split_w + 14.0
        p2_w = usable_w - split_w - 14.0

        # Panel 1: Identity
        y1 = y_top
        if brand.logos:
            lw, lh = SizeCalculator.calculate_logo_size(brand.logos[0], split_w * 0.85, min(usable_h * 0.4, 45.0 * font_scale))
            elements.append(FooterElement(id="logo_1", type="logo", image_url=brand.logos[0].url, x=p1_x, y=y1, width=lw, height=lh))
            y1 += lh + 4.0

        if brand.brand_name.strip():
            elements.append(FooterElement(id="bname_1", type="text", text=brand.brand_name, x=p1_x, y=y1, width=split_w, height=font_sizes["title"] * 1.2, style=ElementStyle(font_size=font_sizes["title"], font_weight="800", color=colors["text_primary"])))

        # Panel 2: Contacts Matrix
        contacts = cls._extract_contacts(brand)
        y2 = y_top
        line_h = min(18.0 * font_scale, max(12.0, usable_h / max(1, len(contacts))))
        for icon, val in contacts:
            elements.append(FooterElement(id=f"cnt_{len(elements)}", type="icon_text", icon=icon, text=val, x=p2_x, y=y2, width=p2_w, height=line_h, style=ElementStyle(font_size=font_sizes["body"], font_weight="600", color=colors["text_primary"])))
            y2 += line_h + 2.0

        return elements

    # ==========================================================================
    # 17. Vertical-Sidebar Layout: Logo & Branding in Sidebar, Contacts in Main
    # ==========================================================================
    @classmethod
    def _arrange_vertical_sidebar(cls, fw, fh, pad_x, pad_y, top_offset, brand, font_sizes, font_scale, colors, default_font, default_frame, shape_key):
        elements: List[FooterElement] = []
        usable_w = fw - (pad_x * 2)
        usable_h = fh - (pad_y * 2) - top_offset
        y_top = pad_y + top_offset

        side_w = usable_w * 0.26
        main_x = pad_x + side_w + 14.0
        main_w = usable_w - side_w - 14.0

        # Sidebar: Logo & Compact Name
        if brand.logos:
            lw, lh = SizeCalculator.calculate_logo_size(brand.logos[0], side_w * 0.9, min(usable_h * 0.5, 50.0 * font_scale))
            elements.append(FooterElement(id="logo_1", type="logo", image_url=brand.logos[0].url, x=pad_x, y=y_top, width=lw, height=lh))

        # Main: 2-column contact list
        contacts = cls._extract_contacts(brand)
        c_col_w = (main_w - 10.0) / 2.0
        half = len(contacts) // 2 or 1

        y1 = y_top
        line_h = min(18.0 * font_scale, max(12.0, usable_h / max(1, half)))
        for icon, val in contacts[:half]:
            elements.append(FooterElement(id=f"c1_{len(elements)}", type="icon_text", icon=icon, text=val, x=main_x, y=y1, width=c_col_w, height=line_h, style=ElementStyle(font_size=font_sizes["small"], color=colors["text_primary"])))
            y1 += line_h + 2.0

        y2 = y_top
        for icon, val in contacts[half:]:
            elements.append(FooterElement(id=f"c2_{len(elements)}", type="icon_text", icon=icon, text=val, x=main_x + c_col_w + 10.0, y=y2, width=c_col_w, height=line_h, style=ElementStyle(font_size=font_sizes["small"], color=colors["text_primary"])))
            y2 += line_h + 2.0

        return elements

    # ==========================================================================
    # 18. Floating-Elements Layout: Separate Floating Sections
    # ==========================================================================
    @classmethod
    def _arrange_floating_elements(cls, fw, fh, pad_x, pad_y, top_offset, brand, font_sizes, font_scale, colors, default_font, default_frame, shape_key):
        elements: List[FooterElement] = []
        usable_w = fw - (pad_x * 2)
        usable_h = fh - (pad_y * 2) - top_offset
        y_top = pad_y + top_offset

        # 3 Floating Island blocks
        island_w = usable_w / 3.0 - 10.0

        # Island 1: Brand
        if brand.logos:
            lw, lh = SizeCalculator.calculate_logo_size(brand.logos[0], island_w * 0.8, min(usable_h * 0.45, 45.0 * font_scale))
            elements.append(FooterElement(id="logo_1", type="logo", image_url=brand.logos[0].url, x=pad_x, y=y_top, width=lw, height=lh))
            if brand.brand_name.strip():
                elements.append(FooterElement(id="bname_1", type="text", text=brand.brand_name, x=pad_x, y=y_top + lh + 3.0, width=island_w, height=font_sizes["title"] * 1.1, style=ElementStyle(font_size=font_sizes["body"], font_weight="bold", color=colors["text_primary"])))

        # Island 2: Contacts
        contacts = cls._extract_contacts(brand)
        c2_x = pad_x + island_w + 15.0
        y2 = y_top
        line_h = min(17.0 * font_scale, max(12.0, usable_h / max(1, len(contacts))))
        for icon, val in contacts[:3]:
            elements.append(FooterElement(id=f"cnt_{len(elements)}", type="icon_text", icon=icon, text=val, x=c2_x, y=y2, width=island_w, height=line_h, style=ElementStyle(font_size=font_sizes["small"], color=colors["text_primary"])))
            y2 += line_h + 2.0

        # Island 3: Profile or QR
        c3_x = c2_x + island_w + 15.0
        if brand.profiles:
            psize = min(usable_h * 0.75, 55.0 * font_scale)
            elements.append(FooterElement(id="prof_1", type="profile", image_url=brand.profiles[0].url, x=c3_x, y=y_top, width=psize, height=psize, style=ElementStyle(frame_shape="circle", border_color=colors["acc_col"], border_width=2.0)))
        elif brand.qr_code_content:
            qr_sz = min(usable_h * 0.70, 50.0 * font_scale)
            qr_url = QRService.generate_qr_data_url(brand.qr_code_content)
            elements.append(FooterElement(id="qr_1", type="qr", image_url=qr_url, x=c3_x, y=y_top, width=qr_sz, height=qr_sz))

        return elements

    # ==========================================================================
    # 19. Asymmetric Layout: Unequal Columns with Varied Sizes and Alignments
    # ==========================================================================
    @classmethod
    def _arrange_asymmetric(cls, fw, fh, pad_x, pad_y, top_offset, brand, font_sizes, font_scale, colors, default_font, default_frame, shape_key):
        elements: List[FooterElement] = []
        usable_w = fw - (pad_x * 2)
        usable_h = fh - (pad_y * 2) - top_offset
        y_top = pad_y + top_offset

        # 60% Left, 40% Right
        left_w = usable_w * 0.58
        right_x = pad_x + left_w + 16.0
        right_w = usable_w - left_w - 16.0

        # Left: Large Bold Title, Tagline, and CTA
        y_l = y_top
        if brand.brand_name.strip():
            elements.append(FooterElement(id="bname_1", type="text", text=brand.brand_name, x=pad_x, y=y_l, width=left_w, height=font_sizes["title"] * 1.3, style=ElementStyle(font_size=font_sizes["title"] * 1.15, font_weight="900", color=colors["text_primary"])))
            y_l += font_sizes["title"] * 1.3 + 3.0

        if brand.tagline and brand.tagline.strip():
            elements.append(FooterElement(id="tag_1", type="text", text=brand.tagline, x=pad_x, y=y_l, width=left_w, height=font_sizes["tagline"] * 1.2, style=ElementStyle(font_size=font_sizes["tagline"], color=colors["acc_col"])))
            y_l += font_sizes["tagline"] * 1.2 + 4.0

        if brand.cta and brand.cta.strip():
            btn_h = min(28.0 * font_scale, 24.0)
            elements.append(FooterElement(id="cta_1", type="badge", text=brand.cta, x=pad_x, y=min(fh - pad_y - btn_h, y_l + 4.0), width=min(left_w * 0.6, 140.0 * font_scale), height=btn_h, style=ElementStyle(background_color=colors["acc_col"], color="#ffffff", font_size=font_sizes["cta"], border_radius=4.0)))

        # Right: High density contacts
        contacts = cls._extract_contacts(brand)
        y_r = y_top
        line_h = min(17.0 * font_scale, max(12.0, usable_h / max(1, len(contacts))))
        for icon, val in contacts:
            elements.append(FooterElement(id=f"cnt_{len(elements)}", type="icon_text", icon=icon, text=val, x=right_x, y=y_r, width=right_w, height=line_h, style=ElementStyle(font_size=font_sizes["small"], font_weight="600", color=colors["text_primary"])))
            y_r += line_h + 2.0

        return elements

    # ==========================================================================
    # 20. Compact Layout: Small Logo, Inline Dot-Separated Text
    # ==========================================================================
    @classmethod
    def _arrange_compact(cls, fw, fh, pad_x, pad_y, top_offset, brand, font_sizes, font_scale, colors, default_font, default_frame, shape_key):
        elements: List[FooterElement] = []
        usable_w = fw - (pad_x * 2)
        usable_h = fh - (pad_y * 2) - top_offset
        y_mid = pad_y + top_offset + (usable_h * 0.15)

        # Inline row
        x_curr = pad_x
        if brand.logos:
            lw, lh = SizeCalculator.calculate_logo_size(brand.logos[0], usable_w * 0.20, min(usable_h * 0.6, 32.0 * font_scale))
            elements.append(FooterElement(id="logo_1", type="logo", image_url=brand.logos[0].url, x=x_curr, y=y_mid, width=lw, height=lh))
            x_curr += lw + 12.0

        if brand.brand_name.strip():
            th = font_sizes["body"] * 1.2
            bw = min(usable_w * 0.25, 160.0 * font_scale)
            elements.append(FooterElement(id="bname_1", type="text", text=brand.brand_name, x=x_curr, y=y_mid + 2.0, width=bw, height=th, style=ElementStyle(font_size=font_sizes["body"], font_weight="bold", color=colors["text_primary"])))
            x_curr += bw + 12.0

        contacts = cls._extract_contacts(brand)
        if contacts:
            rem_w = fw - pad_x - x_curr - (45.0 if brand.qr_code_content else 0.0)
            c_w = rem_w / len(contacts)
            lh = 16.0 * font_scale
            for i, (icon, val) in enumerate(contacts):
                elements.append(FooterElement(id=f"cnt_{i+1}", type="icon_text", icon=icon, text=val, x=x_curr + (i * c_w), y=y_mid + 3.0, width=c_w - 4.0, height=lh, style=ElementStyle(font_size=font_sizes["small"], color=colors["text_secondary"])))

        return elements
