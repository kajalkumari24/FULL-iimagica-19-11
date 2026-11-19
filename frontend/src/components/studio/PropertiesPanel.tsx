import React, { useState } from 'react';
import {
  Wand2,
  CheckCircle2,
  AlertTriangle,
  Type,
  Maximize,
  Sliders,
  AlignLeft,
  AlignCenter,
  AlignRight,
  ShieldAlert,
} from 'lucide-react';
import { useEditorStore } from '../../store/editorStore';
import * as api from '../../api/client';
import { PositionOptionsSection } from './PositionOptionsSection';
import { LogoColorSection } from './LogoColorSection';

export const PropertiesPanel: React.FC = () => {
  const {
    activeFooter,
    selectedElementId,
    posterWidth,
    posterHeight,
    brand,
    setActiveFooter,
    updateActiveFooterElement,
    selectElement,
  } = useEditorStore();

  const [fixNotices, setFixNotices] = useState<string[]>([]);
  const [isValidating, setIsValidating] = useState(false);
  const [isFixing, setIsFixing] = useState(false);
  const [isRearranging, setIsRearranging] = useState(false);

  const handleArrangementChange = async (newArrangement: string) => {
    if (!activeFooter) return;
    setIsRearranging(true);
    try {
      const rearranged = await api.rearrangeFooter(
        activeFooter,
        newArrangement,
        brand,
        posterWidth,
        posterHeight
      );
      setActiveFooter(rearranged);
      setFixNotices([`Switched content arrangement to "${newArrangement.replace(/_/g, ' ')}"`]);
    } catch (err) {
      console.error('Rearrange error:', err);
    } finally {
      setIsRearranging(false);
    }
  };

  if (!activeFooter) {
    return (
      <div className="w-72 h-full bg-slate-800 border-l border-slate-700 p-6 flex flex-col items-center justify-center text-center text-slate-500">
        <Sliders className="w-12 h-12 mb-3 opacity-30 text-indigo-400" />
        <p className="text-sm font-medium text-slate-400">Properties Panel</p>
        <p className="text-xs text-slate-500 mt-1">Generate a footer to begin customizing properties</p>
      </div>
    );
  }

  // Find selected element if any
  const selectedElement = activeFooter.elements.find((el) => el.id === selectedElementId);

  // 1. Auto Fix All
  const handleAutoFix = async () => {
    setIsFixing(true);
    try {
      const res = await api.autoFix(activeFooter, posterWidth, posterHeight);
      setActiveFooter(res.footer);
      setFixNotices(res.changes);
    } catch (err) {
      console.error('Auto fix error:', err);
    } finally {
      setIsFixing(false);
    }
  };

  // 2. Validate Layout
  const handleValidate = async () => {
    setIsValidating(true);
    try {
      const res = await api.validateFooter(activeFooter);
      setActiveFooter({
        ...activeFooter,
        quality_score: res.quality_score,
        validation_notices: res.notices,
      });
      setFixNotices(res.notices.length > 0 ? res.notices : ['Layout is clean, balanced and compliant!']);
    } catch (err) {
      console.error('Validation error:', err);
    } finally {
      setIsValidating(false);
    }
  };

  return (
    <div className="w-72 h-full bg-slate-800 border-l border-slate-700 flex flex-col text-slate-200 select-none overflow-hidden">
      {/* Panel Header */}
      <div className="p-4 border-b border-slate-700 flex items-center justify-between">
        <h3 className="font-semibold text-xs tracking-wider uppercase text-slate-300">
          {selectedElement ? 'Element Properties' : 'Footer Properties'}
        </h3>
        {selectedElement && (
          <button
            onClick={() => selectElement(null)}
            className="text-[11px] text-indigo-400 hover:text-indigo-300"
          >
            Deselect
          </button>
        )}
      </div>

      {/* Main Controls */}
      <div className="flex-1 overflow-y-auto p-4 space-y-5 custom-scrollbar text-xs">
        {selectedElement ? (
          /* Selected Element Controls */
          <div className="space-y-4">
            <div className="p-2.5 bg-slate-900 rounded border border-slate-700">
              <span className="text-[10px] text-slate-500 block">ID: {selectedElement.id}</span>
              <span className="text-xs font-semibold text-indigo-300 capitalize">{selectedElement.type} Element</span>
            </div>

            {/* Text Content */}
            {(selectedElement.type === 'text' || selectedElement.type === 'icon_text' || selectedElement.type === 'badge') && (
              <div>
                <label className="text-[11px] text-slate-400 block mb-1">Text Content</label>
                <input
                  type="text"
                  value={selectedElement.text || ''}
                  onChange={(e) => updateActiveFooterElement(selectedElement.id, { text: e.target.value })}
                  className="w-full bg-slate-900 border border-slate-700 rounded px-2.5 py-1.5 text-slate-100"
                />
              </div>
            )}

            {/* Typography Controls */}
            {selectedElement.style && (
              <div className="space-y-3 pt-2 border-t border-slate-700/60">
                <span className="text-[11px] font-semibold text-slate-400 flex items-center gap-1.5">
                  <Type className="w-3.5 h-3.5 text-indigo-400" /> Typography
                </span>

                <div>
                  <label className="text-[10px] text-slate-400 block mb-1">Font Family</label>
                  <select
                    value={selectedElement.style.font_family || 'Inter'}
                    onChange={(e) =>
                      updateActiveFooterElement(selectedElement.id, {
                        style: { ...selectedElement.style, font_family: e.target.value },
                      })
                    }
                    className="w-full bg-slate-900 border border-slate-700 rounded px-2 py-1 text-slate-200"
                  >
                    <option value="Inter">Inter (Modern Clean)</option>
                    <option value="Montserrat">Montserrat (Corporate)</option>
                    <option value="Oswald">Oswald (Bold Impact)</option>
                    <option value="Playfair Display">Playfair Display (Luxury)</option>
                    <option value="Roboto">Roboto (Standard)</option>
                  </select>
                </div>

                <div className="grid grid-cols-2 gap-2">
                  <div>
                    <label className="text-[10px] text-slate-400 block mb-1">
                      Font Size ({Math.round(selectedElement.style.font_size || 14)}px)
                    </label>
                    <input
                      type="range"
                      min={9}
                      max={48}
                      value={selectedElement.style.font_size || 14}
                      onChange={(e) =>
                        updateActiveFooterElement(selectedElement.id, {
                          style: { ...selectedElement.style, font_size: parseFloat(e.target.value) },
                        })
                      }
                      className="w-full"
                    />
                  </div>
                  <div>
                    <label className="text-[10px] text-slate-400 block mb-1">Color</label>
                    <input
                      type="color"
                      value={selectedElement.style.color || '#ffffff'}
                      onChange={(e) =>
                        updateActiveFooterElement(selectedElement.id, {
                          style: { ...selectedElement.style, color: e.target.value },
                        })
                      }
                      className="w-full h-7 bg-slate-900 border border-slate-700 rounded cursor-pointer"
                    />
                  </div>
                </div>
              </div>
            )}
          </div>
        ) : (
          /* Overall Footer Controls */
          <div className="space-y-4">
            <div className="p-3 bg-slate-900 rounded border border-slate-700">
              <div className="flex items-center justify-between mb-1">
                <span className="text-[11px] text-slate-400">Layout Quality</span>
                <span className="text-xs font-bold text-emerald-400">{activeFooter.quality_score}%</span>
              </div>
              <div className="w-full bg-slate-800 h-1.5 rounded-full overflow-hidden">
                <div
                  className="bg-emerald-500 h-full rounded-full transition-all"
                  style={{ width: `${activeFooter.quality_score}%` }}
                />
              </div>
            </div>

            {/* Automatic Position & Layout Options Section */}
            <PositionOptionsSection mode="panel" />

            {/* Shape Selector */}
            <div>
              <label className="text-[11px] text-slate-400 block mb-1">Shape Style</label>
              <select
                value={activeFooter.background.shape}
                onChange={(e) => {
                  const updatedBg = { ...activeFooter.background, shape: e.target.value };
                  setActiveFooter({ ...activeFooter, background: updatedBg });
                }}
                className="w-full bg-slate-900 border border-slate-700 rounded px-2.5 py-1.5 text-slate-200"
              >
                <option value="classic_rectangle">Classic Rectangle</option>
                <option value="rounded_box">Rounded Box</option>
                <option value="fluid_wave_single">Fluid Wave Single</option>
                <option value="fluid_wave_double">Dual Layer Wave</option>
                <option value="convex_curve">Convex Dome Top</option>
                <option value="concave_curve">Concave Dip Top</option>
                <option value="diagonal_bevel">Diagonal Bevel</option>
                <option value="diagonal_reverse">Reverse Diagonal</option>
                <option value="executive_ribbon">Executive Ribbon</option>
                <option value="floating_capsule">Floating Inset Capsule</option>
                <option value="floating_card">Elevated Floating Card</option>
                <option value="double_layer_offset">Layered Offset Shadow</option>
                <option value="split_banner">Vertical Split Duo</option>
                <option value="split_angled">Angled Split Matrix</option>
                <option value="arch_dome">Cathedral Arch Top</option>
                <option value="center_notch">Hero Badge Tab</option>
                <option value="accent_bar_minimal">Neon Accent Minimal</option>
                <option value="frosted_glass">Frosted Glass Luxe</option>
              </select>
            </div>

            {/* Background Color & Opacity */}
            <div className="grid grid-cols-2 gap-2">
              <div>
                <label className="text-[10px] text-slate-400 block mb-1">Background</label>
                <input
                  type="color"
                  value={activeFooter.background.color || '#0f172a'}
                  onChange={(e) => {
                    const updatedBg = { ...activeFooter.background, color: e.target.value };
                    setActiveFooter({ ...activeFooter, background: updatedBg });
                  }}
                  className="w-full h-8 bg-slate-900 border border-slate-700 rounded cursor-pointer"
                />
              </div>
              <div>
                <label className="text-[10px] text-slate-400 block mb-1">
                  Opacity ({Math.round((activeFooter.background.opacity || 1) * 100)}%)
                </label>
                <input
                  type="range"
                  min={0.2}
                  max={1.0}
                  step={0.05}
                  value={activeFooter.background.opacity || 1}
                  onChange={(e) => {
                    const updatedBg = { ...activeFooter.background, opacity: parseFloat(e.target.value) };
                    setActiveFooter({ ...activeFooter, background: updatedBg });
                  }}
                  className="w-full mt-2"
                />
              </div>
            </div>

            {/* Logo Brand Colors & Extraction Engine */}
            <LogoColorSection />
          </div>
        )}

        {/* Notices & Alerts */}
        {fixNotices.length > 0 && (
          <div className="p-3 bg-slate-900/90 border border-slate-700 rounded-lg space-y-1.5">
            <span className="text-[11px] font-semibold text-slate-300 flex items-center gap-1.5">
              <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" /> Layout Diagnostics
            </span>
            {fixNotices.map((n, i) => (
              <p key={i} className="text-[11px] text-slate-400 leading-tight">
                • {n}
              </p>
            ))}
          </div>
        )}
      </div>

      {/* Action Buttons: Auto Fix & Validate */}
      <div className="p-4 border-t border-slate-700 space-y-2 bg-slate-800/90">
        <button
          onClick={handleAutoFix}
          disabled={isFixing}
          className="w-full py-2 bg-indigo-600/30 hover:bg-indigo-600/40 text-indigo-300 hover:text-white border border-indigo-500/50 rounded-lg flex items-center justify-center gap-2 font-medium transition"
        >
          <Wand2 className="w-3.5 h-3.5 text-indigo-400" /> Auto Adjust (Fix Fonts, Overflows & Spacing)
        </button>
        <button
          onClick={handleValidate}
          disabled={isValidating}
          className="w-full py-2 bg-slate-700/60 hover:bg-slate-700 text-slate-300 hover:text-white border border-slate-600 rounded-lg flex items-center justify-center gap-2 font-medium transition"
        >
          <ShieldAlert className="w-3.5 h-3.5 text-emerald-400" /> Validate Layout & Contrast
        </button>
      </div>
    </div>
  );
};
