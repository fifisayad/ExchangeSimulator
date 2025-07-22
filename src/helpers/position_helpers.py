from ..enums.order_side import OrderSide
from ..enums.position_side import PositionSide
from ..models import Order, Position


class PositionHelpers:
    """A collection of static helper methods for position-related trading logic."""

    @staticmethod
    def get_position_side_with_order(order: Order) -> PositionSide:
        """Determines the position side (LONG or SHORT) based on the order side.

        Args:
            order (Order): The trading order.

        Returns:
            PositionSide: LONG if order side is BUY, otherwise SHORT.
        """
        if order.side == OrderSide.BUY:
            return PositionSide.LONG
        else:
            return PositionSide.SHORT

    @staticmethod
    def lqd_price_calc(
        entry_price: float, leverage: float, side: PositionSide
    ) -> float:
        """Calculates the liquidation price based on entry price, leverage, and position side.

        Args:
            entry_price (float): The entry price of the position.
            leverage (float): The leverage used in the trade.
            side (PositionSide): The side of the position (LONG or SHORT).

        Returns:
            float: The calculated liquidation price.
        """
        lqd_distance = entry_price / leverage
        if side == PositionSide.LONG:
            return entry_price - lqd_distance
        else:
            return entry_price + lqd_distance

    @staticmethod
    def margin_calc(size: float, leverage: float, price: float) -> float:
        """Calculates the required margin for a position.

        Args:
            size (float): The size of the position.
            leverage (float): The leverage applied to the position.
            price (float): The entry price.

        Returns:
            float: The calculated margin required.
        """
        return (size / leverage) * price

    @staticmethod
    def is_order_against_position(order: Order, position: Position) -> bool:
        """Checks if the given order opposes the direction of an existing position.

        Args:
            order (Order): The order to evaluate.
            position (Position): The existing position.

        Returns:
            bool: True if the order is against the position, False otherwise.

        Raises:
            ValueError: If the order and position markets do not match.
        """
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
        """Calculates the profit or loss (PnL) value for a given position.

        Args:
            position (Position): The trading position.
            price (float): The current price.
            size (float): The size of the position.

        Returns:
            float: The calculated PnL value.
        """
        if position.side == PositionSide.LONG:
            price_delta = price - position.entry_price
        else:
            price_delta = position.entry_price - price

        return size * (price_delta / position.entry_price)

    @staticmethod
    def weighted_average_entry_price(position: Position, order: Order) -> float:
        """Calculates the weighted average entry price after an additional order is added.

        Args:
            position (Position): The existing trading position.
            order (Order): The new order being added to the position.

        Returns:
            float: The new weighted average entry price.
        """
        return ((position.size * position.entry_price) + (order.price * order.size)) / (
            position.size + order.size
        )
