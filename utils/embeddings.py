"""
Module pour générer les embeddings avec Hugging Face.

Les embeddings transforment le texte en vecteurs numériques
que le vector store peut indexer et comparer.
"""

from typing import List, Dict, Any
import logging
import numpy as np
from sentence_transformers import SentenceTransformer
from app.config import settings

logger = logging.getLogger(__name__)


class EmbeddingManager:
    """
    Gère la génération des embeddings avec Sentence Transformers.
    
    Attributes:
        model_name: Nom du modèle HuggingFace
        model: Instance du modèle chargé
        embedding_dim: Dimension des vecteurs embeddings
    """
    
    def __init__(self, model_name: str = settings.EMBEDDING_MODEL):
        """
        Initialiser le gestionnaire d'embeddings.
        
        Args:
            model_name: Nom du modèle HuggingFace
                       (défaut: all-MiniLM-L6-v2)
        
        Raises:
            RuntimeError: Si le modèle ne peut pas être chargé
        """
        self.model_name = model_name
        self.model = None
        self.embedding_dim = settings.EMBEDDING_DIMENSION
        
        self._load_model()
    
    def _load_model(self) -> None:
        """
        Charger le modèle Sentence Transformers.
        
        Raises:
            RuntimeError: Si le chargement échoue
        """
        try:
            logger.info(f"Chargement du modèle d'embeddings: {self.model_name}")
            
            # Charger le modèle (avec cache automatique)
            self.model = SentenceTransformer(
                self.model_name,
                device="cpu"  # Change à "cuda" si GPU disponible
            )
            
            # Vérifier la dimension
            test_embedding = self.model.encode("test")
            self.embedding_dim = len(test_embedding)
            
            logger.info(
                f"Modèle chargé: {self.model_name} "
                f"({self.embedding_dim} dimensions)"
            )
        
        except Exception as e:
            error_msg = f"Impossible de charger le modèle {self.model_name}: {e}"
            logger.error(error_msg)
            raise RuntimeError(error_msg) from e
    
    def encode_text(self, text: str) -> np.ndarray:
        """
        Générer l'embedding d'un texte.
        
        Args:
            text: Texte à encoder
        
        Returns:
            Vecteur embedding (ndarray de shape (embedding_dim,))
        
        Raises:
            ValueError: Si le texte est vide
        """
        if not text or not text.strip():
            raise ValueError("Le texte ne peut pas être vide")
        
        try:
            embedding = self.model.encode(
                text,
                convert_to_numpy=True,
                show_progress_bar=False
            )
            return embedding.astype(np.float32)
        
        except Exception as e:
            logger.error(f"Erreur lors de l'encoding: {e}")
            raise
    
    def encode_batch(
        self,
        texts: List[str],
        batch_size: int = settings.BATCH_SIZE
    ) -> np.ndarray:
        """
        Générer les embeddings d'une liste de textes.
        
        Args:
            texts: Liste de textes
            batch_size: Taille du batch (défaut 32)
        
        Returns:
            Matrice d'embeddings (shape: (len(texts), embedding_dim))
        
        Raises:
            ValueError: Si la liste est vide
        """
        if not texts:
            raise ValueError("La liste de textes ne peut pas être vide")
        
        try:
            logger.info(
                f"Encodage de {len(texts)} textes avec batch_size={batch_size}"
            )
            
            embeddings = self.model.encode(
                texts,
                batch_size=batch_size,
                convert_to_numpy=True,
                show_progress_bar=settings.DEBUG_MODE
            )
            
            return embeddings.astype(np.float32)
        
        except Exception as e:
            logger.error(f"Erreur lors de l'encodage batch: {e}")
            raise
    
    def encode_chunks(
        self,
        chunks: List[Dict[str, Any]],
        batch_size: int = settings.BATCH_SIZE
    ) -> List[Dict[str, Any]]:
        """
        Encoder une liste de chunks avec leurs métadonnées.
        
        Args:
            chunks: Liste de dicts avec 'text' et 'metadata'
            batch_size: Taille du batch
        
        Returns:
            Liste de chunks avec embeddings ajoutés
        """
        if not chunks:
            raise ValueError("La liste de chunks ne peut pas être vide")
        
        # Extraire les textes
        texts = [chunk["text"] for chunk in chunks]
        
        # Encoder tous les textes
        embeddings = self.encode_batch(texts, batch_size)
        
        # Ajouter les embeddings aux chunks
        result = []
        for chunk, embedding in zip(chunks, embeddings):
            result.append({
                **chunk,
                "embedding": embedding,
            })
        
        logger.info(f"{len(result)} chunks encodés avec succès")
        return result
    
    def get_embedding_dim(self) -> int:
        """
        Retourner la dimension des embeddings.
        
        Returns:
            Nombre de dimensions
        """
        return self.embedding_dim
    
    def similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """
        Calculer la similarité cosinus entre deux vecteurs.
        
        Args:
            vec1: Premier vecteur
            vec2: Deuxième vecteur
        
        Returns:
            Score de similarité entre -1 et 1 (généralement 0 à 1)
        """
        # Normaliser les vecteurs
        vec1_norm = vec1 / (np.linalg.norm(vec1) + 1e-8)
        vec2_norm = vec2 / (np.linalg.norm(vec2) + 1e-8)
        
        # Calculer le produit scalaire (cosinus)
        return float(np.dot(vec1_norm, vec2_norm))
