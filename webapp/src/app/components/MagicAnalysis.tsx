import { useState } from "react"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/app/components/ui/card"
import { Button } from "@/app/components/ui/button"
import { Textarea } from "@/app/components/ui/textarea"
import { Wand2, Loader2, Mail } from "lucide-react"
import { motion, AnimatePresence } from "motion/react"
import { toast } from "sonner"

export function MagicAnalysis() {
    const [text, setText] = useState("");
    const [analyzing, setAnalyzing] = useState(false);
    const [result, setResult] = useState<{ticker: string, risk: string, summary: string} | null>(null);

    const handleAnalyze = () => {
        if (!text) return;
        setAnalyzing(true);
        // Simulate analysis
        setTimeout(() => {
            setAnalyzing(false);
            setResult({
                ticker: "MSCI WORLD UCITS ETF",
                risk: "Moderate",
                summary: "This ETF tracks the performance of large and mid-cap stocks across 23 developed markets countries. It provides broad global exposure, suitable for long-term growth strategies."
            });
        }, 2000);
    }
    
    const handleEmail = () => {
        toast.promise(
             new Promise((resolve) => setTimeout(resolve, 2000)),
             {
                 loading: 'InvestBuddy is drafting your guide...',
                 success: 'Guide sent to your email!',
                 error: 'Error sending email',
             }
        );
    }

    return (
        <Card className="h-full border-dashed border-2 border-muted hover:border-primary/20 transition-colors bg-card/30">
            <CardHeader>
                <CardTitle className="flex items-center gap-2">
                    <Wand2 className="h-5 w-5 text-purple-500" />
                    Magic Analysis
                </CardTitle>
                <CardDescription>Paste ETF details to analyze instantly.</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
                <AnimatePresence mode="wait">
                    {!result ? (
                        <motion.div 
                            key="input"
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            exit={{ opacity: 0 }}
                            className="space-y-4"
                        >
                            <Textarea 
                                placeholder="Paste text here (e.g. 'iShares Core MSCI World UCITS ETF...')" 
                                className="min-h-[150px] resize-none bg-muted/30 focus:bg-background transition-colors"
                                value={text}
                                onChange={(e) => setText(e.target.value)}
                            />
                            <Button 
                                className="w-full bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white border-0 shadow-lg shadow-purple-900/20" 
                                onClick={handleAnalyze}
                                disabled={analyzing || !text}
                            >
                                {analyzing ? (
                                    <>
                                        <Loader2 className="mr-2 h-4 w-4 animate-spin" /> Analyzing...
                                    </>
                                ) : (
                                    "Analyze Text"
                                )}
                            </Button>
                        </motion.div>
                    ) : (
                        <motion.div 
                            key="result"
                            initial={{ opacity: 0, scale: 0.95 }}
                            animate={{ opacity: 1, scale: 1 }}
                            className="bg-card border rounded-xl p-6 space-y-4 shadow-xl ring-1 ring-white/5"
                        >
                             <div className="flex items-center justify-between">
                                <h3 className="font-bold text-xl text-primary">{result.ticker}</h3>
                                <span className="bg-yellow-500/10 text-yellow-500 px-3 py-1 rounded-full text-xs font-medium border border-yellow-500/20">{result.risk} Risk</span>
                             </div>
                             <p className="text-muted-foreground text-sm leading-relaxed">{result.summary}</p>
                             
                             <div className="pt-4 flex gap-3">
                                <Button variant="outline" className="flex-1" onClick={() => setResult(null)}>Analyze Another</Button>
                                <Button className="flex-1 gap-2 bg-primary text-primary-foreground hover:bg-primary/90" onClick={handleEmail}>
                                    <Mail className="h-4 w-4" /> Explain & Email
                                </Button>
                             </div>
                        </motion.div>
                    )}
                </AnimatePresence>
            </CardContent>
        </Card>
    )
}
