"""
Templates de prompts pour le pipeline RAG.

Contient les prompts systèmes et utilisateurs pour le LLM.
"""


# Prompt système pour le RAG
SYSTEM_PROMPT = """Tu es un assistant expert en analyse documentaire.

IMPORTANT:
- Réponds UNIQUEMENT en te basant sur les documents fournis.
- Si l'information n'est pas dans les documents, dis "Je ne trouve pas cette information dans les documents fournis."
- Cite TOUJOURS les sources (numéro de page, nom du document).
- Sois concis et précis.
- Si la question est ambiguë, demande une clarification.

Contexte des documents:
{context}

Réponds en Français."""


# Template pour insérer le contexte avant la question
RETRIEVAL_QA_PROMPT = """Basé sur le contexte fourni ci-dessous, répondez à la question.

CONTEXTE:
{context}

QUESTION: {question}

RÉPONSE:"""


# Prompt pour résumer des documents
SUMMARIZE_PROMPT = """Résume les points clés du document suivant en 5-10 points essentiels:

DOCUMENT:
{document}

RÉSUMÉ (points clés uniquement):"""


# Prompt pour extraire les informations clés
EXTRACT_INFO_PROMPT = """Extrait les informations clés du document concernant: {topic}

DOCUMENT:
{document}

INFORMATIONS CLÉS CONCERNANT '{topic}':"""


# Prompt pour améliorer la question
IMPROVE_QUESTION_PROMPT = """Reformule cette question pour la rendre plus claire et précise:

Question originale: {question}

Question améliorée:"""


# Prompt pour générer un titre
GENERATE_TITLE_PROMPT = """Génère un titre pertinent et concis pour ce document:

Contenu (100 premiers caractères):
{content}

Titre:"""


def format_context(retrieved_chunks: list) -> str:
    """
    Formater les chunks récupérés en contexte.
    
    Args:
        retrieved_chunks: Liste de chunks avec metadata
    
    Returns:
        String formatée pour insérer dans le prompt
    """
    context_parts = []
    
    for i, chunk_data in enumerate(retrieved_chunks, 1):
        chunk = chunk_data.get("chunk", {})
        text = chunk.get("text", "")
        metadata = chunk.get("metadata", {})
        similarity = chunk_data.get("similarity_score", 0)
        
        # Créer une section pour chaque chunk
        # Utiliser le nom de fichier source si disponible, sinon le titre
        source = (
            metadata.get("source_filename", "")
            or metadata.get("title", "")
            or "Document"
        )
        page = metadata.get("page_num")
        
        section = f"[Source {i}: {source}"
        if page:
            section += f" - Page {page}"
        section += f" - Pertinence: {similarity:.1%}]\n"
        section += text
        
        context_parts.append(section)
    
    return "\n\n---\n\n".join(context_parts)


def get_system_prompt() -> str:
    """Retourner le prompt système."""
    return SYSTEM_PROMPT


def get_retrieval_qa_prompt(
    context: str,
    question: str
) -> str:
    """
    Formater le prompt QA avec contexte.
    
    Args:
        context: Contexte formaté
        question: Question de l'utilisateur
    
    Returns:
        Prompt formaté
    """
    return RETRIEVAL_QA_PROMPT.format(
        context=context,
        question=question
    )
