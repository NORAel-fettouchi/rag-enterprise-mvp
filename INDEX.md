# 📑 INDEX COMPLET - Structure et Navigation

## 🗂️ Vue d'Ensemble du Projet

```
rag-enterprise-mvp/
├── 📄 Documentation
│   ├── README.md                    → Documentation générale
│   ├── QUICKSTART.md                → Guide 5 minutes pour démarrer
│   ├── PROJECT_SUMMARY.md           → Résumé final du projet (CE FICHIER)
│   ├── PROJECT_COMPLETION.md        → État complet d'implémentation
│   ├── PROJECT_PLAN.md              → Plan initial du projet
│   ├── INDEX.md                     → This file (navigation complète)
│
├── 🔧 Configuration
│   ├── requirements.txt              → Dépendances Python
│   ├── .env                         → Variables d'environnement (local)
│   ├── .env.example                 → Template de configuration
│
├── 📦 Application (app/)
│   ├── __init__.py                  → Package app
│   ├── config.py                    → 🎛️ Configuration centralisée
│   ├── main.py                      → 🎮 Interface Streamlit
│   ├── rag_pipeline.py              → 🔄 Orchestration RAG
│   └── prompts.py                   → 💬 Templates LLM
│
├── 🔧 Utilitaires (utils/)
│   ├── __init__.py                  → Package utils
│   ├── pdf_loader.py                → 📄 Chargement PDF
│   ├── chunking.py                  → ✂️ Segmentation texte
│   ├── embeddings.py                → 🧠 Gestion embeddings
│   └── citation_handler.py          → 📚 Gestion citations
│
├── 🗄️ Vector Store (vectorstore/)
│   ├── __init__.py                  → Package vectorstore
│   ├── faiss_store.py               → ⚡ Index FAISS
│   └── index/                       → 💾 Index persisté
│
├── 🧪 Tests (tests/)
│   ├── __init__.py                  → Package tests
│   ├── test_pdf_loader.py           → Tests PDF
│   ├── test_chunking.py             → Tests Chunking
│   └── test_rag_pipeline.py         → Tests Pipeline
│
├── 📁 Données (data/)
│   ├── uploads/                     → PDFs uploadés par utilisateurs
│   └── processed/                   → Données traitées
│
└── 🔍 Scripts de Validation
    └── validate_project.py          → Script de validation complète
```

---

## 📚 Guide de Lecture

### Pour Démarrer Rapidement ⚡
1. **[QUICKSTART.md](QUICKSTART.md)** - 5 minutes pour être opérationnel
2. **[.env.example](.env.example)** - Comprendre la configuration
3. **[app/main.py](app/main.py)** - Voir l'interface

### Pour Comprendre l'Architecture 🏗️
1. **[README.md](README.md)** - Vue d'ensemble générale
2. **[app/rag_pipeline.py](app/rag_pipeline.py)** - Pipeline complet
3. **[PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)** - Résumé détaillé

### Pour Développer ou Modifier 🛠️
1. **[app/config.py](app/config.py)** - Comment configure
2. **[utils/](utils/)** - Modules réutilisables
3. **[tests/](tests/)** - Comment tester
4. **[PROJECT_COMPLETION.md](PROJECT_COMPLETION.md)** - Liste complète

---

## 📖 Chaque Fichier Expliqué

### Configuration & Setup

#### `requirements.txt` 📦
**Rôle**: Définir toutes les dépendances Python  
**Contient**: 20+ packages (Streamlit, LangChain, FAISS, etc.)  
**À faire**: `pip install -r requirements.txt`  
**Taille**: ~39 lignes  

#### `.env.example` ⚙️
**Rôle**: Template de configuration  
**Contient**: Tous les paramètres configurables  
**À faire**: `cp .env.example .env` et éditer  
**Paramètres clés**: CHUNK_SIZE, EMBEDDING_MODEL, LLM_MODEL, etc.  

#### `.env` 🔐
**Rôle**: Configuration locale (pas en git)  
**Contient**: Variables d'environnement de développement  
**À faire**: Créer depuis `.env.example`  
**Secrets**: API keys, tokens, URLs  

---

### Application Principale (app/)

