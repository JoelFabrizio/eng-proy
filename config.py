from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    AI_PROVIDER: str = "ollama"
    STAGE_ID: str = "stage1_pedagogia"
    EMBEDDING_MODEL: str = "nomic-embed-text"
    LLM_MODEL: str = "llama3"
    LLM_TEMPERATURE: float = 0.3
    CHROMA_DIR: str = "./db_vectorial"

    class Config:
        env_file = ".env"
        # Permite ignorar variables extra en el .env si las hubiera

# Instancia global de configuración
settings = Settings()