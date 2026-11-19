import cv2
import numpy as np
from typing import Dict
from app.models.poster import SafeZone

class SpaceDetector:
    def __init__(self):
        pass

    def detect_space(self, img_bgr: np.ndarray) -> Dict:
        """
        Analyzes edge density and visual complexity from bottom to top
        to find safe regions for footers without occluding primary subjects.
        """
        h, w, _ = img_bgr.shape
        gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
        
        # Compute gradient magnitude (Sobel or Canny edges)
        edges = cv2.Canny(gray, 50, 150)

        # Split image into 10 vertical horizontal slices (from top 0 to bottom 9)
        num_slices = 10
        slice_height = h // num_slices
        edge_densities = []

        for i in range(num_slices):
            y_start = i * slice_height
            y_end = (i + 1) * slice_height if i < num_slices - 1 else h
            slice_edges = edges[y_start:y_end, :]
            density = np.sum(slice_edges > 0) / float(slice_edges.size)
            edge_densities.append(density)

        # Inspect bottom slices (8 and 9)
        bottom_slice_density = edge_densities[-1]
        second_bottom_density = edge_densities[-2]

        # Determine reasonable footer height ratio:
        # For tall posters (story/portrait 9:16 or 4:5), 12-16% is ideal.
        # For square posters (1:1), 14-18% is ideal.
        # For landscape (16:9), 16-22% is ideal.
        aspect_ratio = round(w / float(h), 3)

        if aspect_ratio < 0.75: # Tall portrait (e.g. 9:16)
            suggested_ratio = 0.13
        elif aspect_ratio <= 1.25: # Square / 4:5
            suggested_ratio = 0.16
        else: # Landscape
            suggested_ratio = 0.20

        # If bottom is relatively empty (low edge density), we can comfortably use standard or slightly larger ratio
        empty_bottom = False
        if bottom_slice_density < 0.05:
            empty_bottom = True
            empty_space_ratio = 0.20
        elif bottom_slice_density < 0.12:
            empty_bottom = True
            empty_space_ratio = 0.15
        else:
            empty_space_ratio = 0.10

        # Safe margins (standard 3-5% margin inset for floating/capsule styles)
        safe_zone = SafeZone(
            top=0.04,
            bottom=0.04,
            left=0.04,
            right=0.04,
            suggested_footer_height_ratio=suggested_ratio
        )

        return {
            "aspect_ratio": aspect_ratio,
            "edge_densities": [round(float(d), 4) for d in edge_densities],
            "empty_bottom": empty_bottom,
            "detected_empty_bottom_space": empty_space_ratio,
            "safe_zone": safe_zone
        }
