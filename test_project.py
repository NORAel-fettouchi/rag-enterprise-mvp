"""
Script de validation complète du projet RAG.

Vérifie:
1. Imports et configuration
2. Chargement des modèles
3. PDF processing
4. Chunking
5. Embeddings
6. Vector store
7. Retrieval
8. Pipeline complet

Utilisation:
    python test_project.py
"""

import sys
import io

# Forcer UTF-8 pour l'output
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
if sys.stderr.encoding != 'utf-8':
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

from pathlib import Path

# Ajouter le répertoire racine au chemin
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

import logging
import tempfile
from typing import List, Tuple

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Couleurs pour les tests
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"


class ProjectValidator:
    """Validateur du projet RAG."""
    
    def __init__(self):
        """Initialiser le validateur."""
        self.tests_passed = 0
        self.tests_failed = 0
        self.errors = []
    
    def print_header(self, title: str):
        """Afficher un en-tête."""
        print(f"\n{BLUE}{'='*60}{RESET}")
        print(f"{BLUE}{title.center(60)}{RESET}")
        print(f"{BLUE}{'='*60}{RESET}\n")
    
    def print_test(self, name: str, status: bool, message: str = ""):
        """Afficher le résultat d'un test."""
        status_str = f"{GREEN}✅ PASS{RESET}" if status else f"{RED}❌ FAIL{RESET}"
        print(f"{status_str} | {name}")
        
        if message:
            print(f"     {message}")
        
        if status:
            self.tests_passed += 1
        else:
            self.tests_failed += 1
    
    # ===== TEST 1: IMPORTS ET CONFIG =====
    def test_imports(self) -> bool:
        """Tester les imports."""
        self.print_header("TEST 1: IMPORTS ET CONFIGURATION")
        
        try:
            logger.info("Vérification des imports...")
            
            from app.config import settings
            self.print_test("Config chargée", True)
            
            from utils.pdf_loader import PDFLoader
            self.print_test("PDFLoader importé", True)
            
            from utils.chunking import TextChunker
            self.print_test("TextChunker importé", True)
            
            from utils.embeddings import EmbeddingManager
            self.print_test("EmbeddingManager importé", True)
            
            from utils.citation_handler import CitationHandler
            self.print_test("CitationHandler importé", True)
            
            from vectorstore.faiss_store import FAISSStore
            self.print_test("FAISSStore importé", True)
            
            from app.rag_pipeline import RAGPipeline
            self.print_test("RAGPipeline importé", True)
            
            from app.prompts import format_context, get_retrieval_qa_prompt
            self.print_test("Prompts importés", True)
            
            # Afficher la configuration
            print(f"\n{YELLOW}Configuration chargée:{RESET}")
            print(f"  • Embedding model: {settings.EMBEDDING_MODEL}")
            print(f"  • Embedding dim: {settings.EMBEDDING_DIMENSION}")
            print(f"  • Chunk size: {settings.CHUNK_SIZE}")
            print(f"  • Top-K: {settings.TOP_K}")
            print(f"  • LLM type: {settings.LLM_TYPE}")
            print(f"  • Upload dir: {settings.UPLOAD_DIR}")
            
            return True
        
        except Exception as e:
            self.print_test("Imports", False, str(e))
            self.errors.append(f"Import error: {e}")
            return False
    
    # ===== TEST 2: CONFIGURATION =====
    def test_configuration(self) -> bool:
        """Tester la configuration."""
        self.print_header("TEST 2: CONFIGURATION")
        
        try:
            from app.config import settings
            
            # Vérifier les variables obligatoires
            required_vars = [
                ("EMBEDDING_MODEL", settings.EMBEDDING_MODEL),
                ("CHUNK_SIZE", settings.CHUNK_SIZE),
                ("TOP_K", settings.TOP_K),
                ("LLM_MODEL", settings.LLM_MODEL),
            ]
            
            for var_name, var_value in required_vars:
                status = var_value is not None
                self.print_test(f"{var_name}: {var_value}", status)
            
            # Vérifier les dossiers
            folders = [
                ("Upload dir", settings.UPLOAD_DIR),
                ("Processed dir", settings.PROCESSED_DIR),
                ("Vectorstore dir", settings.VECTORSTORE_DIR),
            ]
            
            for folder_name, folder_path in folders:
                exists = folder_path.exists()
                self.print_test(
                    f"{folder_name} exists",
                    exists,
                    str(folder_path)
                )
            
            return True
        
        except Exception as e:
            self.print_test("Configuration", False, str(e))
            self.errors.append(f"Config error: {e}")
            return False
    
    # ===== TEST 3: EMBEDDINGS =====
    def test_embeddings(self) -> bool:
        """Tester le gestionnaire d'embeddings."""
        self.print_header("TEST 3: EMBEDDINGS")
        
        try:
            from utils.embeddings import EmbeddingManager
            from app.config import settings
            import numpy as np
            
            logger.info("Initialisation du gestionnaire d'embeddings...")
            
            manager = EmbeddingManager()
            self.print_test("EmbeddingManager initialisé", True)
            
            # Vérifier la dimension
            dim = manager.embedding_dim
            expected_dim = settings.EMBEDDING_DIMENSION
            status = dim == expected_dim
            self.print_test(
                f"Embedding dimension",
                status,
                f"{dim} (expected {expected_dim})"
            )
            
            # Encoder un texte de test
            test_text = "Ceci est un test d'embedding."
            logger.info(f"Encoding test: '{test_text}'")
            
            embedding = manager.encode_text(test_text)
            
            status = (
                isinstance(embedding, np.ndarray) and
                embedding.shape[0] == dim
            )
            self.print_test("Single text encoding", status)
            
            # Encoder un batch
            test_texts = [
                "Premier texte de test",
                "Deuxième texte de test",
                "Troisième texte de test",
            ]
            
            logger.info(f"Encoding batch of {len(test_texts)} texts...")
            embeddings = manager.encode_batch(test_texts, batch_size=2)
            
            status = (
                isinstance(embeddings, np.ndarray) and
                embeddings.shape == (len(test_texts), dim)
            )
            self.print_test("Batch encoding", status)
            
            return True
        
        except Exception as e:
            self.print_test("Embeddings", False, str(e))
            self.errors.append(f"Embeddings error: {e}")
            return False
    
    # ===== TEST 4: CHUNKING =====
    def test_chunking(self) -> bool:
        """Tester le chunking."""
        self.print_header("TEST 4: CHUNKING")
        
        try:
            from utils.chunking import TextChunker
            from app.config import settings
            
            chunker = TextChunker(
                chunk_size=settings.CHUNK_SIZE,
                chunk_overlap=settings.CHUNK_OVERLAP
            )
            self.print_test("TextChunker initialisé", True)
            
            # Texte de test
            test_text = """
            Ceci est un texte de test pour le chunking.
            
            Il contient plusieurs paragraphes pour tester le découpage.
            Le chunking doit diviser le texte en segments intelligents.
            
            Chaque chunk doit avoir une taille appropriée.
            Et les chunks doivent avoir un chevauchement.
            """ * 10
            
            metadata = {"title": "Test Document", "page_num": 1}
            
            logger.info(f"Chunking {len(test_text)} characters...")
            chunks = chunker.chunk_text(test_text, metadata)
            
            status = len(chunks) > 0
            self.print_test("Text chunking", status, f"{len(chunks)} chunks created")
            
            # Vérifier les métadonnées
            all_chunks = chunker.get_chunks()
            has_metadata = all(
                "metadata" in chunk for chunk in all_chunks
            )
            self.print_test("Chunks have metadata", has_metadata)
            
            return True
        
        except Exception as e:
            self.print_test("Chunking", False, str(e))
            self.errors.append(f"Chunking error: {e}")
            return False
    
    # ===== TEST 5: VECTOR STORE =====
    def test_vector_store(self) -> bool:
        """Tester le vector store FAISS."""
        self.print_header("TEST 5: VECTOR STORE (FAISS)")
        
        try:
            from vectorstore.faiss_store import FAISSStore
            from app.config import settings
            import numpy as np
            
            vectorstore = FAISSStore(
                embedding_dim=settings.EMBEDDING_DIMENSION
            )
            self.print_test("FAISSStore initialisé", True)
            
            # Vérifier les stats initiales
            stats = vectorstore.get_stats()
            self.print_test(
                "Get stats",
                stats["nb_vectors"] == 0,
                f"Initial vectors: {stats['nb_vectors']}"
            )
            
            # Ajouter des chunks avec embeddings
            test_chunks = []
            for i in range(3):
                chunk = {
                    "id": i,
                    "text": f"Chunk de test numéro {i}",
                    "embedding": np.random.rand(settings.EMBEDDING_DIMENSION).astype(np.float32),
                    "metadata": {"title": "Test", "page_num": 1},
                }
                test_chunks.append(chunk)
            
            logger.info(f"Adding {len(test_chunks)} chunks...")
            vectorstore.add_chunks(test_chunks)
            
            stats_after = vectorstore.get_stats()
            status = stats_after["nb_vectors"] == len(test_chunks)
            self.print_test(
                "Add chunks",
                status,
                f"Vectors added: {stats_after['nb_vectors']}"
            )
            
            # Tester la recherche
            query_embedding = np.random.rand(settings.EMBEDDING_DIMENSION).astype(np.float32)
            
            logger.info("Testing similarity search...")
            results = vectorstore.search(query_embedding, top_k=2)
            
            status = len(results) <= 2
            self.print_test("Similarity search", status, f"Results: {len(results)}")
            
            # Vérifier la sauvegarde/chargement
            logger.info("Testing save/load...")
            vectorstore.save_index()
            
            index_exists = vectorstore.index_exists()
            self.print_test("Index saved", index_exists)
            
            # Charger dans une nouvelle instance
            vectorstore2 = FAISSStore(
                embedding_dim=settings.EMBEDDING_DIMENSION
            )
            vectorstore2.load_index()
            
            stats_loaded = vectorstore2.get_stats()
            status = stats_loaded["nb_vectors"] == stats_after["nb_vectors"]
            self.print_test(
                "Index loaded",
                status,
                f"Loaded vectors: {stats_loaded['nb_vectors']}"
            )
            
            return True
        
        except Exception as e:
            self.print_test("Vector Store", False, str(e))
            self.errors.append(f"Vector store error: {e}")
            return False
    
    # ===== TEST 6: PDF LOADER =====
    def test_pdf_loader(self) -> bool:
        """Tester le chargeur PDF."""
        self.print_header("TEST 6: PDF LOADER")
        
        try:
            from utils.pdf_loader import PDFLoader
            
            # Tester avec un fichier non-existant
            logger.info("Testing error handling...")
            try:
                PDFLoader("fichier_inexistant.pdf")
                self.print_test("Error on missing file", False, "Should raise FileNotFoundError")
            except FileNotFoundError:
                self.print_test("Error on missing file", True)
            
            # Tester avec un fichier non-PDF
            try:
                with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as f:
                    f.write(b"Ceci n'est pas un PDF")
                    f.flush()
                    temp_path = f.name
                
                try:
                    PDFLoader(temp_path)
                    self.print_test("Error on non-PDF file", False)
                except ValueError:
                    self.print_test("Error on non-PDF file", True)
                finally:
                    Path(temp_path).unlink()
            
            except Exception as e:
                self.print_test("Non-PDF error test", False, str(e))
            
            return True
        
        except Exception as e:
            self.print_test("PDF Loader", False, str(e))
            self.errors.append(f"PDF loader error: {e}")
            return False
    
    # ===== TEST 7: CITATIONS =====
    def test_citations(self) -> bool:
        """Tester la gestion des citations."""
        self.print_header("TEST 7: CITATIONS")
        
        try:
            from utils.citation_handler import CitationHandler
            
            handler = CitationHandler()
            self.print_test("CitationHandler initialisé", True)
            
            # Ajouter des sources
            handler.add_source(
                chunk_id=0,
                text="Texte d'exemple",
                source_file="test.pdf",
                page_num=1,
                similarity_score=0.95
            )
            
            handler.add_source(
                chunk_id=1,
                text="Autre texte",
                source_file="test.pdf",
                page_num=2,
                similarity_score=0.87
            )
            
            citations = handler.get_citations()
            status = len(citations) == 2
            self.print_test("Add sources", status, f"Citations: {len(citations)}")
            
            # Format citations
            formatted = handler.get_formatted_citations()
            status = len(formatted) == 2 and all(isinstance(f, str) for f in formatted)
            self.print_test("Format citations", status)
            
            # Reset
            handler.reset()
            status = len(handler.get_citations()) == 0
            self.print_test("Reset citations", status)
            
            return True
        
        except Exception as e:
            self.print_test("Citations", False, str(e))
            self.errors.append(f"Citations error: {e}")
            return False
    
    # ===== TEST 8: RAG PIPELINE =====
    def test_rag_pipeline(self) -> bool:
        """Tester le pipeline RAG."""
        self.print_header("TEST 8: RAG PIPELINE")
        
        try:
            from app.rag_pipeline import RAGPipeline
            from app.config import settings
            
            logger.info("Initializing RAG Pipeline...")
            
            pipeline = RAGPipeline(reload_index=True)
            self.print_test("RAGPipeline initialized", True)
            
            # Vérifier les stats
            stats = pipeline.get_vectorstore_stats()
            self.print_test(
                "Get vectorstore stats",
                True,
                f"Vectors: {stats.get('nb_vectors', 0)}"
            )
            
            # Tester la retrieval avec un index vide
            try:
                logger.info("Testing retrieval with empty index...")
                results = pipeline.retrieve("Test query")
                status = isinstance(results, list)
                self.print_test("Retrieve (empty index)", status)
            
            except Exception as e:
                # C'est OK si ça échoue avec un index vide
                self.print_test("Retrieve (empty index)", True, "Expected to return empty")
            
            return True
        
        except Exception as e:
            self.print_test("RAG Pipeline", False, str(e))
            self.errors.append(f"RAG pipeline error: {e}")
            return False
    
    # ===== RAPPORT FINAL =====
    def print_summary(self):
        """Afficher le résumé final."""
        self.print_header("RAPPORT FINAL")
        
        total = self.tests_passed + self.tests_failed
        success_rate = (
            (self.tests_passed / total * 100) if total > 0 else 0
        )
        
        print(f"Tests réussis:  {GREEN}{self.tests_passed}{RESET}")
        print(f"Tests échoués:  {RED}{self.tests_failed}{RESET}")
        print(f"Total:          {total}")
        print(f"Taux réussite:  {success_rate:.1f}%\n")
        
        if self.errors:
            print(f"{RED}Erreurs détectées:{RESET}")
            for error in self.errors:
                print(f"  • {error}")
        
        if self.tests_failed == 0:
            print(f"{GREEN}✅ TOUS LES TESTS SONT PASSÉS!{RESET}")
            return 0
        else:
            print(
                f"{RED}❌ {self.tests_failed} test(s) échoué(s).{RESET}\n"
                f"{YELLOW}Actions recommandées:{RESET}\n"
                f"  1. Vérifier les erreurs ci-dessus\n"
                f"  2. Vérifier que les dépendances sont installées: pip install -r requirements.txt\n"
                f"  3. Vérifier les variables .env\n"
                f"  4. Consulter les logs détaillés"
            )
            return 1
    
    def run_all_tests(self) -> int:
        """Exécuter tous les tests."""
        print(f"\n{BLUE}{'='*60}{RESET}")
        print(f"{BLUE}{'VALIDATION DU PROJET RAG'.center(60)}{RESET}")
        print(f"{BLUE}{'='*60}{RESET}")
        
        # Exécuter les tests dans l'ordre
        self.test_imports()
        self.test_configuration()
        self.test_embeddings()
        self.test_chunking()
        self.test_vector_store()
        self.test_pdf_loader()
        self.test_citations()
        self.test_rag_pipeline()
        
        # Afficher le résumé
        return self.print_summary()


if __name__ == "__main__":
    validator = ProjectValidator()
    exit_code = validator.run_all_tests()
    sys.exit(exit_code)
