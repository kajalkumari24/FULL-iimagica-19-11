import type {
  PosterAnalysis,
  GenerationRequest,
  FooterDesign,
  ValidationResult,
  Project,
  BrandProfile,
  AdaptiveTemplateSpec,
  RepairSvgResult,
  ColorScheme,
  LogoPalette,
} from '../types';

const getApiBase = () => {
  if (import.meta.env.VITE_API_URL) {
    return import.meta.env.VITE_API_URL.replace(/\/+$/, '');
  }
  if (typeof window !== 'undefined' && window.location.hostname !== 'localhost' && window.location.hostname !== '127.0.0.1') {
    return window.location.origin;
  }
  return 'http://127.0.0.1:8000';
};
const API_BASE = getApiBase();
const API_URL = API_BASE.endsWith('/api') ? API_BASE : `${API_BASE}/api`;

export async function checkHealth(): Promise<{ status: string }> {
  const res = await fetch(`${API_URL}/health`);
  if (!res.ok) throw new Error('Health check failed');
  return res.json();
}

export async function analyzePoster(file: File): Promise<PosterAnalysis> {
  const formData = new FormData();
  formData.append('file', file);
  const res = await fetch(`${API_URL}/analyze`, {
    method: 'POST',
    body: formData,
  });
  if (!res.ok) throw new Error('Poster analysis failed');
  return res.json();
}

export async function generateFooters(req: GenerationRequest): Promise<FooterDesign[]> {
  const res = await fetch(`${API_URL}/generate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(req),
  });
  if (!res.ok) throw new Error('Footer generation failed');
  return res.json();
}

export async function autoFix(
  footer: FooterDesign,
  posterW: number,
  posterH: number
): Promise<{ footer: FooterDesign; changes: string[] }> {
  const res = await fetch(`${API_URL}/auto-fix`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ footer, poster_width: posterW, poster_height: posterH }),
  });
  if (!res.ok) throw new Error('Auto-fix failed');
  return res.json();
}

export async function rearrangeFooter(
  footer: FooterDesign,
  arrangement: string,
  brand: BrandProfile,
  posterW: number,
  posterH: number
): Promise<FooterDesign> {
  const res = await fetch(`${API_URL}/rearrange`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      footer,
      arrangement,
      brand,
      poster_width: posterW,
      poster_height: posterH,
    }),
  });
  if (!res.ok) throw new Error('Rearrangement failed');
  return res.json();
}

export async function getPositionOptions(
  footer: FooterDesign,
  brand: BrandProfile,
  posterW: number,
  posterH: number
): Promise<FooterDesign[]> {
  const res = await fetch(`${API_URL}/position-options`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      footer,
      brand,
      poster_width: posterW,
      poster_height: posterH,
    }),
  });
  if (!res.ok) throw new Error('Failed to get position options');
  return res.json();
}

export async function extractLogoColors(logoUrl: string): Promise<LogoPalette> {
  const res = await fetch(`${API_URL}/extract-logo-colors`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ logo_url: logoUrl }),
  });
  if (!res.ok) throw new Error('Failed to extract logo colors');
  return res.json();
}

export async function applyLogoColors(
  footer: FooterDesign,
  scheme: ColorScheme
): Promise<FooterDesign> {
  const res = await fetch(`${API_URL}/apply-logo-colors`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ footer, scheme }),
  });
  if (!res.ok) throw new Error('Failed to apply logo colors');
  return res.json();
}

export async function generateLogoColorVariations(
  footer: FooterDesign,
  logoUrl?: string,
  palette?: LogoPalette
): Promise<FooterDesign[]> {
  const res = await fetch(`${API_URL}/generate-logo-color-variations`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ footer, logo_url: logoUrl, palette }),
  });
  if (!res.ok) throw new Error('Failed to generate color variations');
  return res.json();
}

export async function validateFooter(footer: FooterDesign): Promise<ValidationResult> {
  const res = await fetch(`${API_URL}/validate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(footer),
  });
  if (!res.ok) throw new Error('Validation failed');
  return res.json();
}

export async function exportPoster(
  posterDataUrl: string,
  footer: FooterDesign,
  format: string,
  w: number,
  h: number
): Promise<Blob> {
  const res = await fetch(`${API_URL}/export`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      poster_data_url: posterDataUrl,
      footer,
      format,
      poster_width: w,
      poster_height: h,
    }),
  });
  if (!res.ok) throw new Error('Export failed');
  return res.blob();
}

export async function listProjects(): Promise<Project[]> {
  const res = await fetch(`${API_URL}/projects`);
  if (!res.ok) throw new Error('Failed to list projects');
  return res.json();
}

export async function saveProject(project: Project): Promise<Project> {
  const res = await fetch(`${API_URL}/projects`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(project),
  });
  if (!res.ok) throw new Error('Failed to save project');
  return res.json();
}

export async function getProject(id: string): Promise<Project> {
  const res = await fetch(`${API_URL}/projects/${id}`);
  if (!res.ok) throw new Error('Failed to get project');
  return res.json();
}

export async function deleteProject(id: string): Promise<void> {
  const res = await fetch(`${API_URL}/projects/${id}`, { method: 'DELETE' });
  if (!res.ok) throw new Error('Failed to delete project');
}

export async function duplicateProject(id: string): Promise<Project> {
  const res = await fetch(`${API_URL}/projects/${id}/duplicate`, { method: 'POST' });
  if (!res.ok) throw new Error('Failed to duplicate project');
  return res.json();
}

export async function listBrands(): Promise<BrandProfile[]> {
  const res = await fetch(`${API_URL}/brands`);
  if (!res.ok) throw new Error('Failed to list brands');
  return res.json();
}

export async function saveBrand(brand: BrandProfile): Promise<BrandProfile> {
  const res = await fetch(`${API_URL}/brands`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(brand),
  });
  if (!res.ok) throw new Error('Failed to save brand');
  return res.json();
}

export async function deleteBrand(id: string): Promise<void> {
  const res = await fetch(`${API_URL}/brands/${id}`, { method: 'DELETE' });
  if (!res.ok) throw new Error('Failed to delete brand');
}

export async function listTemplates(): Promise<AdaptiveTemplateSpec[]> {
  const res = await fetch(`${API_URL}/templates`);
  if (!res.ok) throw new Error('Failed to list templates');
  return res.json();
}

export async function repairSvg(
  svgContent: string,
  targetWidth: number = 1080,
  targetHeight: number = 160
): Promise<RepairSvgResult> {
  const res = await fetch(`${API_URL}/repair-svg`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      svg_content: svgContent,
      target_width: targetWidth,
      target_height: targetHeight,
    }),
  });
  if (!res.ok) throw new Error('Failed to repair SVG');
  return res.json();
}
