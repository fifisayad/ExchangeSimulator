from typing import Annotated
from dotenv import load_dotenv
from pydantic import field_validator
from pydantic_settings import BaseSettings, NoDecode
from ..enums.market import Market


class Setting(BaseSettings):
    def __init__(self):
        load_dotenv()
        super().__init__()

    ACTIVE_MARKETS: Annotated[list[Market], NoDecode]

    @field_validator("ACTIVE_MARKETS", mode="before")
    @classmethod
    def decode_active_markets(cls, v: str) -> list[Market]:
        return [Market[x] for x in v.split(",")]

    DEFAULT_SPOT_MAKER_FEE: float
    DEFAULT_SPOT_TAKER_FEE: float
    DEFAULT_PERP_MAKER_FEE: float
    DEFAULT_PERP_TAKER_FEE: float
