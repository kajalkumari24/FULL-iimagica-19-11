export interface CustomField {
  id: string;
  label: string;
  value: string;
  icon?: string;
  order: number;
  visible: boolean;
}

export interface LogoItem {
  id: string;
  name: string;
  url: string;
  width?: number;
  height?: number;
  aspect_ratio: number;
}

export interface ProfileItem {
  id: string;
  name: string;
  url: string;
  frame_style: string;
}

export interface BrandProfile {
  id?: string;
  brand_name: string;
  tagline?: string;
  phone?: string;
  whatsapp?: string;
  email?: string;
  website?: string;
  address?: string;
  cta?: string;
  social_handles?: Record<string, string>;
  qr_code_content?: string;
  primary_color?: string;
  secondary_color?: string;
  accent_color?: string;
  font_family?: string;
  logos: LogoItem[];
  profiles: ProfileItem[];
  custom_fields: CustomField[];
}

export interface DominantColor {
  hex: string;
  rgb: number[];
  percentage: number;
  is_dark: boolean;
}

export interface SafeZone {
  top: number;
  bottom: number;
  left: number;
  right: number;
  suggested_footer_height_ratio: number;
}

export interface PosterAnalysis {
  width: number;
  height: number;
  aspect_ratio: number;
  format: string;
  dominant_colors: DominantColor[];
  suggested_footer_palette: string[];
  average_brightness: number;
  is_bottom_dark: boolean;
  safe_zone: SafeZone;
  detected_empty_bottom_space: number;
}

export interface ElementStyle {
  font_family?: string;
  font_size?: number;
  font_weight?: string;
  color?: string;
  text_align?: string;
  line_height?: number;
  letter_spacing?: number;
  opacity?: number;
  background_color?: string | null;
  border_color?: string | null;
  border_width?: number;
  border_radius?: number;
  padding?: number;
  fit_mode?: string;
  frame_shape?: string;
  shadow?: boolean;
  shadow_color?: string;
  shadow_blur?: number;
}

export interface FooterElement {
  id: string;
  type: string;
  label?: string;
  text?: string;
  icon?: string | null;
  image_url?: string | null;
  x: number;
  y: number;
  width: number;
  height: number;
  rotation: number;
  z_index: number;
  locked: boolean;
  visible: boolean;
  style: ElementStyle;
}

export interface FooterBackground {
  type: string;
  color: string;
  secondary_color?: string | null;
  gradient_direction?: string | null;
  opacity: number;
  blur: number;
  shape: string;
  border_color?: string | null;
  border_width: number;
  border_radius: number;
  shadow: boolean;
  shadow_color: string;
  shadow_blur: number;
}

export interface FooterDesign {
  id: string;
  name: string;
  style_category: string;
  content_arrangement?: string;
  width: number;
  height: number;
  x: number;
  y: number;
  columns: number;
  padding: Record<string, number>;
  background: FooterBackground;
  elements: FooterElement[];
  svg_markup?: string | null;
  preview_data_url?: string | null;
  quality_score: number;
  validation_notices: string[];
}

export interface GenerationRequest {
  poster_width: number;
  poster_height: number;
  brand: BrandProfile;
  style_preference?: string;
  arrangement_preference?: string;
  target_footer_height_ratio?: number | null;
  custom_colors?: string[] | null;
  custom_palette?: Record<string, string> | null;
}

export interface ValidationResult {
  is_valid: boolean;
  quality_score: number;
  notices: string[];
}

export interface Project {
  id: string;
  name: string;
  created_at?: string;
  updated_at?: string;
  poster_filename?: string | null;
  poster_data_url?: string | null;
  poster_width: number;
  poster_height: number;
  brand: BrandProfile;
  active_footer?: FooterDesign | null;
  footer_variations?: FooterDesign[];
  thumbnail_url?: string | null;
  tags?: string[];
}

export interface AdaptiveTemplateSpec {
  id: string;
  name: string;
  category: string;
  shape_key: string;
  arrangement?: string;
  description: string;
  default_bg_color: string;
  default_secondary_color: string;
  default_accent_color: string;
  default_font: string;
  default_frame: string;
  height_rules: {
    portrait: number;
    square: number;
    landscape: number;
  };
  shape_parameters: {
    curve_amplitude: number;
    corner_radius: number;
    ribbon_height: number;
    split_ratio: number;
    inset_margin_ratio: number;
    shadow: boolean;
  };
}

export interface RepairSvgResult {
  is_valid: boolean;
  was_repaired: boolean;
  repaired_svg: string;
  notices: string[];
}

export interface ColorScheme {
  id: string;
  name: string;
  description: string;
  background: string;
  secondary_color: string;
  border_color: string;
  accent: string;
  text_primary: string;
  text_secondary: string;
  badge_bg: string;
  badge_text: string;
  is_dark_bg: boolean;
}

export interface LogoPalette {
  primary: string;
  secondary: string;
  accent: string;
  dark_shade: string;
  light_shade: string;
  dominant_colors: Array<{
    hex: string;
    percentage: number;
    rgb?: number[];
    saturation?: number;
    value?: number;
  }>;
  schemes: ColorScheme[];
}
