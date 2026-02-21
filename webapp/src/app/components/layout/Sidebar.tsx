import {
  LayoutDashboard,
  BookOpen,
  ShieldAlert,
  Bot,
  Settings,
  LogOut
} from "lucide-react";
import { cn } from "@/lib/utils";
import { Button } from "@/app/components/ui/button";

interface SidebarProps {
  activePage: string;
  onNavigate: (page: string) => void;
  isOpen: boolean;
  setIsOpen: (isOpen: boolean) => void;
}

export function Sidebar({ activePage, onNavigate, isOpen, setIsOpen }: SidebarProps) {
  const menuItems = [
    { id: "dashboard", label: "Tableau de bord", icon: LayoutDashboard },
    { id: "glossary", label: "Glossaire", icon: BookOpen },
    { id: "risks", label: "Analyses de Risque", icon: ShieldAlert },
    { id: "learning", label: "Ask AI", icon: Bot },
    { id: "settings", label: "Paramètres", icon: Settings },
  ];

  return (
    <>
      {/* Mobile Overlay */}
      <div 
        className={cn(
          "fixed inset-0 bg-black/20 z-40 lg:hidden transition-opacity backdrop-blur-sm",
          isOpen ? "opacity-100" : "opacity-0 pointer-events-none"
        )} 
        onClick={() => setIsOpen(false)}
      />

      {/* Sidebar */}
      <aside 
        className={cn(
          "fixed top-0 left-0 z-50 h-screen w-64 bg-[#F9F9F7] border-r border-[#E5E5E0] transition-transform duration-300 ease-in-out lg:translate-x-0",
          isOpen ? "translate-x-0" : "-translate-x-full"
        )}
      >
        <div className="flex flex-col h-full px-6 py-8">
          {/* Logo */}
          <div className="h-10 flex items-center mb-10">
            <div className="w-8 h-8 bg-[#1F1F2E] rounded-full flex items-center justify-center mr-3">
               <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M12 2L15.09 8.26L22 9.27L17 14.14L18.18 21.02L12 17.77L5.82 21.02L7 14.14L2 9.27L8.91 8.26L12 2Z" fill="white" stroke="white" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
               </svg>
            </div>
            <span className="text-xl font-semibold text-[#1F1F2E] tracking-tight">
              InvestBuddy
            </span>
          </div>

          {/* Navigation */}
          <nav className="flex-1 space-y-1">
            {menuItems.map((item) => {
              const Icon = item.icon;
              const isActive = activePage === item.id;
              
              return (
                <button
                  key={item.id}
                  onClick={() => {
                    onNavigate(item.id);
                    setIsOpen(false);
                  }}
                  className={cn(
                    "w-full flex items-center gap-3 px-4 py-3 rounded-full text-sm font-medium transition-all duration-200 group relative",
                    isActive 
                      ? "bg-[#1F1F2E] text-white shadow-lg shadow-purple-900/10" 
                      : "text-gray-500 hover:bg-white hover:text-[#1F1F2E]"
                  )}
                >
                  <Icon className={cn("h-4 w-4", isActive ? "text-purple-200" : "text-gray-400 group-hover:text-[#1F1F2E]")} />
                  {item.label}
                </button>
              );
            })}
          </nav>

          {/* Footer */}
          <div className="mt-auto pt-8">
            <div className="bg-[#EBEBE8] rounded-2xl p-5 relative overflow-hidden group">
               <div className="absolute top-0 right-0 w-20 h-20 bg-purple-200/50 rounded-full blur-2xl -mr-10 -mt-10 transition-transform group-hover:scale-150" />
               <h4 className="text-sm font-semibold text-[#1F1F2E] mb-1 relative z-10">Plan Premium</h4>
               <p className="text-xs text-gray-500 mb-3 relative z-10 leading-relaxed">Débloquez l'IA illimitée et les analyses expertes.</p>
               <Button size="sm" className="w-full bg-[#1F1F2E] hover:bg-black text-white rounded-full text-xs h-8 relative z-10">
                  Upgrade
               </Button>
            </div>
            
            <button className="flex items-center gap-3 mt-8 px-4 text-sm font-medium text-gray-500 hover:text-[#1F1F2E] transition-colors">
              <LogOut className="h-4 w-4" />
              Déconnexion
            </button>
          </div>
        </div>
      </aside>
    </>
  );
}
