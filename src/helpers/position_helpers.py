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
