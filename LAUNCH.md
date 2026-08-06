# 🚀 DÉMARRAGE - RAG-ENTERPRISE MVP

## ✅ STATUS: PRÊT À LANCER ✅

L'application est maintenant **entièrement fonctionnelle** et peut être lancée!

---

## 📋 COMMENT LANCER L'APPLICATION

### **Option 1: Double-clic (PLUS FACILE)**

1. Double-cliquez sur le fichier: **`run_app.bat`**
2. L'application démarrera automatiquement

### **Option 2: Ligne de commande**

```bash
# Dans PowerShell/CMD, à la racine du projet:
cd e:\rag-enterprise-mvp
C:\Users\pc\AppData\Local\Programs\Python\Python312\python.exe -m streamlit run streamlit_app.py
```

### **Option 3: Depuis VS Code Terminal**

```bash
streamlit run streamlit_app.py
```

---

## 🌐 ACCÉDER À L'APPLICATION

Une fois l'application lancée, vous verrez:

```
Local URL: http://localhost:8501
Network URL: http://192.168.0.208:8501
```

**Ouvrez dans votre navigateur:** http://localhost:8501

---

## ✨ FONCTIONNALITÉS DISPONIBLES

### **1. Upload PDF**
- Sidebar gauche: Zone de téléchargement
- Sélectionnez un PDF depuis votre ordinateur
- Cliquez "Process PDF"
- Le système:
  - Extrait le texte
  - Crée des chunks de 512 caractères
  - Génère des embeddings 384-D
  - Indexe dans FAISS

### **2. Questions & Réponses**
- Tapez une question dans la zone principale
- Le système:
  - Recherche les 5 chunks les plus pertinents
  - Utilise Ollama/LLM pour générer une réponse
  - Affiche les citations des sources

### **3. Visualisation**
- Affichage structuré des réponses
- Citations avec numéros de page
- Références aux fichiers sources

---

## 🔧 CONFIGURATION

Les paramètres se trouvent dans [.env](.env):

```ini
# Embedding
EMBEDDING_MODEL=all-MiniLM-L6-v2          # Modèle HuggingFace
CHUNK_SIZE=512                             # Taille chunks
CHUNK_OVERLAP=50                           # Chevauchement

# Recherche
TOP_K=5                                    # Nombre résultats

# LLM (génération réponses)
LLM_MODEL=mistral                         # Modèle local
OLLAMA_BASE_URL=http://localhost:11434   # URL Ollama

# Répertoires
UPLOAD_DIR=uploads
PROCESSED_DIR=data/processed
VECTORSTORE_DIR=vectorstore/index
```

---

## 🧪 TESTS

Pour vérifier que tout fonctionne:

```bash
# Test complet (37 tests)
C:\Users\pc\AppData\Local\Programs\Python\Python312\python.exe test_project.py

# Test imports uniquement
C:\Users\pc\AppData\Local\Programs\Python\Python312\python.exe test_imports.py
```

---

## 📦 COMPOSANTS

```
app/
├── config.py           ✅ Configuration globale
├── main.py            ✅ Interface Streamlit
├── rag_pipeline.py    ✅ Orchestration RAG
└── prompts.py         ✅ Templates LLM

utils/
├── pdf_loader.py      ✅ Extraction PDF
├── chunking.py        ✅ Segmentation texte
├── embeddings.py      ✅ Génération embeddings
└── citation_handler.py ✅ Gestion citations

vectorstore/
└── faiss_store.py     ✅ Index FAISS
```

**Statut:** ✅ TOUS LES COMPOSANTS OPÉRATIONNELS

---

## 🐛 DÉPANNAGE

### **Erreur: "ModuleNotFoundError: No module named 'app'"**
→ RÉSOLU ✅ (correction `.resolve()` dans streamlit_app.py)

### **Streamlit ne démarre pas**
→ Vérifiez les logs d'erreur complètement affichés

### **L'app démarre mais PDF ne s'upload pas**
→ Vérifiez que Ollama tourne (pour les réponses LLM)
→ Alternative: Vous pouvez utiliser une clé API OpenAI

### **Les embeddings prennent du temps au premier lancement**
→ Normal! Le modèle se télécharge (90MB) la première fois

---

## 📚 DOCUMENTATION

- **RAG Architecture:** Voir [PROJECT_PLAN.md](PROJECT_PLAN.md)
- **Configuration détaillée:** Voir [app/config.py](app/config.py)
- **Pipeline RAG:** Voir [app/rag_pipeline.py](app/rag_pipeline.py)

---

## 🎯 PROCHAINES ÉTAPES

1. ✅ Lancer l'app avec `run_app.bat` ou command line
2. 📤 Upload un PDF de test
3. ❓ Posez une question sur le contenu
4. 🔍 Explorez les réponses avec citations
5. ⚙️ Ajustez les paramètres si nécessaire

---

## 📞 SUPPORT

Si vous rencontrez des problèmes:
- Vérifiez que Python 3.12 est installé
- Vérifiez les dépendances: `pip install -r requirements.txt`
- Lancez les tests: `python test_project.py`
- Consultez les logs détaillés

---

**BON USAGE! 🎉**
