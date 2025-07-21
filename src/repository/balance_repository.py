from typing import List, Optional
from fifi import db_async_session
from fifi.exceptions import NotExistedSessionException
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..enums.asset import Asset
from .simulator_base_repository import SimulatorBaseRepository
from ..models.balance import Balance


class BalanceRepository(SimulatorBaseRepository):
    """
    Repository class for handling database operations related to the Balance model.

    Provides asynchronous methods to retrieve all balances or balances associated with a specific
    portfolio ID. Supports optional row-level locking using SQL's FOR UPDATE clause.

    Attributes:
        model (Type[Balance]): The SQLAlchemy model associated with this repository.
    """

    def __init__(self):
        super().__init__(model=Balance)

    @db_async_session
    async def get_all_balances(
        self,
        with_for_update: bool = False,
        session: Optional[AsyncSession] = None,
    ) -> List[Balance]:
        """
        Retrieve all balance records from the database.

        Args:
            with_for_update (bool, optional): If True, applies row-level locking using FOR UPDATE.
                Defaults to False.
            session (Optional[AsyncSession], optional): An optional SQLAlchemy AsyncSession.
                If not provided, one must be supplied via the db_async_session decorator.

        Returns:
            List[Balance]: A list of all Balance instances.

        Raises:
            NotExistedSessionException: If no active session is available or provided.
        """
        if not session:
            raise NotExistedSessionException("session is not existed")
        stmt = select(self.model)

        if with_for_update:
            stmt = stmt.with_for_update()

        results = await session.execute(stmt)
        return list(results.scalars().all())

    @db_async_session
    async def get_portfolio_asset_leverage(
        self,
        portfolio_id: str,
        asset: Asset,
        with_for_update: bool = False,
        session: Optional[AsyncSession] = None,
    ) -> Optional[float]:
        if not session:
            raise NotExistedSessionException("session is not existed")
        stmt = select(self.model.leverage).where(
            and_(Balance.portfolio_id == portfolio_id, Balance.asset == asset)
        )

        if with_for_update:
            stmt = stmt.with_for_update()

        result = await session.execute(stmt)
        return result.scalar()
