from pydantic import BaseModel

# Schema para la respuesta del portafolio
class PortfolioResponse(BaseModel):
    user_id: int
    btc_amount: float
    current_value: float

    class Config:
        from_attributes = True

