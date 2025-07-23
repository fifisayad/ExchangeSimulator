from fastapi import APIRouter, Depends, FastAPI, HTTPException
from contextlib import asynccontextmanager

from .deps import get_portfolio_service
from ...services import PortfolioService
from ...schemas import PortfolioSchema


@asynccontextmanager
async def lifespan(app: FastAPI):
    # initialize
    yield
    # cleanup


router = APIRouter(prefix="/portfolio", tags=["Portfolio"], lifespan=lifespan)


@router.get("", response_model=PortfolioSchema)
async def get_portfolio(
    id: str | None = None,
    name: str | None = None,
    portfolio_service: PortfolioService = Depends(get_portfolio_service),
):
    if id:
        portfolio = portfolio_service.read_by_id(id=id)
        if portfolio:
            return portfolio
    if name:
        portfolio = portfolio_service.read_by_name(name=name)
        if portfolio:
            return portfolio
    raise HTTPException(status_code=404, detail="portfolio not found")
