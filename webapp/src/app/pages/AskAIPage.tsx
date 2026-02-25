import { useState, useRef, useEffect } from "react"
import { Input } from "@/app/components/ui/input"
import { Button } from "@/app/components/ui/button"
import { Send, Bot, User, Sparkles } from "lucide-react"
import { Card } from "@/app/components/ui/card"
import { motion } from "motion/react"

interface Message {
    id: string;
    role: 'user' | 'assistant';
    content: string;
    isTyping?: boolean;
}

interface AskAIPageProps {
    initialQuestion?: string | null;
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

export function AskAIPage({ initialQuestion }: AskAIPageProps) {
    const [messages, setMessages] = useState<Message[]>([
        { id: '1', role: 'assistant', content: "Hello! I'm InvestBuddy AI. How can I help you with your financial questions today?", isTyping: true }
    ]);
    const [input, setInput] = useState("");
    const [isTyping, setIsTyping] = useState(false);
    const messagesEndRef = useRef<HTMLDivElement>(null);
    const hasProcessedInitialQuestion = useRef(false);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    }

    useEffect(scrollToBottom, [messages, isTyping]);

    // Handle initial question from lesson click
    useEffect(() => {
        if (initialQuestion && !hasProcessedInitialQuestion.current) {
            hasProcessedInitialQuestion.current = true;
            // Automatically send the question
            setTimeout(() => {
                handleSendWithQuestion(initialQuestion);
            }, 500);
        }
    }, [initialQuestion]);

    const handleSendWithQuestion = async (question: string) => {
        if (!question.trim()) return;

        const userMsg: Message = { id: Date.now().toString(), role: 'user', content: question };
        setMessages(prev => [...prev, userMsg]);
        setIsTyping(true);

        try {
            const response = await fetch('http://localhost:4000/ask', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    question: question,
                    n_results: 2
                }),
            });

            if (!response.ok) throw new Error('Failed to get response');

            const data = await response.json();

            let aiResponse = "";

            if (data.context && data.context.length > 0) {
                aiResponse = "**Based on my knowledge base:**\n\n";
                data.context.forEach((text: string) => {
                    aiResponse += `${text}\n\n`;
                });
            } else {
                aiResponse = "I couldn't find specific information for your question.";
            }

            setIsTyping(false);
            setMessages(prev => [...prev, {
                id: (Date.now() + 1).toString(),
                role: 'assistant',
                content: aiResponse,
                isTyping: true
            }]);
        } catch (error) {
            console.error('Error calling agent:', error);
            setIsTyping(false);
            setMessages(prev => [...prev, {
                id: (Date.now() + 1).toString(),
                role: 'assistant',
                content: "Sorry, I'm having trouble connecting to my knowledge base.",
                isTyping: true
            }]);
        }
    };

    const handleSend = async () => {
        if (!input.trim()) return;
        await handleSendWithQuestion(input);
        setInput("");
    }

    return (
        <div className="space-y-6 animate-in fade-in duration-700">
            <div className="text-center space-y-4">
                <div className="w-16 h-16 rounded-full bg-gradient-to-br from-purple-100 to-blue-100 flex items-center justify-center mx-auto">
                    <Sparkles className="h-8 w-8 text-purple-600" />
                </div>
                <h1 className="text-3xl font-bold text-[#1F1F2E] tracking-tight">Apprentissage IA</h1>
                <p className="text-gray-600 max-w-2xl mx-auto">
                    Apprenez les concepts clés de la crypto et de la finance grâce à notre assistant IA intelligent.
                </p>
            </div>

            <Card className="flex flex-col h-[600px] shadow-2xl border-white/10 bg-card/95 backdrop-blur overflow-hidden mx-auto max-w-4xl">
                 <div className="p-4 border-b bg-muted/10 flex items-center justify-between">
                    <div className="flex items-center gap-2">
                        <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
                        <span className="text-sm font-medium">InvestBuddy AI Assistant</span>
                    </div>
                    <span className="text-xs text-muted-foreground">Powered by RAG & OpenAI</span>
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
                                ) : (
                                    <div style={{ whiteSpace: 'pre-wrap' }}>{msg.content}</div>
                                )}
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
                            onChange={(e: React.ChangeEvent<HTMLInputElement>) => setInput(e.target.value)}
                            placeholder="Posez une question sur la crypto, les ETFs, la blockchain..."
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
        </div>
    )
}