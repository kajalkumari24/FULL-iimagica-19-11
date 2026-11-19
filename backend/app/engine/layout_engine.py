from typing import List, Dict, Any, Optional
from app.models.brand import BrandProfile
from app.models.footer import FooterDesign
from app.engine.adaptive_layout_engine import AdaptiveLayoutEngine

class LayoutEngine:
    def __init__(self):
        self.adaptive_engine = AdaptiveLayoutEngine()

    def generate_variations(
        self,
        poster_width: int,
        poster_height: int,
        brand: BrandProfile,
        palette: Optional[List[str]] = None,
        target_ratio: Optional[float] = None,
        style_preference: Optional[str] = "all",
        arrangement_preference: Optional[str] = "all",
    ) -> List[FooterDesign]:
        return self.adaptive_engine.generate_adaptive_variations(
            poster_width=poster_width,
            poster_height=poster_height,
            brand=brand,
            palette=palette,
            target_ratio=target_ratio,
            category_filter=style_preference,
            arrangement_filter=arrangement_preference,
        )
