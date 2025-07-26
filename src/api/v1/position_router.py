from typing import List, Union
from fastapi import APIRouter, Depends, FastAPI, HTTPException
from contextlib import asynccontextmanager

from ...schemas.position_schema import (
    PositionReadSchema,
    PositionResponseSchema,
)
from .deps import get_position_service
from ...services import PositionService


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
    position_query: PositionReadSchema,
    position_service: PositionService = Depends(get_position_service),
):
    position = None
    if position_query.id:
        position = await position_service.read_by_id(id=position_query.id)
    elif position_query.portfolio_id:
        position = await position_service.get_positions(
            portfolio_id=position_query.portfolio_id,
            market=position_query.market,
            status=position_query.status,
            side=position_query.side,
        )
    else:
        raise HTTPException(
            status_code=400, detail="one of portfolio_id or position_id must be given!!"
        )
    if position:
        return position
    raise HTTPException(status_code=404, detail="position(s) not found")
