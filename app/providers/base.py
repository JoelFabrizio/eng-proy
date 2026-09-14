from abc import ABC, abstractmethod
from typing import Any, List

# Usamos el módulo nativo abc (Abstract Base Classes) de Python para definir qué métodos está obligado a implementar cualquier modelo que agreguemos en el futuro.

class AIProvider(ABC):
    """Interfaz abstracta para proveedores de IA."""
    
    @abstractmethod
    def get_llm(self) -> Any:
        """Devuelve la instancia del modelo de lenguaje (LLM)."""
        pass
        

    @abstractmethod
    def get_embeddings(self) -> Any:
        """Devuelve la instancia del modelo de embeddings."""
        pass