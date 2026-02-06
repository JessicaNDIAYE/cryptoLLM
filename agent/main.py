from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from search_engine import get_financial_context
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

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=4000)