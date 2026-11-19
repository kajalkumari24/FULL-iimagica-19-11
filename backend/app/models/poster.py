from typing import List, Optional
from pydantic import BaseModel, Field

class DominantColor(BaseModel):
    hex: str
    rgb: List[int]
    percentage: float
    is_dark: bool

class SafeZone(BaseModel):
    top: float  # percentage of height 0.0 - 1.0
    bottom: float
    left: float
    right: float
    suggested_footer_height_ratio: float = 0.15

class PosterAnalysis(BaseModel):
    width: int
    height: int
    aspect_ratio: float
    format: str
    dominant_colors: List[DominantColor] = Field(default_factory=list)
    suggested_footer_palette: List[str] = Field(default_factory=list)
    average_brightness: float = 0.5  # 0.0 to 1.0
    is_bottom_dark: bool = True
    safe_zone: SafeZone
    detected_empty_bottom_space: float = 0.15 # detected ratio of bottom space suitable for footer
