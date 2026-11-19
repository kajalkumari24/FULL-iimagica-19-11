import React from 'react';
import {
  LayoutDashboard,
  PenTool,
  Palette,
  LayoutTemplate,
  FolderOpen,
  Settings,
} from 'lucide-react';
import { useEditorStore } from '../store/editorStore';

const navItems = [
  { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { id: 'studio', label: 'Footer Studio', icon: PenTool },
  { id: 'brand', label: 'Brand Kit', icon: Palette },
  { id: 'templates', label: 'Templates', icon: LayoutTemplate },
  { id: 'projects', label: 'My Projects', icon: FolderOpen },
  { id: 'settings', label: 'Settings', icon: Settings },
];

const Sidebar: React.FC = () => {
  const currentPage = useEditorStore((s) => s.currentPage);
  const setCurrentPage = useEditorStore((s) => s.setCurrentPage);

  return (
    <aside className="w-16 lg:w-56 bg-slate-950 border-r border-slate-800 flex flex-col h-full shrink-0">
      <div className="p-3 lg:p-4 border-b border-slate-800">
        <h1 className="hidden lg:block text-lg font-bold bg-gradient-to-r from-indigo-400 to-purple-400 bg-clip-text text-transparent">
          Footer Studio
        </h1>
        <span className="lg:hidden text-xl font-bold text-indigo-400 block text-center">FS</span>
      </div>
      <nav className="flex-1 py-2 space-y-1 px-2">
        {navItems.map((item) => {
          const Icon = item.icon;
          const active = currentPage === item.id;
          return (
            <button
              key={item.id}
              onClick={() => setCurrentPage(item.id)}
              className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all ${
                active
                  ? 'bg-indigo-600/20 text-indigo-400 border border-indigo-500/30'
                  : 'text-slate-400 hover:bg-slate-800 hover:text-slate-200 border border-transparent'
              }`}
            >
              <Icon size={18} />
              <span className="hidden lg:inline">{item.label}</span>
            </button>
          );
        })}
      </nav>
      <div className="p-3 border-t border-slate-800">
        <p className="hidden lg:block text-xs text-slate-600 text-center">v1.0.0</p>
      </div>
    </aside>
  );
};

export default Sidebar;
