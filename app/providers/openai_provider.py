# app/providers/openai_provider.py
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from app.providers.base import AIProvider
from config import settings

# Si quisi
# eramos tener otro proveedor, en este caso openAI, solo tendrías que crear un nuevo módulo, por ejemplo app/providers/openai_provider.py, 
# e implementar la clase OpenAIProvider respetando los mismos métodos (get_llm y get_embeddings).

# Lo más potente de este diseño es que todo el resto del sistema (el servicio de RAG, el historial y el archivo principal) no cambia en lo absoluto, porque solo dependen de la interfaz AIProvider.

class OpenAIProvider(AIProvider):
    """Implementación concreta para OpenAI."""
    
    def __init__(self):
        self._llm = ChatOpenAI(
            model="gpt-4o",
            temperature=settings.LLM_TEMPERATURE,
            api_key=settings.OPENAI_API_KEY
        )
        self._embeddings = OpenAIEmbeddings(
            model="text-embedding-3-small",
            api_key=settings.OPENAI_API_KEY
        )

    def get_llm(self) -> ChatOpenAI:
        return self._llm

    def get_embeddings(self) -> OpenAIEmbeddings:
        return self._embeddings