import os
import cv2
import numpy as np
from PIL import Image
from typing import Dict, Any, Optional
from app.analyzer.color_analyzer import ColorAnalyzer
from app.analyzer.space_detector import SpaceDetector
from app.analyzer.content_analyzer import ContentAnalyzer
from app.models.poster import PosterAnalysis, SafeZone

class PosterAnalyzer:
    def __init__(self):
        self.color_analyzer = ColorAnalyzer()
        self.space_detector = SpaceDetector()
        self.content_analyzer = ContentAnalyzer()

    def analyze_image_bytes(self, image_bytes: bytes, filename: str = "poster.png") -> PosterAnalysis:
        # Decode via OpenCV
        nparr = np.frombuffer(image_bytes, np.uint8)
        img_bgr = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if img_bgr is None:
            raise ValueError("Could not decode image bytes")

        h, w, _ = img_bgr.shape
        aspect_ratio = round(w / float(h), 3)
        ext = os.path.splitext(filename)[1].lower().replace('.', '') or "png"

        # Color analysis
        color_res = self.color_analyzer.analyze_image(img_bgr)
        
        # Space detection
        space_res = self.space_detector.detect_space(img_bgr)

        return PosterAnalysis(
            width=w,
            height=h,
            aspect_ratio=aspect_ratio,
            format=ext,
            dominant_colors=color_res["dominant_colors"],
            suggested_footer_palette=color_res["suggested_footer_palette"],
            average_brightness=color_res["average_brightness"],
            is_bottom_dark=color_res["is_bottom_dark"],
            safe_zone=space_res["safe_zone"],
            detected_empty_bottom_space=space_res["detected_empty_bottom_space"]
        )

    def analyze_image_path(self, file_path: str) -> PosterAnalysis:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        with open(file_path, "rb") as f:
            return self.analyze_image_bytes(f.read(), os.path.basename(file_path))
