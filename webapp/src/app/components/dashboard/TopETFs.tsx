import { Card, CardContent, CardHeader, CardTitle } from "@/app/components/ui/card";

const etfs = [
  { symbol: "IWDA", name: "iShares Core MSCI World", fee: "0.20%", risk: 4, trend: "+12.5%" },
  { symbol: "CSPX", name: "iShares Core S&P 500", fee: "0.07%", risk: 5, trend: "+18.2%" },
  { symbol: "EIMU", name: "iShares Core MSCI EM IMI", fee: "0.18%", risk: 6, trend: "-2.4%" },
  { symbol: "AGGU", name: "iShares Core Global Agg", fee: "0.10%", risk: 2, trend: "+4.1%" },
];

export function TopETFs() {
  return (
    <Card className="bg-white border-0 shadow-sm rounded-[2rem] h-full flex flex-col overflow-hidden">
      <CardHeader className="flex flex-row items-center justify-between pb-4 pt-6 px-6">
        <CardTitle className="text-base font-bold text-[#1F1F2E]">Top ETFs</CardTitle>
        <button className="text-xs font-medium text-gray-400 hover:text-[#1F1F2E]">Voir tout</button>
      </CardHeader>
      <CardContent className="flex-1 p-0">
         <div className="overflow-x-auto">
             <table className="w-full text-sm text-left">
                <thead className="text-xs text-gray-400 font-medium uppercase bg-gray-50/50">
                    <tr>
                        <th className="px-6 py-4 font-semibold">Nom</th>
                        <th className="px-4 py-4 font-semibold text-center">Frais</th>
                        <th className="px-4 py-4 font-semibold text-center">Risque</th>
                        <th className="px-6 py-4 font-semibold text-right">Tendance</th>
                    </tr>
                </thead>
                <tbody className="divide-y divide-gray-50">
                    {etfs.map((etf) => (
                        <tr key={etf.symbol} className="hover:bg-purple-50/30 transition-colors group cursor-pointer">
                            <td className="px-6 py-4">
                                <div className="flex flex-col">
                                    <span className="font-bold text-[#1F1F2E] group-hover:text-purple-600 transition-colors">{etf.symbol}</span>
                                    <span className="text-[11px] text-gray-400 truncate max-w-[120px]">{etf.name}</span>
                                </div>
                            </td>
                            <td className="px-4 py-4 text-center text-gray-500 font-medium">{etf.fee}</td>
                            <td className="px-4 py-4 text-center">
                                <div className="flex justify-center gap-1">
                                    {[...Array(7)].map((_, i) => (
                                        <div 
                                            key={i} 
                                            className={`w-1 h-3 rounded-full ${i < etf.risk ? 'bg-[#1F1F2E]' : 'bg-gray-200'}`} 
                                        />
                                    ))}
                                </div>
                            </td>
                            <td className={`px-6 py-4 text-right font-bold ${etf.trend.startsWith('+') ? 'text-green-600' : 'text-red-500'}`}>
                                {etf.trend}
                            </td>
                        </tr>
                    ))}
                </tbody>
             </table>
         </div>
      </CardContent>
    </Card>
  );
}
