from typing import Dict, Any, List
from app.models.brand import BrandProfile

class ContentAnalyzer:
    def __init__(self):
        pass

    def analyze_brand_content(self, brand: BrandProfile) -> Dict[str, Any]:
        """
        Calculates content metrics, item counts, text lengths,
        and groupings for optimal footer layout distribution.
        """
        items = []

        if brand.brand_name.strip():
            items.append({"type": "brand_name", "value": brand.brand_name, "priority": 1})
        if brand.tagline and brand.tagline.strip():
            items.append({"type": "tagline", "value": brand.tagline, "priority": 2})
        if brand.phone and brand.phone.strip():
            items.append({"type": "phone", "value": brand.phone, "icon": "phone", "priority": 1})
        if brand.whatsapp and brand.whatsapp.strip():
            items.append({"type": "whatsapp", "value": brand.whatsapp, "icon": "whatsapp", "priority": 1})
        if brand.email and brand.email.strip():
            items.append({"type": "email", "value": brand.email, "icon": "email", "priority": 2})
        if brand.website and brand.website.strip():
            items.append({"type": "website", "value": brand.website, "icon": "globe", "priority": 2})
        if brand.address and brand.address.strip():
            items.append({"type": "address", "value": brand.address, "icon": "map-pin", "priority": 3})
        if brand.cta and brand.cta.strip():
            items.append({"type": "cta", "value": brand.cta, "icon": "sparkles", "priority": 1})

        for platform, handle in (brand.social_handles or {}).items():
            if handle.strip():
                items.append({"type": "social", "platform": platform, "value": handle, "icon": platform, "priority": 2})

        for cf in (brand.custom_fields or []):
            if cf.visible and cf.value.strip():
                items.append({"type": "custom", "label": cf.label, "value": cf.value, "icon": cf.icon or "info", "priority": 3})

        has_logo = len(brand.logos) > 0
        has_profile = len(brand.profiles) > 0
        has_qr = bool(brand.qr_code_content and brand.qr_code_content.strip())

        total_text_length = sum(len(str(it.get("value", ""))) for it in items)
        field_count = len(items)

        # Categorize density
        if field_count <= 3 and not (has_logo and has_profile):
            density = "minimal"
            recommended_columns = 2
        elif field_count <= 6:
            density = "medium"
            recommended_columns = 3
        else:
            density = "rich"
            recommended_columns = 4

        return {
            "field_count": field_count,
            "total_text_length": total_text_length,
            "density": density,
            "recommended_columns": recommended_columns,
            "has_logo": has_logo,
            "has_profile": has_profile,
            "has_qr": has_qr,
            "items": items
        }
