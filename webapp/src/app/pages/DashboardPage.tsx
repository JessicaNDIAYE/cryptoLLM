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
  const [selectedCurrency, setSelectedCurrency] = useState("BTCUSDT");
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState<{volatility: number, direction: string, analysis: string} | null>(null);

  const availableCurrencies = [
    { value: "BTCUSDT", label: "Bitcoin (BTC)" },
    { value: "ETHUSDT", label: "Ethereum (ETH)" },
   //  { value: "SOLUSDT", label: "Solana (SOL)" },
   //  { value: "XRPUSDT", label: "Ripple (XRP)" },
   //  { value: "ADAUSDT", label: "Cardano (ADA)" },
   //  { value: "AVAXUSDT", label: "Avalanche (AVAX)" },
  ];

  const runAnalysis = async () => {
    setLoading(true);
    try {
      // API de Prédiction (Port 8080)
      const predRes = await fetch('http://localhost:8080/predict', { 
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                currency: selectedCurrency,
                Open: 42000, High: 43000, Low: 41500, Close: 42500,
                Volume: 1000, RSI: 55, ATR: 0.02, VolumeChange: 0.1, SMA_20: 42000, EMA_50: 41000
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
      <section className="relative w-full rounded-[3rem] overflow-hidden bg-gradient-to-br from-[#F0EBFA] to-[#FFFFFF] min-h-[450px] flex items-center shadow-xl border border-white/50">
          <div className="relative z-10 px-10 md:px-20 w-full flex flex-col md:flex-row justify-between items-center gap-10">
            <div className="max-w-2xl">
                <div className="inline-flex items-center gap-2 bg-purple-100 text-purple-700 px-4 py-1.5 rounded-full text-sm font-semibold mb-6">
                    <span className="relative flex h-2 w-2">
                        <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-purple-400 opacity-75"></span>
                        <span className="relative inline-flex rounded-full h-2 w-2 bg-purple-500"></span>
                    </span>
                    IA Analyse en temps réel
                </div>
                
                <h1 className="text-5xl md:text-7xl font-extrabold text-[#1F1F2E] mb-6 tracking-tight leading-tight">
                    Smart Crypto <br/>
                    <span className="text-transparent bg-clip-text bg-gradient-to-r from-purple-600 to-blue-500">Insights</span>
                </h1>
                
                <p className="text-xl text-gray-500 mb-10 max-w-md">
                    Anticipez les mouvements de marché grâce à nos modèles de Deep Learning et l'analyse de sentiment.
                </p>
                
                <div className="flex flex-wrap gap-4 items-center">
                    <div className="relative">
                        <select 
                            value={selectedCurrency} 
                            onChange={(e) => setSelectedCurrency(e.target.value)}
                            className="appearance-none bg-white border-2 border-purple-100 hover:border-purple-300 rounded-2xl px-6 py-4 pr-12 text-sm font-bold transition-all shadow-sm focus:outline-none focus:ring-2 focus:ring-purple-500/20"
                        >
                            {availableCurrencies.map(c => (
                                <option key={c.value} value={c.value}>{c.label}</option>
                            ))}
                        </select>
                        <div className="absolute right-4 top-1/2 -translate-y-1/2 pointer-events-none text-gray-400">
                            <ArrowRight size={16} className="rotate-90" />
                        </div>
                    </div>
                    
                    <Button 
                        onClick={runAnalysis} 
                        disabled={loading}
                        className="bg-[#1F1F2E] hover:bg-black text-white rounded-2xl px-8 py-7 text-md font-bold transition-all hover:scale-105 active:scale-95 shadow-lg shadow-purple-200"
                    >
                        {loading ? (
                            <div className="flex items-center gap-2">
                                <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                                Analyse...
                            </div>
                        ) : "Lancer l'Analyse Prédictive"}
                    </Button>
                </div>
            </div>

            {/* Preview visuelle facultative à droite */}
            <div className="hidden lg:block w-full max-w-sm">
                <div className="bg-white/40 backdrop-blur-md rounded-[2rem] p-8 border border-white/60 shadow-inner rotate-3 hover:rotate-0 transition-transform duration-500">
                    <div className="text-xs font-bold text-gray-400 mb-4 uppercase tracking-widest">Dernière Prédiction</div>
                    <div className="text-3xl font-black text-[#1F1F2E] mb-2">{selectedCurrency.replace('USDT','')}</div>
                    <div className="text-green-500 font-bold flex items-center gap-1">
                        <ArrowRight size={16} className="-rotate-45" /> +2.4% attendu
                    </div>
                </div>
            </div>
          </div>
      </section>

      {/* Quick Start Guides Section */}
      <section>
        <QuickStartGuides />
      </section>

      
      {/* Main Grid - Middle Section */}
      <section className="w-full">
         <RiskCard 
            currency={selectedCurrency}
            volatility={results?.volatility} 
            direction={results?.direction}
            aiAnalysis={results?.analysis}
         />
      </section>
      <section className="grid grid-cols-1 md:grid-cols-6 xl:grid-cols-12 gap-8 items-start">
  
         {/* Colonne Gauche : RiskCard (Prend plus de place car le texte RAG est long) */}
         {/* <div className="md:col-span-3 xl:col-span-4 h-full">
            <RiskCard 
               currency={selectedCurrency}
               volatility={results?.volatility} 
               direction={results?.direction}
               aiAnalysis={results?.analysis}
            />
         </div> */}

         {/* Colonne Milieu : Learning & Sentiment */}
         <div className="md:col-span-3 xl:col-span-4 flex flex-col gap-8 h-full">
            <div className="flex-1">
               <LearningProgress />
            </div>
            <div className="flex-1">
               <MarketSentiment />
            </div>
         </div>

         {/* Colonne Droite : TopETFs */}
         <div className="md:col-span-6 xl:col-span-4 h-full">
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
