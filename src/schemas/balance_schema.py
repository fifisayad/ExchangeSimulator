from pydantic import BaseModel

from src.enums.asset import Asset


class BalanceSchema(BaseModel):
    portfolio_id: str
    asset: Asset
    quantity: float
    available: float
    frozen: float
    leverage: float


class BalanceReadSchema(BaseModel):
    portfolio_id: str
    id: str | None = None
    asset: Asset | None = None


class BalanceDepositSchema(BaseModel):
    portfolio_id: str
    asset: Asset
    quantity: float


class BalanceResponseSchema(BaseModel):
    id: str
    portfolio_id: str
    asset: Asset
    quantity: float
    available: float
    frozen: float
    burned: float
    leverage: float

    class Config:
        orm_mode = True
