from typing import Any, Dict, Literal, Optional, Union, overload
from fifi import RedisSubscriber, singleton, GetLogger

from ..enums.market import Market
from ..common.settings import Setting


LOGGER = GetLogger().get()


@singleton
class MarketMonitoringService:
    def __init__(self):
        self.trades: Dict[Market, float] = dict()
        LOGGER.info("Monitoring Service initializing is started....")
        self.start()

    def start(self):
        for market in Setting().ACTIVE_MARKETS:
            # TODO: implement monitoring connection flow
            pass

    @overload
    def get_last_trade(self, market: Market) -> float: ...
    @overload
    def get_last_trade(self, market: None = None) -> Dict[Market, float]: ...

    def get_last_trade(
        self, market: Optional[Market] = None
    ) -> Union[Dict[Market, float], float]:
        """ """
        if market:
            return self.trades[market]
        return self.trades
