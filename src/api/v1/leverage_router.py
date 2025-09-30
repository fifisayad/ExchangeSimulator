from fastapi import APIRouter, Depends, FastAPI, HTTPException
from contextlib import asynccontextmanager

from fifi.enums import Market

from .deps import get_leverage_service
from ...schemas.leverage_schema import LeverageSchema
from ...services import LeverageService


@asynccontextmanager
async def lifespan(app: FastAPI):
    # initialize
    yield
    # cleanup


leverage_router = APIRouter(prefix="/leverage", tags=["Leverage"], lifespan=lifespan)


@leverage_router.get("", response_model=LeverageSchema)
async def get_leverage(
    portfolio_id: str,
    market: Market,
    leverage_service: LeverageService = Depends(get_leverage_service),
):
    leverage = await leverage_service.get_portfolio_market_leverage(
        portfolio_id=portfolio_id, market=market
    )
    if leverage:
        return leverage
    raise HTTPException(status_code=404, detail="leverage not found")


@leverage_router.post("", response_model=LeverageSchema)
async def create_or_update_leverage(
    leverage_query: LeverageSchema,
    leverage_service: LeverageService = Depends(get_leverage_service),
):
    leverage = await leverage_service.create_or_update_leverage(
        portfolio_id=leverage_query.portfolio_id,
        market=leverage_query.market,
        leverage=leverage_query.leverage,
    )
    if leverage:
        return leverage
    raise HTTPException(status_code=400, detail="leverage couldn't be created")
