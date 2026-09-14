from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models import User
from app.core.security import verify_password, create_access_token

router = APIRouter()

@router.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    1. Busca al usuario en la base de datos por su username.
    2. Verifica que la contraseña coincida usando bcrypt.
    3. Genera y retorna el Token JWT si todo es correcto.
    """
    # 🔍 1. Buscar usuario en la base de datos
    user = db.query(User).filter(User.username == form_data.username).first()
    
    # ❌ 2. Validar usuario y contraseña
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 🔑 3. Crear el token JWT (incluimos sub=username y el rol)
    access_token = create_access_token(
        data={"sub": user.username, "role": user.role}
    )
    
    # 📦 4. Devolver el token firmado
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }