from fifi.helpers.get_current_time import GetCurrentTime

from src.enums.position_side import PositionSide
from ..services import (
    OrderService,
    BalanceService,
    MarketMonitoringService,
    PositionService,
)
from .engine import Engine


class PositionsOrchestrationEngine(Engine):
    name: str = "positions_orchestration_engine"

    def __init__(self):
        super().__init__()
        self.order_service = OrderService()
        self.balance_service = BalanceService()
        self.position_service = PositionService()
        self.mm_service = MarketMonitoringService()

    async def process(self):
        last_update = GetCurrentTime().get()
        while True:
            check_time = GetCurrentTime().get()
            filled_perp_orders = await self.order_service.get_filled_perp_orders(
                from_update_time=last_update
            )
            last_update = check_time

            open_positions = await self.position_service.get_open_positions_hashmap()

            for order in filled_perp_orders:
                position_key = f"{order.market}_{order.portfolio_id}"
                if position_key in open_positions:
                    await self.position_service.apply_order_to_position(
                        order=order, position=open_positions[position_key]
                    )
                else:
                    await self.position_service.create_position_by_order(order=order)

            for key, position in open_positions.items():
                market_last_trade = self.mm_service.get_last_trade(
                    market=position.market
                )
                if position.side == PositionSide.LONG:
                    if position.lqd_price < market_last_trade:
                        continue

                if position.side == PositionSide.SHORT:
                    if position.lqd_price > market_last_trade:
                        continue

                await self.position_service.liquid_position(position=position)
