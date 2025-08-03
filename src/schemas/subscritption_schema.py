from pydantic import BaseModel

from ..enums.market import Market
from ..enums.data_type import DataType
from ..enums.exchange import Exchange


class SubscriptionRequestSchema(BaseModel):
    exchange: Exchange
    market: Market
    data_type: DataType


class SubscriptionResponseSchema(BaseModel):
    channel: str
