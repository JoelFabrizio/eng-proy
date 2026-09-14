import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_huggingface import HuggingFaceEmbeddings
from app.providers.base import AIProvider
from config import settings

class GeminiProvider(AIProvider):
    """Implementación concreta para Google Gemini en la nube (Gratuito)."""
    
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("⚠️ No se encontró GEMINI_API_KEY en las variables de entorno.")
        
        # Determinar modelo (por defecto gemini-1.5-flash)
        model_name = settings.LLM_MODEL if "gemini" in settings.LLM_MODEL.lower() else "gemini-1.5-flash"
        
        self._llm = ChatGoogleGenerativeAI(
            model=model_name,
            temperature=settings.LLM_TEMPERATURE,
            google_api_key=api_key
        )
        
        # Embeddings en CPU (Hugging Face)
        self._embeddings = HuggingFaceEmbeddings(
            model_name="BAAI/bge-small-en-v1.5"
        )

    def get_llm(self) -> ChatGoogleGenerativeAI:
        return self._llm

    def get_embeddings(self) -> HuggingFaceEmbeddings:
        return self._embeddings