#### `app/__init__.py` 📦
**Rôle**: Marquer app/ comme package Python  
**Contient**: Vide ou imports utiles  
**Size**: Minimal  

#### `app/config.py` 🎛️ [150+ LOC]
**Rôle**: **Configuration centralisée de l'app**  
**Contient**:
- Classe `Settings` chargent depuis `.env`
- Chemins (uploads, vectorstore, etc.)
- Paramètres (chunk_size, embedding_dim, etc.)
- Logging configuration
- Création auto des dossiers

**Importer partout avec**: `from app.config import settings`  

**Paramètres principaux**:
```python
settings.CHUNK_SIZE           # 512
settings.EMBEDDING_MODEL      # all-MiniLM-L6-v2
settings.TOP_K               # 5
settings.LLM_MODEL           # mistral
settings.DEBUG_MODE          # False/True
```

#### `app/main.py` 🎮 [258 LOC]
**Rôle**: **Interface Streamlit - Point d'entrée utilisateur**  
**Contient**:
- Page configuration (title, icon, layout)
- CSS personnalisé (citations, réponses)
- Upload PDF widget
- Chat input
- Affichage réponse + citations
- Paramètres avancés
- Gestion erreurs

**Lancer**: `streamlit run app/main.py`  

**Sections UI**:
- Sidebar: Upload, stats, paramètres
- Main: Affichage réponses
- Expander: Détails retrieval

#### `app/rag_pipeline.py` 🔄 [305+ LOC]
**Rôle**: **Orchestration du pipeline RAG complet**  
**Contient**:
- Classe `RAGPipeline` - combine tous les modules
- `ingest_pdf()` - traiter un PDF complet
- `retrieve()` - chercher chunks pertinents
- `generate_answer()` - générer réponse LLM
- `answer_question()` - pipeline complet Q&A
- `_call_ollama()` - appel LLM

**Workflow implémenté**:
```
PDF → Loader → Chunker → Embeddings → FAISS
Query → Embedding → FAISS Search → Ollama → Response
```

**Classe principale**:
```python
pipeline = RAGPipeline()
stats = pipeline.ingest_pdf("document.pdf")
answer, chunks, citations = pipeline.answer_question("Question?")
```

#### `app/prompts.py` 💬 [105 LOC]
**Rôle**: **Templates pour prompts LLM**  
**Contient**:
- `SYSTEM_PROMPT` - Instructions système RAG
- `RETRIEVAL_QA_PROMPT` - Template Q&A
- `SUMMARIZE_PROMPT` - Résumé
- `EXTRACT_INFO_PROMPT` - Extraction info
- Fonction `format_context()` - formater chunks

**Utilisé par**: RAGPipeline pour générer les prompts  

---

### Utilitaires (utils/)

#### `utils/__init__.py` 📦
**Rôle**: Marquer utils/ comme package  
**Contient**: Vide  

#### `utils/pdf_loader.py` 📄 [141 LOC]
**Rôle**: **Extraire texte et métadonnées des PDFs**  
**Classe**: `PDFLoader`  
**Contient**:
- Chargement PDF avec PyPDF2
- Extraction page par page
- Métadonnées (titre, auteur, pages)
- Gestion erreurs
- Sauvegarde texte

**Utilisation**:
```python
from utils.pdf_loader import PDFLoader
loader = PDFLoader("document.pdf")
text = loader.load()
metadata = loader.get_metadata()  # {title, author, pages}
pages = loader.get_pages()  # [{page_num, text, file}]
```

**Erreurs gérées**:
- Fichier inexistant
- Pas un PDF
- Extraction échouée par page

#### `utils/chunking.py` ✂️ [187 LOC]
**Rôle**: **Découper texte en chunks intelligents**  
**Classe**: `TextChunker`  
**Contient**:
- Segmentation par paragraphes
- Chevauchement entre chunks
- Nettoyage texte
- Métadonnées par chunk
- Support multi-documents

**Paramétrés** (depuis config):
- `CHUNK_SIZE`: 512 caractères
- `CHUNK_OVERLAP`: 50 caractères

**Utilisation**:
```python
from utils.chunking import TextChunker
chunker = TextChunker()
chunks = chunker.chunk_text(text, metadata)
chunks = chunker.get_chunks()  # Liste avec id, text, metadata
```

