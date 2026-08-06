# 📄 RAG Documentaire d'Entreprise - MVP

Système **Retrieval-Augmented Generation (RAG)** permettant de poser des questions en langage naturel sur des documents PDF et recevoir des réponses précises avec **citations des sources**.

## 🎯 Objectif

Créer un MVP permettant :
- ✅ Upload et traitement de PDFs
- ✅ Questions en langage naturel
- ✅ Réponses basées **uniquement** sur les documents
- ✅ Citations des sources utilisées
- ✅ Interface intuitive Streamlit
- ✅ Zéro coût API (tout local)

## 🛠 Stack Technique

| Composant | Technologie | Raison |
|-----------|-------------|--------|
| **Langage** | Python 3.12 | Performance, écosystème ML riche |
| **Interface** | Streamlit | Rapide à développer, déploiement facile |
| **Orchestration RAG** | LangChain | Standard industrie, bien documenté |
| **Embeddings** | Sentence Transformers (HuggingFace) | Gratuit, local, haute qualité |
| **Vector Store** | FAISS (Facebook AI) | Ultra-rapide, légèrement, persiste sur disque |
| **PDF Processing** | PyPDF | Léger, fiable |
| **LLM** | Ollama (local) | Pas d'API externe, confidentialité |
| **Configuration** | Pydantic | Validation types, gestion variables |

## 📋 Architecture Globale

```
┌─────────────────────────────────────────────────────────────┐
│                     Interface Streamlit                      │
│                    (app/main.py)                             │
└──────────────────┬──────────────────────────────────────────┘
                   │
┌──────────────────v──────────────────────────────────────────┐
│              Pipeline RAG (app/rag_pipeline.py)             │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  INGEST: PDF → Chunking → Embeddings → FAISS Index   │   │
│  │  QUERY:  Question → Embeddings → Search → LLM → Répo │   │
│  └──────────────────────────────────────────────────────┘   │
└──────────────────┬──────────────────────────────────────────┘
                   │
        ┌──────────┼──────────┬─────────────┬───────────┐
        │          │          │             │           │
   ┌────v─┐   ┌───v───┐  ┌──v──┐   ┌──────v──┐   ┌───v────┐
   │ PDF  │   │Chunking│  │Embed│   │FAISS    │   │Citations│
   │Loader│   │        │  │ding │   │Store    │   │Handler  │
   └──────┘   └────────┘  └─────┘   └─────────┘   └─────────┘
```

## 📦 Installation

### Prérequis
- **Python 3.12+** (testé sur Python 3.12)
- **pip** (gestionnaire de paquets)
- **Ollama** (optionnel, pour LLM local)

### Étapes d'installation

```bash
# 1. Cloner ou accéder au dossier du projet
cd rag-enterprise-mvp

# 2. Créer un environnement virtuel
python -m venv venv

# Activer l'environnement
# Sur Linux/Mac:
source venv/bin/activate
# Sur Windows:
venv\Scripts\activate

# 3. Mettre à jour pip
pip install --upgrade pip

# 4. Installer les dépendances
pip install -r requirements.txt

# 5. Copier le fichier de configuration
cp .env.example .env
# Optionnel : éditer .env pour personnaliser

# 6. Créer les dossiers de données (si ce n'est pas déjà fait)
mkdir -p data/uploads data/processed vectorstore/index

# 7. Installer et lancer Ollama (optionnel pour LLM local)
# Télécharger depuis https://ollama.ai
# ollama pull mistral
# ollama serve
```

### Vérifier l'installation

```bash
# Tester les imports
python -c "from app.config import settings; print(settings)"

# Vérifier les dossiers
ls -la data/ vectorstore/

# Lancer les tests
pytest tests/ -v
```

## 🚀 Utilisation

### Démarrer l'application

```bash
# Assurez-vous que l'environnement virtuel est activé
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows

# Lancer Streamlit
streamlit run app/main.py

# L'application s'ouvre sur http://localhost:8501
```

