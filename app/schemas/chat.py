from pydantic import BaseModel, Field
from typing import Optional

# Definimos la estructura exacta de los datos que van a entrar y salir a través de las peticiones HTTP. 
# De esto se encargan los esquemas de Pydantic (schemas)

class ChatRequest(BaseModel):
    """Modelo para la petición entrante del usuario."""
    message: str = Field(..., description="El mensaje o pregunta del usuario")
    session_id : Optional[str] = Field(default="default",description="ID de la sesión de chat")
    stage_id: Optional[str] = Field(default="stage1_pedagogia", description="Identificador de la sesión")
    language: Optional[str] = Field(default="Español", description="Idioma preferido para la respuesta")

class ChatResponse(BaseModel):
    """Modelo para la respuesta que devolverá la API."""
    response: str = Field(..., description="Respuesta generada por la IA")
    stage_id: str = Field(..., description="Stage utilizado para procesar la consulta")