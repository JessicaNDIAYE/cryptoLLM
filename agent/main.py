from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from search_engine import get_financial_context
from risk_analyzer import retriever, llm
import uvicorn

app = FastAPI(title="InvestBuddy Knowledge API")

# --- CONFIGURATION CORS CRUCIALE ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"], # L'adresse précise de ton frontend Next.js
    allow_credentials=True,
    allow_methods=["*"], # Autorise POST, OPTIONS, GET, etc.
    allow_headers=["*"], # Autorise tous les headers (Content-Type, etc.)
)
# -----------------------------------

class PredictionDetails(BaseModel):
    volatility: float
    direction: str
class RiskAnalysisRequest(BaseModel):
    currency: str
    prediction: PredictionDetails  # Reçoit {'volatility': 0.05, 'direction': 'up'}
    user_query: str | None = None      # Reçoit "Analyse le risque pour le BTC"

class QueryRequest(BaseModel):
    question: str
    n_results: int = 2

async def get_fear_greed_index() -> str:
    """Récupère le Fear & Greed Index depuis l'API Alternative.me"""
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            response = await client.get("https://api.alternative.me/fng/?limit=1")
            data = response.json()
            value = data["data"][0]["value"]
            label = data["data"][0]["value_classification"]
            return f"{value}/100 ({label})"
    except:
        return "N/A"


async def get_funding_rate(symbol: str = "BTCUSDT") -> str:
    """Récupère le Funding Rate depuis Binance Futures"""
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            response = await client.get(
                "https://fapi.binance.com/fapi/v1/fundingRate",
                params={"symbol": symbol, "limit": 1}
            )
            data = response.json()
            rate = float(data[0]["fundingRate"]) * 100
            if rate > 0.05:
                sentiment = "marché suracheté (pression vendeuse attendue)"
            elif rate < -0.01:
                sentiment = "marché survendu (pression acheteuse attendue)"
            else:
                sentiment = "neutre"
            return f"{rate:.4f}% -> {sentiment}"
    except:
        return "N/A"


@app.post("/ask")
async def ask_knowledge_base(request: QueryRequest):
    try:
        context = get_financial_context(request.question, n_results=request.n_results)
        return {
            "question": request.question,
            "context": context
        }
    except Exception as e:
        print(f"Erreur détectée : {e}")
        raise HTTPException(status_code=500, detail=str(e))
    

@app.post("/analyzeRisk")
async def analyze_risk(request: RiskAnalysisRequest): # Utilise un modèle Pydantic pour valider
    try:
        docs = retriever.invoke(request.user_query)
        # 2. Extraire les prédictions reçues de l'autre API

        vol = request.prediction.volatility
        direc = request.prediction.direction
        currency = request.currency.upper()  

        clean_currency = currency.replace("USDT", "")

        search_query = f"Actualités majeures et événements financiers pour {clean_currency} en 2025"

        docs = retriever.invoke(search_query)
        context = "\n\n".join([doc.page_content for doc in docs])

        vol = request.prediction_data.get('volatility', 'N/A')
        direc = request.prediction_data.get('direction', 'N/A')
        fear_greed = await get_fear_greed_index()
        funding_rate = await get_funding_rate()

        # Calcul du niveau de risque
        try:
            vol_float = float(vol)
            if vol_float > 0.03:
                risk_level = "critique"
                risk_emoji = "🚨"
            elif vol_float > 0.02:
                risk_level = "élevé"
                risk_emoji = "⚠️"
            elif vol_float > 0.01:
                risk_level = "modéré"
                risk_emoji = "⚡"
            else:
                risk_level = "faible"
                risk_emoji = "✅"
        except:
            risk_level = "inconnu"
            risk_emoji = "❓"

        prompt = f"""Tu es InvestBuddy, un conseiller financier expert en cryptomonnaies.

CONTEXTE ACTUEL:
- Niveau de risque: {risk_level} {risk_emoji}
- Volatilité prédite: {vol}
- Direction prédite: {direc}
- Fear & Greed Index: {fear_greed}
- Funding Rate BTC: {funding_rate}
- Actualités récentes: {context[:1500]}

INSTRUCTIONS:
1. Analyse le niveau de risque en te basant sur la volatilité, le Fear & Greed Index, le Funding Rate ET les actualités
2. Donne une position claire (achat/attente/vente partielle) avec un pourcentage de confiance
3. Cite 2-3 faits concrets des actualités et indicateurs qui justifient ton avis
4. Propose une action concrète

FORMAT DE RÉPONSE:
- **Position**: [TON AVIS] ([X]% confiance)
- **Pourquoi**: [2-3 raisons basées sur les données]
- **Action**: [Conseil pratique]

Interdiction de dire "si la volatilité devait" - tu DOIS prendre position.
Maximum 4 phrases.

Réponds en français."""

        response = llm.invoke(prompt)
        return {
            "currency": currency,
            "volatility": vol,
            "direction": direc,
            "analysis": response.content
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=4000)