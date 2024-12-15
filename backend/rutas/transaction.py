from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.database.config import SessionLocal
from backend.modelos.transaction import Transaction
from modelos.user import User
from pydantic import BaseModel
from datetime import datetime

router = APIRouter()

# Dependencia para obtener la sesión de la base de datos
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Modelo de transacción
class TransactionCreate(BaseModel):
    transaction_type: str  # "buy" o "sell"
    amount: float
    price: float

# Crear una transacción
@router.post("/transaction", status_code=status.HTTP_201_CREATED)
def create_transaction(user_id: int, transaction: TransactionCreate, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    total_cost = transaction.amount * transaction.price

    # Validar la transacción
    if transaction.transaction_type == "buy":
        if user.balance < total_cost:
            raise HTTPException(status_code=400, detail="Fondos insuficientes")
        user.balance -= total_cost
    elif transaction.transaction_type == "sell":
        # Aquí se debe agregar una lógica para verificar el saldo en Bitcoin
        user.balance += total_cost
    else:
        raise HTTPException(status_code=400, detail="Tipo de transacción inválido")

    # Registrar la transacción
    new_transaction = Transaction(
        user_id=user.id,
        transaction_type=transaction.transaction_type,
        amount=transaction.amount,
        price=transaction.price,
        timestamp=datetime.utcnow()
    )
    db.add(new_transaction)
    db.commit()
    db.refresh(user)

    return {"message": f"Transacción {transaction.transaction_type} completada", "new_balance": user.balance}

# Consultar historial de transacciones
@router.get("/transactions", status_code=status.HTTP_200_OK)
def get_transactions(user_id: int, db: Session = Depends(get_db)):
    transactions = db.query(Transaction).filter(Transaction.user_id == user_id).all()
    if not transactions:
        raise HTTPException(status_code=404, detail="No se encontraron transacciones")
    return transactions
