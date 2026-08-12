"""
Test de l'isolation des documents dans le RAG.

Scénario critique (TEST 1-5) :
1. Upload Nora's CV -> question sur l'université -> réponse: ENSAO
2. Upload PDF entreprise (AtlasData Solutions) APRÈS le CV
3. Question: nom de l'entreprise -> réponse: AtlasData Solutions
4. Question: siège social -> réponse: Casablanca, Morocco
5. Question: nombre d'employés -> réponse: 85
6. Question: "Qui est Nora El-Fettouchi?" -> NE DOIT PAS répondre avec l'ancien CV

Ce test vérifie la couche retrieval/FAISS directement, car la racine
du bug est l'isolation des données dans le vector store.

Usage:
    python test_document_isolation.py
"""

import sys
import logging
from pathlib import Path

project_root = Path(__file__).parent.resolve()
sys.path.insert(0, str(project_root))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(name)s | %(levelname)s | %(message)s"
)
logger = logging.getLogger(__name__)

from app.config import settings
from app.rag_pipeline import RAGPipeline

print("=" * 70)
print("TEST D'ISOLATION DES DOCUMENTS (RAG)")
print("=" * 70)


def create_minimal_pdf(text: str) -> bytes:
    """Créer un PDF minimal valide avec du texte (lisible par pypdf)."""
    escaped = text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
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


# =============================================================================
# 1. CRÉATION DES PDFS DE TEST
# =============================================================================
print("1. CRÉATION DES PDFS DE TEST")

cv_content = """CV DE NORA EL-FETTOUCHI

Nora EL-FETTOUCHI est une professionnelle experimentee dans le domaine de l'intelligence artificielle.

FORMATION:
- Ecole Nationale des Sciences Appliquees d'Oujda (ENSAO), 2022-2027
- Cycle Ingenieur en Data Science et Cloud Computing

EXPERIENCE:
- Data Engineer chez AKKAN Crowdfunding (2026)
- Stage RAG chez Tesnim Web (2026)"""

enterprise_content = """ATLASDATA SOLUTIONS - DOCUMENTATION ENTREPRISE

AtlasData Solutions est une entreprise specialisee dans la transformation digitale et les solutions de donnees.

Le nom de l'entreprise est AtlasData Solutions.

SIEGE SOCIAL:
- Lieu: Casablanca, Morocco
- Adresse: 45 Boulevard d'Anfa, Casablanca 20000

INFORMATIONS GENERALES:
- Nombre d'employes: 85 employes
- Annee de fondation: 2015"""

cv_path = project_root / "test_nora_cv.pdf"
enterprise_path = project_root / "test_atlasdata_enterprise.pdf"

with open(cv_path, "wb") as f:
    f.write(create_minimal_pdf(cv_content))
print(f"   OK: PDF CV créé: {cv_path.name}")

with open(enterprise_path, "wb") as f:
    f.write(create_minimal_pdf(enterprise_content))
print(f"   OK: PDF entreprise créé: {enterprise_path.name}")
print()

# =============================================================================
# 2. INITIALISATION
# =============================================================================
print("2. INITIALISATION DU PIPELINE")
pipeline = RAGPipeline(reload_index=True)
print("   OK: Pipeline initialisé")
print()

# Variables des résultats
results = {}


def check(name: str, condition: bool, message: str = "") -> None:
    """Ajouter un résultat de test."""
    status = "PASS" if condition else "FAIL"
    print(f"   [{status}] {name}" + (f" - {message}" if message else ""))
    results[name] = condition


# =============================================================================
# 3. TEST 1: INGESTION DU CV
# =============================================================================
print("3. TEST 1: INGESTION CV DE NORA")
pipeline.vectorstore.clear_persistent()
ingest_cv = pipeline.ingest_pdf(cv_path)
sources_cv = pipeline.vectorstore.get_document_sources()
check("CV ingéré", "test_nora_cv.pdf" in sources_cv, f"sources={sources_cv}")
print()

# =============================================================================
# 4. TEST 1: QUESTION UNIVERSITÉ
# =============================================================================
print("4. TEST 1: Quelle est l'université de Nora?")
retrieved = pipeline.retrieve("Quelle est l'universite de Nora ?", top_k=settings.TOP_K)
found_ensao = any(
    "ENSAO" in r["chunk"]["text"] or "Ecole Nationale" in r["chunk"]["text"]
    for r in retrieved
)
all_from_cv = all(
    r["chunk"]["metadata"].get("source_filename") == "test_nora_cv.pdf"
    for r in retrieved
) if retrieved else False
check("T1: ENSAO trouvé", found_ensao)
check("T1: Tous les chunks du CV", all_from_cv)
print()

