import { Button } from "@/app/components/ui/button";
import { User, LogOut } from "lucide-react";

interface ProfileButtonProps {
  onLogout: () => void;
}

export function ProfileButton({ onLogout }: ProfileButtonProps) {
  const storedUser = localStorage.getItem("user");
  const user = storedUser ? JSON.parse(storedUser) : null;

  const handleLogout = () => {
    localStorage.removeItem("token");
    localStorage.removeItem("user");
    onLogout();
  };

  if (!user) {
    return (
      <Button
        variant="ghost"
        size="icon"
        className="text-gray-500 hover:text-[#1F1F2E] rounded-full hover:bg-white/50"
      >
        <User className="h-5 w-5" />
      </Button>
    );
  }

  return (
    <div className="flex items-center gap-2">
      {/* Nom de l'utilisateur */}
      <div className="hidden sm:flex items-center gap-2 bg-white rounded-full px-4 py-2 shadow-sm border border-gray-100">
        <div className="w-6 h-6 bg-[#1F1F2E] rounded-full flex items-center justify-center text-white text-xs font-bold flex-shrink-0">
          {user.prenom?.[0]?.toUpperCase() ?? "?"}
        </div>
        <span className="text-sm font-medium text-[#1F1F2E]">
          {user.prenom} {user.nom}
        </span>
      </div>

      {/* Bouton déconnexion */}
      <Button
        variant="ghost"
        size="icon"
        title="Se déconnecter"
        className="text-gray-500 hover:text-red-600 rounded-full hover:bg-red-50 transition-colors"
        onClick={handleLogout}
      >
        <LogOut className="h-5 w-5" />
      </Button>
    </div>
  );
}
