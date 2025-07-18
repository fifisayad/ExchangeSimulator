from pydantic import BaseModel

from src.enums.asset import Asset


class BalanceSchema(BaseModel):
    portfolio_id: str
    asset: Asset
    quantity: float
    available: float
    frozen: float
    leverage: float
