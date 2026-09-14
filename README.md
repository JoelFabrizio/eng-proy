# 🎓 Asistente Académico RAG de Inglés

🌐 **[English Version](README_EN.md)** | **[Versión en Español](README.md)**

¡Bienvenido al **Asistente Académico RAG**! Este proyecto es una solución integral basada en **Generación Aumentada por Recuperación (RAG)** que actúa como Tutor Académico de Inglés para alumnos y Mentor Pedagógico para profesores.

---

## 🌟 Características Principales

- **Rol Dual (Alumno / Profesor)**:
  - **👨‍🎓 Modo Alumno**: Enfocado en el aprendizaje del idioma inglés, práctica de gramática, vocabulario y lectura. Filtra estrictamente cualquier material docente.
  - **👨‍🏫 Modo Profesor**: Enfocado en metodologías de enseñanza ELT, planificación de clases y didáctica.
- **🎯 Test de Diagnóstico de Nivel de Inglés (A1 - C1)**:
  - Evaluación interactiva adaptativa. El tutor RAG determina el nivel del alumno según el Marco Común Europeo (MCER) y ajusta dinámicamente la complejidad de sus explicaciones.
- **📜 Historial de Chats Persistente**:
  - Almacenamiento seguro en SQLite. Mantiene la conversación activa y permite gestionar múltiples sesiones de chat.
- **📚 Base Vectorial Multicategoría (ChromaDB)**:
  - Búsqueda por similitud semántica con Embeddings de Hugging Face (`BAAI/bge-small-en-v1.5`).
- **🦙 Soporte para Ollama y OpenAI**:
  - Configurable fácilmente mediante variables de entorno (`.env`).

---

## 📁 Estructura del Proyecto

```text
├── app/
│   ├── api/                  # Endpoints FastAPI (Auth, Chat, Sesiones)
│   ├── core/                 # Seguridad (JWT, Bcrypt) y Logging
│   ├── db/                   # Base de datos SQLite y modelos SQLAlchemy
│   ├── providers/            # Fábrica de Proveedores de IA (Ollama / OpenAI)
│   ├── schemas/              # Modelos de validación Pydantic
│   └── services/             # Servicio RAG, Prompts Duales e Historial SQL
├── db_vectorial/             # Base de datos vectorial persistente (ChromaDB)
├── app_ui.py                 # Interfaz gráfica interactiva en Streamlit
├── config.py                 # Configuración de variables del sistema
├── main.py                   # Punto de entrada del servidor FastAPI
├── start.py                  # Script de inicio unificado (Backend + Frontend)
├── crear_embeddings_locales.py # Script para procesar documentos y poblar ChromaDB
├── descargar_drive.py        # Script para descargar material desde Google Drive
├── requirements-cpu.txt      # Requerimientos para ejecución en CPU
├── requirements-gpu.txt      # Requerimientos optimizados para GPU (CUDA 13.0)
├── docker-compose.yml        # Configuración de Docker Compose
└── README.md                 # Documentación del proyecto
```

---

## 🛠️ Requisitos Previos

1. **Python 3.10+** (Recomendado Python 3.10 o 3.11).
2. **Ollama** instalado en tu sistema si usas el proveedor local:
   ```bash
   ollama pull llama3
   ollama pull nomic-embed-text
   ```

---

## 🚀 Instalación y Configuración

### 1. Clonar el repositorio y crear un entorno virtual
```bash
# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
# En Windows (PowerShell):
.\venv\Scripts\Activate.ps1
# En Linux / macOS:
source venv/bin/activate
```

### 2. Instalar dependencias

Elige la versión correspondiente a tu hardware:

- **Para GPU (NVIDIA CUDA 13.0):**
  ```bash
  pip install -r requirements-gpu.txt
  ```

- **Para CPU (Sin aceleración por tarjeta gráfica):**
  ```bash
  pip install -r requirements-cpu.txt
  # o simplemente:
  pip install -r requirements.txt
  ```

### 3. Configurar el archivo `.env`
Crea un archivo `.env` en la raíz del proyecto (o edita el existente):

```ini
AI_PROVIDER=ollama
STAGE_ID=stage1_pedagogia
EMBEDDING_MODEL=nomic-embed-text
LLM_MODEL=llama3
LLM_TEMPERATURE=0.3
CHROMA_DIR=./db_vectorial
```

*(Si deseas usar OpenAI en lugar de Ollama, cambia `AI_PROVIDER=openai` y añade `OPENAI_API_KEY=tu_api_key`).*

---

## 🏁 Cómo Ejecutar la Aplicación

Simplemente ejecuta el script de inicio unificado:

```bash
python start.py
```

El script verificará el estado de las dependencias, lanzará el backend FastAPI y abrirá automáticamente la interfaz de Streamlit en tu navegador:

- 🎨 **Interfaz de Usuario (Streamlit)**: `http://localhost:8501`
- ⚙️ **Backend API (FastAPI)**: `http://127.0.0.1:8000`
- 📑 **Documentación interactiva de la API**: `http://127.0.0.1:8000/docs`

---

## 📖 Guía de Uso de la Aplicación

1. **Registro / Inicio de Sesión**:
   - Crea un usuario e indica tu rol (`Alumno` o `Profesor`).
2. **Test de Nivel (Solo Alumnos)**:
   - Haz clic en **"🎯 Hacer Test de Nivel"** en la barra lateral para evaluar tu nivel de inglés. El bot adaptará sus futuras explicaciones al nivel evaluado.
3. **Gestión de Chats**:
   - Utiliza **"➕ Nuevo Chat"** para iniciar una consulta limpia. Las sesiones solo se guardarán en tu historial tras la primera respuesta del bot.
   - Puedes eliminar cualquier conversación desde el menú de 3 puntos `⋮`.

---

## 🛠️ Herramientas Complementarias

- **Descargar material desde Google Drive**:
  ```bash
  python descargar_drive.py
  ```
- **Generar o actualizar embeddings en ChromaDB**:
  ```bash
  python crear_embeddings_locales.py
  ```
