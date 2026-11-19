import React from 'react';
import Sidebar from './components/Sidebar';
import StudioPage from './pages/StudioPage';
import DashboardPage from './pages/DashboardPage';
import BrandKitPage from './pages/BrandKitPage';
import ProjectsPage from './pages/ProjectsPage';
import TemplatePage from './pages/TemplatePage';
import SettingsPage from './pages/SettingsPage';
import { useEditorStore } from './store/editorStore';

const App: React.FC = () => {
  const currentPage = useEditorStore((s) => s.currentPage);

  const renderPage = () => {
    switch (currentPage) {
      case 'dashboard':
        return <DashboardPage />;
      case 'studio':
        return <StudioPage />;
      case 'brand':
        return <BrandKitPage />;
      case 'templates':
        return <TemplatePage />;
      case 'projects':
        return <ProjectsPage />;
      case 'settings':
        return <SettingsPage />;
      default:
        return <StudioPage />;
    }
  };

  return (
    <div className="flex h-screen w-screen overflow-hidden bg-slate-900">
      <Sidebar />
      <main className="flex-1 overflow-hidden">{renderPage()}</main>
    </div>
  );
};

export default App;
