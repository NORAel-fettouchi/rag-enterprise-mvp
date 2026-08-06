"""
Point d'entrée principal de l'application Streamlit RAG.

Lancer avec: streamlit run streamlit_app.py
"""

import sys
from pathlib import Path

# Ajouter le répertoire racine au chemin pour les imports
# .resolve() convertit en chemin absolu (FIX pour Streamlit)
project_root = Path(__file__).parent.resolve()
sys.path.insert(0, str(project_root))

# Importer et lancer l'app
from app.main import main

if __name__ == "__main__":
    main()