**Stratégie**:
- Découpe intelligente par paragraphes
- Pas de coupure au milieu de mots
- Chevauchement pour contexte

#### `utils/embeddings.py` 🧠 [227 LOC]
**Rôle**: **Générer embeddings avec Sentence Transformers**  
**Classe**: `EmbeddingManager`  
**Contient**:
- Chargement modèle HuggingFace
- Encodage single text
- Encodage batch (optimisé GPU)
- Calcul similarité cosinus
- Gestion dimensions

**Modèle par défaut**: `all-MiniLM-L6-v2` (384 dims, rapide)  

**Utilisation**:
```python
from utils.embeddings import EmbeddingManager
em = EmbeddingManager()
embedding = em.encode_text("Hello world")  # Vecteur 384D
embeddings = em.encode_batch(texts, batch_size=32)  # Matrix
chunks_with_emb = em.encode_chunks(chunks)  # Chunks + embeddings
```

#### `utils/citation_handler.py` 📚 [171 LOC]
**Rôle**: **Gérer citations et tracer sources**  
**Classe**: `CitationHandler`  
**Contient**:
- Ajouter sources
- Formater citations
- Déduplication
- Top sources par score
- Génération bibliographie

**Utilisation**:
```python
from utils.citation_handler import CitationHandler
handler = CitationHandler()
handler.add_source(
    chunk_id=0,
    text="...",
    source_file="document.pdf",
    page_num=2,
    similarity_score=0.95
)
citations = handler.get_formatted_citations()
bibliography = handler.generate_bibliography()
```

---

### Vector Store (vectorstore/)

#### `vectorstore/__init__.py` 📦
**Rôle**: Marquer vectorstore/ comme package  

#### `vectorstore/faiss_store.py` ⚡ [276 LOC]
**Rôle**: **Gérer index FAISS - Recherche vectorielle rapide**  
**Classe**: `FAISSStore`  
**Contient**:
- Création index FAISS (IndexFlatL2)
- Ajout chunks avec embeddings
- Recherche par similarité
- Sauvegarde/chargement index
- Persistance sur disque
- Statistiques

**Utilisation**:
```python
from vectorstore.faiss_store import FAISSStore
store = FAISSStore(embedding_dim=384)
store.add_chunks(chunks_with_embeddings)
results = store.search(query_embedding, top_k=5)
store.save_index()  # Sauvegarde
```

**Fichiers persistés**:
- `vectorstore/index/index.faiss` - Index FAISS binaire
- `vectorstore/index/chunks.json` - Metadata et texte

---

### Tests (tests/)

#### `tests/__init__.py` 📦
**Rôle**: Marquer tests/ comme package  

#### `tests/test_pdf_loader.py` [43 LOC]
**Rôle**: **Tests unitaires pour PDFLoader**  
**Tests**:
- Fichier inexistant → erreur
- Fichier non-PDF → erreur
- PDF invalide → erreur sur load()

**Lancer**: `pytest tests/test_pdf_loader.py -v`  

#### `tests/test_chunking.py` [60 LOC]
**Rôle**: **Tests unitaires pour TextChunker**  
**Tests**:
- Initialisation
- Overlap invalide
- Texte vide
- Texte petit (1 chunk)
- Texte grand (multi-chunks)
- Métadonnées préservées

#### `tests/test_rag_pipeline.py` [47 LOC]
**Rôle**: **Tests unitaires pour RAGPipeline**  
**Tests**:
- Initialisation
- Statistiques vectorstore
- Retrieval sur index vide
- Answer question sur index vide

---

### Données (data/)

#### `data/uploads/` 📂
**Rôle**: Dossier pour PDFs uploadés  
**Créé automatiquement** par config.py  
**Contient**: Fichiers PDF d'utilisateurs  

#### `data/processed/` 📂
**Rôle**: Dossier pour données traitées  
**Créé automatiquement** par config.py  
**Usage**: Textes extraits, métadonnées, etc.  

---

### Documentation

#### `README.md` 📖
**Rôle**: Documentation générale complète  
**Sections**:
- Objectif du projet
- Stack technique
- Architecture générale
- Installation
- Utilisation
- Limitations MVP
- Roadmap

