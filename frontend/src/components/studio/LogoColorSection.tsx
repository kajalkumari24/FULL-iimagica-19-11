import React, { useState } from 'react';
import { Palette, Sparkles, RefreshCw, Check, Pipette, Wand2, Layers, AlertCircle } from 'lucide-react';
import { useEditorStore } from '../../store/editorStore';
import * as api from '../../api/client';
import type { ColorScheme, LogoPalette } from '../../types';

export const LogoColorSection: React.FC = () => {
  const {
    brand,
    logos,
    activeFooter,
    setActiveFooter,
    extractedPalette,
    setExtractedPalette,
    isExtractingColors,
    setIsExtractingColors,
    setFooterVariations,
    updateBrandField,
  } = useEditorStore();

  const [activeSchemeId, setActiveSchemeId] = useState<string>('bold_brand');
  const [isApplying, setIsApplying] = useState<boolean>(false);
  const [isRegenerating, setIsRegenerating] = useState<boolean>(false);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  // Trigger manual extraction if logo exists but palette not yet extracted
  const handleExtractFromLogo = async () => {
    if (!logos || logos.length === 0) return;
    setIsExtractingColors(true);
    try {
      const firstLogo = logos[0];
      const palette = await api.extractLogoColors(firstLogo.url);
      setExtractedPalette(palette);
      updateBrandField('primary_color', palette.primary);
      updateBrandField('secondary_color', palette.secondary);
      updateBrandField('accent_color', palette.accent);
      showMessage('Extracted brand colors from logo!');
    } catch (err) {
      console.error('Failed to extract logo colors:', err);
    } finally {
      setIsExtractingColors(false);
    }
  };

  const showMessage = (msg: string) => {
    setSuccessMessage(msg);
    setTimeout(() => setSuccessMessage(null), 3000);
  };

  // 1. Auto Match Logo Colours (One-click)
  const handleAutoMatch = async () => {
    if (!activeFooter) return;

    let palette = extractedPalette;
    if (!palette && logos.length > 0) {
      setIsExtractingColors(true);
      try {
        palette = await api.extractLogoColors(logos[0].url);
        setExtractedPalette(palette);
      } catch (err) {
        console.error('Extract error:', err);
      } finally {
        setIsExtractingColors(false);
      }
    }

    if (!palette || palette.schemes.length === 0) return;

    setIsApplying(true);
    try {
      const defaultScheme = palette.schemes[0];
      const updated = await api.applyLogoColors(activeFooter, defaultScheme);
      setActiveFooter(updated);
      setActiveSchemeId(defaultScheme.id);
      showMessage('Auto-matched logo colors applied!');
    } catch (err) {
      console.error('Failed to auto-match colors:', err);
    } finally {
      setIsApplying(false);
    }
  };

  // 2. Apply specific scheme
  const handleApplyScheme = async (scheme: ColorScheme) => {
    if (!activeFooter) return;
    setIsApplying(true);
    try {
      const updated = await api.applyLogoColors(activeFooter, scheme);
      setActiveFooter(updated);
      setActiveSchemeId(scheme.id);
      showMessage(`Applied ${scheme.name} theme!`);
    } catch (err) {
      console.error('Failed to apply scheme:', err);
    } finally {
      setIsApplying(false);
    }
  };

  // 3. Regenerate Colour Variations
  const handleRegenerateVariations = async () => {
    if (!activeFooter) return;
    setIsRegenerating(true);
    try {
      const logoUrl = logos.length > 0 ? logos[0].url : undefined;
      const variations = await api.generateLogoColorVariations(
        activeFooter,
        logoUrl,
        extractedPalette || undefined
      );
      if (variations.length > 0) {
        setFooterVariations(variations);
        showMessage('5 logo color variations generated in Carousel!');
      }
    } catch (err) {
      console.error('Failed to regenerate color variations:', err);
    } finally {
      setIsRegenerating(false);
    }
  };

  // Demo Fallback extractor
  const handleLoadDemoPalette = async () => {
    setIsExtractingColors(true);
    try {
      // Tech brand demo SVG logo
      const demoSvg = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">
        <rect fill="#2563eb" width="100" height="100" rx="20"/>
        <circle fill="#f59e0b" cx="50" cy="50" r="30"/>
        <path fill="#06b6d4" d="M30 70 L50 30 L70 70 Z"/>
      </svg>`;
      const palette = await api.extractLogoColors(demoSvg);
      setExtractedPalette(palette);
      updateBrandField('primary_color', palette.primary);
      updateBrandField('secondary_color', palette.secondary);
      updateBrandField('accent_color', palette.accent);
      showMessage('Loaded sample brand palette!');
    } catch (err) {
      console.error(err);
    } finally {
      setIsExtractingColors(false);
    }
  };

  const hasLogo = logos && logos.length > 0;

  return (
    <div className="space-y-3.5 pt-3 border-t border-slate-700/80">
      {/* Header */}
      <div className="flex items-center justify-between">
        <span className="text-[11px] font-semibold text-slate-300 flex items-center gap-1.5 uppercase tracking-wider">
          <Palette className="w-3.5 h-3.5 text-indigo-400" /> Logo Brand Colors
        </span>
        {isExtractingColors && (
          <span className="text-[10px] text-indigo-400 animate-pulse flex items-center gap-1">
            <RefreshCw className="w-3 h-3 animate-spin" /> Analyzing logo...
          </span>
        )}
      </div>

      {successMessage && (
        <div className="p-2 bg-emerald-950/70 border border-emerald-600/50 rounded text-[11px] text-emerald-300 flex items-center gap-1.5">
          <Check className="w-3.5 h-3.5 text-emerald-400 shrink-0" />
          <span>{successMessage}</span>
        </div>
      )}

      {/* When Palette is Available */}
      {extractedPalette ? (
        <div className="space-y-3">
          {/* Swatches Card */}
          <div className="p-2.5 bg-slate-900 rounded-lg border border-slate-700 space-y-2">
            <div className="flex items-center justify-between text-[10px] text-slate-400">
              <span>Extracted Palette</span>
              <span className="text-indigo-400 font-mono">WCAG 2.1 Compliant</span>
            </div>

            <div className="grid grid-cols-5 gap-1.5 text-center">
              <div>
                <div
                  className="w-full h-7 rounded border border-white/20 shadow-sm"
                  style={{ backgroundColor: extractedPalette.primary }}
                  title={`Primary: ${extractedPalette.primary}`}
                />
                <span className="text-[9px] text-slate-400 block mt-0.5 truncate font-mono">
                  {extractedPalette.primary}
                </span>
                <span className="text-[8px] text-slate-500 uppercase">Primary</span>
              </div>
              <div>
                <div
                  className="w-full h-7 rounded border border-white/20 shadow-sm"
                  style={{ backgroundColor: extractedPalette.secondary }}
                  title={`Secondary: ${extractedPalette.secondary}`}
                />
                <span className="text-[9px] text-slate-400 block mt-0.5 truncate font-mono">
                  {extractedPalette.secondary}
                </span>
                <span className="text-[8px] text-slate-500 uppercase">Secondary</span>
              </div>
              <div>
                <div
                  className="w-full h-7 rounded border border-white/20 shadow-sm"
                  style={{ backgroundColor: extractedPalette.accent }}
                  title={`Accent: ${extractedPalette.accent}`}
                />
                <span className="text-[9px] text-slate-400 block mt-0.5 truncate font-mono">
                  {extractedPalette.accent}
                </span>
                <span className="text-[8px] text-slate-500 uppercase">Accent</span>
              </div>
              <div>
                <div
                  className="w-full h-7 rounded border border-white/20 shadow-sm"
                  style={{ backgroundColor: extractedPalette.dark_shade }}
                  title={`Dark Shade: ${extractedPalette.dark_shade}`}
                />
                <span className="text-[9px] text-slate-400 block mt-0.5 truncate font-mono">
                  {extractedPalette.dark_shade}
                </span>
                <span className="text-[8px] text-slate-500 uppercase">Dark</span>
              </div>
              <div>
                <div
                  className="w-full h-7 rounded border border-white/20 shadow-sm"
                  style={{ backgroundColor: extractedPalette.light_shade }}
                  title={`Light Shade: ${extractedPalette.light_shade}`}
                />
                <span className="text-[9px] text-slate-400 block mt-0.5 truncate font-mono">
                  {extractedPalette.light_shade}
                </span>
                <span className="text-[8px] text-slate-500 uppercase">Light</span>
              </div>
            </div>
          </div>

          {/* Action Buttons: Auto Match & Regenerate */}
          <div className="grid grid-cols-2 gap-2">
            <button
              onClick={handleAutoMatch}
              disabled={isApplying || !activeFooter}
              className="py-1.5 px-2 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white rounded font-medium text-[11px] flex items-center justify-center gap-1.5 transition shadow-sm"
              title="Apply dominant brand colors to active footer"
            >
              <Wand2 className="w-3 h-3" /> Auto Match Logo
            </button>
            <button
              onClick={handleRegenerateVariations}
              disabled={isRegenerating || !activeFooter}
              className="py-1.5 px-2 bg-slate-700 hover:bg-slate-600 disabled:opacity-50 text-slate-200 rounded font-medium text-[11px] flex items-center justify-center gap-1.5 transition"
              title="Generate 5 color theme variations"
            >
              <RefreshCw className={`w-3 h-3 ${isRegenerating ? 'animate-spin' : ''}`} /> Regenerate
            </button>
          </div>

          {/* Color Schemes / Theme Pills */}
          <div className="space-y-1.5">
            <span className="text-[10px] text-slate-400 block">Select Theme Combination</span>
            <div className="grid grid-cols-1 gap-1.5">
              {extractedPalette.schemes.map((scheme) => (
                <button
                  key={scheme.id}
                  onClick={() => handleApplyScheme(scheme)}
                  disabled={isApplying || !activeFooter}
                  className={`p-2 rounded-lg border text-left transition flex items-center justify-between ${
                    activeSchemeId === scheme.id
                      ? 'bg-indigo-950/60 border-indigo-500/80 text-white shadow-sm'
                      : 'bg-slate-900 hover:bg-slate-800/80 border-slate-700/80 text-slate-300'
                  }`}
                >
                  <div className="flex items-center gap-2">
                    {/* Mini Swatches Preview */}
                    <div className="flex items-center -space-x-1.5 shrink-0">
                      <div
                        className="w-4 h-4 rounded-full border border-slate-900 shadow-sm"
                        style={{ backgroundColor: scheme.background }}
                      />
                      <div
                        className="w-4 h-4 rounded-full border border-slate-900 shadow-sm"
                        style={{ backgroundColor: scheme.secondary_color }}
                      />
                      <div
                        className="w-4 h-4 rounded-full border border-slate-900 shadow-sm"
                        style={{ backgroundColor: scheme.accent }}
                      />
                    </div>
                    <div>
                      <span className="text-[11px] font-semibold block leading-tight">
                        {scheme.name}
                      </span>
                      <span className="text-[9px] text-slate-400 block line-clamp-1">
                        {scheme.description}
                      </span>
                    </div>
                  </div>
                  {activeSchemeId === scheme.id && (
                    <Check className="w-3.5 h-3.5 text-indigo-400 shrink-0" />
                  )}
                </button>
              ))}
            </div>
          </div>
        </div>
      ) : (
        /* State when no logo is extracted yet */
        <div className="p-3 bg-slate-900/80 rounded-lg border border-slate-700 space-y-2.5">
          <div className="flex items-start gap-2">
            <AlertCircle className="w-4 h-4 text-amber-400 shrink-0 mt-0.5" />
            <p className="text-[11px] text-slate-400 leading-snug">
              {hasLogo
                ? 'Logo detected! Click below to extract dominant colors and create intelligent contrast themes.'
                : 'Upload a brand logo in the left panel to automatically extract dominant colors and apply intelligent, high-contrast themes.'}
            </p>
          </div>

          <div className="flex items-center gap-2 pt-1">
            {hasLogo ? (
              <button
                onClick={handleExtractFromLogo}
                disabled={isExtractingColors}
                className="w-full py-1.5 bg-indigo-600 hover:bg-indigo-500 text-white rounded text-[11px] font-medium flex items-center justify-center gap-1.5 transition"
              >
                <Sparkles className="w-3 h-3" /> Extract From Logo Now
              </button>
            ) : (
              <button
                onClick={handleLoadDemoPalette}
                disabled={isExtractingColors}
                className="w-full py-1.5 bg-slate-700/80 hover:bg-slate-700 text-slate-300 hover:text-white rounded text-[11px] font-medium flex items-center justify-center gap-1.5 transition"
              >
                <Pipette className="w-3 h-3 text-indigo-400" /> Try Sample Brand Palette
              </button>
            )}
          </div>
        </div>
      )}
    </div>
  );
};
