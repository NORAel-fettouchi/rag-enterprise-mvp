"""
Interface Streamlit pour l'application RAG.

Point d'entrée de l'application.
Permet:
- Upload PDF
- Questions
- Affichage réponses + citations
"""

import streamlit as st
import logging
from pathlib import Path
from typing import Optional
import tempfile

from config import settings
from rag_pipeline import RAGPipeline

# Configuration logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


# Configuration Streamlit
st.set_page_config(
    page_title=settings.APP_TITLE,
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personnalisé
st.markdown("""
<style>
    .citation-box {
        background-color: #f0f2f6;
        padding: 10px;
        border-radius: 5px;
        margin: 5px 0;
        border-left: 4px solid #1f77b4;
    }
    .source-badge {
        display: inline-block;
        background-color: #1f77b4;
        color: white;
        padding: 5px 10px;
        border-radius: 3px;
        font-size: 12px;
        margin: 2px;
    }
    .answer-box {
        background-color: #f9f9f9;
        padding: 15px;
        border-radius: 5px;
        border: 1px solid #e0e0e0;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_resource
def initialize_pipeline():
    """
    Initialiser le pipeline RAG une seule fois.
    
    Utilise @st.cache_resource pour ne pas réinitialiser
    à chaque rechargement de la page.
    """
    logger.info("Initialisation du pipeline RAG...")
    return RAGPipeline(reload_index=False)


def main():
    """Fonction principale de l'application."""
    
    # En-tête
    st.title(f"📄 {settings.APP_TITLE}")
    st.markdown(
        "Posez des questions sur vos documents PDF et recevez des réponses "
        "précises avec citations des sources."
    )
    
    # Initialiser le pipeline
    rag_pipeline = initialize_pipeline()
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # Afficher les stats du vectorstore
        stats = rag_pipeline.get_vectorstore_stats()
        st.metric("📊 Vecteurs indexés", stats["nb_vectors"])
        st.metric("🗂️ Chunks totaux", stats["nb_chunks"])
        st.metric("📐 Dimensions embedding", stats["embedding_dim"])
        
        # Section upload
        st.subheader("📤 Upload PDF")
        uploaded_file = st.file_uploader(
            "Sélectionnez un PDF",
            type="pdf",
            help="Fichier PDF à analyser"
        )
        
        if uploaded_file is not None:
            # Sauvegarder temporairement et traiter
            with st.spinner("⏳ Traitement du PDF..."):
                try:
                    # Créer un fichier temporaire
                    with tempfile.NamedTemporaryFile(
                        delete=False,
                        suffix=".pdf"
                    ) as tmp_file:
                        tmp_file.write(uploaded_file.getbuffer())
                        tmp_path = tmp_file.name
                    
                    # Ingérer le PDF
                    ingest_stats = rag_pipeline.ingest_pdf(tmp_path)
                    
                    st.success(
                        f"✅ PDF ingéré avec succès!\n"
                        f"- {ingest_stats['num_chunks']} chunks\n"
                        f"- {ingest_stats['metadata']['pages']} pages"
                    )
                    
                    # Nettoyer le fichier temporaire
                    Path(tmp_path).unlink()
                
                except Exception as e:
                    st.error(f"❌ Erreur lors du traitement: {str(e)}")
                    logger.error(f"Erreur d'ingestion: {e}")
        
        # Paramètres avancés
        with st.expander("🔧 Paramètres avancés"):
            top_k = st.slider(
                "Nombre de chunks à récupérer",
                min_value=1,
                max_value=20,
                value=settings.TOP_K,
                help="Plus = plus de contexte mais aussi plus de bruit"
            )
            
            threshold = st.slider(
                "Seuil de similarité",
                min_value=0.0,
                max_value=1.0,
                value=settings.SIMILARITY_THRESHOLD,
                step=0.05,
                help="Minimum de pertinence pour inclure un chunk"
            )
        
        st.divider()
        st.caption(
            f"⚡ Modèle: {settings.EMBEDDING_MODEL}\n"
            f"🔄 LLM: {settings.LLM_MODEL}"
        )
    
    # Zone principale
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.subheader("❓ Poser une Question")
    
    with col2:
        st.write("")  # Espacement
    
    # Input utilisateur
    question = st.text_input(
        "Votre question:",
        placeholder="Ex: Quel est le résumé du document?",
        label_visibility="collapsed"
    )
    
    # Bouton soumettre
    col1, col2, col3 = st.columns([1, 1, 3])
    
    with col1:
        submit_button = st.button("🔍 Chercher", use_container_width=True)
    
    with col2:
        clear_button = st.button("🗑️ Effacer", use_container_width=True)
    
    if clear_button:
        st.rerun()
    
    # Traiter la question
    if submit_button and question:
        
        # Vérifier que l'index n'est pas vide
        if stats["nb_vectors"] == 0:
            st.warning(
                "⚠️ Aucun document n'a été indexé. "
                "Veuillez d'abord uploader un PDF."
            )
        else:
            with st.spinner("⏳ Analyse en cours..."):
                try:
                    # Générer la réponse
                    answer, retrieved_chunks, citations = rag_pipeline.answer_question(
                        question,
                        top_k=top_k
                    )
                    
                    # Afficher la réponse
                    st.success("✅ Réponse générée!")
                    
                    # Réponse principale
                    st.markdown("### 💬 Réponse")
                    st.markdown(
                        f'<div class="answer-box">{answer}</div>',
                        unsafe_allow_html=True
                    )
                    
                    # Citations
                    if citations:
                        st.markdown("### 📚 Sources utilisées")
                        for citation in citations:
                            st.markdown(
                                f'<div class="citation-box">{citation}</div>',
                                unsafe_allow_html=True
                            )
                    
                    # Chunks récupérés (détails)
                    with st.expander("🔬 Détails de la récupération"):
                        st.write(f"**Chunks pertinents trouvés: {len(retrieved_chunks)}**")
                        
                        for i, result in enumerate(retrieved_chunks, 1):
                            chunk = result["chunk"]
                            score = result["similarity_score"]
                            
                            st.markdown(f"**Chunk {i}** (Pertinence: {score:.1%})")
                            st.caption(chunk.get("text", "")[:200] + "...")
                            
                            # Métadonnées
                            meta = chunk.get("metadata", {})
                            if meta:
                                cols = st.columns(3)
                                with cols[0]:
                                    if "title" in meta:
                                        st.caption(f"📄 {meta['title']}")
                                with cols[1]:
                                    if "page_num" in meta:
                                        st.caption(f"📖 Page {meta['page_num']}")
                                with cols[2]:
                                    st.caption(f"⚡ ID: {chunk.get('id', 'N/A')}")
                            
                            st.divider()
                
                except Exception as e:
                    st.error(f"❌ Erreur: {str(e)}")
                    logger.error(f"Erreur dans answer_question: {e}")
    
    # Footer
    st.divider()
    st.markdown(
        "---\n"
        "**RAG Documentaire d'Entreprise** | "
        "MVP v0.1 | "
        "[Documentation](#)"
    )


if __name__ == "__main__":
    main()