#### `QUICKSTART.md` ⚡
**Rôle**: Guide 5-10 minutes pour démarrer  
**Sections**:
- Installation rapide
- Configuration
- Vérification
- Démarrage app
- Utilisation
- Erreurs courantes
- Architecture simplifiée

#### `PROJECT_SUMMARY.md` 📊
**Rôle**: Résumé final complet  
**Contient**:
- État du projet
- Modules implémentés
- Architecture
- Workflow
- Metrics
- Validation

#### `PROJECT_COMPLETION.md` ✅
**Rôle**: État complète d'implémentation  
**Contient**:
- Checklist complète
- Composants détaillés
- Statistiques
- Configuration
- Stack validée
- Prochaines étapes

#### `PROJECT_PLAN.md` 📋
**Rôle**: Plan initial du projet  
**Contient**: Vue d'ensemble et objectifs  

---

## 🚀 Flux de Travail Par Use Case

### Pour Démarrer
```
1. Lire: QUICKSTART.md (5 min)
2. Faire: pip install -r requirements.txt (3 min)
3. Faire: streamlit run app/main.py (30 sec)
4. Utiliser: Upload PDF + poser question
```

### Pour Comprendre le Code
```
1. Lire: README.md (architecture générale)
2. Lire: app/config.py (paramètres)
3. Lire: app/rag_pipeline.py (flux)
4. Lire: utils/ (modules spécifiques)
```

### Pour Développer/Modifier
```
1. Lire: PROJECT_COMPLETION.md (liste complète)
2. Modifier: Le fichier approprié
3. Tester: pytest tests/ (ou manuellement)
4. Vérifier: python validate_project.py
```

### Pour Déboguer
```
1. Activer: DEBUG_MODE=True dans .env
2. Lancer: streamlit run app/main.py
3. Voir: Logs détaillés dans console
4. Vérifier: app/config.py pour les settings
```

---

## 📊 Statistiques Fichiers

| Dossier | Fichiers | LOC | Purpose |
|---------|----------|-----|---------|
| `app/` | 5 | ~920 | Application principale |
| `utils/` | 5 | ~730 | Modules réutilisables |
| `vectorstore/` | 2 | ~280 | Vector store |
| `tests/` | 4 | ~150 | Tests |
| `docs/` | 6 | - | Documentation |
| **Total** | **22** | **~2100+** | **MVP Complet** |

---

## 🎯 Points d'Entrée

### Pour Utilisateurs
→ **[app/main.py](app/main.py)** - Streamlit interface  

### Pour Développeurs
→ **[app/rag_pipeline.py](app/rag_pipeline.py)** - Core pipeline  

### Pour Configuration
→ **[app/config.py](app/config.py)** - Settings centralisé  

### Pour Modules Spécifiques
→ **[utils/](utils/)** - Tous les modules  

### Pour Installation
→ **[requirements.txt](requirements.txt)** - Dépendances  

### Pour Démarrage
→ **[QUICKSTART.md](QUICKSTART.md)** - 5 min start guide  

---

## 📡 Dépendances Entre Modules

```
main.py
    ↓
config.py ←─ .env
rag_pipeline.py ←─ config.py
    ├─→ pdf_loader.py
    ├─→ chunking.py
    ├─→ embeddings.py
    ├─→ faiss_store.py
    ├─→ citation_handler.py
    └─→ prompts.py
    
tests/
    ├─→ test_pdf_loader.py
    ├─→ test_chunking.py
    └─→ test_rag_pipeline.py
```

---

## ✅ Checklist Navigation

- [ ] Lu QUICKSTART.md
- [ ] Compris app/config.py
- [ ] Compris app/main.py (UI)
- [ ] Compris app/rag_pipeline.py (logic)
- [ ] Compris utils/ (modules)
- [ ] Compris vectorstore/faiss_store.py
- [ ] Vu les tests
- [ ] Lancé l'app avec `streamlit run app/main.py`
- [ ] Upload un PDF
- [ ] Posé une question
- [ ] Obtenu une réponse + citations ✨

---

**Navigation complète du projet RAG Documentaire d'Entreprise**

*Créé: 2026-08-06*  
*Version: 0.1*  
*Status: ✅ COMPLETE*
