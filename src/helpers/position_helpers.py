from ..enums.order_side import OrderSide
from ..enums.position_side import PositionSide
from ..models import Order


class PositionHelpers:

    @staticmethod
    def get_position_side_with_order(order: Order) -> PositionSide:
        if order.side == OrderSide.BUY:
            return PositionSide.LONG
        else:
            return PositionSide.SHORT

    @staticmethod
    def lqd_price_calc(
        entry_price: float, leverage: float, side: PositionSide
    ) -> float:
        lqd_distance = entry_price / leverage
        if side == PositionSide.LONG:
            return entry_price - lqd_distance
        else:
            return entry_price + lqd_distance
