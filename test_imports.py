"""
Script pour tester les imports du projet RAG.

Utilisation:
    python test_imports.py
"""

import sys
from pathlib import Path

print("=" * 60)
print("TEST D'IMPORTS - RAG PROJECT".center(60))
print("=" * 60)

# Ajouter le répertoire racine au chemin (comme dans streamlit_app.py)
project_root = Path(__file__).parent.resolve()
sys.path.insert(0, str(project_root))

print(f"\n✓ Répertoire racine ajouté: {project_root}")
print(f"✓ PYTHONPATH[0]: {sys.path[0]}\n")

# Test 1: Configuration
try:
    from app.config import settings
    print("✅ PASS | from app.config import settings")
    print(f"   - CHUNK_SIZE: {settings.CHUNK_SIZE}")
    print(f"   - EMBEDDING_MODEL: {settings.EMBEDDING_MODEL}")
except Exception as e:
    print(f"❌ FAIL | from app.config import settings")
    print(f"   - Erreur: {e}\n")
    sys.exit(1)

# Test 2: RAG Pipeline
try:
    from app.rag_pipeline import RAGPipeline
    print("✅ PASS | from app.rag_pipeline import RAGPipeline")
except Exception as e:
    print(f"❌ FAIL | from app.rag_pipeline import RAGPipeline")
    print(f"   - Erreur: {e}\n")
    sys.exit(1)

# Test 3: Main
try:
    from app.main import main
    print("✅ PASS | from app.main import main")
except Exception as e:
    print(f"❌ FAIL | from app.main import main")
    print(f"   - Erreur: {e}\n")
    sys.exit(1)

# Test 4: Utils
try:
    from utils.pdf_loader import PDFLoader
    from utils.chunking import TextChunker
    from utils.embeddings import EmbeddingManager
    from utils.citation_handler import CitationHandler
    print("✅ PASS | Utils imports (PDF, Chunking, Embeddings, Citations)")
except Exception as e:
    print(f"❌ FAIL | Utils imports")
    print(f"   - Erreur: {e}\n")
    sys.exit(1)

# Test 5: Vector Store
try:
    from vectorstore.faiss_store import FAISSStore
    print("✅ PASS | from vectorstore.faiss_store import FAISSStore")
except Exception as e:
    print(f"❌ FAIL | from vectorstore.faiss_store import FAISSStore")
    print(f"   - Erreur: {e}\n")
    sys.exit(1)

# Test 6: Prompts
try:
    from app.prompts import format_context, get_retrieval_qa_prompt
    print("✅ PASS | from app.prompts import format_context, get_retrieval_qa_prompt")
except Exception as e:
    print(f"❌ FAIL | from app.prompts")
    print(f"   - Erreur: {e}\n")
    sys.exit(1)

print("\n" + "=" * 60)
print("✅ TOUS LES IMPORTS FONCTIONNENT CORRECTEMENT!".center(60))
print("=" * 60)
print("\n🚀 Vous pouvez maintenant lancer Streamlit:\n")
print("   streamlit run streamlit_app.py\n")
