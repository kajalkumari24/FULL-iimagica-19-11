import cv2
import numpy as np
from typing import List, Dict, Tuple
from app.models.poster import DominantColor

def rgb_to_hex(r: int, g: int, b: int) -> str:
    return f"#{r:02x}{g:02x}{b:02x}"

def hex_to_rgb(hex_str: str) -> Tuple[int, int, int]:
    hex_str = hex_str.lstrip('#')
    if len(hex_str) == 3:
        hex_str = ''.join([c*2 for c in hex_str])
    if len(hex_str) != 6:
        return (0, 0, 0)
    return tuple(int(hex_str[i:i+2], 16) for i in (0, 2, 4))

def calculate_brightness(r: int, g: int, b: int) -> float:
    # Perceived brightness formula (0.0 to 1.0)
    return (0.299 * r + 0.587 * g + 0.114 * b) / 255.0

def calculate_contrast_ratio(rgb1: Tuple[int, int, int], rgb2: Tuple[int, int, int]) -> float:
    # Relative luminance
    def luminance(c):
        vals = []
        for val in c:
            v = val / 255.0
            vals.append(v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4)
        return 0.2126 * vals[0] + 0.7152 * vals[1] + 0.0722 * vals[2]

    lum1 = luminance(rgb1)
    lum2 = luminance(rgb2)
    lighter = max(lum1, lum2)
    darker = min(lum1, lum2)
    return (lighter + 0.05) / (darker + 0.05)

class ColorAnalyzer:
    def __init__(self, k_clusters: int = 5):
        self.k_clusters = k_clusters

    def analyze_image(self, img_bgr: np.ndarray) -> Dict:
        """
        Extracts dominant colors, bottom region brightness, and palette suggestions.
        """
        h, w, _ = img_bgr.shape
        img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
        
        # Bottom 20% slice to specifically inspect where the footer will naturally sit
        bottom_h = max(int(h * 0.2), 10)
        bottom_slice = img_rgb[h - bottom_h : h, :]
        bottom_mean = np.mean(bottom_slice, axis=(0, 1))
        bottom_brightness = calculate_brightness(int(bottom_mean[0]), int(bottom_mean[1]), int(bottom_mean[2]))
        is_bottom_dark = bottom_brightness < 0.5

        # Downsample full image for fast k-means
        resized = cv2.resize(img_rgb, (150, 150), interpolation=cv2.INTER_AREA)
        pixels = resized.reshape(-1, 3).astype(np.float32)

        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 20, 0.2)
        flags = cv2.KMEANS_RANDOM_CENTERS
        _, labels, centers = cv2.kmeans(pixels, self.k_clusters, None, criteria, 10, flags)

        # Count frequencies
        counts = np.bincount(labels.flatten())
        total_pixels = len(labels)

        dominant_colors: List[DominantColor] = []
        for i in range(len(centers)):
            r, g, b = [int(np.clip(c, 0, 255)) for c in centers[i]]
            pct = float(counts[i] / total_pixels)
            hex_val = rgb_to_hex(r, g, b)
            is_dark = calculate_brightness(r, g, b) < 0.5
            dominant_colors.append(DominantColor(
                hex=hex_val,
                rgb=[r, g, b],
                percentage=round(pct * 100, 2),
                is_dark=is_dark
            ))

        # Sort by percentage descending
        dominant_colors.sort(key=lambda x: x.percentage, reverse=True)

        # Suggest high-contrast footer backgrounds and matching accents
        suggested_palette = self._build_footer_palette(dominant_colors, is_bottom_dark)

        overall_mean = np.mean(img_rgb, axis=(0, 1))
        overall_brightness = calculate_brightness(int(overall_mean[0]), int(overall_mean[1]), int(overall_mean[2]))

        return {
            "dominant_colors": dominant_colors,
            "average_brightness": round(overall_brightness, 2),
            "bottom_brightness": round(bottom_brightness, 2),
            "is_bottom_dark": is_bottom_dark,
            "suggested_footer_palette": suggested_palette
        }

    def _build_footer_palette(self, dominants: List[DominantColor], is_bottom_dark: bool) -> List[str]:
        palette = []
        # If the bottom is dark, we provide sleek deep darks, translucent darks, and vibrant brand accents,
        # plus high-contrast clean whites.
        if is_bottom_dark:
            palette.append("#0f172a") # Slate 900
            palette.append("#1e1b4b") # Deep Indigo
            palette.append("#18181b") # Zinc 900
            palette.append("#ffffff") # Pure White card
        else:
            palette.append("#ffffff") # Clean White
            palette.append("#f8fafc") # Slate 50
            palette.append("#0f172a") # High-contrast dark
            palette.append("#1e293b") # Slate 800

        # Inject top dominant colors
        for c in dominants[:3]:
            if c.hex not in palette:
                palette.append(c.hex)

        return palette
