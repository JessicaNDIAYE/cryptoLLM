import { Card, CardContent, CardHeader, CardTitle } from "@/app/components/ui/card";
import { AreaChart, Area, ResponsiveContainer, Tooltip } from 'recharts';

const data = [
  { time: '10:00', value: 30 },
  { time: '11:00', value: 45 },
  { time: '12:00', value: 35 },
  { time: '13:00', value: 55 },
  { time: '14:00', value: 50 },
  { time: '15:00', value: 72 },
];

export function MarketSentiment() {
  return (
    <Card className="bg-white border-0 shadow-sm rounded-[2rem] h-full overflow-hidden relative">
      <div className="absolute top-0 right-0 w-40 h-40 bg-purple-50 rounded-full -mr-16 -mt-16 pointer-events-none" />
      
      <CardHeader className="flex flex-row items-center justify-between pb-2 pt-6 px-6 relative z-10">
        <CardTitle className="text-base font-bold text-[#1F1F2E]">Sentiment du Marché</CardTitle>
        <span className="flex h-2.5 w-2.5 rounded-full bg-green-500 shadow-[0_0_10px_rgba(34,197,94,0.4)]" />
      </CardHeader>
      
      <CardContent className="space-y-4 px-6 pb-6 relative z-10">
        <div className="flex items-end gap-3">
            <span className="text-5xl font-bold text-[#1F1F2E] tracking-tighter">72</span>
            <div className="mb-2 flex flex-col">
                <span className="text-xs text-gray-400 font-medium">/ 100</span>
                <span className="text-xs text-green-600 font-bold uppercase tracking-wider">Bullish</span>
            </div>
        </div>
        
        <div className="h-[80px] w-full -ml-2">
            <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={data}>
                <defs>
                    <linearGradient id="colorValue" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#8b5cf6" stopOpacity={0.2}/>
                    <stop offset="95%" stopColor="#8b5cf6" stopOpacity={0}/>
                    </linearGradient>
                </defs>
                <Tooltip 
                    contentStyle={{ backgroundColor: '#1F1F2E', borderColor: 'transparent', borderRadius: '12px', fontSize: '12px', color: 'white' }} 
                    itemStyle={{ color: '#fff' }}
                    labelStyle={{ display: 'none' }}
                />
                <Area 
                    type="monotone" 
                    dataKey="value" 
                    stroke="#8b5cf6" 
                    strokeWidth={3}
                    fillOpacity={1} 
                    fill="url(#colorValue)" 
                />
                </AreaChart>
            </ResponsiveContainer>
        </div>
        
        <p className="text-[11px] text-gray-400 text-center font-medium">
            Mise à jour en temps réel via API.
        </p>
      </CardContent>
    </Card>
  );
}
