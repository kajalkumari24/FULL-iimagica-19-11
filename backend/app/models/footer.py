from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from app.models.brand import BrandProfile

class ElementStyle(BaseModel):
    font_family: Optional[str] = "Inter"
    font_size: Optional[float] = 16
    font_weight: Optional[str] = "normal"  # normal, bold, 500, 600, 700, 800
    color: Optional[str] = "#ffffff"
    text_align: Optional[str] = "left"  # left, center, right
    line_height: Optional[float] = 1.3
    letter_spacing: Optional[float] = 0.0
    opacity: Optional[float] = 1.0
    background_color: Optional[str] = None
    border_color: Optional[str] = None
    border_width: Optional[float] = 0.0
    border_radius: Optional[float] = 0.0
    padding: Optional[float] = 0.0
    fit_mode: Optional[str] = "contain"  # contain, cover, fill
    frame_shape: Optional[str] = "none"  # circle, square, rounded, arch, etc.
    shadow: Optional[bool] = False
    shadow_color: Optional[str] = "rgba(0,0,0,0.3)"
    shadow_blur: Optional[float] = 4.0

class FooterElement(BaseModel):
    id: str
    type: str  # text, icon_text, logo, profile, shape, badge, qr, divider
    label: Optional[str] = ""
    text: Optional[str] = ""
    icon: Optional[str] = None
    image_url: Optional[str] = None
    x: float
    y: float
    width: float
    height: float
    rotation: float = 0.0
    z_index: int = 1
    locked: bool = False
    visible: bool = True
    style: ElementStyle = Field(default_factory=ElementStyle)

class FooterBackground(BaseModel):
    type: str = "solid"  # solid, gradient, pattern, glass, transparent
    color: str = "#0f172a"
    secondary_color: Optional[str] = "#1e293b"
    gradient_direction: Optional[str] = "to right"  # to right, to bottom, 45deg
    opacity: float = 0.95
    blur: float = 0.0
    shape: str = "rectangle"  # rectangle, rounded, wave, ribbon, diagonal, curved, arch, capsule, double_layer, floating, split
    border_color: Optional[str] = None
    border_width: float = 0.0
    border_radius: float = 0.0
    divider_thickness: Optional[float] = 0.0
    shadow: bool = True
    shadow_color: str = "rgba(0,0,0,0.25)"
    shadow_blur: float = 12.0

class FooterDesign(BaseModel):
    id: str
    name: str
    style_category: str = "modern"  # modern, corporate, minimal, creative, premium, festival, business
    content_arrangement: str = "classic_horizontal"  # 20 distinct arrangement styles
    width: float
    height: float
    x: float
    y: float
    columns: int = 3
    padding: Dict[str, float] = Field(default_factory=lambda: {"top": 12, "bottom": 12, "left": 20, "right": 20})
    background: FooterBackground = Field(default_factory=FooterBackground)
    elements: List[FooterElement] = Field(default_factory=list)
    svg_markup: Optional[str] = None
    preview_data_url: Optional[str] = None
    quality_score: float = 100.0
    validation_notices: List[str] = Field(default_factory=list)

class GenerationRequest(BaseModel):
    poster_width: int
    poster_height: int
    brand: BrandProfile
    style_preference: Optional[str] = "all"  # all, modern, corporate, minimal, creative, premium, festival, business
    arrangement_preference: Optional[str] = "all"  # all, or one of the 20 arrangements
    target_footer_height_ratio: Optional[float] = None
    custom_colors: Optional[List[str]] = None
    custom_palette: Optional[Dict[str, str]] = None