# =============================================================================
# 5. TEST 2: INGESTION PDF ENTREPRISE APRÈS LE CV (CRITIQUE)
# =============================================================================
print("5. TEST 2: INGESTION PDF ENTREPRISE APRÈS LE CV")
print("   IMPORTANT: Doit réinitialiser l'index et supprimer les chunks du CV")
ingest_ent = pipeline.ingest_pdf(enterprise_path)
sources_ent = pipeline.vectorstore.get_document_sources()
check(
    "T2: CV supprimé de l'index",
    "test_nora_cv.pdf" not in sources_ent,
    f"sources={sources_ent}"
)
check(
    "T2: PDF entreprise indexé",
    "test_atlasdata_enterprise.pdf" in sources_ent,
    f"sources={sources_ent}"
)
check("T2: Un seul document dans l'index", len(sources_ent) == 1)
print()

# =============================================================================
# 6. TEST 2: QUESTION NOM ENTREPRISE
# =============================================================================
print("6. TEST 2: Quel est le nom de l'entreprise ?")
retrieved = pipeline.retrieve("Quel est le nom de l'entreprise ?", top_k=settings.TOP_K)
cv_chunks = [
    r for r in retrieved
    if r["chunk"]["metadata"].get("source_filename") == "test_nora_cv.pdf"
]
found_company = any(
    "AtlasData" in r["chunk"]["text"]
    for r in retrieved
)
check("T2: 'AtlasData Solutions' trouvé", found_company)
check("T2: Aucun chunk du CV récupéré", len(cv_chunks) == 0, f"{len(cv_chunks)} chunks CV")
print()

# =============================================================================
# 7. TEST 3: QUESTION SIÈGE SOCIAL
# =============================================================================
print("7. TEST 3: Où est le siège social ?")
retrieved = pipeline.retrieve("Ou est le siege social de l'entreprise ?", top_k=settings.TOP_K)
found_hq = any("Casablanca" in r["chunk"]["text"] for r in retrieved)
cv_chunks = [
    r for r in retrieved
    if r["chunk"]["metadata"].get("source_filename") == "test_nora_cv.pdf"
]
check("T3: 'Casablanca' trouvé", found_hq)
check("T3: Aucun chunk du CV récupéré", len(cv_chunks) == 0)
print()

# =============================================================================
# 8. TEST 4: QUESTION NOMBRE D'EMPLOYÉS
# =============================================================================
print("8. TEST 4: Combien d'employés ?")
retrieved = pipeline.retrieve("Combien d'employes compte l'entreprise ?", top_k=settings.TOP_K)
found_emp = any("85" in r["chunk"]["text"] for r in retrieved)
cv_chunks = [
    r for r in retrieved
    if r["chunk"]["metadata"].get("source_filename") == "test_nora_cv.pdf"
]
check("T4: '85' employés trouvé", found_emp)
check("T4: Aucun chunk du CV récupéré", len(cv_chunks) == 0)
print()

# =============================================================================
# 9. TEST 5: QUESTION SUR NORA (doit échouer à trouver le CV)
# =============================================================================
print("9. TEST 5: Qui est Nora El-Fettouchi ?")
retrieved = pipeline.retrieve("Qui est Nora El-Fettouchi ?", top_k=settings.TOP_K)
cv_chunks = [
    r for r in retrieved
    if r["chunk"]["metadata"].get("source_filename") == "test_nora_cv.pdf"
]
nora_text_found = any(
    "Nora" in r["chunk"]["text"] or "EL-FETTOUCHI" in r["chunk"]["text"]
    for r in retrieved
)
check("T5: Aucun chunk du CV récupéré", len(cv_chunks) == 0)
check("T5: Aucun texte 'Nora' retrouvé", not nora_text_found)
print()

# =============================================================================
# 10. VÉRIFICATION MÉTADONNÉES
# =============================================================================
print("10. VÉRIFICATION METADONNÉES (source_filename, page_num)")
all_meta_ok = True
for chunk in pipeline.vectorstore.chunks:
    meta = chunk.get("metadata", {})
    if not meta.get("source_filename"):
        print(f"   FAIL: Chunk {chunk.get('id')}: source_filename manquant!")
        all_meta_ok = False
    if meta.get("page_num") is None:
        print(f"   FAIL: Chunk {chunk.get('id')}: page_num manquant!")
        all_meta_ok = False
check("Métadonnées OK", all_meta_ok)
print()

# =============================================================================
# RÉSUMÉ
# =============================================================================
final_sources = pipeline.vectorstore.get_document_sources()
print("=" * 70)
print("RÉSUMÉ FINAL")
print(f"   Documents dans l'index: {final_sources}")
print(f"   Vecteurs FAISS: {pipeline.vectorstore.get_stats()['nb_vectors']}")
print(f"   Chunks: {pipeline.vectorstore.get_stats()['nb_chunks']}")
print()

passed = sum(1 for v in results.values() if v)
total = len(results)
print(f"   Résultats: {passed}/{total} tests PASS")
print()

if all(results.values()):
    print("🎉 TOUS LES TESTS D'ISOLATION SONT PASSÉS")
    print("=" * 70)
else:
    print("❌ CERTAINS TESTS ONT ÉCHOUÉ")
    for name, ok in results.items():
        if not ok:
            print(f"   - {name}")
    print("=" * 70)
    sys.exit(1)