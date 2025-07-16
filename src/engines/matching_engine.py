from ..enums.order_side import OrderSide
from ..enums.order_status import OrderStatus
from ..enums.order_type import OrderType
from ..services import *
from ..repository import *
from .engine import Engine


class MatchingEngine(Engine):
    name: str = "matching_engine"

    def __init__(self):
        super().__init__()
        self.mm_service = MarketMonitoringService()
        self.portfolio_service = PortfolioService()
        self.balance_service = BalanceService()
        self.order_service = OrderService()

    async def preprocess(self):
        pass

    async def Process(self):
        while True:
            # get open orders from db
            open_orders = await self.order_service.get_open_orders()

            # check open orders not empty
            if not open_orders:
                continue

            trades = self.mm_service.get_last_trade()
            for order in open_orders:
                if order.type == OrderType.MARKET:
                    order.price = trades[order.market]["price"]
                    order.status = OrderStatus.FILLED
                elif (
                    order.side == OrderSide.BUY and order.price >= trades[order.market]
                ):
                    order.status = OrderStatus.FILLED
                elif (
                    order.side == OrderSide.SELL and order.price <= trades[order.market]
                ):
                    order.status = OrderStatus.FILLED
                else:
                    continue

                # fee calculations
                await self.order_service.fee_calc(order)
                if not order.market.is_perptual():
                    await self.balance_service.update_balances(order)
