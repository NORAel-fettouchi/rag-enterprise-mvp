"""
Module pour gérer les citations et tracer les sources.

Les citations sont essentielles pour la confiance en RAG:
- L'utilisateur voit d'où vient l'info
- On peut vérifier la source
- On évite les hallucinations
"""

from typing import List, Dict, Any, Tuple
import logging

logger = logging.getLogger(__name__)


class CitationHandler:
    """
    Gère les citations et les métadonnées des sources.
    
    Attributes:
        citations: Liste des citations générées
    """
    
    def __init__(self):
        """Initialiser le gestionnaire de citations."""
        self.citations: List[Dict[str, Any]] = []
    
    def add_source(
        self,
        chunk_id: int,
        text: str,
        source_file: str,
        page_num: int | None = None,
        similarity_score: float | None = None
    ) -> Dict[str, Any]:
        """
        Ajouter une source utilisée dans la réponse.
        
        Args:
            chunk_id: ID du chunk utilisé
            text: Texte du chunk
            source_file: Nom du fichier source
            page_num: Numéro de page (optionnel)
            similarity_score: Score de similarité (optionnel)
        
        Returns:
            Dictionnaire de la citation ajoutée
        """
        citation = {
            "chunk_id": chunk_id,
            "text": text[:100] + "..." if len(text) > 100 else text,
            "source_file": source_file,
            "page_num": page_num,
            "similarity_score": similarity_score,
        }
        
        self.citations.append(citation)
        logger.debug(f"Citation ajoutée: {source_file} (page {page_num})")
        
        return citation
    
    def format_citation(self, citation: Dict[str, Any]) -> str:
        """
        Formater une citation pour l'affichage.
        
        Args:
            citation: Dict de citation
        
        Returns:
            String formatée prête à afficher
        """
        source_str = f"📄 {citation['source_file']}"
        
        if citation.get("page_num"):
            source_str += f" (page {citation['page_num']})"
        
        if citation.get("similarity_score"):
            score = citation["similarity_score"]
            source_str += f" [Pertinence: {score:.2%}]"
        
        return source_str
    
    def get_citations(self) -> List[Dict[str, Any]]:
        """
        Retourner toutes les citations collectées.
        
        Returns:
            Liste des citations
        """
        return self.citations
    
    def get_formatted_citations(self) -> List[str]:
        """
        Retourner les citations formatées.
        
        Returns:
            Liste de strings formatées
        """
        return [self.format_citation(c) for c in self.citations]
    
    def reset(self) -> None:
        """Réinitialiser les citations."""
        self.citations = []
        logger.debug("Citations réinitialisées")
    
    def deduplicate_citations(self) -> None:
        """
        Supprimer les citations en double (même fichier + page).
        
        Utile quand plusieurs chunks viennent de la même source.
        """
        seen = set()
        unique_citations = []
        
        for citation in self.citations:
            # Créer une clé unique
            key = (
                citation.get("source_file"),
                citation.get("page_num")
            )
            
            if key not in seen:
                seen.add(key)
                unique_citations.append(citation)
        
        self.citations = unique_citations
        logger.info(
            f"Citations dédupliquées: {len(self.citations)} reste"
        )
    
    def get_top_sources(self, top_k: int = 3) -> List[Dict[str, Any]]:
        """
        Retourner les meilleures sources (par score de similarité).
        
        Args:
            top_k: Nombre de sources à retourner
        
        Returns:
            Liste des top_k sources triées par score
        """
        # Trier par score de similarité décroissant
        sorted_citations = sorted(
            self.citations,
            key=lambda x: x.get("similarity_score", 0),
            reverse=True
        )
        
        return sorted_citations[:top_k]
    
    def generate_bibliography(self) -> str:
        """
        Générer une bibliographie formatée.
        
        Returns:
            String avec liste des sources
        """
        self.deduplicate_citations()
        
        if not self.citations:
            return "Aucune source disponible."
        
        bibliography = "### 📚 Sources utilisées\n\n"
        
        for i, citation in enumerate(self.citations, 1):
            bib_line = f"{i}. {citation['source_file']}"
            
            if citation.get("page_num"):
                bib_line += f", page {citation['page_num']}"
            
            if citation.get("similarity_score"):
                bib_line += (
                    f" (Pertinence: {citation['similarity_score']:.1%})"
                )
            
            bibliography += bib_line + "\n"
        
        return bibliography
    
    def extract_cited_text_with_source(
        self,
        original_chunks: List[Dict[str, Any]]
    ) -> List[Tuple[str, Dict[str, Any]]]:
        """
        Retourner le texte des chunks cités avec leurs sources.
        
        Args:
            original_chunks: Liste originale des chunks
        
        Returns:
            Liste de tuples (chunk_id, chunk_dict)
        """
        chunk_map = {chunk["id"]: chunk for chunk in original_chunks}
        
        result = []
        for citation in self.citations:
            chunk_id = citation["chunk_id"]
            if chunk_id in chunk_map:
                result.append((chunk_id, chunk_map[chunk_id]))
        
        return result
