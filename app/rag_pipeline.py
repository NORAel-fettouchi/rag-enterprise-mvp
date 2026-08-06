"""
Pipeline RAG orchestrant tout le système.

Combine:
1. Chargement PDF
2. Chunking
3. Embeddings
4. Vector Store
5. Retrieval
6. LLM
7. Citations
"""

from typing import List, Dict, Any, Tuple
import logging
from pathlib import Path
import requests
import sys

# Ajouter le répertoire parent pour les imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.pdf_loader import PDFLoader
from utils.chunking import TextChunker
from utils.embeddings import EmbeddingManager
from utils.citation_handler import CitationHandler
from vectorstore.faiss_store import FAISSStore
from app.config import settings
from app.prompts import format_context, get_retrieval_qa_prompt

logger = logging.getLogger(__name__)


class RAGPipeline:
    """
    Pipeline complet RAG.
    
    Attributes:
        pdf_loader: Chargeur PDF
        chunker: Segmentateur texte
        embedding_manager: Gestionnaire embeddings
        vectorstore: Vector store FAISS
        citation_handler: Gestionnaire citations
    """
    
    def __init__(self, reload_index: bool = False):
        """
        Initialiser le pipeline RAG.
        
        Args:
            reload_index: Si False, charger l'index existant si dispo
        """
        logger.info("Initialisation du pipeline RAG...")
        
        # Initialiser les composants
        self.embedding_manager = EmbeddingManager()
        self.vectorstore = FAISSStore(
            embedding_dim=self.embedding_manager.get_embedding_dim()
        )
        self.chunker = TextChunker()
        self.citation_handler = CitationHandler()
        self.pdf_loader = PDFLoader
        
        # Charger l'index existant si disponible
        if not reload_index and self.vectorstore.index_exists():
            try:
                self.vectorstore.load_index()
                logger.info("Index FAISS chargé depuis le disque")
            except Exception as e:
                logger.warning(f"Impossible de charger l'index: {e}")
        
        logger.info("Pipeline RAG initialisé")
    
    def ingest_pdf(self, pdf_path: str | Path) -> Dict[str, Any]:
        """
        Ingérer un PDF complet.
        
        Étapes:
        1. Charger le PDF
        2. Découper en chunks
        3. Générer les embeddings
        4. Ajouter au vector store
        
        Args:
            pdf_path: Chemin du fichier PDF
        
        Returns:
            Dict avec statistiques d'ingestion
        
        Raises:
            FileNotFoundError: Si le PDF n'existe pas
            RuntimeError: Si l'ingestion échoue
        """
        try:
            logger.info(f"Ingestion du PDF: {pdf_path}")
            
            # 1. Charger le PDF
            loader = PDFLoader(pdf_path)
            text = loader.load()
            metadata = loader.get_metadata()
            
            logger.info(f"PDF chargé: {len(text)} caractères")
            
            # 2. Chunking
            chunks_list = self.chunker.chunk_text(text, metadata)
            chunks = self.chunker.get_chunks()
            logger.info(f"Texte découpé en {len(chunks)} chunks")
            
            # 3. Générer les embeddings
            chunks_with_embeddings = self.embedding_manager.encode_chunks(
                chunks,
                batch_size=settings.BATCH_SIZE
            )
            logger.info(f"{len(chunks_with_embeddings)} embeddings générés")
            
            # 4. Ajouter au vector store
            self.vectorstore.add_chunks(chunks_with_embeddings)
            
            # 5. Sauvegarder l'index
            self.vectorstore.save_index()
            
            stats = {
                "pdf_path": str(pdf_path),
                "text_length": len(text),
                "num_chunks": len(chunks),
                "metadata": metadata,
                "vectorstore_stats": self.vectorstore.get_stats(),
            }
            
            logger.info(f"Ingestion complétée: {stats}")
            return stats
        
        except Exception as e:
            error_msg = f"Erreur lors de l'ingestion du PDF: {e}"
            logger.error(error_msg)
            raise RuntimeError(error_msg) from e
    
    def retrieve(
        self,
        query: str,
        top_k: int = settings.TOP_K,
        threshold: float = settings.SIMILARITY_THRESHOLD
    ) -> List[Dict[str, Any]]:
        """
        Récupérer les chunks pertinents pour une requête.
        
        Args:
            query: Question de l'utilisateur
            top_k: Nombre de résultats à retourner
            threshold: Score minimum de similarité
        
        Returns:
            Liste de chunks pertinents avec scores
        
        Raises:
            ValueError: Si la query est vide
            RuntimeError: Si la recherche échoue
        """
        if not query or not query.strip():
            raise ValueError("La requête ne peut pas être vide")
        
        try:
            # Générer l'embedding de la requête
            query_embedding = self.embedding_manager.encode_text(query)
            
            # Rechercher dans le vector store
            results = self.vectorstore.search(query_embedding, top_k)
            
            # Filtrer par seuil de similarité
            filtered_results = [
                r for r in results
                if r["similarity_score"] >= threshold
            ]
            
            # Réinitialiser les citations et les ajouter
            self.citation_handler.reset()
            for result in filtered_results:
                chunk = result["chunk"]
                self.citation_handler.add_source(
                    chunk_id=chunk.get("id"),
                    text=chunk.get("text", ""),
                    source_file=chunk.get("metadata", {}).get("title", "Unknown"),
                    page_num=chunk.get("metadata", {}).get("page_num"),
                    similarity_score=result["similarity_score"],
                )
            
            logger.info(
                f"Récupération: {len(filtered_results)} chunks "
                f"(sur {len(results)} récupérés)"
            )
            
            return filtered_results
        
        except Exception as e:
            error_msg = f"Erreur lors de la récupération: {e}"
            logger.error(error_msg)
            raise RuntimeError(error_msg) from e
    
    def generate_answer(
        self,
        query: str,
        retrieved_chunks: List[Dict[str, Any]]
    ) -> str:
        """
        Générer une réponse avec un LLM.
        
        Utilise Ollama (local) ou HuggingFace (API).
        
        Args:
            query: Question de l'utilisateur
            retrieved_chunks: Chunks pertinents récupérés
        
        Returns:
            Réponse générée par le LLM
        
        Raises:
            RuntimeError: Si la génération échoue
        """
        try:
            # Formater le contexte
            context = format_context(retrieved_chunks)
            
            # Créer le prompt
            prompt = get_retrieval_qa_prompt(context, query)
            
            # Générer la réponse avec Ollama
            response = self._call_ollama(prompt)
            
            logger.info(f"Réponse générée: {len(response)} caractères")
            return response
        
        except Exception as e:
            error_msg = f"Erreur lors de la génération: {e}"
            logger.error(error_msg)
            raise RuntimeError(error_msg) from e
    
    def _call_ollama(self, prompt: str) -> str:
        """
        Appeler Ollama pour générer une réponse.
        
        Args:
            prompt: Prompt formaté
        
        Returns:
            Réponse du LLM
        
        Raises:
            RuntimeError: Si Ollama est indisponible
        """
        try:
            url = f"{settings.OLLAMA_BASE_URL}/api/generate"
            
            payload = {
                "model": settings.LLM_MODEL,
                "prompt": prompt,
                "stream": False,
                "temperature": 0.1,
            }
            
            response = requests.post(url, json=payload, timeout=120)
            response.raise_for_status()
            
            result = response.json()
            return result.get("response", "Erreur: pas de réponse du LLM")
        
        except requests.exceptions.ConnectionError:
            error = (
                f"Impossible de se connecter à Ollama ({settings.OLLAMA_BASE_URL}). "
                "Assurez-vous qu'Ollama est lancé."
            )
            logger.error(error)
            raise RuntimeError(error)
        
        except Exception as e:
            error_msg = f"Erreur Ollama: {e}"
            logger.error(error_msg)
            raise RuntimeError(error_msg) from e
    
    def answer_question(
        self,
        query: str,
        top_k: int = settings.TOP_K
    ) -> Tuple[str, List[Dict[str, Any]], List[str]]:
        """
        Pipeline complet: Retrieve + Generate.
        
        Args:
            query: Question de l'utilisateur
            top_k: Nombre de chunks à récupérer
        
        Returns:
            Tuple (réponse, chunks récupérés, citations)
        """
        # 1. Retrieve
        retrieved_chunks = self.retrieve(query, top_k)
        
        if not retrieved_chunks:
            return (
                "Désolé, je n'ai pas trouvé d'informations pertinentes "
                "dans les documents.",
                [],
                []
            )
        
        # 2. Generate
        answer = self.generate_answer(query, retrieved_chunks)
        
        # 3. Récupérer les citations
        citations = self.citation_handler.get_formatted_citations()
        
        return answer, retrieved_chunks, citations
    
    def get_vectorstore_stats(self) -> Dict[str, Any]:
        """Retourner les statistiques du vector store."""
        return self.vectorstore.get_stats()
