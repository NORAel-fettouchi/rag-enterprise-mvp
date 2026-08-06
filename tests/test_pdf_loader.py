"""
Tests unitaires pour le chargement PDF.

Tests:
- Fichier valide
- Fichier invalide
- Fichier non PDF
"""

import pytest
from pathlib import Path
import tempfile
import sys

# Ajouter le répertoire parent au chemin
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.pdf_loader import PDFLoader


class TestPDFLoader:
    """Tests pour PDFLoader."""
    
    def test_pdf_loader_invalid_path(self):
        """Tester qu'une erreur est levée pour un fichier inexistant."""
        with pytest.raises(FileNotFoundError):
            PDFLoader("fichier_inexistant.pdf")
    
    def test_pdf_loader_non_pdf(self):
        """Tester qu'une erreur est levée pour un non-PDF."""
        with tempfile.NamedTemporaryFile(suffix=".txt") as f:
            f.write(b"Ceci n'est pas un PDF")
            f.flush()
            
            with pytest.raises(ValueError):
                PDFLoader(f.name)
    
    def test_pdf_loader_empty_pdf(self):
        """Tester le chargement d'un PDF invalide."""
        with tempfile.NamedTemporaryFile(suffix=".pdf") as f:
            f.write(b"Pas un vrai PDF")
            f.flush()
            
            # Devrait lever une erreur lors du load()
            loader = PDFLoader(f.name)
            with pytest.raises(RuntimeError):
                loader.load()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
