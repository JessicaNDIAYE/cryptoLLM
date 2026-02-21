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
        # 2. Extraire les prédictions reçues de l'autre API

        vol = request.prediction.volatility
        direc = request.prediction.direction
        currency = request.currency.upper()  

        clean_currency = currency.replace("USDT", "")

        search_query = f"Actualités majeures et événements financiers pour {clean_currency} en 2025"

        docs = retriever.invoke(search_query)
        context = "\n\n".join([doc.page_content for doc in docs])

        # 3. Construire le prompt pour l'analyse finale
        prompt = f"""
        Tu es l'agent InvestBuddy. Analyse le risque suivant :
        - Prédiction ML : Volatilité {vol}, Direction {direc}.
        - Contexte News (Engagement Social inclus) : {context}
        
        Rédige un conseil court : si la volatilité est haute (>0.02) et le sentiment news est négatif, sois très prudent.
        """
        
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