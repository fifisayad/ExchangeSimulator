from ..enums.order_side import OrderSide
from ..enums.position_side import PositionSide
from ..models import Order, Position


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

    @staticmethod
    def margin_calc(size: float, leverage: float, price: float) -> float:
        return (size / leverage) * price

    @staticmethod
    def is_order_against_position(order: Order, position: Position) -> bool:
        if order.market != position.market:
            raise ValueError(
                f"""[PositionHelper-is_order_against_position]: order market {order.market} is 
                not equal with position market {position.market}"""
            )
        if order.side == OrderSide.BUY:
            if position.side == PositionSide.SHORT:
                return True
            else:
                return False
        else:
            if position.side == PositionSide.LONG:
                return True
            else:
                return False

    @staticmethod
    def pnl_value(position: Position, price: float, size: float) -> float:
        if position.side == PositionSide.LONG:
            price_delta = price - position.entry_price
        else:
            price_delta = position.entry_price - price

        return size * (price_delta / position.entry_price)

    @staticmethod
    def weighted_average_entry_price(position: Position, order: Order) -> float:
        return ((position.size * position.entry_price) + (order.price * order.size)) / (
            position.size + order.size
        )
