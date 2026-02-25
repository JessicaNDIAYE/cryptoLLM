import { useState } from "react";
import { Eye, EyeOff, User, Lock } from "lucide-react";

interface LoginPageProps {
  onLogin: (user: { email: string; nom: string; prenom: string }) => void;
  onGoToRegister: () => void;
}

export function LoginPage({ onLogin, onGoToRegister }: LoginPageProps) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError("");

    try {
      const res = await fetch("http://localhost:8080/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
      });

      const data = await res.json();

      if (!res.ok) {
        setError(data.detail || "Email ou mot de passe incorrect");
        return;
      }

      const userData = { email: data.email, nom: data.nom, prenom: data.prenom };
      localStorage.setItem("user", JSON.stringify(userData));
      localStorage.setItem("token", data.token);
      onLogin(userData);
    } catch {
      setError("Impossible de contacter le serveur. Vérifiez que le backend est lancé (port 8080).");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-purple-50 to-blue-50">
      <div className="w-full max-w-md bg-white rounded-3xl shadow-2xl p-8">
        {/* Logo */}
        <div className="flex items-center gap-3 mb-8">
          <div className="w-10 h-10 bg-[#1F1F2E] rounded-full flex items-center justify-center">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path
                d="M12 2L15.09 8.26L22 9.27L17 14.14L18.18 21.02L12 17.77L5.82 21.02L7 14.14L2 9.27L8.91 8.26L12 2Z"
                fill="white" stroke="white" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"
              />
            </svg>
          </div>
          <span className="text-xl font-bold text-[#1F1F2E]">InvestBuddy</span>
        </div>

        <h2 className="text-2xl font-bold text-[#1F1F2E] mb-1">Connexion</h2>
        <p className="text-sm text-gray-500 mb-8">
          Bienvenue ! Entrez vos identifiants pour accéder à votre espace.
        </p>

        <form onSubmit={handleSubmit} className="space-y-4">
          {/* Email */}
          <div className="relative">
            <div className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-400 pointer-events-none">
              <User className="h-4 w-4" />
            </div>
            <input
              type="email"
              placeholder="Email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full pl-11 pr-4 py-3 bg-gray-50 border border-gray-200 rounded-xl text-sm placeholder:text-gray-400 focus:outline-none focus:ring-2 focus:ring-purple-300 focus:border-transparent transition-all"
              required
            />
          </div>

          {/* Mot de passe */}
          <div className="relative">
            <div className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-400 pointer-events-none">
              <Lock className="h-4 w-4" />
            </div>
            <input
              type={showPassword ? "text" : "password"}
              placeholder="Mot de passe"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full pl-11 pr-12 py-3 bg-gray-50 border border-gray-200 rounded-xl text-sm placeholder:text-gray-400 focus:outline-none focus:ring-2 focus:ring-purple-300 focus:border-transparent transition-all"
              required
            />
            <button
              type="button"
              onClick={() => setShowPassword(!showPassword)}
              className="absolute right-4 top-1/2 -translate-y-1/2 text-gray-400 hover:text-[#1F1F2E] transition-colors"
            >
              {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
            </button>
          </div>

          {/* Erreur */}
          {error && (
            <div className="text-sm text-red-600 bg-red-50 rounded-xl p-3 border border-red-100">
              {error}
            </div>
          )}

          {/* Bouton connexion */}
          <button
            type="submit"
            disabled={loading}
            className="w-full bg-[#1F1F2E] hover:bg-black text-white rounded-xl py-3 text-sm font-bold transition-all hover:scale-[1.01] active:scale-[0.99] shadow-lg shadow-purple-900/10 disabled:opacity-60 disabled:cursor-not-allowed"
          >
            {loading ? (
              <div className="flex items-center justify-center gap-2">
                <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                Connexion...
              </div>
            ) : (
              "Se connecter"
            )}
          </button>
        </form>

        {/* Info compte */}
        <div className="mt-6 p-4 bg-purple-50 rounded-xl border border-purple-100">
          <p className="text-xs text-purple-700 font-semibold mb-1">Compte de démo :</p>
          <p className="text-xs text-purple-600">📧 jean.dupont@email.com</p>
          <p className="text-xs text-purple-600">🔑 password123</p>
        </div>

        {/* Séparateur */}
        <div className="flex items-center gap-3 mt-6">
          <div className="flex-1 h-px bg-gray-200" />
          <span className="text-xs text-gray-400">ou</span>
          <div className="flex-1 h-px bg-gray-200" />
        </div>

        {/* Bouton inscription */}
        <button
          type="button"
          onClick={onGoToRegister}
          className="mt-4 w-full border-2 border-[#1F1F2E] text-[#1F1F2E] hover:bg-[#1F1F2E] hover:text-white rounded-xl py-3 text-sm font-bold transition-all hover:scale-[1.01] active:scale-[0.99]"
        >
          Créer un compte
        </button>

        <p className="text-center text-xs text-gray-400 mt-3">
          Pas encore de compte ? Inscrivez-vous gratuitement.
        </p>
      </div>
    </div>
  );
}
