"""
Script de diagnostic complet du pipeline RAG.

Trace chaque étape:
1. PDF Loading
2. Text Extraction
3. Chunking
4. Embeddings
5. FAISS
6. Retrieval
7. Prompt
8. LLM

Usage:
    python diagnostic_rag.py
"""

import sys
from pathlib import Path
import logging
import tempfile
from typing import List, Dict, Any

# Ajouter le répertoire racine au chemin
project_root = Path(__file__).parent.resolve()
sys.path.insert(0, str(project_root))

# Configuration du logging avec PLUS de détails
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s | %(name)s | %(levelname)s | %(message)s"
)
logger = logging.getLogger(__name__)

# Importer les modules après avoir configuré le path
from app.config import settings
from app.rag_pipeline import RAGPipeline
from utils.pdf_loader import PDFLoader
from utils.chunking import TextChunker
from utils.embeddings import EmbeddingManager
from vectorstore.faiss_store import FAISSStore

print("\n" + "=" * 80)
print("DIAGNOSTIC RAG - Traçage complet du pipeline".center(80))
print("=" * 80 + "\n")

# =============================================================================
# 1. VÉRIFIER LA CONFIGURATION
# =============================================================================

print("1️⃣  CONFIGURATION")
print("-" * 80)
print(f"   Modèle embeddings: {settings.EMBEDDING_MODEL}")
print(f"   Dimension embeddings: {settings.EMBEDDING_DIMENSION}")
print(f"   Chunk size: {settings.CHUNK_SIZE}")
print(f"   Chunk overlap: {settings.CHUNK_OVERLAP}")
print(f"   TOP_K (retrieval): {settings.TOP_K}")
print(f"   SIMILARITY_THRESHOLD: {settings.SIMILARITY_THRESHOLD} ⚠️ IMPORTANT!")
print(f"   VECTORSTORE_DIR: {settings.VECTORSTORE_DIR}")
print()

# =============================================================================
# CRÉER UN PDF DE TEST AVEC LE NOM "NORA EL-FETTOUCHI"
# =============================================================================

print("2️⃣  CRÉATION PDF DE TEST")
print("-" * 80)

try:
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas
    import io
    
    # Créer un PDF avec le contenu de test
    pdf_buffer = io.BytesIO()
    c = canvas.Canvas(pdf_buffer, pagesize=letter)
    
    # Écrire le contenu
    content = """
    CV DE NORA EL-FETTOUCHI
    
    Nora EL-FETTOUCHI est une professionnelle expérimentée dans le domaine de 
    l'intelligence artificielle et du traitement des données.
    
    Son nom complet est Nora EL-FETTOUCHI.
    
    Expérience professionnelle:
    - Développeuse IA chez TechCorp (2020-2023)
    - Ingénieure Données chez DataFlow (2018-2020)
    
    Formations:
    - Master IA - Université X (2018)
    - Licence Informatique - Université Y (2016)
    
    Compétences:
    - Machine Learning
    - Deep Learning
    - NLP
    - Python, TensorFlow, PyTorch
    """
    
    c.drawString(50, 750, "CV")
    y_position = 730
    for line in content.strip().split('\n'):
        c.drawString(50, y_position, line)
        y_position -= 20
    
    c.save()
    pdf_bytes = pdf_buffer.getvalue()
    
    # Sauvegarder le PDF de test
    test_pdf_path = project_root / "test_nora_cv.pdf"
    with open(test_pdf_path, "wb") as f:
        f.write(pdf_bytes)
    
    print(f"   ✓ PDF de test créé: {test_pdf_path}")
    print(f"   ✓ Taille: {len(pdf_bytes)} bytes")
    print()
    
except ImportError:
    print("   ⚠️  reportlab non installé, utilisation d'un PDF existant")
    # Chercher un PDF existant
    test_pdf_path = None
    for pdf_file in project_root.glob("*.pdf"):
        test_pdf_path = pdf_file
        break
    
    if not test_pdf_path:
        print("   ❌ Aucun PDF trouvé!")
        sys.exit(1)
    
    print(f"   ✓ Utilisation du PDF: {test_pdf_path}")
    print()

# =============================================================================
# 3. PDF LOADING - Charger et extraire le PDF
# =============================================================================

print("3️⃣  PDF LOADING - Extraction du texte")
print("-" * 80)

try:
    pdf_loader = PDFLoader(test_pdf_path)
    text = pdf_loader.load()
    metadata = pdf_loader.get_metadata()
    
    print(f"   ✓ Fichier chargé: {pdf_loader.file_path}")
    print(f"   ✓ Pages: {metadata.get('pages', '?')}")
    print(f"   ✓ Auteur: {metadata.get('author', 'Unknown')}")
    print(f"   ✓ Titre: {metadata.get('title', 'Unknown')}")
    print(f"   ✓ Texte extrait: {len(text)} caractères")
    print(f"\n   Extrait du texte (premiers 200 chars):")
    print(f"   {repr(text[:200])}")
    print()
    
    # Vérifier si le nom "Nora" est dans le texte
    if "nora" in text.lower():
        print("   ✅ Le nom 'NORA' est présent dans le texte!")
    else:
        print("   ❌ Le nom 'NORA' N'EST PAS présent dans le texte!")
    print()
    
