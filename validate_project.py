#!/usr/bin/env python3
"""
Script de validation complète du projet RAG.

Vérifie:
1. Structure des dossiers
2. Existence des fichiers Python
3. Imports de tous les modules
4. Configuration
5. Dépendances
"""

import sys
import os
from pathlib import Path

# Couleurs pour terminal
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
RESET = "\033[0m"
BLUE = "\033[94m"


def print_header(text):
    """Imprimer un en-tête."""
    print(f"\n{BLUE}{'='*60}")
    print(f"  {text}")
    print(f"{'='*60}{RESET}")


def print_success(text):
    """Imprimer un message de succès."""
    print(f"{GREEN}✅ {text}{RESET}")


def print_error(text):
    """Imprimer un message d'erreur."""
    print(f"{RED}❌ {text}{RESET}")


def print_warning(text):
    """Imprimer un avertissement."""
    print(f"{YELLOW}⚠️  {text}{RESET}")


def check_folder_structure():
    """Vérifier la structure des dossiers."""
    print_header("1. Vérification de la structure des dossiers")
    
    required_dirs = [
        "app",
        "data",
        "data/uploads",
        "data/processed",
        "utils",
        "vectorstore",
        "vectorstore/index",
        "tests",
    ]
    
    base_path = Path(__file__).parent
    all_ok = True
    
    for dir_name in required_dirs:
        dir_path = base_path / dir_name
        if dir_path.exists():
            print_success(f"Dossier trouvé: {dir_name}")
        else:
            print_error(f"Dossier manquant: {dir_name}")
            all_ok = False
    
    return all_ok


def check_python_files():
    """Vérifier l'existence des fichiers Python."""
    print_header("2. Vérification des fichiers Python")
    
    required_files = [
        "app/__init__.py",
        "app/config.py",
        "app/main.py",
        "app/rag_pipeline.py",
        "app/prompts.py",
        "utils/__init__.py",
        "utils/pdf_loader.py",
        "utils/chunking.py",
        "utils/embeddings.py",
        "utils/citation_handler.py",
        "vectorstore/__init__.py",
        "vectorstore/faiss_store.py",
        "tests/__init__.py",
        "tests/test_pdf_loader.py",
        "tests/test_chunking.py",
        "tests/test_rag_pipeline.py",
        "requirements.txt",
        ".env.example",
    ]
    
    base_path = Path(__file__).parent
    all_ok = True
    
    for file_name in required_files:
        file_path = base_path / file_name
        if file_path.exists():
            size_kb = file_path.stat().st_size / 1024
            if file_name.endswith(".py"):
                print_success(f"{file_name:40} ({size_kb:6.1f} KB)")
            else:
                print_success(f"{file_name:40}")
        else:
            print_error(f"Fichier manquant: {file_name}")
            all_ok = False
    
    return all_ok


def check_imports():
    """Vérifier que tous les imports fonctionnent."""
    print_header("3. Vérification des imports Python")
    
    base_path = Path(__file__).parent
    sys.path.insert(0, str(base_path))
    
    modules_to_test = [
        ("app.config", "Settings"),
        ("utils.pdf_loader", "PDFLoader"),
        ("utils.chunking", "TextChunker"),
        ("utils.embeddings", "EmbeddingManager"),
        ("utils.citation_handler", "CitationHandler"),
        ("vectorstore.faiss_store", "FAISSStore"),
        ("app.rag_pipeline", "RAGPipeline"),
        ("app.prompts", None),  # Module, pas de classe spécifique
    ]
    
    all_ok = True
    
    for module_name, class_name in modules_to_test:
        try:
            module = __import__(module_name, fromlist=[class_name] if class_name else [])
            if class_name:
                if hasattr(module, class_name):
                    print_success(f"{module_name}.{class_name}")
                else:
                    print_error(f"{module_name}.{class_name} - classe non trouvée")
                    all_ok = False
            else:
                print_success(f"{module_name}")
        except ImportError as e:
            print_error(f"{module_name} - Erreur: {e}")
            all_ok = False
        except Exception as e:
            print_warning(f"{module_name} - Avertissement: {e}")
    
    return all_ok


def check_configuration():
    """Vérifier que la configuration charge correctement."""
    print_header("4. Vérification de la configuration")
    
    try:
        from app.config import settings
        
        print_success(f"Configuration chargée:")
        print(f"  - CHUNK_SIZE: {settings.CHUNK_SIZE}")
        print(f"  - CHUNK_OVERLAP: {settings.CHUNK_OVERLAP}")
        print(f"  - EMBEDDING_MODEL: {settings.EMBEDDING_MODEL}")
        print(f"  - EMBEDDING_DIMENSION: {settings.EMBEDDING_DIMENSION}")
        print(f"  - TOP_K: {settings.TOP_K}")
        print(f"  - LLM_MODEL: {settings.LLM_MODEL}")
        print(f"  - UPLOAD_DIR: {settings.UPLOAD_DIR}")
        print(f"  - VECTORSTORE_DIR: {settings.VECTORSTORE_DIR}")
        
        # Vérifier que les dossiers ont été créés
        if settings.UPLOAD_DIR.exists():
            print_success(f"Dossier uploads créé: {settings.UPLOAD_DIR}")
        else:
            print_error(f"Dossier uploads NON créé: {settings.UPLOAD_DIR}")
            return False
        
        if settings.VECTORSTORE_DIR.exists():
            print_success(f"Dossier vectorstore créé: {settings.VECTORSTORE_DIR}")
        else:
            print_error(f"Dossier vectorstore NON créé: {settings.VECTORSTORE_DIR}")
            return False
        
        return True
    
    except Exception as e:
        print_error(f"Erreur lors du chargement de la config: {e}")
        return False


def check_dependencies():
    """Vérifier les dépendances principales."""
    print_header("5. Vérification des dépendances")
    
    dependencies = [
        "streamlit",
        "langchain",
        "sentence_transformers",
        "faiss",
        "pydantic",
        "pypdf",
        "numpy",
        "requests",
    ]
    
    all_ok = True
    
    for dep in dependencies:
        try:
            __import__(dep)
            print_success(f"{dep} installé")
        except ImportError:
            print_error(f"{dep} NON installé")
            all_ok = False
    
    return all_ok


def main():
    """Exécuter la validation complète."""
    print(f"\n{BLUE}🔍 Validation du Projet RAG Documentaire d'Entreprise{RESET}")
    print(f"{BLUE}{'='*60}{RESET}")
    
    results = {
        "Structure": check_folder_structure(),
        "Fichiers": check_python_files(),
        "Imports": check_imports(),
        "Configuration": check_configuration(),
        "Dépendances": check_dependencies(),
    }
    
    # Résumé
    print_header("RÉSUMÉ DE LA VALIDATION")
    
    for check_name, result in results.items():
        status = f"{GREEN}✅ OK{RESET}" if result else f"{RED}❌ ERREUR{RESET}"
        print(f"  {check_name:20} : {status}")
    
    all_passed = all(results.values())
    
    print(f"\n{BLUE}{'='*60}{RESET}")
    if all_passed:
        print(f"{GREEN}🎉 Validation réussie! Le projet est prêt.{RESET}")
        return 0
    else:
        print(f"{RED}⚠️  Quelques vérifications ont échoué.{RESET}")
        print(f"{YELLOW}Veuillez corriger les erreurs et relancer le script.{RESET}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
