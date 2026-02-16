from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from search_engine import get_financial_context
from risk_analyzer import retriever
from llm import llm
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
async def analyze_risk(prediction_data: dict, user_query: str):
    new_context = retriever.invoke(user_query)

    volatility = prediction_data['volatility']
    direction = prediction_data['direction']

    prompt = f"""
    Le modèle ML prédit une volatilité de {volatility} avec une direction {direction}.
    En te basant sur ces news : {new_context}, quel est ton conseil d'investissement ?
    """
    return llm.invoke(prompt)



if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=4000)