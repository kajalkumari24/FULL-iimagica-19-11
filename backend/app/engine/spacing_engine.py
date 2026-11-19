from typing import Dict, List, Tuple
from app.models.footer import FooterElement

class SpacingEngine:
    @staticmethod
    def get_layout_bounds(footer_w: float, footer_h: float, shape: str) -> Dict[str, float]:
        # Margin offsets based on shapes (e.g. wave or diagonal headers reduce usable top area)
        top_offset = 0.0
        if shape == "wave":
            top_offset = min(footer_h * 0.18, 30.0)
        elif shape == "diagonal":
            top_offset = min(footer_h * 0.15, 25.0)
        elif shape == "ribbon":
            top_offset = min(footer_h * 0.10, 15.0)

        padding_x = max(16.0, footer_w * 0.035)
        padding_y = max(12.0, footer_h * 0.08)

        usable_w = footer_w - (padding_x * 2)
        usable_h = footer_h - padding_y * 2 - top_offset

        return {
            "padding_x": round(padding_x, 1),
            "padding_y": round(padding_y, 1),
            "top_offset": round(top_offset, 1),
            "usable_w": round(usable_w, 1),
            "usable_h": round(usable_h, 1)
        }

    @staticmethod
    def calculate_columns(usable_w: float, num_columns: int, gap: float = 20.0) -> List[Tuple[float, float]]:
        """
        Returns list of (col_x, col_w)
        """
        total_gaps = (num_columns - 1) * gap
        col_w = max(40.0, (usable_w - total_gaps) / num_columns)
        
        cols = []
        cur_x = 0.0
        for _ in range(num_columns):
            cols.append((round(cur_x, 1), round(col_w, 1)))
            cur_x += col_w + gap
        return cols
