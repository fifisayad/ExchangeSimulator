from typing import List, Optional
from fifi import Repository, db_async_session
from fifi.exceptions import NotExistedSessionException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..enums.order_status import OrderStatus
from ..models.order import Order


class OrderRepository(Repository):

    model = Order

    @db_async_session
    async def get_all_order(
        self,
        status: Optional[OrderStatus],
        with_for_update: bool = False,
        session: Optional[AsyncSession] = None,
    ) -> List[Order]:
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
        if not session:
            raise NotExistedSessionException("session is not existed")
        stmt = select(self.model).where(self.model.portfolio_id == portfolio_id)

        if with_for_update:
            stmt = stmt.with_for_update()

        results = await session.execute(stmt)
        return list(results.scalars().all())
