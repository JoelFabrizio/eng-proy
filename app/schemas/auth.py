from pydantic import BaseModel, Field

# Esquema de validación para el inicio de sesión y la ruta que procesará las credenciales.

class LoginRequest(BaseModel):
    """Esquema para las credenciales de entrada."""
    username: str = Field(..., example="admin")
    password: str = Field(..., example="123456")

class RegisterRequest(BaseModel):
    """Esquema para el registro de nuevos usuarios con rol."""
    username: str = Field(..., example="admin")
    password: str = Field(..., example="123456")
    role: str = Field("alumno", example="alumno")  # alumno o profesor

class UpdateLevelRequest(BaseModel):
    """Esquema para actualizar el nivel de inglés del usuario."""
    level: str = Field(..., example="B1")

class LoginResponse(BaseModel):
    """Esquema para la respuesta tras un login exitoso."""
    access_token: str
    token_type: str = "bearer"
    role: str = "alumno"
    english_level: str = "sin_evaluar"
    message: str