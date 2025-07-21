from copy import deepcopy
from enum import Enum
from .asset import Asset
from .order_side import OrderSide


class Market(Enum):
    BTCUSD = "btcusd"
    ETHUSD = "ethusd"
    BTCUSD_PERP = "btcusd_perp"
    ETHUSD_PERP = "ethusd_perp"

    def is_perptual(self) -> bool:
        if "perp" in self.value:
            return True
        return False

    def get_payment_asset_enum(self, side: OrderSide) -> Asset:
        if self.is_perptual():
            return Asset["USD"]
        market_coins = deepcopy(self.value)
        market_coins = market_coins.replace("_prep", "")
        first_coin = market_coins[:3]
        second_coin = market_coins[3:]
        if side == OrderSide.BUY:
            return Asset[second_coin.upper()]
        else:
            return Asset[first_coin.upper()]
