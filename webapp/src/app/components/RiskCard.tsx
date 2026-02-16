import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/app/components/ui/card"
import { motion } from "motion/react"


interface RiskCardProps {
  currency?: string; // "BTC", "ETH", etc.
  volatility?: number;
  direction?: string;  // "up" ou "down"
  aiAnalysis?: string; // Le texte de ton agent RAG
}

export function RiskCard({currency = "BTC" ,volatility = 0, direction = "up", aiAnalysis }: RiskCardProps) {
  // Normaliser la volatilité pour l'affichage (0 à 0.05 correspond à 0% à 100%)
  const normalizedScore = Math.min(volatility / 0.05, 1);

  return (
    <Card className="w-full bg-card/50 backdrop-blur-sm border-border/40 overflow-hidden relative">
      <div className="absolute inset-0 bg-gradient-to-br from-blue-500/5 to-purple-500/5 pointer-events-none" />
      <CardHeader>
        <CardTitle>Analyse de Risque en Direct du {currency}</CardTitle>
        <CardDescription>Basé sur le modèle ML et les news récentes</CardDescription>
      </CardHeader>
      <CardContent className="flex flex-col items-center justify-center pt-2 pb-8">
         <div className="relative w-64 h-32">
            <svg viewBox="0 0 100 50" className="w-full h-full overflow-visible">
              <defs>
                <linearGradient id="riskGradient" x1="0%" y1="0%" x2="100%" y2="0%">
                   <stop offset="0%" stopColor="#22c55e" /> {/* Vert (Faible) */}
                   <stop offset="50%" stopColor="#eab308" /> {/* Jaune (Moyen) */}
                   <stop offset="100%" stopColor="#ef4444" /> {/* Rouge (Haut) */}
                </linearGradient>
              </defs>
              <path d="M 10 50 A 40 40 0 0 1 90 50" fill="none" stroke="currentColor" strokeWidth="6" className="text-muted/20" strokeLinecap="round" />
              <motion.path 
                d="M 10 50 A 40 40 0 0 1 90 50" 
                fill="none" 
                stroke="url(#riskGradient)" 
                strokeWidth="6" 
                strokeLinecap="round"
                initial={{ pathLength: 0 }}
                animate={{ pathLength: normalizedScore }}
                transition={{ duration: 1.5, ease: "easeOut" }}
              />
            </svg>
            <div className="absolute bottom-0 left-1/2 -translate-x-1/2 translate-y-1/3 flex flex-col items-center">
                 <span className="text-2xl font-bold">{(volatility * 100).toFixed(2)}%</span>
                 <span className="text-[10px] text-muted-foreground uppercase">Volatilité Prédite</span>
            </div>
         </div>
         
         <div className="mt-8 text-center space-y-4">
            <div className="flex gap-2 justify-center">
                <span className={`px-3 py-1 rounded-full text-xs font-bold ${direction === 'up' ? 'bg-green-500/20 text-green-500' : 'bg-red-500/20 text-red-500'}`}>
                    Tendance : {direction === 'up' ? 'HAUSSIÈRE' : 'BAISSIÈRE'}
                </span>
            </div>
            
            {/* Affichage de l'analyse de l'agent RAG */}
            {aiAnalysis && (
                <motion.div 
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="text-sm text-left bg-muted/30 p-4 rounded-xl border border-border/20"
                >
                    <p className="font-semibold mb-1">🤖 Conseil de l'Agent :</p>
                    <p className="text-muted-foreground italic">"{aiAnalysis}"</p>
                </motion.div>
            )}
         </div>
      </CardContent>
    </Card>
  )
}
