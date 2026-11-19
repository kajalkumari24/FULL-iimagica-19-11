from typing import Dict, Any, List
from pydantic import BaseModel, Field

class HeightRatioConfig(BaseModel):
    portrait: float = 0.12   # 9:16 tall posters
    square: float = 0.15     # 1:1 square banners
    landscape: float = 0.20  # 16:9 wide banners

class ShapeParameters(BaseModel):
    curve_amplitude: float = 25.0
    corner_radius: float = 16.0
    ribbon_height: float = 8.0
    split_ratio: float = 0.32
    inset_margin_ratio: float = 0.04
    shadow: bool = False
    has_notch: bool = False
    notch_width_ratio: float = 0.25
    notch_height: float = 28.0

class ContentZoneConfig(BaseModel):
    identity: Dict[str, float] = Field(default_factory=lambda: {"rel_x": 0.0, "rel_w": 0.33, "align": 0.0})
    contacts: Dict[str, float] = Field(default_factory=lambda: {"rel_x": 0.35, "rel_w": 0.35, "align": 0.0})
    actions: Dict[str, float] = Field(default_factory=lambda: {"rel_x": 0.72, "rel_w": 0.28, "align": 1.0})

class ResponsiveRules(BaseModel):
    portrait_columns: int = 2
    square_columns: int = 3
    landscape_columns: int = 3
    collapse_contacts_on_narrow: bool = True
    min_font_scale: float = 0.75
    max_font_scale: float = 1.8

class AdaptiveTemplate(BaseModel):
    id: str
    name: str
    category: str
    shape_key: str
    arrangement: str = "classic_horizontal"
    description: str
    default_bg_color: str
    default_secondary_color: str
    default_accent_color: str
    default_font: str
    default_frame: str
    height_rules: HeightRatioConfig = Field(default_factory=HeightRatioConfig)
    shape_parameters: ShapeParameters = Field(default_factory=ShapeParameters)
    content_zones: ContentZoneConfig = Field(default_factory=ContentZoneConfig)
    responsive_rules: ResponsiveRules = Field(default_factory=ResponsiveRules)

