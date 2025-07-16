from typing import List, Union

from src.enums.order_side import OrderSide
from src.enums.order_type import OrderType

from ..enums.order_status import OrderStatus
from ..repository import OrderRepository
from ..models import Order


class OrderService:
    def __init__(self):
        self.order_repo = OrderRepository()

    async def get_open_orders(self) -> List[Order]:
        return await self.order_repo.get_all_order(status=OrderStatus.ACTIVE)

    async def fee_calc(self, orders: Union[Order, List[Order]]) -> None:
        orders_list: List[Order] = (
            [orders] if type(orders) == Order else orders
        )  # type: ignore
        for order in orders_list:
            order_total = order.size * order.price
            if order.market.is_perptual():
                if order.type == OrderType.LIMIT:
                    order.fee = order.portfolio.perp_maker_fee * order_total
                elif order.type == OrderType.MARKET:
                    order.fee = order.portfolio.perp_taker_fee * order_total
            else:
                if order.type == OrderType.LIMIT:
                    if order.side == OrderSide.BUY:
                        order.fee = order.size * order.portfolio.spot_maker_fee
                    else:
                        order.fee = order_total * order.portfolio.spot_maker_fee
                elif order.type == OrderType.MARKET:
                    if order.side == OrderSide.BUY:
                        order.fee = order.size * order.portfolio.spot_taker_fee
                    else:
                        order.fee = order_total * order.portfolio.spot_taker_fee
        # TODO:implement merge functionality for changes on the db models
