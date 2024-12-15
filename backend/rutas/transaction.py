# backend/rutas/transaction.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.database.config import SessionLocal
from backend.modelos.transaction import Transaction
from backend.modelos.user import User
from backend.modelos.portfolio import Portfolio
from backend.schemas import TransactionCreate, TransactionResponse
from datetime import datetime
from typing import List

router = APIRouter()

# Dependencia para obtener la sesión de la base de datos
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Crear una transacción
@router.post("/{user_id}/transaction", response_model=TransactionResponse, status_code=status.HTTP_201_CREATED)
def create_transaction(user_id: int, transaction: TransactionCreate, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    total_cost = transaction.amount * transaction.price

    # Buscar o crear el portafolio del usuario
    portfolio = db.query(Portfolio).filter(Portfolio.user_id == user.id).first()
    if not portfolio:
        portfolio = Portfolio(user_id=user.id, btc_amount=0.0, current_value=0.0)
        db.add(portfolio)
        db.commit()
        db.refresh(portfolio)

    # Validar la transacción
    if transaction.transaction_type == "buy":
        if user.balance < total_cost:
            raise HTTPException(status_code=400, detail="Fondos insuficientes")
        user.balance -= total_cost
        portfolio.btc_amount += transaction.amount
    elif transaction.transaction_type == "sell":
        if portfolio.btc_amount < transaction.amount:
            raise HTTPException(status_code=400, detail="Saldo BTC insuficiente")
        user.balance += total_cost
        portfolio.btc_amount -= transaction.amount
    else:
        raise HTTPException(status_code=400, detail="Tipo de transacción inválido")

    # Actualizar el valor actual del portafolio
    portfolio.current_value = portfolio.btc_amount * transaction.price

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
    db.refresh(new_transaction)
    db.refresh(user)
    db.refresh(portfolio)

    return new_transaction  # FastAPI usará el response_model para serializarlo

# Consultar historial de transacciones
@router.get("/{user_id}/transactions", response_model=List[TransactionResponse], status_code=status.HTTP_200_OK)
def get_transactions(user_id: int, db: Session = Depends(get_db)):
    transactions = db.query(Transaction).filter(Transaction.user_id == user_id).all()
    if not transactions:
        raise HTTPException(status_code=404, detail="No se encontraron transacciones")
    return transactions  # FastAPI usará el response_model para serializarlas
