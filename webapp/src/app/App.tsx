import { useState } from "react";
import { Sidebar } from "@/app/components/layout/Sidebar";
import { Topbar } from "@/app/components/layout/Topbar";
import { DashboardPage } from "@/app/pages/DashboardPage";
import { AskAIPage } from "@/app/pages/AskAIPage";
import { CryptoLessons } from "@/app/components/dashboard/CryptoLessons";
import { LoginPage } from "@/app/pages/LoginPage";
import { Toaster } from "sonner";

function GlossaryPage({ onLessonClick }: { onLessonClick: (topic: string, question: string) => void }) {
  return (
    <div className="space-y-8 animate-in fade-in duration-700">
      <div className="text-center space-y-4">
        <h1 className="text-3xl font-bold text-[#1F1F2E] tracking-tight">📚 Glossaire Crypto</h1>
        <p className="text-gray-600 max-w-2xl mx-auto">
          Explorez notre glossaire interactif pour apprendre les concepts clés de la crypto et de la finance.
        </p>
      </div>
      <CryptoLessons onLessonClick={onLessonClick} />
    </div>
  );
}

export default function App() {
  const [isLoggedIn, setIsLoggedIn] = useState(() => !!localStorage.getItem("token"));
  const [activePage, setActivePage] = useState("dashboard");
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [prefilledQuestion, setPrefilledQuestion] = useState<string | null>(null);

  const handleNavigate = (page: string) => {
    setActivePage(page);
    if (page !== "learning") {
      setPrefilledQuestion(null);
    }
  };

  const handleLessonClick = (topic: string, question: string) => {
    setPrefilledQuestion(question);
    setActivePage("learning");
  };

  const handleLearnMoreClick = () => {
    setActivePage("glossary");
  };

  if (!isLoggedIn) {
    return (
      <>
        <LoginPage onLogin={() => setIsLoggedIn(true)} />
        <Toaster position="bottom-right" theme="light" />
      </>
    );
  }

  const renderPage = () => {
    switch (activePage) {
      case "dashboard":
        return <DashboardPage onLearnMoreClick={handleLearnMoreClick} />;
      case "glossary":
        return <GlossaryPage onLessonClick={handleLessonClick} />;
      case "trading":
        return <div className="flex flex-col items-center justify-center h-[60vh]"><h2 className="text-2xl font-bold">Marchés & Trading</h2></div>;
      case "risks":
        return <div className="flex flex-col items-center justify-center h-[60vh]"><h2 className="text-2xl font-bold">Analyse de Risques</h2></div>;
      case "learning":
        return <AskAIPage initialQuestion={prefilledQuestion} />;
      case "settings":
        return <div className="flex flex-col items-center justify-center h-[60vh]"><h2 className="text-2xl font-bold">Paramètres</h2></div>;
      default:
        return <DashboardPage onLearnMoreClick={handleLearnMoreClick} />;
    }
  };

  return (
    <div className="min-h-screen bg-[#F9F9F7] text-[#1F1F2E] font-sans selection:bg-purple-200 selection:text-purple-900 overflow-x-hidden">
      <Sidebar 
        activePage={activePage} 
        onNavigate={handleNavigate} 
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