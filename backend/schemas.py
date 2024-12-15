# backend/schemas.py

from pydantic import BaseModel, Field, EmailStr
from typing import Literal, List
from datetime import datetime
from enum import Enum
from pydantic import ConfigDict

# Enumeración para tipos de transacción
class TransactionType(str, Enum):
    buy = "buy"
    sell = "sell"

# Esquema para la creación de usuarios
class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=6)

    model_config = ConfigDict(from_attributes=True)  # Configuración para Pydantic V2

# Esquema para el inicio de sesión de usuarios
class UserLogin(BaseModel):
    email: EmailStr
    password: str

    model_config = ConfigDict(from_attributes=True)

# Esquema para la respuesta de usuarios
class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    balance: float

    model_config = ConfigDict(from_attributes=True)

# Esquema para la creación de transacciones
class TransactionCreate(BaseModel):
    transaction_type: TransactionType  # Renombrado de 'type' a 'transaction_type' para evitar conflictos
    amount: float = Field(..., gt=0, description="Cantidad de Bitcoin")
    price: float = Field(..., gt=0, description="Precio actual de Bitcoin")

    model_config = ConfigDict(from_attributes=True)

# Esquema para la respuesta de transacciones
class TransactionResponse(BaseModel):
    id: int
    user_id: int
    transaction_type: TransactionType
    amount: float
    price: float
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)

# Esquema para la respuesta del portafolio
class PortfolioResponse(BaseModel):
    user_id: int
    btc_amount: float
    current_value: float

    model_config = ConfigDict(from_attributes=True)
