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
from collections import Counter

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
        0. Réinitialiser le vector store (isolation des documents)
        1. Charger le PDF
        2. Découper en chunks
        3. Générer les embeddings
        4. Ajouter au vector store
        
        IMPORTANT (isolation des documents):
        Le vector store est réinitialisé AVANT d'ingérer le nouveau PDF.
        Cela garantit que l'index ne contient QUE le document actuellement
        uploadé — jamais les chunks d'un PDF précédent.
        
        Args:
            pdf_path: Chemin du fichier PDF
        
        Returns:
            Dict avec statistiques d'ingestion
        
        Raises:
            FileNotFoundError: Si le PDF n'existe pas
            RuntimeError: Si l'ingestion échoue
        """
        try:
            pdf_path = Path(pdf_path)
            filename = pdf_path.name
            logger.info(f"Ingestion du PDF: {filename}")
            
            # 0. RÉINITIALISATION COMPLÈTE AVANT INDEXATION
            # ==================================================
            # Supprime les chunks de tout document précédent :
            # - en mémoire (index FAISS + liste de chunks)
            # - sur le disque (index.faiss + chunks.json)
            # Cela empêche le mélange entre PDF A et PDF B.
            # ==================================================
            previous_sources = self.vectorstore.get_document_sources()
            if previous_sources:
                logger.info(
                    f"[ISOLATION] Réinitialisation du vector store. "
                    f"Anciens documents présents: {sorted(previous_sources)}"
                )
            else:
                logger.info(
                    "[ISOLATION] Réinitialisation du vector store "
                    "(aucun document précédent)"
                )
            
            self.vectorstore.clear_persistent()
            
            # 1. Charger le PDF
            loader = PDFLoader(pdf_path)
            text = loader.load()
            metadata = loader.get_metadata()
            
            logger.info(
                f"PDF chargé: {filename} - {len(text)} caractères, "
                f"{metadata.get('pages', '?')} pages"
            )
            
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
            
            # 6. Diagnostic : état du vector store après ingestion
            vs_stats = self.vectorstore.get_stats()
            current_sources = self.vectorstore.get_document_sources()
            logger.info(
                f"[DIAGNOSTIC] Document: {filename} | "
                f"Chunks indexés: {vs_stats['nb_chunks']} | "
                f"Vecteurs: {vs_stats['nb_vectors']} | "
                f"Documents représentés: {len(current_sources)} "
                f"({sorted(current_sources) if current_sources else 'aucun'})"
            )
            
            stats = {
                "pdf_path": str(pdf_path),
                "filename": filename,
                "text_length": len(text),
                "num_chunks": len(chunks),
                "metadata": metadata,
                "vectorstore_stats": vs_stats,
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
                # Utiliser source_filename si dispo, sinon title
                meta = chunk.get("metadata", {})
                source_file = (
                    meta.get("source_filename")
                    or meta.get("title")
                    or "Unknown"
                )
                self.citation_handler.add_source(
                    chunk_id=chunk.get("id"),
                    text=chunk.get("text", ""),
                    source_file=source_file,
                    page_num=meta.get("page_num"),
                    similarity_score=result["similarity_score"],
                )
            
            logger.info(
                f"Récupération: {len(filtered_results)} chunks "
                f"(sur {len(results)} récupérés)"
            )
            
            # Diagnostic des sources récupérées
            if filtered_results:
                source_counts = Counter(
                    r["chunk"].get("metadata", {}).get("source_filename", "Unknown")
                    for r in filtered_results
                )
                logger.info(
                    f"[DIAGNOSTIC] Sources des chunks récupérés: "
                    f"{dict(source_counts)}"
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
        
        Utilise HuggingFace Inference API.
        
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
            
            # Générer la réponse avec HuggingFace Inference API
            response = self._call_huggingface(prompt)
            
            logger.info(f"Réponse générée: {len(response)} caractères")
            return response
        
        except Exception as e:
            error_msg = f"Erreur lors de la génération: {e}"
            logger.error(error_msg)
            raise RuntimeError(error_msg) from e
    
    def _call_huggingface(self, prompt: str) -> str:
        """
        Appeler HuggingFace Inference API pour générer une réponse.
        
        Args:
            prompt: Prompt formaté
        
        Returns:
            Réponse du LLM
        
        Raises:
            RuntimeError: Si l'API est indisponible ou la clé manquante
        """
        # Vérifier que la clé API est configurée
        if not settings.HUGGINGFACE_API_KEY:
            error = (
                "HUGGINGFACE_API_KEY n'est pas configurée. "
                "Ajoutez-la dans le fichier .env."
            )
            logger.error(error)
            raise RuntimeError(error)
        
        try:
            # ===== Construire l'URL de l'API =====
            # L'URL de base est l'endpoint complet chat/completions.
            # Le modèle est passé dans le payload, pas dans l'URL.
            url = settings.HUGGINGFACE_INFERENCE_URL.rstrip("/")
            model_name = settings.LLM_MODEL.strip()
            
            logger.info("========== HUGGINGFACE API REQUEST ==========")
            logger.info(f"Model name: {model_name}")
            # Ne jamais logger l'URL complète si elle contient la clé (normalement non)
            logger.info(f"Final URL: {url}")
            
            headers = {
                "Authorization": f"Bearer {settings.HUGGINGFACE_API_KEY}",
                "Content-Type": "application/json",
            }
            
            # Format OpenAI-compatible chat completions
            payload = {
                "model": model_name,
                "messages": [
                    {"role": "user", "content": prompt}
                ],
                "temperature": settings.LLM_TEMPERATURE,
                "max_tokens": settings.LLM_MAX_NEW_TOKENS,
            }
            
            # Logs de debug (sans révéler la clé API)
            logger.info(
                "Requête HuggingFace Inference API préparée "
                f"(clé: ****{settings.HUGGINGFACE_API_KEY[-4:]})"
            )
            logger.info(
                f"Request payload: prompt_len={len(prompt)} chars, "
                f"temperature={settings.LLM_TEMPERATURE}, "
                f"max_tokens={settings.LLM_MAX_NEW_TOKENS}"
            )
            
            logger.info(
                f"Appel HuggingFace Inference API: {model_name}, "
                f"timeout={settings.LLM_TIMEOUT}s"
            )
            
            response = requests.post(
                url,
                headers=headers,
                json=payload,
                timeout=settings.LLM_TIMEOUT
            )
            
            # LOG DU DEBUG: code de statut et corps de réponse (tronqué)
            logger.info(f"Response status code: {response.status_code}")
            
            # Gestion explicite des erreurs HTTP avec messages actionnables.
            # IMPORTANT: Ne jamais inclure la clé API ou l'URL complète dans les logs.
            if response.status_code == 400:
                error = (
                    "Erreur HTTP 400 de HuggingFace Inference API: "
                    f"le modèle '{model_name}' est incompatible avec "
                    "le provider sélectionné ou la requête est invalide. "
                    "Vérifiez LLM_MODEL dans le fichier .env "
                    "(ex: Qwen/Qwen2.5-7B-Instruct)."
                )
                logger.error(error)
                raise RuntimeError(error)
            
            if response.status_code == 401:
                error = (
                    "Erreur HTTP 401 de HuggingFace Inference API: "
                    "clé API invalide ou expirée. "
                    "Vérifiez HUGGINGFACE_API_KEY dans le fichier .env "
                    "(https://huggingface.co/settings/tokens)."
                )
                logger.error(error)
                raise RuntimeError(error)
            
            if response.status_code == 403:
                error = (
                    "Erreur HTTP 403 de HuggingFace Inference API: "
                    "accès refusé au modèle. Vérifiez que votre compte "
                    "a accès au modèle et que la clé API est valide."
                )
                logger.error(error)
                raise RuntimeError(error)
            
            if response.status_code == 404:
                error = (
                    "Erreur HTTP 404 de HuggingFace Inference API: "
                    f"modèle '{model_name}' introuvable. "
                    "Vérifiez LLM_MODEL dans le fichier .env "
                    "(ex: Qwen/Qwen2.5-7B-Instruct)."
                )
                logger.error(error)
                raise RuntimeError(error)
            
            if response.status_code == 429:
                error = (
                    "Erreur HTTP 429 de HuggingFace Inference API: "
                    "trop de requêtes (rate limit atteint). "
                    "Attendez quelques instants et réessayez, "
                    "ou réduisez la fréquence des requêtes."
                )
                logger.error(error)
                raise RuntimeError(error)
            
            # Toute autre erreur HTTP
            if response.status_code >= 400:
                response_body = ""
                try:
                    response_body = response.text[:500]
                except Exception:
                    response_body = "<non lisible>"
                error = (
                    f"Erreur HTTP {response.status_code} de "
                    "HuggingFace Inference API. "
                    f"Réponse: {response_body}"
                )
                logger.error(error)
                raise RuntimeError(error)
            
            # Succès: parser le corps JSON (sans le logger en entier)
            try:
                result = response.json()
            except ValueError:
                error = (
                    "Réponse invalide de HuggingFace Inference API: "
                    "le corps n'est pas du JSON valide."
                )
                logger.error(error)
                raise RuntimeError(error)
            
            # Format OpenAI-compatible chat completions:
            # {"choices": [{"message": {"content": "..."}}]}
            if isinstance(result, dict) and result.get("choices"):
                choices = result["choices"]
                if choices and isinstance(choices[0], dict):
                    message = choices[0].get("message", {})
                    generated = message.get("content", "")
                    if generated:
                        logger.info(
                            f"Parsed response: chat completion "
                            f"({len(generated)} chars)"
                        )
                        return generated.strip()
            
            # Fallback: réponse directe sous forme de string
            if isinstance(result, str):
                logger.info(
                    f"Parsed response: raw string ({len(result)} chars)"
                )
                return result.strip()
            
            error = (
                "Format de réponse inattendu de HuggingFace Inference API: "
                "le JSON ne correspond pas à chat completions."
            )
            logger.error(error)
            raise RuntimeError(error)
        
        except requests.exceptions.Timeout:
            error = (
                f"Timeout lors de l'appel à HuggingFace Inference API "
                f"({settings.LLM_TIMEOUT}s). Le modèle peut être en cours "
                "de chargement ou surchargé."
            )
            logger.error(error)
            raise RuntimeError(error)
        
        except requests.exceptions.ConnectionError as e:
            error = (
                "Impossible de se connecter à HuggingFace Inference API "
                f"({settings.HUGGINGFACE_INFERENCE_URL}). "
                "Vérifiez votre connexion internet. "
                f"Détail: {e}"
            )
            logger.error(error)
            raise RuntimeError(error)
        
        except requests.exceptions.InvalidURL as e:
            error = (
                "URL invalide pour HuggingFace Inference API: "
                f"{e}. Vérifiez HUGGINGFACE_INFERENCE_URL dans le fichier .env."
            )
            logger.error(error)
            raise RuntimeError(error)
        
        except Exception as e:
            error_msg = f"Erreur HuggingFace Inference API: {e}"
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
        stats = self.vectorstore.get_stats()
        
        # Ajouter le nombre de documents représentés
        sources = self.vectorstore.get_document_sources()
        stats["nb_documents"] = len(sources)
        stats["documents"] = sorted(sources) if sources else []
        
        return stats