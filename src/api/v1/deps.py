from ...engines.matching_engine import MatchingEngine
from ...services import (
    PortfolioService,
    BalanceService,
    OrderService,
    LeverageService,
    PositionService,
)


def get_portfolio_service() -> PortfolioService:
    return PortfolioService()


def get_balance_service() -> BalanceService:
    return BalanceService()


def get_order_service() -> OrderService:
    return OrderService()


def get_leverage_service() -> LeverageService:
    return LeverageService()


def get_matching_engine() -> MatchingEngine:
    return MatchingEngine()


def get_position_service() -> PositionService:
    return PositionService()
