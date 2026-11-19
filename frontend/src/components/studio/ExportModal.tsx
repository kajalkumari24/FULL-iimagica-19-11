import React, { useState } from 'react';
import { Download, X, FileImage, FileCode, CheckCircle2, RefreshCw } from 'lucide-react';
import { useEditorStore } from '../../store/editorStore';
import * as api from '../../api/client';

interface ExportModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const ExportModal: React.FC<ExportModalProps> = ({ isOpen, onClose }) => {
  const { activeFooter, posterDataUrl, posterWidth, posterHeight } = useEditorStore();
  const [format, setFormat] = useState<'png' | 'jpg' | 'svg' | 'pdf'>('png');
  const [isExporting, setIsExporting] = useState(false);

  if (!isOpen || !activeFooter) return null;

  const handleDownload = async () => {
    setIsExporting(true);
    try {
      const blob = await api.exportPoster(
        posterDataUrl,
        activeFooter,
        format,
        posterWidth,
        posterHeight
      );

      // Trigger browser download
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `poster-design-${Date.now()}.${format}`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);

      onClose();
    } catch (err) {
      console.error('Export failed:', err);
      alert('Export failed. Check backend connection.');
    } finally {
      setIsExporting(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 bg-slate-950/80 backdrop-blur-sm flex items-center justify-center p-4">
      <div className="bg-slate-900 border border-slate-700 rounded-xl w-full max-w-md p-6 shadow-2xl space-y-5 text-slate-200">
        <div className="flex items-center justify-between border-b border-slate-800 pb-3">
          <h3 className="font-semibold text-base text-white flex items-center gap-2">
            <Download className="w-5 h-5 text-indigo-400" /> Export Poster
          </h3>
          <button onClick={onClose} className="p-1 text-slate-400 hover:text-white rounded">
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Dimension Specs */}
        <div className="p-3 bg-slate-800/80 rounded-lg border border-slate-700/80 flex items-center justify-between text-xs">
          <span className="text-slate-400">Resolution</span>
          <span className="font-mono font-semibold text-indigo-300">
            {posterWidth} × {posterHeight} px
          </span>
        </div>

        {/* Format Selector */}
        <div className="space-y-2">
          <label className="text-xs font-medium text-slate-300">Select File Format</label>
          <div className="grid grid-cols-2 gap-2.5">
            {[
              { id: 'png', label: 'PNG Image', desc: 'Lossless quality for web & social' },
              { id: 'jpg', label: 'JPG Image', desc: 'Compact high-quality photo print' },
              { id: 'svg', label: 'SVG Vector', desc: 'Editable vector footer elements' },
              { id: 'pdf', label: 'PDF Document', desc: 'Print-ready high resolution' },
            ].map((item) => (
              <button
                key={item.id}
                onClick={() => setFormat(item.id as any)}
                className={`p-3 rounded-lg border text-left transition ${
                  format === item.id
                    ? 'border-indigo-500 bg-indigo-600/15 text-white ring-1 ring-indigo-500'
                    : 'border-slate-800 bg-slate-800/50 hover:border-slate-700 text-slate-300'
                }`}
              >
                <div className="font-semibold text-xs">{item.label}</div>
                <div className="text-[10px] text-slate-400 mt-0.5">{item.desc}</div>
              </button>
            ))}
          </div>
        </div>

        {/* Action Buttons */}
        <div className="pt-2 flex items-center gap-3">
          <button
            onClick={onClose}
            className="flex-1 py-2.5 bg-slate-800 hover:bg-slate-700 rounded-lg text-xs font-medium text-slate-300 transition"
          >
            Cancel
          </button>
          <button
            onClick={handleDownload}
            disabled={isExporting}
            className="flex-1 py-2.5 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white font-semibold text-xs rounded-lg shadow-lg shadow-indigo-600/30 flex items-center justify-center gap-2 transition"
          >
            {isExporting ? (
              <>
                <RefreshCw className="w-4 h-4 animate-spin" /> Rendering...
              </>
            ) : (
              <>
                <Download className="w-4 h-4" /> Download {format.toUpperCase()}
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
};
