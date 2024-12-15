from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.database.config import get_db
from backend.modelos.portfolio import Portfolio
from backend.schemas import PortfolioResponse

router = APIRouter()

# Ruta para obtener el portafolio de un usuario
@router.get("/portfolio/{user_id}", response_model=PortfolioResponse)
def get_portfolio(user_id: int, db: Session = Depends(get_db)):
    portfolio = db.query(Portfolio).filter(Portfolio.user_id == user_id).first()
    if not portfolio:
        raise HTTPException(status_code=404, detail="Portafolio no encontrado")
    return portfolio

# Ruta para actualizar el portafolio de un usuario
@router.put("/portfolio/{user_id}", response_model=PortfolioResponse)
def update_portfolio(user_id: int, btc_amount: float, current_value: float, db: Session = Depends(get_db)):
    portfolio = db.query(Portfolio).filter(Portfolio.user_id == user_id).first()
    if not portfolio:
        raise HTTPException(status_code=404, detail="Portafolio no encontrado")
    portfolio.btc_amount = btc_amount
    portfolio.current_value = current_value
    db.commit()
    db.refresh(portfolio)
    return portfolio
