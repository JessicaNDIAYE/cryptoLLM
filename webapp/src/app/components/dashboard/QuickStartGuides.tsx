import { Card, CardContent } from "@/app/components/ui/card";
import { Badge } from "@/app/components/ui/badge";
import { PlayCircle } from "lucide-react";

export function QuickStartGuides() {
  const guides = [
    { title: "Premiers pas en Crypto", category: "Débutant", duration: "5 min", image: "https://images.unsplash.com/photo-1621761191319-c6fb62004040?auto=format&fit=crop&q=80&w=600" },
    { title: "Comprendre les ETFs", category: "Intermédiaire", duration: "8 min", image: "https://images.unsplash.com/photo-1611974765270-ca1258634369?auto=format&fit=crop&q=80&w=600" },
    { title: "Analyse Technique", category: "Avancé", duration: "12 min", image: "https://images.unsplash.com/photo-1642543492481-44e81e3914a7?auto=format&fit=crop&q=80&w=600" },
    { title: "Gestion des Risques", category: "Essentiel", duration: "6 min", image: "https://images.unsplash.com/photo-1604594849809-dfedbc827105?auto=format&fit=crop&q=80&w=600" },
  ];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between px-1">
         <h2 className="text-xl font-bold text-[#1F1F2E]">Guides de Démarrage</h2>
         <button className="text-sm font-medium text-purple-600 hover:text-purple-800 transition-colors">Voir tout</button>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {guides.map((guide, i) => (
          <Card key={i} className="group relative overflow-hidden border-0 bg-white shadow-sm hover:shadow-xl hover:shadow-purple-100 transition-all duration-300 rounded-[2rem] cursor-pointer">
            <div className="h-40 w-full overflow-hidden relative">
                <div className="absolute inset-0 bg-purple-900/10 group-hover:bg-transparent transition-colors z-10" />
                <img src={guide.image} alt={guide.title} className="w-full h-full object-cover transition-transform duration-700 group-hover:scale-105" />
            </div>
            
            <CardContent className="relative z-20 p-5 pt-4">
               <div className="flex justify-between items-start mb-3">
                 <Badge variant="secondary" className="bg-purple-50 text-purple-700 border-purple-100 backdrop-blur-md text-[10px] h-6 px-2.5 font-medium">
                    {guide.category}
                 </Badge>
                 <span className="text-[11px] text-gray-400 font-medium">{guide.duration}</span>
               </div>
               
               <h3 className="font-bold text-base text-[#1F1F2E] leading-snug mb-4 pr-2">
                  {guide.title}
               </h3>
               
               <div className="flex items-center text-sm font-medium text-gray-400 group-hover:text-purple-600 transition-colors">
                  <PlayCircle className="w-4 h-4 mr-2" />
                  Commencer
               </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}
