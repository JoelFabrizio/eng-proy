from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.rag_service import RAGService, SQLChatMessageHistory
from app.core.logging import logger
from app.core.security import get_current_user 
from app.db.models import User, ChatMessage
from app.db.database import get_db

router = APIRouter()
rag_service = RAGService()

@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(
    request: ChatRequest,
    current_user: User = Depends(get_current_user)
):
    """Endpoint para enviar preguntas al bot RAG especificando session_id."""
    try:
        respuesta = rag_service.ask(
            query=request.message, 
            user_id=current_user.id,
            session_id=request.session_id or "default",
            language=request.language or "Español"
        )
        return ChatResponse(
            response=respuesta,
            stage_id=request.stage_id
        )
    except Exception as e:
        logger.error(f"Error en endpoint /chat: {e}")
        raise HTTPException(status_code=500, detail="Error interno al procesar la consulta")

@router.get("/sessions")
async def get_user_sessions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtiene únicamente las sesiones que contienen al menos una respuesta del asistente."""
    records = (
        db.query(ChatMessage.session_id)
        .filter(ChatMessage.user_id == current_user.id, ChatMessage.role == "assistant")
        .distinct()
        .all()
    )
    sessions = [r[0] for r in records if r[0]]
    
    sessions_data = []
    for s_id in sessions:
        first_msg = (
            db.query(ChatMessage)
            .filter(ChatMessage.user_id == current_user.id, ChatMessage.session_id == s_id, ChatMessage.role == "user")
            .order_by(ChatMessage.id.asc())
            .first()
        )
        title = f"💬 {first_msg.content[:35]}..." if first_msg else "💬 Chat Guardado"
        sessions_data.append({"id": s_id, "title": title})

    return {"sessions": sessions_data}

@router.get("/history/{session_id}")
async def get_session_history(
    session_id: str,
    current_user: User = Depends(get_current_user)
):
    """Obtiene el historial de conversación para una sesión específica."""
    history = SQLChatMessageHistory(user_id=current_user.id, session_id=session_id)
    messages = [
        {"role": "user" if msg.type == "human" else "assistant", "content": msg.content}
        for msg in history.messages
    ]
    return {"messages": messages}

@router.delete("/history/{session_id}")
async def delete_session_history(
    session_id: str,
    current_user: User = Depends(get_current_user)
):
    """Borra el historial de una sesión específica."""
    history = SQLChatMessageHistory(user_id=current_user.id, session_id=session_id)
    history.clear()
    return {"message": f"Sesión '{session_id}' eliminada correctamente"}