### Workflow utilisateur

1. **Ouvrir l'interface** → http://localhost:8501
2. **Upload un PDF** → Via le formulaire en sidebar
3. **Attendre le traitement** → ~30 secondes par PDF (dépend de la taille)
4. **Poser une question** → Exemple: "Quel est le résumé du document?"
5. **Voir la réponse** → Avec citations automatiques

## 📁 Structure du Projet

```
rag-enterprise-mvp/
├── README.md                      # Ce fichier
├── requirements.txt               # Dépendances Python
├── .env.example                   # Variables d'env (template)
├── .env                           # Variables d'env locales (à créer)
│
├── app/                           # Code principal
│   ├── __init__.py               # Package RAG
│   ├── main.py                   # Interface Streamlit 🎨
│   ├── config.py                 # Configuration centralisée ⚙️
│   ├── rag_pipeline.py           # Orchestration RAG 🔄
│   └── prompts.py                # Templates de prompts 📝
│
├── utils/                         # Utilitaires réutilisables
│   ├── __init__.py
│   ├── pdf_loader.py             # Chargement PDF 📄
│   ├── chunking.py               # Segmentation texte ✂️
│   ├── embeddings.py             # Gestion embeddings 🔢
│   └── citation_handler.py       # Gestion citations 📌
│
├── vectorstore/                   # Vector store FAISS
│   ├── __init__.py
│   ├── faiss_store.py            # Implémentation FAISS 🗂️
│   └── index/                    # Dossier index FAISS
│       ├── index.faiss           # Index sérialisé
│       └── chunks.json           # Métadonnées chunks
│
├── data/                          # Données
│   ├── uploads/                  # PDFs uploadés
│   └── processed/                # Données traitées
│
└── tests/                         # Tests unitaires
    ├── __init__.py
    ├── test_pdf_loader.py        # Tests PDF loader ✓
    ├── test_chunking.py          # Tests chunking ✓
    └── test_rag_pipeline.py      # Tests pipeline ✓
```

## ⚙️ Configuration

Tous les paramètres sont gérés via `app/config.py` et le fichier `.env`.

### Variables d'environnement clés

```bash
# Embeddings
EMBEDDING_MODEL=all-MiniLM-L6-v2          # Modèle HuggingFace
EMBEDDING_DIMENSION=384                    # Dimension vecteurs

# Chunking (segmentation du texte)
CHUNK_SIZE=512                              # Taille des chunks
CHUNK_OVERLAP=50                            # Chevauchement

# Retrieval (recherche)
TOP_K=5                                     # Chunks à récupérer
SIMILARITY_THRESHOLD=0.3                    # Seuil pertinence

# LLM (Génération de réponses)
LLM_MODEL=mistral                           # Modèle Ollama
OLLAMA_BASE_URL=http://localhost:11434     # URL Ollama

# Paths
UPLOAD_DIR=data/uploads
PROCESSED_DIR=data/processed
VECTORSTORE_DIR=vectorstore/index

# Debug
DEBUG_MODE=False
LOG_LEVEL=INFO
```

## 🔄 Pipeline Complet (Étape par Étape)

### Phase 1 : Ingestion

```
1. Upload PDF
   ↓
2. PDFLoader.load()
   - Extrait texte de chaque page
   - Récupère métadonnées (titre, auteur, pages)
   ↓
3. TextChunker.chunk_text()
   - Découpe par paragraphes
   - Respecte CHUNK_SIZE
   - Ajoute chevauchement (CHUNK_OVERLAP)
   ↓
4. EmbeddingManager.encode_chunks()
   - Génère embedding pour chaque chunk
   - Utilise Sentence Transformers
   - Batch processing pour performance
   ↓
5. FAISSStore.add_chunks()
   - Ajoute embeddings à l'index FAISS
   - Sauvegarde chunks en JSON
   ↓
6. Sauvegarde index.faiss + chunks.json
```

