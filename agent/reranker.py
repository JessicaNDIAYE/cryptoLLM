"""
Module de reranking pour améliorer la pertinence des résultats RAG
Utilise un modèle cross-encoder pour re-ranking plus précis
"""

from sentence_transformers import CrossEncoder
import numpy as np
import torch
from typing import List, Tuple
import logging

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialisation du modèle de reranking (modèle français/anglais)
# On utilise un modèle cross-encoder spécialisé pour le scoring de pertinence
RERANKER_MODEL = "cross-encoder/ms-marco-MiniLM-L-6-v2"  # Bon pour Q&A en anglais
# Alternative française: "anthea/ms-marco-camembert-base" (si besoin)

class Reranker:
    def __init__(self, model_name: str = RERANKER_MODEL, use_gpu: bool = True):
        """
        Initialise le reranker avec un modèle cross-encoder
        """
        try:
            # Vérifier si CUDA est disponible
            if use_gpu and torch.cuda.is_available():
                device = 'cuda'
                logger.info("GPU détecté, utilisation du reranker sur GPU")
            else:
                device = 'cpu'
                logger.info("Utilisation du reranker sur CPU")
            
            self.model = CrossEncoder(model_name, device=device)
            logger.info(f"Reranker chargé avec succès: {model_name}")
        except Exception as e:
            logger.error(f"Erreur lors du chargement du reranker: {e}")
            # Fallback vers un modèle plus simple si nécessaire
            self.model = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-2-v2")
            logger.info("Fallback vers modèle plus simple")
    
    def rerank(self, query: str, documents: List[str], top_k: int = None) -> List[Tuple[str, float]]:
        """
        Re-rank les documents par pertinence par rapport à la query
        
        Args:
            query: La question de l'utilisateur
            documents: Liste des documents à re-ranker
            top_k: Nombre de documents à retourner (None = tous)
        
        Returns:
            Liste de tuples (document, score) triés par pertinence
        """
        if not documents:
            return []
        
        try:
            # Créer les paires (query, document) pour le scoring
            pairs = [[query, doc] for doc in documents]
            
            # Calculer les scores de pertinence
            scores = self.model.predict(pairs)
            
            # Créer une liste de tuples (document, score)
            scored_docs = list(zip(documents, scores))
            
            # Trier par score décroissant
            scored_docs.sort(key=lambda x: x[1], reverse=True)
            
            # Limiter au top_k si spécifié
            if top_k:
                scored_docs = scored_docs[:top_k]
            
            logger.info(f"Reranking terminé: {len(documents)} documents -> scores calculés")
            return scored_docs
            
        except Exception as e:
            logger.error(f"Erreur lors du reranking: {e}")
            # En cas d'erreur, retourner les documents originaux avec score 0
            return [(doc, 0.0) for doc in documents[:top_k]]

# Instance globale du reranker (singleton)
_reranker_instance = None

def get_reranker():
    """
    Retourne une instance singleton du reranker
    """
    global _reranker_instance
    if _reranker_instance is None:
        _reranker_instance = Reranker()
    return _reranker_instance

def rerank_documents(query: str, documents: List[str], top_k: int = None) -> List[str]:
    """
    Fonction utilitaire pour re-ranker et retourner seulement les textes
    
    Args:
        query: La question
        documents: Liste des documents
        top_k: Nombre de documents à retourner
    
    Returns:
        Liste des documents re-rankés (textes seulement)
    """
    reranker = get_reranker()
    reranked = reranker.rerank(query, documents, top_k)
    return [doc for doc, score in reranked]

if __name__ == "__main__":
    # Test simple
    test_query = "What is a dividend?"
    test_docs = [
        "A dividend is a distribution of profits by a corporation to its shareholders.",
        "Bitcoin is a cryptocurrency created in 2009.",
        "When a company earns a profit, it can reinvest it or distribute it to shareholders as dividends.",
        "Stocks represent ownership in a company."
    ]
    
    reranker = Reranker()
    results = reranker.rerank(test_query, test_docs)
    
    print("\nTest de reranking:")
    print(f"Query: {test_query}\n")
    for doc, score in results:
        print(f"Score: {score:.4f} - {doc[:100]}...")