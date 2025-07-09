# import pytest
# from sqlalchemy.ext.asyncio import AsyncSession
# from sqlalchemy.future import select
# from unittest.mock import AsyncMock, MagicMock
#
# from app.repositories.order_repository import OrderRepository
# from app.models.order import Order, OrderStatus
# from app.exceptions import NotExistedSessionException
#
#
# @pytest.fixture
# def mock_session():
#     return AsyncMock(spec=AsyncSession)
#
#
# @pytest.fixture
# def repository():
#     return OrderRepository()
#
#
# @pytest.mark.asyncio
# async def test_get_all_order_with_status(repository, mock_session):
#     mock_order = Order()
#     mock_order.status = OrderStatus.ACTIVE
#     mock_result = MagicMock()
#     mock_result.scalars().all.return_value = [mock_order]
#     mock_session.execute.return_value = mock_result
#
#     result = await repository.get_all_order(
#         status=OrderStatus.ACTIVE, session=mock_session
#     )
#
#     mock_session.execute.assert_called_once()
#     assert isinstance(result, list)
#     assert result[0].status == OrderStatus.ACTIVE
#
#
# @pytest.mark.asyncio
# async def test_get_all_order_without_status(repository, mock_session):
#     mock_order = Order()
#     mock_order.status = OrderStatus.ACTIVE
#     mock_result = MagicMock()
#     mock_result.scalars().all.return_value = [mock_order]
#     mock_session.execute.return_value = mock_result
#
#     result = await repository.get_all_order(status=None, session=mock_session)
#
#     mock_session.execute.assert_called_once()
#     assert isinstance(result, list)
#     assert result[0].status == OrderStatus.ACTIVE
#
#
# @pytest.mark.asyncio
# async def test_get_all_order_no_session_raises():
#     repo = OrderRepository()
#     with pytest.raises(NotExistedSessionException):
#         await repo.get_all_order(status=None, session=None)
#
#
# @pytest.mark.asyncio
# async def test_get_orders_by_portfolio_id(repository, mock_session):
#     mock_order = Order()
#     mock_order.portfolio_id = "portfolio_123"
#     mock_result = MagicMock()
#     mock_result.scalars().all.return_value = [mock_order]
#     mock_session.execute.return_value = mock_result
#
#     result = await repository.get_orders_by_portfolio_id(
#         "portfolio_123", session=mock_session
#     )
#
#     mock_session.execute.assert_called_once()
#     assert isinstance(result, list)
#     assert result[0].portfolio_id == "portfolio_123"
#
#
# @pytest.mark.asyncio
# async def test_get_orders_by_portfolio_id_no_session_raises():
#     repo = OrderRepository()
#     with pytest.raises(NotExistedSessionException):
#         await repo.get_orders_by_portfolio_id("portfolio_123", session=None)