# ==============================================================================
# The 18 Original Adaptive Base Shape Templates Registry
# ==============================================================================
ORIGINAL_18_TEMPLATES: List[AdaptiveTemplate] = [
    AdaptiveTemplate(
        id="tpl_classic_rect",
        name="Classic Corporate",
        category="corporate",
        shape_key="classic_rectangle",
        arrangement="classic_horizontal",
        description="Full-bleed rectangular bar with clean borders and structured 3-column matrix.",
        default_bg_color="#1e293b",
        default_secondary_color="#334155",
        default_accent_color="#38bdf8",
        default_font="Montserrat",
        default_frame="rounded",
        shape_parameters=ShapeParameters(corner_radius=0.0, shadow=False)
    ),
    AdaptiveTemplate(
        id="tpl_rounded_box",
        name="Modern Rounded",
        category="modern",
        shape_key="rounded_box",
        arrangement="two_column",
        description="Contemporary rounded container with proportional corner curvature.",
        default_bg_color="#0f172a",
        default_secondary_color="#1e1b4b",
        default_accent_color="#6366f1",
        default_font="Inter",
        default_frame="circle",
        shape_parameters=ShapeParameters(corner_radius=20.0, shadow=False)
    ),
    AdaptiveTemplate(
        id="tpl_fluid_wave_single",
        name="Fluid Wave Studio",
        category="creative",
        shape_key="fluid_wave_single",
        arrangement="three_column",
        description="Smooth single sinusoidal crest top with clamped amplitude to prevent distortion on wide banners.",
        default_bg_color="#3b82f6",
        default_secondary_color="#1d4ed8",
        default_accent_color="#f59e0b",
        default_font="Inter",
        default_frame="arch",
        shape_parameters=ShapeParameters(curve_amplitude=24.0)
    ),
    AdaptiveTemplate(
        id="tpl_fluid_wave_double",
        name="Dual Layer Wave",
        category="creative",
        shape_key="fluid_wave_double",
        arrangement="floating_elements",
        description="Double-tier organic waves with overlapping opacity blending.",
        default_bg_color="#4f46e5",
        default_secondary_color="#818cf8",
        default_accent_color="#fbbf24",
        default_font="Inter",
        default_frame="circle",
        shape_parameters=ShapeParameters(curve_amplitude=28.0)
    ),
    AdaptiveTemplate(
        id="tpl_convex_curve",
        name="Convex Dome",
        category="modern",
        shape_key="convex_curve",
        arrangement="centred",
        description="Gentle arched convex curve providing extra breathing room for centered branding.",
        default_bg_color="#09090b",
        default_secondary_color="#27272a",
        default_accent_color="#10b981",
        default_font="Montserrat",
        default_frame="rounded",
        shape_parameters=ShapeParameters(curve_amplitude=22.0)
    ),
    AdaptiveTemplate(
        id="tpl_concave_curve",
        name="Concave Crest",
        category="editorial",
        shape_key="concave_curve",
        arrangement="logo_centre",
        description="Subtle scooped concave slope creating an elegant dip toward the footer center.",
        default_bg_color="#18181b",
        default_secondary_color="#27272a",
        default_accent_color="#ec4899",
        default_font="Playfair Display",
        default_frame="circle",
        shape_parameters=ShapeParameters(curve_amplitude=20.0)
    ),
    AdaptiveTemplate(
        id="tpl_diagonal_bevel",
        name="Diagonal Velocity",
        category="festival",
        shape_key="diagonal_bevel",
        arrangement="asymmetric",
        description="Dynamic forward-slanted diagonal bevel line conveying speed and energy.",
        default_bg_color="#030712",
        default_secondary_color="#1e1b4b",
        default_accent_color="#e11d48",
        default_font="Oswald",
        default_frame="square",
        shape_parameters=ShapeParameters(curve_amplitude=35.0)
    ),
    AdaptiveTemplate(
        id="tpl_diagonal_reverse",
        name="Reverse Angle",
        category="festival",
        shape_key="diagonal_reverse",
        arrangement="right_aligned_stack",
        description="Back-slanted angular footer with vibrant accent stroke.",
        default_bg_color="#022c22",
        default_secondary_color="#064e3b",
        default_accent_color="#10b981",
        default_font="Oswald",
        default_frame="rounded",
        shape_parameters=ShapeParameters(curve_amplitude=35.0)
    ),
    AdaptiveTemplate(
        id="tpl_executive_ribbon",
        name="Executive Ribbon",
        category="premium",
        shape_key="executive_ribbon",
        arrangement="social_bottom",
        description="Solid corporate base with a prominent full-width accent color band across the top border.",
        default_bg_color="#0f172a",
        default_secondary_color="#1e293b",
        default_accent_color="#d97706",
        default_font="Montserrat",
        default_frame="rounded",
        shape_parameters=ShapeParameters(ribbon_height=8.0)
    ),
    AdaptiveTemplate(
        id="tpl_floating_capsule",
        name="Floating Capsule",
        category="modern",
        shape_key="floating_capsule",
        arrangement="compact",
        description="Pill-shaped floating footer floating above the bottom edge with soft ambient shadow.",
        default_bg_color="#1e1b4b",
        default_secondary_color="#312e81",
        default_accent_color="#a855f7",
        default_font="Inter",
        default_frame="circle",
        shape_parameters=ShapeParameters(corner_radius=40.0, shadow=True, inset_margin_ratio=0.03)
    ),
    AdaptiveTemplate(
        id="tpl_floating_card",
        name="Elevated Floating Card",
        category="modern",
        shape_key="floating_card",
        arrangement="contact_card",
        description="Floating rounded rectangular card elevated above the bottom margin.",
        default_bg_color="#0f172a",
        default_secondary_color="#1e293b",
        default_accent_color="#06b6d4",
        default_font="Inter",
        default_frame="rounded",
        shape_parameters=ShapeParameters(corner_radius=16.0, shadow=True, inset_margin_ratio=0.03)
    ),
    AdaptiveTemplate(
        id="tpl_double_layer_offset",
        name="Layered Shadow Card",
        category="creative",
        shape_key="double_layer_offset",
        arrangement="split_panel",
        description="Primary card with an offset colored underlay creating architectural depth.",
        default_bg_color="#0f172a",
        default_secondary_color="#3b82f6",
        default_accent_color="#10b981",
        default_font="Montserrat",
        default_frame="rounded",
        shape_parameters=ShapeParameters(corner_radius=14.0)
    ),
    AdaptiveTemplate(
        id="tpl_split_banner",
        name="Split Duo Banner",
        category="business",
        shape_key="split_banner",
        arrangement="vertical_sidebar",
        description="Distinct two-tone vertical split (32% brand identity block vs 68% contact grid).",
        default_bg_color="#0f172a",
        default_secondary_color="#1e293b",
        default_accent_color="#38bdf8",
        default_font="Inter",
        default_frame="square",
        shape_parameters=ShapeParameters(split_ratio=0.32)
    ),
    AdaptiveTemplate(
        id="tpl_split_angled",
        name="Angled Split Matrix",
        category="business",
        shape_key="split_angled",
        arrangement="four_column",
        description="Diagonal cut dividing the brand showcase from the contact details.",
        default_bg_color="#18181b",
        default_secondary_color="#312e81",
        default_accent_color="#f59e0b",
        default_font="Inter",
        default_frame="circle",
        shape_parameters=ShapeParameters(split_ratio=0.35, curve_amplitude=24.0)
    ),
    AdaptiveTemplate(
        id="tpl_arch_dome",
        name="Cathedral Arch",
        category="editorial",
        shape_key="arch_dome",
        arrangement="profile_focused",
        description="Tapered side shoulders with a rounded central arch.",
        default_bg_color="#111827",
        default_secondary_color="#1f2937",
        default_accent_color="#fbbf24",
        default_font="Playfair Display",
        default_frame="arch",
        shape_parameters=ShapeParameters(corner_radius=24.0)
    ),
    AdaptiveTemplate(
        id="tpl_center_notch",
        name="Hero Badge Notch",
        category="festival",
        shape_key="center_notch",
        arrangement="profile_circle",
        description="Top edge features a raised central badge protrusion highlighting the logo or founder avatar.",
        default_bg_color="#0f172a",
        default_secondary_color="#4f46e5",
        default_accent_color="#f59e0b",
        default_font="Oswald",
        default_frame="circle",
        shape_parameters=ShapeParameters(has_notch=True, notch_width_ratio=0.28, notch_height=26.0)
    ),
    AdaptiveTemplate(
        id="tpl_accent_bar_minimal",
        name="Neon Accent Minimal",
        category="minimal",
        shape_key="accent_bar_minimal",
        arrangement="left_aligned_stack",
        description="Sleek translucent dark card topped with an ultra-thin vibrant neon accent line.",
        default_bg_color="#09090b",
        default_secondary_color="#000000",
        default_accent_color="#06b6d4",
        default_font="Inter",
        default_frame="circle",
        shape_parameters=ShapeParameters(ribbon_height=3.0)
    ),
    AdaptiveTemplate(
        id="tpl_frosted_glass",
        name="Frosted Glass Luxe",
        category="minimal",
        shape_key="frosted_glass",
        arrangement="qr_focused",
        description="Translucent frosted substrate with subtle crisp border stroke and high-legibility typography.",
        default_bg_color="#ffffff",
        default_secondary_color="#f8fafc",
        default_accent_color="#0284c7",
        default_font="Inter",
        default_frame="circle",
        shape_parameters=ShapeParameters(corner_radius=12.0)
    ),
]

