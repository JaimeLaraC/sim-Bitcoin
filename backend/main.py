from fastapi import FastAPI
from backend.database.config import engine, Base  # Importación absoluta
from backend.rutas import user, transaction, portfolio  # Importación absoluta

# Importa los modelos para asegurarte de que las tablas se crean
from backend.modelos import user as user_model, transaction as transaction_model, portfolio as portfolio_model

app = FastAPI()

# Crear las tablas
Base.metadata.create_all(bind=engine)

# Registrar las rutas
app.include_router(user.router, prefix="/users", tags=["users"])
app.include_router(transaction.router, prefix="/transactions", tags=["transactions"])
app.include_router(portfolio.router, prefix="/portfolio", tags=["portfolio"])

@app.get("/")
def root():
    return {"message": "¡Bienvenido a la bolsa de criptomonedas!"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="127.0.0.1", port=8000, reload=True)