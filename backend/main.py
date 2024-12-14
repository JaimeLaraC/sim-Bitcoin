from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def root():
    return {"message": "¡Bienvenido a la bolsa de criptomonedas!"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
