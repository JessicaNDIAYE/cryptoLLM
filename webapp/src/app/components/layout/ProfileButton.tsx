import { Button } from "@/app/components/ui/button";
import { User, LogOut } from "lucide-react";
import { useState } from "react";

export function ProfileButton() {
  const [user, setUser] = useState(() => {
    const storedUser = localStorage.getItem("user");
    return storedUser ? JSON.parse(storedUser) : null;
  });

  const handleLogout = () => {
    localStorage.removeItem("token");
    localStorage.removeItem("user");
    setUser(null);
    window.location.reload();
  };

  if (!user) {
    return (
      <Button variant="ghost" size="icon" className="text-gray-500 hover:text-[#1F1F2E] rounded-full hover:bg-white/50">
        <User className="h-5 w-5" />
      </Button>
    );
  }

  return (
    <div className="flex items-center gap-2">
      <span className="text-sm font-medium text-gray-500">
        {user.prenom} {user.nom}
      </span>
      <Button variant="ghost" size="icon" className="text-gray-500 hover:text-[#1F1F2E] rounded-full hover:bg-white/50">
        <User className="h-5 w-5" />
      </Button>
      <Button
        variant="ghost"
        size="icon"
        className="text-gray-500 hover:text-[#1F1F2E] rounded-full hover:bg-white/50"
        onClick={handleLogout}
      >
        <LogOut className="h-5 w-5" />
      </Button>
    </div>
  );
}