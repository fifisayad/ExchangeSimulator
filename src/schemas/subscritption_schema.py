from pydantic import BaseModel

from fifi.enums import Exchange, DataType, Market


class SubscriptionRequestSchema(BaseModel):
    exchange: Exchange
    market: Market
    data_type: DataType


class SubscriptionResponseSchema(BaseModel):
    channel: str
