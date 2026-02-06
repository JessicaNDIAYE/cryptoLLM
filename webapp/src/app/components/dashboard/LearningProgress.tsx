import { Card, CardContent, CardHeader, CardTitle } from "@/app/components/ui/card";
import { Progress } from "@/app/components/ui/progress";
import { Button } from "@/app/components/ui/button";
import { Trophy, ArrowRight } from "lucide-react";

export function LearningProgress() {
  return (
    <Card className="bg-white border-0 shadow-sm rounded-[2rem] h-full overflow-hidden">
      <CardHeader className="flex flex-row items-center justify-between pb-4 pt-6 px-6">
        <CardTitle className="text-base font-bold text-[#1F1F2E]">Votre Progression</CardTitle>
        <div className="h-8 w-8 rounded-full bg-yellow-50 flex items-center justify-center">
            <Trophy className="h-4 w-4 text-yellow-500" />
        </div>
      </CardHeader>
      <CardContent className="space-y-6 px-6 pb-6">
        <div className="space-y-2">
          <div className="flex justify-between text-xs font-medium">
            <span className="text-gray-500">Fondamentaux</span>
            <span className="text-[#1F1F2E]">80%</span>
          </div>
          <Progress value={80} className="h-2.5 bg-gray-100 [&>div]:bg-[#1F1F2E]" />
        </div>

        <div className="space-y-2">
          <div className="flex justify-between text-xs font-medium">
            <span className="text-gray-500">Stratégies Avancées</span>
            <span className="text-[#1F1F2E]">45%</span>
          </div>
          <Progress value={45} className="h-2.5 bg-gray-100 [&>div]:bg-purple-500" />
        </div>

        <div className="space-y-2">
          <div className="flex justify-between text-xs font-medium">
            <span className="text-gray-500">Gestion de Risque</span>
            <span className="text-[#1F1F2E]">20%</span>
          </div>
          <Progress value={20} className="h-2.5 bg-gray-100 [&>div]:bg-purple-300" />
        </div>
        
        <div className="pt-4">
            <Button className="w-full bg-[#1F1F2E] hover:bg-black text-white text-xs h-10 rounded-xl shadow-lg shadow-purple-900/10">
                Continuer <ArrowRight className="ml-2 h-3.5 w-3.5" />
            </Button>
        </div>
      </CardContent>
    </Card>
  );
}
