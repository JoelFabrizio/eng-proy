# 🎓 English Academic RAG Assistant

🌐 **[English Version](README_EN.md)** | **[Versión en Español](README.md)**

Welcome to the **English Academic RAG Assistant**! This project is a comprehensive solution based on **Retrieval-Augmented Generation (RAG)** that acts as an Academic English Tutor for students and a Pedagogical Mentor for teachers.

---

## 🌟 Key Features

- **Dual Role (Student / Teacher)**:
  - **👨‍🎓 Student Mode**: Focused on learning English, practicing grammar, vocabulary, and reading. Strictly filters out teacher-only pedagogical materials.
  - **👨‍🏫 Teacher Mode**: Focused on ELT (English Language Teaching) methodologies, lesson planning, and didactics.
- **🎯 English Level Diagnostic Test (A1 - C1)**:
  - Adaptive interactive evaluation. The RAG tutor determines the student's level according to the Common European Framework of Reference for Languages (CEFR) and dynamically adjusts the complexity of explanations.
- **📜 Persistent Chat History**:
  - Secure storage in SQLite. Maintains active conversations and manages multiple chat sessions.
- **📚 Multi-category Vector Database (ChromaDB)**:
  - Semantic similarity search using Hugging Face Embeddings (`BAAI/bge-small-en-v1.5`).
- **🦙 Ollama and OpenAI Support**:
  - Easily configurable via environment variables (`.env`).

---

## 📁 Project Structure

```text
├── app/
│   ├── api/                  # FastAPI Endpoints (Auth, Chat, Sessions)
│   ├── core/                 # Security (JWT, Bcrypt) and Logging
│   ├── db/                   # SQLite Database and SQLAlchemy models
│   ├── providers/            # AI Provider Factory (Ollama / OpenAI)
│   ├── schemas/              # Pydantic validation schemas
│   └── services/             # RAG Service, Dual Prompts & SQL History
├── db_vectorial/             # Persistent Vector Database (ChromaDB)
├── app_ui.py                 # Streamlit Interactive Graphical Interface
├── config.py                 # System Configuration Settings
├── main.py                   # FastAPI Server Entrypoint
├── start.py                  # Unified Launch Script (Backend + Frontend)
├── crear_embeddings_locales.py # Script to process documents and populate ChromaDB
├── descargar_drive.py        # Script to download materials from Google Drive
├── requirements-cpu.txt      # CPU Requirements
├── requirements-gpu.txt      # GPU Optimized Requirements (CUDA 13.0)
├── docker-compose.yml        # Docker Compose Configuration
├── README.md                 # Project Documentation (Spanish)
└── README_EN.md              # Project Documentation (English)
```

---

## 🛠️ Prerequisites

1. **Python 3.10+** (Recommended Python 3.10 or 3.11).
2. **Ollama** installed on your system if using the local provider:
   ```bash
   ollama pull llama3
   ollama pull nomic-embed-text
   ```

---

## 🚀 Installation & Setup

### 1. Clone the repository and create a virtual environment
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows (PowerShell):
.\venv\Scripts\Activate.ps1
# On Linux / macOS:
source venv/bin/activate
```

### 2. Install dependencies

Choose the version corresponding to your hardware:

- **For GPU (NVIDIA CUDA 13.0):**
  ```bash
  pip install -r requirements-gpu.txt
  ```

- **For CPU (Without GPU acceleration):**
  ```bash
  pip install -r requirements-cpu.txt
  # or simply:
  pip install -r requirements.txt
  ```

### 3. Configure `.env` file
Create a `.env` file in the project root directory (or edit the existing one):

```ini
AI_PROVIDER=ollama
STAGE_ID=stage1_pedagogia
EMBEDDING_MODEL=nomic-embed-text
LLM_MODEL=llama3
LLM_TEMPERATURE=0.3
CHROMA_DIR=./db_vectorial
```

*(If you want to use OpenAI instead of Ollama, change `AI_PROVIDER=openai` and add `OPENAI_API_KEY=your_api_key`).*

---

## 🏁 How to Run the Application

Simply execute the unified launch script:

```bash
python start.py
```

The script will verify dependencies, launch the FastAPI backend, and automatically open the Streamlit interface in your browser:

- 🎨 **User Interface (Streamlit)**: `http://localhost:8501`
- ⚙️ **Backend API (FastAPI)**: `http://127.0.0.1:8000`
- 📑 **Interactive API Documentation**: `http://127.0.0.1:8000/docs`

---

## 📖 Application Usage Guide

1. **Register / Log In**:
   - Create a user account and select your role (`Student` or `Teacher`).
2. **Level Test (Students Only)**:
   - Click on **"🎯 Make Level Test"** in the sidebar to assess your English level. The bot will adapt future explanations to your level.
3. **Chat Management**:
   - Use **"➕ New Chat"** to start a clean session. Sessions are saved to history after the bot's first response.
   - Delete any conversation from the 3-dot menu `⋮`.

---

## 🛠️ Additional Tools

- **Download materials from Google Drive**:
  ```bash
  python descargar_drive.py
  ```
- **Generate or update embeddings in ChromaDB**:
  ```bash
  python crear_embeddings_locales.py
  ```
