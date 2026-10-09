# RAG Enterprise MVP — Document Question Answering

An AI-powered document assistant that enables users to upload PDF files, ask questions in natural language, and receive context-grounded answers with source references.

## Overview

This project implements a **Retrieval-Augmented Generation (RAG)** pipeline to retrieve relevant information from documents before generating answers. It aims to make document search more efficient while improving answer traceability.

## Key Features

* PDF document upload and text extraction
* Text chunking with configurable size and overlap
* Semantic embeddings using Hugging Face / Sentence Transformers
* Vector similarity search with FAISS
* Context-based answer generation
* Source references to help users verify answers
* Interactive web interface built with Streamlit

## Tech Stack

| Component       | Technology                                  |
| --------------- | ------------------------------------------- |
| Language        | Python                                      |
| User interface  | Streamlit                                   |
| Embeddings      | Hugging Face / Sentence Transformers        |
| Vector database | FAISS                                       |
| PDF processing  | PyPDF                                       |
| LLM integration | Hugging Face or another configured provider |
| Configuration   | Environment variables                       |

## Architecture

```text
PDF Documents
     ↓
Text Extraction
     ↓
Text Chunking
     ↓
Embedding Generation
     ↓
FAISS Vector Index
     ↓
User Question
     ↓
Semantic Retrieval
     ↓
Context-Based Answer
     ↓
Answer + Source References
```

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/NORAel-fettouchi/rag-enterprise-mvp.git
cd rag-enterprise-mvp
```

### 2. Create a virtual environment

**Windows PowerShell**

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Configure the application

Review `.env.example` and configure the environment variables required by the selected language model provider. Keep API keys and other secrets out of version control.

### 5. Run the application

Use the entry point configured by the project. If `app/main.py` contains the Streamlit application:

```bash
streamlit run app/main.py
```

Open the local URL displayed in the terminal.

## How It Works

1. **Ingestion:** PDF documents are uploaded and their text is extracted.
2. **Chunking:** The text is divided into smaller overlapping segments.
3. **Embedding:** Each segment is converted into a numerical vector.
4. **Indexing:** FAISS stores the vectors for efficient similarity search.
5. **Retrieval:** Relevant segments are selected for each user question.
6. **Generation:** The language model generates an answer based on the retrieved context.
7. **Citations:** Source references help users trace answers back to the documents.

## Project Structure

```text
rag-enterprise-mvp/
├── app/
│   ├── main.py
│   ├── config.py
│   └── rag_pipeline.py
├── scripts/
├── tests/
├── utils/
├── .env.example
├── requirements.txt
└── README.md
```

The exact structure may evolve as the project develops.

## Testing

Run the tests available in the repository:

```bash
python -m pytest -v
```

Some integration tests may require model-provider configuration or network access.

## Current Scope and Limitations

* Answer quality depends on document quality and retrieval relevance.
* The system may produce incomplete or inaccurate answers.
* PDF image extraction and OCR may require additional implementation.
* Authentication, multi-user access control, and production monitoring are not included unless explicitly implemented.

## Future Improvements

* Retrieval quality evaluation and automated tests
* Conversation history
* Support for additional document formats
* REST API integration
* Document-level access control
* Containerization and cloud deployment

## Author

**Nora El-Fettouchi**

Engineering student in Data Science & Cloud Computing at ENSAO.

[GitHub Profile](https://github.com/NORAel-fettouchi)

---

*This project is an evolving MVP. Features, model integrations, and setup instructions should be verified against the current implementation.*
