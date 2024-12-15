# tests/test_auth.py

import pytest
import pytest_asyncio
from httpx import AsyncClient
from backend.main import app
from backend.database.config import SessionLocal, Base, engine
from backend.modelos.user import User
from backend.modelos.portfolio import Portfolio
from backend.modelos.transaction import Transaction
from passlib.context import CryptContext

# Ignorar advertencias de deprecación temporalmente (Opcional)
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

# Fixture para configurar la base de datos de pruebas
@pytest_asyncio.fixture(scope="module")
async def setup_db_auth():
    # Crear las tablas
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    
    # Crear un usuario de prueba único
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    hashed_password = pwd_context.hash("123456")
    test_user = User(
        username="testuser_auth", 
        email="test_auth@example.com", 
        password=hashed_password, 
        balance=10000.0
    )
    db.add(test_user)
    db.commit()
    db.refresh(test_user)
    
    # Crear portafolio para el usuario
    test_portfolio = Portfolio(
        user_id=test_user.id, 
        btc_amount=0.0, 
        current_value=0.0
    )
    db.add(test_portfolio)
    db.commit()
    
    yield {"user": test_user, "portfolio": test_portfolio}
    
    # Limpiar la base de datos después de las pruebas
    db.query(Transaction).delete()
    db.query(Portfolio).delete()
    db.query(User).delete()
    db.commit()
    db.close()
    Base.metadata.drop_all(bind=engine)

# Fixture para el cliente de pruebas (asíncrono)
@pytest_asyncio.fixture
async def async_client_fixture_auth(setup_db_auth):
    async with AsyncClient(app=app, base_url="http://testserver") as ac:
        yield ac

@pytest.mark.asyncio
async def test_login_success(async_client_fixture_auth, setup_db_auth):
    user = setup_db_auth["user"]
    response = await async_client_fixture_auth.post(
        "/auth/token",
        data={"username": user.email, "password": "123456"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

@pytest.mark.asyncio
async def test_login_invalid_credentials(async_client_fixture_auth):
    response = await async_client_fixture_auth.post(
        "/auth/token",
        data={"username": "fake@example.com", "password": "wrong"}
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Correo o contraseña incorrectos"

@pytest.mark.asyncio
async def test_protected_route_no_token(async_client_fixture_auth):
    response = await async_client_fixture_auth.get("/users/me")
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"

@pytest.mark.asyncio
async def test_protected_route_invalid_token(async_client_fixture_auth):
    response = await async_client_fixture_auth.get(
        "/users/me",
        headers={"Authorization": "Bearer invalid_token"}
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Token inválido"
