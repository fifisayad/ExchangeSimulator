from fifi.enums import OrderType, OrderSide, Asset, Market

from ..models import Portfolio


class OrderHelper:
    @staticmethod
    def get_recieved_asset(market: Market, side: OrderSide) -> Asset:
        if market.is_perptual():
            return Asset.USD
        market_coins = market.value.replace("_prep", "")
        second_coin = market_coins[:3]
        first_coin = market_coins[3:]
        if side == OrderSide.BUY:
            return Asset[second_coin.upper()]
        else:
            return Asset[first_coin.upper()]

    @staticmethod
    def get_payment_asset(market: Market, side: OrderSide) -> Asset:
        if market.is_perptual():
            return Asset.USD
        market_coins = market.value.replace("_prep", "")
        second_coin = market_coins[:3]
        first_coin = market_coins[3:]
        if side == OrderSide.BUY:
            return Asset[first_coin.upper()]
        else:
            return Asset[second_coin.upper()]

    @staticmethod
    def fee_calc(
        market: Market,
        price: float,
        size: float,
        side: OrderSide,
        order_type: OrderType,
        portfolio: Portfolio,
    ) -> float:
        """Calculates and applies trading fees to one or more orders based on
        order type, side, and whether the market is perpetual or spot.
        """
        order_total = size * price
        if market.is_perptual():
            if order_type == OrderType.LIMIT:
                fee = portfolio.perp_maker_fee * order_total
            elif order_type == OrderType.MARKET:
                fee = portfolio.perp_taker_fee * order_total
            else:
                fee = 0
        else:
            if order_type == OrderType.LIMIT:
                if side == OrderSide.BUY:
                    fee = size * portfolio.spot_maker_fee
                else:
                    fee = order_total * portfolio.spot_maker_fee
            elif order_type == OrderType.MARKET:
                if side == OrderSide.BUY:
                    fee = size * portfolio.spot_taker_fee
                else:
                    fee = order_total * portfolio.spot_taker_fee
            else:
                fee = 0
        return fee

    @staticmethod
    def get_order_payment_asset_total(
        market: Market,
        price: float,
        size: float,
        side: OrderSide,
        leverage: float = 1,
    ) -> float:
        order_total = size * price
        if market.is_perptual():
            if leverage:
                return order_total / leverage
        if side == OrderSide.BUY:
            return order_total
        else:
            return size

    @staticmethod
    def get_order_recieved_asset_total(
        market: Market,
        price: float,
        size: float,
        side: OrderSide,
    ) -> float:
        order_total = size * price
        if market.is_perptual():
            return order_total
        if side == OrderSide.BUY:
            return size
        else:
            return order_total