### Phase 2 : Requête

```
1. Utilisateur pose une question
   ↓
2. EmbeddingManager.encode_text()
   - Génère embedding de la requête
   ↓
3. FAISSStore.search()
   - Recherche TOP_K vecteurs les plus proches
   - Retourne scores de similarité
   ↓
4. CitationHandler.add_source()
   - Collecte les sources utilisées
   ↓
5. RAGPipeline.generate_answer()
   - Formate le contexte
   - Crée le prompt avec chunks pertinents
   - Appelle Ollama pour générer réponse
   ↓
6. Interface Streamlit affiche
   - Réponse du LLM
   - Citations formatées
   - Scores de pertinence
```

## 🧪 Tests

### Lancer tous les tests

```bash
# Mode verbose
pytest tests/ -v

# Avec couverture de code
pytest tests/ --cov=app --cov=utils --cov=vectorstore --cov-report=html

# Test spécifique
pytest tests/test_pdf_loader.py -v
pytest tests/test_chunking.py::TestTextChunker::test_chunker_large_text -v
```

### Fichiers de test

| Fichier | Tests | Couverture |
|---------|-------|-----------|
| `test_pdf_loader.py` | Chargement PDF, erreurs | PDFLoader |
| `test_chunking.py` | Segmentation, chevauchement, metadata | TextChunker |
| `test_rag_pipeline.py` | Initialisation, retrieval, génération | RAGPipeline |

## 📊 Paramètres Recommandés

### Pour MVP (Qualité acceptable, Vitesse)
```
EMBEDDING_MODEL=all-MiniLM-L6-v2      # Léger (384 dims)
CHUNK_SIZE=512                        # Bon compromis
CHUNK_OVERLAP=50                      # Contexte continu
TOP_K=5                               # Retrieval basique
```

### Pour Production (Haute qualité)
```
EMBEDDING_MODEL=all-mpnet-base-v2     # Plus puissant (768 dims)
CHUNK_SIZE=1024                       # Plus de contexte
CHUNK_OVERLAP=100                     # Meilleur chevauchement
TOP_K=10                              # Plus de résultats
```

### Pour Budget Limité (Super léger)
```
EMBEDDING_MODEL=all-MiniLM-L6-v2
CHUNK_SIZE=256
CHUNK_OVERLAP=25
TOP_K=3
```

## ⚡ Performance

### Temps d'exécution typiques (CPU)

| Opération | Temps | Notes |
|-----------|-------|-------|
| Chargement PDF (10 pages) | ~2s | Avec PyPDF |
| Chunking | ~1s | Segmentation texte |
| Génération 50 embeddings | ~5s | Sentence Transformers |
| Recherche FAISS | ~10ms | Sur 1000 chunks |
| Génération réponse LLM | ~10-30s | Via Ollama |
| **TOTAL (Requête)** | **~15-50s** | Dépend de la taille |

### Optimisations possibles
- GPU pour embeddings : 10x plus rapide
- Batch processing : déjà implémenté
- Caching embeddings : v2
- Index FAISS optimisé : v2

## 🔍 Debugging

### Problème : Index vide / Pas de documents
```python
from app.rag_pipeline import RAGPipeline
pipeline = RAGPipeline()
stats = pipeline.get_vectorstore_stats()
print(stats)  # Vérifie nb_vectors
```

### Problème : Ollama ne répond pas
```bash
# Vérifier que Ollama est lancé
curl http://localhost:11434/api/tags

# Lancer Ollama
ollama serve

# Télécharger un modèle
ollama pull mistral
```

### Problème : Embeddings faibles
```python
# Tester la qualité des embeddings
from utils.embeddings import EmbeddingManager
manager = EmbeddingManager()
emb1 = manager.encode_text("Chat")
emb2 = manager.encode_text("Chien")
similarity = manager.similarity(emb1, emb2)
print(f"Similarité chat/chien: {similarity:.2f}")  # Devrait être ~0.3-0.4
```

