import logging
from typing import List, Optional
from fifi import GetLogger, singleton, BaseEngine

from ..enums.position_status import PositionStatus
from ..common.exceptions import InvalidOrder, NotEnoughBalance, NotFoundOrder
from ..enums.market import Market
from ..helpers.order_helper import OrderHelper
from ..helpers.position_helpers import PositionHelpers
from ..models.order import Order
from ..schemas.order_schema import OrderSchema
from ..enums.order_side import OrderSide
from ..enums.order_status import OrderStatus
from ..enums.order_type import OrderType
from ..services import *
from ..repository import *


LOGGER = logging.getLogger(__name__)


@singleton
class MatchingEngine(BaseEngine):
    name: str = "matching_engine"

    def __init__(self):
        super().__init__()
        self.mm_service = MarketMonitoringService()
        self.portfolio_service = PortfolioService()
        self.balance_service = BalanceService()
        self.order_service = OrderService()
        self.position_service = PositionService()
        self.leverage_service = LeverageService()

    async def preprocess(self):
        pass

    async def postprocess(self):
        pass

    async def process(self):
        while True:
            # get open orders from db
            open_orders = await self.order_service.get_open_orders()

            # check open orders not empty
            if not open_orders:
                continue

            await self.match_open_orders(open_orders=open_orders)

    async def match_open_orders(self, open_orders: List[Order]):
        trades = await self.mm_service.get_last_trade()
        for order in open_orders:
            if order.type == OrderType.MARKET:
                continue
            elif order.side == OrderSide.BUY and order.price >= trades[order.market]:
                await self.fill_order(order)
            elif order.side == OrderSide.SELL and order.price <= trades[order.market]:
                await self.fill_order(order)
            else:
                continue

    async def cancel_order(self, order_id: str) -> Order:
        order = await self.order_service.read_by_id(id_=order_id)
        if not order:
            raise NotFoundOrder(f"{order_id=}")

        if order.status != OrderStatus.ACTIVE:
            raise InvalidOrder(f"this {order_id=} is {order.status}!!!")
        order.status = OrderStatus.CANCELED

        payment_asset = OrderHelper.get_payment_asset(
            market=order.market, side=order.side
        )
        payment_total = OrderHelper.get_order_payment_asset_total(
            market=order.market, price=order.price, size=order.size, side=order.side
        )

        await self.balance_service.unlock_balance(
            portfolio_id=order.portfolio_id,
            asset=payment_asset,
            unlocked_qty=payment_total,
        )

        await self.order_service.update_entity(order)
        return order

    async def fill_order(self, order: Order) -> Order:
        if order.status != OrderStatus.ACTIVE:
            LOGGER.info(f"can not fill this {order.id=} {order.status=}")
            return order
        LOGGER.info(f"fill {order.id=}")
        order.status = OrderStatus.FILLED
        recieved_asset = OrderHelper.get_recieved_asset(
            market=order.market, side=order.side
        )
        if not order.market.is_perptual():
            payment_asset = OrderHelper.get_payment_asset(
                market=order.market, side=order.side
            )
            payment_total = OrderHelper.get_order_payment_asset_total(
                market=order.market, price=order.price, size=order.size, side=order.side
            )
            recieved_total = OrderHelper.get_order_recieved_asset_total(
                market=order.market, price=order.price, size=order.size, side=order.side
            )

            await self.balance_service.unlock_balance(
                portfolio_id=order.portfolio_id,
                asset=payment_asset,
                unlocked_qty=payment_total,
            )

            await self.balance_service.pay_balance(
                portfolio_id=order.portfolio_id,
                asset=payment_asset,
                paid_qty=payment_total,
            )

            await self.balance_service.add_balance(
                portfolio_id=order.portfolio_id,
                asset=recieved_asset,
                qty=recieved_total,
            )

        # fee should be paid for any orders
        await self.balance_service.pay_fee(
            portfolio_id=order.portfolio_id,
            asset=recieved_asset,
            paid_qty=order.fee,
        )
        await self.order_service.update_entity(order)
        return order

    async def perpetual_open_position_check(
        self, market: Market, portfolio_id: str, size: float, side: OrderSide
    ) -> bool:
        open_position = await self.position_service.get_positions(
            portfolio_id=portfolio_id, market=market, status=PositionStatus.OPEN
        )
        if open_position:
            open_position = open_position.pop()
            # there is an active position
            if PositionHelpers().is_order_against_position(
                order_side=side, position_side=open_position.side
            ):
                # order against position
                if open_position.size >= size:
                    return True
                else:
                    er_msg = f"""there is an active position for {portfolio_id=}
                        with {open_position.size=}
                        order size must be equal or lessen than position size
                        """
                    LOGGER.error(er_msg)
                    raise InvalidOrder(er_msg)
        return False

    async def create_order(
        self,
        market: Market,
        portfolio_id: str,
        price: Optional[float],
        size: float,
        side: OrderSide,
        order_type: OrderType,
    ) -> Order:
        portfolio = await self.portfolio_service.read_by_id(id_=portfolio_id)
        if not portfolio:
            LOGGER.error(f"{portfolio_id=} is invalid")
            raise InvalidOrder(f"{portfolio_id=} is invalid")

        order_schema = OrderSchema(
            portfolio_id=portfolio_id,
            market=market,
            price=price if price else 0,
            size=size,
            fee=0,
            side=side,
            type=order_type,
        )

        if order_type == OrderType.MARKET:
            order_schema.price = await self.mm_service.get_last_trade(market=market)

        payment_asset = OrderHelper.get_payment_asset(market=market, side=side)
        checked_open_position = False
        leverage = 1
        if market.is_perptual():
            leverage = (
                await self.leverage_service.get_portfolio_market_leverage_value(
                    portfolio_id=order_schema.portfolio_id, market=order_schema.market
                )
                or leverage
            )
            checked_open_position = await self.perpetual_open_position_check(
                market=order_schema.market,
                portfolio_id=order_schema.portfolio_id,
                size=order_schema.size,
                side=order_schema.side,
            )
        payment_total = OrderHelper.get_order_payment_asset_total(
            market=order_schema.market,
            price=order_schema.price,
            side=order_schema.side,
            size=order_schema.size,
            leverage=leverage,
        )

        checked_available_qty = False
        if not (checked_open_position):
            checked_available_qty = await self.balance_service.check_available_qty(
                portfolio_id=portfolio_id, asset=payment_asset, qty=payment_total
            )
            if not checked_available_qty:
                er_msg = f"""{side=} order for 
                    {portfolio_id=} on {market=} 
                    with {size=} can not be created"""
                LOGGER.error(er_msg)
                raise NotEnoughBalance(er_msg)

        if checked_available_qty:
            await self.balance_service.lock_balance(
                portfolio_id=portfolio_id,
                asset=payment_asset,
                locked_qty=payment_total,
            )

        order_schema.fee = OrderHelper.fee_calc(
            portfolio=portfolio,
            market=order_schema.market,
            price=order_schema.price,
            size=order_schema.size,
            side=order_schema.side,
            order_type=order_schema.type,
        )
        LOGGER.info(f"creating new order {order_schema.model_dump()}")
        order = await self.order_service.create(data=order_schema)

        if not order:
            raise InvalidOrder(
                f"There is Problem with creating new order {order_schema.model_dump()}"
            )

        if order.type == OrderType.MARKET:
            return await self.fill_order(order)

        return order
