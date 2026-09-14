from app.providers.base import AIProvider
from app.providers.ollama_provider import OllamaProvider
from app.providers.openai_provider import OpenAIProvider
from config import settings

# La Factory (o Fábrica) es una función o clase que lee el archivo de configuración .env y, según el valor que encuentre ahí, decide cuál proveedor instanciar.

def get_provider() -> AIProvider:
    """Decide y devuelve el proveedor de IA según la configuración."""
    
    if settings.AI_PROVIDER.lower() == "openai":
        return OpenAIProvider()
    elif settings.AI_PROVIDER.lower() == "ollama":
        return OllamaProvider()
    elif settings.AI_PROVIDER.lower() == "gemini":
        from app.providers.gemini_provider import GeminiProvider
        return GeminiProvider()
    else:
        raise ValueError(f"Proveedor no soportado: {settings.AI_PROVIDER}")
    
