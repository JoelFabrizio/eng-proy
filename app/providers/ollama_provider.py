from langchain_ollama import ChatOllama, OllamaEmbeddings
from app.providers.base import AIProvider
from config import settings

# creamos la clase específica para Ollama, conectándola con la configuración de config.py

class OllamaProvider(AIProvider):
    """Implementación concreta para Ollama."""
    
    def __init__(self):
        self._llm = ChatOllama(
            model=settings.LLM_MODEL,
            temperature=settings.LLM_TEMPERATURE
        )
        self._embeddings = OllamaEmbeddings(
            model=settings.EMBEDDING_MODEL
        )

    def get_llm(self) -> ChatOllama:
        return self._llm

    def get_embeddings(self) -> OllamaEmbeddings:
        return self._embeddings