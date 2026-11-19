import React, { useState, useEffect } from 'react';
import { LayoutGrid, Sparkles, Check, CheckCircle2, Shield, Eye } from 'lucide-react';
import { useEditorStore } from '../../store/editorStore';
import { ARRANGEMENT_METADATA, ArrangementMeta } from '../../utils/arrangementMetadata';
import { sanitizeSvg } from '../../utils/sanitizeSvg';
import * as api from '../../api/client';
import type { FooterDesign } from '../../types';

interface PositionOptionsSectionProps {
  mode?: 'panel' | 'grid';
}

export const PositionOptionsSection: React.FC<PositionOptionsSectionProps> = ({ mode = 'panel' }) => {
  const {
    activeFooter,
    brand,
    posterWidth,
    posterHeight,
    setActiveFooter,
  } = useEditorStore();

  const [options, setOptions] = useState<FooterDesign[]>([]);
  const [loading, setLoading] = useState(false);
  const [selectedFilter, setSelectedFilter] = useState<string>('all');
  const [applyingId, setApplyingId] = useState<string | null>(null);

  // Fetch or generate position options whenever activeFooter background or brand changes
  useEffect(() => {
    if (!activeFooter) return;
    let isMounted = true;

    const loadOptions = async () => {
      setLoading(true);
      try {
        const fetched = await api.getPositionOptions(activeFooter, brand, posterWidth, posterHeight);
        if (isMounted) {
          setOptions(fetched);
        }
      } catch (err) {
        console.error('Failed to load position options:', err);
      } finally {
        if (isMounted) setLoading(false);
      }
    };

    loadOptions();

    return () => {
      isMounted = false;
    };
  }, [activeFooter?.id, activeFooter?.background.shape, activeFooter?.background.color, brand]);

  if (!activeFooter) return null;

  const currentArrangementKey = activeFooter.content_arrangement || 'classic_horizontal';
  const currentMeta: ArrangementMeta = ARRANGEMENT_METADATA[currentArrangementKey] || {
    id: currentArrangementKey,
    name: currentArrangementKey.replace(/_/g, ' ').toUpperCase(),
    category: 'all',
    logoPos: 'Custom',
    profilePos: 'Custom',
    contactPos: 'Custom',
    tag: 'Active',
    description: 'Current custom layout arrangement',
  };

  const handleApplyArrangement = async (opt: FooterDesign) => {
    setApplyingId(opt.content_arrangement || opt.id);
    try {
      // Re-apply arrangement keeping active background, color, and padding
      const updated = await api.rearrangeFooter(
        activeFooter,
        opt.content_arrangement || 'classic_horizontal',
        brand,
        posterWidth,
        posterHeight
      );
      setActiveFooter(updated);
    } catch (err) {
      console.error('Failed to apply arrangement:', err);
    } finally {
      setTimeout(() => setApplyingId(null), 300);
    }
  };

  const filteredOptions = options.filter((opt) => {
    if (selectedFilter === 'all') return true;
    const meta = ARRANGEMENT_METADATA[opt.content_arrangement || ''];
    return meta && meta.category === selectedFilter;
  });

  return (
    <div className="space-y-3">
      {/* Section Header */}
      <div className="flex items-center justify-between">
        <label className="text-[11px] font-semibold text-slate-300 flex items-center gap-1.5 uppercase tracking-wider">
          <LayoutGrid className="w-3.5 h-3.5 text-indigo-400" /> Position & Layout Options
        </label>
        <span className="text-[10px] px-2 py-0.5 rounded-full bg-indigo-500/20 text-indigo-300 border border-indigo-500/30 font-medium">
          {options.length || 20} Options
        </span>
      </div>

      {/* Active Position Summary Badge */}
      <div className="p-2.5 bg-slate-900 rounded-lg border border-indigo-500/30 flex flex-col gap-1.5">
        <div className="flex items-center justify-between">
          <span className="text-[11px] font-bold text-indigo-300 flex items-center gap-1">
            <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" /> {currentMeta.name}
          </span>
          <span className="text-[9px] uppercase px-1.5 py-0.2 rounded bg-indigo-900/50 text-indigo-300 font-semibold border border-indigo-700/50">
            {currentMeta.tag}
          </span>
        </div>
        <div className="grid grid-cols-3 gap-1 pt-1 border-t border-slate-800 text-[9px] text-slate-400">
          <div><span className="text-slate-500 block">Logo:</span> {currentMeta.logoPos}</div>
          <div><span className="text-slate-500 block">Profile:</span> {currentMeta.profilePos}</div>
          <div><span className="text-slate-500 block">Contacts:</span> {currentMeta.contactPos}</div>
        </div>
      </div>

      {/* Category Filter Pills */}
      <div className="flex items-center gap-1 overflow-x-auto pb-1 text-[10px] custom-scrollbar">
        {[
          { id: 'all', label: 'All (20)' },
          { id: 'columns', label: 'Columns' },
          { id: 'centred', label: 'Centred' },
          { id: 'profile', label: 'Profile' },
          { id: 'cards', label: 'Cards' },
          { id: 'stacked', label: 'Stacked' },
        ].map((f) => (
          <button
            key={f.id}
            onClick={() => setSelectedFilter(f.id)}
            className={`px-2 py-0.5 rounded-md font-medium whitespace-nowrap transition border ${
              selectedFilter === f.id
                ? 'bg-indigo-600 text-white border-indigo-500'
                : 'bg-slate-900 text-slate-400 border-slate-800 hover:border-slate-700 hover:text-slate-200'
            }`}
          >
            {f.label}
          </button>
        ))}
      </div>

      {/* Visual Preview Cards */}
      <div className="space-y-2 max-h-80 overflow-y-auto pr-1 custom-scrollbar">
        {loading && options.length === 0 ? (
          <div className="p-4 bg-slate-900 rounded border border-slate-800 text-center text-slate-500 text-xs">
            Generating layout options...
          </div>
        ) : (
          filteredOptions.map((opt) => {
            const arrKey = opt.content_arrangement || '';
            const meta = ARRANGEMENT_METADATA[arrKey] || {
              id: arrKey,
              name: opt.name,
              category: 'all',
              logoPos: 'Dynamic',
              profilePos: 'Dynamic',
              contactPos: 'Dynamic',
              tag: 'Layout',
              description: '',
            };
            const isCurrent = currentArrangementKey === arrKey;
            const isApplying = applyingId === arrKey;
            const markup = opt.svg_markup ? sanitizeSvg(opt.svg_markup) : '';

            return (
              <div
                key={opt.id}
                onClick={() => handleApplyArrangement(opt)}
                className={`p-2 rounded-lg cursor-pointer transition-all border flex flex-col gap-1.5 ${
                  isCurrent
                    ? 'border-indigo-500 bg-slate-900/95 ring-1 ring-indigo-500 shadow-md shadow-indigo-500/10'
                    : 'border-slate-700/80 bg-slate-900/60 hover:border-slate-600 hover:bg-slate-900'
                }`}
              >
                {/* SVG Visual Card Thumbnail */}
                <div className="w-full h-14 rounded overflow-hidden bg-slate-950 border border-slate-800/80 flex items-center justify-center relative pointer-events-none p-0.5">
                  {markup ? (
                    <div
                      className="w-full h-full flex items-center justify-center [&>svg]:w-full [&>svg]:h-full [&>svg]:object-contain"
                      dangerouslySetInnerHTML={{ __html: markup }}
                    />
                  ) : (
                    <div
                      className="w-full h-full flex items-center justify-center text-[10px] text-slate-400"
                      style={{ backgroundColor: activeFooter.background.color || '#0f172a' }}
                    >
                      {meta.name}
                    </div>
                  )}

                  {isCurrent && (
                    <div className="absolute top-1 right-1 bg-indigo-600 text-white rounded-full p-0.5 shadow">
                      <Check className="w-2.5 h-2.5" />
                    </div>
                  )}
                </div>

                {/* Card Title & Positions */}
                <div className="flex items-center justify-between">
                  <span className={`text-[11px] font-semibold truncate ${isCurrent ? 'text-indigo-300' : 'text-slate-200'}`}>
                    {meta.name}
                  </span>
                  <span className="text-[9px] uppercase px-1.5 py-0.2 rounded bg-slate-800 text-slate-400 border border-slate-700">
                    {meta.tag}
                  </span>
                </div>

                {/* Sub-positions details */}
                <div className="flex items-center justify-between text-[9px] text-slate-400 pt-0.5 border-t border-slate-800/60">
                  <span className="truncate">Logo: {meta.logoPos}</span>
                  <span className="truncate">Contacts: {meta.contactPos}</span>
                </div>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
};
