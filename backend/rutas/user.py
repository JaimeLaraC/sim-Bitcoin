from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database.config import SessionLocal
from modelos.user import User
from modelos.transaction import Transaction
from passlib.context import CryptContext
from pydantic import BaseModel
from datetime import datetime

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# Dependencia para obtener la sesión de la base de datos
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Esquemas para usuarios y transacciones
class UserCreate(BaseModel):
    username: str
    email: str
    password: str


class UserLogin(BaseModel):
    email: str
    password: str


# Rutas

# Registrar usuario
@router.post("/register")
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
    return {"message": "Usuario registrado con éxito"}


# Iniciar sesión
@router.post("/login")
def login(user: UserLogin, db: Session = Depends(get_db)):
    # Buscar usuario por email
    db_user = db.query(User).filter(User.email == user.email).first()
    if not db_user or not pwd_context.verify(user.password, db_user.password):
        raise HTTPException(status_code=401, detail="Credenciales inválidas")
    return {"message": "Inicio de sesión exitoso", "username": db_user.username}


# Consultar balance
@router.get("/{user_id}/balance")
def get_balance(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return {"balance": user.balance}


# Realizar transacción (compra/venta)
@router.post("/{user_id}/transaction")
def make_transaction(user_id: int, transaction: dict, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    # Validar datos de la transacción
    transaction_type = transaction.get("type")  # "buy" o "sell"
    amount = transaction.get("amount")         # Cantidad de Bitcoin
    price = transaction.get("price")           # Precio actual de Bitcoin

    if transaction_type not in ["buy", "sell"]:
        raise HTTPException(status_code=400, detail="Transacción inválida")

    total_cost = amount * price

    # Validar balance o cantidad
    if transaction_type == "buy" and user.balance < total_cost:
        raise HTTPException(status_code=400, detail="Fondos insuficientes")
    elif transaction_type == "sell" and amount > 0:  # Nota: Aún no rastreamos Bitcoin
        raise HTTPException(status_code=400, detail="No tienes suficientes Bitcoin para vender")

    # Actualizar balance y registrar transacción
    if transaction_type == "buy":
        user.balance -= total_cost
    elif transaction_type == "sell":
        user.balance += total_cost

    # Registrar la transacción
    new_transaction = Transaction(
        user_id=user.id,
        transaction_type=transaction_type,
        amount=amount,
        price=price,
        timestamp=datetime.utcnow()
    )
    db.add(new_transaction)
    db.commit()
    db.refresh(user)

    return {"message": f"Transacción {transaction_type} completada", "new_balance": user.balance}
