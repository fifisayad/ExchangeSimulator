from typing import Any, Dict, Optional
from fifi import RedisSubscriber, singleton, GetLogger

from ..enums.market import Market
from ..common.settings import Setting


LOGGER = GetLogger().get()


@singleton
class MarketMonitoringService:
    def __init__(self):
        self.trades: Dict[Market, Dict] = dict()
        LOGGER.info("Monitoring Service initializing is started....")
        self.start()

    def start(self):
        for market in Setting().active_markets:
            # TODO: implement monitoring connection flow
            pass

    def get_last_trade(self, market: Optional[Market]) -> Dict[Any, Any]:
        """ """
        if market:
            return self.trades[market]
        return self.trades
