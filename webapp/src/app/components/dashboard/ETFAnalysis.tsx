import { Card, CardContent, CardHeader, CardTitle } from "@/app/components/ui/card";
import { Badge } from "@/app/components/ui/badge";
import { CheckCircle2, HelpCircle } from "lucide-react";
import { Button } from "@/app/components/ui/button";
import { AreaChart, Area, ResponsiveContainer } from 'recharts';

const data = [
  { day: 'Lun', val: 40 },
  { day: 'Mar', val: 35 },
  { day: 'Mer', val: 50 },
  { day: 'Jeu', val: 45 },
  { day: 'Ven', val: 60 },
  { day: 'Sam', val: 55 },
  { day: 'Dim', val: 70 },
];

export function ETFAnalysis() {
  return (
    <Card className="bg-white border-0 shadow-sm rounded-[2rem] h-full relative overflow-hidden">
      <div className="absolute inset-0 bg-gradient-to-br from-purple-50/50 to-transparent pointer-events-none" />
      
      <CardHeader className="flex flex-row items-center justify-between pb-2 pt-6 px-6 relative z-10">
         <div>
            <CardTitle className="text-base font-bold text-[#1F1F2E]">Analyse de Résultats</CardTitle>
            <p className="text-xs text-gray-400 mt-1 font-medium">IWDA - iShares Core MSCI World</p>
         </div>
         <Badge variant="outline" className="border-purple-200 text-purple-700 bg-purple-50 px-3 py-1 rounded-full">Score: 92/100</Badge>
      </CardHeader>
      
      <CardContent className="space-y-6 relative z-10 px-6 pb-6">
         <div className="grid grid-cols-2 gap-6">
             <div className="space-y-5">
                <div className="space-y-2">
                    <div className="flex justify-between text-xs font-medium">
                        <span className="text-gray-500">Niveau de Risque</span>
                        <span className="text-orange-500 font-bold">Modéré</span>
                    </div>
                    <div className="h-2 w-full bg-gray-100 rounded-full overflow-hidden">
                        <div className="h-full bg-gradient-to-r from-green-400 via-orange-400 to-red-400 w-[71%]" />
                    </div>
                </div>
                
                <div className="flex flex-col gap-3">
                    <div className="flex items-center text-xs font-medium text-gray-600">
                        <CheckCircle2 className="w-4 h-4 text-green-500 mr-2.5" />
                        TER: 0.20% (Faible)
                    </div>
                    <div className="flex items-center text-xs font-medium text-gray-600">
                         <CheckCircle2 className="w-4 h-4 text-green-500 mr-2.5" />
                         Réplication Physique
                    </div>
                    <div className="flex items-center text-xs font-medium text-gray-600">
                         <HelpCircle className="w-4 h-4 text-blue-500 mr-2.5" />
                         Pas de couverture (Unhedged)
                    </div>
                </div>
             </div>
             
             <div className="h-[120px] w-full bg-white rounded-2xl border border-gray-100 p-3 shadow-sm">
                 <p className="text-[10px] text-gray-400 mb-2 font-medium uppercase tracking-wide">Performance (1A)</p>
                 <ResponsiveContainer width="100%" height="80%">
                    <AreaChart data={data}>
                        <defs>
                            <linearGradient id="colorVal" x1="0" y1="0" x2="0" y2="1">
                                <stop offset="5%" stopColor="#8b5cf6" stopOpacity={0.2}/>
                                <stop offset="95%" stopColor="#8b5cf6" stopOpacity={0}/>
                            </linearGradient>
                        </defs>
                        <Area type="monotone" dataKey="val" stroke="#8b5cf6" strokeWidth={2} fill="url(#colorVal)" />
                    </AreaChart>
                 </ResponsiveContainer>
             </div>
         </div>
         
         <div className="bg-[#F8F8F6] p-4 rounded-xl border border-gray-100">
             <div className="flex items-start gap-3">
                 <div className="w-2 h-2 rounded-full bg-purple-500 mt-2 shrink-0 shadow-[0_0_8px_rgba(168,85,247,0.4)]" />
                 <p className="text-xs text-gray-600 leading-relaxed font-medium">
                    <span className="font-bold text-[#1F1F2E]">L'avis d'InvestBuddy :</span> Cet ETF est idéal pour une stratégie long-terme ("Buy & Hold"). Il offre une diversification massive sur 23 pays développés.
                 </p>
             </div>
             <div className="mt-4 flex gap-3">
                 <Button variant="outline" size="sm" className="h-8 text-xs border-gray-200 text-gray-600 hover:text-[#1F1F2E] hover:bg-white rounded-lg">En savoir plus</Button>
                 <Button variant="ghost" size="sm" className="h-8 text-xs text-gray-400 hover:text-[#1F1F2E]">Notifier changements</Button>
             </div>
         </div>
      </CardContent>
    </Card>
  );
}
