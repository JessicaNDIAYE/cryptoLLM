import os
import chromadb
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# Initialisation du client OpenAI
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def get_openai_embeddings(texts):
    """Récupère les vecteurs via l'API OpenAI"""
    # On peut envoyer les textes par paquets (max 2048 par requête pour OpenAI)
    response = client.embeddings.create(
        input=texts,
        model="text-embedding-3-small"
    )
    return [item.embedding for item in response.data]

# Configuration ChromaDB
current_dir = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(current_dir, "chroma_db_openai") # On change le nom pour ne pas mélanger
db_client = chromadb.PersistentClient(path=db_path)
collection = db_client.get_or_create_collection(name="finrad_docs")

def ingest_with_openai():
    file_path = os.path.join(current_dir,"data", "education", "finrad_library.txt")
    
    with open(file_path, "r", encoding="utf-8") as f:
        docs = [d.strip() for d in f.read().split("\n\n") if len(d.strip()) > 10]

    print(f"Vectorisation de {len(docs)} documents via OpenAI...")
    
    # Pour 13 000 docs, on fait des paquets de 500 pour ne pas saturer l'API
    batch_size = 500
    for i in range(0, len(docs), batch_size):
        batch_docs = docs[i : i + batch_size]
        embeddings = get_openai_embeddings(batch_docs)
        
        collection.add(
            documents=batch_docs,
            embeddings=embeddings,
            ids=[f"id_{j}" for j in range(i, i + len(batch_docs))]
        )
        print(f"Progress: {i + len(batch_docs)}/{len(docs)}")

if __name__ == "__main__":
    ingest_with_openai()