from pydantic import BaseModel

from src.enums.market import Market


class LeverageSchema(BaseModel):
    portfolio_id: str
    market: Market
    leverage: float
