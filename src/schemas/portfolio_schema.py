from pydantic import BaseModel
from ..common.settings import Setting


class PortfolioSchema(BaseModel):
    name: str


class PortfolioResponseSchema(BaseModel):
    id: str
    name: str
    spot_taker_fee: float = Setting().DEFAULT_SPOT_TAKER_FEE
    spot_maker_fee: float = Setting().DEFAULT_SPOT_MAKER_FEE
    perp_taker_fee: float = Setting().DEFAULT_PERP_TAKER_FEE
    perp_maker_fee: float = Setting().DEFAULT_PERP_MAKER_FEE

    class Config:
        orm_mode = True