### Activation du DEBUG_MODE

```bash
# Dans .env
DEBUG_MODE=True
LOG_LEVEL=DEBUG

# Logs plus détaillés
python -c "
from app.config import settings
settings.DEBUG_MODE = True
"
```

## 🚨 Erreurs Courantes

| Erreur | Cause | Solution |
|--------|-------|----------|
| `ModuleNotFoundError: langchain` | Dépendances non installées | `pip install -r requirements.txt` |
| `.env` not found | Config manquante | `cp .env.example .env` |
| `ConnectionError: Ollama` | Ollama pas lancé | `ollama serve` |
| `FAISS index too small` | Pas assez de chunks | Upload plus de PDFs |
| `CUDA out of memory` | GPU saturé | Réduire BATCH_SIZE ou utiliser CPU |

## 📈 Limitations du MVP

- ⏸️ Pas de support images dans PDFs
- ⏸️ Pas de multi-utilisateurs / authentification
- ⏸️ Pas de persistance base de données (sauf index FAISS)
- ⏸️ Pas de caching avancé des embeddings
- ⏸️ Pas de monitoring/alertes
- ⏸️ Pas de versioning des documents

## 🔄 Feuille de Route (Post-MVP)

### V1.1
- [ ] Multi-documents simultanés
- [ ] Export réponse (PDF, Markdown)
- [ ] Historique conversations

### V2
- [ ] Base de données persistante (PostgreSQL)
- [ ] Cache embeddings
- [ ] API REST (FastAPI)
- [ ] Support images OCR
- [ ] Multi-langues

### V3
- [ ] Dashboard d'administration
- [ ] Analytics utilisateur
- [ ] Fine-tuning modèles
- [ ] Déploiement cloud (AWS/Azure)

### V4
- [ ] Authentification multi-utilisateurs
- [ ] Collaboration temps réel
- [ ] Webhooks et intégrations

## 📚 Ressources

### Documentation Officielle
- [LangChain Python](https://python.langchain.com/)
- [FAISS Documentation](https://faiss.ai/)
- [Streamlit Docs](https://docs.streamlit.io/)
- [Sentence Transformers](https://www.sbert.net/)
- [HuggingFace Models](https://huggingface.co/models)

### Articles Utiles
- [RAG Concepts](https://docs.llamaindex.ai/en/stable/module_guides/indexing/retrieval_augmented_generation/)
- [FAISS Indexing](https://github.com/facebookresearch/faiss/wiki)
- [Embeddings Explainés](https://huggingface.co/blog/getting-the-best-of-simcse)

### Modèles Recommandés

#### Embeddings
- `all-MiniLM-L6-v2` : Léger (384 dims, ~30MB)
- `all-mpnet-base-v2` : Puissant (768 dims, ~430MB)
- `multilingual-e5-large` : Multi-langues (1024 dims)

#### LLMs (Ollama)
- `mistral` : Très rapide, 7B params
- `neural-chat` : Spécialisé conversation
- `orca-mini` : Léger mais basique

## 🤝 Contribution

Pour contribuer :
1. Fork le projet
2. Créer une branche (`git checkout -b feature/AmazingFeature`)
3. Commit les changements (`git commit -m 'Add AmazingFeature'`)
4. Push la branche (`git push origin feature/AmazingFeature`)
5. Ouvrir une Pull Request

## 📝 License

MIT License - Libre d'utilisation

## 👨‍💻 Support

Pour les questions ou problèmes :
1. Consulter la documentation
2. Vérifier les issues existantes
3. Ouvrir une nouvelle issue avec détails

---

**Version** : MVP 0.1  
**Python** : 3.12+  
**Dernière mise à jour** : 2026-08-05  
**Statut** : Production-ready pour MVP
#   r a g - e n t e r p r i s e - m v p  
 