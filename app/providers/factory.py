import os
from app.providers.base import AIProvider
from config import settings
from app.core.logging import logger

def get_provider() -> AIProvider:
    """Decide y devuelve el proveedor de IA según la configuración."""
    provider_name = settings.AI_PROVIDER.lower()
    
    # Si se detecta una API key de nube (Gemini/OpenAI) y el proveedor por defecto es Ollama, conmutar automáticamente
    gemini_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    openai_key = os.getenv("OPENAI_API_KEY")

    if provider_name == "ollama" and (gemini_key or openai_key):
        if gemini_key:
            logger.info("⚡ API Key de Gemini detectada. Conmutando automáticamente el proveedor a 'gemini'.")
            provider_name = "gemini"
        elif openai_key:
            logger.info("⚡ API Key de OpenAI detectada. Conmutando automáticamente el proveedor a 'openai'.")
            provider_name = "openai"

    if provider_name == "openai":
        from app.providers.openai_provider import OpenAIProvider
        return OpenAIProvider()
    elif provider_name == "gemini":
        from app.providers.gemini_provider import GeminiProvider
        return GeminiProvider()
    elif provider_name == "ollama":
        from app.providers.ollama_provider import OllamaProvider
        return OllamaProvider()
    else:
        raise ValueError(f"Proveedor no soportado: {settings.AI_PROVIDER}")
    
