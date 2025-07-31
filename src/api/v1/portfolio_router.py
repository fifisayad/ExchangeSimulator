from fastapi import APIRouter, Depends, FastAPI, HTTPException
from contextlib import asynccontextmanager

from .deps import get_portfolio_service
from ...services import PortfolioService
from ...schemas.portfolio_schema import (
    PortfolioResponseSchema,
    PortfolioSchema,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # initialize
    yield
    # cleanup


portfolio_router = APIRouter(prefix="/portfolio", tags=["Portfolio"], lifespan=lifespan)


@portfolio_router.get("", response_model=PortfolioResponseSchema)
async def get_portfolio(
    id: str | None = None,
    name: str | None = None,
    portfolio_service: PortfolioService = Depends(get_portfolio_service),
):
    if id:
        portfolio = await portfolio_service.read_by_id(id_=id)
        if portfolio:
            return portfolio
    if name:
        portfolio = await portfolio_service.read_by_name(name=name)
        if portfolio:
            return portfolio
    raise HTTPException(status_code=404, detail="portfolio not found")


@portfolio_router.post("", response_model=PortfolioResponseSchema)
async def create_portfolio(
    portfolio: PortfolioSchema,
    portfolio_service: PortfolioService = Depends(get_portfolio_service),
):
    try:
        existed_portfolio = await portfolio_service.read_by_name(portfolio.name)
        if existed_portfolio:
            raise HTTPException(
                status_code=400, detail=f"the portfolio {portfolio.name=} is existed"
            )
        return await portfolio_service.create(data=portfolio)
    except Exception as ex:
        raise HTTPException(status_code=400, detail=str(ex))


@portfolio_router.patch("", response_model=PortfolioResponseSchema)
async def update_portfolio(
    portfolio: PortfolioSchema,
    portfolio_service: PortfolioService = Depends(get_portfolio_service),
):
    try:
        return await portfolio_service.update_by_name(
            name=portfolio.name, data=portfolio
        )
    except Exception as ex:
        raise HTTPException(status_code=400, detail=str(ex))
