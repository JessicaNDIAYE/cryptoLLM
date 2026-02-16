import pandas as pd
import chromadb
from chromadb.utils import embedding_functions
import math

# 1. Configuration
CSV_FILE = 'news_currencies_source_joinedResult.csv'
CHROMA_PATH = "./chroma_db"
COLLECTION_NAME = "crypto_news"
BATCH_SIZE = 1000  # On traite 1000 news à la fois pour la mémoire

def ingest_data():
    # Initialisation de ChromaDB
    client = chromadb.PersistentClient(path=CHROMA_PATH)
    collection = client.get_or_create_collection(name=COLLECTION_NAME)

    print(f"🚀 Début de l'importation de {CSV_FILE}...")

    # 2. Lecture par morceaux (chunks) pour économiser la RAM
    # chunksize permet de ne pas charger les 248k lignes d'un coup
    reader = pd.read_csv(CSV_FILE, chunksize=BATCH_SIZE)

    for i, chunk in enumerate(reader):
        # Nettoyage rapide du lot actuel
        chunk['description'] = chunk['description'].fillna('')
        chunk['currencies'] = chunk['currencies'].fillna('Général')
        
        # Préparation des documents (le texte que le LLM va lire)
        documents = []
        metadatas = []
        ids = []

        for _, row in chunk.iterrows():
            # Construction du texte enrichi
            content = (
                f"Date: {row['newsDatetime']} | "
                f"Crypto: {row['currencies']} | "
                f"Titre: {row['title']} | "
                f"Détails: {row['description']} | "
                f"Engagement Social: Likes:{row['liked']}, Dislikes:{row['disliked']}, Comments:{row['comments']} | "
                f"Sentiment: Pos:{row['positive']}, Neg:{row['negative']}, Toxic:{row['toxic']}"
            )
            
            documents.append(content)
            
            # Métadonnées pour le filtrage (très important pour la performance)
            metadatas.append({
                "currencies": str(row['currencies']),
                "importance": int(row['important']),
                "sentiment_neg": int(row['negative'])
            })
            
            # Utilisation de l'ID unique du CSV
            ids.append(str(row['id']))

        # 3. Ajout au Vector Store
        collection.add(
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
        
        if (i + 1) % 10 == 0:
            print(f"✅ { (i + 1) * BATCH_SIZE } news indexées...")

    print("✨ Ingestion terminée avec succès !")

if __name__ == "__main__":
    ingest_data()