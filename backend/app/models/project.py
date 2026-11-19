from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
from datetime import datetime
from app.models.brand import BrandProfile
from app.models.footer import FooterDesign

class Project(BaseModel):
    id: str
    name: str = "Untitled Project"
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    poster_filename: Optional[str] = None
    poster_data_url: Optional[str] = None
    poster_width: int = 1080
    poster_height: int = 1080
    brand: BrandProfile = Field(default_factory=BrandProfile)
    active_footer: Optional[FooterDesign] = None
    footer_variations: List[FooterDesign] = Field(default_factory=list)
    thumbnail_url: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