# ==============================================================================
# The 30 New Professional, Modern & Creative Footer Designs
# ==============================================================================
NEW_30_TEMPLATES: List[AdaptiveTemplate] = [
    # ---------------- Wave Designs (10 Styles) ----------------
    AdaptiveTemplate(
        id="tpl_wave_single_smooth",
        name="Single Smooth Wave",
        category="wave",
        shape_key="wave_single_smooth",
        arrangement="classic_horizontal",
        description="Gracefully flowing continuous sinusoidal crest with linear gradient transition.",
        default_bg_color="#0284c7",
        default_secondary_color="#0369a1",
        default_accent_color="#38bdf8",
        default_font="Inter",
        default_frame="circle",
        shape_parameters=ShapeParameters(curve_amplitude=26.0)
    ),
    AdaptiveTemplate(
        id="tpl_wave_double",
        name="Double Wave",
        category="wave",
        shape_key="wave_double",
        arrangement="two_column",
        description="Two harmonic overlapping waves creating gentle layered depth and movement.",
        default_bg_color="#2563eb",
        default_secondary_color="#60a5fa",
        default_accent_color="#f59e0b",
        default_font="Inter",
        default_frame="rounded",
        shape_parameters=ShapeParameters(curve_amplitude=30.0)
    ),
    AdaptiveTemplate(
        id="tpl_wave_triple_layered",
        name="Triple Layered Wave",
        category="wave",
        shape_key="wave_triple_layered",
        arrangement="vertical_stacked",
        description="Three tiered cascading fluid strata with multi-opacity depth layering.",
        default_bg_color="#4338ca",
        default_secondary_color="#6366f1",
        default_accent_color="#f43f5e",
        default_font="Montserrat",
        default_frame="arch",
        shape_parameters=ShapeParameters(curve_amplitude=34.0)
    ),
    AdaptiveTemplate(
        id="tpl_wave_asymmetric",
        name="Asymmetric Wave",
        category="wave",
        shape_key="wave_asymmetric",
        arrangement="asymmetric",
        description="Bold asymmetric crest rising on the left and sloping dynamically toward the right.",
        default_bg_color="#0f172a",
        default_secondary_color="#1e293b",
        default_accent_color="#10b981",
        default_font="Inter",
        default_frame="rounded",
        shape_parameters=ShapeParameters(curve_amplitude=36.0)
    ),
    AdaptiveTemplate(
        id="tpl_wave_deep_bottom",
        name="Deep Bottom Wave",
        category="wave",
        shape_key="wave_deep_bottom",
        arrangement="three_column",
        description="Deep swooping parabolic wave creating maximum canvas space for brand details.",
        default_bg_color="#042f2e",
        default_secondary_color="#0f766e",
        default_accent_color="#2dd4bf",
        default_font="Inter",
        default_frame="circle",
        shape_parameters=ShapeParameters(curve_amplitude=42.0)
    ),
    AdaptiveTemplate(
        id="tpl_wave_side",
        name="Side Wave",
        category="wave",
        shape_key="wave_side",
        arrangement="vertical_sidebar",
        description="Horizontal flowing lateral wave emphasizing progressive visual rhythm.",
        default_bg_color="#1e1b4b",
        default_secondary_color="#4338ca",
        default_accent_color="#fbbf24",
        default_font="Montserrat",
        default_frame="rounded",
        shape_parameters=ShapeParameters(curve_amplitude=28.0)
    ),
    AdaptiveTemplate(
        id="tpl_wave_curved_corners",
        name="Wave with Curved Corners",
        category="wave",
        shape_key="wave_curved_corners",
        arrangement="contact_card",
        description="Sinusoidal wave top contained inside a rounded corner bottom shield.",
        default_bg_color="#111827",
        default_secondary_color="#374151",
        default_accent_color="#818cf8",
        default_font="Inter",
        default_frame="rounded",
        shape_parameters=ShapeParameters(corner_radius=20.0, curve_amplitude=24.0)
    ),
    AdaptiveTemplate(
        id="tpl_wave_gradient",
        name="Gradient Wave",
        category="wave",
        shape_key="wave_gradient",
        arrangement="social_bottom",
        description="Vibrant tri-color multi-stop gradient wave with radiant visual energy.",
        default_bg_color="#7c3aed",
        default_secondary_color="#c026d3",
        default_accent_color="#f59e0b",
        default_font="Inter",
        default_frame="circle",
        shape_parameters=ShapeParameters(curve_amplitude=30.0)
    ),
    AdaptiveTemplate(
        id="tpl_wave_floating_logo",
        name="Wave with Floating Logo Area",
        category="wave",
        shape_key="wave_floating_logo",
        arrangement="logo_top",
        description="Flowing wave featuring an elevated left platform specifically engineered for brand logos.",
        default_bg_color="#0f172a",
        default_secondary_color="#2563eb",
        default_accent_color="#38bdf8",
        default_font="Montserrat",
        default_frame="rounded",
        shape_parameters=ShapeParameters(curve_amplitude=28.0)
    ),
    AdaptiveTemplate(
        id="tpl_wave_center_profile",
        name="Wave with Centre Profile Section",
        category="wave",
        shape_key="wave_center_profile",
        arrangement="profile_focused",
        description="Wave crest crowned with a central architectural dome for a founder or speaker profile photo.",
        default_bg_color="#18181b",
        default_secondary_color="#3f3f46",
        default_accent_color="#e11d48",
        default_font="Inter",
        default_frame="circle",
        shape_parameters=ShapeParameters(curve_amplitude=30.0)
    ),

    # ---------------- Curved Designs (7 Styles) ----------------
    AdaptiveTemplate(
        id="tpl_curve_half_circle",
        name="Half-Circle Curve",
        category="curved",
        shape_key="curve_half_circle",
        arrangement="profile_circle",
        description="Bold geometric half-circle dome rising seamlessly from the footer centerline.",
        default_bg_color="#0f172a",
        default_secondary_color="#1e293b",
        default_accent_color="#0ea5e9",
        default_font="Inter",
        default_frame="circle",
        shape_parameters=ShapeParameters(curve_amplitude=38.0)
    ),
    AdaptiveTemplate(
        id="tpl_curve_convex",
        name="Convex Curve",
        category="curved",
        shape_key="curve_convex",
        arrangement="centred",
        description="Smooth upward-bulging convex arch providing a balanced, harmonious baseline.",
        default_bg_color="#1e1e24",
        default_secondary_color="#2e2e38",
        default_accent_color="#10b981",
        default_font="Montserrat",
        default_frame="rounded",
        shape_parameters=ShapeParameters(curve_amplitude=24.0)
    ),
    AdaptiveTemplate(
        id="tpl_curve_concave",
        name="Concave Curve",
        category="curved",
        shape_key="curve_concave",
        arrangement="logo_centre",
        description="Elegant downward scoop directing viewer focus toward the poster's visual center.",
        default_bg_color="#09090b",
        default_secondary_color="#18181b",
        default_accent_color="#f43f5e",
        default_font="Playfair Display",
        default_frame="arch",
        shape_parameters=ShapeParameters(curve_amplitude=22.0)
    ),
    AdaptiveTemplate(
        id="tpl_curve_double",
        name="Double Curved Footer",
        category="curved",
        shape_key="curve_double",
        arrangement="four_column",
        description="Dual alternating Bezier curves producing rhythmic elegance across wide posters.",
        default_bg_color="#172554",
        default_secondary_color="#1e40af",
        default_accent_color="#60a5fa",
        default_font="Inter",
        default_frame="rounded",
        shape_parameters=ShapeParameters(curve_amplitude=26.0)
    ),
    AdaptiveTemplate(
        id="tpl_curve_organic_fluid",
        name="Organic Fluid Curve",
        category="curved",
        shape_key="curve_organic_fluid",
        arrangement="floating_elements",
        description="Multi-point cubic spline curve with accent trim line for contemporary creative agencies.",
        default_bg_color="#022c22",
        default_secondary_color="#065f46",
        default_accent_color="#34d399",
        default_font="Inter",
        default_frame="circle",
        shape_parameters=ShapeParameters(curve_amplitude=30.0)
    ),
    AdaptiveTemplate(
        id="tpl_curve_arch",
        name="Arch-Shaped Footer",
        category="curved",
        shape_key="curve_arch",
        arrangement="vertical_stacked",
        description="Classic Romanesque rounded arch pillars crowning the footer boundaries.",
        default_bg_color="#1e1b4b",
        default_secondary_color="#312e81",
        default_accent_color="#c084fc",
        default_font="Playfair Display",
        default_frame="arch",
        shape_parameters=ShapeParameters(corner_radius=28.0)
    ),
    AdaptiveTemplate(
        id="tpl_curve_circular_corners",
        name="Circular Corner Footer",
        category="curved",
        shape_key="curve_circular_corners",
        arrangement="two_column",
        description="Extended full-width footer with pronounced circular quarter-arc top corners.",
        default_bg_color="#0f172a",
        default_secondary_color="#1e293b",
        default_accent_color="#38bdf8",
        default_font="Montserrat",
        default_frame="rounded",
        shape_parameters=ShapeParameters(corner_radius=35.0)
    ),

    # ---------------- Modern Designs (13 Styles) ----------------
    AdaptiveTemplate(
        id="tpl_modern_diagonal_layered",
        name="Diagonal Layered Footer",
        category="modern",
        shape_key="modern_diagonal_layered",
        arrangement="asymmetric",
        description="Two-tiered angled geometric planes with dynamic velocity accent rule.",
        default_bg_color="#09090b",
        default_secondary_color="#18181b",
        default_accent_color="#f59e0b",
        default_font="Oswald",
        default_frame="square",
        shape_parameters=ShapeParameters(curve_amplitude=38.0)
    ),
    AdaptiveTemplate(
        id="tpl_modern_slanted_split",
        name="Slanted Split Footer",
        category="modern",
        shape_key="modern_slanted_split",
        arrangement="split_panel",
        description="65-degree angled divider splitting corporate identity from contact matrix.",
        default_bg_color="#0f172a",
        default_secondary_color="#1e293b",
        default_accent_color="#06b6d4",
        default_font="Inter",
        default_frame="rounded",
        shape_parameters=ShapeParameters(split_ratio=0.36)
    ),
    AdaptiveTemplate(
        id="tpl_modern_zigzag",
        name="Zigzag Footer",
        category="geometric",
        shape_key="modern_zigzag",
        arrangement="contact_card",
        description="Rhythmic geometric sawtooth apex delivering high-impact festival energy.",
        default_bg_color="#18181b",
        default_secondary_color="#27272a",
        default_accent_color="#ec4899",
        default_font="Oswald",
        default_frame="square",
        shape_parameters=ShapeParameters(curve_amplitude=12.0)
    ),
    AdaptiveTemplate(
        id="tpl_modern_geometric_polygon",
        name="Geometric Polygon Footer",
        category="geometric",
        shape_key="modern_geometric_polygon",
        arrangement="four_column",
        description="Multi-faceted faceted vertices creating architectural polygonal aesthetics.",
        default_bg_color="#020617",
        default_secondary_color="#0f172a",
        default_accent_color="#38bdf8",
        default_font="Montserrat",
        default_frame="shield",
        shape_parameters=ShapeParameters(curve_amplitude=24.0)
    ),
    AdaptiveTemplate(
        id="tpl_modern_floating_glass",
        name="Floating Glass Footer",
        category="modern",
        shape_key="modern_floating_glass",
        arrangement="floating_elements",
        description="Floating frosted translucent card with soft diffusion shadow and illuminated borders.",
        default_bg_color="#0f172a",
        default_secondary_color="#1e293b",
        default_accent_color="#38bdf8",
        default_font="Inter",
        default_frame="circle",
        shape_parameters=ShapeParameters(corner_radius=18.0, shadow=True, inset_margin_ratio=0.02)
    ),
    AdaptiveTemplate(
        id="tpl_modern_transparent_overlay",
        name="Transparent Overlay Footer",
        category="minimal",
        shape_key="modern_transparent_overlay",
        arrangement="compact",
        description="Subtle darkened overlay allowing poster photography to shine through footer content.",
        default_bg_color="#000000",
        default_secondary_color="#18181b",
        default_accent_color="#ffffff",
        default_font="Inter",
        default_frame="circle",
        shape_parameters=ShapeParameters(corner_radius=0.0)
    ),
    AdaptiveTemplate(
        id="tpl_modern_rounded_capsule",
        name="Rounded Capsule Footer",
        category="modern",
        shape_key="modern_rounded_capsule",
        arrangement="compact",
        description="Sleek floating pill-shaped stadium capsule with luminous border.",
        default_bg_color="#1e1b4b",
        default_secondary_color="#312e81",
        default_accent_color="#a855f7",
        default_font="Inter",
        default_frame="circle",
        shape_parameters=ShapeParameters(corner_radius=44.0, shadow=True, inset_margin_ratio=0.025)
    ),
    AdaptiveTemplate(
        id="tpl_modern_layered_shadow",
        name="Layered Shadow Footer",
        category="modern",
        shape_key="modern_layered_shadow",
        arrangement="two_column",
        description="Double offset cards creating tangible 3D physical card perspective.",
        default_bg_color="#0f172a",
        default_secondary_color="#2563eb",
        default_accent_color="#fbbf24",
        default_font="Montserrat",
        default_frame="rounded",
        shape_parameters=ShapeParameters(corner_radius=16.0)
    ),
    AdaptiveTemplate(
        id="tpl_modern_ribbon",
        name="Ribbon-Style Footer",
        category="corporate",
        shape_key="modern_ribbon",
        arrangement="social_bottom",
        description="Prestige executive ribbon banner featuring an accent authority band.",
        default_bg_color="#1e293b",
        default_secondary_color="#334155",
        default_accent_color="#d97706",
        default_font="Montserrat",
        default_frame="rounded",
        shape_parameters=ShapeParameters(ribbon_height=8.0)
    ),
    AdaptiveTemplate(
        id="tpl_modern_folded_corner",
        name="Folded Corner Footer",
        category="geometric",
        shape_key="modern_folded_corner",
        arrangement="qr_focused",
        description="Origami corner fold accent highlighting status, certifications, or awards.",
        default_bg_color="#18181b",
        default_secondary_color="#27272a",
        default_accent_color="#10b981",
        default_font="Inter",
        default_frame="square",
        shape_parameters=ShapeParameters(corner_radius=0.0)
    ),
    AdaptiveTemplate(
        id="tpl_modern_asymmetric_split",
        name="Asymmetric Split Footer",
        category="modern",
        shape_key="modern_asymmetric_split",
        arrangement="split_panel",
        description="32% brand identity block cleanly offset from the 68% contact grid.",
        default_bg_color="#0f172a",
        default_secondary_color="#1e293b",
        default_accent_color="#6366f1",
        default_font="Inter",
        default_frame="rounded",
        shape_parameters=ShapeParameters(split_ratio=0.32)
    ),
    AdaptiveTemplate(
        id="tpl_modern_gradient_mesh",
        name="Gradient Mesh Footer",
        category="modern",
        shape_key="modern_gradient_mesh",
        arrangement="logo_centre",
        description="Multi-stop ambient gradient mesh radiating rich color harmonies.",
        default_bg_color="#312e81",
        default_secondary_color="#701a75",
        default_accent_color="#f59e0b",
        default_font="Inter",
        default_frame="circle",
        shape_parameters=ShapeParameters(corner_radius=0.0)
    ),
    AdaptiveTemplate(
        id="tpl_modern_minimal_accent",
        name="Minimal Accent-Line Footer",
        category="minimal",
        shape_key="modern_minimal_accent",
        arrangement="left_aligned_stack",
        description="Understated modern elegance topped with a luminous 3.5px neon accent rule.",
        default_bg_color="#09090b",
        default_secondary_color="#18181b",
        default_accent_color="#06b6d4",
        default_font="Inter",
        default_frame="circle",
        shape_parameters=ShapeParameters(ribbon_height=3.5)
    ),
]

# Combined 48 Templates Registry (18 Original + 30 New)
ADAPTIVE_TEMPLATES_REGISTRY: List[AdaptiveTemplate] = ORIGINAL_18_TEMPLATES + NEW_30_TEMPLATES

def get_template_by_id(tpl_id: str) -> AdaptiveTemplate:
    for t in ADAPTIVE_TEMPLATES_REGISTRY:
        if t.id == tpl_id:
            return t
    return ADAPTIVE_TEMPLATES_REGISTRY[0]

def list_templates_by_category(category: str) -> List[AdaptiveTemplate]:
    if not category or category.lower() == "all":
        return ADAPTIVE_TEMPLATES_REGISTRY
    return [t for t in ADAPTIVE_TEMPLATES_REGISTRY if t.category.lower() == category.lower()]

def list_templates_by_arrangement(arrangement: str) -> List[AdaptiveTemplate]:
    if not arrangement or arrangement.lower() == "all":
        return ADAPTIVE_TEMPLATES_REGISTRY
    return [t for t in ADAPTIVE_TEMPLATES_REGISTRY if t.arrangement.lower() == arrangement.lower()]
