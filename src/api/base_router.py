from fastapi import APIRouter, FastAPI
from contextlib import asynccontextmanager

from fifi import DatabaseProvider

from ..engines.matching_engine import MatchingEngine
from ..engines.positions_orchestration_engine import PositionsOrchestrationEngine
from ..common.settings import Setting
from .v1.router import router as router_v1


setting = Setting()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # initialize
    await DatabaseProvider().init_models()
    MatchingEngine().start()
    PositionsOrchestrationEngine().start()
    yield
    # cleanup
    MatchingEngine().stop()
    PositionsOrchestrationEngine().stop()


base_router = APIRouter(tags=["ExchangeAPIs"], lifespan=lifespan)


base_router.include_router(router=router_v1)
