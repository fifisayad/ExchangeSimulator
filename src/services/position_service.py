from typing import Dict, List

from src.enums.order_side import OrderSide
from src.enums.position_side import PositionSide

from ..enums.position_status import PositionStatus
from ..models import Order, Position
from ..repository import PositionRepository
from ..schemas import PositionSchema


class PositionService:

    def __init__(self) -> None:
        self.position_repo = PositionRepository()

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
        pass

    async def create_position_by_order(self, order: Order) -> Position:
        position = PositionSchema()
        if order.side == OrderSide.BUY:
            position.side = PositionSide.LONG
        else:
            position.side = PositionSide.SHORT
        # TODO:add logic for opening new position
        return await self.position_repo.create(position)

    async def liquid_position(self, position: Position) -> None:
        pass
