"""
Module pour découper le texte en chunks (segments) intelligents.

Le chunking est crucial pour le RAG:
- Chunks trop petits = perte de contexte
- Chunks trop grands = bruit et coûts embedding élevés
"""

from typing import List, Dict, Any
import logging
from app.config import settings

logger = logging.getLogger(__name__)


class TextChunker:
    """
    Découpe le texte en chunks avec chevauchement.
    
    Attributes:
        chunk_size: Taille maximale d'un chunk (caractères)
        chunk_overlap: Chevauchement entre chunks (caractères)
        chunks: Liste des chunks générés
    """
    
    def __init__(
        self,
        chunk_size: int = settings.CHUNK_SIZE,
        chunk_overlap: int = settings.CHUNK_OVERLAP
    ):
        """
        Initialiser le chunker.
        
        Args:
            chunk_size: Taille d'un chunk (défaut 512)
            chunk_overlap: Chevauchement (défaut 50)
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.chunks: List[Dict[str, Any]] = []
        
        if chunk_overlap >= chunk_size:
            raise ValueError(
                f"Overlap ({chunk_overlap}) ne peut pas être >= size ({chunk_size})"
            )
    
    def chunk_text(
        self,
        text: str,
        metadata: Dict[str, Any] | None = None
    ) -> List[str]:
        """
        Découper le texte en chunks.
        
        Args:
            text: Texte à découper
            metadata: Métadonnées à associer (source, titre, etc.)
        
        Returns:
            Liste de chunks
        """
        if not text or not text.strip():
            logger.warning("Texte vide fourni au chunker")
            return []
        
        metadata = metadata or {}
        self.chunks = []
        
        # Nettoyer le texte
        text = self._clean_text(text)
        
        # Diviser par paragraphes d'abord (plus intelligent)
        paragraphs = text.split("\n\n")
        current_chunk = ""
        chunk_id = 0
        
        for paragraph in paragraphs:
            # Si l'ajout dépasse la limite, sauvegarder le chunk actuel
            if (
                len(current_chunk) + len(paragraph) > self.chunk_size
                and current_chunk
            ):
                # Sauvegarder le chunk (avec une copie des métadonnées)
                self.chunks.append({
                    "id": chunk_id,
                    "text": current_chunk.strip(),
                    "size": len(current_chunk),
                    "metadata": self._enrich_metadata(metadata, current_chunk),
                })
                chunk_id += 1
                
                # Démarrer un nouveau chunk avec chevauchement
                overlap_text = self._get_overlap(current_chunk)
                current_chunk = overlap_text + paragraph
            else:
                current_chunk += "\n\n" + paragraph if current_chunk else paragraph
        
        # Sauvegarder le dernier chunk
        if current_chunk.strip():
            self.chunks.append({
                "id": chunk_id,
                "text": current_chunk.strip(),
                "size": len(current_chunk),
                "metadata": self._enrich_metadata(metadata, current_chunk),
            })
        
        logger.info(
            f"Texte découpé en {len(self.chunks)} chunks "
            f"(size={self.chunk_size}, overlap={self.chunk_overlap})"
        )
        
        return [chunk["text"] for chunk in self.chunks]
    
    def _enrich_metadata(
        self,
        metadata: Dict[str, Any],
        chunk_text: str
    ) -> Dict[str, Any]:
        """
        Enrichir les métadonnées d'un chunk.
        
        Copie le dict de métadonnées (évite les références partagées)
        et extrait le numéro de page depuis le marker [Page N] du texte.
        
        Args:
            metadata: Métadonnées de base du document
            chunk_text: Texte du chunk (peut contenir [Page N])
        
        Returns:
            Copie des métadonnées avec source_filename et page_num
        """
        enriched = dict(metadata)
        
        # Extraire les numéros de page depuis le texte (markers [Page N])
        import re
        page_markers = re.findall(r"\[Page (\d+)\]", chunk_text)
        if page_markers:
            enriched["page_num"] = int(page_markers[0])
        else:
            enriched["page_num"] = None
        
        # Garantir un nom de fichier source
        if "source_filename" not in enriched or not enriched["source_filename"]:
            enriched["source_filename"] = enriched.get("title", "Unknown.pdf")
        
        return enriched
    
    def _clean_text(self, text: str) -> str:
        """
        Nettoyer le texte (espaces multiples, lignes vides, etc.).
        
        Args:
            text: Texte brut
        
        Returns:
            Texte nettoyé
        """
        # Remplacer les espaces multiples par un seul
        text = " ".join(text.split())
        
        # Remplacer les sauts de ligne multiples
        while "\n\n\n" in text:
            text = text.replace("\n\n\n", "\n\n")
        
        return text.strip()
    
    def _get_overlap(self, chunk: str) -> str:
        """
        Extraire les derniers caractères pour le chevauchement.
        
        Args:
            chunk: Chunk courant
        
        Returns:
            Partie à conserver pour le chevauchement
        """
        # Garder les derniers overlap_size caractères
        overlap_size = min(self.chunk_overlap, len(chunk))
        
        # Ne pas couper au milieu d'un mot
        overlap_text = chunk[-overlap_size:]
        last_space = overlap_text.rfind(" ")
        
        if last_space != -1:
            overlap_text = overlap_text[last_space + 1:]
        
        return overlap_text
    
    def get_chunks(self) -> List[Dict[str, Any]]:
        """
        Retourner tous les chunks avec métadonnées.
        
        Returns:
            Liste des chunks avec ID, texte, métadonnées
        """
        return self.chunks
    
    def chunk_documents(
        self,
        documents: List[str],
        metadatas: List[Dict[str, Any]] | None = None
    ) -> List[Dict[str, Any]]:
        """
        Découper plusieurs documents d'un coup.
        
        Args:
            documents: Liste de textes
            metadatas: Métadonnées correspondantes
        
        Returns:
            Liste de tous les chunks de tous les documents
        """
        if not metadatas:
            metadatas = [{} for _ in documents]
        
        all_chunks = []
        global_chunk_id = 0
        
        for doc_idx, (doc, meta) in enumerate(zip(documents, metadatas)):
            chunks = self.chunk_text(doc, meta)
            
            for chunk in chunks:
                all_chunks.append({
                    "id": global_chunk_id,
                    "doc_index": doc_idx,
                    "text": chunk,
                    "metadata": meta,
                })
                global_chunk_id += 1
        
        return all_chunks
