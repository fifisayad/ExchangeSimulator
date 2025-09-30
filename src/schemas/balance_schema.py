from pydantic import BaseModel

from fifi.enums import Asset


class BalanceSchema(BaseModel):
    portfolio_id: str
    asset: Asset
    quantity: float
    available: float
    frozen: float


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
    fee_paid: float
