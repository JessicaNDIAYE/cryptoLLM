import { Search, Bell, Wallet, User } from "lucide-react";
import { Button } from "@/app/components/ui/button";
import { Input } from "@/app/components/ui/input";

interface TopbarProps {
  onMenuClick: () => void;
}

export function Topbar({ onMenuClick }: TopbarProps) {
  return (
    <header className="h-20 bg-[#F9F9F7]/80 backdrop-blur-md sticky top-0 z-30 flex items-center justify-between px-6 lg:px-10 transition-all">
      <div className="flex items-center gap-4 flex-1">
        <Button variant="ghost" size="icon" className="lg:hidden -ml-2 text-[#1F1F2E]" onClick={onMenuClick}>
          <svg
            xmlns="http://www.w3.org/2000/svg"
            width="24"
            height="24"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
          >
            <line x1="4" x2="20" y1="12" y2="12" />
            <line x1="4" x2="20" y1="6" y2="6" />
            <line x1="4" x2="20" y1="18" y2="18" />
          </svg>
        </Button>
        
        <div className="hidden md:flex items-center gap-6 text-sm font-medium text-gray-500">
             <span className="text-[#1F1F2E] cursor-pointer">Tableau de bord</span>
        </div>
      </div>

      <div className="flex items-center gap-4">
         <div className="relative hidden md:block w-64 mr-4">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
            <Input 
              placeholder="Rechercher..." 
              className="pl-10 bg-white border-none shadow-sm hover:shadow-md transition-shadow rounded-full h-10 text-sm placeholder:text-gray-400"
            />
         </div>

        <Button variant="ghost" size="icon" className="text-gray-500 hover:text-[#1F1F2E] rounded-full hover:bg-white/50">
          <Bell className="h-5 w-5" />
          <span className="absolute top-2.5 right-2.5 h-1.5 w-1.5 bg-red-500 rounded-full border border-[#F9F9F7]" />
        </Button>
        
        <Button className="hidden sm:flex gap-2 bg-[#1F1F2E] hover:bg-black text-white rounded-full h-10 px-5 text-xs font-medium shadow-lg shadow-purple-900/10">
          <Wallet className="h-3.5 w-3.5" />
          Connect Wallet
        </Button>
      </div>
    </header>
  );
}
