from typing import List, Union
from fastapi import APIRouter, Depends, FastAPI, HTTPException
from contextlib import asynccontextmanager

from fifi.enums import PositionSide, PositionStatus

from .deps import get_position_service
from ...services import PositionService
from ...schemas.position_schema import PositionResponseSchema
from ...enums.market import Market


@asynccontextmanager
async def lifespan(app: FastAPI):
    # initialize
    yield
    # cleanup


position_router = APIRouter(prefix="/position", tags=["Position"], lifespan=lifespan)


@position_router.get(
    "", response_model=Union[PositionResponseSchema, List[PositionResponseSchema]]
)
async def get_position(
    position_id: str | None = None,
    portfolio_id: str | None = None,
    market: Market | None = None,
    side: PositionSide | None = None,
    status: PositionStatus | None = None,
    position_service: PositionService = Depends(get_position_service),
):
    position = None
    if position_id:
        position = await position_service.read_by_id(id_=position_id)
    elif portfolio_id:
        position = await position_service.get_positions(
            portfolio_id=portfolio_id,
            market=market,
            status=status,
            side=side,
        )
    else:
        raise HTTPException(
            status_code=400, detail="one of portfolio_id or position_id must be given!!"
        )
    if position:
        return position
    raise HTTPException(status_code=404, detail="position(s) not found")
