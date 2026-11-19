import React, { useEffect, useState } from 'react';
import { LayoutTemplate, Sparkles, ArrowRight, Wand2, CheckCircle2, AlertTriangle, ShieldCheck } from 'lucide-react';
import { useEditorStore } from '../store/editorStore';
import * as api from '../api/client';
import type { AdaptiveTemplateSpec, RepairSvgResult } from '../types';

const TemplatePage: React.FC = () => {
  const { setCurrentPage, posterWidth, posterHeight, brand, setFooterVariations, selectFooter, setIsGenerating } = useEditorStore();
  const [templates, setTemplates] = useState<AdaptiveTemplateSpec[]>([]);
  const [activeCategory, setActiveCategory] = useState<string>('all');

  // SVG Repair Inspector State
  const [svgInput, setSvgInput] = useState('');
  const [repairResult, setRepairResult] = useState<RepairSvgResult | null>(null);
  const [isRepairing, setIsRepairing] = useState(false);

  useEffect(() => {
    api.listTemplates()
      .then(setTemplates)
      .catch((err) => console.error('Failed to load templates:', err));
  }, []);

  // Requested Category Filters: Wave, Curved, Modern, Geometric, Minimal, Corporate
  const categories = ['all', 'wave', 'curved', 'modern', 'geometric', 'minimal', 'corporate'];

  const filteredTemplates = activeCategory === 'all'
    ? templates
    : templates.filter((t) => t.category.toLowerCase() === activeCategory.toLowerCase());

  const handleApplyTemplate = async (tmpl: AdaptiveTemplateSpec) => {
    setIsGenerating(true);
    try {
      const vars = await api.generateFooters({
        poster_width: posterWidth,
        poster_height: posterHeight,
        brand,
        style_preference: tmpl.category,
      });

      // Find the specific variation matching this template
      const matchedIdx = vars.findIndex((v) => v.name.toLowerCase() === tmpl.name.toLowerCase());
      setFooterVariations(vars);
      selectFooter(matchedIdx >= 0 ? matchedIdx : 0);
      setCurrentPage('studio');
    } catch (err) {
      console.error(err);
      setCurrentPage('studio');
    } finally {
      setIsGenerating(false);
    }
  };

  const handleRepairTest = async () => {
    if (!svgInput.trim()) return;
    setIsRepairing(true);
    try {
      const res = await api.repairSvg(svgInput, posterWidth, 160);
      setRepairResult(res);
    } catch (err) {
      console.error('Repair error:', err);
    } finally {
      setIsRepairing(false);
    }
  };

  // Helper to render live responsive SVG thumbnail preview for every design
  const renderThumbnailSvg = (tmpl: AdaptiveTemplateSpec) => {
    const bg = tmpl.default_bg_color || '#0f172a';
    const sec = tmpl.default_secondary_color || '#1e293b';
    const acc = tmpl.default_accent_color || '#f59e0b';
    const shape = tmpl.shape_key.toLowerCase();

    let pathMarkup = `<rect width="360" height="90" fill="${bg}"/>`;

    if (shape.includes('wave')) {
      if (shape.includes('triple')) {
        pathMarkup = `
          <path d="M 0,16 Q 100,0 200,16 T 360,8 L 360,90 L 0,90 Z" fill="${acc}" opacity="0.3"/>
          <path d="M 0,24 Q 120,4 240,24 T 360,12 L 360,90 L 0,90 Z" fill="${sec}" opacity="0.6"/>
          <path d="M 0,32 Q 90,8 180,28 T 360,16 L 360,90 L 0,90 Z" fill="${bg}"/>
        `;
      } else if (shape.includes('double')) {
        pathMarkup = `
          <path d="M 0,18 Q 110,2 220,20 T 360,10 L 360,90 L 0,90 Z" fill="${sec}" opacity="0.5"/>
          <path d="M 0,26 Q 90,6 180,24 T 360,14 L 360,90 L 0,90 Z" fill="${bg}"/>
        `;
      } else if (shape.includes('gradient')) {
        pathMarkup = `
          <defs>
            <linearGradient id="thm_grad_${tmpl.id}" x1="0" y1="0" x2="1" y2="1">
              <stop offset="0%" stop-color="${bg}"/>
              <stop offset="60%" stop-color="${sec}"/>
              <stop offset="100%" stop-color="${acc}"/>
            </linearGradient>
          </defs>
          <path d="M 0,22 Q 90,4 180,22 T 360,12 L 360,90 L 0,90 Z" fill="url(#thm_grad_${tmpl.id})"/>
        `;
      } else {
        pathMarkup = `<path d="M 0,24 Q 90,4 180,22 T 360,14 L 360,90 L 0,90 Z" fill="${bg}"/>`;
      }
    } else if (shape.includes('convex')) {
      pathMarkup = `<path d="M 0,22 Q 180,0 360,22 L 360,90 L 0,90 Z" fill="${bg}"/>`;
    } else if (shape.includes('concave')) {
      pathMarkup = `<path d="M 0,0 Q 180,22 360,0 L 360,90 L 0,90 Z" fill="${bg}"/>`;
    } else if (shape.includes('arch')) {
      pathMarkup = `<path d="M 0,22 A 22 22 0 0 1 22,0 L 338,0 A 22 22 0 0 1 360,22 L 360,90 L 0,90 Z" fill="${bg}"/>`;
    } else if (shape.includes('diagonal') || shape.includes('bevel') || shape.includes('angle')) {
      pathMarkup = `
        <polygon points="0,26 360,0 360,90 0,90" fill="${bg}"/>
        <line x1="0" y1="26" x2="360" y2="0" stroke="${acc}" stroke-width="2.5"/>
      `;
    } else if (shape.includes('zigzag')) {
      pathMarkup = `
        <polygon points="0,12 30,0 60,12 90,0 120,12 150,0 180,12 210,0 240,12 270,0 300,12 330,0 360,12 360,90 0,90" fill="${bg}"/>
      `;
    } else if (shape.includes('capsule') || shape.includes('rounded')) {
      pathMarkup = `<rect x="6" y="8" width="348" height="74" rx="28" fill="${bg}" stroke="${sec}" stroke-width="1.5"/>`;
    } else if (shape.includes('ribbon')) {
      pathMarkup = `
        <rect x="0" y="0" width="360" height="6" fill="${acc}"/>
        <rect x="0" y="6" width="360" height="84" fill="${bg}"/>
      `;
    } else if (shape.includes('split')) {
      pathMarkup = `
        <rect x="0" y="0" width="120" height="90" fill="${sec}"/>
        <rect x="120" y="0" width="240" height="90" fill="${bg}"/>
        <line x1="120" y1="0" x2="120" y2="90" stroke="${acc}" stroke-width="2"/>
      `;
    } else if (shape.includes('glass') || shape.includes('frosted')) {
      pathMarkup = `<rect x="8" y="8" width="344" height="74" rx="12" fill="${bg}" opacity="0.85" stroke="rgba(255,255,255,0.3)" stroke-width="1.5"/>`;
    }

    const arr = (tmpl.arrangement || 'classic_horizontal').toLowerCase();
    let contentMarkup = '';

    if (arr === 'centred') {
      contentMarkup = `
        <circle cx="180" cy="30" r="12" fill="#ffffff" opacity="0.9"/>
        <rect x="130" y="47" width="100" height="7" rx="3" fill="#ffffff" opacity="0.95"/>
        <rect x="145" y="58" width="70" height="5" rx="2" fill="${acc}" opacity="0.85"/>
        <rect x="100" y="70" width="45" height="5" rx="2" fill="#cbd5e1" opacity="0.7"/>
        <rect x="155" y="70" width="50" height="5" rx="2" fill="#cbd5e1" opacity="0.7"/>
        <rect x="215" y="70" width="45" height="5" rx="2" fill="#cbd5e1" opacity="0.7"/>
      `;
    } else if (arr === 'logo_centre') {
      contentMarkup = `
        <rect x="25" y="44" width="90" height="7" rx="3" fill="#ffffff" opacity="0.9"/>
        <rect x="25" y="56" width="65" height="5" rx="2" fill="${acc}" opacity="0.8"/>
        <rect x="25" y="66" width="75" height="5" rx="2" fill="#94a3b8" opacity="0.7"/>
        <circle cx="180" cy="50" r="18" fill="#ffffff" opacity="0.95"/>
        <rect x="245" y="44" width="85" height="6" rx="3" fill="#cbd5e1" opacity="0.85"/>
        <rect x="245" y="54" width="75" height="6" rx="3" fill="#cbd5e1" opacity="0.85"/>
        <rect x="245" y="64" width="65" height="6" rx="3" fill="#94a3b8" opacity="0.7"/>
      `;
    } else if (arr === 'profile_focused') {
      contentMarkup = `
        <circle cx="40" cy="50" r="22" fill="#ffffff" stroke="${acc}" stroke-width="2.5" opacity="0.95"/>
        <rect x="75" y="38" width="95" height="8" rx="3" fill="#ffffff" opacity="0.95"/>
        <rect x="75" y="50" width="75" height="6" rx="2" fill="${acc}" opacity="0.85"/>
        <rect x="75" y="60" width="60" height="14" rx="4" fill="${acc}"/>
        <rect x="210" y="42" width="120" height="6" rx="3" fill="#cbd5e1" opacity="0.85"/>
        <rect x="210" y="52" width="105" height="6" rx="3" fill="#cbd5e1" opacity="0.85"/>
        <rect x="210" y="62" width="90" height="6" rx="3" fill="#94a3b8" opacity="0.7"/>
      `;
    } else if (arr === 'profile_circle') {
      contentMarkup = `
        <rect x="25" y="46" width="85" height="7" rx="3" fill="#ffffff" opacity="0.9"/>
        <rect x="25" y="58" width="65" height="5" rx="2" fill="${acc}" opacity="0.8"/>
        <circle cx="180" cy="50" r="22" fill="#ffffff" stroke="${acc}" stroke-width="2" opacity="0.95"/>
        <rect x="245" y="44" width="85" height="6" rx="3" fill="#cbd5e1" opacity="0.85"/>
        <rect x="245" y="54" width="75" height="6" rx="3" fill="#cbd5e1" opacity="0.85"/>
        <rect x="245" y="64" width="60" height="6" rx="3" fill="#94a3b8" opacity="0.7"/>
      `;
    } else if (arr === 'vertical_stacked') {
      contentMarkup = `
        <circle cx="35" cy="32" r="10" fill="#ffffff" opacity="0.85"/>
        <rect x="52" y="28" width="120" height="7" rx="3" fill="#ffffff" opacity="0.9"/>
        <rect x="52" y="38" width="80" height="5" rx="2" fill="${acc}" opacity="0.8"/>
        <line x1="20" y1="56" x2="340" y2="56" stroke="rgba(255,255,255,0.15)" stroke-width="1"/>
        <rect x="25" y="66" width="65" height="6" rx="3" fill="#cbd5e1" opacity="0.85"/>
        <rect x="105" y="66" width="70" height="6" rx="3" fill="#cbd5e1" opacity="0.85"/>
        <rect x="190" y="66" width="75" height="6" rx="3" fill="#cbd5e1" opacity="0.85"/>
        <rect x="280" y="66" width="55" height="6" rx="3" fill="${acc}" opacity="0.85"/>
      `;
    } else if (arr === 'four_column') {
      contentMarkup = `
        <rect x="20" y="40" width="65" height="8" rx="3" fill="#ffffff" opacity="0.9"/>
        <rect x="20" y="52" width="50" height="5" rx="2" fill="${acc}" opacity="0.8"/>
        <rect x="100" y="40" width="65" height="6" rx="3" fill="#cbd5e1" opacity="0.85"/>
        <rect x="100" y="50" width="55" height="6" rx="3" fill="#cbd5e1" opacity="0.85"/>
        <rect x="180" y="40" width="65" height="6" rx="3" fill="#cbd5e1" opacity="0.85"/>
        <rect x="180" y="50" width="55" height="6" rx="3" fill="#cbd5e1" opacity="0.85"/>
        <rect x="260" y="40" width="60" height="6" rx="3" fill="${acc}" opacity="0.85"/>
        <rect x="305" y="48" width="28" height="28" rx="3" fill="#ffffff"/>
      `;
    } else if (arr === 'contact_card') {
      contentMarkup = `
        <circle cx="35" cy="50" r="14" fill="#ffffff" opacity="0.9"/>
        <rect x="58" y="42" width="70" height="7" rx="3" fill="#ffffff" opacity="0.9"/>
        <rect x="58" y="53" width="50" height="5" rx="2" fill="${acc}" opacity="0.8"/>
        <rect x="145" y="38" width="90" height="18" rx="5" fill="${sec}" stroke="rgba(255,255,255,0.2)"/>
        <rect x="155" y="44" width="70" height="6" rx="2" fill="#ffffff" opacity="0.85"/>
        <rect x="145" y="60" width="90" height="18" rx="5" fill="${sec}" stroke="rgba(255,255,255,0.2)"/>
        <rect x="155" y="66" width="70" height="6" rx="2" fill="#ffffff" opacity="0.85"/>
        <rect x="245" y="38" width="90" height="18" rx="5" fill="${sec}" stroke="rgba(255,255,255,0.2)"/>
        <rect x="255" y="44" width="70" height="6" rx="2" fill="#ffffff" opacity="0.85"/>
        <rect x="245" y="60" width="90" height="18" rx="5" fill="${acc}"/>
        <rect x="255" y="66" width="70" height="6" rx="2" fill="#000000" opacity="0.8"/>
      `;
    } else if (arr === 'social_bottom') {
      contentMarkup = `
        <circle cx="35" cy="38" r="12" fill="#ffffff" opacity="0.9"/>
        <rect x="55" y="34" width="80" height="7" rx="3" fill="#ffffff" opacity="0.9"/>
        <rect x="180" y="34" width="75" height="6" rx="3" fill="#cbd5e1" opacity="0.85"/>
        <rect x="270" y="34" width="65" height="6" rx="3" fill="#cbd5e1" opacity="0.85"/>
        <rect x="0" y="62" width="360" height="28" fill="${sec}" opacity="0.9"/>
        <circle cx="45" cy="76" r="6" fill="${acc}"/>
        <circle cx="75" cy="76" r="6" fill="${acc}"/>
        <circle cx="105" cy="76" r="6" fill="${acc}"/>
        <rect x="140" y="73" width="180" height="6" rx="3" fill="#ffffff" opacity="0.8"/>
      `;
    } else if (arr === 'qr_focused') {
      contentMarkup = `
        <circle cx="35" cy="50" r="14" fill="#ffffff" opacity="0.9"/>
        <rect x="58" y="42" width="90" height="7" rx="3" fill="#ffffff" opacity="0.9"/>
        <rect x="58" y="53" width="70" height="5" rx="2" fill="${acc}" opacity="0.8"/>
        <rect x="58" y="63" width="110" height="5" rx="2" fill="#cbd5e1" opacity="0.7"/>
        <rect x="285" y="30" width="48" height="48" rx="6" fill="#ffffff" stroke="${acc}" stroke-width="2"/>
        <rect x="291" y="36" width="36" height="36" rx="3" fill="#09090b"/>
      `;
    } else if (arr === 'split_panel') {
      contentMarkup = `
        <rect x="10" y="24" width="105" height="54" rx="6" fill="${sec}" stroke="rgba(255,255,255,0.15)"/>
        <circle cx="32" cy="45" r="10" fill="#ffffff" opacity="0.9"/>
        <rect x="48" y="42" width="55" height="6" rx="2" fill="#ffffff"/>
        <rect x="130" y="36" width="105" height="6" rx="3" fill="#cbd5e1" opacity="0.85"/>
        <rect x="130" y="48" width="95" height="6" rx="3" fill="#cbd5e1" opacity="0.85"/>
        <rect x="130" y="60" width="85" height="6" rx="3" fill="#cbd5e1" opacity="0.85"/>
        <rect x="260" y="42" width="70" height="22" rx="4" fill="${acc}"/>
      `;
    } else if (arr === 'vertical_sidebar') {
      contentMarkup = `
        <rect x="0" y="0" width="85" height="90" fill="${sec}" opacity="0.95"/>
        <circle cx="42" cy="34" r="14" fill="#ffffff" opacity="0.9"/>
        <rect x="15" y="56" width="55" height="6" rx="2" fill="#ffffff"/>
        <rect x="105" y="36" width="100" height="6" rx="3" fill="#cbd5e1" opacity="0.85"/>
        <rect x="105" y="48" width="90" height="6" rx="3" fill="#cbd5e1" opacity="0.85"/>
        <rect x="105" y="60" width="80" height="6" rx="3" fill="#cbd5e1" opacity="0.85"/>
        <rect x="230" y="36" width="95" height="6" rx="3" fill="#cbd5e1" opacity="0.85"/>
        <rect x="230" y="48" width="85" height="6" rx="3" fill="#cbd5e1" opacity="0.85"/>
      `;
    } else if (arr === 'floating_elements') {
      contentMarkup = `
        <rect x="14" y="28" width="95" height="46" rx="8" fill="${sec}" stroke="rgba(255,255,255,0.2)"/>
        <circle cx="34" cy="51" r="10" fill="#ffffff" opacity="0.9"/>
        <rect x="50" y="48" width="48" height="6" rx="2" fill="#ffffff"/>
        <rect x="120" y="28" width="115" height="46" rx="8" fill="${sec}" stroke="rgba(255,255,255,0.2)"/>
        <rect x="130" y="40" width="85" height="5" rx="2" fill="#cbd5e1"/>
        <rect x="130" y="52" width="75" height="5" rx="2" fill="#cbd5e1"/>
        <rect x="246" y="28" width="95" height="46" rx="8" fill="${sec}" stroke="rgba(255,255,255,0.2)"/>
        <rect x="278" y="36" width="30" height="30" rx="4" fill="#ffffff"/>
      `;
    } else if (arr === 'asymmetric') {
      contentMarkup = `
        <rect x="25" y="32" width="135" height="10" rx="3" fill="#ffffff" opacity="0.95"/>
        <rect x="25" y="46" width="100" height="6" rx="2" fill="${acc}" opacity="0.85"/>
        <rect x="25" y="58" width="75" height="16" rx="4" fill="${acc}"/>
        <rect x="195" y="36" width="135" height="6" rx="3" fill="#cbd5e1" opacity="0.85"/>
        <rect x="195" y="48" width="120" height="6" rx="3" fill="#cbd5e1" opacity="0.85"/>
        <rect x="195" y="60" width="105" height="6" rx="3" fill="#cbd5e1" opacity="0.85"/>
      `;
    } else if (arr === 'compact') {
      contentMarkup = `
        <circle cx="28" cy="52" r="10" fill="#ffffff" opacity="0.9"/>
        <rect x="46" y="48" width="60" height="8" rx="2" fill="#ffffff"/>
        <circle cx="118" cy="52" r="2" fill="${acc}"/>
        <rect x="128" y="49" width="65" height="6" rx="2" fill="#cbd5e1"/>
        <circle cx="203" cy="52" r="2" fill="${acc}"/>
        <rect x="213" y="49" width="65" height="6" rx="2" fill="#cbd5e1"/>
        <rect x="298" y="41" width="24" height="24" rx="3" fill="#ffffff"/>
      `;
    } else if (arr === 'two_column') {
      contentMarkup = `
        <circle cx="32" cy="44" r="12" fill="#ffffff" opacity="0.9"/>
        <rect x="52" y="38" width="95" height="7" rx="3" fill="#ffffff" opacity="0.9"/>
        <rect x="52" y="49" width="70" height="5" rx="2" fill="${acc}" opacity="0.8"/>
        <rect x="32" y="62" width="60" height="14" rx="4" fill="${acc}"/>
        <rect x="190" y="38" width="130" height="6" rx="3" fill="#cbd5e1" opacity="0.85"/>
        <rect x="190" y="48" width="115" height="6" rx="3" fill="#cbd5e1" opacity="0.85"/>
        <rect x="190" y="58" width="100" height="6" rx="3" fill="#cbd5e1" opacity="0.85"/>
      `;
    } else {
      // Classic Horizontal / Three-Column default
      contentMarkup = `
        <circle cx="28" cy="54" r="14" fill="#ffffff" opacity="0.85" />
        <rect x="52" y="44" width="75" height="7" rx="3" fill="#ffffff" opacity="0.9" />
        <rect x="52" y="56" width="55" height="5" rx="2" fill="#94a3b8" opacity="0.7" />
        <rect x="160" y="46" width="85" height="6" rx="3" fill="#cbd5e1" opacity="0.85" />
        <rect x="160" y="57" width="70" height="5" rx="2.5" fill="#94a3b8" opacity="0.7" />
        <rect x="278" y="44" width="62" height="18" rx="6" fill="${acc}" />
        <rect x="288" y="50" width="42" height="5" rx="2" fill="#000000" opacity="0.8" />
      `;
    }

    return (
      <svg
        viewBox="0 0 360 90"
        className="w-full h-20 rounded-lg overflow-hidden bg-slate-950 border border-slate-700/80 shadow-inner"
      >
        <g dangerouslySetInnerHTML={{ __html: pathMarkup }} />
        <g dangerouslySetInnerHTML={{ __html: contentMarkup }} />
      </svg>
    );
  };

  return (
    <div className="h-full w-full bg-slate-900 p-8 overflow-y-auto text-slate-100 select-none">
      <div className="max-w-6xl mx-auto space-y-8">
        {/* Header */}
        <div className="border-b border-slate-800 pb-5 flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-white flex items-center gap-2.5">
              <LayoutTemplate className="w-6 h-6 text-indigo-400" /> Adaptive Template Registry
            </h1>
            <p className="text-xs text-slate-400 mt-1">
              48 mathematically responsive base shape templates (18 core + 30 new wave, curved, geometric & modern styles). Each dynamically recalculates curve amplitudes, padding, and column counts.
            </p>
          </div>
          <span className="text-xs px-3 py-1 bg-indigo-900/60 text-indigo-300 border border-indigo-700 rounded-full font-mono font-medium">
            {templates.length} Active Templates
          </span>
        </div>

        {/* Category Pills */}
        <div className="flex items-center gap-2 overflow-x-auto pb-1">
          {categories.map((cat) => (
            <button
              key={cat}
              onClick={() => setActiveCategory(cat)}
              className={`px-3.5 py-1.5 rounded-lg text-xs font-semibold capitalize transition ${activeCategory.toLowerCase() === cat.toLowerCase()
                  ? 'bg-indigo-600 text-white shadow-md shadow-indigo-600/30 ring-1 ring-indigo-400'
                  : 'bg-slate-800 hover:bg-slate-700 text-slate-400 hover:text-slate-200 border border-slate-700/80'
                }`}
            >
              {cat}
            </button>
          ))}
        </div>

        {/* Templates Grid with Real SVG Previews */}
        <div className="grid grid-cols-3 gap-5">
          {filteredTemplates.map((tmpl) => (
            <div
              key={tmpl.id}
              onClick={() => handleApplyTemplate(tmpl)}
              className="p-4 rounded-xl bg-slate-800/90 border border-slate-700 hover:border-indigo-500/60 hover:shadow-xl hover:shadow-indigo-500/10 cursor-pointer transition space-y-3.5 flex flex-col justify-between group"
            >
              <div className="space-y-3">
                {/* Real SVG Design Preview Thumbnail */}
                {renderThumbnailSvg(tmpl)}

                <div className="flex items-start justify-between pt-1">
                  <h3 className="font-semibold text-sm text-white group-hover:text-indigo-300 transition">{tmpl.name}</h3>
                  <div className="flex flex-col items-end gap-1">
                    <span className="text-[9px] uppercase font-mono px-2 py-0.5 rounded bg-slate-900 text-indigo-300 border border-slate-700">
                      {tmpl.category}
                    </span>
                    {tmpl.arrangement && (
                      <span className="text-[8px] capitalize font-mono px-1.5 py-0.5 rounded bg-cyan-950 text-cyan-300 border border-cyan-800">
                        {tmpl.arrangement.replace(/_/g, ' ')}
                      </span>
                    )}
                  </div>
                </div>
                <p className="text-xs text-slate-400 leading-relaxed min-h-[34px] line-clamp-2">{tmpl.description}</p>
              </div>

              {/* Color & Typography Specs */}
              <div className="pt-2.5 border-t border-slate-700/60 flex items-center justify-between">
                <div className="flex items-center gap-1.5">
                  {[tmpl.default_bg_color, tmpl.default_secondary_color, tmpl.default_accent_color].map((c, i) => (
                    <span
                      key={i}
                      className="w-4 h-4 rounded-full border border-slate-600 shadow-sm"
                      style={{ backgroundColor: c }}
                      title={c}
                    />
                  ))}
                </div>
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    handleApplyTemplate(tmpl);
                  }}
                  className="px-3 py-1 bg-indigo-600/80 hover:bg-indigo-600 text-white rounded text-xs font-medium flex items-center gap-1 transition"
                >
                  Apply & Edit <ArrowRight className="w-3 h-3" />
                </button>
              </div>
            </div>
          ))}
        </div>

        {/* SVG Repair Lab Section */}
        <div className="border border-slate-700/80 rounded-xl bg-slate-800/50 p-6 space-y-4">
          <div className="flex items-center justify-between border-b border-slate-700/60 pb-3">
            <div>
              <h2 className="text-base font-semibold text-white flex items-center gap-2">
                <Wand2 className="w-4 h-4 text-indigo-400" /> SVG Repair & Compliance Lab
              </h2>
              <p className="text-xs text-slate-400 mt-0.5">
                Paste any external SVG to inspect viewBox scaling, remove script hazards, and ensure aspect ratio compliance.
              </p>
            </div>
            <span className="text-xs bg-slate-700/60 px-2.5 py-1 rounded text-slate-300 flex items-center gap-1">
              <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" /> XML Defused Parser
            </span>
          </div>

          <div className="space-y-3">
            <textarea
              rows={4}
              value={svgInput}
              onChange={(e) => setSvgInput(e.target.value)}
              placeholder="<svg ...> Paste raw SVG code here to test repair and sanitization...</svg>"
              className="w-full bg-slate-900 border border-slate-700 rounded-lg p-3 text-xs font-mono text-slate-200 focus:outline-none focus:border-indigo-500"
            />
            <div className="flex justify-end">
              <button
                onClick={handleRepairTest}
                disabled={isRepairing || !svgInput.trim()}
                className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-40 text-xs font-semibold rounded-lg flex items-center gap-2 text-white transition shadow-md shadow-indigo-600/20"
              >
                {isRepairing ? 'Inspecting...' : 'Sanitize & Test Repair'}
              </button>
            </div>
          </div>

          {repairResult && (
            <div className="p-4 rounded-lg bg-slate-900/90 border border-slate-700 space-y-3 text-xs">
              <div className="flex items-center justify-between">
                <span className="font-semibold flex items-center gap-1.5">
                  {repairResult.is_valid ? (
                    <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                  ) : (
                    <AlertTriangle className="w-4 h-4 text-amber-400" />
                  )}
                  {repairResult.is_valid ? 'SVG is Valid & Safe' : 'Issues Repaired Automatically'}
                </span>
                <span className="text-[10px] font-mono text-slate-400">
                  {repairResult.was_repaired ? 'Normalized & Sanitized' : 'Structure Verified'}
                </span>
              </div>
              {repairResult.notices && repairResult.notices.length > 0 && (
                <ul className="list-disc list-inside space-y-1 text-slate-300 text-[11px]">
                  {repairResult.notices.map((iss: string, idx: number) => (
                    <li key={idx}>{iss}</li>
                  ))}
                </ul>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default TemplatePage;
