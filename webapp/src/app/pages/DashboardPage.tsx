import { QuickStartGuides } from "@/app/components/dashboard/QuickStartGuides";
import { LearningProgress } from "@/app/components/dashboard/LearningProgress";
import { MarketSentiment } from "@/app/components/dashboard/MarketSentiment";
import { TopETFs } from "@/app/components/dashboard/TopETFs";
import { ETFAnalysis } from "@/app/components/dashboard/ETFAnalysis";
import { Button } from "@/app/components/ui/button";
import { ArrowRight } from "lucide-react";

export function DashboardPage() {
  return (
    <div className="space-y-10 animate-in fade-in duration-700 pb-10">
      
      {/* Hero Section - Bloom Style */}
      <section className="relative w-full rounded-[2.5rem] overflow-hidden bg-[#EAE4F2] min-h-[400px] flex items-center">
         {/* Background Decoration */}
         <div className="absolute inset-0 z-0">
            <div className="absolute top-0 left-0 w-full h-full bg-gradient-to-br from-[#E8E2F7] via-[#F2EEFA] to-[#E3DDF2] opacity-80" />
            <div className="absolute top-[-20%] right-[-10%] w-[600px] h-[600px] bg-purple-300/30 rounded-full blur-[100px]" />
            <div className="absolute bottom-[-20%] left-[-10%] w-[500px] h-[500px] bg-blue-200/30 rounded-full blur-[80px]" />
            
            {/* 3D Elements (Simulated with Unsplash Images cropped/masked) */}
            <img 
                src="https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?auto=format&fit=crop&q=80&w=800" 
                alt="Abstract 3D Shape" 
                className="absolute right-0 bottom-0 h-[450px] object-cover mix-blend-multiply opacity-60 mask-image-gradient"
                style={{ maskImage: 'linear-gradient(to left, black, transparent)' }}
            />
         </div>

         <div className="relative z-10 px-10 md:px-16 max-w-2xl">
            <div className="mb-6 inline-flex items-center gap-2 px-3 py-1 rounded-full bg-white/60 backdrop-blur-sm border border-white/40">
                <span className="w-2 h-2 rounded-full bg-[#1F1F2E]" />
                <span className="text-xs font-semibold text-[#1F1F2E] uppercase tracking-wider">InvestBuddy 2.0</span>
            </div>
            
            <h1 className="text-5xl md:text-6xl font-bold text-[#1F1F2E] mb-6 leading-[1.1] tracking-tight">
               Where Money <br/>
               <span className="text-transparent bg-clip-text bg-gradient-to-r from-purple-600 to-blue-600">Grows</span>
            </h1>
            
            <p className="text-lg text-gray-600 mb-8 leading-relaxed max-w-lg">
               Une plateforme d'apprentissage programmable et pilotée par l'utilité, conçue pour une intégration native de vos connaissances financières.
            </p>
            
            <div className="flex gap-4">
                <Button className="h-12 px-8 rounded-full bg-[#1F1F2E] hover:bg-black text-white text-sm font-medium shadow-xl shadow-purple-900/10 transition-transform hover:scale-105">
                    Commencer maintenant
                </Button>
                <Button variant="outline" className="h-12 px-8 rounded-full border-2 border-[#1F1F2E]/10 bg-transparent hover:bg-white text-[#1F1F2E] text-sm font-medium">
                    En savoir plus
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
         <div className="xl:col-span-3 h-full">
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
