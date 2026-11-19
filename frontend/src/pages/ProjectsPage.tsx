import React, { useEffect, useState } from 'react';
import { FolderOpen, Copy, Trash2, ArrowUpRight, Plus } from 'lucide-react';
import { useEditorStore } from '../store/editorStore';
import * as api from '../api/client';
import type { Project } from '../types';

const ProjectsPage: React.FC = () => {
  const {
    setCurrentPage,
    setPosterDataUrl,
    setPosterDimensions,
    setBrand,
    setActiveFooter,
  } = useEditorStore();

  const [projects, setProjects] = useState<Project[]>([]);

  useEffect(() => {
    loadProjects();
  }, []);

  const loadProjects = async () => {
    try {
      const list = await api.listProjects();
      setProjects(list);
    } catch (err) {
      console.error(err);
    }
  };

  const handleOpen = (p: Project) => {
    if (p.poster_data_url) setPosterDataUrl(p.poster_data_url);
    if (p.poster_width && p.poster_height) setPosterDimensions(p.poster_width, p.poster_height);
    if (p.brand) setBrand(p.brand);
    if (p.active_footer) setActiveFooter(p.active_footer);
    setCurrentPage('studio');
  };

  const handleDuplicate = async (id: string) => {
    await api.duplicateProject(id);
    loadProjects();
  };

  const handleDelete = async (id: string) => {
    if (confirm('Delete this project?')) {
      await api.deleteProject(id);
      loadProjects();
    }
  };

  return (
    <div className="h-full w-full bg-slate-900 p-8 overflow-y-auto text-slate-100 select-none">
      <div className="max-w-6xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between border-b border-slate-800 pb-5">
          <div>
            <h1 className="text-2xl font-bold text-white flex items-center gap-2.5">
              <FolderOpen className="w-6 h-6 text-emerald-400" /> My Projects
            </h1>
            <p className="text-xs text-slate-400 mt-1">
              Access and manage your saved poster projects, brand assets, and customized footer variations.
            </p>
          </div>
          <button
            onClick={() => setCurrentPage('studio')}
            className="px-4 py-2 bg-emerald-600 hover:bg-emerald-500 rounded-lg text-xs font-semibold flex items-center gap-2 shadow-lg shadow-emerald-600/20 transition"
          >
            <Plus className="w-4 h-4" /> New Project
          </button>
        </div>

        {/* Projects Grid */}
        {projects.length === 0 ? (
          <div className="p-12 bg-slate-800/40 rounded-xl border border-slate-800 text-center text-slate-500 space-y-2">
            <p className="text-base font-medium">No projects saved yet</p>
            <p className="text-xs">Create your first design in the Footer Studio and save it here.</p>
          </div>
        ) : (
          <div className="grid grid-cols-3 gap-5">
            {projects.map((p) => (
              <div
                key={p.id}
                className="p-4 rounded-xl bg-slate-800/90 border border-slate-700 hover:border-slate-500 transition space-y-3 flex flex-col justify-between"
              >
                <div
                  onClick={() => handleOpen(p)}
                  className="h-36 bg-slate-900 rounded-lg overflow-hidden flex items-center justify-center cursor-pointer group relative"
                >
                  {p.poster_data_url ? (
                    <img src={p.poster_data_url} alt={p.name} className="h-full w-full object-cover" />
                  ) : (
                    <span className="text-xs text-slate-600 font-mono">
                      {p.poster_width || 1080} × {p.poster_height || 1080}
                    </span>
                  )}
                  <div className="absolute inset-0 bg-slate-950/60 opacity-0 group-hover:opacity-100 transition flex items-center justify-center">
                    <span className="px-3 py-1.5 bg-indigo-600 text-white rounded text-xs font-semibold flex items-center gap-1 shadow">
                      Open <ArrowUpRight className="w-3.5 h-3.5" />
                    </span>
                  </div>
                </div>

                <div>
                  <h4 className="font-semibold text-sm text-slate-200 truncate">{p.name}</h4>
                  <p className="text-[11px] text-slate-500 mt-0.5">
                    Updated {new Date(p.updated_at || p.created_at || Date.now()).toLocaleDateString()}
                  </p>
                </div>

                <div className="flex items-center justify-between pt-2 border-t border-slate-700/60 text-xs">
                  <button
                    onClick={() => handleDuplicate(p.id)}
                    className="text-slate-400 hover:text-slate-200 flex items-center gap-1"
                    title="Duplicate Project"
                  >
                    <Copy className="w-3.5 h-3.5" /> Duplicate
                  </button>
                  <button
                    onClick={() => handleDelete(p.id)}
                    className="text-slate-500 hover:text-rose-400"
                    title="Delete Project"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default ProjectsPage;
