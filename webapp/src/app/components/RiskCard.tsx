import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/app/components/ui/card"
import { motion } from "motion/react"

export function RiskCard({ score = 4 }: { score?: number }) {
  // score is 1-7
  // normalize score to 0-1 for pathLength
  const normalizedScore = score / 7;

  return (
    <Card className="w-full bg-card/50 backdrop-blur-sm border-border/40 overflow-hidden relative">
      <div className="absolute inset-0 bg-gradient-to-br from-blue-500/5 to-purple-500/5 pointer-events-none" />
      <CardHeader>
        <CardTitle>Risk Profile</CardTitle>
        <CardDescription>Based on your investment goals</CardDescription>
      </CardHeader>
      <CardContent className="flex flex-col items-center justify-center pt-2 pb-8">
         {/* SVG Gauge */}
         <div className="relative w-64 h-32">
            <svg viewBox="0 0 100 50" className="w-full h-full overflow-visible">
              {/* Defs for gradient */}
              <defs>
                <linearGradient id="riskGradient" x1="0%" y1="0%" x2="100%" y2="0%">
                   <stop offset="0%" stopColor="#3b82f6" /> {/* Blue */}
                   <stop offset="50%" stopColor="#8b5cf6" /> {/* Purple */}
                   <stop offset="100%" stopColor="#f43f5e" /> {/* Red-Pink */}
                </linearGradient>
              </defs>
              
              {/* Background Path (Grey) */}
              <path d="M 10 50 A 40 40 0 0 1 90 50" fill="none" stroke="currentColor" strokeWidth="6" className="text-muted/20" strokeLinecap="round" />
              
              {/* Active Path (Gradient) */}
              <motion.path 
                d="M 10 50 A 40 40 0 0 1 90 50" 
                fill="none" 
                stroke="url(#riskGradient)" 
                strokeWidth="6" 
                strokeLinecap="round"
                initial={{ pathLength: 0 }}
                animate={{ pathLength: normalizedScore }}
                transition={{ duration: 1.5, ease: "easeOut", delay: 0.2 }}
              />
            </svg>
            
            <div className="absolute bottom-0 left-1/2 -translate-x-1/2 translate-y-1/3 flex flex-col items-center">
                 <motion.span 
                    className="text-4xl font-bold tabular-nums"
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 1 }}
                 >
                    {score}
                 </motion.span>
                 <span className="text-xs text-muted-foreground uppercase tracking-widest text-[10px]">Level / 7</span>
            </div>
         </div>
         
         <div className="mt-8 text-center space-y-2">
            <motion.h4 
                className="font-medium text-lg"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 1.2 }}
            >
                {score < 3 ? "Conservative" : score < 5 ? "Balanced" : "Aggressive"}
            </motion.h4>
            <motion.p 
                className="text-sm text-muted-foreground px-4"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 1.4 }}
            >
               {score < 3 ? "Priority on capital preservation with minimal volatility." : score < 5 ? "Strategic growth balanced with risk management." : "Maximum growth potential accepting higher volatility."}
            </motion.p>
         </div>
      </CardContent>
    </Card>
  )
}
