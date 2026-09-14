from fastapi import APIRouter
from app.api.v1.endpoints import chat
from app.api.v1.endpoints import chat, auth

# Router principal de la API v1.
# Este archivo se encarga de agrupar todos los endpoints de la versión 1 de tu API.

api_router = APIRouter()

# Incluimos las rutas del módulo chat
api_router.include_router(auth.router, prefix="/auth", tags=["Autenticación"])

# Incluimos las rutas del modulo de autenticacion
api_router.include_router(chat.router, prefix="/rag", tags=["Chat RAG"])