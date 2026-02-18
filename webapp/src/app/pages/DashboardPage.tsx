import { QuickStartGuides } from "@/app/components/dashboard/QuickStartGuides";
import { LearningProgress } from "@/app/components/dashboard/LearningProgress";
import { MarketSentiment } from "@/app/components/dashboard/MarketSentiment";
import { TopETFs } from "@/app/components/dashboard/TopETFs";
import { ETFAnalysis } from "@/app/components/dashboard/ETFAnalysis";
import { Button } from "@/app/components/ui/button";
import React, { useState } from "react";
import { RiskCard } from "@/app/components/RiskCard";
import { ArrowRight } from "lucide-react";

export function DashboardPage() {
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState<{volatility: number, direction: string, analysis: string} | null>(null);

  const runAnalysis = async () => {
    setLoading(true);
    try {
      // API de Prédiction (Port 8000)
      const predRes = await fetch('http://localhost:8080/predictBTC', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
          currency: "BTC", 
          Open: 42000, 
          High: 43000, 
          Low: 41500, 
          Close: 42500,
          Volume: 1000, 
          RSI: 55, 
          ATR: 0.02, 
          VolumeChange: 0.1, 
          SMA_20: 42000, 
          EMA_50: 41000
        })
      });
      const predData = await predRes.json();

      // API Agent/RAG (Port 4000)
      const agentRes = await fetch('http://localhost:4000/analyzeRisk', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
          prediction_data: predData.prediction, // Envoi de volatility et direction
          user_query: "Pourquoi le bitcoin à un pourcentage de volatilité de " + (predData.prediction.volatility * 100).toFixed(2) + "% et une tendance " + predData.prediction.direction + " ?"
        })
      });
      const agentData = await agentRes.json();

      // Mise à jour de l'interface avec les données reçues
      setResults({
        volatility: predData.prediction.volatility,
        direction: predData.prediction.direction,
        analysis: agentData.analysis
      });
    } catch (e) {
      console.error("Erreur lors de l'analyse :", e);
    } finally {
      setLoading(false);
    }
  };
  return (
    <div className="space-y-10 animate-in fade-in duration-700 pb-10">
      <section className="relative w-full rounded-[2.5rem] overflow-hidden bg-[#EAE4F2] min-h-[400px] flex items-center">
          <div className="absolute inset-0 z-0">
             <div className="absolute top-0 left-0 w-full h-full bg-gradient-to-br from-[#E8E2F7] via-[#F2EEFA] to-[#E3DDF2] opacity-80" />
          </div>

          <div className="relative z-10 px-10 md:px-16 max-w-2xl">
            <h1 className="text-5xl md:text-6xl font-bold text-[#1F1F2E] mb-6 leading-[1.1]">
                Where Money <br/>
                <span className="text-transparent bg-clip-text bg-gradient-to-r from-purple-600 to-blue-600">Grows</span>
            </h1>
            
            <p className="text-lg text-gray-600 mb-8">
                Plateforme pilotée par l'IA pour vos investissements cryptos.
            </p>
            
            <div className="flex gap-4">
                <Button 
                    onClick={runAnalysis} 
                    disabled={loading} 
                    className="h-12 px-8 rounded-full bg-[#1F1F2E] hover:bg-black text-white"
                >
                    {loading ? "Analyse en cours..." : "Lancer l'analyse de risque"}
                </Button>
            </div>
          </div>
      </section>

      {/* Quick Start Guides Section */}
      <section>
        <QuickStartGuides />
      </section>

      {/* Main Grid - Middle Section */}
      <section className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-12 gap-8 h-auto xl:h-[380px]">
         <div className="md:col-span-4">
            <RiskCard 
              volatility={results?.volatility} 
              direction={results?.direction}
              aiAnalysis={results?.analysis}
            />
         </div>
         <div className="">
            <LearningProgress />
         </div>
         <div className="xl:col-span-4 h-full">
            <MarketSentiment />
         </div>
         <div className="xl:col-span-5 h-full">
            <TopETFs />
         </div>
      </section>

      {/* Bottom Grid - Analysis */}
      <section className="grid grid-cols-1 gap-8 h-auto">
         <div className="h-full">
            <ETFAnalysis />
         </div>
      </section>
      
      <div className="flex justify-between items-center text-xs font-medium text-gray-400 pt-10 pb-4 border-t border-gray-200/50">
         <span>InvestBuddy © 2026. Design inspired by BloomFi.</span>
         <div className="flex gap-6">
             <a href="#" className="hover:text-[#1F1F2E] transition-colors">Privacy</a>
             <a href="#" className="hover:text-[#1F1F2E] transition-colors">Terms</a>
             <a href="#" className="hover:text-[#1F1F2E] transition-colors">Cookies</a>
         </div>
      </div>
    </div>
  );
}
