from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.api import api_router
from app.core.logging import logger
from config import settings

from app.db.database import init_db
import app.db.models  # 👈 Registra los modelos (User, ChatMessage) en SQLAlchemy antes de crear las tablas

# Inicializamos la aplicación FastAPI
app = FastAPI(
    title="RAG Academic API",
    description="Backend modular para asistente académico RAG",
    version="1.0.0"
)

# 🗄️ Inicializar la Base de Datos al arrancar
init_db()

# 🌐 Configuración de CORS
origins = [
    "http://localhost",
    "http://localhost:3000",  # Frontend común (React, etc.)
    "http://127.0.0.1:8000",
    "*"                       # Permite cualquier origen en desarrollo
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Endpoint de comprobación de estado
@app.get("/health", tags=["Health Check"])
async def health_check():
    """Verifica que el servidor esté activo."""
    return {
        "status": "ok", 
        "provider": settings.AI_PROVIDER, 
        "stage": settings.STAGE_ID
    }

# Incluimos el router global de la API v1
app.include_router(api_router, prefix="/api/v1")

if __name__ == "__main__":
    import uvicorn
    logger.info("🚀 Iniciando Servidor Web con Uvicorn...")
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)