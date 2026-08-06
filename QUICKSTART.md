# 🚀 GUIDE DE DÉMARRAGE RAPIDE - RAG Documentaire d'Entreprise

## ⏱️ Temps Estimé: 5-10 minutes

---

## 📝 Étape 1: Préparation (2 min)

### 1.1 Vérifier Python 3.12
```bash
python --version
# Doit afficher: Python 3.12.x
```

### 1.2 Naviguer au dossier projet
```bash
cd e:\rag-enterprise-mvp
```

---

## 📦 Étape 2: Installation des Dépendances (3-5 min)

### 2.1 Créer un environnement virtuel (optionnel mais recommandé)
```bash
python -m venv venv
venv\Scripts\activate  # Sur Windows
# source venv/bin/activate  # Sur Mac/Linux
```

### 2.2 Installer les dépendances
```bash
pip install -r requirements.txt
```

**Patience**: Cette étape peut prendre 2-5 minutes car elle télécharge:
- Streamlit (interface web)
- LangChain (orchestration RAG)
- Sentence Transformers (embeddings)
- FAISS (vector store)
- Et bien d'autres...

---

## ⚙️ Étape 3: Configuration (1 min)

### 3.1 Créer le fichier .env
```bash
cp .env.example .env
```

### 3.2 (Optionnel) Éditer .env
Les paramètres par défaut sont déjà optimisés, mais vous pouvez les modifier:
```env
EMBEDDING_MODEL=all-MiniLM-L6-v2  # Modèle d'embeddings
CHUNK_SIZE=512                     # Taille des segments
TOP_K=5                            # Nombre de résultats
LLM_MODEL=mistral                 # Modèle LLM
DEBUG_MODE=False                  # Activer le debug
```

---

## 🧪 Étape 4: Vérification (2 min)

### 4.1 Tester la configuration
```bash
python -c "from app.config import settings; print(f'✅ Config OK: {settings.CHUNK_SIZE} chars par chunk')"
```

**Résultat attendu**:
```
✅ Config OK: 512 chars par chunk
```

### 4.2 Tester les imports
```bash
python -c "from app.rag_pipeline import RAGPipeline; print('✅ Pipeline importé')"
```

**Résultat attendu**:
```
✅ Pipeline importé
```

---

## 🎮 Étape 5: Lancer l'Application (1 min)

### 5.1 Démarrer Streamlit
```bash
streamlit run app/main.py
```

**Résultat attendu**:
- Une fenêtre du navigateur s'ouvre à `http://localhost:8501`
- L'interface RAG s'affiche avec:
  - Zone d'upload de PDFs
  - Champ de question
  - Affichage des réponses

### 5.2 Arrêter l'application
Appuyez sur `Ctrl+C` dans le terminal

---

## 📖 Étape 6: Utiliser l'Application (1-2 min)

### 6.1 Upload un PDF
1. Cliquez sur **"Sélectionnez un PDF"** dans la sidebar
2. Choisissez un fichier PDF sur votre ordinateur
3. Attendez le message **"PDF ingéré avec succès!"**

**Note**: Le traitement prend quelques secondes selon la taille du PDF

### 6.2 Poser une Question
1. Entrez votre question dans le champ **"Votre question:"**
   - Ex: "Quel est le sujet principal du document?"
2. Cliquez sur **"🔍 Chercher"**
3. La réponse s'affiche avec:
   - 💬 **Réponse** - Générée par l'IA basée sur vos documents
   - 📚 **Sources utilisées** - Citations avec numéros de page
   - 🔬 **Détails de la récupération** - Chunks pertinents trouvés

### 6.3 Personnaliser la Recherche
Dans la section **"🔧 Paramètres avancés"**:
- **Nombre de chunks**: Plus = plus de contexte (défaut: 5)
- **Seuil de similarité**: Moins = plus de résultats (défaut: 0.3)

---

## 🔌 Étape 7: Configurer le LLM (OPTIONNEL)

### 7.1 Utiliser Ollama (LOCAL - RECOMMANDÉ)

**Avantages**: Gratuit, local, confidentiel

#### Installation
1. Télécharger Ollama: https://ollama.ai
2. Installer et lancer l'application
3. Dans terminal: `ollama pull mistral` (télécharge le modèle)
4. Dans un autre terminal: `ollama serve`

**Résultat**: Ollama tourne sur `http://localhost:11434`

#### Configuration dans .env
```env
LLM_TYPE=ollama
LLM_MODEL=mistral
OLLAMA_BASE_URL=http://localhost:11434
```

Redémarrez streamlit et testez!

---

## 📊 Étape 8: Valider le Workflow Complet

### Test complet: upload → question → réponse

```python
from app.rag_pipeline import RAGPipeline
from pathlib import Path

# 1. Créer le pipeline
pipeline = RAGPipeline()

# 2. Ingérer un PDF (si vous en avez un)
# stats = pipeline.ingest_pdf("data/uploads/mon_document.pdf")
# print(f"Chunks créés: {stats['num_chunks']}")

# 3. Poser une question
answer, chunks, citations = pipeline.answer_question("Qui est l'auteur?")
print(f"Réponse: {answer}")
print(f"Citations: {citations}")
```

---

## 🔴 Erreurs Courantes & Solutions

### Erreur 1: "ModuleNotFoundError"
```
Erreur: No module named 'streamlit'
```
**Solution**:
```bash
pip install -r requirements.txt
```

