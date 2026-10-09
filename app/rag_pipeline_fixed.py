"""
Pipeline RAG (version corrigée).

Corrections principales:
- Pas d'insertion sys.path globale (les paquets doivent être importables depuis la racine)
- Header Authorization construit depuis settings.HUGGINGFACE_API_KEY
- Format compatible OpenAI Chat Completions pour Hugging Face Inference Router
- Conservation de la logique existante
"""

from typing import List, Dict, Any, Tuple
import logging
from pathlib import Path
import requests
from collections import Counter

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
    """

    def __init__(self, reload_index: bool = False):

        logger.info("Initialisation du pipeline RAG...")

        # ===== EMBEDDINGS =====
        self.embedding_manager = EmbeddingManager()

        # ===== VECTOR STORE =====
        self.vectorstore = FAISSStore(
            embedding_dim=self.embedding_manager.get_embedding_dim()
        )

        # ===== CHUNKER =====
        self.chunker = TextChunker()

        # ===== CITATIONS =====
        self.citation_handler = CitationHandler()

        # ===== PDF LOADER =====
        self.pdf_loader = PDFLoader

        # ===== CHARGEMENT INDEX EXISTANT =====
        if not reload_index and self.vectorstore.index_exists():

            try:
                self.vectorstore.load_index()
                logger.info("Index FAISS chargé depuis le disque")

            except Exception as e:
                logger.warning(
                    f"Impossible de charger l'index existant : {e}"
                )

        logger.info("Pipeline RAG initialisé")


    # ==========================================================
    # INGESTION PDF
    # ==========================================================

    def ingest_pdf(
        self,
        pdf_path: str | Path
    ) -> Dict[str, Any]:

        try:

            pdf_path = Path(pdf_path)
            filename = pdf_path.name

            logger.info(f"Ingestion du PDF : {filename}")

            # Nettoyage de l'ancien document
            previous_sources = (
                self.vectorstore.get_document_sources()
            )

            if previous_sources:
                logger.info(
                    f"[ISOLATION] Suppression des anciens documents : "
                    f"{sorted(previous_sources)}"
                )

            self.vectorstore.clear_persistent()

            # Chargement du PDF
            loader = PDFLoader(pdf_path)

            text = loader.load()

            metadata = loader.get_metadata()

            logger.info(
                f"PDF chargé : {filename} | "
                f"{len(text)} caractères | "
                f"{metadata.get('pages', '?')} pages"
            )

            # Chunking
            self.chunker.chunk_text(
                text,
                metadata
            )

            chunks = self.chunker.get_chunks()

            logger.info(
                f"Nombre de chunks générés : {len(chunks)}"
            )

            # Embeddings
            chunks_with_embeddings = (
                self.embedding_manager.encode_chunks(
                    chunks,
                    batch_size=settings.BATCH_SIZE
                )
            )

            logger.info(
                f"{len(chunks_with_embeddings)} embeddings générés"
            )

            # Ajout FAISS
            self.vectorstore.add_chunks(
                chunks_with_embeddings
            )

            # Sauvegarde
            self.vectorstore.save_index()

            # Statistiques
            vs_stats = self.vectorstore.get_stats()

            stats = {
                "pdf_path": str(pdf_path),
                "filename": filename,
                "text_length": len(text),
                "num_chunks": len(chunks),
                "metadata": metadata,
                "vectorstore_stats": vs_stats,
            }

            logger.info(
                f"Ingestion terminée avec succès : {stats}"
            )

            return stats

        except Exception as e:

            error_msg = (
                f"Erreur lors de l'ingestion du PDF : {e}"
            )

            logger.error(error_msg)

            raise RuntimeError(error_msg) from e


    # ==========================================================
    # RETRIEVAL
    # ==========================================================

    def retrieve(
        self,
        query: str,
        top_k: int = settings.TOP_K,
        threshold: float = settings.SIMILARITY_THRESHOLD
    ) -> List[Dict[str, Any]]:

        if not query or not query.strip():
            raise ValueError(
                "La question ne peut pas être vide"
            )

        try:

            # Embedding question
            query_embedding = (
                self.embedding_manager.encode_text(
                    query
                )
            )

            # Recherche FAISS
            results = self.vectorstore.search(
                query_embedding,
                top_k
            )

            # Filtrage
            filtered_results = [
                result
                for result in results
                if result["similarity_score"] >= threshold
            ]

            # Citations
            self.citation_handler.reset()

            for result in filtered_results:
                chunk = result["chunk"]
                metadata = chunk.get(
                    "metadata",
                    {}
                )

                source_file = (
                    metadata.get("source_filename")
                    or metadata.get("title")
                    or "Unknown"
                )

                self.citation_handler.add_source(
                    chunk_id=chunk.get("id"),
                    text=chunk.get("text", ""),
                    source_file=source_file,
                    page_num=metadata.get("page_num"),
                    similarity_score=result[
                        "similarity_score"
                    ],
                )

            logger.info(
                f"Récupération : {len(filtered_results)} chunks retenus sur {len(results)}"
            )

            if filtered_results:
                source_counts = Counter(
                    result["chunk"].get("metadata", {}).get("source_filename", "Unknown")
                    for result in filtered_results
                )
                logger.info(f"Sources récupérées : {dict(source_counts)}")

            return filtered_results

        except Exception as e:
            error_msg = (
                f"Erreur lors de la récupération : {e}"
            )
            logger.error(error_msg)
            raise RuntimeError(error_msg) from e


    # ==========================================================
    # GENERATION
    # ==========================================================

    def generate_answer(
        self,
        query: str,
        retrieved_chunks: List[Dict[str, Any]]
    ) -> str:

        try:
            context = format_context(retrieved_chunks)

            prompt = get_retrieval_qa_prompt(
                context=context,
                question=query
            )

            answer = self._call_huggingface(prompt)

            logger.info(
                f"Réponse générée : {len(answer)} caractères"
            )

            return answer

        except Exception as e:
            error_msg = (
                f"Erreur lors de la génération : {e}"
            )
            logger.error(error_msg)
            raise RuntimeError(error_msg) from e


    # ==========================================================
    # HUGGING FACE API
    # ==========================================================

    def _call_huggingface(
        self,
        prompt: str
    ) -> str:

        # Vérification API Key
        if not settings.HUGGINGFACE_API_KEY:
            raise RuntimeError(
                "HUGGINGFACE_API_KEY est absente. Ajoutez votre clé dans le fichier .env."
            )

        url = (
            settings
            .HUGGINGFACE_INFERENCE_URL
            .rstrip("/")
        )

        model_name = (
            settings
            .LLM_MODEL
            .strip()
        )

        logger.info("========== HUGGING FACE API ==========")
        logger.info(f"Modèle : {model_name}")
        logger.info(f"URL : {url}")

        # Headers
        headers = {
            "Authorization": f"Bearer {settings.HUGGINGFACE_API_KEY}",
            "Content-Type": "application/json",
        }

        # Payload OpenAI Chat Completions compatible
        payload = {
            "model": model_name,
            "messages": [
                {"role": "system", "content": (
                    "Tu es un assistant expert en analyse documentaire. "
                    "Réponds uniquement à partir du contexte fourni. Si l'information est "
                    "absente, indique-le clairement. Réponds en français."
                )},
                {"role": "user", "content": prompt}
            ],
            "temperature": settings.LLM_TEMPERATURE,
            "max_tokens": settings.LLM_MAX_NEW_TOKENS,
        }

        try:
            response = requests.post(
                url,
                headers=headers,
                json=payload,
                timeout=settings.LLM_TIMEOUT
            )

            logger.info(f"HTTP Status : {response.status_code}")

            if response.status_code >= 400:
                # Tenter d'obtenir le détail JSON retourné par l'API
                try:
                    error_detail = response.json()
                except Exception:
                    error_detail = response.text[:1000]

                # Messages spécifiques pour les codes courants
                if response.status_code == 401:
                    hint = (
                        "401 Unauthorized — clé API invalide ou absente. "
                        "Vérifiez que HUGGINGFACE_API_KEY est défini correctement dans .env (sans guillemets) "
                        "et que Streamlit a redémarré après la mise à jour."
                    )
                elif response.status_code == 403:
                    hint = (
                        "403 Forbidden — accès refusé. Vérifiez les permissions du token HF ou l'URL d'inférence."
                    )
                elif response.status_code == 404:
                    hint = (
                        "404 Not Found — l'URL d'inférence ou le modèle est introuvable. Vérifiez HUGGINGFACE_INFERENCE_URL et le nom du modèle."
                    )
                elif response.status_code == 429:
                    hint = (
                        "429 Rate limit — vous atteignez la limite de requêtes. Essayez plus tard ou utilisez un token avec de meilleurs quotas."
                    )
                else:
                    hint = "Erreur HTTP depuis Hugging Face."

                error = (
                    f"Erreur HTTP {response.status_code} Hugging Face. Model: {model_name}. Detail API: {error_detail} | {hint}"
                )

                logger.error(error)
                raise RuntimeError(error)

            try:
                result = response.json()
            except ValueError:
                raise RuntimeError(
                    "La réponse de Hugging Face n'est pas un JSON valide : "
                    f"{response.text[:500]}"
                )

            # Extraction chat completion
            if isinstance(result, dict) and result.get("choices"):
                choices = result.get("choices", [])
                if choices:
                    choice = choices[0]
                    message = choice.get("message", {})
                    content = message.get("content")
                    if content:
                        logger.info(f"Réponse LLM extraite : {len(content)} caractères")
                        return content.strip()

                    # fallback
                    reasoning_content = message.get("reasoning_content")
                    if reasoning_content:
                        logger.warning("Le modèle a retourné reasoning_content au lieu de content.")
                        return reasoning_content.strip()

                    raise RuntimeError(
                        "La réponse du LLM ne contient ni 'content' ni 'reasoning_content'. "
                        f"Réponse : {result}"
                    )

            raise RuntimeError(
                "Format de réponse Hugging Face inattendu. "
                f"Réponse : {str(result)[:1000]}"
            )

        except requests.exceptions.Timeout:
            raise RuntimeError(
                f"Timeout Hugging Face après {settings.LLM_TIMEOUT} secondes."
            )
        except requests.exceptions.ConnectionError as e:
            raise RuntimeError(
                "Impossible de se connecter à Hugging Face. "
                f"Détail : {e}"
            )
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Erreur réseau Hugging Face : {e}")


    # ==========================================================
    # PIPELINE COMPLET
    # ==========================================================

    def answer_question(
        self,
        query: str,
        top_k: int = settings.TOP_K
    ) -> Tuple[
        str,
        List[Dict[str, Any]],
        List[str]
    ]:

        retrieved_chunks = self.retrieve(
            query=query,
            top_k=top_k
        )

        if not retrieved_chunks:
            return (
                "Je ne trouve pas cette information dans les documents fournis.",
                [],
                []
            )

        answer = self.generate_answer(
            query=query,
            retrieved_chunks=retrieved_chunks
        )

        citations = self.citation_handler.get_formatted_citations()

        return (
            answer,
            retrieved_chunks,
            citations
        )

    # ==========================================================
    # STATISTIQUES
    # ==========================================================

    def get_vectorstore_stats(self) -> Dict[str, Any]:
        stats = self.vectorstore.get_stats()
        sources = self.vectorstore.get_document_sources()
        stats["nb_documents"] = len(sources)
        stats["documents"] = sorted(sources) if sources else []
        return stats

    # ==========================================================
    # HUGGING FACE KEY VALIDATION
    # ==========================================================

    def validate_hf_key(self) -> Dict[str, Any]:
        """
        Effectuer un petit appel test à Hugging Face pour valider que
        la clé API et l'URL d'inférence fonctionnent.

        Returns:
            Dict contenant 'ok' (bool), 'status' (int optionnel), 'message' (str)
        """
        if not settings.HUGGINGFACE_API_KEY or 'METTEZ' in (settings.HUGGINGFACE_API_KEY or ''):
            return {
                "ok": False,
                "message": "HUGGINGFACE_API_KEY absent ou placeholder dans .env. Mettez votre clé et redémarrez Streamlit."
            }

        url = settings.HUGGINGFACE_INFERENCE_URL.rstrip('/')
        model_name = settings.LLM_MODEL.strip()

        headers = {
            "Authorization": f"Bearer {settings.HUGGINGFACE_API_KEY}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": model_name,
            "messages": [{"role": "user", "content": "Ping"}],
            "max_tokens": 1,
            "temperature": 0.0,
        }

        try:
            resp = requests.post(url, headers=headers, json=payload, timeout=10)

            if resp.status_code == 200:
                return {"ok": True, "status": 200, "message": "Clé valide — test HF OK (HTTP 200)."}

            # otherwise try to parse body
            try:
                detail = resp.json()
            except Exception:
                detail = resp.text[:1000]

            # map common codes to helpful hints
            hint = ""
            if resp.status_code == 401:
                hint = "401 Unauthorized — clé API invalide ou absente. Vérifiez que HUGGINGFACE_API_KEY est défini correctement et redémarrez Streamlit."
            elif resp.status_code == 403:
                hint = "403 Forbidden — accès refusé. Vérifiez les permissions du token HF ou l'URL d'inférence."
            elif resp.status_code == 404:
                hint = "404 Not Found — URL d'inférence ou modèle introuvable. Vérifiez HUGGINGFACE_INFERENCE_URL et LLM_MODEL."
            elif resp.status_code == 429:
                hint = "429 Rate limit — vous atteignez la limite de requêtes."

            return {"ok": False, "status": resp.status_code, "message": f"HTTP {resp.status_code}: {detail} | {hint}"}

        except requests.exceptions.RequestException as e:
            return {"ok": False, "message": f"Erreur réseau lors du test HF: {e}"}
