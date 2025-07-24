from ...services import PortfolioService, BalanceService, OrderService


def get_portfolio_service() -> PortfolioService:
    return PortfolioService()


def get_balance_service() -> BalanceService:
    return BalanceService()


def get_order_service() -> OrderService:
    return OrderService()
