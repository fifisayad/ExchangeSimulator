import traceback

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fifi.helpers.get_logger import LoggerFactory

from src import Setting, base_router


setting = Setting()
LOGGER = LoggerFactory(setting.LOG_LEVEL).get(__name__)

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
