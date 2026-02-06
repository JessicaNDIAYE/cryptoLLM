import { useState, useRef, useEffect } from "react"
import { Input } from "@/app/components/ui/input"
import { Button } from "@/app/components/ui/button"
import { Send, Bot, User } from "lucide-react"
import { Card } from "@/app/components/ui/card"
import { motion } from "motion/react"

interface Message {
    id: string;
    role: 'user' | 'assistant';
    content: string;
    isTyping?: boolean;
}

function Typewriter({ text, speed = 20, onComplete }: { text: string, speed?: number, onComplete?: () => void }) {
  const [displayedText, setDisplayedText] = useState('');

  useEffect(() => {
    setDisplayedText(''); 
    let i = 0;
    const interval = setInterval(() => {
      if (i < text.length) {
        setDisplayedText(prev => prev + text.charAt(i));
        i++;
      } else {
        clearInterval(interval);
        onComplete && onComplete();
      }
    }, speed);
    return () => clearInterval(interval);
  }, [text, speed]);

  return <span>{displayedText}</span>;
}

export function ChatInterface() {
    const [messages, setMessages] = useState<Message[]>([
        { id: '1', role: 'assistant', content: "Hello! I'm InvestBuddy. How can I help you master your finances today?", isTyping: true }
    ]);
    const [input, setInput] = useState("");
    const [isTyping, setIsTyping] = useState(false);
    const messagesEndRef = useRef<HTMLDivElement>(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    }

    useEffect(scrollToBottom, [messages, isTyping]);

    const handleSend = async () => {
        if (!input.trim()) return;
        
        const userMsg: Message = { id: Date.now().toString(), role: 'user', content: input };
        setMessages(prev => [...prev, userMsg]);
        setInput("");
        setIsTyping(true);

        // Simulate API delay
        setTimeout(() => {
             const responses = [
                 "That's a great question about ETFs. Let me break it down simply.",
                 "Risk management is key. Have you checked your risk profile today?",
                 "Based on your conservative profile, you might want to look at government bonds.",
                 "Compound interest is the eighth wonder of the world! Start early.",
                 "I can help you analyze that. Paste the ETF details in the analysis tool!",
             ];
             const randomResponse = responses[Math.floor(Math.random() * responses.length)];
             
             setIsTyping(false);
             setMessages(prev => [...prev, { id: (Date.now() + 1).toString(), role: 'assistant', content: randomResponse, isTyping: true }]);
        }, 1500);
    }

    return (
        <Card className="flex flex-col h-[600px] shadow-2xl border-white/10 bg-card/95 backdrop-blur overflow-hidden">
             <div className="p-4 border-b bg-muted/10 flex items-center justify-between">
                <div className="flex items-center gap-2">
                    <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
                    <span className="text-sm font-medium">InvestBuddy AI</span>
                </div>
                <span className="text-xs text-muted-foreground">Powered by n8n & FastAPI</span>
             </div>
             <div className="flex-1 overflow-y-auto p-4 space-y-6">
                {messages.map((msg) => (
                    <motion.div 
                        key={msg.id} 
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        className={`flex gap-3 ${msg.role === 'user' ? 'flex-row-reverse' : ''}`}
                    >
                        <div className={`w-8 h-8 rounded-full flex items-center justify-center shrink-0 border ${msg.role === 'assistant' ? 'bg-primary/10 border-primary/20 text-primary' : 'bg-secondary border-secondary text-secondary-foreground'}`}>
                            {msg.role === 'assistant' ? <Bot size={16} /> : <User size={16} />}
                        </div>
                        <div className={`rounded-2xl p-4 max-w-[85%] text-sm leading-relaxed shadow-sm ${
                            msg.role === 'user' 
                            ? 'bg-primary text-primary-foreground rounded-tr-sm' 
                            : 'bg-muted/30 rounded-tl-sm border border-border/40'
                        }`}>
                            {msg.role === 'assistant' && msg.isTyping ? (
                                 <Typewriter text={msg.content} speed={15} />
                            ) : msg.content}
                        </div>
                    </motion.div>
                ))}
                {isTyping && (
                    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="flex gap-3">
                         <div className="w-8 h-8 rounded-full bg-primary/10 border border-primary/20 text-primary flex items-center justify-center shrink-0">
                            <Bot size={16} />
                         </div>
                         <div className="bg-muted/30 border border-border/40 rounded-2xl p-4 rounded-tl-sm flex gap-1 items-center h-12">
                            <span className="w-1.5 h-1.5 bg-foreground/40 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                            <span className="w-1.5 h-1.5 bg-foreground/40 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                            <span className="w-1.5 h-1.5 bg-foreground/40 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                         </div>
                    </motion.div>
                )}
                <div ref={messagesEndRef} />
             </div>
             
             <div className="p-4 border-t bg-background/50 backdrop-blur">
                <form 
                    onSubmit={(e) => { e.preventDefault(); handleSend(); }}
                    className="flex gap-2 relative"
                >
                    <Input 
                        value={input} 
                        onChange={e => setInput(e.target.value)} 
                        placeholder="Ask about your portfolio..." 
                        className="bg-muted/50 border-transparent focus:bg-background focus:border-primary/20 pr-12 h-12 rounded-full px-6 transition-all"
                    />
                    <Button 
                        type="submit" 
                        size="icon" 
                        disabled={!input.trim() || isTyping}
                        className="absolute right-1 top-1 h-10 w-10 rounded-full"
                    >
                        <Send size={18} />
                    </Button>
                </form>
             </div>
        </Card>
    )
}
