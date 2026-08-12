"""
Module pour charger et extraire le texte des fichiers PDF.

Utilise pypdf pour extraire le texte de manière fiable.
"""

from pathlib import Path
from typing import List, Dict, Any
from pypdf import PdfReader
import logging

logger = logging.getLogger(__name__)


class PDFLoader:
    """
    Charge un PDF et extrait le texte avec métadonnées.
    
    Attributes:
        file_path: Chemin du fichier PDF
        text: Texte extrait
        metadata: Métadonnées du PDF (pages, titre, etc.)
    """
    
    def __init__(self, file_path: str | Path):
        """
        Initialiser le loader PDF.
        
        Args:
            file_path: Chemin complet du fichier PDF
            
        Raises:
            FileNotFoundError: Si le fichier n'existe pas
            ValueError: Si le fichier n'est pas un PDF valide
        """
        self.file_path = Path(file_path)
        
        if not self.file_path.exists():
            raise FileNotFoundError(f"Fichier introuvable: {file_path}")
        
        if self.file_path.suffix.lower() != ".pdf":
            raise ValueError(f"Le fichier doit être un PDF: {file_path}")
        
        self.text = ""
        self.metadata = {}
        self.pages = []
    
    def load(self) -> str:
        """
        Charger et extraire le texte du PDF.
        
        Returns:
            Texte extrait du PDF
            
        Raises:
            RuntimeError: Si l'extraction échoue
        """
        try:
            with open(self.file_path, "rb") as pdf_file:
                pdf_reader = PdfReader(pdf_file)
                
                # Extraire les métadonnées
                if pdf_reader.metadata:
                    self.metadata = {
                        "title": pdf_reader.metadata.get("/Title", "Unknown"),
                        "author": pdf_reader.metadata.get("/Author", "Unknown"),
                        "pages": len(pdf_reader.pages),
                        "source_filename": self.file_path.name,
                    }
                else:
                    self.metadata = {
                        "title": self.file_path.stem,
                        "author": "Unknown",
                        "pages": len(pdf_reader.pages),
                        "source_filename": self.file_path.name,
                    }
                
                # Extraire le texte page par page
                full_text = []
                for page_num, page in enumerate(pdf_reader.pages, start=1):
                    try:
                        page_text = page.extract_text()
                        if page_text:
                            full_text.append(f"[Page {page_num}]\n{page_text}")
                            self.pages.append({
                                "page_num": page_num,
                                "text": page_text,
                                "file": str(self.file_path.name)
                            })
                    except Exception as e:
                        logger.warning(f"Erreur extraction page {page_num}: {e}")
                        full_text.append(f"[Page {page_num} - Erreur extraction]")
                
                self.text = "\n".join(full_text)
                
                logger.info(
                    f"PDF chargé: {self.file_path.name} "
                    f"({self.metadata['pages']} pages, "
                    f"{len(self.text)} caractères)"
                )
                
                return self.text
        
        except Exception as e:
            error_msg = f"Erreur lors du chargement du PDF {self.file_path}: {e}"
            logger.error(error_msg)
            raise RuntimeError(error_msg) from e
    
    def get_metadata(self) -> Dict[str, Any]:
        """
        Retourner les métadonnées extraites du PDF.
        
        Returns:
            Dict avec titre, auteur, nombre de pages
        """
        return self.metadata
    
    def get_pages(self) -> List[Dict[str, Any]]:
        """
        Retourner le texte de chaque page avec ses métadonnées.
        
        Returns:
            Liste de dicts avec page_num, text, file
        """
        return self.pages
    
    def save_text(self, output_path: str | Path) -> None:
        """
        Sauvegarder le texte extrait dans un fichier.
        
        Args:
            output_path: Chemin du fichier de sortie
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(self.text, encoding="utf-8")
        logger.info(f"Texte sauvegardé: {output_path}")
