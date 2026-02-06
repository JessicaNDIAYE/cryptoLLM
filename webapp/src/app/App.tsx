import { useState } from "react";
import { Sidebar } from "@/app/components/layout/Sidebar";
import { Topbar } from "@/app/components/layout/Topbar";
import { DashboardPage } from "@/app/pages/DashboardPage";
import { AskAIPage } from "@/app/pages/AskAIPage";
import { Toaster } from "sonner";

function PlaceholderPage({ title }: { title: string }) {
  return (
    <div className="flex flex-col items-center justify-center h-[60vh] text-center space-y-4 animate-in fade-in zoom-in duration-300">
       <div className="w-20 h-20 rounded-full bg-white shadow-xl shadow-purple-100 flex items-center justify-center mb-4">
          <span className="text-4xl">🌱</span>
       </div>
       <h2 className="text-3xl font-bold text-[#1F1F2E] tracking-tight">{title}</h2>
       <p className="text-gray-500 max-w-md text-lg">
         Cette section est en train de fleurir. Revenez bientôt pour voir vos investissements grandir.
       </p>
    </div>
  );
}

export default function App() {
  const [activePage, setActivePage] = useState("dashboard");
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const renderPage = () => {
    switch (activePage) {
      case "dashboard":
        return <DashboardPage />;
      case "glossary":
        return <PlaceholderPage title="Glossaire Financier" />;
      case "trading":
        return <PlaceholderPage title="Marchés & Trading" />;
      case "risks":
        return <PlaceholderPage title="Analyse de Risques" />;
      case "learning":
        return <AskAIPage />;
      case "settings":
        return <PlaceholderPage title="Paramètres" />;
      default:
        return <DashboardPage />;
    }
  };

  return (
    <div className="min-h-screen bg-[#F9F9F7] text-[#1F1F2E] font-sans selection:bg-purple-200 selection:text-purple-900 overflow-x-hidden">
      <Sidebar 
        activePage={activePage} 
        onNavigate={setActivePage} 
        isOpen={sidebarOpen}
        setIsOpen={setSidebarOpen}
      />
      
      <div className="lg:pl-64 flex flex-col min-h-screen transition-all duration-300">
        <Topbar onMenuClick={() => setSidebarOpen(true)} />
        
        <main className="flex-1 p-6 lg:p-10 overflow-y-auto">
           {renderPage()}
        </main>
      </div>
      
      <Toaster position="bottom-right" theme="light" />
    </div>
  );
}
