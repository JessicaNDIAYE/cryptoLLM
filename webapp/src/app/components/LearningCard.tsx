import { Card, CardContent } from "@/app/components/ui/card"
import { Progress } from "@/app/components/ui/progress"
import { Badge } from "@/app/components/ui/badge"
import { ArrowRight, BookOpen, CheckCircle2 } from "lucide-react"
import { cn } from "@/lib/utils"

interface LearningCardProps {
  title: string
  category: string
  progress: number
  duration: string
  active?: boolean
  onClick?: () => void
}

export function LearningCard({ title, category, progress, duration, active, onClick }: LearningCardProps) {
    return (
        <Card 
            className={cn(
                "group relative overflow-hidden transition-all duration-300 hover:shadow-lg cursor-pointer",
                active ? "border-primary/50 bg-primary/5 shadow-md" : "hover:bg-accent/5 hover:border-primary/30"
            )}
            onClick={onClick}
        >
             <CardContent className="p-6">
                <div className="flex justify-between items-start mb-4">
                    <Badge variant={active ? "default" : "secondary"} className="mb-2">{category}</Badge>
                    {progress === 100 && <CheckCircle2 className="h-5 w-5 text-green-500" />}
                </div>
                
                <h3 className="text-lg font-semibold mb-2 group-hover:text-primary transition-colors pr-8">{title}</h3>
                <div className="flex items-center text-sm text-muted-foreground mb-6">
                    <BookOpen className="h-4 w-4 mr-2" />
                    <span>{duration} read</span>
                </div>

                <div className="space-y-2">
                    <div className="flex justify-between text-xs text-muted-foreground">
                        <span>{progress === 0 ? "Not started" : progress === 100 ? "Completed" : "In progress"}</span>
                        <span>{progress}%</span>
                    </div>
                    <Progress value={progress} className="h-1.5" />
                </div>
                
                <div className={cn(
                    "absolute bottom-6 right-6 transition-all duration-300 transform",
                    active ? "opacity-100 translate-x-0" : "opacity-0 translate-x-4 group-hover:opacity-100 group-hover:translate-x-0"
                )}>
                     <div className="bg-primary text-primary-foreground rounded-full p-2 shadow-lg">
                        <ArrowRight className="h-4 w-4" />
                     </div>
                </div>
             </CardContent>
        </Card>
    )
}
