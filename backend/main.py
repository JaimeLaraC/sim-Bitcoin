from fastapi import FastAPI
from database.config import engine, Base

# Importa los modelos para registrarlos
from modelos.user import User
from modelos.transaction import Transaction

app = FastAPI()

# Crea las tablas en la base de datos
Base.metadata.create_all(bind=engine)

@app.get("/")
def root():
    return {"message": "¡Bienvenido a la bolsa de criptomonedas!"}
