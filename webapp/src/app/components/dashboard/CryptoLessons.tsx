import { Card, CardContent } from "@/app/components/ui/card";
import { Badge } from "@/app/components/ui/badge";
import { BookOpen, Bitcoin, Link2, TrendingUp, Wallet, Coins } from "lucide-react";

interface CryptoLessonsProps {
  onLessonClick: (topic: string, question: string) => void;
}

const lessonTopics = [
  {
    id: "bitcoin",
    title: "C'est quoi le Bitcoin ?",
    teaser: "La première cryptomonnaie décentralisée",
    icon: Bitcoin,
    color: "bg-orange-100 text-orange-600",
    question: "Explique-moi ce qu'est le Bitcoin et comment il fonctionne"
  },
  {
    id: "blockchain",
    title: "Comprendre la Blockchain",
    teaser: "La technologie derrière les cryptos",
    icon: Link2,
    color: "bg-blue-100 text-blue-600",
    question: "Qu'est-ce que la blockchain et pourquoi est-elle révolutionnaire ?"
  },
  {
    id: "volatilite",
    title: "La Volatilité expliquée",
    teaser: "Pourquoi les prix varient autant",
    icon: TrendingUp,
    color: "bg-purple-100 text-purple-600",
    question: "Qu'est-ce que la volatilité en finance et comment l'interpréter ?"
  },
  {
    id: "etf",
    title: "Les ETFs : Guide complet",
    teaser: "Investir facilement dans les marchés",
    icon: Coins,
    color: "bg-green-100 text-green-600",
    question: "C'est quoi un ETF et comment ça fonctionne ?"
  },
  {
    id: "wallet",
    title: "Les Wallets Crypto",
    teaser: "Stocker ses cryptos en sécurité",
    icon: Wallet,
    color: "bg-pink-100 text-pink-600",
    question: "Qu'est-ce qu'un wallet crypto et comment choisir le bon ?"
  },
  {
    id: "defi",
    title: "La DeFi : Finance décentralisée",
    teaser: "Le futur de la finance sans banques",
    icon: BookOpen,
    color: "bg-indigo-100 text-indigo-600",
    question: "Explique-moi la DeFi (finance décentralisée) et ses opportunités"
  }
];

export function CryptoLessons({ onLessonClick }: CryptoLessonsProps) {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between px-1">
        <div>
          <h2 className="text-xl font-bold text-[#1F1F2E]">🎓 Leçons Crypto</h2>
          <p className="text-sm text-gray-500 mt-1">Apprenez les concepts clés de la crypto avec notre IA</p>
        </div>
        <button className="text-sm font-medium text-purple-600 hover:text-purple-800 transition-colors">
          Voir le glossaire
        </button>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
        {lessonTopics.map((lesson) => {
          const IconComponent = lesson.icon;
          return (
            <Card 
              key={lesson.id}
              onClick={() => onLessonClick(lesson.title, lesson.question)}
              className="group relative overflow-hidden border-0 bg-white shadow-sm hover:shadow-xl hover:shadow-purple-100 transition-all duration-300 rounded-2xl cursor-pointer hover:scale-[1.02]"
            >
              <CardContent className="p-5">
                <div className="flex items-start gap-4">
                  <div className={`w-12 h-12 rounded-xl ${lesson.color} flex items-center justify-center shrink-0 group-hover:scale-110 transition-transform duration-300`}>
                    <IconComponent className="w-6 h-6" />
                  </div>
                  
                  <div className="flex-1 min-w-0">
                    <h3 className="font-bold text-base text-[#1F1F2E] leading-snug mb-1 group-hover:text-purple-600 transition-colors">
                      {lesson.title}
                    </h3>
                    <p className="text-sm text-gray-500 leading-relaxed">
                      {lesson.teaser}
                    </p>
                  </div>
                </div>
                
                <div className="mt-4 pt-3 border-t border-gray-100 flex items-center justify-between">
                  <Badge variant="secondary" className="bg-purple-50 text-purple-700 text-[10px] h-5 px-2 font-medium">
                    <BookOpen className="w-3 h-3 mr-1" />
                    Leçon interactive
                  </Badge>
                  <span className="text-xs text-gray-400 group-hover:text-purple-600 transition-colors font-medium flex items-center gap-1">
                    Commencer
                    <span className="group-hover:translate-x-1 transition-transform">→</span>
                  </span>
                </div>
              </CardContent>
            </Card>
          );
        })}
      </div>
    </div>
  );
}