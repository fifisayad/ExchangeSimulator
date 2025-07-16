from typing import Annotated
from dotenv import load_dotenv
from pydantic import field_validator
from pydantic_settings import BaseSettings, NoDecode
from ..enums.market import Market


class Setting(BaseSettings):
    def __init__(self):
        load_dotenv()
        super().__init__()

    active_markets: Annotated[list[Market], NoDecode]

    @field_validator("active_markets", mode="before")
    @classmethod
    def decode_active_markets(cls, v: str) -> list[Market]:
        return [Market[x] for x in v.split(",")]
