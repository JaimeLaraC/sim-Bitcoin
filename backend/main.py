from fastapi import FastAPI
from database.config import engine, Base
from rutas import user

app = FastAPI()

# Crear las tablas
Base.metadata.create_all(bind=engine)

# Registrar las rutas
app.include_router(user.router, prefix="/users", tags=["users"])

@app.get("/")
def root():
    return {"message": "¡Bienvenido a la bolsa de criptomonedas!"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
