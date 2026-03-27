# RAG Pipeline from Scratch — Open Source, Zero API Cost

> A complete Retrieval Augmented Generation (RAG) system built from scratch using fully open-source tools. No OpenAI. No paid APIs. Built on Wikipedia's Human Rights corpus with 490 articles and 64,014 sentence embeddings.

---

## What is RAG?

**RAG (Retrieval Augmented Generation)** solves a core limitation of Large Language Models — they only know what they were trained on. RAG allows an AI model to answer questions based on **your own documents**.

```
Your Documents → Embeddings → Vector Database → Semantic Search → LLM → Grounded Answer
```

Instead of the AI guessing, it retrieves real content from your corpus and generates answers based on that content.

---

## Tech Stack

| Component | Tool | Purpose |
|-----------|------|---------|
| Runtime | Google Colab | Cloud development environment (107GB disk) |
| LLM | deepseek-r1:8b via Ollama | Chat and answer generation |
| Embeddings | nomic-embed-text via Ollama | Converting text to 768-dim vectors |
| Vector DB | PostgreSQL 14 + pgvector | Storing and searching embeddings |
| ORM | SQLAlchemy | Database session management |
| Tokenizer | NLTK sent_tokenize | Sentence-level chunking |
| Corpus | Wikipedia API | 490 Human Rights articles |
| Doc Parser | Docling | PDF, DOCX, PPTX text extraction |

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    INDEXING PIPELINE                      │
│                                                           │
│  Wikipedia API → 490 Articles → NLTK Chunking            │
│       → nomic-embed-text → 768-dim Vectors               │
│       → PostgreSQL + pgvector (64,014 embeddings)        │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│                    QUERY PIPELINE                         │
│                                                           │
│  User Question → nomic-embed-text → Query Vector         │
│       → pgvector cosine similarity search                │
│       → Top-K relevant sentence chunks                   │
│       → Context window expansion                         │
│       → deepseek-r1:8b → Grounded Answer                │
└─────────────────────────────────────────────────────────┘
```

---

## Project Structure

```
rag-models-from-scratch/
│
├── all_articles/                    # 490 Wikipedia articles (corpus)
│
├── ModelFile                        # Ollama model configuration
│   FROM deepseek-r1:8b
│   PARAMETER temperature 0
│   PARAMETER num_ctx 4096
│   PARAMETER seed 42
│
├── ollama_functions.py              # Test embeddings and chat with Ollama
├── generate_corpus.py               # Scrape Wikipedia articles
├── database_connect_embeddings.py   # PostgreSQL schema and session
├── populate_vector_db.py            # Generate and store embeddings
├── pull_db_content.py               # Semantic search with pgvector
├── prepare_content.py               # Context window expansion
└── run_rag.py                       # Full RAG pipeline (entry point)
```

---

## Setup Instructions

### Prerequisites
- Google Colab account (free tier works)
- GitHub account

### Step 1 — Clone the Repository

```python
from google.colab import drive
drive.mount('/content/drive')

!git clone https://github.com/your-github-username/rag-models-from-scratch-with-open-source-3980304.git
import os
os.chdir('/content/rag-models-from-scratch-with-open-source-3980304')
```

### Step 2 — Install System Dependencies

```python
# Install zstd (required for Ollama)
!apt-get install -y zstd

# Install Ollama
!curl -fsSL https://ollama.com/install.sh | sh

# Install PostgreSQL
!apt-get install -y postgresql postgresql-contrib

# Install pgvector from source (no pre-built package available)
!apt-get install -y git build-essential postgresql-server-dev-14
!git clone https://github.com/pgvector/pgvector.git
!cd pgvector && make && make install
```

### Step 3 — Install Python Packages

```python
!pip install ollama wikipedia psycopg2-binary pgvector sqlalchemy \
            beautifulsoup4 nltk requests numpy docling
```

### Step 4 — Start Ollama Server

```python
import subprocess
import time

subprocess.Popen(['ollama', 'serve'])
time.sleep(5)
print("Ollama server started!")
```

### Step 5 — Download Models

```python
# Chat model (for generating answers)
!ollama pull deepseek-r1:8b

# Embedding model (for converting text to vectors)
# NOTE: These are two DIFFERENT types of models serving different purposes
!ollama pull nomic-embed-text
```

> **Key Learning:** Chat models (deepseek) and embedding models (nomic-embed-text) serve fundamentally different functions. Attempting to use a chat model for embeddings throws a `501 error`. Always use a dedicated embedding model for vector generation.

### Step 6 — Set Up PostgreSQL

```python
# Start PostgreSQL
!service postgresql start

# Create database
!sudo -u postgres psql -c "CREATE DATABASE text_embeddings;"

# Set password
!sudo -u postgres psql -c "ALTER USER postgres PASSWORD 'postgres';"

# Grant privileges
!sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE text_embeddings TO postgres;"

