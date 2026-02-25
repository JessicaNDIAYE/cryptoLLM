import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/app/components/ui/card"
import { motion } from "motion/react"


interface RiskCardProps {
  currency?: string; // "BTC", "ETH", etc.
  volatility?: number;
  direction?: string;  // "up" ou "down"
  aiAnalysis?: string; // Le texte de ton agent RAG
}

export function RiskCard({currency = "BTCUSDT" ,volatility = 0, direction = "up", aiAnalysis }: RiskCardProps) {
  const displayCurrency = currency.replace("USDT", "");
  // Normaliser la volatilité pour l'affichage (0 à 0.05 correspond à 0% à 100%)
  const normalizedScore = Math.min(volatility / 0.05, 1);

  return (
    <Card className="w-full bg-card/50 backdrop-blur-sm border-border/40 overflow-hidden relative">
      <div className="absolute inset-0 bg-gradient-to-br from-blue-500/5 to-purple-500/5 pointer-events-none" />
      <CardHeader>
        <div className="flex justify-between items-center">
          <div>
            <CardTitle>Analyse de Risque : {displayCurrency}</CardTitle>
            <CardDescription>Modèles Prédictifs & agent conseillé</CardDescription>
          </div>
          {/* Badge de la monnaie active */}
          <div className="bg-primary/10 text-primary text-xs font-mono px-2 py-1 rounded border border-primary/20">
            {currency}
          </div>
        </div>
      </CardHeader>
      <CardContent className="flex flex-col items-center justify-center pt-2 pb-8">
         <div className="relative w-64 h-32">
            <svg viewBox="0 0 100 50" className="w-full h-full overflow-visible">
              <defs>
                <linearGradient id="riskGradient" x1="0%" y1="0%" x2="100%" y2="0%">
                   <stop offset="0%" stopColor="#22c55e" /> 
                   <stop offset="50%" stopColor="#eab308" />
                   <stop offset="100%" stopColor="#ef4444" /> 
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
            <div className="flex gap-4 justify-center">
            {/* Indicateur de Direction */}
              <div className={`flex items-center gap-2 px-4 py-1.5 rounded-full text-sm font-bold shadow-sm ${
                direction === 'up' ? 'bg-green-500/10 text-green-500 border border-green-500/20' : 'bg-red-500/10 text-red-500 border border-red-500/20'
              }`}>
                <span className="relative flex h-2 w-2">
                  <span className={`animate-ping absolute inline-flex h-full w-full rounded-full opacity-75 ${direction === 'up' ? 'bg-green-400' : 'bg-red-400'}`}></span>
                  <span className={`relative inline-flex rounded-full h-2 w-2 ${direction === 'up' ? 'bg-green-500' : 'bg-red-500'}`}></span>
                </span>
                Tendance : {direction === 'up' ? 'HAUSSIÈRE' : 'BAISSIÈRE'}
              </div>
            </div>
            
            {/* Affichage de l'analyse de l'agent RAG */}
            {aiAnalysis && (
                <motion.div 
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="text-sm text-left bg-muted/30 p-4 rounded-xl border border-border/20"
                >
                    <p className="font-semibold mb-1">Conseil de l'Agent :</p>
                    <p className="text-muted-foreground italic">"{aiAnalysis}"</p>
                </motion.div>
            )}
         </div>
      </CardContent>
    </Card>
  )
}
