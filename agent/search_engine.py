import chromadb
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
current_dir = os.path.dirname(os.path.abspath(__file__))

# On pointe vers la nouvelle base OpenAI
db_path = os.path.join(current_dir, "chroma_db_openai")
db_client = chromadb.PersistentClient(path=db_path)
collection = db_client.get_collection(name="finrad_docs")

def get_financial_context(query, n_results=2):
    # 1. Transformer la question en vecteur via OpenAI
    response = client.embeddings.create(
        input=[query],
        model="text-embedding-3-small"
    )
    query_embedding = response.data[0].embedding
    
    # 2. Chercher dans ChromaDB
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results
    )
    return results['documents'][0]

if __name__ == "__main__":
    # Test de vérité
    question = "What is a dividend?" # Teste en anglais d'abord pour valider
    context = get_financial_context(question)
    print(f"\nQuestion: {question}")
    print(f"Contextes trouvés: {context}")