# Enable pgvector extension
!sudo -u postgres psql -d text_embeddings -c "CREATE EXTENSION IF NOT EXISTS vector;"
```

### Step 7 — Generate the Corpus

```python
!python3 generate_corpus.py
# Downloads 490 Wikipedia articles on Human Rights
# Saves as .txt files in all_articles/
```

### Step 8 — Generate and Store Embeddings

```python
!python3 populate_vector_db.py
# Reads each article
# Splits into sentences using NLTK
# Converts each sentence to 768-dim vector using nomic-embed-text
# Stores in PostgreSQL — results in 64,014 embeddings
```

### Step 9 — Run the Full RAG Pipeline

```python
!python3 run_rag.py "What are human rights violations in North Korea?"
```

**Example Output:**
```
North Korea is widely recognized for severe human rights violations.
The government maintains strict control over its citizens:

1. Torture and Ill-Treatment: Widespread use of torture by authorities
2. Forced Labor: Institutionalized forced labor including political prisoners
3. Lack of Freedom of Expression: Strict censorship and suppression of free speech
4. Forced Repatriation: Forced return of refugees facing persecution
5. Denial of Basic Rights: Restrictions on religious freedom and right to emigrate
```

---

## File Descriptions

### `database_connect_embeddings.py`
Defines the PostgreSQL schema using SQLAlchemy ORM.

```python
class TextEmbedding(Base):
    __tablename__ = 'text_embeddings'
    id = Column(Integer, primary_key=True, autoincrement=True)
    embedding = Column(Vector)        # 768-dimensional float vector
    content = Column(String)          # Original sentence text
    file_name = Column(String)        # Source article filename
    sentence_number = Column(Integer) # Position in original article
```

### `populate_vector_db.py`
Reads articles, chunks them into sentences, generates embeddings, stores in DB.

```python
sentences = sent_tokenize(content)
embeddings = embed(model="nomic-embed-text", input=sentences)["embeddings"]
# Each sentence → 768 numbers representing its semantic meaning
```

### `prepare_content.py`
Expands search results into full context windows. Instead of returning single sentences, it returns surrounding paragraphs for better context quality.

### `run_rag.py`
The complete pipeline entry point. Accepts any query, retrieves context, generates answer.

---

## Key Technical Decisions & Learnings

### 1. Separate Models for Separate Purposes
The course originally used `deepseek-r1:8b` for both chat and embeddings. This fails because:
- Chat models are trained to generate conversational text
- Embedding models are trained to produce semantic vector representations

**Solution:** Use `nomic-embed-text` (274MB, 768-dim) for embeddings and `deepseek-r1:8b` for generation.

### 2. pgvector Compilation from Source
No pre-built `postgresql-14-pgvector` package exists for Colab's environment. Built from source:

```bash
git clone https://github.com/pgvector/pgvector.git
cd pgvector && make && make install
```

### 3. Sentence-Level Chunking Strategy
Chunking at the sentence level (via NLTK) rather than fixed character windows preserves semantic coherence. Each chunk remains a complete thought.

### 4. Context Window Expansion
Raw search returns the single most similar sentence. The `prepare_content.py` module expands this to include surrounding sentences (configurable window size), providing the LLM with full paragraph context.

### 5. Environment Migration
The project began in GitHub Codespaces (32GB disk) but was migrated to Google Colab (107GB disk) after the `docling` installation filled available storage. This demonstrated the importance of environment planning for ML projects.

---

## Alternative Models and Frameworks

During this project, several alternatives were explored:

| Component | What We Used | Alternatives Explored | Why We Chose Ours |
|-----------|-------------|----------------------|-------------------|
| Chat LLM | deepseek-r1:8b | qwen3:0.6b | Course designed for deepseek |
| Embeddings | nomic-embed-text | Qwen3-Embedding-0.6B, SFR-Embedding-Mistral | Already available via Ollama |
| Vector DB | PostgreSQL + pgvector | Chroma, Pinecone, Weaviate | SQL familiarity + pgvector power |
| Doc Parser | Docling | PyMuPDF, pdfplumber | Multi-format support |
| Chunking | NLTK sentences | LangChain text splitter, fixed windows | Semantic coherence |
| Env | Google Colab | GitHub Codespaces, local setup | Disk space requirements |

---

## Corpus Statistics

| Metric | Value |
|--------|-------|
| Total articles | 490 |
| Successfully embedded | 416 |
| Total sentence embeddings | 64,014 |
| Embedding dimensions | 768 |
| Database | PostgreSQL 14 + pgvector |

---

## How to Ask Questions

```python
# Modify the query in run_rag.py or pass as argument
!python3 run_rag.py "What are women's rights in Saudi Arabia?"
!python3 run_rag.py "Tell me about the Universal Declaration of Human Rights"
!python3 run_rag.py "What human rights violations occur in China?"
```

---

## Future Improvements

- [ ] Add GPU support for faster embedding generation
- [ ] Implement re-ranking for better retrieval quality
- [ ] Build a web interface using Gradio or Streamlit
- [ ] Expand corpus to other domains (legal, medical, technical)
- [ ] Fine-tune the LLM on domain-specific data
- [ ] Apply to Industrial IoT / OT Security anomaly detection

---

## License

Built as an independent learning project exploring RAG architecture 
using open-source tools. Inspired by a LinkedIn Learning course, 
with substantial modifications and independent implementation 
throughout.