### Erreur 2: "Ollama not running"
```
Erreur: Connection refused to http://localhost:11434
```
**Solution**:
```bash
# Ouvrir un terminal séparé et lancer:
ollama serve
```

### Erreur 3: "Modèle télécharge lentement"
```
Le premier lancement peut prendre du temps...
```
**Explication**: Le modèle d'embeddings (384 MB) se télécharge automatiquement  
**Patience**: C'est normal, attendez ou vérifiez votre connexion

### Erreur 4: "Port 8501 déjà utilisé"
```bash
# Utiliser un autre port
streamlit run app/main.py --server.port 8502
```

### Erreur 5: "Dossiers 'data' manquants"
```bash
# Créer manuellement
mkdir -p data/uploads data/processed vectorstore/index
```

---

## 📝 Cas d'Usage Exemples

### Exemple 1: Analyse de Rapport
```
Q: "Résume les points clés du rapport"
R: [IA générera un résumé basé sur le document]
```

### Exemple 2: Recherche d'Information
```
Q: "Quel est le nom du CEO?"
R: [IA cherchera dans le PDF et affichera la source]
```

### Exemple 3: Questions Multiples
```
Q1: "Quels sont les objectifs?"
Q2: "Comment atteindre ces objectifs?"
R: [Les réponses seront basées uniquement sur le PDF]
```

---

## 🎓 Comprendre l'Architecture

```
┌─────────────────────────────────────────┐
│     You Upload PDF                      │
└──────────────┬──────────────────────────┘
               │
┌──────────────v──────────────────────────┐
│  PDF Loader (utils/pdf_loader.py)      │
│  Extrait le texte du PDF               │
└──────────────┬──────────────────────────┘
               │
┌──────────────v──────────────────────────┐
│  TextChunker (utils/chunking.py)       │
│  Découpe en segments intelligents       │
└──────────────┬──────────────────────────┘
               │
┌──────────────v──────────────────────────┐
│  EmbeddingManager (utils/embeddings.py)│
│  Convertit texte → vecteurs numériques │
└──────────────┬──────────────────────────┘
               │
┌──────────────v──────────────────────────┐
│  FAISSStore (vectorstore/faiss_store.py)
│  Indexe les vecteurs                    │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│  You Ask a Question                     │
└──────────────┬──────────────────────────┘
               │
┌──────────────v──────────────────────────┐
│  RAGPipeline (app/rag_pipeline.py)     │
│  1. Convertir question → vecteur       │
│  2. Chercher dans FAISS                │
│  3. Récupérer segments pertinents      │
└──────────────┬──────────────────────────┘
               │
┌──────────────v──────────────────────────┐
│  LLM (Ollama) - Générer réponse        │
│  "Basé sur ces segments..."            │
└──────────────┬──────────────────────────┘
               │
┌──────────────v──────────────────────────┐
│  CitationHandler - Formater citations   │
│  "Sources: Page 2, Page 5..."          │
└──────────────┬──────────────────────────┘
               │
┌──────────────v──────────────────────────┐
│  Streamlit Interface                    │
│  Affiche réponse + citations + détails │
└─────────────────────────────────────────┘
```

---

## ✅ Checklist de Démarrage

- [ ] Python 3.12 installé
- [ ] Dépendances installées (`pip install -r requirements.txt`)
- [ ] .env créé (ou gardé par défaut)
- [ ] Configuration testée (`python -c "from app.config import settings"`)
- [ ] Streamlit démarré (`streamlit run app/main.py`)
- [ ] PDF uploadé
- [ ] Question posée
- [ ] Réponse + citations affichées ✨

---

## 💡 Tips & Astuces

### 🎯 Pour Meilleures Résultats
- Posez des questions **claires et spécifiques**
- Utilisez des PDFs avec du texte **bien structuré**
- Augmentez TOP_K si trop peu de résultats

### ⚡ Pour Meilleures Performances
- Utilisez `EMBEDDING_MODEL=all-MiniLM-L6-v2` (rapide)
- Réduisez CHUNK_SIZE si très gros PDF (ex: 256)
- Utilisez Ollama local plutôt que remote

### 🔒 Pour Confidentialité
- Ollama fonctionne **100% localement**
- Aucune donnée n'est envoyée à l'extérieur
- Tous les modèles tournent sur votre machine

---

## 📚 Documentation Complète

Voir:
- [README.md](README.md) - Documentation générale
- [PROJECT_COMPLETION.md](PROJECT_COMPLETION.md) - État complet du projet
- [PROJECT_PLAN.md](PROJECT_PLAN.md) - Plan initial

---

## 🚨 Besoin d'Aide?

1. **Erreur pendant l'installation**
   → Vérifiez `requirements.txt`
   → Relancez: `pip install --upgrade pip`

2. **Erreur pendant le lancement**
   → Vérifiez que `.env` existe
   → Activez DEBUG_MODE pour voir les logs

3. **Réponses très courtes ou vides**
   → Vérifiez que le PDF a été bien uploadé
   → Augmentez TOP_K dans paramètres avancés

4. **Lent au premier lancement**
   → Normal! Les modèles se téléchargent (~1 Go)
   → Les prochains lancements seront rapides

---

**🎉 Vous êtes prêt à utiliser le RAG! Bon usage!**

**Questions? Consultez la documentation ou les logs avec `DEBUG_MODE=True`**

---

*Dernière mise à jour: 2026-08-06*  
*MVP Version: 0.1*  
*Status: ✅ PRODUCTION READY*
