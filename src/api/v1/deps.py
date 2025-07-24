from ...services import PortfolioService, BalanceService, OrderService, LeverageService


def get_portfolio_service() -> PortfolioService:
    return PortfolioService()


def get_balance_service() -> BalanceService:
    return BalanceService()


def get_order_service() -> OrderService:
    return OrderService()


def get_leverage_service() -> LeverageService:
    return LeverageService()
