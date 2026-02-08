"""
Controlador para el endpoint del chatbot
"""
import logging
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from graphmap.domain.services.chatbot_service import ChatbotService

logger = logging.getLogger(__name__)

# Crear router
router = APIRouter(
    prefix="/chat",
    tags=["chatbot"],
    responses={404: {"description": "Not found"}},
)

# Instanciar servicio
chatbot_service = ChatbotService()


class ChatMessage(BaseModel):
    """Modelo para mensajes de chat"""
    role: str
    content: str


class ChatRequest(BaseModel):
    """Modelo para solicitud de chat"""
    message: str
    conversation_history: Optional[List[Dict]] = Field(default_factory=list)


class ChatResponse(BaseModel):
    """Modelo para respuesta de chat"""
    response: str
    conversation_history: List[Dict]
    tool_used: bool


@router.post("/", response_model=ChatResponse)
async def chat_with_bot(request: ChatRequest):
    """
    Endpoint para chatear con el bot sobre el grafo
    """
    try:
        result = chatbot_service.chat(
            user_message=request.message,
            conversation_history=request.conversation_history
        )

        return ChatResponse(
            response=result["response"],
            conversation_history=result["conversation_history"],
            tool_used=result["tool_used"]
        )

    except RuntimeError:
        logger.exception("Chat processing failed")
        raise HTTPException(
            status_code=503,
            detail="Chat service is not configured"
        )
    except Exception:
        logger.exception("Chat processing failed")
        raise HTTPException(
            status_code=500,
            detail="Error processing chat"
        )
