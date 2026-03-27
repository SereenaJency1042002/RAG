# Commands Reference Guide

> Complete list of all commands used in this project, organized by phase.
> Use this as a quick reference to reproduce the setup from scratch.

---

## Phase 1 — Environment Setup (Google Colab)

### Mount Google Drive
```python
from google.colab import drive
drive.mount('/content/drive')
```
**Purpose:** Connect Google Drive for persistent storage across sessions.

### Clone Repository
```python
!git clone https://github.com/your-github-username/rag-models-from-scratch-with-open-source-3980304.git
import os
os.chdir('/content/rag-models-from-scratch-with-open-source-3980304')
```
**Purpose:** Bring the project files into the Colab environment.

---

## Phase 2 — Install Ollama

### Install zstd (dependency)
```bash
!apt-get install -y zstd
```
**Purpose:** Required compression tool for Ollama installation. Without this, Ollama install fails with extraction error.

### Install Ollama
```bash
!curl -fsSL https://ollama.com/install.sh | sh
```
**Purpose:** Install the Ollama LLM inference server.

### Start Ollama Server
```python
import subprocess
import time

subprocess.Popen(['ollama', 'serve'])
time.sleep(5)
print("Ollama server started!")
```
**Purpose:** Start Ollama as a background process. Must be running before any model commands.

### Download Chat Model
```bash
!ollama pull deepseek-r1:8b
```
**Purpose:** Download the 8B parameter DeepSeek reasoning model (5.2GB) for answer generation.

### Download Embedding Model
```bash
!ollama pull nomic-embed-text
```
**Purpose:** Download the dedicated embedding model (274MB). Converts text to 768-dimensional vectors. **Do not use the chat model for embeddings — it will throw a 501 error.**

### Create Custom Model from ModelFile
```bash
!ollama create custom_deepseek -f ModelFile
```
**Purpose:** Create a custom model variant with specific parameters (temperature=0, num_ctx=4096, seed=42).

### List Downloaded Models
```bash
!ollama list
```
**Purpose:** Verify which models are available locally.

### Test Chat Model
```bash
!ollama run deepseek-r1:8b
```
**Purpose:** Interactive test to verify the model responds correctly.

---

## Phase 3 — PostgreSQL Setup

### Install PostgreSQL
```bash
!apt-get install -y postgresql postgresql-contrib
```
**Purpose:** Install the PostgreSQL database server.

### Start PostgreSQL
```bash
!service postgresql start
```
**Purpose:** Start the PostgreSQL service. Must be run every Colab session.

### Check PostgreSQL Status
```bash
!service postgresql status
```
**Purpose:** Verify PostgreSQL is running.

### Create Database
```bash
!sudo -u postgres psql -c "CREATE DATABASE text_embeddings;"
```
**Purpose:** Create the database that will store our embeddings.

### Set Password
```bash
!sudo -u postgres psql -c "ALTER USER postgres PASSWORD 'postgres';"
```
**Purpose:** Set a password for the postgres user to allow Python connections.

### Grant Privileges
```bash
!sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE text_embeddings TO postgres;"
```
**Purpose:** Give full access to the postgres user for our database.

### Install pgvector from Source
```bash
!apt-get install -y git build-essential postgresql-server-dev-14
!git clone https://github.com/pgvector/pgvector.git
!cd pgvector && make && make install
```
**Purpose:** Install the pgvector extension that enables vector operations in PostgreSQL. No pre-built package was available for PostgreSQL 14 on Colab.

### Enable pgvector Extension
```bash
!sudo -u postgres psql -d text_embeddings -c "CREATE EXTENSION IF NOT EXISTS vector;"
```
**Purpose:** Activate pgvector inside our specific database.

### Check Embedding Count
```python
import psycopg2

conn = psycopg2.connect(
    host="localhost",
    database="text_embeddings",
    user="postgres",
    password="postgres"
)
cur = conn.cursor()
cur.execute("SELECT COUNT(*) FROM text_embeddings;")
count = cur.fetchone()[0]
print(f"Total embeddings stored: {count}")
conn.close()
```
**Purpose:** Verify how many embeddings are stored in the database.

---

## Phase 4 — Python Packages

### Install All Required Packages
```bash
!pip install ollama wikipedia psycopg2-binary pgvector sqlalchemy \
            beautifulsoup4 nltk requests numpy docling
```

| Package | Purpose |
|---------|---------|
| ollama | Python SDK to communicate with Ollama server |
| wikipedia | Scrape Wikipedia articles for corpus |
| psycopg2-binary | Connect Python to PostgreSQL |
| pgvector | pgvector support for SQLAlchemy |
| sqlalchemy | ORM for database operations |
| beautifulsoup4 | Parse HTML content |
| nltk | Sentence tokenization for chunking |
| requests | HTTP requests |
| numpy | Numerical array operations |
| docling | Multi-format document parser (PDF, DOCX, PPTX) |

---

## Phase 5 — Run the Pipeline

