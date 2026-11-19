from app.design_library.shapes.adaptive_shapes import AdaptiveShapes

class FooterShapes:
    @staticmethod
    def get_shape_svg(shape_name: str, width: float, height: float, fill: str, secondary_fill: str = "", opacity: float = 1.0, radius: float = 0.0) -> str:
        return AdaptiveShapes.generate_shape_svg(
            shape_key=shape_name,
            width=width,
            height=height,
            fill=fill,
            secondary_fill=secondary_fill,
            opacity=opacity,
            radius=radius,
        )
