import React, { useState } from 'react';
import { Download, Undo2, Redo2, Sparkles, Save } from 'lucide-react';
import { InputPanel } from '../components/studio/InputPanel';
import { CanvasPanel } from '../components/studio/CanvasPanel';
import { PropertiesPanel } from '../components/studio/PropertiesPanel';
import { VariationsPanel } from '../components/studio/VariationsPanel';
import { ExportModal } from '../components/studio/ExportModal';
import { useEditorStore } from '../store/editorStore';
import * as api from '../api/client';

const StudioPage: React.FC = () => {
  const {
    activeFooter,
    brand,
    posterDataUrl,
    posterWidth,
    posterHeight,
    undo,
    redo,
    undoStack,
    redoStack,
  } = useEditorStore();

  const [isExportOpen, setIsExportOpen] = useState(false);
  const [projectTitle, setProjectTitle] = useState('Untitled Poster Project');
  const [saveSuccess, setSaveSuccess] = useState(false);

  const handleSaveProject = async () => {
    try {
      await api.saveProject({
        id: 'proj_' + Math.random().toString(36).substring(2, 9),
        name: projectTitle,
        poster_width: posterWidth,
        poster_height: posterHeight,
        poster_data_url: posterDataUrl,
        brand,
        active_footer: activeFooter || undefined,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
        footer_variations: [],
        tags: [],
      });
      setSaveSuccess(true);
      setTimeout(() => setSaveSuccess(false), 2500);
    } catch (err) {
      console.error('Failed to save project:', err);
    }
  };

  return (
    <div className="flex flex-col h-full w-full bg-slate-900 text-slate-100 overflow-hidden select-none">
      {/* Studio Top Action Bar */}
      <div className="h-14 bg-slate-800/90 border-b border-slate-700 px-6 flex items-center justify-between z-10">
        <div className="flex items-center gap-3">
          <input
            type="text"
            value={projectTitle}
            onChange={(e) => setProjectTitle(e.target.value)}
            className="bg-transparent hover:bg-slate-700/50 focus:bg-slate-900 px-2 py-1 rounded font-semibold text-sm border border-transparent focus:border-slate-600 focus:outline-none transition"
          />
          {saveSuccess && (
            <span className="text-xs text-emerald-400 font-medium bg-emerald-950/60 border border-emerald-800 px-2 py-0.5 rounded">
              Saved!
            </span>
          )}
        </div>

        {/* Center Undo / Redo */}
        <div className="flex items-center gap-1 bg-slate-900/60 p-1 rounded-lg border border-slate-700">
          <button
            onClick={undo}
            disabled={undoStack.length === 0}
            className="p-1.5 hover:bg-slate-800 rounded text-slate-400 hover:text-white disabled:opacity-30 transition"
            title="Undo"
          >
            <Undo2 className="w-4 h-4" />
          </button>
          <button
            onClick={redo}
            disabled={redoStack.length === 0}
            className="p-1.5 hover:bg-slate-800 rounded text-slate-400 hover:text-white disabled:opacity-30 transition"
            title="Redo"
          >
            <Redo2 className="w-4 h-4" />
          </button>
        </div>

        {/* Right Action Buttons */}
        <div className="flex items-center gap-3">
          <button
            onClick={handleSaveProject}
            className="px-3.5 py-1.5 bg-slate-700 hover:bg-slate-600 text-xs font-semibold rounded-lg flex items-center gap-1.5 transition"
          >
            <Save className="w-3.5 h-3.5" /> Save
          </button>
          <button
            onClick={() => setIsExportOpen(true)}
            disabled={!activeFooter}
            className="px-4 py-1.5 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-40 text-xs font-semibold rounded-lg shadow-md shadow-indigo-600/30 flex items-center gap-1.5 text-white transition"
          >
            <Download className="w-3.5 h-3.5" /> Export Final Poster
          </button>
        </div>
      </div>

      {/* Main Studio Work Area */}
      <div className="flex-1 flex overflow-hidden">
        {/* Left Input Sidebar */}
        <InputPanel />

        {/* Center Viewport & Bottom Variations */}
        <div className="flex-1 flex flex-col overflow-hidden">
          <CanvasPanel />
          <VariationsPanel />
        </div>

        {/* Right Properties Sidebar */}
        <PropertiesPanel />
      </div>

      {/* Export Modal */}
      <ExportModal isOpen={isExportOpen} onClose={() => setIsExportOpen(false)} />
    </div>
  );
};

export default StudioPage;
