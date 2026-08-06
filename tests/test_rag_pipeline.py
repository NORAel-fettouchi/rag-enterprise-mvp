"""
Tests unitaires pour le pipeline RAG.

Tests:
- Initialisation
- Retrieval
- Vectorstore stats
"""

import pytest
from app.rag_pipeline import RAGPipeline
from app.config import settings


class TestRAGPipeline:
    """Tests pour RAGPipeline."""
    
    def test_pipeline_initialization(self):
        """Tester l'initialisation du pipeline."""
        pipeline = RAGPipeline(reload_index=True)
        
        assert pipeline.embedding_manager is not None
        assert pipeline.vectorstore is not None
        assert pipeline.chunker is not None
        assert pipeline.citation_handler is not None
    
    def test_vectorstore_stats(self):
        """Tester les stats du vectorstore."""
        pipeline = RAGPipeline(reload_index=True)
        stats = pipeline.get_vectorstore_stats()
        
        assert "nb_vectors" in stats
        assert "embedding_dim" in stats
        assert "nb_chunks" in stats
        
        # Au départ, l'index est vide
        assert stats["nb_vectors"] == 0
    
    def test_retrieve_empty_index(self):
        """Tester la récupération quand l'index est vide."""
        pipeline = RAGPipeline(reload_index=True)
        
        retrieved = pipeline.retrieve("test query")
        assert len(retrieved) == 0
    
    def test_answer_question_empty_index(self):
        """Tester answer_question quand l'index est vide."""
        pipeline = RAGPipeline(reload_index=True)
        
        answer, chunks, citations = pipeline.answer_question("test question")
        
        # Doit retourner un message vide d'infos
        assert "trouvé" in answer.lower() or "désolé" in answer.lower()
        assert len(chunks) == 0
        assert len(citations) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
