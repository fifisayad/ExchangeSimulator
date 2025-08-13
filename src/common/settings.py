from typing import Annotated
from dotenv import load_dotenv
from fifi import singleton
from pydantic import field_validator
from pydantic_settings import BaseSettings, NoDecode
from ..enums.market import Market
from ..enums.exchange import Exchange


@singleton
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

    # API Endpoints Settings
    API_PREFIX: str = "exapi"
    API_VERSION: str = "v1"

    # Market Monitoring Settings
    MM_API_PATH: str = "localhost:3456/"
    MM_SUBSCRIPTION_PATH: str = "subscribe/"
    MM_EXCHANGE: Exchange = Exchange.HYPERLIQUID

    # Logs Path
    EXCEPTION_LOGS_PATH: str = "./logs/"