except Exception as e:
    print(f"   ❌ ERREUR PDF LOADING: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# =============================================================================
# 4. CHUNKING - Découper le texte en chunks
# =============================================================================

print("4️⃣  CHUNKING - Segmentation du texte")
print("-" * 80)

try:
    chunker = TextChunker()
    chunks_data = chunker.chunk_text(text, metadata)
    chunks = chunker.get_chunks()
    
    print(f"   ✓ Chunks générés: {len(chunks)}")
    print(f"   ✓ Configuration: size={settings.CHUNK_SIZE}, overlap={settings.CHUNK_OVERLAP}")
    
    if len(chunks) > 0:
        first_chunk = chunks[0]
        print(f"\n   Premier chunk:")
        print(f"   - Text length: {len(first_chunk.get('text', ''))} chars")
        print(f"   - Content: {repr(first_chunk.get('text', '')[:150])}")
        print(f"   - Metadata: {first_chunk.get('metadata', {})}")
        
        # Vérifier si "Nora" est dans le premier chunk
        if "nora" in first_chunk.get('text', '').lower():
            print(f"   ✅ Le nom 'NORA' est présent dans le premier chunk!")
    
    # Afficher tous les chunks
    print(f"\n   Détails de tous les chunks:")
    for i, chunk in enumerate(chunks):
        chunk_text = chunk.get('text', '')
        print(f"   Chunk {i}: {len(chunk_text)} chars - {repr(chunk_text[:60])}")
    print()
    
except Exception as e:
    print(f"   ❌ ERREUR CHUNKING: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# =============================================================================
# 5. EMBEDDINGS - Générer les embeddings
# =============================================================================

print("5️⃣  EMBEDDINGS - Génération des vecteurs")
print("-" * 80)

try:
    embedding_manager = EmbeddingManager()
    chunks_with_embeddings = embedding_manager.encode_chunks(
        chunks,
        batch_size=settings.BATCH_SIZE
    )
    
    print(f"   ✓ Embeddings générés: {len(chunks_with_embeddings)}")
    print(f"   ✓ Dimension: {settings.EMBEDDING_DIMENSION}")
    
    if len(chunks_with_embeddings) > 0:
        first_embedding = chunks_with_embeddings[0]
        print(f"\n   Premier embedding:")
        print(f"   - Keys: {list(first_embedding.keys())}")
        print(f"   - Text length: {len(first_embedding.get('text', ''))} chars")
        
        if 'embedding' in first_embedding:
            emb = first_embedding['embedding']
            print(f"   - Embedding shape: {len(emb)}")
            print(f"   - Embedding (first 5): {emb[:5]}")
    print()
    
except Exception as e:
    print(f"   ❌ ERREUR EMBEDDINGS: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# =============================================================================
# 6. FAISS VECTOR STORE - Ajouter au store et vérifier
# =============================================================================

print("6️⃣  FAISS VECTOR STORE - Indexation des vecteurs")
print("-" * 80)

try:
    vectorstore = FAISSStore(
        embedding_dim=settings.EMBEDDING_DIMENSION
    )
    
    # Ajouter les chunks
    vectorstore.add_chunks(chunks_with_embeddings)
    stats = vectorstore.get_stats()
    
    print(f"   ✓ Chunks ajoutés au FAISS")
    print(f"   ✓ Nombre de vecteurs: {stats['nb_vectors']}")
    print(f"   ✓ Nombre de chunks: {stats['nb_chunks']}")
    print(f"   ✓ Dimension: {stats['embedding_dim']}")
    
    # Sauvegarder l'index
    vectorstore.save_index()
    print(f"   ✓ Index sauvegardé: {vectorstore.index_path}")
    print()
    
except Exception as e:
    print(f"   ❌ ERREUR FAISS: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# =============================================================================
# 7. RETRIEVAL - Tester la recherche
# =============================================================================

print("7️⃣  RETRIEVAL - Recherche dans l'index FAISS")
print("-" * 80)

try:
    # Charger l'index de nouveau pour simuler un nouveau démarrage
    vectorstore_loaded = FAISSStore(
        embedding_dim=settings.EMBEDDING_DIMENSION
    )
    vectorstore_loaded.load_index()
    stats = vectorstore_loaded.get_stats()
    
    print(f"   ✓ Index chargé depuis le disque")
    print(f"   ✓ Nombre de vecteurs dans l'index: {stats['nb_vectors']}")
    print()
    
    # Tester la recherche avec la question de l'utilisateur
    query = "Est-ce que ce CV appartient à Nora ?"
    
    print(f"   Question: '{query}'")
    print()
    
    # Générer l'embedding de la requête
    query_embedding = embedding_manager.encode_text(query)
    print(f"   ✓ Embedding de la requête généré ({len(query_embedding)} dims)")
    print(f"   ✓ Embedding (first 5): {query_embedding[:5]}")
    print()
    
    # Rechercher dans l'index SANS filtrage de seuil
    all_results = vectorstore_loaded.search(query_embedding, top_k=20)
    
    print(f"   ✓ Résultats trouvés: {len(all_results)}")
    print()
    
    if len(all_results) == 0:
        print("   ❌ AUCUN résultat trouvé dans l'index!")
    else:
        print(f"   Résultats (les 20 premiers):")
        for i, result in enumerate(all_results):
            similarity = result.get('similarity_score', 0)
            chunk_text = result.get('chunk', {}).get('text', '')[:100]
            
            # Colorer les résultats selon le seuil
            if similarity >= settings.SIMILARITY_THRESHOLD:
                status = "✅ PASS"  # Au-dessus du seuil
            else:
                status = "❌ FAIL"  # En-dessous du seuil
            
            print(f"   [{i+1}] {status} Score: {similarity:.4f} | {repr(chunk_text)}")
        
        print()
        
        # Vérifier le filtrage par seuil
        above_threshold = [r for r in all_results if r['similarity_score'] >= settings.SIMILARITY_THRESHOLD]
        print(f"   📊 Statistiques:")
        print(f"   - Résultats totaux: {len(all_results)}")
        print(f"   - Résultats au-dessus du seuil ({settings.SIMILARITY_THRESHOLD}): {len(above_threshold)}")
        print(f"   - Score MIN: {min(r['similarity_score'] for r in all_results):.4f}")
        print(f"   - Score MAX: {max(r['similarity_score'] for r in all_results):.4f}")
        print()
        
        if len(above_threshold) == 0:
            print(f"   ⚠️  PROBLÈME IDENTIFIÉ: Aucun résultat au-dessus du seuil {settings.SIMILARITY_THRESHOLD}!")
            print(f"   💡 Solution: Réduire SIMILARITY_THRESHOLD")
        else:
            print(f"   ✅ {len(above_threshold)} résultats retournés au LLM")
    
    print()
    
except Exception as e:
    print(f"   ❌ ERREUR RETRIEVAL: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# =============================================================================
# 8. PROMPT & LLM - Vérifier la génération du prompt
# =============================================================================

print("8️⃣  PROMPT FORMATTING & LLM")
print("-" * 80)

try:
    from app.prompts import format_context, get_retrieval_qa_prompt
    
    # Formater le contexte avec les résultats au-dessus du seuil
    context = format_context(above_threshold)
    
    print(f"   ✓ Contexte formaté: {len(context)} caractères")
    print()
    print(f"   Contexte:")
    print(f"   {repr(context[:200])}")
    print()
    
    # Créer le prompt
    prompt = get_retrieval_qa_prompt(context, query)
    
    print(f"   ✓ Prompt créé: {len(prompt)} caractères")
    print()
    print(f"   Prompt:")
    print("-" * 80)
    print(prompt[:500])  # Afficher les 500 premiers caractères
    print("-" * 80)
    print()
    
    if len(above_threshold) == 0:
        print("   ❌ Contexte vide -> LLM retournera 'pas d'informations pertinentes'")
    else:
        print("   ✅ Contexte non vide -> LLM peut générer une réponse")
    
except Exception as e:
    print(f"   ❌ ERREUR PROMPT: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# =============================================================================
# RÉSUMÉ
# =============================================================================

print("\n" + "=" * 80)
print("RÉSUMÉ DU DIAGNOSTIC".center(80))
print("=" * 80 + "\n")

print("✅ ÉTAPES RÉUSSIES:")
print("   1. PDF Loading - OK")
print("   2. Text Extraction - OK")
print("   3. Chunking - OK")
print("   4. Embeddings - OK")
print("   5. FAISS - OK")
print("   6. Retrieval - OK (résultats trouvés)")
print()

if len(above_threshold) == 0:
    print("❌ PROBLÈME IDENTIFIÉ:")
    print(f"   Le seuil de similarité ({settings.SIMILARITY_THRESHOLD}) est trop élevé!")
    print(f"   Aucun résultat n'atteint ce seuil.")
    print(f"   Score MAX trouvé: {max(r['similarity_score'] for r in all_results):.4f}")
    print()
    print("💡 SOLUTION:")
    print(f"   Réduire SIMILARITY_THRESHOLD de {settings.SIMILARITY_THRESHOLD} à 0.1-0.2")
    print(f"   Ou mettre à 0.0 pour désactiver le filtrage")
else:
    print("✅ PIPELINE FONCTIONNEL:")
    print(f"   {len(above_threshold)} résultats seront envoyés au LLM")

print("\n" + "=" * 80 + "\n")
