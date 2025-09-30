from pydantic import BaseModel

from fifi.enums import Market


class LeverageSchema(BaseModel):
    portfolio_id: str
    market: Market
    leverage: float
