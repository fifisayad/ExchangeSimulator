from ..enums.order_side import OrderSide
from ..enums.asset import Asset
from ..enums.market import Market


class OrderHelper:
    @staticmethod
    def get_payment_asset_enum(market: Market, side: OrderSide) -> Asset:
        if market.is_perptual():
            return Asset.USD
        market_coins = market.value.replace("_prep", "")
        first_coin = market_coins[:3]
        second_coin = market_coins[3:]
        if side == OrderSide.BUY:
            return Asset[second_coin.upper()]
        else:
            return Asset[first_coin.upper()]
