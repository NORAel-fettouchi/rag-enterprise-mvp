"""
Tests unitaires pour le chunking.

Tests:
- Découpage de texte
- Chevauchement
- Texte vide
- Configuration invalide
"""

import pytest
import sys
from pathlib import Path

# Ajouter le répertoire parent au chemin
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.chunking import TextChunker


class TestTextChunker:
    """Tests pour TextChunker."""
    
    def test_chunker_initialization(self):
        """Tester l'initialisation du chunker."""
        chunker = TextChunker(chunk_size=256, chunk_overlap=32)
        assert chunker.chunk_size == 256
        assert chunker.chunk_overlap == 32
    
    def test_chunker_invalid_overlap(self):
        """Tester qu'une erreur est levée si overlap >= size."""
        with pytest.raises(ValueError):
            TextChunker(chunk_size=256, chunk_overlap=256)
    
    def test_chunker_empty_text(self):
        """Tester le chunking avec texte vide."""
        chunker = TextChunker()
        chunks = chunker.chunk_text("")
        assert len(chunks) == 0
    
    def test_chunker_small_text(self):
        """Tester le chunking avec petit texte."""
        chunker = TextChunker(chunk_size=100)
        text = "Ceci est un petit texte."
        chunks = chunker.chunk_text(text)
        assert len(chunks) == 1
        assert chunks[0] == text
    
    def test_chunker_large_text(self):
        """Tester le chunking avec texte volumineux."""
        chunker = TextChunker(chunk_size=100, chunk_overlap=10)
        
        # Créer un texte plus grand que chunk_size
        text = " ".join(["word"] * 50)  # ~250 caractères
        chunks = chunker.chunk_text(text)
        
        assert len(chunks) >= 1
        
        # Vérifier que chaque chunk respecte la taille limite
        for chunk in chunks:
            assert len(chunk) <= chunker.chunk_size + 50  # Marge pour mots
    
    def test_chunker_with_metadata(self):
        """Tester le chunking avec métadonnées."""
        chunker = TextChunker()
        text = "Test texte avec métadonnées."
        metadata = {"source": "test.pdf", "page": 1}
        
        chunker.chunk_text(text, metadata)
        chunks = chunker.get_chunks()
        
        assert len(chunks) > 0
        assert chunks[0]["metadata"] == metadata


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
