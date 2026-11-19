import React, { useEffect, useState } from 'react';
import { PenTool, FolderOpen, Palette, Sparkles, Plus, Clock } from 'lucide-react';
import { useEditorStore } from '../store/editorStore';
import * as api from '../api/client';
import type { Project } from '../types';

const DashboardPage: React.FC = () => {
  const { setCurrentPage } = useEditorStore();
  const [projects, setProjects] = useState<Project[]>([]);

  useEffect(() => {
    api.listProjects().then(setProjects).catch(console.error);
  }, []);

  return (
    <div className="h-full w-full bg-slate-900 p-8 overflow-y-auto text-slate-100 select-none">
      <div className="max-w-6xl mx-auto space-y-8">
        {/* Welcome Banner */}
        <div className="p-8 rounded-2xl bg-gradient-to-r from-indigo-900/60 via-slate-800 to-slate-800 border border-slate-700/80 shadow-xl flex items-center justify-between">
          <div className="space-y-2">
            <h1 className="text-2xl font-bold text-white flex items-center gap-3">
              <Sparkles className="w-6 h-6 text-indigo-400" /> Welcome to Footer Studio
            </h1>
            <p className="text-sm text-slate-400 max-w-xl">
              Automate and customize publication-grade footers for your posters, event banners, and social flyers with instant color-matching and dynamic safe-zone layout calculations.
            </p>
          </div>
          <button
            onClick={() => setCurrentPage('studio')}
            className="px-5 py-3 bg-indigo-600 hover:bg-indigo-500 rounded-xl font-semibold text-sm shadow-lg shadow-indigo-600/30 flex items-center gap-2 transition"
          >
            <Plus className="w-4 h-4" /> Create New Design
          </button>
        </div>

        {/* Quick Stats Grid */}
        <div className="grid grid-cols-3 gap-5">
          <div
            onClick={() => setCurrentPage('studio')}
            className="p-5 rounded-xl bg-slate-800/80 border border-slate-700 hover:border-indigo-500/50 cursor-pointer transition"
          >
            <div className="p-2.5 bg-indigo-500/10 text-indigo-400 rounded-lg w-fit mb-3">
              <PenTool className="w-5 h-5" />
            </div>
            <h3 className="font-semibold text-base text-white">Footer Studio</h3>
            <p className="text-xs text-slate-400 mt-1">Open the canvas to edit or generate footers</p>
          </div>

          <div
            onClick={() => setCurrentPage('brand')}
            className="p-5 rounded-xl bg-slate-800/80 border border-slate-700 hover:border-indigo-500/50 cursor-pointer transition"
          >
            <div className="p-2.5 bg-purple-500/10 text-purple-400 rounded-lg w-fit mb-3">
              <Palette className="w-5 h-5" />
            </div>
            <h3 className="font-semibold text-base text-white">Brand Kits</h3>
            <p className="text-xs text-slate-400 mt-1">Manage reusable logos, colors, and presets</p>
          </div>

          <div
            onClick={() => setCurrentPage('projects')}
            className="p-5 rounded-xl bg-slate-800/80 border border-slate-700 hover:border-indigo-500/50 cursor-pointer transition"
          >
            <div className="p-2.5 bg-emerald-500/10 text-emerald-400 rounded-lg w-fit mb-3">
              <FolderOpen className="w-5 h-5" />
            </div>
            <h3 className="font-semibold text-base text-white">Projects</h3>
            <p className="text-xs text-slate-400 mt-1">{projects.length} saved project(s)</p>
          </div>
        </div>

        {/* Recent Projects Section */}
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-semibold text-white flex items-center gap-2">
              <Clock className="w-4 h-4 text-slate-400" /> Recent Projects
            </h3>
            {projects.length > 0 && (
              <button
                onClick={() => setCurrentPage('projects')}
                className="text-xs text-indigo-400 hover:text-indigo-300"
              >
                View All
              </button>
            )}
          </div>

          {projects.length === 0 ? (
            <div className="p-8 rounded-xl bg-slate-800/40 border border-slate-800 text-center text-slate-500 text-sm">
              No saved projects yet. Open the Footer Studio to start your first design.
            </div>
          ) : (
            <div className="grid grid-cols-3 gap-5">
              {projects.slice(0, 3).map((p) => (
                <div
                  key={p.id}
                  onClick={() => setCurrentPage('studio')}
                  className="p-4 rounded-xl bg-slate-800/90 border border-slate-700 hover:border-slate-500 cursor-pointer transition space-y-3"
                >
                  <div className="h-32 bg-slate-900 rounded-lg overflow-hidden flex items-center justify-center">
                    {p.poster_data_url ? (
                      <img src={p.poster_data_url} alt={p.name} className="h-full w-full object-cover" />
                    ) : (
                      <span className="text-xs text-slate-600 font-mono">1080 × 1080</span>
                    )}
                  </div>
                  <div>
                    <h4 className="font-semibold text-sm text-slate-200 truncate">{p.name}</h4>
                    <p className="text-[11px] text-slate-500 mt-0.5">
                      {new Date(p.created_at || Date.now()).toLocaleDateString()}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default DashboardPage;
