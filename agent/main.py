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


class RiskAnalysisRequest(BaseModel):
    prediction_data: dict  # Reçoit {'volatility': 0.05, 'direction': 'up'}
    user_query: str        # Reçoit "Analyse le risque pour le BTC"

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
        # 1. Récupérer les news liées à la crypto via ton index FAISS/Chroma
        docs = retriever.invoke(request.user_query)
        context = "\n\n".join([doc.page_content for doc in docs])

        # 2. Extraire les prédictions reçues de l'autre API
        vol = request.prediction_data.get('volatility', 'N/A')
        direc = request.prediction_data.get('direction', 'N/A')

        # 3. Construire le prompt pour l'analyse finale
        prompt = f"""
        Tu es l'agent InvestBuddy. Analyse le risque suivant :
        - Prédiction ML : Volatilité {vol}, Direction {direc}.
        - Contexte News (Engagement Social inclus) : {context}
        
        Rédige un conseil court : si la volatilité est haute (>0.02) et le sentiment news est négatif, sois très prudent.
        """
        
        response = llm.invoke(prompt)
        return {"analysis": response.content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=4000)