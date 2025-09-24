import httpx
import asyncio
import logging
from typing import Dict, Optional, Union, overload
from fastapi.encoders import jsonable_encoder
from fifi import RedisSubscriber, singleton

from ..enums.data_type import DataType
from ..schemas.subscritption_schema import SubscriptionRequestSchema
from ..common.exceptions import APIError
from ..enums.market import Market
from ..common.settings import Setting


LOGGER = logging.getLogger(__name__)


@singleton
class MarketMonitoringService:
    trades: Dict[Market, float]
    subscribers: Dict[Market, RedisSubscriber]

    def __init__(self):
        self.setting = Setting()
        self.trades = dict()
        self.subscribers = dict()

    async def start(self):
        if len(self.subscribers) > 0:
            return
        LOGGER.info("Monitoring Service initializing is started....")
        for market in self.setting.ACTIVE_MARKETS:
            channel = await self.subscribe(market=market, data_type=DataType.TRADES)
            self.subscribers[market] = await RedisSubscriber.create(channel=channel)
            self.trades[market] = -1
            while self.trades[market] == -1:
                await asyncio.sleep(0.5)
                await self.get_last_trade(market=market)

    async def subscribe(self, market: Market, data_type: DataType) -> str:
        url = f"{self.setting.MM_API_PATH}{self.setting.MM_SUBSCRIPTION_PATH}"
        subscritption_schema = SubscriptionRequestSchema(
            exchange=self.setting.MM_EXCHANGE, market=market, data_type=data_type
        )
        try:
            async with httpx.AsyncClient(
                timeout=httpx.Timeout(10.0, connect=5.0),
                transport=httpx.AsyncHTTPTransport(retries=3),
                headers={"Content-Type": "application/json"},
            ) as client:
                resp = await client.post(
                    url, json=jsonable_encoder(subscritption_schema)
                )
                resp.raise_for_status()
                return resp.json()["channel"]
        except Exception as e:
            raise APIError(f"Read position failed: {e}")

    @overload
    async def get_last_trade(self, market: Market) -> float: ...
    @overload
    async def get_last_trade(self, market: None = None) -> Dict[Market, float]: ...

    async def get_last_trade(
        self, market: Optional[Market] = None
    ) -> Union[Dict[Market, float], float]:
        """ """
        if market:
            last_trade = await self.subscribers[market].get_last_message()
            if last_trade:
                if last_trade["type"] == "trades":
                    self.trades[market] = last_trade["data"]["price"]
            return self.trades[market]
        for sub_market in self.subscribers:
            last_trade = await self.subscribers[sub_market].get_last_message()
            if last_trade:
                if last_trade["type"] == "trades":
                    self.trades[sub_market] = last_trade["data"]["price"]
        return self.trades
