import time
from contextlib import asynccontextmanager

import sentry_sdk
import uvicorn
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from fastapi_versioning import VersionedFastAPI
from redis import asyncio as aioredis
from sqladmin import Admin
from prometheus_fastapi_instrumentator import Instrumentator

from app.admin.auth import authentication_backend
from app.admin.views import BookingsAdmin, HotelsAdmin, RoomsAdmin, UsersAdmin
from app.api.bookings import router as router_bookings
from app.api.hotels import router as router_hotels
from app.api.rooms import router as router_rooms
from app.api.users import router as router_users
from app.prometheus.prometheus import router as router_prometheus
from app.config import settings
from app.database import engine
from app.logger import logger


# Init Sentry for monitoring server errors
sentry_sdk.init(
    dsn=settings.SENTRY_DSN,
    # Set traces_sample_rate to 1.0 to capture 100%
    # of transactions for performance monitoring.
    # We recommend adjusting this value in production,
    traces_sample_rate=1.0,
)


@asynccontextmanager
async def lifespan(app: FastAPI) -> None:
    """
    The function returns the application lifecycle,
    commands before yield are executed before startup,
    after yield are executed after application stop
    :param app: FastAPI instance
    :return: None
    """
    logger.info("Initializing Redis")
    redis = aioredis.from_url(settings.redis_url)
    FastAPICache.init(RedisBackend(redis), prefix="cache")
    logger.info("Redis initialized")
    yield


app = FastAPI()


app.include_router(router_users)
app.include_router(router_bookings)
app.include_router(router_hotels)
app.include_router(router_rooms)
app.include_router(router_prometheus)


# add API versioning
app = VersionedFastAPI(
    app,
    version_format='{major}',
    prefix_format='/v{major}',
    description="""
    To access the required documentation,
    select the required version and follow the link,
    e.g. "v1/docs", to access the most up-to-date version
    of the API go to "latest/docs"
    """,
    enable_latest=True,
    lifespan=lifespan
)


origins = ["http://localhost:3000"]


# Add SQLAdmin to the project
admin = Admin(app, engine, authentication_backend=authentication_backend)


admin.add_view(UsersAdmin)
admin.add_view(BookingsAdmin)
admin.add_view(RoomsAdmin)
admin.add_view(HotelsAdmin)


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """
    The function measures the execution time of each request
    :param request: request instance
    :param call_next: function which call API
    :return: response to clients
    """
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    logger.info(
        "Requetst execution time", extra={"process_time": round(process_time, 4)}
    )
    return response


# setup prometheus
instrumentator = Instrumentator(
    should_group_status_codes=False,
    excluded_handlers=[".*admin.*", "/metrics"]
)

instrumentator.instrument(app).expose(app)


# mount static directory
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# dev function to run and debug app
if __name__ == "__main__":
    uvicorn.run(app)
