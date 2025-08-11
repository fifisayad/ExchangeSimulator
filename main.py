import coloredlogs
import logging
import traceback
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from src import Setting, base_router


coloredlogs.install()
LOGGER = logging.getLogger(__name__)
name_to_level = logging.getLevelNamesMapping()
logging.basicConfig(
    level=name_to_level["INFO"],
    format="[%(asctime)s] [%(levelname)s] [%(funcName)s] %(message)s",
)

setting = Setting()

# Create fastapi server
app = FastAPI(
    openapi_url=f"/{setting.API_PREFIX}/openapi.json",  # Customize the OpenAPI schema URL
    docs_url=f"/{setting.API_PREFIX}/docs",  # Customize the Swagger UI URL
)


@app.middleware("http")
async def log_internal_errors(request: Request, call_next):
    try:
        return await call_next(request)
    except HTTPException:
        # Let FastAPI handle HTTPExceptions normally
        raise
    except Exception as e:
        # Capture unexpected errors only
        error_trace = traceback.format_exc()
        LOGGER.error(f"Internal Server Error at {request.url}:\n{error_trace}")

        return JSONResponse(
            status_code=500, content={"detail": f"Internal Server Error: {error_trace}"}
        )


app.include_router(base_router, prefix=f"/{setting.API_PREFIX}")
