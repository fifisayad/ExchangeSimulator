from typing import List, Optional
from fifi import Repository, db_async_session
from fifi.exceptions import NotExistedSessionException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..enums.order_status import OrderStatus
from ..models.order import Order


class OrderRepository(Repository):
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
        status: Optional[OrderStatus],
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
    async def get_orders_by_portfolio_id(
        self,
        portfolio_id: str,
        with_for_update: bool = False,
        session: Optional[AsyncSession] = None,
    ) -> List[Order]:
        """
        Retrieve all orders associated with a specific portfolio ID.

        Args:
            portfolio_id (str): The portfolio ID to filter orders by.
            with_for_update (bool, optional): Whether to lock the selected rows using FOR UPDATE. Defaults to False.
            session (Optional[AsyncSession], optional): An optional SQLAlchemy AsyncSession. If not provided, one must be available via the db_async_session decorator.

        Returns:
            List[Order]: A list of Order instances associated with the given portfolio ID.

        Raises:
            NotExistedSessionException: If no valid session is provided or available.
        """
        if not session:
            raise NotExistedSessionException("session is not existed")
        stmt = select(self.model).where(self.model.portfolio_id == portfolio_id)

        if with_for_update:
            stmt = stmt.with_for_update()

        results = await session.execute(stmt)
        return list(results.scalars().all())
