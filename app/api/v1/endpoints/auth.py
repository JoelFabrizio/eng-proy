from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from app.schemas.auth import LoginRequest, RegisterRequest, LoginResponse, UpdateLevelRequest
from app.core.logging import logger
from app.db.database import get_db
from app.db.models import User
from app.core.security import verify_password, hash_password, create_access_token, get_current_user

router = APIRouter()

# ---------------------------------------------------------
# 1. Endpoint de Registro (/register)
# ---------------------------------------------------------
@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(credentials: RegisterRequest, db: Session = Depends(get_db)):
    """Registra un nuevo usuario guardando su rol y contraseña encriptada en SQLite."""
    
    # Validar si el usuario ya existe
    existing_user = db.query(User).filter(User.username == credentials.username).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El nombre de usuario ya está registrado"
        )
    
    # Validar y asignar el rol
    user_role = credentials.role.lower().strip()
    if user_role not in ["alumno", "profesor"]:
        user_role = "alumno"

    # Crear hash de la contraseña
    hashed_pwd = hash_password(credentials.password)
    
    # Crear el nuevo objeto de usuario
    new_user = User(
        username=credentials.username,
        hashed_password=hashed_pwd,
        role=user_role
    )
    
    # Guardar en SQLite
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    logger.info(f"👤 Nuevo usuario registrado: {new_user.username} (Rol: {new_user.role})")
    return {"message": "Usuario creado con éxito", "username": new_user.username, "role": new_user.role}


# ---------------------------------------------------------
# 2. Endpoint de Login (/login)
# ---------------------------------------------------------
@router.post("/login", response_model=LoginResponse)
async def login(credentials: LoginRequest, db: Session = Depends(get_db)):
    """Autentica un usuario comprobando el hash y genera un Token JWT real."""
    
    user = db.query(User).filter(User.username == credentials.username).first()
    
    if not user or not verify_password(credentials.password, user.hashed_password):
        logger.warning(f"⚠️ Intento fallido de inicio de sesión para: {credentials.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas"
        )
    
    logger.info(f"🔑 Usuario '{user.username}' autenticado con éxito.")
    
    # ✅ Generamos un token JWT firmado real con el username dentro del campo 'sub'
    token_jwt = create_access_token(data={"sub": user.username})
    user_level = getattr(user, "english_level", "sin_evaluar") or "sin_evaluar"
    
    return LoginResponse(
        access_token=token_jwt,
        role=user.role,
        english_level=user_level,
        message="Autenticación exitosa"
    )

# ---------------------------------------------------------
# 3. Endpoint para Actualizar Nivel de Inglés (/level)
# ---------------------------------------------------------
@router.put("/level")
async def update_english_level(
    payload: UpdateLevelRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Actualiza el nivel de inglés del usuario autenticado en SQLite."""
    new_level = payload.level.strip().upper()
    current_user.english_level = new_level
    db.add(current_user)
    db.commit()
    db.refresh(current_user)
    logger.info(f"🎯 Nivel de inglés de '{current_user.username}' actualizado a: {new_level}")
    return {"message": "Nivel de inglés actualizado con éxito", "english_level": new_level}
