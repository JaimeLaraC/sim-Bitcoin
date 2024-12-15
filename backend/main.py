# backend/main.py

from fastapi import FastAPI
from backend.database.config import engine, Base

# Definir metadatos para la documentación
tags_metadata = [
    {
        "name": "Autenticación",
        "description": "Operaciones relacionadas con el inicio de sesión y la autenticación."
    },
    {
        "name": "Usuarios",
        "description": "Operaciones relacionadas con usuarios: creación y gestión."
    },
    {
        "name": "Transacciones",
        "description": "Manejo de transacciones de criptomonedas."
    },
    {
        "name": "Portafolio",
        "description": "Gestión de portafolios de usuarios."
    },
    {
        "name": "General",
        "description": "Rutas generales para comprobaciones de salud."
    }
]

# Crear la aplicación de FastAPI
app = FastAPI(
    title="API de Simulación de Bolsa de Criptomonedas",
    description="API para manejar usuarios, transacciones y portafolios.",
    version="1.0.0",
    openapi_tags=tags_metadata
)

# Crear las tablas en la base de datos
Base.metadata.create_all(bind=engine)

# Importar routers después de definir app para evitar importaciones circulares
from backend.rutas import user, transaction, portfolio, auth  # Importaciones absolutas

# Registrar las rutas
app.include_router(auth.router, tags=["Autenticación"])
app.include_router(user.router, prefix="/users", tags=["Usuarios"])
app.include_router(transaction.router, prefix="/transactions", tags=["Transacciones"])
app.include_router(portfolio.router, prefix="/portfolios", tags=["Portafolio"])

@app.get("/", tags=["General"])
def root():
    """
    Mensaje de bienvenida a la aplicación.
    """
    return {"message": "¡Bienvenido a la bolsa de criptomonedas!"}

@app.get("/health", tags=["General"])
def health_check():
    """
    Comprobación del estado de la aplicación.
    """
    return {"status": "OK"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="127.0.0.1", port=8000, reload=True)
