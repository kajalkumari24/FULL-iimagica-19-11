from typing import List, Optional, Dict
from pydantic import BaseModel, Field

class CustomField(BaseModel):
    id: str
    label: str
    value: str
    icon: Optional[str] = "info"
    order: int = 0
    visible: bool = True

class LogoItem(BaseModel):
    id: str
    name: str = "Logo"
    url: str  # Data URI or file path
    width: Optional[int] = None
    height: Optional[int] = None
    aspect_ratio: float = 1.0

class ProfileItem(BaseModel):
    id: str
    name: str = "Profile"
    url: str  # Data URI or file path
    frame_style: str = "circle"  # circle, square, rounded, arch, shield, hexagon

class BrandProfile(BaseModel):
    id: Optional[str] = "default"
    brand_name: str = ""
    tagline: Optional[str] = ""
    phone: Optional[str] = ""
    whatsapp: Optional[str] = ""
    email: Optional[str] = ""
    website: Optional[str] = ""
    address: Optional[str] = ""
    cta: Optional[str] = ""  # Call to Action, e.g. "Visit Us Today", "Call For Booking"
    social_handles: Dict[str, str] = Field(default_factory=dict) # e.g. {"instagram": "@brand", "facebook": "fb/brand"}
    qr_code_content: Optional[str] = ""
    primary_color: Optional[str] = "#1e293b"
    secondary_color: Optional[str] = "#3b82f6"
    accent_color: Optional[str] = "#f59e0b"
    font_family: Optional[str] = "Inter"
    logos: List[LogoItem] = Field(default_factory=list)
    profiles: List[ProfileItem] = Field(default_factory=list)
    custom_fields: List[CustomField] = Field(default_factory=list)
