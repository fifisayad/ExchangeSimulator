from datetime import datetime
from typing import List, Optional
from sqlalchemy import Text, and_, cast, select
from sqlalchemy.ext.asyncio import AsyncSession

from fifi.enums import OrderStatus
from fifi import db_async_session
from fifi.exceptions import NotExistedSessionException

from .simulator_base_repository import SimulatorBaseRepository
from ..models.order import Order


class OrderRepository(SimulatorBaseRepository):
    """
    Repository class for handling database operations related to the Order model.

    This class provides asynchronous methods to retrieve orders from the database,
    with support for filtering by order status or portfolio ID, and optional row-level locking.

    Attributes:
        model (Type[Order]): The SQLAlchemy model associated with this repository.
    """

    def __init__(self):
        super().__init__(model=Order)

    @db_async_session
    async def get_all_order(
        self,
        status: Optional[OrderStatus] = None,
        with_for_update: bool = False,
        session: Optional[AsyncSession] = None,
    ) -> List[Order]:
        """
        Retrieve all orders, optionally filtered by status.

        Args:
            status (Optional[OrderStatus]): The status to filter orders by. If None, returns all orders.
            with_for_update (bool, optional): Whether to lock the selected rows using FOR UPDATE. Defaults to False.
            session (Optional[AsyncSession], optional): An optional SQLAlchemy AsyncSession. If not provided, one must be available via the db_async_session decorator.

        Returns:
            List[Order]: A list of Order instances matching the query.

        Raises:
            NotExistedSessionException: If no valid session is provided or available.
        """
        if not session:
            raise NotExistedSessionException("session is not existed")
        stmt = select(self.model)
        if status:
            stmt = stmt.where(Order.status == status)

        if with_for_update:
            stmt = stmt.with_for_update()

        results = await session.execute(stmt)
        return list(results.scalars().all())

    @db_async_session
    async def get_filled_perp_orders(
        self,
        from_update_time: Optional[datetime] = None,
        with_for_update: bool = False,
        session: Optional[AsyncSession] = None,
    ) -> List[Order]:
        """
        Retrieve all filled perpetual orders, optionally filtered by update time
        and locked for update.

        Args:
            from_update_time (Optional[datetime]): If provided, only orders updated
                at or after this timestamp will be returned.
            with_for_update (bool): If True, applies a SELECT ... FOR UPDATE lock
                to the query, useful in transactional workflows. Defaults to False.
            session (Optional[AsyncSession]): The SQLAlchemy async session. If not
                provided, a session is expected to be injected by the @db_async_session decorator.

        Returns:
            List[Order]: A list of orders with status FILLED and market containing "perp".

        Raises:
            NotExistedSessionException: If the session is not available.
        """
        if not session:
            raise NotExistedSessionException("session is not existed")
        stmt = select(self.model).where(
            and_(
                Order.status == OrderStatus.FILLED,
                cast(Order.market, Text).ilike("%perp%"),
            )
        )
        if from_update_time:
            stmt = stmt.where(Order.updated_at >= from_update_time)

        if with_for_update:
            stmt = stmt.with_for_update()

        results = await session.execute(stmt)
        return list(results.scalars().all())
