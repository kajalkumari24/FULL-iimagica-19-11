import React, { useState } from 'react';
import { Settings, Server, Database, Cpu, CheckCircle2 } from 'lucide-react';

const SettingsPage: React.FC = () => {
  const [apiUrl, setApiUrl] = useState('http://127.0.0.1:8000');
  const [saved, setSaved] = useState(false);

  const handleSave = () => {
    localStorage.setItem('FOOTER_API_URL', apiUrl);
    setSaved(true);
    setTimeout(() => setSaved(false), 2000);
  };

  return (
    <div className="h-full w-full bg-slate-900 p-8 overflow-y-auto text-slate-100 select-none">
      <div className="max-w-4xl mx-auto space-y-6">
        {/* Header */}
        <div className="border-b border-slate-800 pb-5">
          <h1 className="text-2xl font-bold text-white flex items-center gap-2.5">
            <Settings className="w-6 h-6 text-slate-400" /> System Settings
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Configure local backend endpoints, storage drivers, and AI fallback parameters.
          </p>
        </div>

        {/* Backend Endpoint Settings */}
        <div className="p-6 bg-slate-800 rounded-xl border border-slate-700 space-y-4">
          <h3 className="font-semibold text-sm text-white flex items-center gap-2">
            <Server className="w-4 h-4 text-indigo-400" /> Backend API Endpoint
          </h3>
          <div className="space-y-2 text-xs">
            <label className="text-slate-400">FastAPI Server URL</label>
            <div className="flex gap-2">
              <input
                type="text"
                value={apiUrl}
                onChange={(e) => setApiUrl(e.target.value)}
                className="flex-1 bg-slate-900 border border-slate-700 rounded-lg p-2.5 text-slate-200"
              />
              <button
                onClick={handleSave}
                className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 rounded-lg font-semibold text-white transition"
              >
                Save
              </button>
            </div>
            {saved && (
              <p className="text-emerald-400 text-xs flex items-center gap-1 mt-1">
                <CheckCircle2 className="w-3.5 h-3.5" /> Endpoint configuration saved
              </p>
            )}
          </div>
        </div>

        {/* Persistence Status */}
        <div className="p-6 bg-slate-800 rounded-xl border border-slate-700 space-y-3">
          <h3 className="font-semibold text-sm text-white flex items-center gap-2">
            <Database className="w-4 h-4 text-emerald-400" /> Persistence & Storage Engine
          </h3>
          <div className="p-3 bg-slate-900 rounded-lg border border-slate-700/60 text-xs text-slate-300 space-y-1">
            <div className="flex items-center justify-between">
              <span className="text-slate-400">Current Storage Driver:</span>
              <span className="font-semibold text-emerald-400 font-mono">Local JSON Filesystem (Stand-alone)</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-slate-400">Storage Location:</span>
              <span className="font-mono text-slate-400">backend/data/</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-slate-400">MongoDB Integration:</span>
              <span className="text-slate-500">Configurable via MONGODB_URI (Optional)</span>
            </div>
          </div>
        </div>

        {/* AI Engine Status */}
        <div className="p-6 bg-slate-800 rounded-xl border border-slate-700 space-y-3">
          <h3 className="font-semibold text-sm text-white flex items-center gap-2">
            <Cpu className="w-4 h-4 text-purple-400" /> Layout Calculation Subsystem
          </h3>
          <div className="p-3 bg-slate-900 rounded-lg border border-slate-700/60 text-xs text-slate-300 space-y-1">
            <div className="flex items-center justify-between">
              <span className="text-slate-400">Layout Engine:</span>
              <span className="font-semibold text-purple-400 font-mono">Deterministic Python Algorithms</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-slate-400">Computer Vision:</span>
              <span className="font-mono text-slate-300">OpenCV 4.x + NumPy (K-Means & Canny)</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-slate-400">External API Requirement:</span>
              <span className="font-semibold text-emerald-400">0% (Completely Free & Local)</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SettingsPage;
