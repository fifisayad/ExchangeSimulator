from fastapi import APIRouter, FastAPI
from contextlib import asynccontextmanager
from ..engines.matching_engine import MatchingEngine
from ..common.settings import Setting
from .v1.router import router as router_v1


setting = Setting()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # initialize
    await MatchingEngine().start()
    yield
    # cleanup


base_router = APIRouter(
    prefix=f"/{setting.API_VERSION}", tags=["ExchangeAPIs"], lifespan=lifespan
)


base_router.include_router(router=router_v1)
