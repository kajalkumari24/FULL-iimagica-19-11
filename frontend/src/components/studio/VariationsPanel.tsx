import React, { useState, useEffect } from 'react';
import { Sparkles, Layers, LayoutGrid, Check, CheckCircle2 } from 'lucide-react';
import { useEditorStore } from '../../store/editorStore';
import { sanitizeSvg } from '../../utils/sanitizeSvg';
import { ARRANGEMENT_METADATA } from '../../utils/arrangementMetadata';
import * as api from '../../api/client';
import type { FooterDesign } from '../../types';

export const VariationsPanel: React.FC = () => {
  const {
    footerVariations,
    selectedFooterIndex,
    selectFooter,
    activeFooter,
    brand,
    posterWidth,
    posterHeight,
    setActiveFooter,
  } = useEditorStore();

  const [activeTab, setActiveTab] = useState<'variations' | 'positions'>('variations');
  const [positionOptions, setPositionOptions] = useState<FooterDesign[]>([]);
  const [loadingPositions, setLoadingPositions] = useState(false);

  // Load position options for the current active footer
  useEffect(() => {
    if (!activeFooter) return;
    let isMounted = true;

    const fetchOptions = async () => {
      setLoadingPositions(true);
      try {
        const res = await api.getPositionOptions(activeFooter, brand, posterWidth, posterHeight);
        if (isMounted) {
          setPositionOptions(res);
        }
      } catch (err) {
        console.error('Error fetching position options:', err);
      } finally {
        if (isMounted) setLoadingPositions(false);
      }
    };

    fetchOptions();

    return () => {
      isMounted = false;
    };
  }, [activeFooter?.id, activeFooter?.background.shape, activeFooter?.background.color, brand]);

  // When no footers generated and no active footer
  if (footerVariations.length === 0 && !activeFooter) {
    return (
      <div className="h-32 bg-slate-800 border-t border-slate-700 flex items-center justify-center text-slate-500 text-xs gap-2 select-none">
        <Sparkles className="w-4 h-4 text-indigo-400 opacity-50" />
        Click "Generate Footers" on the left to see multiple design variations here
      </div>
    );
  }

  const handleSelectPositionOption = async (opt: FooterDesign) => {
    if (!activeFooter) return;
    try {
      const updated = await api.rearrangeFooter(
        activeFooter,
        opt.content_arrangement || 'classic_horizontal',
        brand,
        posterWidth,
        posterHeight
      );
      setActiveFooter(updated);
    } catch (err) {
      console.error('Failed to apply position arrangement:', err);
    }
  };

  const currentArrangement = activeFooter?.content_arrangement || 'classic_horizontal';

  return (
    <div className="h-38 bg-slate-800 border-t border-slate-700 flex flex-col select-none overflow-hidden">
      {/* Header with Two Tabs */}
      <div className="px-4 py-1.5 border-b border-slate-700/80 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <button
            onClick={() => setActiveTab('variations')}
            className={`px-2.5 py-1 rounded text-[11px] font-semibold uppercase tracking-wider flex items-center gap-1.5 transition ${activeTab === 'variations'
                ? 'bg-indigo-600 text-white shadow-sm'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-750'
              }`}
          >
            <Layers className="w-3.5 h-3.5 text-indigo-300" />
            Style Variations ({footerVariations.length})
          </button>

          {activeFooter && (
            <button
              onClick={() => setActiveTab('positions')}
              className={`px-2.5 py-1 rounded text-[11px] font-semibold uppercase tracking-wider flex items-center gap-1.5 transition ${activeTab === 'positions'
                  ? 'bg-indigo-600 text-white shadow-sm'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-750'
                }`}
            >
              <LayoutGrid className="w-3.5 h-3.5 text-indigo-300" />
              Position & Layout Options ({positionOptions.length || 20})
            </button>
          )}
        </div>

        <span className="text-[10px] text-slate-400">
          {activeTab === 'variations'
            ? 'Click any card to change background & theme'
            : 'Click any card to automatically rearrange elements'}
        </span>
      </div>

      {/* Horizontal Carousel */}
      <div className="flex-1 flex items-center gap-3 px-4 overflow-x-auto custom-scrollbar py-2">
        {activeTab === 'variations' ? (
          /* Style Variations Carousel */
          footerVariations.map((variation, index) => {
            const isSelected = selectedFooterIndex === index;
            const sanitizedMarkup = variation.svg_markup ? sanitizeSvg(variation.svg_markup) : '';

            return (
              <div
                key={variation.id || index}
                onClick={() => selectFooter(index)}
                className={`flex-shrink-0 w-52 h-26 rounded-lg cursor-pointer p-2 flex flex-col justify-between transition-all border ${isSelected
                    ? 'border-indigo-500 bg-slate-900 shadow-md shadow-indigo-500/20 ring-1 ring-indigo-500'
                    : 'border-slate-700 bg-slate-900/60 hover:border-slate-500 hover:bg-slate-900'
                  }`}
              >
                {/* Real SVG Thumbnail Preview Box */}
                <div className="w-full h-14 rounded overflow-hidden flex items-center justify-center bg-slate-950 border border-slate-800/80 p-0.5 relative pointer-events-none">
                  {sanitizedMarkup ? (
                    <div
                      className="w-full h-full flex items-center justify-center [&>svg]:w-full [&>svg]:h-full [&>svg]:object-contain"
                      dangerouslySetInnerHTML={{ __html: sanitizedMarkup }}
                    />
                  ) : (
                    <div
                      className="w-full h-full rounded flex items-center justify-center"
                      style={{
                        backgroundColor: variation.background.color || '#0f172a',
                        opacity: variation.background.opacity || 1,
                      }}
                    >
                      <span className="text-[9px] font-bold text-white/80 truncate px-1">
                        {variation.name}
                      </span>
                    </div>
                  )}
                </div>

                {/* Title & Category Label */}
                <div className="flex items-center justify-between pt-1">
                  <span className="text-[11px] font-medium text-slate-200 truncate">{variation.name}</span>
                  <span className="text-[9px] uppercase px-1.5 py-0.5 rounded bg-slate-800 text-slate-400 border border-slate-700">
                    {variation.style_category}
                  </span>
                </div>
              </div>
            );
          })
        ) : (
          /* Position & Layout Options Carousel */
          positionOptions.map((opt) => {
            const arrKey = opt.content_arrangement || '';
            const meta = ARRANGEMENT_METADATA[arrKey] || {
              id: arrKey,
              name: opt.name,
              category: 'all',
              logoPos: 'Custom',
              profilePos: 'Custom',
              contactPos: 'Custom',
              tag: 'Layout',
              description: '',
            };
            const isSelected = currentArrangement === arrKey;
            const markup = opt.svg_markup ? sanitizeSvg(opt.svg_markup) : '';

            return (
              <div
                key={opt.id}
                onClick={() => handleSelectPositionOption(opt)}
                className={`flex-shrink-0 w-56 h-26 rounded-lg cursor-pointer p-2 flex flex-col justify-between transition-all border ${isSelected
                    ? 'border-indigo-500 bg-slate-900 shadow-md shadow-indigo-500/20 ring-1 ring-indigo-500'
                    : 'border-slate-700 bg-slate-900/60 hover:border-slate-500 hover:bg-slate-900'
                  }`}
              >
                {/* SVG Thumbnail Preview Box */}
                <div className="w-full h-14 rounded overflow-hidden flex items-center justify-center bg-slate-950 border border-slate-800/80 p-0.5 relative pointer-events-none">
                  {markup ? (
                    <div
                      className="w-full h-full flex items-center justify-center [&>svg]:w-full [&>svg]:h-full [&>svg]:object-contain"
                      dangerouslySetInnerHTML={{ __html: markup }}
                    />
                  ) : (
                    <div className="w-full h-full flex items-center justify-center text-[10px] text-slate-400">
                      {meta.name}
                    </div>
                  )}

                  {isSelected && (
                    <div className="absolute top-1 right-1 bg-indigo-600 text-white rounded-full p-0.5 shadow">
                      <Check className="w-2.5 h-2.5" />
                    </div>
                  )}
                </div>

                {/* Title & Position Badges */}
                <div className="flex items-center justify-between pt-1">
                  <span className={`text-[11px] font-semibold truncate ${isSelected ? 'text-indigo-300' : 'text-slate-200'}`}>
                    {meta.name}
                  </span>
                  <span className="text-[9px] uppercase px-1.5 py-0.5 rounded bg-indigo-950/60 text-indigo-300 border border-indigo-800/60 font-medium">
                    {meta.tag}
                  </span>
                </div>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
};