### Step 1: Generate Corpus
```bash
!python3 generate_corpus.py
```
**Purpose:** Scrape 490 Wikipedia articles about Human Rights. Saves as .txt files in `all_articles/`.

### Step 2: Test Ollama Functions
```bash
!python3 ollama_functions.py
```
**Purpose:** Verify embeddings (nomic-embed-text → 768 numbers) and chat (deepseek → response) both work.

### Step 3: Set Up Database Schema
```bash
!python3 database_connect_embeddings.py
```
**Purpose:** Create the `text_embeddings` table in PostgreSQL with the correct schema.

### Step 4: Populate Vector Database
```bash
!python3 populate_vector_db.py
```
**Purpose:** Read all articles, split into sentences, generate embeddings, store in PostgreSQL. Generates 64,014 embeddings.

### Step 5: Test Semantic Search
```bash
!python3 pull_db_content.py
```
**Purpose:** Test that cosine similarity search works correctly against stored embeddings.

### Step 6: Test Context Preparation
```bash
!python3 prepare_content.py
```
**Purpose:** Verify that context window expansion works (retrieves surrounding sentences, not just single matches).

### Step 7: Run Full RAG Pipeline
```bash
!python3 run_rag.py "What are human rights violations in North Korea?"
```
**Purpose:** Complete end-to-end RAG — retrieves context from database, sends to deepseek, generates grounded answer.

---

## Phase 6 — GitHub

### Configure Git
```bash
!git config --global user.email "your@email.com"
!git config --global user.name "your-github-username"
```
**Purpose:** Set identity for git commits.

### Check Status
```bash
!git status
```
**Purpose:** See which files have changed or are untracked.

### Add Files
```bash
!git add .
```
**Purpose:** Stage all changed and new files for commit.

### Remove Embedded Git Repo
```bash
!git rm --cached pgvector -r
!echo "pgvector/" >> .gitignore
```
**Purpose:** pgvector was cloned as a separate git repo inside our repo. This removes it from tracking and adds it to .gitignore.

### Commit
```bash
!git commit -m "Add RAG pipeline: embeddings, vector DB, retrieval and generation"
```
**Purpose:** Save staged changes with a descriptive message.

### Push to GitHub
```bash
!git push origin main
```
**Purpose:** Upload changes to GitHub remote repository.

---

## Daily Startup Commands (Every Colab Session)

Every time you open a new Colab session, run these in order:

```python
# 1. Mount Drive
from google.colab import drive
drive.mount('/content/drive')

# 2. Navigate to project
import os
os.chdir('/content/rag-models-from-scratch-with-open-source-3980304')

# 3. Start Ollama
import subprocess, time
subprocess.Popen(['ollama', 'serve'])
time.sleep(5)

# 4. Start PostgreSQL
import subprocess
subprocess.run('service postgresql start', shell=True)

# 5. Install packages (Colab resets on each session)
subprocess.run('pip install ollama psycopg2-binary pgvector sqlalchemy nltk -q', shell=True)
```

---

## Debugging Commands

### Check Disk Space
```bash
!df -h /
```

### Check RAM Usage
```bash
!free -h
```

### Check Which Articles Are Missing Embeddings
```python
import os
import psycopg2

all_articles = set(os.listdir('all_articles'))
conn = psycopg2.connect(host="localhost", database="text_embeddings",
                         user="postgres", password="postgres")
cur = conn.cursor()
cur.execute("SELECT DISTINCT file_name FROM text_embeddings;")
embedded = set([row[0] for row in cur.fetchall()])
conn.close()

missing = all_articles - embedded
print(f"Total: {len(all_articles)} | Embedded: {len(embedded)} | Missing: {len(missing)}")
```

### Restart Ollama if Connection Fails
```python
import subprocess, time
subprocess.Popen(['ollama', 'serve'])
time.sleep(5)
print("Ollama restarted!")
```

### Test Database Connection
```python
import psycopg2
conn = psycopg2.connect(host="localhost", database="text_embeddings",
                         user="postgres", password="postgres")
print("Connected! ✅")
conn.close()
```

---

## Common Errors and Fixes

| Error | Cause | Fix |
|-------|-------|-----|
| `zstd: command not found` | Missing package | `apt-get install -y zstd` |
| `501 model does not support embeddings` | Using chat model for embeddings | Use `nomic-embed-text` instead |
| `ConnectionError: Failed to connect to Ollama` | Ollama server not running | Run `subprocess.Popen(['ollama', 'serve'])` |
| `No space left on device` | Disk full | Remove unnecessary models with `ollama rm model-name` |
| `vector.control: No such file or directory` | pgvector not installed | Build from source (see Phase 3) |
| `fe_sendauth: no password supplied` | PostgreSQL password not set | `ALTER USER postgres PASSWORD 'postgres'` |
| `KeyboardInterrupt on psql` | Terminal got stuck | Use Python psycopg2 instead of shell psql |
