from typing import Dict, Any, Tuple
from app.models.brand import BrandProfile, LogoItem, ProfileItem

class SizeCalculator:
    """
    Computes precise dimensions for logos, avatars, buttons, columns and overall footer
    based on poster dimensions and content density.
    """

    @staticmethod
    def calculate_footer_dimensions(poster_width: float, poster_height: float, density: str, style_name: str, requested_ratio: float = None) -> Tuple[float, float, float, float]:
        """
        Returns (width, height, x, y)
        """
        if requested_ratio and 0.08 <= requested_ratio <= 0.35:
            ratio = requested_ratio
        else:
            # Dynamic height ratio based on content density & aspect ratio
            aspect = poster_width / float(poster_height)
            if density == "minimal":
                ratio = 0.10 if aspect < 0.8 else 0.12
            elif density == "medium":
                ratio = 0.13 if aspect < 0.8 else 0.15
            else: # rich
                ratio = 0.16 if aspect < 0.8 else 0.18

        # Floating or capsule styles have inset margins
        if style_name in ["floating", "capsule"]:
            margin_x = round(poster_width * 0.04)
            margin_b = round(poster_height * 0.03)
            w = poster_width - (margin_x * 2)
            h = round(poster_height * ratio)
            x = margin_x
            y = poster_height - h - margin_b
        else:
            w = poster_width
            h = round(poster_height * ratio)
            x = 0.0
            y = poster_height - h

        return (float(w), float(h), float(x), float(y))

    @staticmethod
    def calculate_logo_size(logo: LogoItem, max_w: float, max_h: float) -> Tuple[float, float]:
        aspect = logo.aspect_ratio if (logo.aspect_ratio and logo.aspect_ratio > 0) else 1.0
        
        # Fit inside max_w x max_h preserving aspect ratio
        if max_w / aspect <= max_h:
            w = max_w
            h = w / aspect
        else:
            h = max_h
            w = h * aspect
        return (round(w, 1), round(h, 1))

    @staticmethod
    def calculate_profile_size(profile: ProfileItem, max_h: float) -> float:
        # Profile is 1:1 circular/rounded badge
        return round(min(max_h, 80.0), 1)
