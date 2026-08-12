"""
Test complet du pipeline RAG de bout en bout.

Vérifie:
PDF → extraction → chunking → embeddings → FAISS → retrieval
→ context → prompt → Hugging Face LLM → answer

Usage:
    python test_full_pipeline.py
"""

import sys
import io
from pathlib import Path
import logging

# Ajouter le répertoire racine au chemin
project_root = Path(__file__).parent.resolve()
sys.path.insert(0, str(project_root))

# Configuration logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(name)s | %(levelname)s | %(message)s"
)
logger = logging.getLogger(__name__)

from app.config import settings
from app.rag_pipeline import RAGPipeline

print("=" * 70)
print("TEST COMPLET DU PIPELINE RAG")
print("=" * 70)
print(f"LLM_MODEL: {settings.LLM_MODEL}")
print(f"Endpoint: {settings.HUGGINGFACE_INFERENCE_URL}")
print(f"Clé API: {'OUI' if settings.HUGGINGFACE_API_KEY else 'NON'}")
print()

# =============================================================================
# 1. CRÉER UN PDF DE TEST (sans reportlab, PDF minimal valide)
# =============================================================================
print("1️⃣  CRÉATION PDF DE TEST")
print("-" * 70)

def create_minimal_pdf(text: str) -> bytes:
    """Créer un PDF minimal valide avec du texte (lisible par pypdf)."""
    # Échapper les caractères spéciaux pour le flux PDF
    escaped = text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
    
    # Construire un PDF minimal avec une page contenant le texte
    content = f"""%PDF-1.4
1 0 obj
<< /Type /Catalog /Pages 2 0 R >>
endobj
2 0 obj
<< /Type /Pages /Kids [3 0 R] /Count 1 >>
endobj
3 0 obj
<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792]
   /Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >>
endobj
4 0 obj
<< /Length {len(escaped) + 50} >>
stream
BT /F1 12 Tf 50 700 Td 14 TL
({escaped}) Tj
ET
endstream
endobj
5 0 obj
<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>
endobj
xref
0 6
0000000000 65535 f 
0000000009 00000 n 
0000000058 00000 n 
0000000115 00000 n 
0000000242 00000 n 
0000000341 00000 n 
trailer
<< /Size 6 /Root 1 0 R >>
startxref
400
%%EOF
"""
    return content.encode("latin-1", errors="replace")

# Contenu du CV de test
cv_content = """CV DE NORA EL-FETTOUCHI

Nora EL-FETTOUCHI est une professionnelle experimentee dans le domaine de l'intelligence artificielle et du traitement des donnees.

Son nom complet est Nora EL-FETTOUCHI.

Experience professionnelle:
- Developpeuse IA chez TechCorp (2020-2023)
- Ingenieure Donnees chez DataFlow (2018-2020)

Formations:
- Master IA - Universite X (2018)
- Licence Informatique - Universite Y (2016)

Competences:
- Machine Learning
- Deep Learning
- NLP
- Python, TensorFlow, PyTorch"""

test_pdf_path = project_root / "test_pipeline_cv.pdf"
pdf_bytes = create_minimal_pdf(cv_content)
with open(test_pdf_path, "wb") as f:
    f.write(pdf_bytes)

print(f"   ✓ PDF créé: {test_pdf_path} ({len(pdf_bytes)} bytes)")
print()

# =============================================================================
# 2. INITIALISER LE PIPELINE
# =============================================================================
print("2️⃣  INITIALISATION DU PIPELINE")
print("-" * 70)
pipeline = RAGPipeline(reload_index=True)
print("   ✓ Pipeline initialisé")
print()

# =============================================================================
# 3. INGESTION (extraction → chunking → embeddings → FAISS)
# =============================================================================
print("3️⃣  INGESTION DU PDF")
print("-" * 70)
ingest_stats = pipeline.ingest_pdf(test_pdf_path)
print(f"   ✓ Texte extrait: {ingest_stats['text_length']} caractères")
print(f"   ✓ Chunks: {ingest_stats['num_chunks']}")
print(f"   ✓ Pages: {ingest_stats['metadata'].get('pages', '?')}")
print(f"   ✓ Vecteurs FAISS: {ingest_stats['vectorstore_stats']['nb_vectors']}")
print()

# =============================================================================
# 4. RETRIEVAL (retrieval → context → prompt)
# =============================================================================
print("4️⃣  RETRIEVAL")
print("-" * 70)
query = "Quel est le nom complet de la personne dans le CV ?"
retrieved = pipeline.retrieve(query, top_k=settings.TOP_K)
print(f"   ✓ Chunks récupérés: {len(retrieved)}")
for i, r in enumerate(retrieved, 1):
    print(f"   [{i}] Score: {r['similarity_score']:.4f} | {r['chunk']['text'][:60]!r}")
print()

if not retrieved:
    print("   ❌ Aucun chunk récupéré (seuil trop élevé?)")
    sys.exit(1)

# =============================================================================
# 5. GÉNÉRATION (prompt → Hugging Face → answer)
# =============================================================================
print("5️⃣  GÉNÉRATION DE LA RÉPONSE (Hugging Face)")
print("-" * 70)
print("   Appel à l'API Hugging Face...")
answer, chunks, citations = pipeline.answer_question(query, top_k=settings.TOP_K)
print(f"   ✓ Réponse générée ({len(answer)} caractères):")
print()
print(f"   💬 {answer}")
print()

# =============================================================================
# 6. CITATIONS
# =============================================================================
print("6️⃣  CITATIONS")
print("-" * 70)
if citations:
    for c in citations:
        print(f"   📚 {c}")
else:
    print("   (aucune citation)")
print()

# =============================================================================
# RÉSUMÉ
# =============================================================================
print("=" * 70)
print("RÉSUMÉ DU TEST COMPLET")
print("=" * 70)
print("✅ PDF → extraction → chunking → embeddings → FAISS → retrieval")
print("✅ context → prompt → Hugging Face LLM → answer")
print(f"✅ Réponse: {answer[:100]!r}")
print("=" * 70)