"""
Configuration centralisée pour l'application RAG.

Ce module charge toutes les variables d'environnement et les paramètres de configuration.
Il est le point unique de référence pour tous les paramètres de l'app.

Raison d'être :
- Évite la duplication des paramètres
- Facilite les changements de configuration
- Permet des profils différents (dev, test, prod)
- Sécurise les secrets (via .env)
"""

import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

# Charger les variables d'env depuis .env
load_dotenv()


class Settings:
    """
    Classe de configuration simple (sans Pydantic).
    
    Charge les variables d'environnement et définit les paramètres par défaut.
    """
    
    def __init__(self):
        """Initialiser la configuration."""
        # ===== PATHS =====
        self.PROJECT_ROOT = Path(__file__).parent.parent
        self.UPLOAD_DIR = self.PROJECT_ROOT / "data" / "uploads"
        self.PROCESSED_DIR = self.PROJECT_ROOT / "data" / "processed"
        self.VECTORSTORE_DIR = self.PROJECT_ROOT / "vectorstore" / "index"
        
        # ===== EMBEDDINGS =====
        self.EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
        self.EMBEDDING_DIMENSION = int(os.getenv("EMBEDDING_DIMENSION", "384"))
        
        # ===== CHUNKING =====
        self.CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "512"))
        self.CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "50"))
        
        # ===== RETRIEVAL =====
        self.TOP_K = int(os.getenv("TOP_K", "5"))
        self.SIMILARITY_THRESHOLD = float(os.getenv("SIMILARITY_THRESHOLD", "0.3"))
        
        # ===== LLM =====
        self.LLM_TYPE = os.getenv("LLM_TYPE", "ollama")
        self.LLM_MODEL = os.getenv("LLM_MODEL", "mistral")
        self.HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY")
        self.OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        self.LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.1"))
        
        # ===== APP =====
        self.APP_TITLE = os.getenv("APP_TITLE", "RAG Documentaire d'Entreprise")
        self.APP_DESCRIPTION = os.getenv("APP_DESCRIPTION", "Posez des questions sur vos documents PDF")
        self.STREAMLIT_PORT = int(os.getenv("STREAMLIT_PORT", "8501"))
        
        # ===== DEBUG & LOGGING =====
        self.DEBUG_MODE = os.getenv("DEBUG_MODE", "False").lower() in ("true", "1", "yes")
        self.LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
        
        # ===== PERFORMANCE =====
        self.BATCH_SIZE = int(os.getenv("BATCH_SIZE", "32"))
        self.NUM_WORKERS = int(os.getenv("NUM_WORKERS", "4"))
        
        # Créer les dossiers
        self._create_directories()
    
    def _create_directories(self):
        """Créer les dossiers nécessaires s'ils n'existent pas."""
        for directory in [self.UPLOAD_DIR, self.PROCESSED_DIR, self.VECTORSTORE_DIR]:
            directory.mkdir(parents=True, exist_ok=True)
            if self.DEBUG_MODE:
                print(f"✓ Dossier créé/vérifié : {directory}")
    
    def __str__(self) -> str:
        """Représentation lisible de la configuration (sans secrets)."""
        return f"""
        === Configuration RAG ===
        Embeddings: {self.EMBEDDING_MODEL} ({self.EMBEDDING_DIMENSION} dims)
        Chunking: size={self.CHUNK_SIZE}, overlap={self.CHUNK_OVERLAP}
        Retrieval: top_k={self.TOP_K}, threshold={self.SIMILARITY_THRESHOLD}
        LLM: {self.LLM_TYPE} - {self.LLM_MODEL}
        Paths:
          - Upload: {self.UPLOAD_DIR}
          - Processed: {self.PROCESSED_DIR}
          - Vectorstore: {self.VECTORSTORE_DIR}
        """


# Instance globale unique de configuration
# À importer partout : from app.config import settings
settings = Settings()