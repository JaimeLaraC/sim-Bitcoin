# backend/main.py

from fastapi import FastAPI
from backend.database.config import engine, Base
from backend.rutas import user, transaction, portfolio, auth  # Importaciones absolutas

# Importar modelos para asegurarse de que las tablas se crean
from backend.modelos import user as user_model, transaction as transaction_model, portfolio as portfolio_model

# Crear las tablas en la base de datos
Base.metadata.create_all(bind=engine)

app = FastAPI()

# Registrar las rutas
app.include_router(auth.router, tags=["Autenticación"])
app.include_router(user.router, prefix="/users", tags=["Usuarios"])
app.include_router(transaction.router, prefix="/users", tags=["Transacciones"])
app.include_router(portfolio.router, prefix="/users", tags=["Portafolio"])

@app.get("/")
def root():
    return {"message": "¡Bienvenido a la bolsa de criptomonedas!"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="127.0.0.1", port=8000, reload=True)
