import { Card, CardContent, CardHeader, CardTitle } from "@/app/components/ui/card";
import { Bot, MessageSquare, X, Send } from "lucide-react";
import { Button } from "@/app/components/ui/button";

export function AskAI() {
  return (
    <Card className="bg-white border-0 shadow-sm rounded-[2rem] h-full flex flex-col overflow-hidden">
      <CardHeader className="flex flex-row items-center justify-between pb-4 pt-6 px-6 border-b border-gray-50">
        <div className="flex items-center gap-2.5">
            <div className="bg-purple-100 p-1.5 rounded-lg">
                <Bot className="h-4 w-4 text-purple-600" />
            </div>
            <CardTitle className="text-base font-bold text-[#1F1F2E]">Assistant IA</CardTitle>
        </div>
        <X className="h-4 w-4 text-gray-400 cursor-pointer hover:text-[#1F1F2E] transition-colors" />
      </CardHeader>
      
      <CardContent className="flex-1 p-5 flex flex-col gap-4 bg-[#FDFCFC]">
        <div className="space-y-3">
             <div className="bg-white p-4 rounded-2xl border border-gray-100 hover:border-purple-200 hover:shadow-md transition-all cursor-pointer group shadow-sm">
                 <div className="flex gap-3">
                     <div className="h-9 w-9 rounded-full bg-purple-50 flex items-center justify-center shrink-0">
                         <MessageSquare className="h-4 w-4 text-purple-500" />
                     </div>
                     <div>
                         <h4 className="text-sm font-bold text-[#1F1F2E] group-hover:text-purple-700 transition-colors">Volatilité détectée</h4>
                         <p className="text-xs text-gray-500 mt-1 leading-relaxed">Le marché crypto montre des signes de forte variation aujourd'hui.</p>
                     </div>
                 </div>
             </div>
             
             <div className="bg-white p-4 rounded-2xl border border-gray-100 hover:border-blue-200 hover:shadow-md transition-all cursor-pointer group shadow-sm">
                 <div className="flex gap-3">
                     <div className="h-9 w-9 rounded-full bg-blue-50 flex items-center justify-center shrink-0">
                         <Bot className="h-4 w-4 text-blue-500" />
                     </div>
                     <div>
                         <h4 className="text-sm font-bold text-[#1F1F2E] group-hover:text-blue-700 transition-colors">Nouveau module dispo</h4>
                         <p className="text-xs text-gray-500 mt-1 leading-relaxed">"Comprendre les obligations" est maintenant en ligne.</p>
                     </div>
                 </div>
             </div>
        </div>

        <div className="mt-auto relative">
             <div className="bg-white border border-gray-100 rounded-2xl p-2 pl-4 flex items-center gap-3 shadow-sm focus-within:ring-2 focus-within:ring-purple-100 transition-all">
                 <div className="h-6 w-6 rounded-full bg-gradient-to-tr from-purple-500 to-blue-500 shrink-0" />
                 <input 
                    type="text" 
                    placeholder="Posez une question..." 
                    className="bg-transparent border-none text-sm text-[#1F1F2E] placeholder:text-gray-400 focus:outline-none flex-1 w-full font-medium"
                 />
                 <Button size="icon" className="h-9 w-9 rounded-xl bg-[#1F1F2E] hover:bg-black text-white shadow-lg shadow-purple-900/10">
                     <Send className="h-4 w-4" />
                 </Button>
             </div>
        </div>
      </CardContent>
    </Card>
  );
}
