# backend/rutas/user.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.database.config import SessionLocal
from backend.modelos.user import User
from backend.modelos.portfolio import Portfolio  # Asegúrate de tener este modelo definido
from passlib.context import CryptContext
from pydantic import BaseModel, Field

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Dependencia para obtener la sesión de la base de datos
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Esquemas para usuarios
class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: str
    password: str = Field(..., min_length=6)

class UserLogin(BaseModel):
    email: str
    password: str

# Rutas para usuarios

@router.post("/register", status_code=status.HTTP_201_CREATED, response_model=dict)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    # Verificar si el usuario ya existe
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="El usuario ya está registrado")

    # Encriptar contraseña
    hashed_password = pwd_context.hash(user.password)

    # Crear usuario
    new_user = User(
        username=user.username,
        email=user.email,
        password=hashed_password,
        balance=10000.0  # Dinero ficticio inicial
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Crear portafolio para el usuario
    new_portfolio = Portfolio(user_id=new_user.id, btc_amount=0.0, current_value=0.0)
    db.add(new_portfolio)
    db.commit()

    return {"message": "Usuario registrado con éxito"}

@router.post("/login", response_model=dict)
def login(user: UserLogin, db: Session = Depends(get_db)):
    # Buscar usuario por email
    db_user = db.query(User).filter(User.email == user.email).first()
    if not db_user or not pwd_context.verify(user.password, db_user.password):
        raise HTTPException(status_code=401, detail="Credenciales inválidas")
    return {"message": "Inicio de sesión exitoso", "username": db_user.username}

@router.get("/{user_id}/balance", response_model=dict)
def get_balance(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return {"balance": user.balance}
