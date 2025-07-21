from typing import Dict, List

from ..enums.asset import Asset
from ..enums.position_status import PositionStatus
from ..models import Order, Position
from ..repository import PositionRepository
from ..schemas import PositionSchema
from ..helpers.position_helpers import PositionHelpers
from .balance_service import BalanceService


# TODO: adding position id for orders
class PositionService:

    def __init__(self) -> None:
        self.position_repo = PositionRepository()
        self.balance_service = BalanceService()

    async def get_open_positions(self) -> List[Position]:
        return await self.position_repo.get_all_positions(status=PositionStatus.OPEN)

    async def get_open_positions_hashmap(self) -> Dict[str, Position]:
        open_positions = await self.get_open_positions()
        positions = dict()
        # unique hash for this is {market}_{portfolio_id}
        for position in open_positions:
            positions[f"{position.market}_{position.portfolio_id}"] = position
        return positions

    async def apply_order_to_position(self, order: Order, position: Position) -> None:
        if PositionHelpers.is_order_against_position(order, position):
            if order.size >= position.size:
                await self.close_position(order, position)
            else:
                await self.close_partially_position(order, position)
        else:
            await self.merge_order_with_position(order, position)

    async def merge_order_with_position(self, order: Order, position: Position) -> None:
        pass

    async def close_partially_position(self, order: Order, position: Position) -> None:
        position.close_price = order.price
        position.pnl += PositionHelpers.pnl_value(
            position=position, price=order.price, size=order.price * order.size
        )

        # unlock margin
        is_unlocked = await self.balance_service.unlock_balance(
            portfolio_id=position.portfolio_id,
            asset=Asset.USD,
            unlocked_qty=position.entry_price * order.size,
        )
        position.margin -= position.entry_price * order.size
        position.size -= order.size

        # add pnl value
        is_realized = await self.balance_service.add_balance(
            portfolio_id=position.portfolio_id, asset=Asset.USD, qty=position.pnl
        )
        if is_unlocked & is_realized:
            await self.position_repo.update_entity(position)

    async def close_position(self, order: Order, position: Position) -> None:
        position.close_price = order.price
        position.pnl += PositionHelpers.pnl_value(
            position=position, price=order.price, size=order.price * order.size
        )
        position.status = PositionStatus.CLOSE

        # unlock margin
        is_unlocked = await self.balance_service.unlock_balance(
            portfolio_id=position.portfolio_id,
            asset=Asset.USD,
            unlocked_qty=position.margin,
        )

        # add pnl value
        is_realized = await self.balance_service.add_balance(
            portfolio_id=position.portfolio_id, asset=Asset.USD, qty=position.pnl
        )
        if is_unlocked & is_realized:
            await self.position_repo.update_entity(position)

    async def create_position_by_order(self, order: Order) -> Position:
        position = PositionSchema()
        position.entry_price = order.price
        position.portfolio_id = order.portfolio_id
        position.market = order.market
        position.size = order.size
        position.side = PositionHelpers.get_position_side_with_order(order)
        leverage = await self.balance_service.get_portfolio_asset_leverage(
            portfolio_id=position.portfolio_id,
            asset=order.market.get_payment_asset_enum(order.side),
        )
        if leverage:
            position.leverage = leverage
        else:
            # just in impossible case ;)
            position.leverage = 1
        position.lqd_price = PositionHelpers.lqd_price_calc(
            entry_price=order.price, leverage=position.leverage, side=position.side
        )
        position.margin = PositionHelpers.margin_calc(
            position.size, position.leverage, position.entry_price
        )
        return await self.position_repo.create(position)

    async def liquid_position(self, position: Position) -> None:
        is_sucessful = self.balance_service.burn_balance(
            portfolio_id=position.portfolio_id,
            asset=Asset.USD,
            burned_qty=position.margin,
        )
        if is_sucessful:
            position.pnl = (-1) * position.margin
            position.status = PositionStatus.LIQUID
            await self.position_repo.update_entity(position)
